import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.multilingual.multilingual_manager import MultilingualManager

def test_language_detection():
    """Test language detection functionality."""
    multilingual_manager = MultilingualManager()
    
    # Test English
    english_text = "This is a test of the language detection system. We are testing if it can correctly identify English text."
    lang_code, confidence = multilingual_manager.detect_language(english_text)
    print(f"English text detected as: {lang_code} with confidence {confidence:.2f}")
    
    # Test Spanish
    spanish_text = "Esto es una prueba del sistema de detección de idiomas. Estamos probando si puede identificar correctamente el texto en español."
    lang_code, confidence = multilingual_manager.detect_language(spanish_text)
    print(f"Spanish text detected as: {lang_code} with confidence {confidence:.2f}")
    
    # Test French
    french_text = "Ceci est un test du système de détection de langue. Nous testons s'il peut identifier correctement le texte français."
    lang_code, confidence = multilingual_manager.detect_language(french_text)
    print(f"French text detected as: {lang_code} with confidence {confidence:.2f}")

def test_translation():
    """Test translation functionality."""
    multilingual_manager = MultilingualManager()
    
    # Test English to Spanish
    english_text = "Hello, how are you today? This is a test of the translation system."
    spanish_translation = multilingual_manager.translate(english_text, source="en", target="es")
    print(f"English to Spanish: {spanish_translation}")
    
    # Test Spanish to English
    spanish_text = "Hola, ¿cómo estás hoy? Esta es una prueba del sistema de traducción."
    english_translation = multilingual_manager.translate(spanish_text, source="es", target="en")
    print(f"Spanish to English: {english_translation}")

def test_mom_translation():
    """Test MoM data translation."""
    multilingual_manager = MultilingualManager()
    
    # Create a sample MoM data structure
    mom_data = {
        "meeting_title": "Project Status Update",
        "date_time": "2023-05-15 10:00",
        "attendees": ["John Smith", "Jane Doe", "Bob Johnson"],
        "agenda": ["Review progress", "Discuss challenges", "Plan next steps"],
        "discussion_points": [
            "Team has completed 80% of planned tasks",
            "Budget constraints are affecting timeline",
            "Need to prioritize remaining features"
        ],
        "action_items": [
            {"description": "Update project timeline", "assignee": "John Smith", "deadline": "2023-05-20"},
            {"description": "Request additional budget", "assignee": "Jane Doe", "deadline": "2023-05-18"}
        ],
        "decisions": [
            "Postpone non-critical features to next release",
            "Schedule weekly status updates"
        ],
        "next_steps": [
            "Follow up on budget request",
            "Revise project timeline"
        ]
    }
    
    # Translate to Spanish
    spanish_mom = multilingual_manager.translate_mom(mom_data, source="en", target="es")
    print("\nTranslated MoM (English to Spanish):")
    print(f"Title: {spanish_mom['meeting_title']}")
    print(f"Action Items: {spanish_mom['action_items'][0]['description']}")
    
    # Translate back to English
    english_mom = multilingual_manager.translate_mom(spanish_mom, source="es", target="en")
    print("\nTranslated back to English:")
    print(f"Title: {english_mom['meeting_title']}")
    print(f"Action Items: {english_mom['action_items'][0]['description']}")

if __name__ == "__main__":
    print("Testing language detection...")
    test_language_detection()
    
    print("\nTesting translation...")
    test_translation()
    
    print("\nTesting MoM translation...")
    test_mom_translation()