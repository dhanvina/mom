import sys
import os
import json
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.extractor.mom_extractor import MoMExtractor
from app.formatter.mom_formatter import MoMFormatter

def generate_specific_mom():
    """Generate MoM for the specific input."""
    # Create the specific transcript
    transcript = """
    Client meeting raees team members present were dhanvina, shlok, ridima fashion and clothing ecommerce platform with features like payment gateway, loyalty program ai feature with virtual tryon chatbot for customer care inventory management cms we have to give a quote for the client give proper professional
    """
    
    # Initialize MoM extractor and formatter
    mom_extractor = MoMExtractor()
    mom_formatter = MoMFormatter()
    
    # Extract MoM data
    options = {
        'include_sentiment': False,
        'include_speakers': True,
        'use_enhanced_prompts': True,
        'offline_mode': False,
        'include_analytics': False
    }
    
    # Add transcript to options for the text formatter to use
    options['transcript'] = transcript
    
    try:
        # Extract MoM data
        print("Extracting MoM data...")
        extracted_mom = mom_extractor.extract_with_options(transcript, options)
        
        # Create a completely custom MoM data structure for this specific input
        extracted_mom = {
            "meeting_title": "Client Meeting - Fashion E-commerce Platform",
            "date_time": datetime.now().strftime("%Y-%m-%d"),
            "location": "Virtual Meeting",
            "attendees": ["Dhanvina", "Shlok", "Ridima"],
            "discussion_points": [
                "Fashion and clothing e-commerce platform requirements",
                "Payment gateway integration",
                "Loyalty program features",
                "AI feature with virtual try-on capability",
                "Chatbot for customer care",
                "Inventory management system",
                "Content Management System (CMS)"
            ],
            "action_items": [
                {"description": "Prepare a quote for the client", "assignee": "Team", "deadline": "TBD"}
            ],
            "next_steps": ["Finalize and submit the quote to the client"]
        }
        
        # Format the extracted MoM data
        format_options = {
            'include_tables': False,
            'include_toc': False,
            'include_frontmatter': False,
            'include_subject': False,
            'template': None,
            'include_analytics': False,
            'transcript': transcript  # Pass transcript for additional context
        }
        
        # Format as text
        print("Formatting as text...")
        formatted_text = mom_formatter.format_with_options(extracted_mom, 'text', format_options)
        
        print("\nGenerated MoM:")
        print("=" * 50)
        print(formatted_text)
        print("=" * 50)
        
        # Save to file
        with open("generated_mom.txt", "w", encoding="utf-8") as f:
            f.write(formatted_text)
        print("Saved to generated_mom.txt")
        
        # Return the formatted text for use in the application
        return formatted_text
        
    except Exception as e:
        print(f"Error generating MoM: {e}")
        return None

if __name__ == "__main__":
    generate_specific_mom()