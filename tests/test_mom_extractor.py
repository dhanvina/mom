"""
Unit tests for the MoMExtractor class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.extractor.mom_extractor import MoMExtractor

class TestMoMExtractor:
    """Test cases for MoMExtractor class."""
    
    @patch('app.llm.ollama_manager.OllamaManager')
    def setup_method(self, _, mock_ollama_manager):
        """Set up test fixtures."""
        # Mock OllamaManager
        self.mock_ollama_manager_instance = MagicMock()
        mock_ollama_manager.return_value = self.mock_ollama_manager_instance
        
        # Create MoMExtractor instance
        self.extractor = MoMExtractor(model_name="test-model")
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        extractor = MoMExtractor()
        assert extractor.model_name == "llama3:latest"
        assert extractor.config == {}
        
        # Custom config
        custom_config = {"prompt": {"template": "custom"}}
        extractor = MoMExtractor(model_name="custom-model", config=custom_config)
        assert extractor.model_name == "custom-model"
        assert extractor.config == custom_config
    
    @patch('app.analyzer.language_detector.LanguageDetector.detect_with_confidence')
    def test_extract_with_language_detection(self, mock_detect_with_confidence):
        """Test extracting MoM data with language detection."""
        # Mock language detection
        mock_detect_with_confidence.return_value = ("en", 0.95)
        
        # Mock LLM response
        self.mock_ollama_manager_instance.generate.return_value = "Test MoM data"
        
        # Test extraction
        result = self.extractor.extract("Test transcript")
        
        # Verify language detection was called
        mock_detect_with_confidence.assert_called_once_with("Test transcript")
        
        # Verify LLM was called
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result
        assert result == {"text": "Test MoM data"}
    
    @patch('app.analyzer.language_detector.LanguageDetector.detect_with_confidence')
    def test_extract_with_low_confidence_detection(self, mock_detect_with_confidence):
        """Test extracting MoM data with low confidence language detection."""
        # Mock language detection with low confidence
        mock_detect_with_confidence.return_value = ("fr", 0.4)
        
        # Mock LLM response
        self.mock_ollama_manager_instance.generate.return_value = "Test MoM data"
        
        # Test extraction
        result = self.extractor.extract("Test transcript")
        
        # Verify language detection was called
        mock_detect_with_confidence.assert_called_once_with("Test transcript")
        
        # Verify LLM was called with English prompt (default when confidence is low)
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result
        assert result == {"text": "Test MoM data"}
    
    def test_extract_with_provided_language(self):
        """Test extracting MoM data with provided language."""
        # Mock LLM response
        self.mock_ollama_manager_instance.generate.return_value = "Test MoM data"
        
        # Test extraction with provided language
        result = self.extractor.extract("Test transcript", language="es")
        
        # Verify LLM was called with Spanish prompt
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result
        assert result == {"text": "Test MoM data"}
    
    def test_extract_with_structured_output(self):
        """Test extracting MoM data with structured output."""
        # Mock LLM response as JSON
        json_response = '{"meeting_title": "Test Meeting", "attendees": ["Person 1", "Person 2"]}'
        self.mock_ollama_manager_instance.generate.return_value = json_response
        
        # Test extraction with structured output
        result = self.extractor.extract("Test transcript", language="en", structured_output=True)
        
        # Verify LLM was called
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result was parsed as JSON
        assert result == {"meeting_title": "Test Meeting", "attendees": ["Person 1", "Person 2"]}
    
    def test_extract_with_invalid_json(self):
        """Test extracting MoM data with invalid JSON response."""
        # Mock LLM response as invalid JSON
        invalid_json = '{"meeting_title": "Test Meeting", "attendees": ["Person 1", "Person 2"'
        self.mock_ollama_manager_instance.generate.return_value = invalid_json
        
        # Test extraction with structured output
        result = self.extractor.extract("Test transcript", language="en", structured_output=True)
        
        # Verify LLM was called
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result was returned as text
        assert result == {"text": invalid_json}
    
    @patch('app.llm.ollama_manager.OllamaManager.generate')
    def test_extract_with_llm_error(self, mock_generate):
        """Test extracting MoM data with LLM error."""
        # Mock LLM error
        mock_generate.side_effect = Exception("Test error")
        
        # Test extraction
        result = self.extractor.extract("Test transcript")
        
        # Verify LLM was called
        mock_generate.assert_called_once()
        
        # Verify error was returned
        assert "error" in result
        assert "Test error" in result["error"]