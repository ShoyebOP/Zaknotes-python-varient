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

def test_markdown_to_blocks_simple():
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    md = "# Heading 1\n\nThis is a paragraph.\n\n- Bullet 1\n- Bullet 2"
    blocks = service.markdown_to_blocks(md)
    
    assert len(blocks) == 4
    assert blocks[0]["type"] == "heading_1"
    assert blocks[0]["heading_1"]["rich_text"][0]["text"]["content"] == "Heading 1"
    assert blocks[1]["type"] == "paragraph"
    assert blocks[1]["paragraph"]["rich_text"][0]["text"]["content"] == "This is a paragraph."
    assert blocks[2]["type"] == "bulleted_list_item"
    assert blocks[3]["type"] == "bulleted_list_item"

def test_inline_formatting_bold_italic():
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    text = "This is **bold** and *italic* and `code`."
    rich_text = service.process_inline_formatting(text)
    
    # We expect multiple segments
    # 1. "This is " (plain)
    # 2. "bold" (bold: True)
    # 3. " and " (plain)
    # 4. "italic" (italic: True)
    # 5. " and " (plain)
    # 6. "code" (code: True)
    # 7. "." (plain)
    
    assert len(rich_text) > 1
    
    # Find segments (simplistic check)
    contents = [rt["text"]["content"] for rt in rich_text]
    assert "bold" in contents
    assert "italic" in contents
    assert "code" in contents
    
    for rt in rich_text:
        content = rt["text"]["content"]
        annotations = rt.get("annotations", {})
        if content == "bold":
            assert annotations.get("bold") is True
        elif content == "italic":
            assert annotations.get("italic") is True
        elif content == "code":
            assert annotations.get("code") is True

def test_markdown_to_blocks_latex_and_table():
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    md = """Inline $E=mc^2$
$$
x^2 + y^2 = z^2
$$

| H1 | H2 |
|---|---|
| R1C1 | R1C2 |
"""
    blocks = service.markdown_to_blocks(md)
    
    # Blocks:
    # 0. Paragraph with inline math
    # 1. Equation block
    # 2. Equation block (table)
    
    assert len(blocks) == 3
    assert blocks[0]["type"] == "paragraph"
    assert blocks[0]["paragraph"]["rich_text"][1]["type"] == "equation"
    assert blocks[0]["paragraph"]["rich_text"][1]["equation"]["expression"] == "E=mc^2"
    
    assert blocks[1]["type"] == "equation"
    assert blocks[1]["equation"]["expression"] == "x^2 + y^2 = z^2"
    
    assert blocks[2]["type"] == "equation"
    assert "\\begin{array}" in blocks[2]["equation"]["expression"]
    assert "R1C1" in blocks[2]["equation"]["expression"]

def test_notion_service_create_page_batching(mock_notion_client):
    mock_instance = mock_notion_client.return_value
    mock_instance.pages.create.return_value = {"id": "new_page_id", "url": "http://notion.so/new_page"}
    
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    
    # Create 150 blocks to trigger batching
    blocks = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}] * 150
    
    with patch.object(service, 'markdown_to_blocks', return_value=blocks):
        url = service.create_page(title="Test Page", markdown_text="some md")
    
    assert url == "http://notion.so/new_page"
    # Should call pages.create once
    mock_instance.pages.create.assert_called_once()
    # Should call blocks.children.append once for the remaining 50 blocks
    mock_instance.blocks.children.append.assert_called_once()
    args, kwargs = mock_instance.blocks.children.append.call_args
    assert kwargs["block_id"] == "new_page_id"
    assert len(kwargs["children"]) == 50

def test_notion_service_create_page_retry_on_429(mock_notion_client):
    from notion_client import APIResponseError
    
    mock_instance = mock_notion_client.return_value
    
    # Create a mock 429 error
    mock_response = MagicMock()
    mock_response.status_code = 429
    error_429 = APIResponseError(mock_response, "Rate limit", "rate_limit_reached")
    
    # Fail once, then succeed
    mock_instance.databases.retrieve.return_value = {"properties": {"Name": {"type": "title"}}}
    mock_instance.pages.create.side_effect = [error_429, {"id": "success_id", "url": "http://success"}]
    
    service = NotionService(notion_secret="test_secret", database_id="test_db")
    
    with patch('time.sleep') as mock_sleep:
        url = service.create_page("Retry Test", "md")
    
    assert url == "http://success"
    assert mock_instance.pages.create.call_count == 2
    mock_sleep.assert_called_once()
