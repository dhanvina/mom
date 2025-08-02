"""
Audio extractor module for AI-powered MoM generator.

This module provides functionality for extracting text from audio files.
"""

import logging
import os
import tempfile
from typing import Dict, Any, Optional, List, Union
import speech_recognition as sr
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioExtractor:
    """
    Extracts text from audio files.
    
    This class provides methods for extracting text from audio files using
    speech recognition.
    
    Attributes:
        config (Dict): Configuration options for the extractor
        recognizer (sr.Recognizer): Speech recognizer instance
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AudioExtractor with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the extractor
        """
        self.config = config or {}
        self.recognizer = sr.Recognizer()
        
        # Set recognition parameters from config
        self.energy_threshold = self.config.get("energy_threshold", 300)
        self.pause_threshold = self.config.get("pause_threshold", 0.8)
        self.dynamic_energy_threshold = self.config.get("dynamic_energy_threshold", True)
        
        # Apply configuration to recognizer
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.pause_threshold = self.pause_threshold
        self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
        
        # Set recognition engine
        self.recognition_engine = self.config.get("recognition_engine", "google")
        
        logger.info("AudioExtractor initialized")
    
    def extract(self, source: str) -> str:
        """
        Extract text from an audio file.
        
        Args:
            source (str): Path to the audio file
            
        Returns:
            str: Extracted text
            
        Raises:
            ValueError: If the audio file format is not supported
            RuntimeError: If speech recognition fails
        """
        # Check if file exists
        if not os.path.exists(source):
            raise ValueError(f"Audio file not found: {source}")
        
        # Check file extension
        _, ext = os.path.splitext(source)
        ext = ext.lower()
        
        if ext not in [".mp3", ".wav", ".flac", ".aiff", ".aif", ".m4a"]:
            raise ValueError(f"Unsupported audio format: {ext}")
        
        # Convert to WAV if needed
        if ext != ".wav":
            source = self._convert_to_wav(source)
        
        # Extract text using speech recognition
        text = self._recognize_speech(source)
        
        # Clean up temporary file if created
        if ext != ".wav" and os.path.exists(source):
            try:
                os.remove(source)
            except Exception as e:
                logger.warning(f"Failed to remove temporary WAV file: {e}")
        
        return text
    
    def _convert_to_wav(self, source: str) -> str:
        """
        Convert audio file to WAV format.
        
        Args:
            source (str): Path to the audio file
            
        Returns:
            str: Path to the converted WAV file
            
        Raises:
            RuntimeError: If conversion fails
        """
        try:
            # Create a temporary file for the WAV output
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            
            # Load audio file using pydub
            audio = AudioSegment.from_file(source)
            
            # Export as WAV
            audio.export(temp_path, format="wav")
            
            logger.info(f"Converted audio file to WAV: {temp_path}")
            return temp_path
            
        except Exception as e:
            error_msg = f"Failed to convert audio file to WAV: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _recognize_speech(self, source: str) -> str:
        """
        Recognize speech in an audio file.
        
        Args:
            source (str): Path to the WAV audio file
            
        Returns:
            str: Recognized text
            
        Raises:
            RuntimeError: If speech recognition fails
        """
        try:
            # Check file size and duration
            file_size = os.path.getsize(source) / (1024 * 1024)  # Size in MB
            
            # Load audio file
            with sr.AudioFile(source) as audio_file:
                # Determine if we should process in chunks
                if file_size > 10:  # If file is larger than 10MB
                    return self._recognize_large_file(audio_file)
                else:
                    # Record audio data
                    audio_data = self.recognizer.record(audio_file)
                    
                    # Recognize speech
                    return self._perform_recognition(audio_data)
                
        except Exception as e:
            error_msg = f"Speech recognition failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _recognize_large_file(self, audio_file: sr.AudioFile) -> str:
        """
        Recognize speech in a large audio file by processing it in chunks.
        
        Args:
            audio_file (sr.AudioFile): Audio file object
            
        Returns:
            str: Recognized text
        """
        # Get audio duration
        audio_duration = audio_file.DURATION
        
        # Process in 30-second chunks
        chunk_duration = 30  # seconds
        chunks = []
        
        for i in range(0, int(audio_duration) + chunk_duration, chunk_duration):
            # Record chunk
            chunk = self.recognizer.record(audio_file, duration=min(chunk_duration, audio_duration - i))
            
            # Recognize chunk
            try:
                chunk_text = self._perform_recognition(chunk)
                chunks.append(chunk_text)
                logger.info(f"Processed audio chunk {i//chunk_duration + 1}")
            except Exception as e:
                logger.warning(f"Failed to recognize chunk {i//chunk_duration + 1}: {e}")
        
        # Combine chunks
        return " ".join(chunks)
    
    def _perform_recognition(self, audio_data: sr.AudioData) -> str:
        """
        Perform speech recognition on audio data.
        
        Args:
            audio_data (sr.AudioData): Audio data to recognize
            
        Returns:
            str: Recognized text
            
        Raises:
            RuntimeError: If speech recognition fails
        """
        try:
            # Use the configured recognition engine
            if self.recognition_engine == "google":
                return self.recognizer.recognize_google(audio_data)
            elif self.recognition_engine == "sphinx":
                return self.recognizer.recognize_sphinx(audio_data)
            elif self.recognition_engine == "whisper":
                return self.recognizer.recognize_whisper(audio_data)
            else:
                # Default to Google
                return self.recognizer.recognize_google(audio_data)
                
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            error_msg = f"Speech recognition service error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Speech recognition error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)