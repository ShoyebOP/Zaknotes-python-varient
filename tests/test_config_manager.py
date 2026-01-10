import os
import json
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager

TEST_CONFIG_FILE = "test_config.json"

@pytest.fixture
def config_manager():
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)
    manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    yield manager
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)

def test_load_defaults(config_manager):
    """Test that defaults are loaded when config file does not exist."""
    assert config_manager.get("transcription_model") == "gemini-2.5-flash"
    assert config_manager.get("note_generation_model") == "gemini-3-pro-preview"

def test_save_and_load(config_manager):
    """Test saving and reloading configuration."""
    config_manager.set("transcription_model", "test-model")
    config_manager.save()
    
    # Reload with a new instance
    new_manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    assert new_manager.get("transcription_model") == "test-model"

def test_get_nonexistent_key(config_manager):
    """Test retrieving nonexistent keys with and without defaults."""
    assert config_manager.get("nonexistent") is None
    assert config_manager.get("nonexistent", "default") == "default"
