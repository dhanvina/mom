"""
Unit tests for the MoMExtractor class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.extractor.mom_extractor import MoMExtractor

class TestMoMExtractor:
    """Test cases for MoMExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_ollama_manager = MagicMock()
        self.mock_prompt_manager = MagicMock()
        self.mock_sentiment_analyzer = MagicMock()
        
        # Create patcher for OllamaManager
        self.ollama_manager_patcher = patch('app.extractor.mom_extractor.OllamaManager')
        self.mock_ollama_manager_class = self.ollama_manager_patcher.start()
        self.mock_ollama_manager_class.return_value = self.mock_ollama_manager
        
        # Create patcher for PromptManager
        self.prompt_manager_patcher = patch('app.extractor.mom_extractor.PromptManager')
        self.mock_prompt_manager_class = self.prompt_manager_patcher.start()
        self.mock_prompt_manager_class.return_value = self.mock_prompt_manager
        
        # Create patcher for SentimentAnalyzer
        self.sentiment_analyzer_patcher = patch('app.extractor.mom_extractor.SentimentAnalyzer')
        self.mock_sentiment_analyzer_class = self.sentiment_analyzer_patcher.start()
        self.mock_sentiment_analyzer_class.return_value = self.mock_sentiment_analyzer
        
        # Initialize extractor
        self.extractor = MoMExtractor(model_name="test-model")
        
        # Test transcript
        self.test_transcript = "This is a test meeting transcript."
    
    def teardown_method(self):
        """Tear down test fixtures."""
        self.ollama_manager_patcher.stop()
        self.prompt_manager_patcher.stop()
        self.sentiment_analyzer_patcher.stop()
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        extractor = MoMExtractor()
        assert extractor.model_name == "llama3:latest"
        assert extractor.config == {}
        
        # Custom config
        custom_config = {"key": "value"}
        extractor = MoMExtractor(model_name="custom-model", config=custom_config)
        assert extractor.model_name == "custom-model"
        assert extractor.config == custom_config
    
    @patch('app.extractor.mom_extractor.ollama')
    def test_generate_llm_response(self, mock_ollama):
        """Test generating LLM response."""
        # Mock prompt
        mock_prompt = MagicMock()
        mock_messages = [MagicMock(content="system prompt"), MagicMock(content="user prompt")]
        mock_prompt.format_messages.return_value = mock_messages
        
        # Mock ollama response
        mock_ollama.chat.return_value = {"message": {"content": "Generated MoM content"}}
        
        # Test generating response
        result = self.extractor._generate_llm_response(self.test_transcript, mock_prompt)
        
        # Verify prompt was called correctly
        mock_prompt.format_messages.assert_called_once_with(transcript=self.test_transcript)
        
        # Verify ollama was called correctly
        mock_ollama.chat.assert_called_once()
        args, kwargs = mock_ollama.chat.call_args
        assert kwargs["model"] == "test-model"
        assert len(kwargs["messages"]) == 2
        assert kwargs["messages"][0]["role"] == "system"
        assert kwargs["messages"][1]["role"] == "user"
        
        # Verify result
        assert result == "Generated MoM content"
    
    def test_parse_llm_response_json(self):
        """Test parsing LLM response in JSON format."""
        json_response = '{"meeting_title": "Test Meeting", "date_time": "2023-01-01", "attendees": "John, Jane"}'
        result = self.extractor._parse_llm_response(json_response)
        
        assert result["meeting_title"] == "Test Meeting"
        assert result["date_time"] == "2023-01-01"
        assert result["attendees"] == "John, Jane"
    
    def test_parse_llm_response_text(self):
        """Test parsing LLM response in text format with headers."""
        text_response = """
        # Meeting Title
        Project Kickoff
        
        ## Date and Time
        January 1, 2023
        
        ## Attendees
        John, Jane
        
        ## Key Discussion Points
        - Point 1
        - Point 2
        """
        
        result = self.extractor._parse_llm_response(text_response)
        
        assert "Project Kickoff" in result["meeting_title"]
        assert "January 1, 2023" in result["date_time"]
        assert "John, Jane" in result["attendees"]
        assert "Point 1" in result["discussion_points"]
        assert "Point 2" in result["discussion_points"]
    
    def test_parse_llm_response_unstructured(self):
        """Test parsing unstructured LLM response."""
        unstructured_response = "This is an unstructured response without clear sections."
        result = self.extractor._parse_llm_response(unstructured_response)
        
        # Unstructured response should be placed in discussion_points
        assert result["discussion_points"] == unstructured_response
        assert result["meeting_title"] == ""
        assert result["attendees"] == ""
    
    def test_extract_success(self):
        """Test successful extraction."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Mock prompt
        mock_prompt = MagicMock()
        self.mock_prompt_manager.get_prompt.return_value = mock_prompt
        
        # Mock _generate_llm_response
        with patch.object(self.extractor, '_generate_llm_response') as mock_generate:
            mock_generate.return_value = "# Meeting Title\nTest Meeting"
            
            # Test extraction
            result = self.extractor.extract(self.test_transcript)
            
            # Verify server and model checks
            self.mock_ollama_manager.is_server_running.assert_called_once()
            self.mock_ollama_manager.is_model_available.assert_called_once()
            
            # Verify prompt manager was called correctly
            self.mock_prompt_manager.get_prompt.assert_called_once_with("en")
            
            # Verify LLM generation
            mock_generate.assert_called_once_with(self.test_transcript, mock_prompt)
            
            # Verify result
            assert isinstance(result, dict)
            assert "Test Meeting" in result["meeting_title"]
    
    def test_extract_with_sentiment_analysis(self):
        """Test extraction with sentiment analysis."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Mock prompt
        mock_prompt = MagicMock()
        self.mock_prompt_manager.get_prompt.return_value = mock_prompt
        
        # Mock sentiment analyzer
        self.mock_sentiment_analyzer.analyze.return_value = {
            "overall": {"sentiment": "positive", "score": 0.8}
        }
        
        # Mock _generate_llm_response
        with patch.object(self.extractor, '_generate_llm_response') as mock_generate:
            mock_generate.return_value = "# Meeting Title\nTest Meeting"
            
            # Test extraction with sentiment analysis
            result = self.extractor.extract(self.test_transcript, analyze_sentiment=True)
            
            # Verify sentiment analyzer was called
            self.mock_sentiment_analyzer.analyze.assert_called_once_with(self.test_transcript)
            
            # Verify result includes sentiment data
            assert "sentiment" in result
            assert result["sentiment"]["overall"]["sentiment"] == "positive"
    
    def test_extract_with_language(self):
        """Test extraction with different language."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Mock prompt
        mock_prompt = MagicMock()
        self.mock_prompt_manager.get_prompt.return_value = mock_prompt
        
        # Mock _generate_llm_response
        with patch.object(self.extractor, '_generate_llm_response') as mock_generate:
            mock_generate.return_value = "# Título de la Reunión\nReunión de Prueba"
            
            # Test extraction with Spanish language
            result = self.extractor.extract(self.test_transcript, language="es")
            
            # Verify prompt manager was called correctly
            self.mock_prompt_manager.get_prompt.assert_called_once_with("es")
            
            # Verify result
            assert isinstance(result, dict)
            assert "Reunión de Prueba" in result["meeting_title"]
    
    def test_extract_structured(self):
        """Test structured extraction."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Mock prompt
        mock_prompt = MagicMock()
        self.mock_prompt_manager.get_structured_prompt.return_value = mock_prompt
        
        # Mock _generate_llm_response
        with patch.object(self.extractor, '_generate_llm_response') as mock_generate:
            mock_generate.return_value = '{"meeting_title": "Test Meeting", "attendees": ["John", "Jane"]}'
            
            # Test structured extraction
            result = self.extractor.extract_structured(self.test_transcript)
            
            # Verify prompt manager was called correctly
            self.mock_prompt_manager.get_structured_prompt.assert_called_once()
            
            # Verify LLM generation
            mock_generate.assert_called_once_with(self.test_transcript, mock_prompt)
            
            # Verify result
            assert isinstance(result, dict)
            assert result["meeting_title"] == "Test Meeting"
            assert "John" in result["attendees"]
    
    def test_extract_with_options(self):
        """Test extraction with options."""
        # Mock extract and extract_structured methods
        with patch.object(self.extractor, 'extract') as mock_extract, \
             patch.object(self.extractor, 'extract_structured') as mock_extract_structured:
            
            # Set up mock returns
            mock_extract.return_value = {"meeting_title": "Regular Extraction"}
            mock_extract_structured.return_value = {"meeting_title": "Structured Extraction"}
            
            # Test with regular options
            options = {"language": "fr", "analyze_sentiment": True}
            result1 = self.extractor.extract_with_options(self.test_transcript, options)
            
            # Verify extract was called correctly
            mock_extract.assert_called_once_with(self.test_transcript, "fr", True)
            assert result1["meeting_title"] == "Regular Extraction"
            
            # Test with structured output option
            options = {"language": "de", "structured_output": True}
            result2 = self.extractor.extract_with_options(self.test_transcript, options)
            
            # Verify extract_structured was called correctly
            mock_extract_structured.assert_called_once_with(self.test_transcript, "de")
            assert result2["meeting_title"] == "Structured Extraction"
    
    def test_extract_server_not_running(self):
        """Test extraction when server is not running."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = False
        
        # Test extraction
        with pytest.raises(RuntimeError) as excinfo:
            self.extractor.extract(self.test_transcript)
        
        assert "Ollama server is not running" in str(excinfo.value)
    
    def test_extract_model_not_available(self):
        """Test extraction when model is not available."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = False
        self.mock_ollama_manager.pull_model.return_value = False
        
        # Test extraction
        with pytest.raises(RuntimeError) as excinfo:
            self.extractor.extract(self.test_transcript)
        
        assert "Failed to pull model" in str(excinfo.value)