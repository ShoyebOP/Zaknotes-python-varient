import sys
import os
import pytest
import json
from unittest.mock import patch, MagicMock, mock_open

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.link_extractor import parse_netscape_cookies, extract_link

@pytest.fixture
def mock_cookie_file(tmp_path):
    cookie_content = (
        "# Netscape HTTP Cookie File\n"
        "example.com\tFALSE\t/\tFALSE\t0\tname\tvalue\n"
        ".example.org\tTRUE\t/path\tTRUE\t1234567890\tname2\tvalue2\n"
        "#HttpOnly_example.net\tFALSE\t/\tTRUE\t0\tname3\tvalue3\n"
    )
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text(cookie_content)
    return str(cookie_file)

def test_parse_netscape_cookies(mock_cookie_file):
    cookies = parse_netscape_cookies(mock_cookie_file)
    assert len(cookies) == 3
    
    assert cookies[0]['name'] == 'name'
    assert cookies[0]['value'] == 'value'
    assert cookies[0]['domain'] == 'example.com'
    assert cookies[0]['path'] == '/'
    assert cookies[0]['secure'] is False
    assert cookies[0]['httpOnly'] is False

    assert cookies[1]['name'] == 'name2'
    assert cookies[1]['value'] == 'value2'
    assert cookies[1]['domain'] == '.example.org'
    assert cookies[1]['path'] == '/path'
    assert cookies[1]['secure'] is True
    assert cookies[1]['httpOnly'] is False

    assert cookies[2]['name'] == 'name3'
    assert cookies[2]['value'] == 'value3'
    assert cookies[2]['domain'] == 'example.net'
    assert cookies[2]['path'] == '/'
    assert cookies[2]['secure'] is True
    assert cookies[2]['httpOnly'] is True

def test_parse_netscape_cookies_not_found():
    with pytest.raises(SystemExit):
        parse_netscape_cookies("nonexistent.txt")

@patch('src.link_extractor.sync_playwright')
def test_extract_link_success(mock_playwright, mock_cookie_file):
    # Mocking Playwright's complex structure
    mock_p = mock_playwright.return_value.__enter__.return_value
    mock_browser = mock_p.chromium.launch.return_value
    mock_context = mock_browser.new_context.return_value
    mock_page = mock_context.new_page.return_value
    
    # Mock frames
    mock_frame1 = MagicMock()
    mock_frame1.url = 'https://player.vimeo.com/video/123?autoplay=1'
    mock_page.frames = [mock_frame1]
    
    link = extract_link('https://example.com', mock_cookie_file)
    assert link == 'https://player.vimeo.com/video/123'
    mock_browser.new_context.assert_called()

@patch('src.link_extractor.sync_playwright')
def test_extract_link_no_links(mock_playwright, mock_cookie_file):
    mock_p = mock_playwright.return_value.__enter__.return_value
    mock_browser = mock_p.chromium.launch.return_value
    mock_context = mock_browser.new_context.return_value
    mock_page = mock_context.new_page.return_value
    
    mock_page.frames = []
    
    link = extract_link('https://example.com', mock_cookie_file)
    assert link is None

@patch('src.link_extractor.sync_playwright')
@patch('src.link_extractor.select_with_timeout')
def test_extract_link_multiple_links(mock_select, mock_playwright, mock_cookie_file):
    mock_p = mock_playwright.return_value.__enter__.return_value
    mock_browser = mock_p.chromium.launch.return_value
    mock_context = mock_browser.new_context.return_value
    mock_page = mock_context.new_page.return_value
    
    mock_frame1 = MagicMock()
    mock_frame1.url = 'https://player.vimeo.com/video/1'
    mock_frame2 = MagicMock()
    mock_frame2.url = 'https://player.vimeo.com/video/2'
    mock_page.frames = [mock_frame1, mock_frame2]
    
    mock_select.return_value = 'https://player.vimeo.com/video/2'
    
    link = extract_link('https://example.com', mock_cookie_file)
    assert link == 'https://player.vimeo.com/video/2'
    mock_select.assert_called_once()

def test_parse_netscape_cookies_empty(tmp_path):
    cookie_file = tmp_path / "empty_cookies.txt"
    cookie_file.write_text("")
    cookies = parse_netscape_cookies(str(cookie_file))
    assert len(cookies) == 0

def test_main_function(mock_cookie_file):
    with patch('sys.argv', ['link_extractor.py', '--url', 'https://example.com', '--cookies', mock_cookie_file]):
        with patch('src.link_extractor.extract_link', return_value='https://player.vimeo.com/video/123') as mock_extract:
            with patch('sys.exit') as mock_exit:
                from src.link_extractor import main
                main()
                mock_extract.assert_called_with('https://example.com', mock_cookie_file, None)
                mock_exit.assert_called_with(0)

def test_main_function_no_link(mock_cookie_file):
    with patch('sys.argv', ['link_extractor.py', '--url', 'https://example.com', '--cookies', mock_cookie_file]):
        with patch('src.link_extractor.extract_link', return_value=None) as mock_extract:
            with patch('sys.exit') as mock_exit:
                from src.link_extractor import main
                main()
                mock_extract.assert_called_with('https://example.com', mock_cookie_file, None)
                mock_exit.assert_called_with(1)