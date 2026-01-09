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
