import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.notion_service import NotionService

@pytest.fixture
def mock_notion_client():
    with patch('src.notion_service.Client') as mock:
        yield mock

def test_notion_service_initialization(mock_notion_client):
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    mock_notion_client.assert_called_once_with(auth="test_secret")
    assert service.database_id == "test_db"

def test_notion_service_check_connection_success(mock_notion_client):
    mock_instance = mock_notion_client.return_value
    mock_instance.databases.retrieve.return_value = {"id": "test_db"}
    
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    assert service.check_connection() is True
    mock_instance.databases.retrieve.assert_called_once_with(database_id="test_db")

def test_notion_service_check_connection_failure(mock_notion_client):
    mock_instance = mock_notion_client.return_value
    mock_instance.databases.retrieve.side_effect = Exception("API Error")
    
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    assert service.check_connection() is False
