import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class RcloneService:
    def __init__(self):
        pass

    def push_note(self, local_path: str, remote_dest: str) -> Tuple[bool, str]:
        """
        Pushes a local file to a remote destination using rclone.
        
        Args:
            local_path: Path to the local file.
            remote_dest: Remote destination (e.g., 'remote:path').
            
        Returns:
            Tuple[bool, str]: (Success status, Result message)
        """
        try:
            cmd = ["rclone", "copy", local_path, remote_dest]
            logger.info(f"Executing rclone command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                check=False # We handle returncode manually
            )
            
            if result.returncode == 0:
                msg = f"Note successfully pushed to rclone destination: {remote_dest}"
                logger.info(msg)
                return True, msg
            else:
                error_msg = result.stderr.decode('utf-8').strip()
                msg = f"Rclone push failed with return code {result.returncode}: {error_msg}"
                logger.error(msg)
                return False, msg
                
        except Exception as e:
            msg = f"Unexpected error during rclone push: {str(e)}"
            logger.error(msg)
            return False, msg
