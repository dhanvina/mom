"""
Unit tests for the MultilingualManager class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.multilingual.multilingual_manager import MultilingualManager

class TestMultilingualManager:
    """Test cases for MultilingualManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.multilingual_manager = MultilingualManager()
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        multilingual_manager = MultilingualManager()
        assert multilingual_manager.config == {}
        
        # Custom config
        custom_config = {"language_detector": {"sample_size": 500}}
        multilingual_manager = MultilingualManager(config=custom_config)
        assert multilingual_manager.config == custom_config
    
    @patch('app.analyzer.language_detector.LanguageDetector.detect_with_confidence')
    def test_detect_language(self, mock_detect_with_confidence):
        """Test detecting language."""
        # Mock detect_with_confidence method
        mock_detect_with_confidence.return_value = ("fr", 0.95)
        
        # Test detection
        lang, confidence = self.multilingual_manager.detect_language("Bonjour le monde")
        
        # Verify detect_with_confidence was called
        mock_detect_with_confidence.assert_called_once_with("Bonjour le monde")
        
        # Verify result
        assert lang == "fr"
        assert confidence == 0.95
    
    @patch('app.translator.translator.Translator.translate_item')
    def test_translate(self, mock_translate_item):
        """Test translating content."""
        # Mock translate_item method
        mock_translate_item.return_value = "Hello world"
        
        # Test translation
        result = self.multilingual_manager.translate("Bonjour le monde", source="fr", target="en")
        
        # Verify translate_item was called
        mock_translate_item.assert_called_once_with("Bonjour le monde", "fr", "en")
        
        # Verify result
        assert result == "Hello world"
    
    @patch('app.translator.translator.Translator.translate_mom')
    def test_translate_mom(self, mock_translate_mom):
        """Test translating MoM data."""
        # Mock translate_mom method
        mock_translate_mom.return_value = {
            "meeting_title": "Team Meeting",
            "translation": {"source": "fr", "target": "en"}
        }
        
        # Test translation
        mom_data = {"meeting_title": "Réunion d'équipe"}
        result = self.multilingual_manager.translate_mom(mom_data, source="fr", target="en")
        
        # Verify translate_mom was called
        mock_translate_mom.assert_called_once_with(mom_data, "fr", "en")
        
        # Verify result
        assert result == {
            "meeting_title": "Team Meeting",
            "translation": {"source": "fr", "target": "en"}
        }
    
    @patch('app.prompt.language_prompts.LanguagePrompts.get_system_prompt')
    def test_get_system_prompt(self, mock_get_system_prompt):
        """Test getting system prompt."""
        # Mock get_system_prompt method
        mock_get_system_prompt.return_value = "System prompt in French"
        
        # Test getting system prompt
        result = self.multilingual_manager.get_system_prompt("fr")
        
        # Verify get_system_prompt was called
        mock_get_system_prompt.assert_called_once_with("fr")
        
        # Verify result
        assert result == "System prompt in French"
    
    @patch('app.translator.translator.Translator.get_supported_languages')
    def test_get_supported_languages(self, mock_get_supported_languages):
        """Test getting supported languages."""
        # Mock get_supported_languages method
        mock_get_supported_languages.return_value = {"en": "English", "fr": "French"}
        
        # Test getting supported languages
        result = self.multilingual_manager.get_supported_languages()
        
        # Verify get_supported_languages was called
        mock_get_supported_languages.assert_called_once()
        
        # Verify result
        assert result == {"en": "English", "fr": "French"}
    
    @patch('app.translator.translator.Translator.is_language_supported')
    def test_is_language_supported(self, mock_is_language_supported):
        """Test checking if a language is supported."""
        # Mock is_language_supported method
        mock_is_language_supported.side_effect = lambda lang: lang in ["en", "fr", "es"]
        
        # Test supported languages
        assert self.multilingual_manager.is_language_supported("en") == True
        assert self.multilingual_manager.is_language_supported("fr") == True
        
        # Test unsupported language
        assert self.multilingual_manager.is_language_supported("xx") == False
    
    @patch('app.analyzer.language_detector.LanguageDetector.get_language_name')
    def test_get_language_name(self, mock_get_language_name):
        """Test getting language name."""
        # Mock get_language_name method
        mock_get_language_name.side_effect = lambda lang: {"en": "English", "fr": "French"}.get(lang, f"Unknown ({lang})")
        
        # Test getting language names
        assert self.multilingual_manager.get_language_name("en") == "English"
        assert self.multilingual_manager.get_language_name("fr") == "French"
        assert self.multilingual_manager.get_language_name("xx") == "Unknown (xx)"