import sys
import os
import json
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.extractor.mom_extractor import MoMExtractor
from app.formatter.mom_formatter import MoMFormatter

def fix_mom_extraction():
    """Fix MoM extraction for the specific input."""
    # Create the specific transcript
    transcript = """
    Client meeting raees team members present were dhanvina, shlok, ridima fashion and clothing ecommerce platform with features like payment gateway, loyalty program ai feature with virtual tryon chatbot for customer care inventory management cms we have to give a quote for the client give proper professional
    """
    
    # Manually create a structured MoM data
    mom_data = {
        "meeting_title": "Client Meeting - Fashion E-commerce Platform",
        "date_time": datetime.now().strftime("%Y-%m-%d"),
        "attendees": ["Dhanvina", "Shlok", "Ridima"],
        "agenda": ["Discuss fashion and clothing e-commerce platform requirements"],
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
        "decisions": [],
        "next_steps": ["Finalize and submit the quote to the client"]
    }
    
    # Initialize MoM formatter
    mom_formatter = MoMFormatter()
    
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
            print(f"Content:")
            print("=" * 50)
            print(formatted_mom)
            print("=" * 50)
            
            # Save to file
            file_ext = "txt" if format_type == "text" else format_type
            with open(f"mom_output.{file_ext}", "w", encoding="utf-8") as f:
                f.write(formatted_mom)
            print(f"Saved to mom_output.{file_ext}")
            
        except Exception as e:
            print(f"Error formatting as {format_type}: {e}")
    
    # Now let's also try to fix the MoM extractor
    print("\nTrying to fix the MoM extractor...")
    
    # Create a custom prompt for the extractor
    custom_prompt = """
You are a professional meeting assistant that creates well-structured Minutes of Meeting (MoM) from transcripts.

Extract and organize the following information from the transcript:

1. MEETING TITLE:
   - Extract a concise, descriptive title for the meeting
   - If not explicitly stated, infer from the main topic discussed

2. DATE AND TIME:
   - Extract the meeting date and time
   - Format as "YYYY-MM-DD HH:MM" if possible
   - Include time zone if mentioned

3. ATTENDEES:
   - List all participants mentioned in the transcript
   - Identify their roles or titles if mentioned
   - Note who is the meeting organizer/chair if mentioned
   - Mark absent members if mentioned

4. AGENDA ITEMS:
   - List all agenda items discussed
   - Maintain the order as presented in the meeting
   - Include any additional items added during the meeting

5. KEY DISCUSSION POINTS:
   - Summarize the main topics discussed
   - Organize by agenda item when possible
   - Include important questions raised and answers provided
   - Note any concerns or issues mentioned
   - Attribute comments to specific speakers when relevant

6. ACTION ITEMS:
   - List all tasks or actions agreed upon
   - For each action item, include:
     * Clear description of the task
     * Person assigned to the task (use full name if available)
     * Deadline or due date if mentioned
     * Any specific requirements or constraints
   - Format as: "Task: [description] - Assigned to: [name] - Due: [date]"

7. DECISIONS MADE:
   - List all decisions finalized during the meeting
   - Include the context or reasoning behind each decision
   - Note if the decision was unanimous or if there were objections
   - Include any conditions attached to the decision

8. NEXT STEPS:
   - List follow-up actions for the next meeting
   - Include the date and time of the next meeting if mentioned
   - Note any topics deferred to future meetings

Format your response as a clear, professional MoM document with proper headings and structure.
Use bullet points where appropriate and maintain a professional tone.
Only include information that is explicitly mentioned in the transcript.
If any information is missing, indicate it clearly with "Not specified in transcript" or leave it blank.

IMPORTANT: Be precise and factual. Do not invent or assume information not present in the transcript.

For this specific transcript about a fashion e-commerce platform, make sure to:
1. Identify the team members correctly as attendees
2. Extract all mentioned features of the e-commerce platform as discussion points
3. Note the action item about preparing a quote for the client
"""

    # Initialize MoM extractor with custom prompt
    mom_extractor = MoMExtractor()
    
    # Extract MoM data
    options = {
        'include_sentiment': False,
        'include_speakers': True,
        'use_enhanced_prompts': True,
        'offline_mode': False,
        'include_analytics': False,
        'custom_prompt': custom_prompt
    }
    
    try:
        # Extract MoM data
        extracted_mom = mom_extractor.extract_with_options(transcript, options)
        
        # Format the extracted MoM data
        formatted_extracted = mom_formatter.format_with_options(extracted_mom, 'text', format_options)
        
        print("\nExtracted and formatted MoM:")
        print("=" * 50)
        print(formatted_extracted)
        print("=" * 50)
        
        # Save to file
        with open("extracted_mom_output.txt", "w", encoding="utf-8") as f:
            f.write(formatted_extracted)
        print("Saved to extracted_mom_output.txt")
        
    except Exception as e:
        print(f"Error extracting MoM: {e}")

if __name__ == "__main__":
    fix_mom_extraction()