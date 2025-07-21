"""
Unit tests for the PromptManager class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.prompt.prompt_manager import PromptManager
from app.prompt.language_prompts import LanguagePrompts

class TestPromptManager:
    """Test cases for PromptManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.prompt_manager = PromptManager()
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        prompt_manager = PromptManager()
        assert prompt_manager.config == {}
        
        # Custom config
        custom_config = {"model": "test-model"}
        prompt_manager = PromptManager(config=custom_config)
        assert prompt_manager.config == custom_config
    
    @patch('app.prompt.language_prompts.LanguagePrompts.get_system_prompt')
    def test_build_system_prompt(self, mock_get_system_prompt):
        """Test building system prompt."""
        # Mock the get_system_prompt method
        mock_get_system_prompt.return_value = "Test system prompt"
        
        # Test building system prompt
        prompt_manager = PromptManager()
        system_prompt = prompt_manager._build_system_prompt()
        
        # Verify get_system_prompt was called with "en" (called twice: once during init, once during test)
        assert mock_get_system_prompt.call_count == 2
        mock_get_system_prompt.assert_called_with("en")
        
        # Verify result
        assert system_prompt == "Test system prompt"
    
    def test_build_chat_prompt(self):
        """Test building chat prompt."""
        # Mock the system prompt
        self.prompt_manager.system_prompt = "Test system prompt"
        
        # Test building chat prompt
        chat_prompt = self.prompt_manager._build_chat_prompt()
        
        # Verify chat prompt structure
        assert len(chat_prompt.messages) == 2
        assert chat_prompt.messages[0].prompt.template == "Test system prompt"
        assert chat_prompt.messages[1].prompt.template == "Transcript:\n{transcript}"
    
    @patch('app.prompt.language_prompts.LanguagePrompts.get_system_prompt')
    def test_get_prompt(self, mock_get_system_prompt):
        """Test getting prompt for different languages."""
        # Mock the get_system_prompt method
        mock_get_system_prompt.side_effect = lambda lang: f"System prompt in {lang}"
        
        # Test getting prompt for English
        en_prompt = self.prompt_manager.get_prompt("en")
        mock_get_system_prompt.assert_called_with("en")
        assert en_prompt.messages[0].prompt.template == "System prompt in en"
        
        # Test getting prompt for Spanish
        es_prompt = self.prompt_manager.get_prompt("es")
        mock_get_system_prompt.assert_called_with("es")
        assert es_prompt.messages[0].prompt.template == "System prompt in es"
        
        # Test getting prompt for French
        fr_prompt = self.prompt_manager.get_prompt("fr")
        mock_get_system_prompt.assert_called_with("fr")
        assert fr_prompt.messages[0].prompt.template == "System prompt in fr"
    
    @patch('app.prompt.language_prompts.LanguagePrompts.get_system_prompt')
    def test_get_structured_prompt(self, mock_get_system_prompt):
        """Test getting structured prompt for different languages."""
        # Mock the get_system_prompt method
        mock_get_system_prompt.side_effect = lambda lang: f"System prompt in {lang}"
        
        # Test getting structured prompt for English
        en_prompt = self.prompt_manager.get_structured_prompt("en")
        mock_get_system_prompt.assert_called_with("en")
        assert "System prompt in en" in en_prompt.messages[0].prompt.template
        assert "JSON" in en_prompt.messages[0].prompt.template
        
        # Test getting structured prompt for Spanish
        es_prompt = self.prompt_manager.get_structured_prompt("es")
        mock_get_system_prompt.assert_called_with("es")
        assert "System prompt in es" in es_prompt.messages[0].prompt.template
        assert "JSON" in es_prompt.messages[0].prompt.template
    
    def test_get_json_instructions(self):
        """Test getting JSON instructions for different languages."""
        # Test English instructions
        en_instructions = self.prompt_manager._get_json_instructions("en")
        assert "Please format your response as a JSON object" in en_instructions
        
        # Test Spanish instructions
        es_instructions = self.prompt_manager._get_json_instructions("es")
        assert "Por favor, formatea tu respuesta como un objeto JSON" in es_instructions
        
        # Test French instructions
        fr_instructions = self.prompt_manager._get_json_instructions("fr")
        assert "Veuillez formater votre réponse sous forme d'objet JSON" in fr_instructions
        
        # Test German instructions
        de_instructions = self.prompt_manager._get_json_instructions("de")
        assert "Bitte formatieren Sie Ihre Antwort als JSON-Objekt" in de_instructions
        
        # Test Japanese instructions (now supported)
        ja_instructions = self.prompt_manager._get_json_instructions("ja")
        assert "以下の構造のJSONオブジェクトとして回答をフォーマットしてください" in ja_instructions
        
        # Test unsupported language (should default to English with a note)
        xx_instructions = self.prompt_manager._get_json_instructions("xx")
        assert "Please format your response as a JSON object" in xx_instructions
        assert "respond in xx language" in xx_instructions