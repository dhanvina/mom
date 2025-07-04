import ollama
from ollama import Client
from typing import List

class OllamaManager:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = Client() # uses default localhost

    def is_server_running(self) -> bool:
        """
        Checks if the ollama server is running.
        Returns:
            bool: True if running, False otherwise
        """
        try:
            self.client.list()
            return True
        except: 
            return False
    
    def list_models(self)-> list[str]:
        """
        Lists the available models.
        Returns:
        List[str]: List of model names
        """
        try: 
            return [model.model for model in ollama.list().models]
        except Exception as e:
            print(f"Error listing the models {e}")
            return []

    def is_model_available(self) -> bool:
        """
        Checks if the model is available.
        Returns:
            bool: True if available, False otherwise
        """
        return self.model_name in self.list_models()

    def pull_model(self) -> bool:
        """
        Pull the model from ollama.
        Return:
            bool: True if successful, False otherwise
        """
        try:
            ollama.pull(self.model_name)
            return True
        except Exception as e:
            print(f"Error while downloading the model {e}")
            return False
    

