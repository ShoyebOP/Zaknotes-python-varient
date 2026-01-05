import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

class TestJobSubMenu(unittest.TestCase):
    @patch('zaknotes.JobManager')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_job_submenu_routing(self, mock_print, mock_input, mock_manager_class):
        import zaknotes
        
        # Mock inputs: 
        # '1' (Note Gen) -> '5' (Back) -> '5' (Exit)
        mock_input.side_effect = ['1', '5', '5']
        
        try:
            zaknotes.main_menu()
        except SystemExit:
            pass
        
        # Verify sub-menu was printed (we can check mock_print calls)
        # But even better, we can verify routing if we implement methods.
        
        # Let's test a specific sub-option: Option 3 (Cancel Old Pending)
        # '1' (Note Gen) -> '3' (Cancel) -> '5' (Exit)
        mock_input.side_effect = ['1', '3', '5']
        mock_manager = mock_manager_class.return_value
        
        try:
            zaknotes.main_menu()
        except SystemExit:
            pass
            
        mock_manager.cancel_pending.assert_called()

if __name__ == '__main__':
    unittest.main()
