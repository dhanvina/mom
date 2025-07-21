"""
Unit tests for the TranscriptLoader class.
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from app.loader.transcript_loader import TranscriptLoader

class TestTranscriptLoader:
    """Test cases for TranscriptLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = TranscriptLoader()
        self.test_text = "This is a test transcript.\nIt has multiple lines.\nAnd some formatting."
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        loader = TranscriptLoader()
        assert loader.config == {}
        
        # Custom config
        custom_config = {"key": "value"}
        loader = TranscriptLoader(config=custom_config)
        assert loader.config == custom_config
    
    def test_load_from_text(self):
        """Test loading from text string."""
        result = self.loader.load_from_text(self.test_text)
        assert isinstance(result, str)
        assert "test transcript" in result
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        # Test whitespace normalization
        text = "  Multiple    spaces   \n\n  and line breaks  "
        result = self.loader._preprocess_text(text)
        assert result == "Multiple spaces and line breaks"
        
        # Test line ending normalization
        text = "Line 1\r\nLine 2\rLine 3"
        result = self.loader._preprocess_text(text)
        assert result == "Line 1 Line 2 Line 3"
    
    def test_detect_file_type(self):
        """Test file type detection."""
        assert self.loader.detect_file_type("file.txt") == "txt"
        assert self.loader.detect_file_type("file.docx") == "docx"
        assert self.loader.detect_file_type("file.pdf") == "pdf"
        assert self.loader.detect_file_type("file.unknown") == "unknown"
    
    def test_load_from_file_txt(self):
        """Test loading from text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(self.test_text.encode('utf-8'))
            temp_path = temp_file.name
        
        try:
            # Test loading the file
            result = self.loader.load_from_file(temp_path)
            assert isinstance(result, str)
            assert "test transcript" in result
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_load_from_file_nonexistent(self):
        """Test loading from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_from_file("nonexistent_file.txt")
    
    def test_load_from_file_unsupported(self):
        """Test loading from unsupported file type."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as temp_file:
            temp_file.write(self.test_text.encode('utf-8'))
            temp_path = temp_file.name
        
        try:
            # Test loading the file
            with pytest.raises(ValueError) as excinfo:
                self.loader.load_from_file(temp_path)
            assert "Unsupported file format" in str(excinfo.value)
        finally:
            # Clean up
            os.unlink(temp_path)
    
    @patch('docx.Document')
    def test_load_from_file_docx(self, mock_document):
        """Test loading from docx file."""
        # Mock Document class
        mock_doc = MagicMock()
        mock_doc.paragraphs = [
            MagicMock(text="Paragraph 1"),
            MagicMock(text="Paragraph 2"),
            MagicMock(text="Paragraph 3")
        ]
        mock_document.return_value = mock_doc
        
        # Create a temporary docx file (content doesn't matter as we're mocking)
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
            temp_file.write(b"dummy content")
            temp_path = temp_file.name
        
        try:
            # Test loading the file
            result = self.loader.load_from_file(temp_path)
            assert isinstance(result, str)
            assert "Paragraph 1" in result
            assert "Paragraph 2" in result
            assert "Paragraph 3" in result
        finally:
            # Clean up
            os.unlink(temp_path)