import pytest
from unittest.mock import MagicMock, patch
from src.bot_engine import AIStudioBot
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

@pytest.fixture
def mock_bot():
    with patch('src.bot_engine.BrowserDriver'), patch('src.bot_engine.PdfConverter'):
        bot = AIStudioBot()
        bot.page = MagicMock()
        return bot

def test_select_model_already_selected(mock_bot):
    mock_card = MagicMock()
    mock_card.text_content.return_value = "Gemini 3 Pro Preview"
    mock_bot.page.wait_for_selector.return_value = mock_card
    
    mock_bot.select_model()
    
    mock_card.click.assert_not_called()

def test_select_model_switches_successfully(mock_bot):
    mock_card = MagicMock()
    mock_card.text_content.return_value = "Gemini 2.5 Pro"
    mock_target_btn = MagicMock()
    
    # CALL 1: card_selector
    # CALL 2: target_btn_selector
    mock_bot.page.wait_for_selector.side_effect = [mock_card, mock_target_btn]
    
    mock_bot.select_model()
    
    mock_card.click.assert_called_once()
    mock_target_btn.click.assert_called_once()

def test_select_system_instruction_already_selected(mock_bot):
    mock_card = MagicMock()
    mock_bot.page.wait_for_selector.return_value = mock_card
    
    mock_dropdown = MagicMock()
    mock_dropdown.text_content.return_value = "note generator"
    # CALL 1: card_selector
    # CALL 2: dropdown_selector
    mock_bot.page.wait_for_selector.side_effect = [mock_card, mock_dropdown]
    
    mock_bot.select_system_instruction()
    
    mock_card.click.assert_called_once()
    mock_dropdown.click.assert_not_called()

def test_select_system_instruction_fails_after_3_attempts(mock_bot):
    mock_card = MagicMock()
    # 1 for initial card, 3 for dropdown failures
    mock_bot.page.wait_for_selector.side_effect = [
        mock_card, 
        PlaywrightTimeoutError("timeout"),
        PlaywrightTimeoutError("timeout"),
        PlaywrightTimeoutError("timeout")
    ]
    
    with pytest.raises(Exception, match="after 3 attempts"):
        mock_bot.select_system_instruction()
    
    assert mock_card.click.call_count == 3

def test_select_system_instruction_retries_and_succeeds(mock_bot):
    mock_card = MagicMock()
    mock_dropdown = MagicMock()
    mock_dropdown.text_content.return_value = "note generator"
    
    # CALL 1: card
    # CALL 2: dropdown (fail)
    # CALL 3: dropdown (success)
    mock_bot.page.wait_for_selector.side_effect = [
        mock_card, 
        PlaywrightTimeoutError("timeout"),
        mock_dropdown
    ]
    
    mock_bot.select_system_instruction()
    
    assert mock_card.click.call_count == 2
    mock_dropdown.click.assert_not_called()

def test_generate_notes_success(mock_bot):
    # Mocking various components for generate_notes
    mock_bot.page.locator.return_value = MagicMock()
    mock_run_btn = MagicMock()
    mock_run_btn.is_enabled.return_value = True
    mock_bot.page.locator.return_value.first = mock_run_btn
    
    mock_stop_btn = MagicMock()
    mock_stop_btn.count.side_effect = [1, 0] # Generation starts, then finishes
    mock_bot.page.get_by_label.return_value = mock_stop_btn
    
    mock_last_turn = MagicMock()
    mock_bot.page.locator.return_value.filter.return_value.last = mock_last_turn
    
    mock_bot.page.evaluate.return_value = "Mocked AI Response"
    
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()), \
         patch('src.bot_engine.PdfConverter', MagicMock()):
        
        text, pdf_path = mock_bot.generate_notes("dummy.mp3")
        
        assert text == "Mocked AI Response"
        assert pdf_path is not None
        assert "dummy.pdf" in pdf_path

def test_generate_notes_timeout_waiting_for_run(mock_bot):
    # Mock run button never enabled
    mock_run_btn = MagicMock()
    mock_run_btn.is_enabled.return_value = False
    mock_bot.page.locator.return_value.first = mock_run_btn
    
    with patch('os.path.exists', return_value=True), \
         patch('time.sleep', MagicMock()): # Speed up test
        
        text, pdf_path = mock_bot.generate_notes("dummy.mp3")
        
        assert text is None
        assert pdf_path is None