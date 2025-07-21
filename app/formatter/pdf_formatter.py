"""
PDF formatter module for AI-powered MoM generator.

This module provides functionality for formatting MoM data into PDF format.
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional, List, Union
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, ListFlowable, ListItem
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .base_formatter import BaseFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PdfFormatter(BaseFormatter):
    """
    Formats MoM data into PDF format.
    
    This class provides methods for formatting MoM data into PDF documents
    using ReportLab.
    
    Attributes:
        config (Dict): Configuration options for the formatter
        styles (Dict): Dictionary of paragraph styles
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PdfFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        super().__init__(config)
        self.styles = self._create_styles()
        logger.info("PdfFormatter initialized")
    
    def format(self, mom_data: Dict[str, Any]) -> bytes:
        """
        Format MoM data into a PDF document.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            
        Returns:
            bytes: PDF document as bytes
        """
        try:
            logger.info("Formatting MoM data into PDF")
            
            # Create a temporary file for the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                pdf_path = temp_file.name
            
            try:
                # Create the PDF document
                doc = SimpleDocTemplate(
                    pdf_path,
                    pagesize=letter,
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )
                
                # Create the content elements
                elements = []
                
                # Add title
                if "meeting_title" in mom_data:
                    elements.append(Paragraph(mom_data["meeting_title"], self.styles["Title"]))
                    elements.append(Spacer(1, 0.25 * inch))
                
                # Add date and time
                if "date_time" in mom_data:
                    elements.append(Paragraph(f"Date & Time: {mom_data['date_time']}", self.styles["Normal"]))
                    elements.append(Spacer(1, 0.1 * inch))
                
                # Add location
                if "location" in mom_data:
                    elements.append(Paragraph(f"Location: {mom_data['location']}", self.styles["Normal"]))
                    elements.append(Spacer(1, 0.1 * inch))
                
                # Add attendees
                if "attendees" in mom_data and mom_data["attendees"]:
                    elements.append(Paragraph("Attendees:", self.styles["Heading2"]))
                    attendees_list = []
                    
                    # Check if attendees is a list of strings or a list of dictionaries
                    if isinstance(mom_data["attendees"][0], str):
                        # List of strings
                        for attendee in mom_data["attendees"]:
                            attendees_list.append(ListItem(Paragraph(attendee, self.styles["Normal"])))
                    else:
                        # List of dictionaries
                        for attendee in mom_data["attendees"]:
                            name = attendee.get("name", "")
                            role = attendee.get("role", "")
                            if role:
                                attendees_list.append(ListItem(Paragraph(f"{name} ({role})", self.styles["Normal"])))
                            else:
                                attendees_list.append(ListItem(Paragraph(name, self.styles["Normal"])))
                    
                    elements.append(ListFlowable(attendees_list, bulletType='bullet', start=None))
                    elements.append(Spacer(1, 0.2 * inch))
                
                # Add agenda
                if "agenda" in mom_data and mom_data["agenda"]:
                    elements.append(Paragraph("Agenda:", self.styles["Heading2"]))
                    agenda_list = []
                    
                    for item in mom_data["agenda"]:
                        agenda_list.append(ListItem(Paragraph(item, self.styles["Normal"])))
                    
                    elements.append(ListFlowable(agenda_list, bulletType='bullet', start=None))
                    elements.append(Spacer(1, 0.2 * inch))
                
                # Add discussion points
                if "discussion_points" in mom_data and mom_data["discussion_points"]:
                    elements.append(Paragraph("Discussion Points:", self.styles["Heading2"]))
                    discussion_list = []
                    
                    for item in mom_data["discussion_points"]:
                        discussion_list.append(ListItem(Paragraph(item, self.styles["Normal"])))
                    
                    elements.append(ListFlowable(discussion_list, bulletType='bullet', start=None))
                    elements.append(Spacer(1, 0.2 * inch))
                
                # Add action items
                if "action_items" in mom_data and mom_data["action_items"]:
                    elements.append(Paragraph("Action Items:", self.styles["Heading2"]))
                    
                    # Check if action_items is a list of strings or a list of dictionaries
                    if isinstance(mom_data["action_items"][0], str):
                        # List of strings
                        action_list = []
                        for item in mom_data["action_items"]:
                            action_list.append(ListItem(Paragraph(item, self.styles["Normal"])))
                        elements.append(ListFlowable(action_list, bulletType='bullet', start=None))
                    else:
                        # List of dictionaries - create a table
                        data = [["Action Item", "Assignee", "Due Date", "Status"]]
                        
                        for item in mom_data["action_items"]:
                            description = item.get("description", item.get("task", ""))
                            assignee = item.get("assignee", "")
                            deadline = item.get("deadline", item.get("due", ""))
                            status = item.get("status", "")
                            data.append([description, assignee, deadline, status])
                        
                        # Create table
                        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.2*inch, 1*inch])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        elements.append(table)
                    
                    elements.append(Spacer(1, 0.2 * inch))
                
                # Add decisions
                if "decisions" in mom_data and mom_data["decisions"]:
                    elements.append(Paragraph("Decisions:", self.styles["Heading2"]))
                    decisions_list = []
                    
                    # Check if decisions is a list of strings or a list of dictionaries
                    if isinstance(mom_data["decisions"][0], str):
                        # List of strings
                        for item in mom_data["decisions"]:
                            decisions_list.append(ListItem(Paragraph(item, self.styles["Normal"])))
                    else:
                        # List of dictionaries
                        for item in mom_data["decisions"]:
                            decision = item.get("decision", "")
                            context = item.get("context", "")
                            if context:
                                decisions_list.append(ListItem(
                                    Paragraph(decision, self.styles["Normal"]),
                                    value=Paragraph(f"Context: {context}", self.styles["Italic"])
                                ))
                            else:
                                decisions_list.append(ListItem(Paragraph(decision, self.styles["Normal"])))
                    
                    elements.append(ListFlowable(decisions_list, bulletType='bullet', start=None))
                    elements.append(Spacer(1, 0.2 * inch))
                
                # Add next steps
                if "next_steps" in mom_data and mom_data["next_steps"]:
                    elements.append(Paragraph("Next Steps:", self.styles["Heading2"]))
                    next_steps_list = []
                    
                    for item in mom_data["next_steps"]:
                        next_steps_list.append(ListItem(Paragraph(item, self.styles["Normal"])))
                    
                    elements.append(ListFlowable(next_steps_list, bulletType='bullet', start=None))
                    elements.append(Spacer(1, 0.2 * inch))
                
                # Add sentiment analysis if available
                if "sentiment" in mom_data:
                    elements.append(Paragraph("Meeting Sentiment:", self.styles["Heading2"]))
                    
                    sentiment = mom_data["sentiment"]
                    if isinstance(sentiment, dict):
                        # Format sentiment data
                        overall = sentiment.get("overall", {})
                        overall_score = overall.get("score", 0)
                        overall_label = overall.get("label", "Neutral")
                        
                        elements.append(Paragraph(f"Overall Sentiment: {overall_label} ({overall_score:.2f})", 
                                                 self.styles["Normal"]))
                        
                        # Add participant sentiments if available
                        if "participants" in sentiment:
                            elements.append(Spacer(1, 0.1 * inch))
                            elements.append(Paragraph("Participant Sentiments:", self.styles["Normal"]))
                            
                            data = [["Participant", "Sentiment", "Score"]]
                            for name, values in sentiment["participants"].items():
                                data.append([name, values.get("label", "Neutral"), f"{values.get('score', 0):.2f}"])
                            
                            # Create table
                            table = Table(data, colWidths=[2*inch, 2*inch, 1*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                            elements.append(table)
                    else:
                        # Simple string sentiment
                        elements.append(Paragraph(f"Overall Sentiment: {sentiment}", self.styles["Normal"]))
                    
                    elements.append(Spacer(1, 0.2 * inch))
                
                # Add analytics if available
                if "analytics" in mom_data:
                    elements.append(Paragraph("Meeting Analytics:", self.styles["Heading2"]))
                    
                    analytics = mom_data["analytics"]
                    if isinstance(analytics, dict):
                        # Add speaking time distribution if available
                        if "speaking_time" in analytics:
                            elements.append(Paragraph("Speaking Time Distribution:", self.styles["Heading3"]))
                            
                            data = [["Participant", "Speaking Time", "Percentage"]]
                            for item in analytics["speaking_time"]:
                                name = item.get("name", "")
                                time = item.get("time", 0)
                                percentage = item.get("percentage", 0)
                                data.append([name, f"{time} seconds", f"{percentage:.1f}%"])
                            
                            # Create table
                            table = Table(data, colWidths=[2*inch, 2*inch, 1*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.2 * inch))
                        
                        # Add topics if available
                        if "topics" in analytics:
                            elements.append(Paragraph("Main Topics Discussed:", self.styles["Heading3"]))
                            topics_list = []
                            
                            for topic in analytics["topics"]:
                                if isinstance(topic, dict):
                                    name = topic.get("name", "")
                                    frequency = topic.get("frequency", 0)
                                    topics_list.append(ListItem(
                                        Paragraph(f"{name} (mentioned {frequency} times)", self.styles["Normal"])
                                    ))
                                else:
                                    topics_list.append(ListItem(Paragraph(topic, self.styles["Normal"])))
                            
                            elements.append(ListFlowable(topics_list, bulletType='bullet', start=None))
                            elements.append(Spacer(1, 0.2 * inch))
                    
                    # Add any other analytics as simple paragraphs
                    for key, value in analytics.items():
                        if key not in ["speaking_time", "topics"] and isinstance(value, str):
                            elements.append(Paragraph(f"{key.replace('_', ' ').title()}: {value}", self.styles["Normal"]))
                            elements.append(Spacer(1, 0.1 * inch))
                
                # Build the PDF
                doc.build(elements)
                
                # Read the PDF file
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                
                return pdf_bytes
            
            finally:
                # Clean up temporary file
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
        
        except Exception as e:
            error_msg = f"Error formatting MoM data into PDF: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _create_styles(self) -> Dict[str, Any]:
        """
        Create paragraph styles for the PDF document.
        
        Returns:
            Dict[str, Any]: Dictionary of paragraph styles
        """
        styles = getSampleStyleSheet()
        
        # Customize styles
        styles["Title"].alignment = TA_CENTER
        styles["Title"].fontSize = 16
        
        styles["Heading2"].fontSize = 14
        styles["Heading2"].spaceAfter = 6
        
        styles["Heading3"].fontSize = 12
        styles["Heading3"].spaceAfter = 6
        
        # Add custom styles
        try:
            styles.add(
                ParagraphStyle(
                    name='Italic',
                    parent=styles['Normal'],
                    fontName='Helvetica-Oblique',
                    fontSize=10
                )
            )
        except KeyError:
            # Style already exists, skip adding it
            pass
        
        return styles