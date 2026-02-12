import sys
import os
import pytest

# Add project root to sys.path so we can import zaknotes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import zaknotes

def test_new_menu_functions_exist():
    """Test that the new menu option functions are defined."""
    assert hasattr(zaknotes, 'manage_notion_settings'), "zaknotes should have manage_notion_settings"
    assert hasattr(zaknotes, 'cleanup_stranded_chunks'), "zaknotes should have cleanup_stranded_chunks"
    assert hasattr(zaknotes, 'configure_audio_chunking'), "zaknotes should have configure_audio_chunking"
    assert hasattr(zaknotes, 'configure_user_agent'), "zaknotes should have configure_user_agent"

def test_old_menu_functions_removed():
    """Test that the old browser functions are removed."""
    assert not hasattr(zaknotes, 'refresh_browser_profile'), "zaknotes should NOT have refresh_browser_profile"
    assert not hasattr(zaknotes, 'launch_manual_browser'), "zaknotes should NOT have launch_manual_browser"
    assert not hasattr(zaknotes, 'configure_gemini_models'), "zaknotes should NOT have configure_gemini_models"
