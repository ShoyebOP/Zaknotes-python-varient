import pytest
from unittest.mock import MagicMock, patch, ANY
from bot_engine import AIStudioBot

@pytest.fixture
def mock_browser_driver():
    with patch('bot_engine.BrowserDriver') as MockDriver:
        driver_instance = MockDriver.return_value
        # Mock the page object
        mock_page = MagicMock()
        driver_instance.page = mock_page
        yield driver_instance

def test_bot_initialization(mock_browser_driver):
    bot = AIStudioBot()
    assert bot.driver == mock_browser_driver

def test_ensure_connection_navigates_to_new_chat(mock_browser_driver):
    bot = AIStudioBot()
    mock_browser_driver.page.url = "about:blank"
    mock_context = MagicMock()
    mock_browser_driver.context = mock_context
    mock_context.pages = []
    mock_context.new_page.return_value = mock_browser_driver.page
    bot.ensure_connection()
    mock_context.new_page.assert_called()
    mock_browser_driver.page.goto.assert_called_with("https://aistudio.google.com/prompts/new_chat")

def test_select_model_gemini_3_pro(mock_browser_driver):
    bot = AIStudioBot()
    mock_page = mock_browser_driver.page
    bot.page = mock_page
    mock_card = MagicMock()
    mock_card.text_content.return_value = "Gemini 3 Pro Preview"
    mock_page.wait_for_selector.return_value = mock_card
    bot.select_model()
    mock_page.wait_for_selector.assert_called()

def test_select_system_instruction(mock_browser_driver):
    bot = AIStudioBot()
    mock_page = mock_browser_driver.page
    bot.page = mock_page
    mock_card = MagicMock()
    mock_dropdown = MagicMock()
    mock_dropdown.text_content.return_value = "note generator"
    mock_page.wait_for_selector.side_effect = [mock_card, mock_dropdown]
    bot.select_system_instruction()
    mock_card.click.assert_called()

def test_generate_notes_success(mock_browser_driver):
    bot = AIStudioBot()
    mock_page = mock_browser_driver.page
    bot.page = mock_page
    
    # Simple, highly permissive mock
    m = MagicMock()
    m.is_enabled.return_value = True
    m.count.side_effect = [1, 0, 0, 0, 0, 0]
    m.locator.return_value = m
    m.filter.return_value = m
    m.first = m
    m.last = m
    m.get_by_text.return_value = m
    m.get_by_label.return_value = m
    
    mock_page.locator.return_value = m
    mock_page.get_by_label.return_value = m
    mock_page.get_by_text.return_value = m
    mock_page.evaluate.return_value = "# Final Response content"
    
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()):
        text, path = bot.generate_notes("test.mp3")
    
    assert text == "# Final Response content"
    assert m.click.called