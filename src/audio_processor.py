import os
import shutil
import subprocess
from typing import List

class AudioProcessor:
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Returns the file size in bytes."""
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path)

    @staticmethod
    def is_under_limit(file_path: str, limit_mb: int = 20) -> bool:
        """Checks if the file size is under the specified limit in MB."""
        size_bytes = AudioProcessor.get_file_size(file_path)
        limit_bytes = limit_mb * 1024 * 1024
        return size_bytes < limit_bytes

    @staticmethod
    def get_bitrate(file_path: str) -> int:
        """Returns the bitrate in bits per second."""
        try:
            command = [
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=bit_rate", "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            val = result.stdout.strip()
            if val == "N/A" or not val:
                command = [
                    "ffprobe", "-v", "error", "-show_entries", "format=bit_rate", 
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    file_path
                ]
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                val = result.stdout.strip()
            
            return int(val) if val and val != "N/A" else 0
        except (subprocess.CalledProcessError, ValueError):
            return 0

    @staticmethod
    def reencode_to_optimal(input_path: str, output_path: str, bitrate: str = "48k") -> bool:
        """Re-encodes the audio to an optimal bitrate for transcription."""
        try:
            print(f"      - Re-encoding {input_path} at {bitrate} (optimal)...")
            command = [
                "ffmpeg", "-y", "-i", input_path,
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
    def remove_silence(input_path: str, output_path: str, threshold_db: int = -50) -> bool:
        """Removes silence from the audio using ffmpeg silenceremove filter."""
        try:
            print(f"      - Removing silence (threshold: {threshold_db}dB)...")
            # silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-50dB
            # This removes all silence periods longer than 1s that are below -50dB
            command = [
                "ffmpeg", "-y", "-i", input_path,
                "-af", f"silenceremove=stop_periods=-1:stop_duration=1:stop_threshold={threshold_db}dB",
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error during silence removal: {e.stderr.decode('utf-8', errors='replace')}")
            return False

    @staticmethod
    def split_into_chunks(input_path: str, output_pattern: str, segment_time: int = 1800) -> List[str]:
        """
        Splits the audio into chunks of specified duration (default 1800s / 30m).
        Returns a list of paths to the created chunks.
        """
        try:
            print(f"      - Splitting into chunks of {segment_time}s...")
            command = [
                "ffmpeg", "-y", "-i", input_path,
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
    def process_for_transcription(input_path: str, limit_mb: int = 20, segment_time: int = 1800, output_dir: str = "temp") -> List[str]:
        """
        Orchestrates the audio processing.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 1. First, always remove silence and re-encode to optimal bitrate
        print(f"   - Preparing audio for transcription...")
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        extension = os.path.splitext(input_path)[1] or ".mp3"
        
        prepared_path = os.path.join(output_dir, f"{base_name}_prepared{extension}")
        
        # Intermediate path for silence removal
        silence_removed_path = prepared_path + ".nosilence" + extension
        if AudioProcessor.remove_silence(input_path, silence_removed_path):
            if not AudioProcessor.reencode_to_optimal(silence_removed_path, prepared_path):
                # If re-encoding fails, use silence removed version
                shutil.copy2(silence_removed_path, prepared_path)
            try: os.remove(silence_removed_path)
            except: pass
        else:
            # If silence removal fails, try re-encoding original
            if not AudioProcessor.reencode_to_optimal(input_path, prepared_path):
                # If both fail, use original
                shutil.copy2(input_path, prepared_path)

        # 2. Check size and split if needed
        size_mb = AudioProcessor.get_file_size(prepared_path) / (1024 * 1024)
        if size_mb < limit_mb:
            print(f"   - Processed file size ({size_mb:.2f}MB) is within limit.")
            return [prepared_path]

        print(f"   - Processed file size ({size_mb:.2f}MB) still exceeds limit. Splitting...")
        output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d{extension}")
        
        chunks = AudioProcessor.split_into_chunks(prepared_path, output_pattern, segment_time)
        print(f"   - Split into {len(chunks)} chunks.")
        
        return chunks
