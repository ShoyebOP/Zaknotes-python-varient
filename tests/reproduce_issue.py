import os
import sys
import pytest
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_api_wrapper import GeminiAPIWrapper

def test_client_initialization_success():
    """Verifies that genai.Client initializes successfully with http_options."""
    mock_key_manager = MagicMock()
    mock_key_manager.get_available_key.return_value = "dummy-key"
    
    wrapper = GeminiAPIWrapper(key_manager=mock_key_manager)
    
    # This should NOT raise TypeError now
    client, api_key = wrapper._get_client("transcription")
    
    assert api_key == "dummy-key"
    assert client is not None
    print("Successfully initialized genai.Client")

if __name__ == "__main__":
    test_client_initialization_success()
