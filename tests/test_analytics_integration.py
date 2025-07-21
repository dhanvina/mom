"""
Unit tests for analytics integration with MoM output.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.formatter.analytics_formatter import AnalyticsFormatter
from app.analyzer.meeting_analytics import MeetingAnalytics
from app.formatter.mom_formatter import MoMFormatter

class TestAnalyticsIntegration:
    """Test cases for analytics integration with MoM output."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analytics_formatter = AnalyticsFormatter()
        self.meeting_analytics = MeetingAnalytics()
        self.mom_formatter = MoMFormatter()
        
        # Sample analytics data
        self.analytics_data = {
            "speaking_time": {
                "John Doe": 45.5,
                "Jane Smith": 35.2,
                "Mark Johnson": 19.3
            },
            "topics": [
                {
                    "topic": "Budget Planning",
                    "relevance": 85.0,
                    "time_spent": "15 minutes",
                    "key_participants": ["John Doe", "Jane Smith"]
                },
                {
                    "topic": "Project Timeline",
                    "relevance": 70.0,
                    "time_spent": "10 minutes",
                    "key_participants": ["Jane Smith", "Mark Johnson"]
                },
                {
                    "topic": "Resource Allocation",
                    "relevance": 45.0,
                    "time_spent": "5 minutes",
                    "key_participants": ["John Doe"]
                }
            ],
            "efficiency_metrics": {
                "efficiency_score": 75.5,
                "participation_balance": 68.2,
                "engagement_score": 82.1,
                "content_density": 71.3,
                "time_efficiency": 78.9,
                "duration_minutes": 45,
                "action_items": 3,
                "decisions": 2,
                "has_agenda": True,
                "has_summary": False
            },
            "suggestions": [
                {
                    "category": "structure",
                    "suggestion": "End meetings with a summary of key points and action items",
                    "reason": "No clear summary was detected at the end of the meeting",
                    "benefit": "Summaries ensure everyone leaves with the same understanding",
                    "priority": 1
                },
                {
                    "category": "participation",
                    "suggestion": "Encourage more balanced participation among attendees",
                    "reason": "Some participants dominated the conversation",
                    "benefit": "Balanced participation ensures all perspectives are heard",
                    "priority": 2
                },
                {
                    "category": "content",
                    "suggestion": "Focus on substantive content and minimize tangents",
                    "reason": "The meeting had some off-topic discussions",
                    "benefit": "Focusing on substantive content makes meetings more productive",
                    "priority": 3
                }
            ]
        }
        
        # Sample MoM data
        self.mom_data = {
            "meeting_title": "Project Planning Meeting",
            "date_time": "2023-12-01 10:00",
            "attendees": ["John Doe", "Jane Smith", "Mark Johnson"],
            "agenda": ["Budget Planning", "Project Timeline", "Resource Allocation"],
            "discussion_points": [
                {
                    "topic": "Budget Planning",
                    "details": "Discussed Q4 budget allocation and resource needs"
                },
                {
                    "topic": "Project Timeline",
                    "details": "Reviewed project milestones and delivery dates"
                }
            ],
            "action_items": [
                {
                    "description": "Finalize budget proposal",
                    "assignee": "John Doe",
                    "deadline": "2023-12-15",
                    "status": "pending"
                },
                {
                    "description": "Update project timeline",
                    "assignee": "Jane Smith",
                    "deadline": "2023-12-10",
                    "status": "pending"
                }
            ],
            "decisions": [
                "Approved additional budget for Q4",
                "Extended project deadline by one week"
            ],
            "next_steps": [
                "Schedule follow-up meeting",
                "Distribute updated timeline"
            ]
        }
    
    def test_format_analytics_summary(self):
        """Test creating analytics summary."""
        summary = self.analytics_formatter.format_analytics_summary(self.analytics_data)
        
        # Verify summary structure
        assert "efficiency_rating" in summary
        assert "efficiency_score" in summary
        assert "key_metrics" in summary
        assert "top_topics" in summary
        assert "top_suggestions" in summary
        assert "speaking_leaders" in summary
        
        # Verify efficiency rating
        assert summary["efficiency_rating"] == "Good"  # 75.5 score
        assert summary["efficiency_score"] == 75.5
        
        # Verify key metrics
        key_metrics = summary["key_metrics"]
        assert key_metrics["participation_balance"] == 68.2
        assert key_metrics["engagement_score"] == 82.1
        assert key_metrics["content_density"] == 71.3
        assert key_metrics["time_efficiency"] == 78.9
        
        # Verify top topics
        assert len(summary["top_topics"]) == 3
        assert "Budget Planning" in summary["top_topics"]
        assert "Project Timeline" in summary["top_topics"]
        assert "Resource Allocation" in summary["top_topics"]
        
        # Verify top suggestions
        assert len(summary["top_suggestions"]) == 3
        assert any("summary" in suggestion for suggestion in summary["top_suggestions"])
        
        # Verify speaking leaders
        assert len(summary["speaking_leaders"]) == 3
        assert summary["speaking_leaders"][0] == "John Doe"  # Highest speaking time
        assert summary["speaking_leaders"][1] == "Jane Smith"
        assert summary["speaking_leaders"][2] == "Mark Johnson"
    
    def test_create_analytics_section(self):
        """Test creating complete analytics section."""
        section = self.analytics_formatter.create_analytics_section(
            self.analytics_data, 
            format_type="text", 
            include_visualizations=True
        )
        
        # Verify section structure
        assert "title" in section
        assert "content" in section
        assert "summary" in section
        assert "visualizations" in section
        
        # Verify title
        assert section["title"] == "Meeting Analytics"
        
        # Verify content is formatted
        assert "MEETING ANALYTICS" in section["content"]
        assert "SPEAKING TIME DISTRIBUTION" in section["content"]
        assert "MAIN TOPICS DISCUSSED" in section["content"]
        assert "MEETING EFFICIENCY" in section["content"]
        assert "SUGGESTIONS FOR IMPROVEMENT" in section["content"]
        
        # Verify visualizations
        visualizations = section["visualizations"]
        assert "speaking_time" in visualizations
        assert "topics" in visualizations
        assert "efficiency" in visualizations
        
        # Verify speaking time visualization data
        speaking_viz = visualizations["speaking_time"]
        assert "labels" in speaking_viz
        assert "values" in speaking_viz
        assert len(speaking_viz["labels"]) == 3
        assert len(speaking_viz["values"]) == 3
        assert "John Doe" in speaking_viz["labels"]
        assert 45.5 in speaking_viz["values"]
    
    def test_integrate_with_mom_data(self):
        """Test integrating analytics with MoM data."""
        integrated_data = self.analytics_formatter.integrate_with_mom_data(
            self.mom_data, 
            self.analytics_data
        )
        
        # Verify original data is preserved
        assert integrated_data["meeting_title"] == "Project Planning Meeting"
        assert integrated_data["date_time"] == "2023-12-01 10:00"
        
        # Verify analytics summary is added to metadata
        assert "metadata" in integrated_data
        assert "analytics_summary" in integrated_data["metadata"]
        
        analytics_summary = integrated_data["metadata"]["analytics_summary"]
        assert analytics_summary["efficiency_rating"] == "Good"
        assert analytics_summary["efficiency_score"] == 75.5
        
        # Verify enhanced attendees with participation data
        attendees = integrated_data["attendees"]
        assert len(attendees) == 3
        
        # Check if attendees are enhanced with participation data
        john_attendee = next((a for a in attendees if (isinstance(a, dict) and a.get("name") == "John Doe") or a == "John Doe"), None)
        assert john_attendee is not None
        
        if isinstance(john_attendee, dict):
            assert "participation_percentage" in john_attendee
            assert john_attendee["participation_percentage"] == 45.5
        
        # Verify enhanced discussion points with topic relevance
        discussion_points = integrated_data["discussion_points"]
        budget_discussion = next((d for d in discussion_points if d["topic"] == "Budget Planning"), None)
        assert budget_discussion is not None
        
        if "relevance_score" in budget_discussion:
            assert budget_discussion["relevance_score"] == 85.0
            assert budget_discussion["time_spent"] == "15 minutes"
        
        # Verify suggested action items are added
        action_items = integrated_data["action_items"]
        original_action_count = len(self.mom_data["action_items"])
        assert len(action_items) >= original_action_count
        
        # Check for process improvement suggestions
        process_improvements = [item for item in action_items if item.get("type") == "process_improvement"]
        assert len(process_improvements) > 0
        
        # Verify analytics section is added
        assert "analytics" in integrated_data
        analytics_section = integrated_data["analytics"]
        assert "title" in analytics_section
        assert "content" in analytics_section
        assert "summary" in analytics_section
    
    def test_format_analytics_text(self):
        """Test formatting analytics as text."""
        formatted_text = self.analytics_formatter._format_text(self.analytics_data)
        
        # Verify text formatting
        assert "MEETING ANALYTICS" in formatted_text
        assert "SPEAKING TIME DISTRIBUTION" in formatted_text
        assert "MAIN TOPICS DISCUSSED" in formatted_text
        assert "MEETING EFFICIENCY" in formatted_text
        assert "SUGGESTIONS FOR IMPROVEMENT" in formatted_text
        
        # Verify speaking time data
        assert "John Doe: 45.5%" in formatted_text
        assert "Jane Smith: 35.2%" in formatted_text
        assert "Mark Johnson: 19.3%" in formatted_text
        
        # Verify topics data
        assert "Budget Planning: 85.0%" in formatted_text
        assert "Project Timeline: 70.0%" in formatted_text
        
        # Verify efficiency metrics
        assert "Overall Efficiency Score: 75.5/100" in formatted_text
        assert "Participation Balance: 68.2/100" in formatted_text
        assert "Engagement Score: 82.1/100" in formatted_text
        
        # Verify suggestions
        assert "End meetings with a summary" in formatted_text
        assert "Encourage more balanced participation" in formatted_text
    
    def test_format_analytics_html(self):
        """Test formatting analytics as HTML."""
        formatted_html = self.analytics_formatter._format_html(self.analytics_data)
        
        # Verify HTML structure
        assert "<div class='analytics-section'>" in formatted_html
        assert "<h2>Meeting Analytics</h2>" in formatted_html
        assert "<h3>Speaking Time Distribution</h3>" in formatted_html
        assert "<h3>Main Topics Discussed</h3>" in formatted_html
        assert "<h3>Meeting Efficiency</h3>" in formatted_html
        assert "<h3>Suggestions for Improvement</h3>" in formatted_html
        
        # Verify CSS styles are included
        assert "<style>" in formatted_html
        assert ".analytics-section" in formatted_html
        assert ".bar-chart" in formatted_html
        assert ".metrics-grid" in formatted_html
        
        # Verify data is included
        assert "John Doe" in formatted_html
        assert "45.5%" in formatted_html
        assert "Budget Planning" in formatted_html
        assert "85.0%" in formatted_html
    
    def test_format_analytics_markdown(self):
        """Test formatting analytics as Markdown."""
        formatted_md = self.analytics_formatter._format_markdown(self.analytics_data)
        
        # Verify Markdown structure
        assert "## Meeting Analytics" in formatted_md
        assert "### Speaking Time Distribution" in formatted_md
        assert "### Main Topics Discussed" in formatted_md
        assert "### Meeting Efficiency" in formatted_md
        assert "### Suggestions for Improvement" in formatted_md
        
        # Verify Markdown formatting
        assert "- **John Doe**: 45.5%" in formatted_md
        assert "- **Budget Planning**: 85.0%" in formatted_md
        assert "- **Overall Efficiency Score**: 75.5/100" in formatted_md
        
        # Verify suggestions formatting
        assert "1. **End meetings with a summary" in formatted_md
        assert "2. **Encourage more balanced participation" in formatted_md
    
    def test_create_visualization_data(self):
        """Test creating visualization data."""
        viz_data = self.analytics_formatter.create_visualization_data(self.analytics_data)
        
        # Verify visualization data structure
        assert "speaking_time" in viz_data
        assert "topics" in viz_data
        assert "efficiency" in viz_data
        
        # Verify speaking time visualization
        speaking_viz = viz_data["speaking_time"]
        assert "labels" in speaking_viz
        assert "values" in speaking_viz
        assert len(speaking_viz["labels"]) == 3
        assert len(speaking_viz["values"]) == 3
        assert speaking_viz["labels"] == ["John Doe", "Jane Smith", "Mark Johnson"]
        assert speaking_viz["values"] == [45.5, 35.2, 19.3]
        
        # Verify topics visualization
        topics_viz = viz_data["topics"]
        assert "labels" in topics_viz
        assert "values" in topics_viz
        assert len(topics_viz["labels"]) == 3
        assert len(topics_viz["values"]) == 3
        assert topics_viz["labels"] == ["Budget Planning", "Project Timeline", "Resource Allocation"]
        assert topics_viz["values"] == [85.0, 70.0, 45.0]
        
        # Verify efficiency visualization
        efficiency_viz = viz_data["efficiency"]
        assert "labels" in efficiency_viz
        assert "values" in efficiency_viz
        assert len(efficiency_viz["labels"]) == 5
        assert len(efficiency_viz["values"]) == 5
        assert efficiency_viz["labels"] == ["Overall", "Participation", "Engagement", "Content", "Time"]
        assert efficiency_viz["values"] == [75.5, 68.2, 82.1, 71.3, 78.9]