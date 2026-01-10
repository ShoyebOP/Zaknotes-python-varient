import sys
import os
import pytest

# Add project root to sys.path so we can import zaknotes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import zaknotes

def test_new_menu_functions_exist():
    """Test that the new menu option functions are defined."""
    assert hasattr(zaknotes, 'configure_gemini_models'), "zaknotes should have configure_gemini_models"
    assert hasattr(zaknotes, 'cleanup_stranded_chunks'), "zaknotes should have cleanup_stranded_chunks"

def test_old_menu_functions_removed():
    """Test that the old browser profile function is removed."""
    assert not hasattr(zaknotes, 'refresh_browser_profile'), "zaknotes should NOT have refresh_browser_profile"
