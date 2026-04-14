import logging
import sys
from src.rclone_service import RcloneService

# Configure logging to see the service output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def verify_phase_2():
    print("Verifying Phase 2: Rclone Service Implementation...")
    service = RcloneService()
    
    # 1. Verify success/failure return structure
    # We'll use a likely non-existent local file to test failure handling
    success, message = service.push_note("non_existent_file_xyz.txt", "remote:path")
    print(f"Push result (expected failure): success={success}")
    print(f"Message: {message}")
    
    if success is False and "failed" in message.lower():
        print("PASSED: Error handling for missing file works as expected")
        return True
    else:
        print("FAILED: Unexpected result for non-existent file")
        return False

if __name__ == "__main__":
    success = verify_phase_2()
    if not success:
        sys.exit(1)
