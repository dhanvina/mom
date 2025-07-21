"""
Unit tests for the MainApp class.
"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from app.core.main_app import MainApp, ConfigManager

class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    def test_init_with_default_path(self):
        """Test initialization with default config path."""
        with patch('os.path.exists') as mock_exists, \
             patch('json.load') as mock_load, \
             patch('os.makedirs') as mock_makedirs, \
             patch('builtins.open', create=True) as mock_open:
            
            # Mock file doesn't exist
            mock_exists.return_value = False
            
            # Initialize config manager
            config_manager = ConfigManager()
            
            # Verify default config was created
            mock_makedirs.assert_called_once()
            mock_open.assert_called_once()
            assert isinstance(config_manager.config, dict)
            assert "model_name" in config_manager.config
    
    def test_init_with_existing_config(self):
        """Test initialization with existing config file."""
        test_config = {
            "model_name": "test-model",
            "custom_key": "custom_value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(test_config, temp_file)
            temp_path = temp_file.name
        
        try:
            # Initialize config manager with temp file
            config_manager = ConfigManager(config_path=temp_path)
            
            # Verify config was loaded
            assert config_manager.config["model_name"] == "test-model"
            assert config_manager.config["custom_key"] == "custom_value"
            
            # Verify default keys were added
            assert "default_format" in config_manager.config
            assert "offline_mode" in config_manager.config
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_get_set_save(self):
        """Test get, set, and save methods."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Initialize config manager with temp file
            config_manager = ConfigManager(config_path=temp_path)
            
            # Test get with default
            assert config_manager.get("nonexistent_key", "default") == "default"
            
            # Test set
            config_manager.set("test_key", "test_value")
            assert config_manager.get("test_key") == "test_value"
            
            # Test save
            assert config_manager.save() == True
            
            # Verify file was saved correctly
            with open(temp_path, 'r') as f:
                saved_config = json.load(f)
                assert saved_config["test_key"] == "test_value"
        finally:
            # Clean up
            os.unlink(temp_path)


class TestMainApp:
    """Test cases for MainApp class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_config_manager = MagicMock()
        self.mock_transcript_loader = MagicMock()
        self.mock_mom_extractor = MagicMock()
        self.mock_mom_formatter = MagicMock()
        
        # Create patchers
        self.config_manager_patcher = patch('app.core.main_app.ConfigManager')
        self.transcript_loader_patcher = patch('app.core.main_app.TranscriptLoader')
        self.mom_extractor_patcher = patch('app.core.main_app.MoMExtractor')
        self.mom_formatter_patcher = patch('app.core.main_app.MoMFormatter')
        
        # Start patchers
        self.mock_config_manager_class = self.config_manager_patcher.start()
        self.mock_transcript_loader_class = self.transcript_loader_patcher.start()
        self.mock_mom_extractor_class = self.mom_extractor_patcher.start()
        self.mock_mom_formatter_class = self.mom_formatter_patcher.start()
        
        # Set up mock returns
        self.mock_config_manager_class.return_value = self.mock_config_manager
        self.mock_transcript_loader_class.return_value = self.mock_transcript_loader
        self.mock_mom_extractor_class.return_value = self.mock_mom_extractor
        self.mock_mom_formatter_class.return_value = self.mock_mom_formatter
        
        # Mock config values
        self.mock_config_manager.get.side_effect = lambda key, default=None: {
            'model_name': 'test-model',
            'loader': {'key': 'loader_value'},
            'extractor': {'key': 'extractor_value'},
            'formatter': {'key': 'formatter_value'}
        }.get(key, default)
        
        # Initialize app
        self.app = MainApp()
    
    def teardown_method(self):
        """Tear down test fixtures."""
        self.config_manager_patcher.stop()
        self.transcript_loader_patcher.stop()
        self.mom_extractor_patcher.stop()
        self.mom_formatter_patcher.stop()
    
    def test_init(self):
        """Test initialization."""
        # Verify components were initialized correctly
        self.mock_config_manager_class.assert_called_once()
        self.mock_transcript_loader_class.assert_called_once_with(config={'key': 'loader_value'})
        self.mock_mom_extractor_class.assert_called_once_with(model_name='test-model', config={'key': 'extractor_value'})
        self.mock_mom_formatter_class.assert_called_once_with(config={'key': 'formatter_value'})
    
    def test_setup_success(self):
        """Test successful setup."""
        # Mock dependencies
        self.mock_mom_extractor.ollama_manager.is_server_running.return_value = True
        self.mock_mom_extractor.ollama_manager.is_model_available.return_value = True
        
        # Test setup
        success, message = self.app.setup()
        
        # Verify result
        assert success == True
        assert "successful" in message
    
    def test_setup_server_not_running(self):
        """Test setup when server is not running."""
        # Mock dependencies
        self.mock_mom_extractor.ollama_manager.is_server_running.return_value = False
        
        # Test setup
        success, message = self.app.setup()
        
        # Verify result
        assert success == False
        assert "Ollama server is not running" in message
    
    def test_setup_model_not_available(self):
        """Test setup when model is not available."""
        # Mock dependencies
        self.mock_mom_extractor.ollama_manager.is_server_running.return_value = True
        self.mock_mom_extractor.ollama_manager.is_model_available.return_value = False
        self.mock_mom_extractor.ollama_manager.pull_model.return_value = False
        self.mock_mom_extractor.model_name = "test-model"
        
        # Test setup
        success, message = self.app.setup()
        
        # Verify result
        assert success == False
        assert "Failed to pull model: test-model" in message
    
    def test_process_file(self):
        """Test processing a file."""
        # Mock dependencies
        self.mock_transcript_loader.load_from_file.return_value = "Processed transcript"
        self.mock_mom_extractor.extract.return_value = {"key": "value"}
        self.mock_mom_formatter.format.return_value = "Formatted output"
        
        # Test processing
        result = self.app.process_file("test_file.txt", "html")
        
        # Verify dependencies were called correctly
        self.mock_transcript_loader.load_from_file.assert_called_once_with("test_file.txt")
        self.mock_mom_extractor.extract.assert_called_once_with("Processed transcript")
        self.mock_mom_formatter.format.assert_called_once_with({"key": "value"}, "html")
        
        # Verify result
        assert result["mom_data"] == {"key": "value"}
        assert result["output"] == "Formatted output"
    
    def test_process_text(self):
        """Test processing text."""
        # Mock dependencies
        self.mock_transcript_loader.load_from_text.return_value = "Processed transcript"
        self.mock_mom_extractor.extract.return_value = {"key": "value"}
        self.mock_mom_formatter.format.return_value = "Formatted output"
        
        # Test processing
        result = self.app.process_text("Raw transcript", "json")
        
        # Verify dependencies were called correctly
        self.mock_transcript_loader.load_from_text.assert_called_once_with("Raw transcript")
        self.mock_mom_extractor.extract.assert_called_once_with("Processed transcript")
        self.mock_mom_formatter.format.assert_called_once_with({"key": "value"}, "json")
        
        # Verify result
        assert result["mom_data"] == {"key": "value"}
        assert result["output"] == "Formatted output"
    
    def test_save_output(self):
        """Test saving output to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output", "test_output.txt")
            
            # Test saving
            result = self.app.save_output("Test output content", output_path)
            
            # Verify result
            assert result == True
            assert os.path.exists(output_path)
            
            # Verify content
            with open(output_path, 'r') as f:
                content = f.read()
                assert content == "Test output content"