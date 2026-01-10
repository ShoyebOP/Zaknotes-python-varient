import os
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
    def reencode_audio(input_path: str, output_path: str, bitrate: str = "16k") -> bool:
        """Re-encodes the audio to a lower bitrate using ffmpeg."""
        try:
            command = [
                "ffmpeg", "-y", "-i", input_path,
                "-b:a", bitrate,
                output_path
            ]
            subprocess.run(command, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during re-encoding: {e.stderr.decode()}")
            return False

    @staticmethod
    def split_into_chunks(input_path: str, output_pattern: str, segment_time: int = 1800) -> List[str]:
        """
        Splits the audio into chunks of specified duration (default 1800s / 30m).
        Returns a list of paths to the created chunks.
        """
        try:
            command = [
                "ffmpeg", "-y", "-i", input_path,
                "-f", "segment",
                "-segment_time", str(segment_time),
                "-c", "copy",
                output_pattern
            ]
            subprocess.run(command, check=True, capture_output=True)
            
            # Find the created files
            directory = os.path.dirname(output_pattern) or "."
            # Base name without the format specifier
            # Handle cases like chunk_%03d.mp3
            base_parts = os.path.basename(output_pattern).split("%")
            prefix = base_parts[0]
            
            chunks = []
            for f in sorted(os.listdir(directory)):
                if f.startswith(prefix) and f != os.path.basename(input_path):
                     # Check if it matches the pattern (roughly)
                     chunks.append(os.path.join(directory, f))
            return chunks
            
        except subprocess.CalledProcessError as e:
            print(f"Error during splitting: {e.stderr.decode()}")
            return []

    @staticmethod
    def process_for_transcription(input_path: str, limit_mb: int = 20, segment_time: int = 1800, output_dir: str = "temp") -> List[str]:
        """
        Orchestrates the audio processing:
        1. Check size. If < limit, return [input_path].
        2. Else, split into chunks.
        3. For each chunk, if still > limit, re-encode with lower bitrate.
        4. Return list of chunk paths.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        if AudioProcessor.is_under_limit(input_path, limit_mb):
            return [input_path]

        # Needs splitting
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        extension = os.path.splitext(input_path)[1] or ".mp3"
        output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d{extension}")
        
        chunks = AudioProcessor.split_into_chunks(input_path, output_pattern, segment_time)
        
        final_chunks = []
        for chunk in chunks:
            if AudioProcessor.is_under_limit(chunk, limit_mb):
                final_chunks.append(chunk)
            else:
                # Still too large, re-encode
                reencoded_path = chunk.replace(extension, f"_reencoded{extension}")
                if AudioProcessor.reencode_audio(chunk, reencoded_path, bitrate="16k"):
                    if AudioProcessor.is_under_limit(reencoded_path, limit_mb):
                        final_chunks.append(reencoded_path)
                        try: os.remove(chunk)
                        except: pass
                    else:
                        final_chunks.append(reencoded_path)
                        try: os.remove(chunk)
                        except: pass
                else:
                    final_chunks.append(chunk)
                    
        return final_chunks
