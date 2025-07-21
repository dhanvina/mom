"""
YouTube extractor module for AI-powered MoM generator.

This module provides functionality for downloading audio from YouTube videos
and converting it to text using speech recognition.
"""

import os
import logging
import tempfile
import re
from typing import Any, Dict, Optional
from pytube import YouTube
from .base_extractor import BaseExtractor
from .audio_extractor import AudioExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeExtractor(BaseExtractor):
    """
    Extracts text from YouTube videos by downloading audio and using speech recognition.
    
    This class provides methods for downloading YouTube videos, extracting the audio track,
    and converting it to text using speech recognition.
    
    Attributes:
        config (Dict): Configuration options for the extractor
        audio_extractor (AudioExtractor): Audio extractor for speech recognition
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the YouTubeExtractor with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the extractor
        """
        super().__init__(config)
        self.audio_extractor = AudioExtractor(config)
        logger.info("YouTubeExtractor initialized")
    
    def extract(self, source: str) -> str:
        """
        Extract text from a YouTube video by downloading audio and using speech recognition.
        
        Args:
            source (str): YouTube URL or video ID
            
        Returns:
            str: The extracted text
            
        Raises:
            IOError: If the video cannot be downloaded or processed
            ValueError: If the URL is invalid
        """
        try:
            logger.info(f"Extracting text from YouTube video: {source}")
            
            # Validate and normalize URL
            url = self._normalize_url(source)
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                audio_path = temp_audio.name
            
            try:
                # Download audio from YouTube
                logger.info(f"Downloading audio from YouTube: {url}")
                yt = YouTube(url)
                
                # Get video information
                title = yt.title
                author = yt.author
                length = yt.length
                logger.info(f"Video info - Title: {title}, Author: {author}, Length: {length} seconds")
                
                # Get audio stream
                audio_stream = yt.streams.filter(only_audio=True).first()
                if not audio_stream:
                    raise ValueError("No audio stream found for this YouTube video")
                
                # Download audio
                logger.info(f"Downloading audio stream")
                audio_file = audio_stream.download(output_path=os.path.dirname(audio_path), 
                                                  filename=os.path.basename(audio_path))
                
                # Extract text from audio
                logger.info("Extracting text from audio")
                if length > 600:  # If video is longer than 10 minutes
                    # Process large audio files in chunks
                    chunk_size_ms = self.config.get('chunk_size_ms', 60000)
                    text = self.audio_extractor.extract_large_audio(audio_path, chunk_size_ms)
                else:
                    # Process audio file as a whole
                    text = self.audio_extractor.extract(audio_path)
                
                # Add video metadata to the beginning of the text
                metadata = f"Title: {title}\nAuthor: {author}\nDuration: {length} seconds\n\n"
                
                return metadata + text
            
            finally:
                # Clean up temporary files
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
        
        except Exception as e:
            error_msg = f"Error extracting text from YouTube video: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)
    
    def _normalize_url(self, source: str) -> str:
        """
        Normalize YouTube URL or video ID.
        
        Args:
            source (str): YouTube URL or video ID
            
        Returns:
            str: Normalized YouTube URL
            
        Raises:
            ValueError: If the URL or video ID is invalid
        """
        # Check if source is already a valid URL
        if source.startswith(('http://', 'https://')):
            # Validate URL format
            if re.match(r'https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+', source):
                return source
            else:
                raise ValueError(f"Invalid YouTube URL format: {source}")
        
        # Check if source is a video ID
        elif re.match(r'^[a-zA-Z0-9_-]{11}$', source):
            return f"https://www.youtube.com/watch?v={source}"
        
        else:
            raise ValueError(f"Invalid YouTube URL or video ID: {source}")
    
    def extract_segment(self, source: str, start_time: int, end_time: Optional[int] = None) -> str:
        """
        Extract text from a specific segment of a YouTube video.
        
        Args:
            source (str): YouTube URL or video ID
            start_time (int): Start time in seconds
            end_time (int, optional): End time in seconds. If None, extracts until the end.
            
        Returns:
            str: The extracted text
            
        Raises:
            IOError: If the video cannot be downloaded or processed
            ValueError: If the URL is invalid or if times are invalid
        """
        try:
            logger.info(f"Extracting text from YouTube video segment: {start_time}s to {end_time}s")
            
            if start_time < 0:
                raise ValueError("Start time cannot be negative")
            if end_time is not None and end_time <= start_time:
                raise ValueError("End time must be greater than start time")
            
            # Validate and normalize URL
            url = self._normalize_url(source)
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                audio_path = temp_audio.name
            
            try:
                # Download audio from YouTube
                logger.info(f"Downloading audio from YouTube: {url}")
                yt = YouTube(url)
                
                # Get video information
                title = yt.title
                author = yt.author
                length = yt.length
                logger.info(f"Video info - Title: {title}, Author: {author}, Length: {length} seconds")
                
                # Validate end_time
                if end_time is None:
                    end_time = length
                elif end_time > length:
                    logger.warning(f"End time {end_time}s exceeds video length {length}s")
                    end_time = length
                
                # Get audio stream
                audio_stream = yt.streams.filter(only_audio=True).first()
                if not audio_stream:
                    raise ValueError("No audio stream found for this YouTube video")
                
                # Download audio
                logger.info(f"Downloading audio stream")
                audio_file = audio_stream.download(output_path=os.path.dirname(audio_path), 
                                                  filename=os.path.basename(audio_path))
                
                # Create a temporary file for the segment
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_segment:
                    segment_path = temp_segment.name
                
                try:
                    # Extract segment using moviepy
                    from moviepy.editor import AudioFileClip
                    
                    audio_clip = AudioFileClip(audio_path)
                    segment_clip = audio_clip.subclip(start_time, end_time)
                    segment_clip.write_audiofile(segment_path, logger=None)
                    
                    # Close clips to release resources
                    segment_clip.close()
                    audio_clip.close()
                    
                    # Extract text from audio segment
                    logger.info("Extracting text from audio segment")
                    text = self.audio_extractor.extract(segment_path)
                    
                    # Add video metadata to the beginning of the text
                    segment_duration = end_time - start_time
                    metadata = (f"Title: {title}\nAuthor: {author}\n"
                               f"Segment: {start_time}s to {end_time}s (Duration: {segment_duration}s)\n\n")
                    
                    return metadata + text
                
                finally:
                    # Clean up segment file
                    if os.path.exists(segment_path):
                        os.unlink(segment_path)
            
            finally:
                # Clean up temporary files
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
        
        except Exception as e:
            error_msg = f"Error extracting text from YouTube video segment: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)