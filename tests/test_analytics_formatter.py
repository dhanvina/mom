"""
Unit tests for the AnalyticsFormatter class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.formatter.analytics_formatter import AnalyticsFormatter

class TestAnalyticsFormatter:
    """Test cases for AnalyticsFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = AnalyticsFormatter()
        
        # Create test analytics
        self.analytics = {
            "speaking_time": {
                "John Smith": 55.0,
                "Jane Doe": 45.0,
                "Unknown": 0.0
            },
            "topics": [
                {"topic": "project timeline", "relevance": 30.0},
                {"topic": "resource allocation", "relevance": 25.0},
                {"topic": "budget discussion", "relevance": 20.0},
                {"topic": "action items", "relevance": 15.0},
                {"topic": "next steps", "relevance": 10.0}
            ],
            "efficiency_metrics": {
                "efficiency_score": 75.0,
                "participation_balance": 80.0,
                "engagement_score": 70.0,
                "content_density": 65.0,
                "time_efficiency": 85.0
            },
            "suggestions": [
                {
                    "category": "structure",
                    "suggestion": "Start meetings with a clear agenda",
                    "reason": "No clear agenda was detected",
                    "benefit": "A well-structured agenda helps participants prepare",
                    "priority": 1
                },
                {
                    "category": "content",
                    "suggestion": "Clearly define action items with assigned owners",
                    "reason": "Some action items lacked clear ownership",
                    "benefit": "Well-defined action items ensure accountability",
                    "priority": 2
                }
            ]
        }
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        formatter = AnalyticsFormatter()
        assert formatter.config == {}
        
        # Custom config
        custom_config = {"include_visualizations": True}
        formatter = AnalyticsFormatter(config=custom_config)
        assert formatter.config == custom_config
    
    def test_format_analytics_text(self):
        """Test formatting analytics as text."""
        # Format analytics as text
        result = self.formatter.format_analytics(self.analytics, "text")
        
        # Verify result is a string
        assert isinstance(result, str)
        
        # Verify key sections are included
        assert "MEETING ANALYTICS" in result
        assert "SPEAKING TIME DISTRIBUTION" in result
        assert "MAIN TOPICS DISCUSSED" in result
        assert "MEETING EFFICIENCY" in result
        assert "SUGGESTIONS FOR IMPROVEMENT" in result
        
        # Verify content
        assert "John Smith: 55.0%" in result
        assert "Jane Doe: 45.0%" in result
        assert "project timeline: 30.0%" in result
        assert "Overall Efficiency Score: 75.0/100" in result
        assert "Start meetings with a clear agenda" in result
    
    def test_format_analytics_html(self):
        """Test formatting analytics as HTML."""
        # Format analytics as HTML
        result = self.formatter.format_analytics(self.analytics, "html")
        
        # Verify result is a string
        assert isinstance(result, str)
        
        # Verify key HTML elements are included
        assert "<div class='analytics-section'>" in result
        assert "<h2>Meeting Analytics</h2>" in result
        assert "<h3>Speaking Time Distribution</h3>" in result
        assert "<h3>Main Topics Discussed</h3>" in result
        assert "<h3>Meeting Efficiency</h3>" in result
        assert "<h3>Suggestions for Improvement</h3>" in result
        
        # Verify content
        assert "John Smith" in result
        assert "Jane Doe" in result
        assert "project timeline" in result
        assert "75.0/100" in result
        assert "Start meetings with a clear agenda" in result
        
        # Verify CSS styles are included
        assert "<style>" in result
        assert ".analytics-section" in result
        assert ".bar-chart" in result
        assert ".metrics-grid" in result
    
    def test_format_analytics_markdown(self):
        """Test formatting analytics as Markdown."""
        # Format analytics as Markdown
        result = self.formatter.format_analytics(self.analytics, "markdown")
        
        # Verify result is a string
        assert isinstance(result, str)
        
        # Verify key Markdown elements are included
        assert "## Meeting Analytics" in result
        assert "### Speaking Time Distribution" in result
        assert "### Main Topics Discussed" in result
        assert "### Meeting Efficiency" in result
        assert "### Suggestions for Improvement" in result
        
        # Verify content
        assert "**John Smith**: 55.0%" in result
        assert "**Jane Doe**: 45.0%" in result
        assert "**project timeline**: 30.0%" in result
        assert "**Overall Efficiency Score**: 75.0/100" in result
        assert "**Start meetings with a clear agenda**" in result
    
    def test_format_analytics_unsupported_format(self):
        """Test formatting analytics with unsupported format."""
        # Format analytics with unsupported format
        result = self.formatter.format_analytics(self.analytics, "pdf")
        
        # Verify result is a string (should default to text format)
        assert isinstance(result, str)
        
        # Verify key sections are included (from text format)
        assert "MEETING ANALYTICS" in result
    
    def test_create_visualization_data(self):
        """Test creating visualization data."""
        # Create visualization data
        data = self.formatter.create_visualization_data(self.analytics)
        
        # Verify data structure
        assert "speaking_time" in data
        assert "topics" in data
        assert "efficiency" in data
        
        # Verify speaking time data
        assert "labels" in data["speaking_time"]
        assert "values" in data["speaking_time"]
        assert "John Smith" in data["speaking_time"]["labels"]
        assert "Jane Doe" in data["speaking_time"]["labels"]
        assert "Unknown" not in data["speaking_time"]["labels"]
        assert 55.0 in data["speaking_time"]["values"]
        assert 45.0 in data["speaking_time"]["values"]
        
        # Verify topics data
        assert "labels" in data["topics"]
        assert "values" in data["topics"]
        assert "project timeline" in data["topics"]["labels"]
        assert 30.0 in data["topics"]["values"]
        
        # Verify efficiency data
        assert "labels" in data["efficiency"]
        assert "values" in data["efficiency"]
        assert "Overall" in data["efficiency"]["labels"]
        assert 75.0 in data["efficiency"]["values"]