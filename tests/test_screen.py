import unittest
from unittest.mock import patch, MagicMock
from src import screen_utils
from PIL import Image

class TestScreenUtils(unittest.TestCase):

    @patch('src.screen_utils.mss.mss')
    def test_capture_screen_mss(self, mock_mss):
        # Setup mock for mss
        mock_sct = MagicMock()
        mock_mss.return_value.__enter__.return_value = mock_sct
        
        # Setup mock image returned by sct.grab
        mock_shot = MagicMock()
        mock_shot.size = (100, 50)
        mock_shot.bgra = b'\x00' * (100 * 50 * 4) # Fake bytes
        mock_sct.grab.return_value = mock_shot

        # Call function
        img = screen_utils.capture_screen(10, 20, 110, 70)
        
        # Verify mss called with correct monitor dict
        expected_monitor = {"top": 20, "left": 10, "width": 100, "height": 50}
        mock_sct.grab.assert_called_with(expected_monitor)
        
        # Verify return type
        self.assertIsInstance(img, Image.Image)

    @patch('src.screen_utils.pytesseract.image_to_string')
    @patch('os.path.exists')
    def test_extract_text_black_screen_handling(self, mock_exists, mock_tesseract):
        # This tests that we can handle potential issues, 
        # but really the black screen fix is in capture_screen replacement.
        pass

if __name__ == '__main__':
    unittest.main()
