import os
import sys
import subprocess
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_wrapper import GeminiCLIWrapper

@patch('subprocess.run')
def test_run_command_success(mock_run):
    """Test successful command execution."""
    # We must mock bytes since the wrapper calls .decode()
    mock_run.return_value = MagicMock(
        stdout=b'{"response": "test"}', 
        stderr=b'', 
        returncode=0
    )
    
    result = GeminiCLIWrapper.run_command(["arg1", "arg2"])
    
    mock_run.assert_called_once()
    assert result['success'] is True
    assert result['stdout'] == '{"response": "test"}'

@patch('subprocess.run')
def test_run_command_failure(mock_run):
    """Test command failure."""
    # CalledProcessError expects bytes for stdout/stderr if they are provided
    mock_run.side_effect = subprocess.CalledProcessError(1, ['gemini'], stderr=b"error")
    
    result = GeminiCLIWrapper.run_command(["arg1"])
    
    assert result['success'] is False
    assert result['stderr'] == "error"

def test_extract_response_content_valid():
    """Test extraction from valid JSON."""
    raw = '{"response": "hello world"}'
    assert GeminiCLIWrapper.extract_response_content(raw) == "hello world"

def test_extract_response_content_truncated():
    """Test extraction from truncated JSON."""
    raw = '{"response": "hello world ... truncated'
    assert GeminiCLIWrapper.extract_response_content(raw) == "hello world ... truncated"

def test_extract_response_content_escaped():
    """Test extraction with escaped characters."""
    raw = r'{"response": "line1\nline2 with \"quote\""}'
    assert GeminiCLIWrapper.extract_response_content(raw) == 'line1\nline2 with "quote"'