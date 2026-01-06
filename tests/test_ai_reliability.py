import pytest
from unittest.mock import MagicMock, patch, call
from src.bot_engine import AIStudioBot

@pytest.fixture
def mock_bot():
    with patch('src.bot_engine.BrowserDriver'), patch('src.bot_engine.PdfConverter'):
        bot = AIStudioBot()
        bot.page = MagicMock()
        return bot

def test_generate_notes_includes_2s_sleep_after_upload(mock_bot):
    # Setup mocks
    mock_file_input = MagicMock()
    mock_run_btn = MagicMock()
    mock_run_btn.is_enabled.return_value = True
    
    def side_effect(selector, **kwargs):
        if "data-test-upload-file-input" in selector:
            return mock_file_input
        if 'ms-run-button button[aria-label="Run"]' in selector:
            return MagicMock(first=mock_run_btn)
        return MagicMock()

    mock_bot.page.locator.side_effect = side_effect
    
    mock_stop_btn = MagicMock()
    mock_stop_btn.count.side_effect = [0, 0] # Generation doesn't start in this test to avoid other sleeps
    mock_bot.page.get_by_label.return_value = mock_stop_btn
    
    mock_last_turn = MagicMock()
    mock_bot.page.locator.return_value.filter.return_value.last = mock_last_turn
    mock_bot.page.evaluate.return_value = "Mocked AI Response"
    
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()), \
         patch('src.bot_engine.PdfConverter', MagicMock()), \
         patch('time.sleep') as mock_sleep:
        
        mock_bot.generate_notes("dummy.mp3")
        
        # Verify call order: 
        # 1. set_input_files
        # 2. time.sleep(2)
        # 3. run_btn.is_enabled()
        
        # Find index of set_input_files
        # Note: set_input_files is called on mock_file_input
        # mock_sleep(2) should be called after that.
        
        sleep_calls = [call(2) for c in mock_sleep.call_args_list if c == call(2)]
        assert len(sleep_calls) >= 1, "Should sleep for 2 seconds after upload"

def test_generate_notes_growth_monitoring_loop(mock_bot):
    # Setup mocks
    mock_bot.page.locator.return_value = MagicMock()
    mock_run_btn = MagicMock()
    mock_run_btn.is_enabled.return_value = True
    
    mock_stop_btn = MagicMock()
    mock_stop_btn.count.return_value = 0 # Assume stop button doesn't appear or we don't rely on it
    
    def locator_side_effect(selector, **kwargs):
        if 'ms-run-button button[aria-label="Run"]' in selector:
            return MagicMock(first=mock_run_btn)
        if "ms-chat-turn" in selector:
            m = MagicMock()
            m.filter.return_value.last = mock_last_turn
            return m
        return MagicMock()

    mock_bot.page.locator.side_effect = locator_side_effect
    mock_bot.page.get_by_label.return_value = mock_stop_btn
    
    mock_last_turn = MagicMock()
    
    # Mocking _get_clean_text_length call (which calls evaluate)
    # The code calls locator.evaluate(js_func)
    # We want to simulate:
    # 1. Phase A: Length 0 (waiting) -> Length 10 (started)
    # 2. Phase B: Length 10 -> 20 -> 30 -> 30 (stable)
    
    # We can mock the evaluate return value directly on the locator
    # Note: last_model_turn is a locator.
    
    # Sequence of clean lengths:
    # 0, 0, 0 (Thinking)
    # 10 (Started)
    # 20, 30, 40 (Growing)
    # 40... (Stable for 15s)
    
    lengths = [0, 0, 0] + [10] + [20, 30, 40] + [40] * 20
    mock_last_turn.evaluate.side_effect = lengths
    
    mock_bot.page.evaluate.return_value = "Hello" # Final clipboard value
    
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()), \
         patch('src.bot_engine.PdfConverter', MagicMock()), \
         patch('time.sleep') as mock_sleep, \
         patch('time.time') as mock_time:
        
        mock_time.return_value = 0
        
        mock_bot.generate_notes("dummy.mp3")
        
        # Verify that evaluate was called enough times (Waiting + Growing + Stability)
        assert mock_last_turn.evaluate.call_count >= 15
        
        # Verify scroll was called
        mock_last_turn.scroll_into_view_if_needed.assert_called()



