"""
Unit tests for the EmailFormatter class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.formatter.email_formatter import EmailFormatter

class TestEmailFormatter:
    """Test cases for EmailFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = EmailFormatter()
        
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
        formatter = EmailFormatter()
        assert formatter.config == {}
        
        # Custom config
        custom_config = {
            "logo_url": "https://example.com/logo.png",
            "company_name": "Example Corp",
            "primary_color": "#FF5733"
        }
        formatter = EmailFormatter(config=custom_config)
        assert formatter.config == custom_config
    
    def test_format_basic(self):
        """Test formatting basic MoM data into email HTML."""
        # Format MoM data
        html = self.formatter.format(self.mom_data)
        
        # Verify result
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "<h1>Test Meeting</h1>" in html
        assert "<strong>Date &amp; Time:</strong> 2023-01-01 10:00" in html
        assert "<strong>Location:</strong> Conference Room A" in html
        assert "<h2>Attendees</h2>" in html
        assert "<li>John Doe</li>" in html
        assert "<h2>Agenda</h2>" in html
        assert "<h2>Discussion Points</h2>" in html
        assert "<h2>Action Items</h2>" in html
        assert "<table>" in html
        assert "<tr><th>Action Item</th><th>Assignee</th><th>Due Date</th><th>Status</th></tr>" in html
        assert "<tr class='action-item'><td>Task 1</td><td>John Doe</td><td>2023-01-15</td><td>pending</td></tr>" in html
        assert "<h2>Decisions</h2>" in html
        assert "<li class='decision'><strong>Decision 1</strong><br><em>Context: Context for decision 1</em></li>" in html
        assert "<h2>Next Steps</h2>" in html
        assert "<li class='next-step'>Step 1</li>" in html
    
    def test_format_with_sentiment(self):
        """Test formatting MoM data with sentiment analysis into email HTML."""
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
        html = self.formatter.format(mom_data)
        
        # Verify result
        assert "<h2>Meeting Sentiment</h2>" in html
        assert "<strong>Overall Sentiment:</strong> Positive (0.75)" in html
        assert "<h3>Participant Sentiments</h3>" in html
        assert "<tr><th>Participant</th><th>Sentiment</th><th>Score</th></tr>" in html
        assert "<tr><td>John Doe</td><td>Positive</td><td>0.80</td></tr>" in html
    
    def test_format_with_analytics(self):
        """Test formatting MoM data with analytics into email HTML."""
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
        html = self.formatter.format(mom_data)
        
        # Verify result
        assert "<h2>Meeting Analytics</h2>" in html
        assert "<h3>Speaking Time Distribution</h3>" in html
        assert "<tr><th>Participant</th><th>Speaking Time</th><th>Percentage</th></tr>" in html
        assert "<tr><td>John Doe</td><td>300 seconds</td><td>50.0%</td></tr>" in html
        assert "<h3>Main Topics Discussed</h3>" in html
        assert "<li>Project Status (mentioned 15 times)</li>" in html
        assert "<strong>Meeting Duration:</strong> 10 minutes" in html
        assert "<strong>Efficiency Score:</strong> 85%" in html
    
    def test_format_minimal_data(self):
        """Test formatting minimal MoM data into email HTML."""
        # Minimal MoM data
        minimal_data = {
            "meeting_title": "Minimal Meeting"
        }
        
        # Format MoM data
        html = self.formatter.format(minimal_data)
        
        # Verify result
        assert "<h1>Minimal Meeting</h1>" in html
        assert "<h2>Attendees</h2>" not in html
        assert "<h2>Agenda</h2>" not in html
    
    def test_format_string_action_items(self):
        """Test formatting MoM data with string action items into email HTML."""
        # MoM data with string action items
        mom_data = self.mom_data.copy()
        mom_data["action_items"] = ["Do task 1", "Do task 2"]
        
        # Format MoM data
        html = self.formatter.format(mom_data)
        
        # Verify result
        assert "<h2>Action Items</h2>" in html
        assert "<li class='action-item'>Do task 1</li>" in html
        assert "<li class='action-item'>Do task 2</li>" in html
        assert "<table>" not in html or ("<table>" in html and "<th>Action Item</th>" not in html)
    
    def test_format_string_decisions(self):
        """Test formatting MoM data with string decisions into email HTML."""
        # MoM data with string decisions
        mom_data = self.mom_data.copy()
        mom_data["decisions"] = ["Decision 1", "Decision 2"]
        
        # Format MoM data
        html = self.formatter.format(mom_data)
        
        # Verify result
        assert "<h2>Decisions</h2>" in html
        assert "<li class='decision'>Decision 1</li>" in html
        assert "<li class='decision'>Decision 2</li>" in html
        assert "<em>Context:" not in html
    
    def test_format_with_branding(self):
        """Test formatting MoM data with branding into email HTML."""
        # Create formatter with branding config
        branding_config = {
            "logo_url": "https://example.com/logo.png",
            "company_name": "Example Corp",
            "primary_color": "#FF5733",
            "include_branding": True
        }
        formatter = EmailFormatter(config=branding_config)
        
        # Format MoM data
        html = formatter.format(self.mom_data)
        
        # Verify result
        assert "https://example.com/logo.png" in html
        assert "Example Corp" in html
        assert "#FF5733" in html
    
    def test_format_without_branding(self):
        """Test formatting MoM data without branding into email HTML."""
        # Create formatter with branding disabled
        config = {"include_branding": False}
        formatter = EmailFormatter(config=config)
        
        # Format MoM data
        html = formatter.format(self.mom_data)
        
        # Verify result
        assert "<img src='" not in html
    
    def test_format_with_custom_template(self):
        """Test formatting MoM data with custom template into email HTML."""
        # Create formatter with custom template
        custom_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Custom Template</title>
        </head>
        <body>
            <h1>Custom Template</h1>
            {{content}}
        </body>
        </html>
        """
        config = {"template": custom_template}
        formatter = EmailFormatter(config=config)
        
        # Format MoM data
        html = formatter.format(self.mom_data)
        
        # Verify result
        assert "<h1>Custom Template</h1>" in html
        assert "<h1>Test Meeting</h1>" in html
    
    def test_format_error(self):
        """Test error handling during formatting."""
        # Mock a function to raise an exception
        with patch.object(self.formatter, '_get_email_template', side_effect=Exception("Test error")):
            # Format MoM data
            with pytest.raises(ValueError) as excinfo:
                self.formatter.format(self.mom_data)
            
            # Verify error message
            assert "Error formatting MoM data into email" in str(excinfo.value)