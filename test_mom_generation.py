import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import only what we need
from app.prompt.prompt_template import PromptManager
from app.utils.ollama_utils import OllamaManager

def test_ollama_connection():
    """Test connection to Ollama server."""
    try:
        # Initialize Ollama manager
        ollama_manager = OllamaManager("llama3:latest")
        
        # Check if server is running
        server_running = ollama_manager.is_server_running()
        print(f"Ollama server running: {server_running}")
        
        if not server_running:
            print("Ollama server is not running. Please start it and try again.")
            return False
        
        # Check if model is available
        model_available = ollama_manager.is_model_available()
        print(f"Model 'llama3:latest' available: {model_available}")
        
        if not model_available:
            print("Model is not available. Attempting to pull...")
            success = ollama_manager.pull_model()
            print(f"Pull model result: {success}")
            
        # Test simple generation
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ]
        
        response = ollama_manager.generate(messages)
        print("\nTest response from Ollama:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"Error testing Ollama connection: {e}")
        return False

def test_mom_generation():
    """Test MoM generation with a simple transcript."""
    # Create a simple transcript
    transcript = """
    Client Meeting: Raees
    
    Team members present were Dhanvina, Shlok, Ridima
    
    We discussed a fashion and clothing ecommerce platform with features like:
    - Payment gateway
    - Loyalty program
    - AI feature with virtual try-on
    - Chatbot for customer care
    - Inventory management
    - CMS
    
    We need to give a quote for the client.
    """
    
    # First test Ollama connection
    if not test_ollama_connection():
        print("Cannot test MoM generation due to Ollama connection issues.")
        return
    
    # Now try to import MoMGenerator
    try:
        from app.extractor.mom_extractor import MoMExtractor
        
        # Initialize MoM extractor
        mom_extractor = MoMExtractor()
        
        # Extract MoM data
        options = {
            'include_sentiment': False,
            'include_speakers': True,
            'use_enhanced_prompts': True,
            'offline_mode': False,
            'include_analytics': False
        }
        
        mom_data = mom_extractor.extract_with_options(transcript, options)
        
        # Print the result
        print("\nExtracted MoM data:")
        print("=" * 50)
        import json
        print(json.dumps(mom_data, indent=2))
        print("=" * 50)
        
    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error generating MoM: {e}")

if __name__ == "__main__":
    test_mom_generation()