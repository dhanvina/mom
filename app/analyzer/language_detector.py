"""
Language detector module for AI-powered MoM generator.

This module provides functionality for detecting the language of meeting transcripts.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    import ollama
    OLLAMA_AVAILABLE = True
except (ImportError, TypeError) as e:
    OLLAMA_AVAILABLE = False
    ollama = None
    print(f"Warning: Ollama not available: {e}")

from app.utils.ollama_utils import OllamaManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Detects the language of meeting transcripts.
    
    This class provides methods for detecting the language of meeting transcripts
    using LLM-based language detection.
    
    Attributes:
        model_name (str): Name of the LLM model to use
        ollama_manager (OllamaManager): Manager for Ollama operations
        config (Dict): Configuration options for the detector
        language_codes (Dict): Dictionary of language codes and names
    """
    
    def __init__(self, model_name: str = "llama3:latest", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LanguageDetector with model and configuration.
        
        Args:
            model_name (str, optional): Name of the LLM model to use. Defaults to "llama3:latest".
            config (Dict, optional): Configuration options for the detector
        """
        self.model_name = model_name
        self.config = config or {}
        self.ollama_manager = OllamaManager(model_name)
        
        # Initialize language codes
        self.language_codes = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'pa': 'Punjabi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'mr': 'Marathi',
            'ur': 'Urdu',
            'fa': 'Persian',
            'tr': 'Turkish',
            'vi': 'Vietnamese',
            'th': 'Thai',
            'id': 'Indonesian',
            'ms': 'Malay',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'da': 'Danish',
            'fi': 'Finnish',
            'pl': 'Polish',
            'cs': 'Czech',
            'sk': 'Slovak',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'bg': 'Bulgarian',
            'el': 'Greek',
            'he': 'Hebrew',
            'uk': 'Ukrainian',
            'sr': 'Serbian',
            'hr': 'Croatian',
            'bs': 'Bosnian',
            'sl': 'Slovenian',
            'mk': 'Macedonian',
            'lt': 'Lithuanian',
            'lv': 'Latvian',
            'et': 'Estonian'
        }
        
        logger.info(f"LanguageDetector initialized with model: {model_name}")
    
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of a text.
        
        Args:
            text (str): The text to detect the language of
            
        Returns:
            Tuple[str, float]: Language code and confidence score
            
        Raises:
            RuntimeError: If detection fails
        """
        try:
            # Ensure Ollama server is running and model is available
            if not self.ollama_manager.is_server_running():
                raise RuntimeError("Ollama server is not running")
            
            if not self.ollama_manager.is_model_available():
                success = self.ollama_manager.pull_model()
                if not success:
                    raise RuntimeError(f"Failed to pull model: {self.model_name}")
            
            # Use LLM-based language detection
            language_code, confidence = self._detect_with_llm(text)
            
            return language_code, confidence
        
        except Exception as e:
            error_msg = f"Error detecting language: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def detect_with_confidence(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of a text with confidence score.
        
        This method is an alias for detect() to maintain compatibility with tests.
        
        Args:
            text (str): The text to detect the language of
            
        Returns:
            Tuple[str, float]: Language code and confidence score
            
        Raises:
            RuntimeError: If detection fails
        """
        return self.detect(text)
    
    def _detect_with_llm(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of a text using LLM.
        
        Args:
            text (str): The text to detect the language of
            
        Returns:
            Tuple[str, float]: Language code and confidence score
        """
        # Prepare prompt for language detection
        system_prompt = """
You are a language detection expert. Analyze the provided text and determine what language it is written in.
Respond with a JSON object containing:
1. The ISO 639-1 language code (2-letter code)
2. The language name in English
3. Your confidence level (0.0 to 1.0)

Format your response as:
{
  "language_code": "en",
  "language_name": "English",
  "confidence": 0.95
}

If you cannot determine the language with reasonable confidence, use "und" as the language code and "Undetermined" as the language name.
"""
        
        # Truncate text if it's too long
        max_length = 1000
        if len(text) > max_length:
            logger.info(f"Truncating text from {len(text)} to {max_length} characters for language detection")
            text = text[:max_length]
        
        # Prepare payload for Ollama
        payload = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Detect the language of this text:\n\n{text}"}
        ]
        
        try:
            # Check if ollama is available
            if not OLLAMA_AVAILABLE or ollama is None:
                logger.warning("Ollama is not available, defaulting to English")
                return "en", 0.0
            
            # Send to Ollama
            logger.info(f"Sending text to model '{self.model_name}' for language detection")
            response = ollama.chat(model=self.model_name, messages=payload)
            
            # Parse response
            response_text = response["message"]["content"]
            
            # Extract JSON from response
            import json
            import re
            # Find JSON object in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                language_data = json.loads(json_str)
                
                language_code = language_data.get("language_code", "en")
                confidence = language_data.get("confidence", 0.0)
                
                return language_code, confidence
            else:
                # If no JSON found, try to extract language code from text
                logger.warning("No JSON found in language detection response, trying to extract language code from text")
                
                # Look for common language code patterns
                for code, name in self.language_codes.items():
                    if code.lower() in response_text.lower() or name.lower() in response_text.lower():
                        return code, 0.5
                
                # Default to English if no language code found
                logger.warning("Could not extract language code from response, defaulting to English")
                return "en", 0.0
        
        except Exception as e:
            logger.error(f"Error detecting language with LLM: {e}")
            return "en", 0.0
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get the language name for a language code.
        
        Args:
            language_code (str): The language code
            
        Returns:
            str: The language name
        """
        return self.language_codes.get(language_code, "Unknown")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get a dictionary of supported languages.
        
        Returns:
            Dict[str, str]: Dictionary of language codes and names
        """
        return self.language_codes.copy()