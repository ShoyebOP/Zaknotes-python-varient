import os
import sys
import time
import pytest
import httpx
from unittest.mock import patch, MagicMock
from google.genai import errors, types

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_api_wrapper import GeminiAPIWrapper
from src.api_key_manager import APIKeyManager
from src.config_manager import ConfigManager

@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigManager)
    config.get.side_effect = lambda key, default=None: {
        "api_timeout": 5,
        "api_max_retries": 1, # 1 retry only for faster test
        "api_retry_delay": 0.1
    }.get(key, default)
    return config

def test_rotation_on_timeout_exhaustion(tmp_path, mock_config):
    """Verify that rotation occurs after a key is exhausted due to timeouts."""
    keys_file = tmp_path / "api_keys.json"
    import json
    with open(keys_file, 'w') as f:
        json.dump({
            "keys": [
                {"key": "key-1", "usage": {"gemini-3-flash-preview": 0}, "exhausted": {"gemini-3-flash-preview": False}},
                {"key": "key-2", "usage": {"gemini-3-flash-preview": 0}, "exhausted": {"gemini-3-flash-preview": False}}
            ],
            "last_reset_date": "2026-02-09"
        }, f)
    
    # Mock _get_current_time_pt
    with patch.object(APIKeyManager, '_get_current_time_pt', return_value=MagicMock(strftime=lambda x: "2026-02-09")):
        key_manager = APIKeyManager(keys_file=str(keys_file))
        wrapper = GeminiAPIWrapper(key_manager=key_manager, config=mock_config)
        
        with patch('google.genai.Client') as mock_client_class, patch('time.sleep'):
            mock_client_1 = MagicMock()
            mock_client_2 = MagicMock()
            mock_client_class.side_effect = [mock_client_1, mock_client_2]
            
            # Key-1: Fail with timeout twice (initial + 1 retry)
            timeout_error = httpx.ReadTimeout("Timeout", request=MagicMock())
            mock_client_1.models.generate_content.side_effect = timeout_error
            
            # Key-2: Succeed
            mock_client_2.models.generate_content.return_value = MagicMock(text="Success with Key 2")
            
            response = wrapper.generate_content("test prompt")
            
            assert response == "Success with Key 2"
            
            # Key-1 should have been called 2 times (initial + 1 retry)
            assert mock_client_1.models.generate_content.call_count == 2
            # Key-2 should have been called 1 time
            assert mock_client_2.models.generate_content.call_count == 1
            
            # Verify Key-1 is marked exhausted
            keys = key_manager.list_keys()
            assert keys[0]["key"] == "key-1"
            assert keys[0]["exhausted"]["gemini-3-flash-preview"] is True
            assert keys[1]["key"] == "key-2"
            assert keys[1]["exhausted"]["gemini-3-flash-preview"] is False
