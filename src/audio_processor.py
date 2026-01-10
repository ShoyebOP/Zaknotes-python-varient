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
