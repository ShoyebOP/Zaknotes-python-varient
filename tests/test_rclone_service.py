import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rclone_service import RcloneService

def test_rclone_service_exists():
    """Verify that RcloneService can be imported."""
    assert RcloneService is not None

@patch('subprocess.run')
def test_rclone_push_note_success(mock_run):
    """Test successful rclone push."""
    # Setup mock
    mock_run.return_value = MagicMock(returncode=0, stdout=b"Success", stderr=b"")
    
    service = RcloneService()
    success, message = service.push_note("local/path/note.md", "remote:path")
    
    assert success is True
    assert "successfully pushed" in message.lower()
    
    # Verify subprocess call
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "rclone" in args
    assert "copy" in args
    assert "local/path/note.md" in args
    assert "remote:path" in args

@patch('subprocess.run')
def test_rclone_push_note_failure(mock_run):
    """Test failed rclone push."""
    # Setup mock
    mock_run.return_value = MagicMock(returncode=1, stdout=b"", stderr=b"Error message")
    
    service = RcloneService()
    success, message = service.push_note("local/path/note.md", "remote:path")
    
    assert success is False
    assert "failed" in message.lower()
    assert "Error message" in message

@patch('subprocess.run')
def test_rclone_push_note_exception(mock_run):
    """Test exception during rclone push."""
    # Setup mock
    mock_run.side_effect = Exception("System error")
    
    service = RcloneService()
    success, message = service.push_note("local/path/note.md", "remote:path")
    
    assert success is False
    assert "unexpected error" in message.lower()
    assert "System error" in message
