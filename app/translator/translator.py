"""
Translator module for AI-powered MoM generator.

This module provides functionality for translating MoM content between languages.
"""

import logging
from typing import Dict, Any, Optional, List, Union
try:
    from deep_translator import GoogleTranslator
    from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    GoogleTranslator = None
    GOOGLE_LANGUAGES_TO_CODES = {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translator:
    """
    Translates MoM content between languages.
    
    This class provides methods for translating Minutes of Meeting (MoM)
    content between different languages.
    
    Attributes:
        config (Dict): Configuration options for the translator
        translator (GoogleTranslator): Google Translator instance
        supported_languages (Dict): Dictionary of supported language codes and names
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Translator with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the translator
        """
        self.config = config or {}
        
        # Initialize supported languages
        if DEEP_TRANSLATOR_AVAILABLE:
            # Invert the dictionary to get code -> language mapping
            self.supported_languages = {}
            for lang, code in GOOGLE_LANGUAGES_TO_CODES.items():
                self.supported_languages[code] = lang
        else:
            self.supported_languages = {}
            logger.warning("No translation library available. Translation functionality will be limited.")
        
        logger.info("Translator initialized")
    
    def translate_text(self, text: str, source: Optional[str] = None, target: str = "en") -> str:
        """
        Translate a text from source language to target language.
        
        Args:
            text (str): Text to translate
            source (str, optional): Source language code. If None, language will be detected.
            target (str): Target language code. Defaults to "en".
            
        Returns:
            str: Translated text
            
        Raises:
            ValueError: If target language is not supported
            RuntimeError: If translation fails
        """
        if not text:
            return text
            
        if target not in self.supported_languages:
            raise ValueError(f"Target language '{target}' is not supported")
            
        try:
            # Translate text
            translator = GoogleTranslator(source=source or 'auto', target=target)
            translation = translator.translate(text)
            return translation
        except Exception as e:
            error_msg = f"Translation failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def translate_list(self, items: List[str], source: Optional[str] = None, target: str = "en") -> List[str]:
        """
        Translate a list of texts from source language to target language.
        
        Args:
            items (List[str]): List of texts to translate
            source (str, optional): Source language code. If None, language will be detected.
            target (str): Target language code. Defaults to "en".
            
        Returns:
            List[str]: List of translated texts
        """
        return [self.translate_text(item, source, target) for item in items]
    
    def translate_dict(self, data: Dict[str, Any], source: Optional[str] = None, target: str = "en") -> Dict[str, Any]:
        """
        Translate values in a dictionary from source language to target language.
        
        Args:
            data (Dict[str, Any]): Dictionary with values to translate
            source (str, optional): Source language code. If None, language will be detected.
            target (str): Target language code. Defaults to "en".
            
        Returns:
            Dict[str, Any]: Dictionary with translated values
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.translate_text(value, source, target)
            elif isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    result[key] = self.translate_list(value, source, target)
                else:
                    result[key] = [self.translate_item(item, source, target) for item in value]
            elif isinstance(value, dict):
                result[key] = self.translate_dict(value, source, target)
            else:
                result[key] = value
        return result
    
    def translate_item(self, item: Any, source: Optional[str] = None, target: str = "en") -> Any:
        """
        Translate an item from source language to target language.
        
        Args:
            item (Any): Item to translate
            source (str, optional): Source language code. If None, language will be detected.
            target (str): Target language code. Defaults to "en".
            
        Returns:
            Any: Translated item
        """
        if isinstance(item, str):
            return self.translate_text(item, source, target)
        elif isinstance(item, list):
            return [self.translate_item(i, source, target) for i in item]
        elif isinstance(item, dict):
            return self.translate_dict(item, source, target)
        else:
            return item
    
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
        # Add translation metadata
        translated_data = self.translate_dict(mom_data, source, target)
        translated_data["translation"] = {
            "source": source or "auto",
            "target": target
        }
        
        return translated_data
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get a dictionary of supported language codes and names.
        
        Returns:
            Dict[str, str]: Dictionary of language codes and names
        """
        return self.supported_languages
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code (str): Language code to check
            
        Returns:
            bool: True if the language is supported, False otherwise
        """
        return language_code in self.supported_languages