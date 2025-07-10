 """
Ollama management utilities for AI-powered MoM generator.

This module provides utilities for managing Ollama server connections,
model availability, and model operations using the Ollama Python client.
"""


import ollama
from ollama import Client
from typing import List
import logging

#configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaManager:
    """
    Manages Ollama server connections and model operations.
    
    This class provides methods for checking server status, listing available
    models, pulling models, and ensuring model availability for AI operations.
    
    Attributes:
        model_name (str): Name of the model to manage
        client (Client): Ollama client instance
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = Client() # uses default localhost
        logger.info(f"Initiated OllamaManager for model: {model_name}")

    def is_server_running(self) -> bool:
        """
        Checks if the ollama server is running.
        Attempts to list models to verify server connectivity.
        
        Returns:
            bool: True if server is running, False otherwise
        """
        try:
            self.client.list()
            logger.debug("Ollama server is running")
            return True
        except Exception as e: 
            logger.warning(f"Ollama server is not running: {e}")
            return False
    
    def list_models(self)-> list[str]:
        """
        List all available models on the Ollama server.
        
        Returns:
            List[str]: List of available model names
        """
        try: 
            models = [model.model for model in ollama.list().models]
            logger.info(f"Found {len(models)} available models: {models}")
            return models
        
        except Exception as e:
            logger.error(f"Error listing the models {e}")
            return []

    def is_model_available(self) -> bool:
        """
       Check if a specific model is available.
        
        Args:
            model_name (str, optional): Model name to check. 
                                      Defaults to self.model_name.
        
        Returns:
            bool: True if model is available, False otherwise
        """
        model = self.model_name
        available_models = self.list_models()
        is_available = model in available_models

        if is_available:
            logger.info(f"Model '{model}' is available")
        else:
            logger.warning(f"Model '{model}' is not available")
        
        return is_available

    def pull_model(self) -> bool:
        """
        Pull/download a model from Ollama.
        
        Args:
            model_name (str, optional): Model name to pull. 
                                      Defaults to self.model_name.
        
        Returns:
            bool: True if successful, False otherwise
        """
        model = self.model_name
        try:
            logger.info(f"Pulling model '{model}' ....")
            ollama.pull(model)
            return True
        
        except Exception as e:
            logger.error(f"Error while pulling the model {model}: {e}")
            return False
    
    def get_model_info(self, model_name) -> dict:
        """
        Get information about a specific model.
        
        Args:
            model_name (str, optional): Model name. Defaults to self.model_name.
        
        Returns:
            dict: Model information including size, last used, etc.
        """
        try:
            models = ollama.list().models
            for model_info in models:
                if model_info.model == self.model:
                    logger.info(f"Retrived info for model '{self.model}'")
                    return {
                        "name": model_info.name,
                        "model": model_info.model,
                        "size": model_info.size,
                        "modified_at": model_info.modified_at,
                        "digest": model_info.digest
                    }
            logger.warning(f"Model '{self.model}' not found in model list")
            return {}
        except Exception as e:
            logger.error(f"Error getting model info for '{self.model}': {e}")
            return {}

    
class OllamaRunningError(Exception):
    """
    Raised when Ollama server is not running
    """
    pass

class ModelNotFoundError(Exception):
    """
    Raised when a model is not available and cannot be pulled
    """
    pass