"""
Text formatter module for AI-powered MoM generator.

This module provides functionality for formatting structured MoM data
into plain text format.
"""

import logging
from typing import Any, Dict, Optional
from .base_formatter import BaseFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextFormatter(BaseFormatter):
    """
    Formats MoM data into plain text.
    
    This class provides methods for formatting structured MoM data into
    a well-formatted plain text document.
    
    Attributes:
        config (Dict): Configuration options for the formatter
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TextFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        super().__init__(config)
        logger.info("TextFormatter initialized")
    
    def format(self, mom_data: Dict[str, Any]) -> str:
        """
        Format MoM data into plain text.
        
        Args:
            mom_data (Dict[str, Any]): Structured MoM data
            
        Returns:
            str: Formatted plain text
        """
        logger.info("Formatting MoM data as plain text")
        
        # Get section separator from config or use default
        section_separator = self.config.get('section_separator', '\n\n')
        
        # Format each section
        sections = []
        
        # Title section
        title = mom_data.get('meeting_title', 'Minutes of Meeting')
        sections.append(f"MINUTES OF MEETING: {title}")
        
        # Date and time
        date_time = mom_data.get('date_time', 'N/A')
        sections.append(f"DATE & TIME: {date_time}")
        
        # Location if available
        if 'location' in mom_data and mom_data['location']:
            location = mom_data['location']
            sections.append(f"LOCATION: {location}")
        
        # Attendees
        sections.append("ATTENDEES:")
        if 'attendees' in mom_data and mom_data['attendees']:
            if isinstance(mom_data['attendees'], list):
                for attendee in mom_data['attendees']:
                    if isinstance(attendee, dict):
                        name = attendee.get('name', '')
                        role = attendee.get('role', '')
                        if role:
                            sections.append(f"- {name} ({role})")
                        else:
                            sections.append(f"- {name}")
                    else:
                        # Clean up any prefixes like '+' or '*' that might appear
                        attendee_str = str(attendee).strip()
                        if attendee_str.startswith('+') or attendee_str.startswith('*'):
                            attendee_str = attendee_str[1:].strip()
                        sections.append(f"- {attendee_str}")
            else:
                sections.append(str(mom_data['attendees']))
        else:
            sections.append("- No attendees specified")
        
        # Agenda - only include if there are actual agenda items
        if 'agenda' in mom_data and mom_data['agenda']:
            sections.append("AGENDA:")
            if isinstance(mom_data['agenda'], list):
                for item in mom_data['agenda']:
                    sections.append(f"- {item}")
            else:
                sections.append(str(mom_data['agenda']))
        
        # Discussion points
        sections.append("DISCUSSION POINTS:")
        if 'discussion_points' in mom_data and mom_data['discussion_points']:
            if isinstance(mom_data['discussion_points'], list):
                for point in mom_data['discussion_points']:
                    sections.append(f"- {point}")
            else:
                sections.append(str(mom_data['discussion_points']))
        else:
            # Try to extract discussion points from the transcript if available
            if 'transcript' in mom_data:
                transcript = mom_data['transcript']
                # Extract key phrases that might be discussion points
                import re
                features = re.findall(r'(\w+\s+\w+(?:\s+\w+)?)\s+(?:feature|platform|system|program)', transcript.lower())
                if features:
                    for feature in features:
                        sections.append(f"- {feature.strip().title()} feature/system")
                else:
                    sections.append("- No specific discussion points extracted")
            else:
                sections.append("- No discussion points specified")
        
        # Action items
        sections.append("ACTION ITEMS:")
        if 'action_items' in mom_data and mom_data['action_items']:
            if isinstance(mom_data['action_items'], list):
                for item in mom_data['action_items']:
                    if isinstance(item, dict):
                        desc = item.get('description', '')
                        assignee = item.get('assignee', '')
                        deadline = item.get('deadline', '')
                        if assignee and deadline:
                            sections.append(f"- {desc} (Assigned to: {assignee}, Due: {deadline})")
                        elif assignee:
                            sections.append(f"- {desc} (Assigned to: {assignee})")
                        else:
                            sections.append(f"- {desc}")
                    else:
                        sections.append(f"- {item}")
            else:
                sections.append(str(mom_data['action_items']))
        else:
            # Try to extract action items from the transcript
            if 'transcript' in mom_data:
                transcript = mom_data['transcript']
                if 'quote' in transcript.lower() or 'proposal' in transcript.lower():
                    sections.append("- Prepare a quote for the client")
                else:
                    sections.append("- No specific action items extracted")
            else:
                sections.append("- No action items specified")
        
        # Decisions
        sections.append("DECISIONS:")
        if 'decisions' in mom_data and mom_data['decisions']:
            if isinstance(mom_data['decisions'], list):
                for decision in mom_data['decisions']:
                    if isinstance(decision, dict):
                        sections.append(f"- {decision.get('decision', '')}")
                    else:
                        sections.append(f"- {decision}")
            else:
                sections.append(str(mom_data['decisions']))
        else:
            sections.append("- No decisions recorded")
        
        # Next steps
        sections.append("NEXT STEPS:")
        if 'next_steps' in mom_data and mom_data['next_steps']:
            if isinstance(mom_data['next_steps'], list):
                for step in mom_data['next_steps']:
                    sections.append(f"- {step}")
            else:
                sections.append(str(mom_data['next_steps']))
        else:
            # Try to infer next steps from action items
            if 'action_items' in mom_data and mom_data['action_items']:
                sections.append("- Follow up on action items")
            else:
                sections.append("- No specific next steps specified")
        
        # Join all sections
        return section_separator.join(sections)