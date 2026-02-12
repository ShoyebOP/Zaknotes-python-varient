import os
import json
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigManager
from src.notion_config_manager import NotionConfigManager

TEST_CONFIG_FILE = "test_config_notion.json"
TEST_NOTION_KEYS_FILE = "test_notion_keys.json"

@pytest.fixture
def config_manager():
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)
    manager = ConfigManager(config_file=TEST_CONFIG_FILE)
    yield manager
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)

@pytest.fixture
def notion_config_manager():
    if os.path.exists(TEST_NOTION_KEYS_FILE):
        os.remove(TEST_NOTION_KEYS_FILE)
    manager = NotionConfigManager(keys_file=TEST_NOTION_KEYS_FILE)
    yield manager
    if os.path.exists(TEST_NOTION_KEYS_FILE):
        os.remove(TEST_NOTION_KEYS_FILE)

def test_notion_integration_default_false(config_manager):
    """Test that notion_integration_enabled defaults to False."""
    assert config_manager.get("notion_integration_enabled") is False

def test_notion_config_load_save(notion_config_manager):
    """Test saving and loading Notion credentials."""
    notion_config_manager.set_credentials("secret_123", "db_456")
    
    # Reload with a new instance
    new_manager = NotionConfigManager(keys_file=TEST_NOTION_KEYS_FILE)
    secret, db_id = new_manager.get_credentials()
    assert secret == "secret_123"
    assert db_id == "db_456"

def test_notion_config_defaults(notion_config_manager):
    """Test default values for Notion credentials."""
    secret, db_id = notion_config_manager.get_credentials()
    assert secret == ""
    assert db_id == ""
