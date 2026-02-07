import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_key_manager import APIKeyManager
from src.gemini_api_wrapper import GeminiAPIWrapper

TEST_KEYS_FILE = "keys/test_proactive_keys.json"

@pytest.fixture
def api_setup():
    os.makedirs("keys", exist_ok=True)
    if os.path.exists(TEST_KEYS_FILE):
        os.remove(TEST_KEYS_FILE)
    
    manager = APIKeyManager(keys_file=TEST_KEYS_FILE)
    manager.add_key("test-key")
    wrapper = GeminiAPIWrapper(key_manager=manager)
    
    yield manager, wrapper
    
    if os.path.exists(TEST_KEYS_FILE):
        os.remove(TEST_KEYS_FILE)

def test_proactive_increment_before_request(api_setup):
    """Test that quota is incremented BEFORE the request is made."""
    manager, wrapper = api_setup
    model = wrapper.MODELS["note"]
    
    # Mock the client.models.generate_content to check usage inside the call
    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        def side_effect(*args, **kwargs):
            # Check usage DURING the request
            keys = manager.list_keys()
            assert keys[0]["usage"][model] == 1
            return MagicMock(text="response")
            
        mock_client.models.generate_content.side_effect = side_effect
        
        wrapper.generate_content("test prompt", model_type="note")
        
        # Check usage AFTER the request (should still be 1, not 2)
        keys = manager.list_keys()
        assert keys[0]["usage"][model] == 1

def test_failed_request_keeps_increment(api_setup):
    """Test that failed requests still consume quota."""
    manager, wrapper = api_setup
    model = wrapper.MODELS["note"]
    
    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API Failure")
        
        with pytest.raises(Exception, match="API Failure"):
            wrapper.generate_content("test prompt", model_type="note")
            
        # Usage should be 1 despite the failure
        keys = manager.list_keys()
        assert keys[0]["usage"][model] == 1
