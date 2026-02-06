import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.downloader import download_audio
from src.config_manager import ConfigManager

@pytest.fixture
def mock_config():
    with patch('src.downloader.ConfigManager') as mock:
        instance = mock.return_value
        instance.get.return_value = "TestUserAgent/1.0"
        yield instance

@pytest.fixture
def mock_run():
    with patch('subprocess.run') as mock:
        mock.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock

def test_download_audio_uses_configured_ua(mock_config, mock_run):
    """Test that download_audio uses the User-Agent from config."""
    job = {'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'name': 'test_job'}
    
    # We need to bypass the actual download
    # The current download_audio doesn't take config as input, it creates one
    # So we patched ConfigManager in src.downloader
    
    download_audio(job)
    
    # Check if any of the calls to subprocess.run contained the User-Agent
    found_ua = False
    for call in mock_run.call_args_list:
        args = call[0][0]
        cmd_str = " ".join(args) if isinstance(args, list) else args
        if "TestUserAgent/1.0" in cmd_str:
            found_ua = True
            break
    
    assert found_ua, "Configured User-Agent not found in any yt-dlp command"
