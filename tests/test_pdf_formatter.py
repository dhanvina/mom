"""
Unit tests for the PdfFormatter class.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import tempfile
from app.formatter.pdf_formatter import PdfFormatter

class TestPdfFormatter:
    """Test cases for PdfFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = PdfFormatter()
        
        # Create test MoM data
        self.mom_data = {
            "meeting_title": "Test Meeting",
            "date_time": "2023-01-01 10:00",
            "location": "Conference Room A",
            "attendees": ["John Doe", "Jane Smith", "Bob Johnson"],
            "agenda": ["Item 1", "Item 2", "Item 3"],
            "discussion_points": ["Discussion 1", "Discussion 2"],
            "action_items": [
                {"description": "Task 1", "assignee": "John Doe", "deadline": "2023-01-15", "status": "pending"},
                {"description": "Task 2", "assignee": "Jane Smith", "deadline": "2023-01-20", "status": "in_progress"}
            ],
            "decisions": [
                {"decision": "Decision 1", "context": "Context for decision 1"},
                {"decision": "Decision 2", "context": "Context for decision 2"}
            ],
            "next_steps": ["Step 1", "Step 2"]
        }
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        formatter = PdfFormatter()
        assert formatter.config == {}
        assert formatter.styles is not None
        
        # Custom config
        custom_config = {"page_size": "A4", "margin": 1.0}
        formatter = PdfFormatter(config=custom_config)
        assert formatter.config == custom_config
    
    def test_format_basic(self):
        """Test formatting basic MoM data into PDF."""
        # Format MoM data
        pdf_bytes = self.formatter.format(self.mom_data)
        
        # Verify result
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_format_with_sentiment(self):
        """Test formatting MoM data with sentiment analysis into PDF."""
        # Add sentiment data
        mom_data = self.mom_data.copy()
        mom_data["sentiment"] = {
            "overall": {"score": 0.75, "label": "Positive"},
            "participants": {
                "John Doe": {"score": 0.8, "label": "Positive"},
                "Jane Smith": {"score": 0.6, "label": "Neutral"},
                "Bob Johnson": {"score": 0.9, "label": "Positive"}
            }
        }
        
        # Format MoM data
        pdf_bytes = self.formatter.format(mom_data)
        
        # Verify result
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_format_with_analytics(self):
        """Test formatting MoM data with analytics into PDF."""
        # Add analytics data
        mom_data = self.mom_data.copy()
        mom_data["analytics"] = {
            "speaking_time": [
                {"name": "John Doe", "time": 300, "percentage": 50.0},
                {"name": "Jane Smith", "time": 180, "percentage": 30.0},
                {"name": "Bob Johnson", "time": 120, "percentage": 20.0}
            ],
            "topics": [
                {"name": "Project Status", "frequency": 15},
                {"name": "Budget", "frequency": 10},
                {"name": "Timeline", "frequency": 8}
            ],
            "meeting_duration": "10 minutes",
            "efficiency_score": "85%"
        }
        
        # Format MoM data
        pdf_bytes = self.formatter.format(mom_data)
        
        # Verify result
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_format_minimal_data(self):
        """Test formatting minimal MoM data into PDF."""
        # Minimal MoM data
        minimal_data = {
            "meeting_title": "Minimal Meeting"
        }
        
        # Format MoM data
        pdf_bytes = self.formatter.format(minimal_data)
        
        # Verify result
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_format_error(self):
        """Test error handling during formatting."""
        # Mock SimpleDocTemplate to raise an exception
        with patch('app.formatter.pdf_formatter.SimpleDocTemplate', side_effect=Exception("Test error")):
            # Format MoM data
            with pytest.raises(ValueError) as excinfo:
                self.formatter.format(self.mom_data)
            
            # Verify error message
            assert "Error formatting MoM data into PDF" in str(excinfo.value)
    
    def test_create_styles(self):
        """Test creating paragraph styles."""
        # Get styles
        styles = self.formatter._create_styles()
        
        # Verify styles
        assert "Title" in styles
        assert "Heading2" in styles
        assert "Normal" in styles
        assert "Italic" in styles