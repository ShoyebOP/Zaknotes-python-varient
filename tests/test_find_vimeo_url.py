import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.find_vimeo_url import extract_vimeo_url, parse_netscape_cookies

@pytest.fixture
def mock_cookie_file(tmp_path):
    cookie_content = (
        "example.com\tTRUE\t/\tFALSE\t2147483647\ttest_name\ttest_value\n"
        "example.com\tFALSE\t/\tTRUE\t2147483647\t__Host-test\thost_val\n"
    )
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text(cookie_content)
    return str(cookie_file)

def test_parse_netscape_cookies(mock_cookie_file):
    cookies = parse_netscape_cookies(mock_cookie_file, "example.com")
    assert len(cookies) == 2
    
    # Check standard cookie
    c1 = next(c for c in cookies if c['name'] == 'test_name')
    assert c1['domain'] == '.example.com'
    
    # Check __Host- cookie
    c2 = next(c for c in cookies if c['name'] == '__Host-test')
    assert c2['domain'] == 'example.com' # Should be host-only (no dot)
    assert c2['secure'] is True
    assert c2['path'] == '/'

@patch('src.find_vimeo_url.sync_playwright')
def test_extract_vimeo_url_success(mock_playwright, mock_cookie_file):
    # Setup mock playwright
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    mock_page.content.return_value = '<html><body><iframe src="https://player.vimeo.com/video/12345"></iframe></body></html>'
    
    url = "https://example.com/video"
    result = extract_vimeo_url(url, mock_cookie_file)
    
    assert result == "https://player.vimeo.com/video/12345"
    mock_page.goto.assert_called_with(url, wait_until="networkidle")
    mock_browser.close.assert_called_once()

@patch('src.find_vimeo_url.sync_playwright')
def test_extract_vidinfra_url_success(mock_playwright, mock_cookie_file):
    # Setup mock playwright
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    vidinfra_url = "https://player.vidinfra.com/67ffe06f-ca94-4c8d-a450-6e7eee26a702/default/f0eec8df-b3f9-4030-8391-0220af7e78ba?autoplay=false"
    mock_page.content.return_value = f'<html><body><iframe src="{vidinfra_url}"></iframe></body></html>'
    
    url = "https://example.com/video"
    result = extract_vimeo_url(url, mock_cookie_file)
    
    assert result == vidinfra_url
    mock_browser.close.assert_called_once()

@patch('src.find_vimeo_url.sync_playwright')
def test_extract_vimeo_url_no_iframe(mock_playwright, mock_cookie_file):
    # Setup mock playwright
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    mock_page.content.return_value = '<html><body><p>No iframe here</p></body></html>'
    
    url = "https://example.com/video"
    
    with pytest.raises(SystemExit) as cm:
        extract_vimeo_url(url, mock_cookie_file)
    
    assert cm.value.code == 1
    mock_browser.close.assert_called_once()

def test_parse_netscape_cookies_not_found():
    with pytest.raises(SystemExit) as cm:
        parse_netscape_cookies("nonexistent.txt", "example.com")
    assert cm.value.code == 1

def test_parse_netscape_cookies_malformed(tmp_path):
    f = tmp_path / "malformed.txt"
    f.write_text("not a cookie file")
    # This shouldn't necessarily exit if it just finds no matches
    cookies = parse_netscape_cookies(str(f), "example.com")
    assert len(cookies) == 0

@patch('src.find_vimeo_url.extract_vimeo_url')
@patch('src.find_vimeo_url.os.path.isfile')
def test_main_success(mock_isfile, mock_extract):
    from src.find_vimeo_url import main
    mock_isfile.return_value = True
    mock_extract.return_value = "https://player.vimeo.com/video/1"
    
    with patch('sys.argv', ['find_vimeo_url.py', '--url', 'http://test.com', '--cookies', 'cookies.txt']):
        with patch('sys.stdout', new=MagicMock()) as mock_stdout:
            with pytest.raises(SystemExit) as cm:
                main()
            assert cm.value.code == 0

@patch('src.find_vimeo_url.os.path.isfile')
def test_main_no_cookie_file(mock_isfile):
    from src.find_vimeo_url import main
    mock_isfile.return_value = False
    
    with patch('sys.argv', ['find_vimeo_url.py', '--url', 'http://test.com', '--cookies', 'nonexistent.txt']):
        with pytest.raises(SystemExit) as cm:
            main()
        assert cm.value.code == 1
