"""
Unit tests for the Translator class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.translator.translator import Translator

class TestTranslator:
    """Test cases for Translator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.translator = Translator()
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        translator = Translator()
        assert translator.config == {}
        
        # Custom config
        custom_config = {"api_key": "test-key"}
        translator = Translator(config=custom_config)
        assert translator.config == custom_config
    
    @patch('app.translator.translator.GoogleTranslator.translate')
    def test_translate_text(self, mock_translate):
        """Test translating text."""
        # Mock translate method
        mock_translation = MagicMock()
        mock_translation.text = "Bonjour"
        mock_translate.return_value = mock_translation
        
        # Test translation
        result = self.translator.translate_text("Hello", source="en", target="fr")
        
        # Verify translate was called with correct parameters
        mock_translate.assert_called_once_with("Hello", src="en", dest="fr")
        
        # Verify result
        assert result == "Bonjour"
    
    @patch('app.translator.translator.GoogleTranslator.translate')
    def test_translate_text_with_auto_detection(self, mock_translate):
        """Test translating text with auto language detection."""
        # Mock translate method
        mock_translation = MagicMock()
        mock_translation.text = "Hello"
        mock_translate.return_value = mock_translation
        
        # Test translation with auto detection
        result = self.translator.translate_text("Bonjour", target="en")
        
        # Verify translate was called with None source
        mock_translate.assert_called_once_with("Bonjour", src=None, dest="en")
        
        # Verify result
        assert result == "Hello"
    
    def test_translate_text_with_unsupported_language(self):
        """Test translating text with unsupported language."""
        # Test translation with unsupported language
        with pytest.raises(ValueError) as excinfo:
            self.translator.translate_text("Hello", source="en", target="xx")
        
        # Verify error message
        assert "Target language 'xx' is not supported" in str(excinfo.value)
    
    @patch('app.translator.translator.GoogleTranslator.translate')
    def test_translate_text_with_error(self, mock_translate):
        """Test translating text with error."""
        # Mock translate method to raise an exception
        mock_translate.side_effect = Exception("Test error")
        
        # Test translation with error
        with pytest.raises(RuntimeError) as excinfo:
            self.translator.translate_text("Hello", source="en", target="fr")
        
        # Verify error message
        assert "Translation failed: Test error" in str(excinfo.value)
    
    @patch('app.translator.translator.Translator.translate_text')
    def test_translate_list(self, mock_translate_text):
        """Test translating a list of texts."""
        # Mock translate_text method
        mock_translate_text.side_effect = lambda text, source, target: f"Translated: {text}"
        
        # Test translation
        result = self.translator.translate_list(["Hello", "World"], source="en", target="fr")
        
        # Verify translate_text was called for each item
        assert mock_translate_text.call_count == 2
        
        # Verify result
        assert result == ["Translated: Hello", "Translated: World"]
    
    @patch('app.translator.translator.Translator.translate_text')
    def test_translate_dict(self, mock_translate_text):
        """Test translating values in a dictionary."""
        # Mock translate_text method
        mock_translate_text.side_effect = lambda text, source, target: f"Translated: {text}"
        
        # Test translation
        data = {
            "greeting": "Hello",
            "farewell": "Goodbye"
        }
        result = self.translator.translate_dict(data, source="en", target="fr")
        
        # Verify translate_text was called for each value
        assert mock_translate_text.call_count == 2
        
        # Verify result
        assert result == {
            "greeting": "Translated: Hello",
            "farewell": "Translated: Goodbye"
        }
    
    @patch('app.translator.translator.Translator.translate_text')
    def test_translate_dict_with_nested_values(self, mock_translate_text):
        """Test translating values in a dictionary with nested values."""
        # Mock translate_text method
        mock_translate_text.side_effect = lambda text, source, target: f"Translated: {text}"
        
        # Test translation
        data = {
            "greeting": "Hello",
            "phrases": ["Good morning", "Good evening"],
            "nested": {
                "farewell": "Goodbye"
            }
        }
        result = self.translator.translate_dict(data, source="en", target="fr")
        
        # Verify translate_text was called for each string value
        assert mock_translate_text.call_count == 4
        
        # Verify result
        assert result == {
            "greeting": "Translated: Hello",
            "phrases": ["Translated: Good morning", "Translated: Good evening"],
            "nested": {
                "farewell": "Translated: Goodbye"
            }
        }
    
    @patch('app.translator.translator.Translator.translate_dict')
    def test_translate_mom(self, mock_translate_dict):
        """Test translating MoM data."""
        # Mock translate_dict method
        mock_translate_dict.return_value = {
            "meeting_title": "Translated: Meeting Title",
            "attendees": ["Translated: Person 1", "Translated: Person 2"]
        }
        
        # Test translation
        mom_data = {
            "meeting_title": "Meeting Title",
            "attendees": ["Person 1", "Person 2"]
        }
        result = self.translator.translate_mom(mom_data, source="en", target="fr")
        
        # Verify translate_dict was called
        mock_translate_dict.assert_called_once_with(mom_data, "en", "fr")
        
        # Verify result includes translation metadata
        assert result == {
            "meeting_title": "Translated: Meeting Title",
            "attendees": ["Translated: Person 1", "Translated: Person 2"],
            "translation": {
                "source": "en",
                "target": "fr"
            }
        }
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = self.translator.get_supported_languages()
        
        # Verify result is a dictionary
        assert isinstance(languages, dict)
        
        # Verify common languages are included
        assert "en" in languages
        assert "fr" in languages
        assert "es" in languages
        assert "de" in languages
    
    def test_is_language_supported(self):
        """Test checking if a language is supported."""
        # Test supported languages
        assert self.translator.is_language_supported("en") == True
        assert self.translator.is_language_supported("fr") == True
        assert self.translator.is_language_supported("es") == True
        
        # Test unsupported language
        assert self.translator.is_language_supported("xx") == False