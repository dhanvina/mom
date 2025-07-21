"""
Base formatter module for AI-powered MoM generator.

This module provides the base class for all formatters that convert
structured MoM data into various output formats.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseFormatter(ABC):
    """
    Base class for all formatters.
    
    This abstract class defines the interface that all formatters must implement.
    Formatters are responsible for converting structured MoM data into various
    output formats.
    
    Attributes:
        config (Dict): Configuration options for the formatter
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the BaseFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        self.config = config or {}
    
    @abstractmethod
    def format(self, mom_data: Dict[str, Any]) -> str:
        """
        Format MoM data into the desired output format.
        
        Args:
            mom_data (Dict[str, Any]): Structured MoM data
            
        Returns:
            str: Formatted output
            
        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        raise NotImplementedError("Subclasses must implement format method")