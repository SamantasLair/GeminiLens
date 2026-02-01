import unittest
from unittest.mock import patch, MagicMock
from src import gemini_service

class TestGeminiService(unittest.TestCase):

    @patch('src.gemini_service.config.GEMINI_API_KEY', 'fake_key')
    @patch('src.gemini_service.genai.GenerativeModel')
    @patch('src.gemini_service.genai.configure')
    def test_get_answer_success(self, mock_configure, mock_model_class):
        # Setup Mock Response
        mock_instance = mock_model_class.return_value
        mock_response = MagicMock()
        mock_response.text = "Jawaban Bahasa Indonesia."
        mock_instance.generate_content.return_value = mock_response
        
        response = gemini_service.get_answer("Pertanyaan")
        
        self.assertEqual(response, "Jawaban Bahasa Indonesia.")
        mock_configure.assert_called_with(api_key='fake_key')
        # Check model instantiation
        mock_model_class.assert_called_with('gemini-1.5-flash')

    @patch('src.gemini_service.config.GEMINI_API_KEY', None)
    def test_get_answer_no_key(self):
        # This relies on the module level check inside the function
        # Since we cannot easily un-import/re-import to trigger the module level check
        # We test the function's internal check if we added one, 
        # BUT current implementation checks config.GEMINI_API_KEY inside configure_gemini called by get_answer
        
        # We need to explicitly mock the config object imported in gemini_service
        with patch('src.gemini_service.config') as mock_config:
            mock_config.GEMINI_API_KEY = None
            response = gemini_service.get_answer("Question")
            self.assertTrue("Error" in response)

if __name__ == '__main__':
    unittest.main()
