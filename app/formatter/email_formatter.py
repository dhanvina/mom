"""
Email formatter module for AI-powered MoM generator.

This module provides functionality for formatting MoM data into email-ready HTML format.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from .base_formatter import BaseFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailFormatter(BaseFormatter):
    """
    Formats MoM data into email-ready HTML format.
    
    This class provides methods for formatting MoM data into HTML emails.
    
    Attributes:
        config (Dict): Configuration options for the formatter
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the EmailFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        super().__init__(config)
        logger.info("EmailFormatter initialized")
    
    def format(self, mom_data: Dict[str, Any]) -> str:
        """
        Format MoM data into an email-ready HTML document.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            
        Returns:
            str: HTML email content as a string
        """
        try:
            logger.info("Formatting MoM data into email-ready HTML")
            
            # Get email template
            template = self._get_email_template()
            
            # Generate content sections
            title_section = self._format_title_section(mom_data)
            metadata_section = self._format_metadata_section(mom_data)
            attendees_section = self._format_attendees_section(mom_data)
            agenda_section = self._format_agenda_section(mom_data)
            discussion_section = self._format_discussion_section(mom_data)
            action_items_section = self._format_action_items_section(mom_data)
            decisions_section = self._format_decisions_section(mom_data)
            next_steps_section = self._format_next_steps_section(mom_data)
            
            # Combine all sections
            content = (
                title_section +
                metadata_section +
                attendees_section +
                agenda_section +
                discussion_section +
                action_items_section +
                decisions_section +
                next_steps_section
            )
            
            # Add analytics if available
            if "analytics" in mom_data:
                analytics_section = self._format_analytics_section(mom_data["analytics"])
                content += analytics_section
            
            # Add sentiment if available
            if "sentiment" in mom_data:
                sentiment_section = self._format_sentiment_section(mom_data["sentiment"])
                content += sentiment_section
            
            # Fill template with content
            email_html = template.replace("{{content}}", content)
            
            # Add custom branding if configured
            if self.config.get("include_branding", True):
                email_html = self._add_branding(email_html, mom_data)
            
            return email_html
        
        except Exception as e:
            error_msg = f"Error formatting MoM data into email: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _get_email_template(self) -> str:
        """
        Get the email template.
        
        Returns:
            str: Email template HTML
        """
        # Use custom template if provided in config
        if "template" in self.config:
            return self.config["template"]
        
        # Default email template
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Meeting Minutes</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background-color: #f5f5f5;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #ddd;
                }
                h1 {
                    color: #2c3e50;
                    margin-top: 0;
                }
                h2 {
                    color: #3498db;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 5px;
                    margin-top: 25px;
                }
                .metadata {
                    background-color: #f9f9f9;
                    padding: 10px;
                    margin-bottom: 20px;
                    border-left: 4px solid #3498db;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                ul {
                    margin-top: 5px;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #eee;
                    font-size: 0.9em;
                    color: #777;
                }
                .action-item {
                    background-color: #fffaf0;
                }
                .decision {
                    background-color: #f0f8ff;
                }
                .next-step {
                    background-color: #f0fff0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Meeting Minutes</h1>
            </div>
            
            {{content}}
            
            <div class="footer">
                <p>Generated by AI-powered MoM Generator</p>
            </div>
        </body>
        </html>
        """
    
    def _format_title_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the title section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the title section
        """
        if "meeting_title" in mom_data:
            return f"<h1>{mom_data['meeting_title']}</h1>\n"
        return ""
    
    def _format_metadata_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the metadata section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the metadata section
        """
        metadata = []
        
        if "date_time" in mom_data:
            metadata.append(f"<p><strong>Date & Time:</strong> {mom_data['date_time']}</p>")
        
        if "location" in mom_data:
            metadata.append(f"<p><strong>Location:</strong> {mom_data['location']}</p>")
        
        if metadata:
            return f"<div class='metadata'>\n{''.join(metadata)}\n</div>\n"
        
        return ""
    
    def _format_attendees_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the attendees section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the attendees section
        """
        if "attendees" not in mom_data or not mom_data["attendees"]:
            return ""
        
        html = "<h2>Attendees</h2>\n<ul>\n"
        
        # Check if attendees is a list of strings or a list of dictionaries
        if isinstance(mom_data["attendees"][0], str):
            # List of strings
            for attendee in mom_data["attendees"]:
                html += f"<li>{attendee}</li>\n"
        else:
            # List of dictionaries
            for attendee in mom_data["attendees"]:
                name = attendee.get("name", "")
                role = attendee.get("role", "")
                if role:
                    html += f"<li>{name} ({role})</li>\n"
                else:
                    html += f"<li>{name}</li>\n"
        
        html += "</ul>\n"
        return html
    
    def _format_agenda_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the agenda section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the agenda section
        """
        if "agenda" not in mom_data or not mom_data["agenda"]:
            return ""
        
        html = "<h2>Agenda</h2>\n<ul>\n"
        
        for item in mom_data["agenda"]:
            html += f"<li>{item}</li>\n"
        
        html += "</ul>\n"
        return html
    
    def _format_discussion_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the discussion points section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the discussion points section
        """
        if "discussion_points" not in mom_data or not mom_data["discussion_points"]:
            return ""
        
        html = "<h2>Discussion Points</h2>\n<ul>\n"
        
        for item in mom_data["discussion_points"]:
            html += f"<li>{item}</li>\n"
        
        html += "</ul>\n"
        return html
    
    def _format_action_items_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the action items section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the action items section
        """
        if "action_items" not in mom_data or not mom_data["action_items"]:
            return ""
        
        html = "<h2>Action Items</h2>\n"
        
        # Check if action_items is a list of strings or a list of dictionaries
        if isinstance(mom_data["action_items"][0], str):
            # List of strings
            html += "<ul>\n"
            for item in mom_data["action_items"]:
                html += f"<li class='action-item'>{item}</li>\n"
            html += "</ul>\n"
        else:
            # List of dictionaries - create a table
            html += "<table>\n"
            html += "<tr><th>Action Item</th><th>Assignee</th><th>Due Date</th><th>Status</th></tr>\n"
            
            for item in mom_data["action_items"]:
                description = item.get("description", item.get("task", ""))
                assignee = item.get("assignee", "")
                deadline = item.get("deadline", item.get("due", ""))
                status = item.get("status", "")
                html += f"<tr class='action-item'><td>{description}</td><td>{assignee}</td><td>{deadline}</td><td>{status}</td></tr>\n"
            
            html += "</table>\n"
        
        return html
    
    def _format_decisions_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the decisions section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the decisions section
        """
        if "decisions" not in mom_data or not mom_data["decisions"]:
            return ""
        
        html = "<h2>Decisions</h2>\n<ul>\n"
        
        # Check if decisions is a list of strings or a list of dictionaries
        if isinstance(mom_data["decisions"][0], str):
            # List of strings
            for item in mom_data["decisions"]:
                html += f"<li class='decision'>{item}</li>\n"
        else:
            # List of dictionaries
            for item in mom_data["decisions"]:
                decision = item.get("decision", "")
                context = item.get("context", "")
                if context:
                    html += f"<li class='decision'><strong>{decision}</strong><br><em>Context: {context}</em></li>\n"
                else:
                    html += f"<li class='decision'>{decision}</li>\n"
        
        html += "</ul>\n"
        return html
    
    def _format_next_steps_section(self, mom_data: Dict[str, Any]) -> str:
        """
        Format the next steps section.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: Formatted HTML for the next steps section
        """
        if "next_steps" not in mom_data or not mom_data["next_steps"]:
            return ""
        
        html = "<h2>Next Steps</h2>\n<ul>\n"
        
        for item in mom_data["next_steps"]:
            html += f"<li class='next-step'>{item}</li>\n"
        
        html += "</ul>\n"
        return html
    
    def _format_analytics_section(self, analytics: Dict[str, Any]) -> str:
        """
        Format the analytics section.
        
        Args:
            analytics (Dict[str, Any]): Analytics data
            
        Returns:
            str: Formatted HTML for the analytics section
        """
        if not analytics:
            return ""
        
        html = "<h2>Meeting Analytics</h2>\n"
        
        # Add speaking time distribution if available
        if "speaking_time" in analytics:
            html += "<h3>Speaking Time Distribution</h3>\n"
            
            html += "<table>\n"
            html += "<tr><th>Participant</th><th>Speaking Time</th><th>Percentage</th></tr>\n"
            
            for item in analytics["speaking_time"]:
                name = item.get("name", "")
                time = item.get("time", 0)
                percentage = item.get("percentage", 0)
                html += f"<tr><td>{name}</td><td>{time} seconds</td><td>{percentage:.1f}%</td></tr>\n"
            
            html += "</table>\n"
        
        # Add topics if available
        if "topics" in analytics:
            html += "<h3>Main Topics Discussed</h3>\n<ul>\n"
            
            for topic in analytics["topics"]:
                if isinstance(topic, dict):
                    name = topic.get("name", "")
                    frequency = topic.get("frequency", 0)
                    html += f"<li>{name} (mentioned {frequency} times)</li>\n"
                else:
                    html += f"<li>{topic}</li>\n"
            
            html += "</ul>\n"
        
        # Add any other analytics as simple paragraphs
        for key, value in analytics.items():
            if key not in ["speaking_time", "topics"] and isinstance(value, str):
                html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>\n"
        
        return html
    
    def _format_sentiment_section(self, sentiment: Union[Dict[str, Any], str]) -> str:
        """
        Format the sentiment section.
        
        Args:
            sentiment (Union[Dict[str, Any], str]): Sentiment data
            
        Returns:
            str: Formatted HTML for the sentiment section
        """
        if not sentiment:
            return ""
        
        html = "<h2>Meeting Sentiment</h2>\n"
        
        if isinstance(sentiment, dict):
            # Format sentiment data
            overall = sentiment.get("overall", {})
            overall_score = overall.get("score", 0)
            overall_label = overall.get("label", "Neutral")
            
            html += f"<p><strong>Overall Sentiment:</strong> {overall_label} ({overall_score:.2f})</p>\n"
            
            # Add participant sentiments if available
            if "participants" in sentiment:
                html += "<h3>Participant Sentiments</h3>\n"
                
                html += "<table>\n"
                html += "<tr><th>Participant</th><th>Sentiment</th><th>Score</th></tr>\n"
                
                for name, values in sentiment["participants"].items():
                    label = values.get("label", "Neutral")
                    score = values.get("score", 0)
                    html += f"<tr><td>{name}</td><td>{label}</td><td>{score:.2f}</td></tr>\n"
                
                html += "</table>\n"
        else:
            # Simple string sentiment
            html += f"<p><strong>Overall Sentiment:</strong> {sentiment}</p>\n"
        
        return html
    
    def _add_branding(self, html: str, mom_data: Dict[str, Any]) -> str:
        """
        Add branding elements to the email.
        
        Args:
            html (str): Email HTML content
            mom_data (Dict[str, Any]): MoM data
            
        Returns:
            str: HTML with branding elements
        """
        # Get branding from config
        logo_url = self.config.get("logo_url", "")
        company_name = self.config.get("company_name", "")
        primary_color = self.config.get("primary_color", "#3498db")
        
        # Replace branding placeholders
        if logo_url:
            html = html.replace("<h1>Meeting Minutes</h1>", 
                               f"<div style='display: flex; align-items: center;'>"
                               f"<img src='{logo_url}' alt='{company_name}' style='max-height: 50px; margin-right: 15px;'>"
                               f"<h1>Meeting Minutes</h1>"
                               f"</div>")
        
        if company_name:
            html = html.replace("<p>Generated by AI-powered MoM Generator</p>", 
                               f"<p>Generated by AI-powered MoM Generator for {company_name}</p>")
        
        # Replace primary color
        html = html.replace("color: #3498db;", f"color: {primary_color};")
        html = html.replace("border-left: 4px solid #3498db;", f"border-left: 4px solid {primary_color};")
        
        return html