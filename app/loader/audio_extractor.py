"""
Audio extractor module for AI-powered MoM generator.

This module provides functionality for extracting text from audio files
using speech recognition.
"""

import os
import logging
import tempfile
from typing import Any, Dict, Optional, Union
import speech_recognition as sr
from pydub import AudioSegment
from .base_extractor import BaseExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioExtractor(BaseExtractor):
    """
    Extracts text from audio files using speech recognition.
    
    This class provides methods for loading and extracting text from audio files
    such as MP3, WAV, etc.
    
    Attributes:
        config (Dict): Configuration options for the extractor
        recognizer (sr.Recognizer): Speech recognition engine
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AudioExtractor with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the extractor
        """
        super().__init__(config)
        self.recognizer = sr.Recognizer()
        
        # Configure recognizer from config
        if self.config.get('energy_threshold'):
            self.recognizer.energy_threshold = self.config.get('energy_threshold')
        if self.config.get('pause_threshold'):
            self.recognizer.pause_threshold = self.config.get('pause_threshold')
        
        logger.info("AudioExtractor initialized")
    
    def extract(self, source: Union[str, bytes]) -> str:
        """
        Extract text from an audio file using speech recognition.
        
        Args:
            source (Union[str, bytes]): Path to the audio file or bytes content
            
        Returns:
            str: The extracted text
            
        Raises:
            IOError: If the audio file cannot be read or processed
            ValueError: If the audio format is not supported
        """
        try:
            logger.info("Extracting text from audio file")
            
            # Convert source to WAV format for speech recognition
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
            
            try:
                # Handle different source types
                if isinstance(source, str):
                    # Source is a file path
                    file_ext = os.path.splitext(source)[1].lower()
                    if file_ext == '.mp3':
                        audio = AudioSegment.from_mp3(source)
                    elif file_ext == '.wav':
                        audio = AudioSegment.from_wav(source)
                    elif file_ext == '.ogg':
                        audio = AudioSegment.from_ogg(source)
                    elif file_ext == '.flac':
                        audio = AudioSegment.from_file(source, format="flac")
                    else:
                        raise ValueError(f"Unsupported audio format: {file_ext}")
                elif isinstance(source, bytes):
                    # Source is bytes, assume MP3
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                        temp_mp3.write(source)
                        temp_mp3_path = temp_mp3.name
                    try:
                        audio = AudioSegment.from_mp3(temp_mp3_path)
                    finally:
                        os.unlink(temp_mp3_path)
                else:
                    raise ValueError(f"Unsupported source type: {type(source)}")
                
                # Export as WAV for speech recognition
                audio.export(wav_path, format="wav")
                
                # Perform speech recognition
                with sr.AudioFile(wav_path) as audio_file:
                    audio_data = self.recognizer.record(audio_file)
                    
                    # Use the appropriate recognition engine based on config
                    engine = self.config.get('recognition_engine', 'google')
                    language = self.config.get('language', 'en-US')
                    
                    if engine == 'google':
                        text = self.recognizer.recognize_google(audio_data, language=language)
                    elif engine == 'sphinx':
                        text = self.recognizer.recognize_sphinx(audio_data, language=language)
                    else:
                        # Default to Google
                        text = self.recognizer.recognize_google(audio_data, language=language)
                
                return self.preprocess(text)
            
            finally:
                # Clean up temporary WAV file
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
        
        except sr.UnknownValueError:
            error_msg = "Speech recognition could not understand audio"
            logger.error(error_msg)
            raise IOError(error_msg)
        
        except sr.RequestError as e:
            error_msg = f"Could not request results from speech recognition service: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)
        
        except Exception as e:
            error_msg = f"Error extracting text from audio: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)
    
    def extract_large_audio(self, source: str, chunk_size_ms: int = 60000) -> str:
        """
        Extract text from a large audio file by processing it in chunks.
        
        Args:
            source (str): Path to the audio file
            chunk_size_ms (int): Size of each chunk in milliseconds
            
        Returns:
            str: The extracted text
        """
        try:
            logger.info(f"Extracting text from large audio file in chunks of {chunk_size_ms}ms")
            
            # Load the audio file
            if source.lower().endswith('.mp3'):
                audio = AudioSegment.from_mp3(source)
            elif source.lower().endswith('.wav'):
                audio = AudioSegment.from_wav(source)
            elif source.lower().endswith('.ogg'):
                audio = AudioSegment.from_ogg(source)
            elif source.lower().endswith('.flac'):
                audio = AudioSegment.from_file(source, format="flac")
            else:
                raise ValueError(f"Unsupported audio format: {os.path.splitext(source)[1]}")
            
            # Process audio in chunks
            chunks = [audio[i:i+chunk_size_ms] for i in range(0, len(audio), chunk_size_ms)]
            logger.info(f"Split audio into {len(chunks)} chunks")
            
            # Extract text from each chunk
            texts = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                    wav_path = temp_wav.name
                
                try:
                    # Export chunk as WAV
                    chunk.export(wav_path, format="wav")
                    
                    # Perform speech recognition on chunk
                    with sr.AudioFile(wav_path) as audio_file:
                        audio_data = self.recognizer.record(audio_file)
                        
                        # Use the appropriate recognition engine based on config
                        engine = self.config.get('recognition_engine', 'google')
                        language = self.config.get('language', 'en-US')
                        
                        try:
                            if engine == 'google':
                                chunk_text = self.recognizer.recognize_google(audio_data, language=language)
                            elif engine == 'sphinx':
                                chunk_text = self.recognizer.recognize_sphinx(audio_data, language=language)
                            else:
                                # Default to Google
                                chunk_text = self.recognizer.recognize_google(audio_data, language=language)
                            
                            texts.append(chunk_text)
                        
                        except sr.UnknownValueError:
                            logger.warning(f"Could not understand audio in chunk {i+1}")
                            texts.append("")
                        
                        except sr.RequestError as e:
                            logger.warning(f"Request error in chunk {i+1}: {e}")
                            texts.append("")
                
                finally:
                    # Clean up temporary WAV file
                    if os.path.exists(wav_path):
                        os.unlink(wav_path)
            
            # Combine all texts
            full_text = " ".join(texts)
            return self.preprocess(full_text)
        
        except Exception as e:
            error_msg = f"Error extracting text from large audio: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)