import unittest
from unittest.mock import patch, MagicMock
import sys
import os

import zaknotes

class TestCLIStructure(unittest.TestCase):
    @patch('zaknotes.main_menu')
    def test_default_interactive_mode(self, mock_main_menu):
        """Test that running without args enters interactive mode."""
        with patch.object(sys, 'argv', ['zaknotes.py']):
            zaknotes.main()
            mock_main_menu.assert_called_once()

    @patch('zaknotes.main_menu')
    def test_local_flag_parsing_empty(self, mock_main_menu):
        """Test that --local flag is parsed correctly with no names."""
        with patch.object(sys, 'argv', ['zaknotes.py', '--local']):
            # For now, it just prints DEBUG
            zaknotes.main()
            mock_main_menu.assert_not_called()

    @patch('zaknotes.main_menu')
    def test_local_flag_parsing_with_names(self, mock_main_menu):
        """Test that --local flag is parsed correctly with names."""
        with patch.object(sys, 'argv', ['zaknotes.py', '--local', 'Bio', 'Hist']):
            zaknotes.main()
            mock_main_menu.assert_not_called()

if __name__ == '__main__':
    unittest.main()
