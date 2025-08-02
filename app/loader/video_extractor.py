"""
Video extractor module for AI-powered MoM generator.

This module provides functionality for extracting audio from video files
and converting it to text using speech recognition.
"""

import os
import logging
import tempfile
from typing import Any, Dict, Optional, Union
from moviepy.editor import VideoFileClip
from .base_extractor import BaseExtractor
from .audio_extractor import AudioExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoExtractor(BaseExtractor):
    """
    Extracts text from video files by extracting audio and using speech recognition.
    
    This class provides methods for loading video files, extracting the audio track,
    and converting it to text using speech recognition.
    
    Attributes:
        config (Dict): Configuration options for the extractor
        audio_extractor (AudioExtractor): Audio extractor for speech recognition
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the VideoExtractor with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the extractor
        """
        super().__init__(config)
        self.audio_extractor = AudioExtractor(config)
        logger.info("VideoExtractor initialized")
    
    def extract(self, source: Union[str, bytes]) -> str:
        """
        Extract text from a video file by extracting audio and using speech recognition.
        
        Args:
            source (Union[str, bytes]): Path to the video file or bytes content
            
        Returns:
            str: The extracted text
            
        Raises:
            IOError: If the video file cannot be read or processed
            ValueError: If the video format is not supported
        """
        try:
            logger.info("Extracting text from video file")
            
            # Handle different source types
            if isinstance(source, str):
                # Source is a file path
                video_path = source
            elif isinstance(source, bytes):
                # Source is bytes, save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                    temp_video.write(source)
                    video_path = temp_video.name
            else:
                raise ValueError(f"Unsupported source type: {type(source)}")
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                audio_path = temp_audio.name
            
            try:
                # Extract audio from video
                logger.info(f"Extracting audio from video: {video_path}")
                video_clip = VideoFileClip(video_path)
                audio_clip = video_clip.audio
                
                # Save audio to temporary file
                audio_clip.write_audiofile(audio_path, logger=None)
                
                # Close clips to release resources
                audio_clip.close()
                video_clip.close()
                
                # Extract text from audio
                logger.info("Extracting text from audio")
                if self.config.get('process_large_files', False):
                    # Process large audio files in chunks
                    chunk_size_ms = self.config.get('chunk_size_ms', 60000)
                    text = self.audio_extractor.extract_large_audio(audio_path, chunk_size_ms)
                else:
                    # Process audio file as a whole
                    text = self.audio_extractor.extract(audio_path)
                
                return text
            
            finally:
                # Clean up temporary files
                if isinstance(source, bytes) and os.path.exists(video_path):
                    os.unlink(video_path)
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
        
        except Exception as e:
            error_msg = f"Error extracting text from video: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)
    
    def extract_segment(self, source: str, start_time: float, end_time: float) -> str:
        """
        Extract text from a specific segment of a video file.
        
        Args:
            source (str): Path to the video file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            
        Returns:
            str: The extracted text
            
        Raises:
            IOError: If the video file cannot be read or processed
            ValueError: If the video format is not supported or if times are invalid
        """
        try:
            logger.info(f"Extracting text from video segment: {start_time}s to {end_time}s")
            
            if start_time < 0:
                raise ValueError("Start time cannot be negative")
            if end_time <= start_time:
                raise ValueError("End time must be greater than start time")
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                segment_video_path = temp_video.name
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                segment_audio_path = temp_audio.name
            
            try:
                # Extract segment from video
                video_clip = VideoFileClip(source)
                
                # Check if end time is beyond video duration
                if end_time > video_clip.duration:
                    logger.warning(f"End time {end_time}s exceeds video duration {video_clip.duration}s")
                    end_time = video_clip.duration
                
                # Extract segment
                segment_clip = video_clip.subclip(start_time, end_time)
                
                # Extract audio from segment
                audio_clip = segment_clip.audio
                
                # Save audio to temporary file
                audio_clip.write_audiofile(segment_audio_path, logger=None)
                
                # Close clips to release resources
                audio_clip.close()
                segment_clip.close()
                video_clip.close()
                
                # Extract text from audio
                text = self.audio_extractor.extract(segment_audio_path)
                
                return text
            
            finally:
                # Clean up temporary files
                if os.path.exists(segment_video_path):
                    os.unlink(segment_video_path)
                if os.path.exists(segment_audio_path):
                    os.unlink(segment_audio_path)
        
        except Exception as e:
            error_msg = f"Error extracting text from video segment: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)