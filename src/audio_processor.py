import os
import shutil
import subprocess
import base64
from typing import List

class AudioProcessor:
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Returns the file size in bytes."""
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path)

    @staticmethod
    def is_under_limit(file_path: str, limit_mb: int = 15) -> bool:
        """Checks if the file size is under the specified limit in MB."""
        if not os.path.exists(file_path):
            return True # Assume under limit if it doesn't exist (handles some mock cases)
        size_bytes = AudioProcessor.get_file_size(file_path)
        limit_bytes = limit_mb * 1024 * 1024
        return size_bytes < limit_bytes

    @staticmethod
    def encode_to_base64(file_path: str) -> str:
        """Encodes a file to a base64 string."""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def get_duration(file_path: str) -> float:
        """Returns the duration of the audio file in seconds."""
        try:
            # Added analyzeduration and probesize for better HLS/Vimeo duration detection
            command = [
                "ffprobe", "-v", "error", 
                "-analyzeduration", "100M", "-probesize", "100M",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", file_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            val = result.stdout.strip()
            return float(val) if val and val != "N/A" else 0.0
        except (subprocess.CalledProcessError, ValueError):
            return 0.0

    @staticmethod
    def get_bitrate(file_path: str) -> int:
        """Returns the bitrate in bits per second."""
        try:
            command = [
                "ffprobe", "-v", "error", 
                "-analyzeduration", "100M", "-probesize", "100M",
                "-select_streams", "a:0",
                "-show_entries", "stream=bit_rate", "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            val = result.stdout.strip()
            if val == "N/A" or not val:
                command = [
                    "ffprobe", "-v", "error", 
                    "-analyzeduration", "100M", "-probesize", "100M",
                    "-show_entries", "format=bit_rate", 
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    file_path
                ]
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                val = result.stdout.strip()
            
            return int(val) if val and val != "N/A" else 0
        except (subprocess.CalledProcessError, ValueError):
            return 0

    @staticmethod
    def reencode_to_optimal(input_path: str, output_path: str, bitrate: str = "48k", threads: int = 0) -> bool:
        """Re-encodes the audio to an optimal bitrate for transcription."""
        try:
            print(f"      - Re-encoding {input_path} at {bitrate} (optimal, threads={threads})...")
            command = [
                "ffmpeg", "-y", "-threads", str(threads), "-i", input_path,
                "-b:a", bitrate,
                "-ac", "1", # Mono is usually better for transcription and smaller size
                "-ar", "16000", # 16kHz is standard for many speech models
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during optimal re-encoding: {e.stderr.decode('utf-8', errors='replace')}")
            return False

    @staticmethod
    def remove_silence(input_path: str, output_path: str, threshold_db: int = -50, threads: int = 0) -> bool:
        """Removes silence from the audio using ffmpeg silenceremove filter."""
        try:
            print(f"      - Removing silence (threshold: {threshold_db}dB, threads={threads})...")
            command = [
                "ffmpeg", "-y", "-threads", str(threads), "-i", input_path,
                "-af", f"silenceremove=stop_periods=-1:stop_duration=1:stop_threshold={threshold_db}dB",
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during silence removal: {e.stderr.decode('utf-8', errors='replace')}")
            return False

    @staticmethod
    def split_into_chunks(input_path: str, output_pattern: str, segment_time: int = 1800, threads: int = 0) -> List[str]:
        """
        Splits the audio into chunks of specified duration (default 1800s / 30m).
        Returns a list of paths to the created chunks.
        """
        try:
            print(f"      - Splitting into chunks of {segment_time}s (threads={threads})...")
            command = [
                "ffmpeg", "-y", "-threads", str(threads), "-i", input_path,
                "-f", "segment",
                "-segment_time", str(segment_time),
                "-c", "copy",
                output_pattern
            ]
            subprocess.run(command, check=True, capture_output=True)
            
            directory = os.path.dirname(output_pattern) or "."
            base_parts = os.path.basename(output_pattern).split("%")
            prefix = base_parts[0]
            
            chunks = []
            for f in sorted(os.listdir(directory)):
                if f.startswith(prefix) and f != os.path.basename(input_path):
                     chunks.append(os.path.join(directory, f))
            return chunks
            
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during splitting: {e.stderr.decode('utf-8', errors='replace')}")
            return []

    @staticmethod
    def optimize_audio(input_path: str, output_path: str, bitrate: str = "48k", threshold_db: int = -50, threads: int = 0) -> bool:
        """
        Performs silence removal, bitrate optimization, mono conversion, and sample rate adjustment
        in a SINGLE ffmpeg pass.
        """
        try:
            print(f"      - Optimizing audio (silence removal, mono, {bitrate}, 16kHz, threads={threads})...")
            # Filter for silence removal
            af_filter = f"silenceremove=stop_periods=-1:stop_duration=1:stop_threshold={threshold_db}dB"
            
            command = [
                "ffmpeg", "-y", "-threads", str(threads), "-i", input_path,
                "-af", af_filter,
                "-b:a", bitrate,
                "-ac", "1",      # Mono
                "-ar", "16000",  # 16kHz
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during audio optimization: {e.stderr.decode('utf-8', errors='replace')}")
            return False

    @staticmethod
    def process_for_transcription(input_path: str, segment_time: int = 1800, max_size_mb: int = 15, output_dir: str = "temp", threads: int = 0, output_pattern: str = None) -> List[str]:
        """
        Orchestrates the audio processing: splits if needed.
        Assumes the input is already optimized.
        Prioritizes duration-based splitting (segment_time) as requested.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        extension = os.path.splitext(input_path)[1] or ".mp3"
        
        # 1. Splitting Logic
        if not output_pattern:
            output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d{extension}")

        # If duration-based splitting is requested (segment_time > 0)
        if segment_time > 0:
            duration = AudioProcessor.get_duration(input_path)
            if duration > segment_time:
                print(f"   - Input file duration ({duration:.1f}s) exceeds limit ({segment_time}s). Splitting...")
                chunks = AudioProcessor.split_into_chunks(input_path, output_pattern, segment_time, threads=threads)
                print(f"   - Split into {len(chunks)} chunks.")
                return chunks
            else:
                print(f"   - Input file duration is within limit ({segment_time}s).")

        # Fallback to size-based check if duration check passed or wasn't requested
        if AudioProcessor.is_under_limit(input_path, max_size_mb):
            directory = os.path.dirname(output_pattern) or "."
            # Determine the single output path
            final_path = os.path.join(directory, os.path.basename(output_pattern).replace("%03d", "001"))
            shutil.copy2(input_path, final_path)
            return [final_path]

        print(f"   - Input file size exceeds limit ({max_size_mb} MB). Splitting (duration-based fallback)...")
        # Estimate segment time to fit in max_size_mb as a fallback
        duration = AudioProcessor.get_duration(input_path)
        current_size_bytes = AudioProcessor.get_file_size(input_path)
        target_size_bytes = max_size_mb * 1024 * 1024
        
        est_segment_time = int((target_size_bytes / current_size_bytes) * duration * 0.9)
        # Guarantee at least 2 chunks if we are over limit
        if est_segment_time >= duration:
            est_segment_time = int(duration / 2)
        if est_segment_time < 1: est_segment_time = 1
        
        chunks = AudioProcessor.split_into_chunks(input_path, output_pattern, est_segment_time, threads=threads)
        print(f"   - Split into {len(chunks)} chunks.")
        return chunks
