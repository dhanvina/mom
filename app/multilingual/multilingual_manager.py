"""
Multilingual manager module for AI-powered MoM generator.

This module provides functionality for managing multi-language support.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from app.analyzer.language_detector import LanguageDetector
from app.translator.translator import Translator
from app.prompt.language_prompts import LanguagePrompts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultilingualManager:
    """
    Manages multi-language support for MoM generation.
    
    This class provides methods for language detection, translation, and
    language-specific prompt management.
    
    Attributes:
        config (Dict): Configuration options for the multilingual manager
        language_detector (LanguageDetector): Detector for transcript language
        translator (Translator): Translator for MoM content
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MultilingualManager with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the multilingual manager
        """
        self.config = config or {}
        self.language_detector = LanguageDetector("llama3:latest", self.config.get("language_detector", {}))
        self.translator = Translator(self.config.get("translator", {}))
        logger.info("MultilingualManager initialized")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of a text.
        
        Args:
            text (str): Text to detect the language of
            
        Returns:
            Tuple[str, float]: Detected language code and confidence score
        """
        return self.language_detector.detect_with_confidence(text)
    
    def translate(self, content: Any, source: Optional[str] = None, target: str = "en") -> Any:
        """
        Translate content from source language to target language.
        
        Args:
            content (Any): Content to translate (string, list, or dictionary)
            source (str, optional): Source language code. If None, language will be detected.
            target (str): Target language code. Defaults to "en".
            
        Returns:
            Any: Translated content
        """
        return self.translator.translate_item(content, source, target)
    
    def translate_mom(self, mom_data: Dict[str, Any], source: Optional[str] = None, target: str = "en") -> Dict[str, Any]:
        """
        Translate MoM data from source language to target language.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to translate
            source (str, optional): Source language code. If None, language will be detected.
            target (str): Target language code. Defaults to "en".
            
        Returns:
            Dict[str, Any]: Translated MoM data
        """
        return self.translator.translate_mom(mom_data, source, target)
    
    def get_system_prompt(self, language: str) -> str:
        """
        Get the system prompt for a specific language.
        
        Args:
            language (str): Language code
            
        Returns:
            str: System prompt in the specified language
        """
        return LanguagePrompts.get_system_prompt(language)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get a dictionary of supported language codes and names.
        
        Returns:
            Dict[str, str]: Dictionary of language codes and names
        """
        return self.translator.get_supported_languages()
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code (str): Language code to check
            
        Returns:
            bool: True if the language is supported, False otherwise
        """
        return self.translator.is_language_supported(language_code)
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get the name of a language from its code.
        
        Args:
            language_code (str): Language code
            
        Returns:
            str: Language name
        """
        return self.language_detector.get_language_name(language_code)