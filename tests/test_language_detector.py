"""
Unit tests for the LanguageDetector class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.analyzer.language_detector import LanguageDetector

class TestLanguageDetector:
    """Test cases for LanguageDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_ollama_manager = MagicMock()
        
        # Create patcher for OllamaManager
        self.ollama_manager_patcher = patch('app.analyzer.language_detector.OllamaManager')
        self.mock_ollama_manager_class = self.ollama_manager_patcher.start()
        self.mock_ollama_manager_class.return_value = self.mock_ollama_manager
        
        # Initialize detector
        self.detector = LanguageDetector(model_name="test-model")
        
        # Test texts in different languages
        self.english_text = "This is a test text in English."
        self.spanish_text = "Este es un texto de prueba en español."
        self.french_text = "Ceci est un texte de test en français."
        self.german_text = "Dies ist ein Testtext auf Deutsch."
    
    def teardown_method(self):
        """Tear down test fixtures."""
        self.ollama_manager_patcher.stop()
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        detector = LanguageDetector()
        assert detector.model_name == "llama3:latest"
        assert detector.config == {}
        
        # Custom config
        custom_config = {"key": "value"}
        detector = LanguageDetector(model_name="custom-model", config=custom_config)
        assert detector.model_name == "custom-model"
        assert detector.config == custom_config
    
    def test_language_codes(self):
        """Test language codes dictionary."""
        # Check if common languages are included
        assert "en" in self.detector.language_codes
        assert "es" in self.detector.language_codes
        assert "fr" in self.detector.language_codes
        assert "de" in self.detector.language_codes
        
        # Check language names
        assert self.detector.language_codes["en"] == "English"
        assert self.detector.language_codes["es"] == "Spanish"
        assert self.detector.language_codes["fr"] == "French"
        assert self.detector.language_codes["de"] == "German"
    
    @patch('app.analyzer.language_detector.ollama')
    def test_detect_english(self, mock_ollama):
        """Test detecting English language."""
        # Mock ollama response
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"language_code": "en", "language_name": "English", "confidence": 0.95}'
            }
        }
        
        # Mock server and model checks
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Test detecting language
        language_code, confidence = self.detector.detect(self.english_text)
        
        # Verify ollama was called correctly
        mock_ollama.chat.assert_called_once()
        
        # Verify result
        assert language_code == "en"
        assert confidence == 0.95
    
    @patch('app.analyzer.language_detector.ollama')
    def test_detect_spanish(self, mock_ollama):
        """Test detecting Spanish language."""
        # Mock ollama response
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"language_code": "es", "language_name": "Spanish", "confidence": 0.92}'
            }
        }
        
        # Mock server and model checks
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Test detecting language
        language_code, confidence = self.detector.detect(self.spanish_text)
        
        # Verify ollama was called correctly
        mock_ollama.chat.assert_called_once()
        
        # Verify result
        assert language_code == "es"
        assert confidence == 0.92
    
    @patch('app.analyzer.language_detector.ollama')
    def test_detect_no_json(self, mock_ollama):
        """Test detecting language when response is not JSON."""
        # Mock ollama response
        mock_ollama.chat.return_value = {
            "message": {
                "content": "The language of the text is English."
            }
        }
        
        # Mock server and model checks
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Test detecting language
        language_code, confidence = self.detector.detect(self.english_text)
        
        # Verify ollama was called correctly
        mock_ollama.chat.assert_called_once()
        
        # Verify result
        assert language_code == "en"
        assert confidence == 0.5
    
    def test_get_language_name(self):
        """Test getting language name from code."""
        assert self.detector.get_language_name("en") == "English"
        assert self.detector.get_language_name("es") == "Spanish"
        assert self.detector.get_language_name("fr") == "French"
        assert self.detector.get_language_name("de") == "German"
        assert self.detector.get_language_name("xx") == "Unknown"
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = self.detector.get_supported_languages()
        
        # Check if it's a copy, not the original
        assert languages is not self.detector.language_codes
        
        # Check if it contains the same data
        assert languages == self.detector.language_codes
    
    def test_detect_server_not_running(self):
        """Test detecting language when server is not running."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = False
        
        # Test detecting language
        with pytest.raises(RuntimeError) as excinfo:
            self.detector.detect(self.english_text)
        
        assert "Ollama server is not running" in str(excinfo.value)
    
    def test_detect_model_not_available(self):
        """Test detecting language when model is not available."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = False
        self.mock_ollama_manager.pull_model.return_value = False
        
        # Test detecting language
        with pytest.raises(RuntimeError) as excinfo:
            self.detector.detect(self.english_text)
        
        assert "Failed to pull model" in str(excinfo.value)