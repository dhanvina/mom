"""
Text extractor module for AI-powered MoM generator.

This module provides functionality for extracting text from text files.
"""

import logging
from typing import Any, Dict, Optional
from .base_extractor import BaseExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextExtractor(BaseExtractor):
    """
    Extracts text from text files.
    
    This class provides methods for loading and extracting text from .txt files.
    
    Attributes:
        config (Dict): Configuration options for the extractor
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TextExtractor with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the extractor
        """
        super().__init__(config)
        logger.info("TextExtractor initialized")
    
    def extract(self, source: str) -> str:
        """
        Extract text from a text file.
        
        Args:
            source (str): Path to the text file
            
        Returns:
            str: The extracted text
            
        Raises:
            IOError: If the file cannot be read
        """
        try:
            logger.info(f"Extracting text from file: {source}")
            with open(source, 'r', encoding='utf-8') as file:
                content = file.read()
            return self.preprocess(content)
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decoding failed for {source}, trying with latin-1")
            with open(source, 'r', encoding='latin-1') as file:
                content = file.read()
            return self.preprocess(content)
        except Exception as e:
            error_msg = f"Error extracting text from file {source}: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)