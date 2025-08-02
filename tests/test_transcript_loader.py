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
        # Create mock extractors
        self.mock_text_extractor = MagicMock()
        self.mock_docx_extractor = MagicMock()
        self.mock_pdf_extractor = MagicMock()
        self.mock_audio_extractor = MagicMock()
        self.mock_video_extractor = MagicMock()
        self.mock_youtube_extractor = MagicMock()
        
        # Create patchers
        self.text_extractor_patcher = patch('app.loader.text_extractor.TextExtractor')
        self.docx_extractor_patcher = patch('app.loader.docx_extractor.DocxExtractor')
        self.pdf_extractor_patcher = patch('app.loader.pdf_extractor.PDFExtractor')
        self.audio_extractor_patcher = patch('app.loader.audio_extractor.AudioExtractor')
        self.video_extractor_patcher = patch('app.loader.video_extractor.VideoExtractor')
        self.youtube_extractor_patcher = patch('app.loader.youtube_extractor.YouTubeExtractor')
        
        # Start patchers
        self.mock_text_extractor_class = self.text_extractor_patcher.start()
        self.mock_docx_extractor_class = self.docx_extractor_patcher.start()
        self.mock_pdf_extractor_class = self.pdf_extractor_patcher.start()
        self.mock_audio_extractor_class = self.audio_extractor_patcher.start()
        self.mock_video_extractor_class = self.video_extractor_patcher.start()
        self.mock_youtube_extractor_class = self.youtube_extractor_patcher.start()
        
        # Set up mock returns
        self.mock_text_extractor_class.return_value = self.mock_text_extractor
        self.mock_docx_extractor_class.return_value = self.mock_docx_extractor
        self.mock_pdf_extractor_class.return_value = self.mock_pdf_extractor
        self.mock_audio_extractor_class.return_value = self.mock_audio_extractor
        self.mock_video_extractor_class.return_value = self.mock_video_extractor
        self.mock_youtube_extractor_class.return_value = self.mock_youtube_extractor
        
        # Initialize loader
        self.loader = TranscriptLoader()
    
    def teardown_method(self):
        """Tear down test fixtures."""
        self.text_extractor_patcher.stop()
        self.docx_extractor_patcher.stop()
        self.pdf_extractor_patcher.stop()
        self.audio_extractor_patcher.stop()
        self.video_extractor_patcher.stop()
        self.youtube_extractor_patcher.stop()
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        loader = TranscriptLoader()
        assert loader.config == {}
        assert 'txt' in loader.extractors
        assert 'docx' in loader.extractors
        assert 'pdf' in loader.extractors
        assert 'mp3' in loader.extractors
        assert 'mp4' in loader.extractors
        assert 'youtube' in loader.extractors
        
        # Custom config
        custom_config = {
            'text': {'encoding': 'utf-8'},
            'docx': {'extract_comments': True},
            'pdf': {'extract_images': False},
            'audio': {'recognition_engine': 'google'},
            'video': {'process_large_files': True},
            'youtube': {'download_quality': 'high'}
        }
        
        with patch('app.loader.text_extractor.TextExtractor') as mock_text_extractor, \
             patch('app.loader.docx_extractor.DocxExtractor') as mock_docx_extractor, \
             patch('app.loader.pdf_extractor.PDFExtractor') as mock_pdf_extractor, \
             patch('app.loader.audio_extractor.AudioExtractor') as mock_audio_extractor, \
             patch('app.loader.video_extractor.VideoExtractor') as mock_video_extractor, \
             patch('app.loader.youtube_extractor.YouTubeExtractor') as mock_youtube_extractor:
            
            loader = TranscriptLoader(config=custom_config)
            
            # Verify extractors were initialized with correct configs
            mock_text_extractor.assert_called_once_with({'encoding': 'utf-8'})
            mock_docx_extractor.assert_called_once_with({'extract_comments': True})
            mock_pdf_extractor.assert_called_once_with({'extract_images': False})
            mock_audio_extractor.assert_called_once_with({'recognition_engine': 'google'})
            mock_video_extractor.assert_called_once_with({'process_large_files': True})
            mock_youtube_extractor.assert_called_once_with({'download_quality': 'high'})
    
    def test_load_from_file_txt(self):
        """Test loading from a text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'Test transcript content')
            file_path = temp_file.name
        
        try:
            # Mock extractor
            self.mock_text_extractor.extract.return_value = "Processed text content"
            
            # Test loading
            result = self.loader.load_from_file(file_path)
            
            # Verify extractor was called
            self.mock_text_extractor.extract.assert_called_once_with(file_path)
            
            # Verify result
            assert result == "Processed text content"
        finally:
            # Clean up
            os.unlink(file_path)
    
    def test_load_from_file_docx(self):
        """Test loading from a docx file."""
        # Create a temporary docx file path (we don't need to create the actual file)
        file_path = "test_document.docx"
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            # Mock extractor
            self.mock_docx_extractor.extract.return_value = "Processed docx content"
            
            # Test loading
            result = self.loader.load_from_file(file_path)
            
            # Verify extractor was called
            self.mock_docx_extractor.extract.assert_called_once_with(file_path)
            
            # Verify result
            assert result == "Processed docx content"
    
    def test_load_from_file_pdf(self):
        """Test loading from a PDF file."""
        # Create a temporary PDF file path (we don't need to create the actual file)
        file_path = "test_document.pdf"
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            # Mock extractor
            self.mock_pdf_extractor.extract.return_value = "Processed PDF content"
            
            # Test loading
            result = self.loader.load_from_file(file_path)
            
            # Verify extractor was called
            self.mock_pdf_extractor.extract.assert_called_once_with(file_path)
            
            # Verify result
            assert result == "Processed PDF content"
    
    def test_load_from_file_mp3(self):
        """Test loading from an MP3 file."""
        # Create a temporary MP3 file path (we don't need to create the actual file)
        file_path = "test_audio.mp3"
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            # Mock extractor
            self.mock_audio_extractor.extract.return_value = "Processed audio content"
            
            # Test loading
            result = self.loader.load_from_file(file_path)
            
            # Verify extractor was called
            self.mock_audio_extractor.extract.assert_called_once_with(file_path)
            
            # Verify result
            assert result == "Processed audio content"
    
    def test_load_from_file_mp4(self):
        """Test loading from an MP4 file."""
        # Create a temporary MP4 file path (we don't need to create the actual file)
        file_path = "test_video.mp4"
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            # Mock extractor
            self.mock_video_extractor.extract.return_value = "Processed video content"
            
            # Test loading
            result = self.loader.load_from_file(file_path)
            
            # Verify extractor was called
            self.mock_video_extractor.extract.assert_called_once_with(file_path)
            
            # Verify result
            assert result == "Processed video content"
    
    def test_load_from_youtube(self):
        """Test loading from a YouTube URL."""
        # YouTube URL
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # Mock extractor
        self.mock_youtube_extractor.extract.return_value = "Processed YouTube content"
        
        # Test loading
        result = self.loader.load_from_youtube(url)
        
        # Verify extractor was called
        self.mock_youtube_extractor.extract.assert_called_once_with(url)
        
        # Verify result
        assert result == "Processed YouTube content"
    
    def test_load_from_file_youtube_url(self):
        """Test loading from a file path that is actually a YouTube URL."""
        # YouTube URL
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # Mock _is_youtube_url
        with patch.object(self.loader, '_is_youtube_url', return_value=True):
            # Mock extractor
            self.mock_youtube_extractor.extract.return_value = "Processed YouTube content"
            
            # Test loading
            result = self.loader.load_from_file(url)
            
            # Verify extractor was called
            self.mock_youtube_extractor.extract.assert_called_once_with(url)
            
            # Verify result
            assert result == "Processed YouTube content"
    
    def test_load_from_file_unsupported(self):
        """Test loading from an unsupported file type."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as temp_file:
            file_path = temp_file.name
        
        try:
            # Mock file existence
            with patch('os.path.exists', return_value=True):
                # Test loading
                with pytest.raises(ValueError) as excinfo:
                    self.loader.load_from_file(file_path)
                
                # Verify error message
                assert "Unsupported file format" in str(excinfo.value)
        finally:
            # Clean up
            os.unlink(file_path)
    
    def test_load_from_file_not_found(self):
        """Test loading from a non-existent file."""
        # Non-existent file path
        file_path = "nonexistent_file.txt"
        
        # Mock file existence
        with patch('os.path.exists', return_value=False):
            # Test loading
            with pytest.raises(FileNotFoundError) as excinfo:
                self.loader.load_from_file(file_path)
            
            # Verify error message
            assert "File not found" in str(excinfo.value)
    
    def test_load_from_text(self):
        """Test loading from text."""
        # Mock extractor
        self.mock_text_extractor.preprocess.return_value = "Preprocessed text"
        
        # Test loading
        result = self.loader.load_from_text("Raw text")
        
        # Verify extractor was called
        self.mock_text_extractor.preprocess.assert_called_once_with("Raw text")
        
        # Verify result
        assert result == "Preprocessed text"
    
    def test_load_from_bytes(self):
        """Test loading from bytes."""
        # Mock extractor
        self.mock_pdf_extractor.extract.return_value = "Processed PDF content"
        
        # Test loading
        result = self.loader.load_from_bytes(b'PDF content', 'pdf')
        
        # Verify extractor was called
        self.mock_pdf_extractor.extract.assert_called_once_with(b'PDF content')
        
        # Verify result
        assert result == "Processed PDF content"
    
    def test_load_from_bytes_unsupported(self):
        """Test loading from bytes with unsupported format."""
        # Test loading
        with pytest.raises(ValueError) as excinfo:
            self.loader.load_from_bytes(b'Content', 'xyz')
        
        # Verify error message
        assert "Unsupported file format" in str(excinfo.value)
    
    def test_detect_file_type(self):
        """Test file type detection."""
        # Test various file types
        assert self.loader.detect_file_type("document.txt") == "txt"
        assert self.loader.detect_file_type("document.docx") == "docx"
        assert self.loader.detect_file_type("document.pdf") == "pdf"
        assert self.loader.detect_file_type("audio.mp3") == "mp3"
        assert self.loader.detect_file_type("video.mp4") == "mp4"
        
        # Test YouTube URL
        with patch.object(self.loader, '_is_youtube_url', return_value=True):
            assert self.loader.detect_file_type("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube"
    
    def test_is_youtube_url(self):
        """Test YouTube URL detection."""
        # Test valid YouTube URLs
        assert self.loader._is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == True
        assert self.loader._is_youtube_url("https://youtu.be/dQw4w9WgXcQ") == True
        
        # Test invalid URLs
        assert self.loader._is_youtube_url("https://www.example.com") == False
        assert self.loader._is_youtube_url("document.txt") == False
    
    def test_basic_preprocess(self):
        """Test basic text preprocessing."""
        # Test preprocessing
        result = self.loader._basic_preprocess("  Line  1  \r\n  Line  2  \r  Line  3  ")
        
        # Verify result
        assert result == "Line 1 Line 2 Line 3"