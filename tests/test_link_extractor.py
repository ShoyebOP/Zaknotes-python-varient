import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import queue

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.link_extractor import extract_link, parse_netscape_cookies

@pytest.fixture
def mock_cookie_file(tmp_path):
    cookie_content = (
        "example.com\tTRUE\t/\tFALSE\t2147483647\ttest_name\ttest_value\n"
        "example.com\tFALSE\t/\tTRUE\t2147483647\t__Host-test\thost_val\n"
        "another.com\tTRUE\t/\tFALSE\t2147483647\tanother_name\tanother_value\n"
    )
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text(cookie_content)
    return str(cookie_file)

def test_parse_netscape_cookies(mock_cookie_file):
    # Should now return ALL cookies regardless of domain argument
    cookies = parse_netscape_cookies(mock_cookie_file)
    assert len(cookies) == 3
    
    # Check standard cookie
    c1 = next(c for c in cookies if c['name'] == 'test_name')
    assert c1['domain'] == '.example.com'
    
    # Check __Host- cookie
    c2 = next(c for c in cookies if c['name'] == '__Host-test')
    assert c2['domain'] == 'example.com'
    assert c2['secure'] is True
    
    # Check another domain cookie
    c3 = next(c for c in cookies if c['name'] == 'another_name')
    assert c3['domain'] == '.another.com'

@patch('src.link_extractor.sync_playwright')
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
    
    vimeo_url = "https://player.vimeo.com/video/12345"
    mock_frame = MagicMock()
    mock_frame.url = vimeo_url
    mock_page.frames = [mock_frame]
    
    url = "https://example.com/video"
    result = extract_link(url, mock_cookie_file)
    
    assert result == vimeo_url
    mock_browser.close.assert_called_once()
    mock_page.wait_for_timeout.assert_called()

@patch('src.link_extractor.sync_playwright')
@patch('builtins.input', return_value='2')
def test_extract_multiple_links_selection(mock_input, mock_playwright, mock_cookie_file):
    mock_pw = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_pw
    mock_browser = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_page = MagicMock()
    mock_context.new_page.return_value = mock_page
    
    url1 = "https://player.vimeo.com/video/A1"
    url2 = "https://player.vimeo.com/video/B2"
    
    mock_frame1 = MagicMock()
    mock_frame1.url = url1
    
    mock_frame2 = MagicMock()
    mock_frame2.url = url2
    
    mock_page.frames = [mock_frame1, mock_frame2]
    
    url = "https://example.com/video"
    result = extract_link(url, mock_cookie_file)
    
    assert result == url2
    mock_input.assert_called()

def test_select_with_timeout_valid(monkeypatch):
    from src.link_extractor import select_with_timeout
    options = ["a", "b", "c"]
    monkeypatch.setattr('builtins.input', lambda _: "2")
    assert select_with_timeout(options, timeout=1) == "b"

def test_select_with_timeout_invalid(monkeypatch):
    from src.link_extractor import select_with_timeout
    options = ["a", "b", "c"]
    monkeypatch.setattr('builtins.input', lambda _: "invalid")
    assert select_with_timeout(options, timeout=1) == "a"

def test_select_with_timeout_empty_queue():
    from src.link_extractor import select_with_timeout
    options = ["a", "b", "c"]
    with patch('queue.Queue.get', side_effect=queue.Empty):
        assert select_with_timeout(options, timeout=0.1) == "a"

def test_parse_netscape_cookies_not_found():
    with pytest.raises(SystemExit) as e:
        parse_netscape_cookies("nonexistent.txt")
    assert e.value.code == 1

def test_parse_netscape_cookies_malformed(tmp_path):
    bad_file = tmp_path / "bad_cookies.txt"
    bad_file.write_text("malformed line")
    cookies = parse_netscape_cookies(str(bad_file))
    assert len(cookies) == 0

def test_main_function(mock_cookie_file):
    with patch('sys.argv', ['link_extractor.py', '--url', 'https://example.com', '--cookies', mock_cookie_file]):
        with patch('src.link_extractor.extract_link', return_value='https://player.vimeo.com/video/123') as mock_extract:
            with patch('sys.exit') as mock_exit:
                from src.link_extractor import main
                main()
                mock_extract.assert_called_with('https://example.com', mock_cookie_file)
                mock_exit.assert_called_with(0)

def test_main_function_no_link(mock_cookie_file):
    with patch('sys.argv', ['link_extractor.py', '--url', 'https://example.com', '--cookies', mock_cookie_file]):
        with patch('src.link_extractor.extract_link', return_value=None) as mock_extract:
            with patch('sys.exit') as mock_exit:
                from src.link_extractor import main
                main()
                mock_extract.assert_called_with('https://example.com', mock_cookie_file)
                mock_exit.assert_called_with(1)
