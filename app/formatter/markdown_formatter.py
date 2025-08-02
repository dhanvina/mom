"""
Markdown formatter module for AI-powered MoM generator.

This module provides functionality for formatting MoM data into Markdown format.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from .base_formatter import BaseFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkdownFormatter(BaseFormatter):
    """
    Formats MoM data into Markdown format.
    
    This class provides methods for formatting MoM data into Markdown documents.
    
    Attributes:
        config (Dict): Configuration options for the formatter
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MarkdownFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        super().__init__(config)
        logger.info("MarkdownFormatter initialized")
    
    def format(self, mom_data: Dict[str, Any]) -> str:
        """
        Format MoM data into a Markdown document.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            
        Returns:
            str: Markdown document as a string
        """
        try:
            logger.info("Formatting MoM data into Markdown")
            
            # Initialize markdown content
            markdown = []
            
            # Add title
            if "meeting_title" in mom_data:
                markdown.append(f"# {mom_data['meeting_title']}\n")
            
            # Add metadata section
            metadata = []
            if "date_time" in mom_data:
                metadata.append(f"**Date & Time:** {mom_data['date_time']}")
            if "location" in mom_data:
                metadata.append(f"**Location:** {mom_data['location']}")
            
            if metadata:
                markdown.append("\n".join(metadata) + "\n")
            
            # Add attendees
            if "attendees" in mom_data and mom_data["attendees"]:
                markdown.append("## Attendees\n")
                
                # Check if attendees is a list of strings or a list of dictionaries
                if isinstance(mom_data["attendees"][0], str):
                    # List of strings
                    for attendee in mom_data["attendees"]:
                        markdown.append(f"- {attendee}")
                else:
                    # List of dictionaries
                    for attendee in mom_data["attendees"]:
                        name = attendee.get("name", "")
                        role = attendee.get("role", "")
                        if role:
                            markdown.append(f"- {name} ({role})")
                        else:
                            markdown.append(f"- {name}")
                
                markdown.append("")
            
            # Add agenda
            if "agenda" in mom_data and mom_data["agenda"]:
                markdown.append("## Agenda\n")
                
                for item in mom_data["agenda"]:
                    markdown.append(f"- {item}")
                
                markdown.append("")
            
            # Add discussion points
            if "discussion_points" in mom_data and mom_data["discussion_points"]:
                markdown.append("## Discussion Points\n")
                
                for item in mom_data["discussion_points"]:
                    markdown.append(f"- {item}")
                
                markdown.append("")
            
            # Add action items
            if "action_items" in mom_data and mom_data["action_items"]:
                markdown.append("## Action Items\n")
                
                # Check if action_items is a list of strings or a list of dictionaries
                if isinstance(mom_data["action_items"][0], str):
                    # List of strings
                    for item in mom_data["action_items"]:
                        markdown.append(f"- {item}")
                else:
                    # List of dictionaries - create a table
                    markdown.append("| Action Item | Assignee | Due Date | Status |")
                    markdown.append("| ----------- | -------- | -------- | ------ |")
                    
                    for item in mom_data["action_items"]:
                        description = item.get("description", item.get("task", ""))
                        assignee = item.get("assignee", "")
                        deadline = item.get("deadline", item.get("due", ""))
                        status = item.get("status", "")
                        markdown.append(f"| {description} | {assignee} | {deadline} | {status} |")
                
                markdown.append("")
            
            # Add decisions
            if "decisions" in mom_data and mom_data["decisions"]:
                markdown.append("## Decisions\n")
                
                # Check if decisions is a list of strings or a list of dictionaries
                if isinstance(mom_data["decisions"][0], str):
                    # List of strings
                    for item in mom_data["decisions"]:
                        markdown.append(f"- {item}")
                else:
                    # List of dictionaries
                    for item in mom_data["decisions"]:
                        decision = item.get("decision", "")
                        context = item.get("context", "")
                        if context:
                            markdown.append(f"- **{decision}**")
                            markdown.append(f"  - Context: {context}")
                        else:
                            markdown.append(f"- {decision}")
                
                markdown.append("")
            
            # Add next steps
            if "next_steps" in mom_data and mom_data["next_steps"]:
                markdown.append("## Next Steps\n")
                
                for item in mom_data["next_steps"]:
                    markdown.append(f"- {item}")
                
                markdown.append("")
            
            # Add sentiment analysis if available
            if "sentiment" in mom_data:
                markdown.append("## Meeting Sentiment\n")
                
                sentiment = mom_data["sentiment"]
                if isinstance(sentiment, dict):
                    # Format sentiment data
                    overall = sentiment.get("overall", {})
                    overall_score = overall.get("score", 0)
                    overall_label = overall.get("label", "Neutral")
                    
                    markdown.append(f"**Overall Sentiment:** {overall_label} ({overall_score:.2f})\n")
                    
                    # Add participant sentiments if available
                    if "participants" in sentiment:
                        markdown.append("**Participant Sentiments:**\n")
                        
                        markdown.append("| Participant | Sentiment | Score |")
                        markdown.append("| ----------- | --------- | ----- |")
                        
                        for name, values in sentiment["participants"].items():
                            label = values.get("label", "Neutral")
                            score = values.get("score", 0)
                            markdown.append(f"| {name} | {label} | {score:.2f} |")
                        
                        markdown.append("")
                else:
                    # Simple string sentiment
                    markdown.append(f"**Overall Sentiment:** {sentiment}\n")
            
            # Add analytics if available
            if "analytics" in mom_data:
                markdown.append("## Meeting Analytics\n")
                
                analytics = mom_data["analytics"]
                if isinstance(analytics, dict):
                    # Add speaking time distribution if available
                    if "speaking_time" in analytics:
                        markdown.append("### Speaking Time Distribution\n")
                        
                        markdown.append("| Participant | Speaking Time | Percentage |")
                        markdown.append("| ----------- | ------------- | ---------- |")
                        
                        for item in analytics["speaking_time"]:
                            name = item.get("name", "")
                            time = item.get("time", 0)
                            percentage = item.get("percentage", 0)
                            markdown.append(f"| {name} | {time} seconds | {percentage:.1f}% |")
                        
                        markdown.append("")
                    
                    # Add topics if available
                    if "topics" in analytics:
                        markdown.append("### Main Topics Discussed\n")
                        
                        for topic in analytics["topics"]:
                            if isinstance(topic, dict):
                                name = topic.get("name", "")
                                frequency = topic.get("frequency", 0)
                                markdown.append(f"- {name} (mentioned {frequency} times)")
                            else:
                                markdown.append(f"- {topic}")
                        
                        markdown.append("")
                    
                    # Add any other analytics as simple paragraphs
                    for key, value in analytics.items():
                        if key not in ["speaking_time", "topics"] and isinstance(value, str):
                            markdown.append(f"**{key.replace('_', ' ').title()}:** {value}")
                    
                    markdown.append("")
            
            # Join all markdown parts
            return "\n".join(markdown)
        
        except Exception as e:
            error_msg = f"Error formatting MoM data into Markdown: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)