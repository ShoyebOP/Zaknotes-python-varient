import os
import sys
import pytest
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleanup_service import FileCleanupService

def test_cleanup_job_files(tmp_path):
    """Test deletion of specific files."""
    f1 = tmp_path / "test1.txt"
    f1.write_text("content")
    f2 = tmp_path / "test2.txt"
    f2.write_text("content")
    
    FileCleanupService.cleanup_job_files([str(f1), str(f2)])
    
    assert not os.path.exists(f1)
    assert not os.path.exists(f2)

def test_cleanup_uploads(tmp_path):
    """Test purging of the uploads directory."""
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    (uploads_dir / "class1.mp3").write_text("audio")
    (uploads_dir / "class2.mp4").write_text("video")
    (uploads_dir / ".gitkeep").write_text("")
    
    FileCleanupService.cleanup_uploads(uploads_dir=str(uploads_dir))
    
    assert not os.path.exists(uploads_dir / "class1.mp3")
    assert not os.path.exists(uploads_dir / "class2.mp4")
    assert os.path.exists(uploads_dir / ".gitkeep")

def test_cleanup_all_temp_files_including_uploads(tmp_path):
    """Test cleanup of all directories including uploads."""
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "junk.mp3").write_text("junk")
    
    down_dir = tmp_path / "downloads"
    down_dir.mkdir()
    (down_dir / "movie.mp3").write_text("movie")
    
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    (uploads_dir / "class.mp3").write_text("audio")
    
    # Run with include_uploads=True
    FileCleanupService.cleanup_all_temp_files(
        temp_dir=str(temp_dir), 
        downloads_dir=str(down_dir), 
        uploads_dir=str(uploads_dir),
        include_uploads=True
    )
    
    assert not os.path.exists(temp_dir / "junk.mp3")
    assert not os.path.exists(down_dir / "movie.mp3")
    assert not os.path.exists(uploads_dir / "class.mp3")

def test_cleanup_all_temp_files_excluding_uploads(tmp_path):
    """Test cleanup of all directories excluding uploads."""
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "junk.mp3").write_text("junk")
    
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    (uploads_dir / "class.mp3").write_text("audio")
    
    # Run with include_uploads=False (default)
    FileCleanupService.cleanup_all_temp_files(
        temp_dir=str(temp_dir), 
        uploads_dir=str(uploads_dir),
        include_uploads=False
    )
    
    assert not os.path.exists(temp_dir / "junk.mp3")
    assert os.path.exists(uploads_dir / "class.mp3") # Should STILL exist
