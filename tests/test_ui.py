import unittest
from unittest.mock import patch
from src import ui_utils
import time

class TestUIUtils(unittest.TestCase):

    @patch('src.ui_utils.notification.notify')
    def test_show_toast(self, mock_notify):
        ui_utils.show_toast("Title", "Message")
        
        # Wait a bit for the thread to run
        time.sleep(0.1)
        
        mock_notify.assert_called_with(
            title="Title",
            message="Message",
            app_name='ScreenGemini',
            timeout=10
        )

if __name__ == '__main__':
    unittest.main()
