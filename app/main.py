import ollama
import logging
from prompt.prompt_template import PromptManager
from utils.ollama_utils import OllamaManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoMGenerator:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.prompt = PromptManager()
        self.ollama_manager = OllamaManager(model_name)

    def setup(self) -> tuple[bool, str]:
        """checks if the model and server are ready
            returns (bool,str)
        """
        if not self.ollama_manager.is_server_running():
            return False,"Ollama server is not running"
        
        if not self.ollama_manager.is_model_available():
            success = self.ollama_manager.pull_model()
            if not success:
                return False,f"failed to pull {self.model_name} model"
        return True, "server and model are setup"
    
    def generate_mom(self, transcript) -> str:
        """ generates mom"""
        try:
            message = self.prompt_manager.chat_prompt.format_messages(transcript= transcript)
            payload = [
                {"role": "system", "content":message[0].content},
                {"role": "user", "content":message[1].content}

            ]
            logger.info(f"Sending transcript to model '{self.model_name}'")
            response = ollama.chat(model= self.model_name, messages=payload)
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"error generating MoM:{e}")
            raise RuntimeError(f"failed to generate MoM: {e}")