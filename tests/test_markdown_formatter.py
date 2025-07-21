"""
Unit tests for the MarkdownFormatter class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.formatter.markdown_formatter import MarkdownFormatter

class TestMarkdownFormatter:
    """Test cases for MarkdownFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = MarkdownFormatter()
        
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
        formatter = MarkdownFormatter()
        assert formatter.config == {}
        
        # Custom config
        custom_config = {"table_format": "github"}
        formatter = MarkdownFormatter(config=custom_config)
        assert formatter.config == custom_config
    
    def test_format_basic(self):
        """Test formatting basic MoM data into Markdown."""
        # Format MoM data
        markdown = self.formatter.format(self.mom_data)
        
        # Verify result
        assert isinstance(markdown, str)
        assert "# Test Meeting" in markdown
        assert "**Date & Time:** 2023-01-01 10:00" in markdown
        assert "**Location:** Conference Room A" in markdown
        assert "## Attendees" in markdown
        assert "- John Doe" in markdown
        assert "## Agenda" in markdown
        assert "## Discussion Points" in markdown
        assert "## Action Items" in markdown
        assert "| Action Item | Assignee | Due Date | Status |" in markdown
        assert "| Task 1 | John Doe | 2023-01-15 | pending |" in markdown
        assert "## Decisions" in markdown
        assert "**Decision 1**" in markdown
        assert "Context: Context for decision 1" in markdown
        assert "## Next Steps" in markdown
        assert "- Step 1" in markdown
    
    def test_format_with_sentiment(self):
        """Test formatting MoM data with sentiment analysis into Markdown."""
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
        markdown = self.formatter.format(mom_data)
        
        # Verify result
        assert "## Meeting Sentiment" in markdown
        assert "**Overall Sentiment:** Positive (0.75)" in markdown
        assert "**Participant Sentiments:**" in markdown
        assert "| Participant | Sentiment | Score |" in markdown
        assert "| John Doe | Positive | 0.80 |" in markdown
    
    def test_format_with_analytics(self):
        """Test formatting MoM data with analytics into Markdown."""
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
        markdown = self.formatter.format(mom_data)
        
        # Verify result
        assert "## Meeting Analytics" in markdown
        assert "### Speaking Time Distribution" in markdown
        assert "| Participant | Speaking Time | Percentage |" in markdown
        assert "| John Doe | 300 seconds | 50.0% |" in markdown
        assert "### Main Topics Discussed" in markdown
        assert "- Project Status (mentioned 15 times)" in markdown
        assert "**Meeting Duration:** 10 minutes" in markdown
        assert "**Efficiency Score:** 85%" in markdown
    
    def test_format_minimal_data(self):
        """Test formatting minimal MoM data into Markdown."""
        # Minimal MoM data
        minimal_data = {
            "meeting_title": "Minimal Meeting"
        }
        
        # Format MoM data
        markdown = self.formatter.format(minimal_data)
        
        # Verify result
        assert "# Minimal Meeting" in markdown
        assert "## Attendees" not in markdown
        assert "## Agenda" not in markdown
    
    def test_format_string_action_items(self):
        """Test formatting MoM data with string action items into Markdown."""
        # MoM data with string action items
        mom_data = self.mom_data.copy()
        mom_data["action_items"] = ["Do task 1", "Do task 2"]
        
        # Format MoM data
        markdown = self.formatter.format(mom_data)
        
        # Verify result
        assert "## Action Items" in markdown
        assert "- Do task 1" in markdown
        assert "- Do task 2" in markdown
        assert "| Action Item |" not in markdown
    
    def test_format_string_decisions(self):
        """Test formatting MoM data with string decisions into Markdown."""
        # MoM data with string decisions
        mom_data = self.mom_data.copy()
        mom_data["decisions"] = ["Decision 1", "Decision 2"]
        
        # Format MoM data
        markdown = self.formatter.format(mom_data)
        
        # Verify result
        assert "## Decisions" in markdown
        assert "- Decision 1" in markdown
        assert "- Decision 2" in markdown
        assert "Context:" not in markdown
    
    def test_format_error(self):
        """Test error handling during formatting."""
        # Mock a function to raise an exception
        with patch.object(self.formatter, 'format', side_effect=Exception("Test error")):
            # Format MoM data
            with pytest.raises(ValueError) as excinfo:
                self.formatter.format(self.mom_data)
            
            # Verify error message
            assert "Error formatting MoM data into Markdown" in str(excinfo.value)