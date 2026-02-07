import os
import sys
import pytest
import shutil
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleanup_service import FileCleanupService

@pytest.fixture
def temp_workspace():
    # Setup
    os.makedirs("temp_test", exist_ok=True)
    os.makedirs("downloads_test", exist_ok=True)
    
    # Create some files
    with open("temp_test/job_1_chunk_001.mp3", 'w') as f: f.write("c1")
    with open("temp_test/job_2_chunk_001.mp3", 'w') as f: f.write("c2")
    with open("downloads_test/Test_Job_1.mp3", 'w') as f: f.write("audio1")
    with open("downloads_test/Test_Job_2.mp3", 'w') as f: f.write("audio2")
    
    yield "temp_test", "downloads_test"
    
    # Teardown
    if os.path.exists("temp_test"): shutil.rmtree("temp_test")
    if os.path.exists("downloads_test"): shutil.rmtree("downloads_test")

def test_targeted_cleanup(temp_workspace):
    temp_dir, downloads_dir = temp_workspace
    
    # Job 1 is completed (purge), Job 2 is pending (keep)
    jobs_to_purge = [
        {"id": "1", "name": "Test Job 1", "status": "completed"}
    ]
    
    with patch("src.downloader.get_expected_audio_path") as mock_path:
        # We need to return paths relative to our test downloads dir
        mock_path.side_effect = lambda j: os.path.join(downloads_dir, f"{j['name'].replace(' ', '_')}.mp3")
        
        FileCleanupService.cleanup_all_temp_files(
            temp_dir=temp_dir, 
            downloads_dir=downloads_dir, 
            jobs_to_purge=jobs_to_purge
        )
        
        # Verify Job 1 files are GONE
        assert not os.path.exists(os.path.join(temp_dir, "job_1_chunk_001.mp3"))
        assert not os.path.exists(os.path.join(downloads_dir, "Test_Job_1.mp3"))
        
        # Verify Job 2 files are KEPT
        assert os.path.exists(os.path.join(temp_dir, "job_2_chunk_001.mp3"))
        assert os.path.exists(os.path.join(downloads_dir, "Test_Job_2.mp3"))
