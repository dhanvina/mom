"""
Integration tests for the MoMFormatter class with all formatters.
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from app.formatter.mom_formatter import MoMFormatter

class TestMoMFormatterIntegration:
    """Integration test cases for MoMFormatter class with all formatters."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create MoMFormatter instance
        self.formatter = MoMFormatter()
        
        # Create test MoM data
        self.mom_data = {
            "meeting_title": "Test Meeting",
            "date_time": "2023-01-01 10:00",
            "location": "Conference Room A",
            "attendees": ["John Doe", "Jane Smith", "Bob Johnson"],
            "agenda": ["Item 1", "Item 2", "Item 3"],
            "discussion_points": ["Discussion 1", "Discussion 2"],
            "action_items": [
                {"description": "Task 1", "assignee": "John Doe", "deadline": "2023-01-15", "status": "pending"},
                {"description": "Task 2", "assignee": "Jane Smith", "deadline": "2023-01-20", "status": "in_progress"}
            ],
            "decisions": [
                {"decision": "Decision 1", "context": "Context for decision 1"},
                {"decision": "Decision 2", "context": "Context for decision 2"}
            ],
            "next_steps": ["Step 1", "Step 2"]
        }
    
    def test_initialize_formatters(self):
        """Test initialization of formatters."""
        # Verify formatters were initialized
        assert len(self.formatter.formatters) > 0
        assert 'text' in self.formatter.formatters
        assert 'json' in self.formatter.formatters
        
        # These formatters might not be available if dependencies are missing
        expected_formatters = ['text', 'html', 'json', 'pdf', 'markdown', 'email', 'docx']
        available_formatters = list(self.formatter.formatters.keys())
        
        # Log available formatters
        print(f"Available formatters: {available_formatters}")
        
        # Check that at least the basic formatters are available
        assert 'text' in available_formatters
        assert 'json' in available_formatters
    
    def test_register_formatter(self):
        """Test registering a custom formatter."""
        # Create mock formatter
        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Custom formatted content"
        
        # Register formatter
        self.formatter.register_formatter('custom', mock_formatter)
        
        # Verify formatter was registered
        assert 'custom' in self.formatter.formatters
        assert self.formatter.formatters['custom'] == mock_formatter
        
        # Test using the formatter
        result = self.formatter.format_with_formatter(self.mom_data, 'custom')
        assert result == "Custom formatted content"
        mock_formatter.format.assert_called_once_with(self.mom_data)
    
    def test_get_formatter(self):
        """Test getting a formatter."""
        # Get existing formatter
        formatter = self.formatter.get_formatter('text')
        assert formatter is not None
        
        # Get non-existent formatter
        formatter = self.formatter.get_formatter('nonexistent')
        assert formatter is None
    
    def test_format_with_formatter(self):
        """Test formatting with different formatters."""
        # Test with text formatter
        if 'text' in self.formatter.formatters:
            result = self.formatter.format_with_formatter(self.mom_data, 'text')
            assert isinstance(result, str)
            assert "Test Meeting" in result
        
        # Test with json formatter
        if 'json' in self.formatter.formatters:
            result = self.formatter.format_with_formatter(self.mom_data, 'json')
            assert isinstance(result, str)
            assert "Test Meeting" in result
        
        # Test with non-existent formatter
        with pytest.raises(ValueError) as excinfo:
            self.formatter.format_with_formatter(self.mom_data, 'nonexistent')
        assert "No formatter registered for format type" in str(excinfo.value)
    
    def test_detect_format_type(self):
        """Test detecting format type from file path."""
        # Test various file extensions
        assert self.formatter.detect_format_type("document.txt") == "text"
        assert self.formatter.detect_format_type("document.html") == "html"
        assert self.formatter.detect_format_type("document.md") == "markdown"
        assert self.formatter.detect_format_type("document.json") == "json"
        assert self.formatter.detect_format_type("document.pdf") == "pdf"
        assert self.formatter.detect_format_type("document.docx") == "docx"
        assert self.formatter.detect_format_type("document.doc") == "docx"
        assert self.formatter.detect_format_type("document.eml") == "email"
        
        # Test case insensitivity
        assert self.formatter.detect_format_type("document.TXT") == "text"
        assert self.formatter.detect_format_type("document.HTML") == "html"
        
        # Test unsupported extension
        with pytest.raises(ValueError) as excinfo:
            self.formatter.detect_format_type("document.xyz")
        assert "Unsupported file extension" in str(excinfo.value)
    
    def test_format_to_file(self):
        """Test formatting and saving to file."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with text formatter
            if 'text' in self.formatter.formatters:
                file_path = os.path.join(temp_dir, "output.txt")
                
                # Mock formatter to avoid actual formatting
                mock_formatter = MagicMock()
                mock_formatter.format.return_value = "Text formatted content"
                self.formatter.formatters['text'] = mock_formatter
                
                # Format and save to file
                self.formatter.format_to_file(self.mom_data, file_path)
                
                # Verify file was created
                assert os.path.exists(file_path)
                
                # Verify file content
                with open(file_path, 'r') as f:
                    content = f.read()
                    assert content == "Text formatted content"
            
            # Test with pdf formatter (binary output)
            if 'pdf' in self.formatter.formatters:
                file_path = os.path.join(temp_dir, "output.pdf")
                
                # Mock formatter to avoid actual formatting
                mock_formatter = MagicMock()
                mock_formatter.format.return_value = b"%PDF-1.5"  # Fake PDF content
                self.formatter.formatters['pdf'] = mock_formatter
                
                # Format and save to file
                self.formatter.format_to_file(self.mom_data, file_path)
                
                # Verify file was created
                assert os.path.exists(file_path)
                
                # Verify file content
                with open(file_path, 'rb') as f:
                    content = f.read()
                    assert content == b"%PDF-1.5"
    
    def test_format_to_file_error(self):
        """Test error handling when formatting to file."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "output.txt")
            
            # Mock formatter to raise an exception
            mock_formatter = MagicMock()
            mock_formatter.format.side_effect = Exception("Test error")
            self.formatter.formatters['text'] = mock_formatter
            
            # Format and save to file
            with pytest.raises(ValueError) as excinfo:
                self.formatter.format_to_file(self.mom_data, file_path)
            
            # Verify error message
            assert "Error saving formatted MoM" in str(excinfo.value)
    
    def test_format_to_file_unsupported_extension(self):
        """Test error handling when formatting to file with unsupported extension."""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "output.xyz")
            
            # Format and save to file
            with pytest.raises(ValueError) as excinfo:
                self.formatter.format_to_file(self.mom_data, file_path)
            
            # Verify error message
            assert "Unsupported file extension" in str(excinfo.value)