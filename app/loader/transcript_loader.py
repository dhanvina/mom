"""
Transcript loader module for AI-powered MoM generator.

This module provides functionality for loading and preprocessing meeting transcripts
from various file formats including text, docx, PDF, audio, video, and YouTube.
"""

import os
import re
import logging
from typing import Optional, Dict, Any, Union
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptLoader:
    """
    Loads and preprocesses meeting transcripts from various file formats.
    
    This class provides methods for loading transcripts from different file formats,
    detecting file types, and preprocessing the content for further analysis.
    
    Attributes:
        config (Dict): Configuration options for the loader
        extractors (Dict): Dictionary of extractors for different file types
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TranscriptLoader with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the loader
        """
        self.config = config or {}
        self.extractors = {}
        self._initialize_extractors()
        logger.info("TranscriptLoader initialized")
    
    def _initialize_extractors(self):
        """Initialize extractors for different file types."""
        try:
            # Import extractors
            from .text_extractor import TextExtractor
            from .docx_extractor import DocxExtractor
            from .pdf_extractor import PDFExtractor
            from .audio_extractor import AudioExtractor
            from .video_extractor import VideoExtractor
            from .youtube_extractor import YouTubeExtractor
            
            # Create extractor instances
            self.extractors = {
                'txt': TextExtractor(self.config.get('text', {})),
                'docx': DocxExtractor(self.config.get('docx', {})),
                'pdf': PDFExtractor(self.config.get('pdf', {})),
                'mp3': AudioExtractor(self.config.get('audio', {})),
                'wav': AudioExtractor(self.config.get('audio', {})),
                'ogg': AudioExtractor(self.config.get('audio', {})),
                'flac': AudioExtractor(self.config.get('audio', {})),
                'mp4': VideoExtractor(self.config.get('video', {})),
                'avi': VideoExtractor(self.config.get('video', {})),
                'mkv': VideoExtractor(self.config.get('video', {})),
                'mov': VideoExtractor(self.config.get('video', {})),
                'youtube': YouTubeExtractor(self.config.get('youtube', {}))
            }
            
            logger.info(f"Initialized extractors for file types: {', '.join(self.extractors.keys())}")
        
        except ImportError as e:
            logger.warning(f"Could not initialize all extractors: {e}")
            # Initialize with basic extractors that don't have external dependencies
            try:
                from .text_extractor import TextExtractor
                self.extractors['txt'] = TextExtractor(self.config.get('text', {}))
                logger.info("Initialized text extractor only")
            except ImportError:
                logger.warning("Could not initialize any extractors")
    
    def load_from_file(self, file_path: str) -> str:
        """
        Load transcript from a file.
        
        Args:
            file_path (str): Path to the transcript file
            
        Returns:
            str: The transcript content as a string
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported
        """
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        file_type = self.detect_file_type(file_path)
        
        if file_type in self.extractors:
            logger.info(f"Loading file with {file_type} extractor: {file_path}")
            return self.extractors[file_type].extract(file_path)
        else:
            error_msg = f"Unsupported file format: {file_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def load_from_text(self, text: str) -> str:
        """
        Load transcript from a text string.
        
        Args:
            text (str): The transcript text
            
        Returns:
            str: The preprocessed transcript text
        """
        if 'txt' in self.extractors:
            # Use the text extractor's preprocess method
            return self.extractors['txt'].preprocess(text)
        else:
            # Fallback to basic preprocessing
            return self._basic_preprocess(text)
    
    def load_from_youtube(self, url: str) -> str:
        """
        Load transcript from a YouTube video.
        
        Args:
            url (str): YouTube URL or video ID
            
        Returns:
            str: The transcript content as a string
            
        Raises:
            ValueError: If the URL is invalid or YouTube extractor is not available
        """
        if 'youtube' not in self.extractors:
            error_msg = "YouTube extractor is not available"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Loading transcript from YouTube: {url}")
        return self.extractors['youtube'].extract(url)
    
    def load_from_bytes(self, content: bytes, file_type: str) -> str:
        """
        Load transcript from bytes content.
        
        Args:
            content (bytes): File content as bytes
            file_type (str): File type (e.g., 'txt', 'docx', 'pdf', 'mp3', etc.)
            
        Returns:
            str: The transcript content as a string
            
        Raises:
            ValueError: If the file type is not supported
        """
        if file_type not in self.extractors:
            error_msg = f"Unsupported file format: {file_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Loading transcript from bytes with {file_type} extractor")
        return self.extractors[file_type].extract(content)
    
    def detect_file_type(self, file_path: str) -> str:
        """
        Detect the type of a file based on its extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: The file type (extension without the dot)
        """
        # Check if it's a YouTube URL
        if self._is_youtube_url(file_path):
            return 'youtube'
        
        # Otherwise, get the file extension
        return os.path.splitext(file_path)[1].lower()[1:]
    
    def _is_youtube_url(self, url: str) -> bool:
        """
        Check if a string is a YouTube URL.
        
        Args:
            url (str): String to check
            
        Returns:
            bool: True if the string is a YouTube URL, False otherwise
        """
        youtube_patterns = [
            r'https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(www\.)?youtu\.be/[\w-]+'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        
        return False
    
    def _basic_preprocess(self, text: str) -> str:
        """
        Basic preprocessing for text.
        
        Args:
            text (str): The raw text
            
        Returns:
            str: The preprocessed text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text