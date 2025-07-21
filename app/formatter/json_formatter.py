"""
JSON formatter module for AI-powered MoM generator.

This module provides functionality for formatting structured MoM data
into JSON format.
"""

import json
import logging
from typing import Any, Dict, Optional
from .base_formatter import BaseFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JsonFormatter(BaseFormatter):
    """
    Formats MoM data into JSON.
    
    This class provides methods for formatting structured MoM data into
    a JSON document.
    
    Attributes:
        config (Dict): Configuration options for the formatter
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the JsonFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        super().__init__(config)
        logger.info("JsonFormatter initialized")
    
    def format(self, mom_data: Dict[str, Any]) -> str:
        """
        Format MoM data into JSON.
        
        Args:
            mom_data (Dict[str, Any]): Structured MoM data
            
        Returns:
            str: Formatted JSON string
        """
        logger.info("Formatting MoM data as JSON")
        
        # Get indent from config or use default
        indent = self.config.get('indent', 2)
        
        # Convert to JSON
        return json.dumps(mom_data, indent=indent, ensure_ascii=False)