import os
import json
import pytest
import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_key_manager import APIKeyManager

TEST_KEYS_FILE = "keys/test_api_keys.json"

@pytest.fixture
def key_manager():
    # Ensure keys directory exists for test file
    os.makedirs("keys", exist_ok=True)
    if os.path.exists(TEST_KEYS_FILE):
        os.remove(TEST_KEYS_FILE)
    manager = APIKeyManager(keys_file=TEST_KEYS_FILE)
    yield manager
    if os.path.exists(TEST_KEYS_FILE):
        os.remove(TEST_KEYS_FILE)

def test_add_and_list_keys(key_manager):
    """Test adding and listing API keys."""
    key_manager.add_key("key-1")
    key_manager.add_key("key-2")
    keys = key_manager.list_keys()
    assert len(keys) == 2
    assert "key-1" in [k["key"] for k in keys]
    assert "key-2" in [k["key"] for k in keys]

def test_remove_key(key_manager):
    """Test removing an API key."""
    key_manager.add_key("key-1")
    key_manager.add_key("key-2")
    key_manager.remove_key("key-1")
    keys = key_manager.list_keys()
    assert len(keys) == 1
    assert keys[0]["key"] == "key-2"

def test_get_available_key_simple(key_manager):
    """Test getting an available key when quotas are fresh."""
    key_manager.add_key("key-1")
    key = key_manager.get_available_key("gemini-2.5-flash")
    assert key == "key-1"

def test_quota_tracking(key_manager):
    """Test that usage is tracked correctly."""
    key_manager.add_key("key-1")
    model = "gemini-2.5-flash"
    
    # Use 5 requests
    for _ in range(5):
        key_manager.get_available_key(model)
        key_manager.record_usage("key-1", model)
        
    keys = key_manager.list_keys()
    assert keys[0]["usage"][model] == 5

def test_key_cycling_when_quota_hit(key_manager):
    """Test that it cycles to next key when quota is hit."""
    key_manager.add_key("key-1")
    key_manager.add_key("key-2")
    model = "gemini-2.5-flash"
    
    # Max out key-1 (20 requests)
    for _ in range(20):
        key_manager.record_usage("key-1", model)
        
    # Should now return key-2
    key = key_manager.get_available_key(model)
    assert key == "key-2"

def test_no_keys_available(key_manager):
    """Test behavior when all keys have hit quota."""
    key_manager.add_key("key-1")
    model = "gemini-2.5-flash"
    
    for _ in range(20):
        key_manager.record_usage("key-1", model)
        
    key = key_manager.get_available_key(model)
    assert key is None

def test_mark_exhausted(key_manager):
    """Test marking a key as exhausted."""
    key_manager.add_key("key-1")
    model = "gemini-2.5-flash"
    key_manager.mark_exhausted("key-1", model)
    
    # get_available_key should skip it even if usage is 0
    key = key_manager.get_available_key(model)
    assert key is None

def test_get_status_report(key_manager):
    """Test the status report formatting."""
    key_manager.add_key("key-123456789")
    model = "gemini-2.5-flash"
    key_manager.record_usage("key-123456789", model)
    key_manager.mark_exhausted("key-123456789", "gemini-3-flash-preview")
    
    report = key_manager.get_status_report()
    assert len(report) == 1
    assert "key-...6789" in report[0]
    assert "gemini-2.5-flash: 1/20" in report[0]
    assert "gemini-3-flash-preview: 0/20 [EXHAUSTED]" in report[0]

def test_quota_reset_at_midnight_pt(key_manager):
    """Test that quotas and exhausted flags reset at PT midnight."""
    key_manager.add_key("key-1")
    model = "gemini-2.5-flash"
    
    # Use some quota and mark exhausted on day 1
    key_manager.record_usage("key-1", model)
    key_manager.mark_exhausted("key-1", model)
    
    # Mock current time to be next day PT
    with patch('src.api_key_manager.APIKeyManager._get_current_time_pt') as mock_time:
        # Day 1
        mock_time.return_value = datetime(2026, 2, 3, 12, 0, tzinfo=timezone(timedelta(hours=-8)))
        key_manager.reset_quotas_if_needed()
        assert key_manager.list_keys()[0]["usage"][model] == 1
        assert key_manager.list_keys()[0]["exhausted"][model] is True
        
        # Day 2
        mock_time.return_value = datetime(2026, 2, 4, 0, 1, tzinfo=timezone(timedelta(hours=-8)))
        key_manager.reset_quotas_if_needed()
        assert key_manager.list_keys()[0]["usage"][model] == 0
        assert key_manager.list_keys()[0]["exhausted"][model] is False

def test_round_robin_rotation(key_manager):
    """Test that it rotates through available keys on every call."""
    key_manager.add_key("key-1")
    key_manager.add_key("key-2")
    key_manager.add_key("key-3")
    model = "gemini-2.5-flash"
    
    assert key_manager.get_available_key(model) == "key-1"
    assert key_manager.get_available_key(model) == "key-2"
    assert key_manager.get_available_key(model) == "key-3"
    assert key_manager.get_available_key(model) == "key-1"

