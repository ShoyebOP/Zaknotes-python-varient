import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.downloader import download_audio

def test_get_cookie_path_exists(tmp_path, monkeypatch):
    from src.downloader import get_cookie_path
    cookie_dir = tmp_path / "cookies"
    cookie_dir.mkdir()
    specific_cookie = cookie_dir / "test_client.txt"
    specific_cookie.write_text("cookie data")
    
    # Mock COOKIES_DIR and DEFAULT_COOKIE constants
    monkeypatch.setattr('src.downloader.COOKIES_DIR', str(cookie_dir))
    monkeypatch.setattr('src.downloader.DEFAULT_COOKIE', str(cookie_dir / "bangi.txt"))
    
    assert get_cookie_path("test_client") == str(specific_cookie)

def test_get_cookie_path_default(tmp_path, monkeypatch):
    from src.downloader import get_cookie_path
    cookie_dir = tmp_path / "cookies"
    cookie_dir.mkdir()
    default_cookie = cookie_dir / "bangi.txt"
    default_cookie.write_text("default cookie data")
    
    monkeypatch.setattr('src.downloader.COOKIES_DIR', str(cookie_dir))
    monkeypatch.setattr('src.downloader.DEFAULT_COOKIE', str(default_cookie))
    
    assert get_cookie_path("nonexistent") == str(default_cookie)

def test_run_command_success():
    from src.downloader import run_command
    with patch('subprocess.run') as mock_sub:
        mock_sub.return_value = MagicMock(returncode=0, stdout="Success Output", stderr="")
        assert run_command("echo test") == "Success Output"

def test_run_command_failure():
    from src.downloader import run_command
    with patch('subprocess.run') as mock_sub:
        mock_sub.return_value = MagicMock(returncode=1, stdout="", stderr="Error Message")
        with pytest.raises(Exception, match="Error Message"):
            run_command("false")

@pytest.fixture
def mock_job():
    return {
        "id": "test_id",
        "name": "Test Job",
        "url": "https://example.com/video"
    }

@patch('src.downloader.run_command')
@patch('src.downloader.get_cookie_path')
def test_download_facebook(mock_cookies, mock_run, mock_job):
    mock_job['url'] = "https://facebook.com/video/123"
    mock_cookies.return_value = "cookies/bangi.txt"
    
    download_audio(mock_job)
    
    # Verify yt-dlp was called
    args = mock_run.call_args[0][0]
    assert "facebook.com" in args
    assert "--cookies \"cookies/bangi.txt\"" in args

@patch('src.downloader.run_command')
@patch('src.downloader.get_cookie_path')
def test_download_youtube(mock_cookies, mock_run, mock_job):
    mock_job['url'] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_cookies.return_value = "cookies/bangi.txt"
    
    download_audio(mock_job)
    
    args = mock_run.call_args[0][0]
    # YouTube should use the fallback logic according to spec
    assert "youtube.com" in args
    assert "Referer: https://www.youtube.com/" in args

@patch('src.downloader.run_command')
@patch('src.downloader.get_cookie_path')
def test_download_mediadelivery(mock_cookies, mock_run, mock_job):
    # SPEC: mediadelivery.net link provided directly
    mock_job['url'] = "https://iframe.mediadelivery.net/embed/123/456"
    mock_cookies.return_value = "cookies/bangi.txt"
    
    download_audio(mock_job)
    
    args = mock_run.call_args[0][0]
    assert "mediadelivery.net" in args
    assert "Referer: https://academic.aparsclassroom.com/" in args
    assert "Origin: https://academic.aparsclassroom.com" in args

@patch('src.downloader.run_command')
@patch('src.downloader.get_cookie_path')
def test_download_edgecoursebd(mock_cookies, mock_run, mock_job):
    mock_job['url'] = "https://edgecoursebd.com/video"
    mock_cookies.return_value = "cookies/bangi.txt"
    
    # Mock the scraper run_command
    # First call is scraper, second is yt-dlp
    mock_run.side_effect = ["https://player.vimeo.com/video/999", "Done"]
    
    download_audio(mock_job)
    
    assert mock_run.call_count == 2
    scraper_call = mock_run.call_args_list[0][0][0]
    assert "link_extractor.py" in scraper_call
    
    yt_dlp_call = mock_run.call_args_list[1][0][0]
    assert "player.vimeo.com" in yt_dlp_call

@patch('src.downloader.run_command')
@patch('src.downloader.get_cookie_path')
def test_download_fallback_failure(mock_cookies, mock_run, mock_job):
    mock_job['url'] = "https://unknown-domain.com/video"
    mock_cookies.return_value = "cookies/bangi.txt"
    
    # Simulate yt-dlp failure
    mock_run.side_effect = Exception("Download failed")
    
    with pytest.raises(Exception):
        download_audio(mock_job)
    
    # Verify it tried the generic command
    args = mock_run.call_args[0][0]
    assert "unknown-domain.com" in args
