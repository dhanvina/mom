"""
Translator module for AI-powered MoM generator.

This module provides functionality for translating meeting transcripts and MoM data
between different languages.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
import ollama
from utils.ollama_utils import OllamaManager
from .language_detector import LanguageDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translator:
    """
    Translates meeting transcripts and MoM data between languages.
    
    This class provides methods for translating text and structured data
    between different languages using LLM-based translation.
    
    Attributes:
        model_name (str): Name of the LLM model to use
        ollama_manager (OllamaManager): Manager for Ollama operations
        language_detector (LanguageDetector): Detector for language detection
        config (Dict): Configuration options for the translator
    """
    
    def __init__(self, model_name: str = "llama3:latest", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Translator with model and configuration.
        
        Args:
            model_name (str, optional): Name of the LLM model to use. Defaults to "llama3:latest".
            config (Dict, optional): Configuration options for the translator
        """
        self.model_name = model_name
        self.config = config or {}
        self.ollama_manager = OllamaManager(model_name)
        self.language_detector = LanguageDetector(model_name)
        logger.info(f"Translator initialized with model: {model_name}")
    
    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """
        Translate text to the target language.
        
        Args:
            text (str): The text to translate
            target_language (str): The target language code
            source_language (str, optional): The source language code. If None, it will be detected.
            
        Returns:
            str: The translated text
            
        Raises:
            RuntimeError: If translation fails
        """
        try:
            # Ensure Ollama server is running and model is available
            if not self.ollama_manager.is_server_running():
                raise RuntimeError("Ollama server is not running")
            
            if not self.ollama_manager.is_model_available():
                success = self.ollama_manager.pull_model()
                if not success:
                    raise RuntimeError(f"Failed to pull model: {self.model_name}")
            
            # Detect source language if not provided
            if source_language is None:
                source_language, _ = self.language_detector.detect(text)
            
            # Skip translation if source and target languages are the same
            if source_language == target_language:
                logger.info(f"Source and target languages are the same ({source_language}), skipping translation")
                return text
            
            # Get language names for better prompting
            source_language_name = self.language_detector.get_language_name(source_language)
            target_language_name = self.language_detector.get_language_name(target_language)
            
            # Translate text
            logger.info(f"Translating text from {source_language_name} to {target_language_name}")
            translated_text = self._translate_with_llm(text, source_language, target_language)
            
            return translated_text
        
        except Exception as e:
            error_msg = f"Error translating text: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def translate_mom_data(self, mom_data: Dict[str, Any], target_language: str, 
                          source_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate MoM data to the target language.
        
        Args:
            mom_data (Dict[str, Any]): The MoM data to translate
            target_language (str): The target language code
            source_language (str, optional): The source language code. If None, it will be detected.
            
        Returns:
            Dict[str, Any]: The translated MoM data
            
        Raises:
            RuntimeError: If translation fails
        """
        try:
            # Detect source language if not provided
            if source_language is None:
                # Combine all text fields for better language detection
                combined_text = ""
                for key, value in mom_data.items():
                    if isinstance(value, str):
                        combined_text += value + "\n\n"
                
                if combined_text:
                    source_language, _ = self.language_detector.detect(combined_text)
                else:
                    source_language = "en"  # Default to English if no text is available
            
            # Skip translation if source and target languages are the same
            if source_language == target_language:
                logger.info(f"Source and target languages are the same ({source_language}), skipping translation")
                return mom_data
            
            # Get language names for better prompting
            source_language_name = self.language_detector.get_language_name(source_language)
            target_language_name = self.language_detector.get_language_name(target_language)
            
            logger.info(f"Translating MoM data from {source_language_name} to {target_language_name}")
            
            # Create a copy of the MoM data to avoid modifying the original
            translated_data = {}
            
            # Translate each field
            for key, value in mom_data.items():
                # Skip non-string fields and fields that should not be translated
                if not isinstance(value, str) or key in ['sentiment', 'topics', 'metrics', 'improvement_suggestions']:
                    translated_data[key] = value
                    continue
                
                # Skip empty fields
                if not value:
                    translated_data[key] = value
                    continue
                
                # Translate the field
                translated_value = self._translate_with_llm(value, source_language, target_language)
                translated_data[key] = translated_value
            
            return translated_data
        
        except Exception as e:
            error_msg = f"Error translating MoM data: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _translate_with_llm(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translate text using LLM.
        
        Args:
            text (str): The text to translate
            source_language (str): The source language code
            target_language (str): The target language code
            
        Returns:
            str: The translated text
        """
        # Get language names for better prompting
        source_language_name = self.language_detector.get_language_name(source_language)
        target_language_name = self.language_detector.get_language_name(target_language)
        
        # Prepare prompt for translation
        system_prompt = f"""
You are a professional translator. Translate the provided text from {source_language_name} to {target_language_name}.
Maintain the original formatting, including paragraphs, bullet points, and any special formatting.
Ensure the translation is accurate, natural, and preserves the meaning and tone of the original text.
Only respond with the translated text, without any additional comments or explanations.
"""
        
        # Truncate text if it's too long
        max_length = 8000
        if len(text) > max_length:
            logger.info(f"Text is too long ({len(text)} characters), splitting into chunks for translation")
            return self._translate_long_text(text, source_language, target_language)
        
        # Prepare payload for Ollama
        payload = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        try:
            # Send to Ollama
            logger.info(f"Sending text to model '{self.model_name}' for translation")
            response = ollama.chat(model=self.model_name, messages=payload)
            
            # Get translated text
            translated_text = response["message"]["content"]
            
            return translated_text
        
        except Exception as e:
            logger.error(f"Error translating text with LLM: {e}")
            return text  # Return original text if translation fails
    
    def _translate_long_text(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translate long text by splitting it into chunks.
        
        Args:
            text (str): The text to translate
            source_language (str): The source language code
            target_language (str): The target language code
            
        Returns:
            str: The translated text
        """
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        # Group paragraphs into chunks of approximately 4000 characters
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            
            if current_length + paragraph_length > 4000:
                # Start a new chunk
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_length = paragraph_length
            else:
                # Add to current chunk
                current_chunk.append(paragraph)
                current_length += paragraph_length
        
        # Add the last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        # Translate each chunk
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {i+1}/{len(chunks)}")
            translated_chunk = self._translate_with_llm(chunk, source_language, target_language)
            translated_chunks.append(translated_chunk)
        
        # Combine translated chunks
        return '\n\n'.join(translated_chunks)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get a dictionary of supported languages.
        
        Returns:
            Dict[str, str]: Dictionary of language codes and names
        """
        return self.language_detector.get_supported_languages()