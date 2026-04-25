import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.downloader import download_audio

@pytest.fixture
def vimeo_job():
    return {
        "id": "vimeo_test",
        "name": "Vimeo Direct Test",
        "url": "https://player.vimeo.com/video/123456789"
    }

@patch('src.downloader.run_command')
@patch('src.downloader.get_cookie_path')
@patch('src.downloader.ConfigManager')
def test_vimeo_direct_download_refinement(mock_config_class, mock_cookies, mock_run, vimeo_job):
    # Setup mock config
    mock_config = mock_config_class.return_value
    mock_config.get.return_value = "Test-User-Agent"
    
    # Mock that a cookie file EXISTS, but it should NOT be used for direct Vimeo
    mock_cookies.return_value = "cookies/bangi.txt"
    
    download_audio(vimeo_job)
    
    # Verify yt-dlp was called
    assert mock_run.called
    args = mock_run.call_args[0][0]
    
    # REQUIREMENTS:
    # 1. No cookies
    assert "--cookies" not in args, "Cookies should be disabled for direct Vimeo URLs"
    
    # 2. Specific Referer and Origin
    referer_found = False
    origin_found = False
    for i in range(len(args)):
        if args[i] == "--add-header":
            header = args[i+1]
            if header.startswith("Referer: https://vimeo.com/"):
                referer_found = True
            if header.startswith("Origin: https://vimeo.com"):
                origin_found = True
                
    assert referer_found, "Referer should be set to vimeo.com for direct Vimeo URLs"
    assert origin_found, "Origin should be set to vimeo.com for direct Vimeo URLs"
    
    # 3. User-Agent should still be there
    assert any("User-Agent: Test-User-Agent" in a for a in args)

if __name__ == "__main__":
    pytest.main([__file__])
