"""
Base extractor module for AI-powered MoM generator.

This module provides the base class for all extractors that convert
different file formats to text for processing.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    """
    Base class for all extractors.
    
    This abstract class defines the interface that all extractors must implement.
    Extractors are responsible for converting different file formats to text.
    
    Attributes:
        config (Dict): Configuration options for the extractor
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the BaseExtractor with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the extractor
        """
        self.config = config or {}
    
    @abstractmethod
    def extract(self, source: Any) -> str:
        """
        Extract text from the source.
        
        Args:
            source (Any): The source to extract text from (file path, bytes, etc.)
            
        Returns:
            str: The extracted text
            
        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        raise NotImplementedError("Subclasses must implement extract method")
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess the extracted text.
        
        This method performs basic preprocessing on the extracted text,
        such as removing extra whitespace, normalizing line endings, etc.
        
        Args:
            text (str): The raw extracted text
            
        Returns:
            str: The preprocessed text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text