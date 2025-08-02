import sys
import os
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import only what we need
from app.extractor.mom_extractor import MoMExtractor
from app.formatter.mom_formatter import MoMFormatter

def test_specific_input():
    """Test MoM generation with the specific input that's causing issues."""
    # Create the specific transcript
    transcript = """
    Client meeting raees team members present were dhanvina, shlok, ridima fashion and clothing ecommerce platform with features like payment gateway, loyalty program ai feature with virtual tryon chatbot for customer care inventory management cms we have to give a quote for the client give proper professional
    """
    
    # Initialize MoM extractor and formatter
    mom_extractor = MoMExtractor()
    mom_formatter = MoMFormatter()
    
    # Generate MoM
    try:
        # Set options
        options = {
            'include_sentiment': False,
            'include_speakers': True,
            'use_enhanced_prompts': True,
            'offline_mode': False,
            'include_analytics': False
        }
        
        # Extract MoM data
        print("Extracting MoM data...")
        mom_data = mom_extractor.extract_with_options(transcript, options)
        
        # Print the extracted data
        print("\nExtracted MoM data:")
        print("=" * 50)
        print(f"Type: {type(mom_data)}")
        if isinstance(mom_data, dict):
            print(json.dumps(mom_data, indent=2))
        else:
            print(mom_data)
        print("=" * 50)
        
        # Format the MoM data
        format_options = {
            'include_tables': False,
            'include_toc': False,
            'include_frontmatter': False,
            'include_subject': False,
            'template': None,
            'include_analytics': False
        }
        
        # Try different formats
        formats = ['text', 'markdown', 'html', 'json']
        for format_type in formats:
            print(f"\nFormatting as {format_type}...")
            try:
                formatted_mom = mom_formatter.format_with_options(mom_data, format_type, format_options)
                print(f"Type: {type(formatted_mom)}")
                print(f"Content (first 100 chars): {str(formatted_mom)[:100]}...")
            except Exception as e:
                print(f"Error formatting as {format_type}: {e}")
        
    except Exception as e:
        print(f"Error generating MoM: {e}")

if __name__ == "__main__":
    test_specific_input()