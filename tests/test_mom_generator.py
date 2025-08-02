"""
Unit tests for the MoMGenerator class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.main import MoMGenerator

class TestMoMGenerator:
    """Test cases for MoMGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_prompt_manager = MagicMock()
        self.mock_ollama_manager = MagicMock()
        self.mock_mom_extractor = MagicMock()
        self.mock_mom_formatter = MagicMock()
        
        # Create patchers
        self.prompt_manager_patcher = patch('app.main.PromptManager')
        self.ollama_manager_patcher = patch('app.main.OllamaManager')
        self.mom_extractor_patcher = patch('app.main.MoMExtractor')
        self.mom_formatter_patcher = patch('app.main.MoMFormatter')
        
        # Start patchers
        self.mock_prompt_manager_class = self.prompt_manager_patcher.start()
        self.mock_ollama_manager_class = self.ollama_manager_patcher.start()
        self.mock_mom_extractor_class = self.mom_extractor_patcher.start()
        self.mock_mom_formatter_class = self.mom_formatter_patcher.start()
        
        # Set up mock returns
        self.mock_prompt_manager_class.return_value = self.mock_prompt_manager
        self.mock_ollama_manager_class.return_value = self.mock_ollama_manager
        self.mock_mom_extractor_class.return_value = self.mock_mom_extractor
        self.mock_mom_formatter_class.return_value = self.mock_mom_formatter
        
        # Initialize generator
        self.generator = MoMGenerator(model_name="test-model")
        
        # Test transcript
        self.test_transcript = "This is a test meeting transcript."
    
    def teardown_method(self):
        """Tear down test fixtures."""
        self.prompt_manager_patcher.stop()
        self.ollama_manager_patcher.stop()
        self.mom_extractor_patcher.stop()
        self.mom_formatter_patcher.stop()
    
    def test_init(self):
        """Test initialization."""
        # Verify components were initialized correctly
        self.mock_prompt_manager_class.assert_called_once()
        self.mock_ollama_manager_class.assert_called_once_with("test-model")
        self.mock_mom_extractor_class.assert_called_once_with("test-model")
        self.mock_mom_formatter_class.assert_called_once()
    
    def test_setup_success(self):
        """Test successful setup."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = True
        
        # Test setup
        success, message = self.generator.setup()
        
        # Verify result
        assert success == True
        assert "setup" in message
    
    def test_setup_server_not_running(self):
        """Test setup when server is not running."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = False
        
        # Test setup
        success, message = self.generator.setup()
        
        # Verify result
        assert success == False
        assert "Ollama server is not running" in message
    
    def test_setup_model_not_available(self):
        """Test setup when model is not available."""
        # Mock dependencies
        self.mock_ollama_manager.is_server_running.return_value = True
        self.mock_ollama_manager.is_model_available.return_value = False
        self.mock_ollama_manager.pull_model.return_value = False
        
        # Test setup
        success, message = self.generator.setup()
        
        # Verify result
        assert success == False
        assert "failed to pull test-model model" in message
    
    @patch('app.main.ollama')
    def test_generate_mom(self, mock_ollama):
        """Test generating MoM."""
        # Mock prompt manager
        mock_messages = [MagicMock(content="system prompt"), MagicMock(content="user prompt")]
        self.mock_prompt_manager.chat_prompt.format_messages.return_value = mock_messages
        
        # Mock ollama response
        mock_ollama.chat.return_value = {"message": {"content": "Generated MoM content"}}
        
        # Test generating MoM
        result = self.generator.generate_mom(self.test_transcript)
        
        # Verify prompt manager was called correctly
        self.mock_prompt_manager.chat_prompt.format_messages.assert_called_once_with(transcript=self.test_transcript)
        
        # Verify ollama was called correctly
        mock_ollama.chat.assert_called_once()
        args, kwargs = mock_ollama.chat.call_args
        assert kwargs["model"] == "test-model"
        assert len(kwargs["messages"]) == 2
        assert kwargs["messages"][0]["role"] == "system"
        assert kwargs["messages"][1]["role"] == "user"
        
        # Verify result
        assert result == "Generated MoM content"
    
    def test_generate_mom_with_options_structured(self):
        """Test generating MoM with options (structured output)."""
        # Mock extractor
        self.mock_mom_extractor.extract_with_options.return_value = {"key": "value"}
        
        # Test generating MoM with options
        options = {"structured_output": True}
        result = self.generator.generate_mom_with_options(self.test_transcript, options)
        
        # Verify extractor was called correctly
        self.mock_mom_extractor.extract_with_options.assert_called_once_with(self.test_transcript, options)
        
        # Verify formatter was not called
        self.mock_mom_formatter.format_with_options.assert_not_called()
        
        # Verify result
        assert result == {"key": "value"}
    
    def test_generate_mom_with_options_formatted(self):
        """Test generating MoM with options (formatted output)."""
        # Mock extractor and formatter
        self.mock_mom_extractor.extract_with_options.return_value = {"key": "value"}
        self.mock_mom_formatter.format_with_options.return_value = "Formatted MoM content"
        
        # Test generating MoM with options
        options = {
            "structured_output": False,
            "format_type": "html",
            "include_tables": True,
            "template": "default"
        }
        result = self.generator.generate_mom_with_options(self.test_transcript, options)
        
        # Verify extractor was called correctly
        self.mock_mom_extractor.extract_with_options.assert_called_once_with(self.test_transcript, options)
        
        # Verify formatter was called correctly
        self.mock_mom_formatter.format_with_options.assert_called_once()
        args, kwargs = self.mock_mom_formatter.format_with_options.call_args
        assert args[0] == {"key": "value"}
        assert args[1] == "html"
        assert kwargs["include_tables"] == True
        assert kwargs["template"] == "default"
        
        # Verify result
        assert result == "Formatted MoM content"
    
    def test_generate_mom_with_options_error(self):
        """Test generating MoM with options when an error occurs."""
        # Mock extractor to raise an exception
        self.mock_mom_extractor.extract_with_options.side_effect = Exception("Test error")
        
        # Test generating MoM with options
        options = {"structured_output": False}
        with pytest.raises(RuntimeError) as excinfo:
            self.generator.generate_mom_with_options(self.test_transcript, options)
        
        # Verify error message
        assert "Failed to generate MoM: Test error" in str(excinfo.value)