import os
import sys
import logging
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_api_wrapper import GeminiAPIWrapper
from src.api_key_manager import APIKeyManager

@pytest.fixture
def api_setup():
    manager = MagicMock(spec=APIKeyManager)
    manager.get_available_key.return_value = "test-key-long-enough"
    wrapper = GeminiAPIWrapper(key_manager=manager)
    return manager, wrapper

def test_debug_logging_content(api_setup, caplog):
    """Test that debug logs contain expected info and truncated content."""
    manager, wrapper = api_setup
    caplog.set_level(logging.DEBUG)
    
    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="This is a very long response that should be truncated in the logs for readability.")
        
        wrapper.generate_content("This is a very long prompt that should also be truncated in the logs.", model_type="note")
        
        # Check logs
        log_text = caplog.text
        assert "Gemini API Request - Type: note" in log_text
        assert "Key: test...ough" in log_text
        assert "Prompt (truncated): This is a very long prompt" in log_text
        assert "Gemini API Response - Success" in log_text
        assert "Response (truncated): This is a very long response" in log_text

def test_debug_logging_error(api_setup, caplog):
    """Test that debug logs contain error info."""
    manager, wrapper = api_setup
    caplog.set_level(logging.DEBUG)
    
    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Custom Error Message")
        
        with pytest.raises(Exception):
            wrapper.generate_content("prompt", model_type="note")
            
        log_text = caplog.text
        assert "Gemini API Response - Exception" in log_text
        assert "Error: Custom Error Message" in log_text
