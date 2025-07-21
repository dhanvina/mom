"""
Unit tests for the MoMFormatter class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.formatter.mom_formatter import MoMFormatter
from app.template.template_model import Template, BrandingElement

class TestMoMFormatter:
    """Test cases for MoMFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = MoMFormatter()
        
        # Create a test template
        self.template = Template(
            name="Test Template",
            description="Test template for unit tests",
            format_type="text",
            content="""
MINUTES OF MEETING

Meeting Title: {meeting_title}
Date & Time: {date_time}

Attendees:
{attendees}

Agenda:
{agenda}

Key Discussion Points:
{discussion_points}

Action Items:
{action_items}

Decisions Made:
{decisions}

Next Steps:
{next_steps}
            """.strip(),
            sections=["meeting_title", "date_time", "attendees", "agenda", 
                     "discussion_points", "action_items", "decisions", "next_steps"]
        )
        
        # Create test MoM data
        self.mom_data = {
            "meeting_title": "Test Meeting",
            "date_time": "2023-01-01 10:00",
            "attendees": ["John Doe", "Jane Smith"],
            "agenda": ["Item 1", "Item 2"],
            "discussion_points": ["Discussion 1", "Discussion 2"],
            "action_items": [
                {"task": "Task 1", "assignee": "John Doe", "due": "2023-01-15"},
                {"task": "Task 2", "assignee": "Jane Smith", "due": "2023-01-20"}
            ],
            "decisions": ["Decision 1", "Decision 2"],
            "next_steps": ["Step 1", "Step 2"]
        }
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        formatter = MoMFormatter()
        assert formatter.config == {}
        
        # Custom config
        custom_config = {"template": {"custom": "value"}}
        formatter = MoMFormatter(config=custom_config)
        assert formatter.config == custom_config
    
    @patch('app.template.template_customizer.TemplateCustomizer.apply')
    def test_format(self, mock_apply):
        """Test formatting MoM data using a template."""
        # Mock apply method
        mock_apply.return_value = "Formatted content"
        
        # Format MoM data
        result = self.formatter.format(self.mom_data, self.template)
        
        # Verify apply was called with correct parameters
        mock_apply.assert_called_once_with(self.template, self.mom_data, None, None)
        
        # Verify result
        assert result == "Formatted content"
    
    @patch('app.template.template_customizer.TemplateCustomizer.apply')
    @patch('app.formatter.analytics_formatter.AnalyticsFormatter.format_analytics')
    def test_format_with_analytics(self, mock_format_analytics, mock_apply):
        """Test formatting MoM data with analytics."""
        # Mock apply method
        mock_apply.return_value = "Formatted content"
        
        # Mock format_analytics method
        mock_format_analytics.return_value = "Analytics content"
        
        # Add analytics to MoM data
        mom_data_with_analytics = self.mom_data.copy()
        mom_data_with_analytics["analytics"] = {"test": "analytics"}
        
        # Format MoM data with analytics
        result = self.formatter.format(mom_data_with_analytics, self.template, include_analytics=True)
        
        # Verify apply was called with correct parameters
        mock_apply.assert_called_once_with(self.template, mom_data_with_analytics, None, None)
        
        # Verify format_analytics was called with correct parameters
        mock_format_analytics.assert_called_once_with({"test": "analytics"}, self.template.format_type)
        
        # Verify result includes both content and analytics
        assert "Formatted content" in result
        assert "Analytics content" in result
    
    @patch('app.template.template_customizer.TemplateCustomizer.apply_with_template_name')
    def test_format_with_template_name(self, mock_apply_with_template_name):
        """Test formatting MoM data using a template by name."""
        # Mock apply_with_template_name method
        mock_apply_with_template_name.return_value = "Formatted content"
        
        # Mock template manager
        template_manager = MagicMock()
        
        # Format MoM data
        result = self.formatter.format_with_template_name(
            self.mom_data, "Test Template", template_manager
        )
        
        # Verify apply_with_template_name was called with correct parameters
        mock_apply_with_template_name.assert_called_once_with(
            "Test Template", self.mom_data, template_manager, "en", None, None
        )
        
        # Verify result
        assert result == "Formatted content"
    
    def test_format_with_format_type(self):
        """Test formatting MoM data using a template of a specific format type."""
        # Mock template manager
        template_manager = MagicMock()
        template_manager.get_templates.return_value = [self.template]
        template_manager.get_template.return_value = self.template
        
        # Mock format method
        self.formatter.format = MagicMock(return_value="Formatted content")
        
        # Format MoM data
        result = self.formatter.format_with_format_type(
            self.mom_data, "text", template_manager
        )
        
        # Verify get_templates was called with correct parameters
        template_manager.get_templates.assert_called_once_with("text")
        
        # Verify get_template was called with correct parameters
        template_manager.get_template.assert_called_once_with(self.template.name, "en")
        
        # Verify format was called with correct parameters
        self.formatter.format.assert_called_once_with(self.mom_data, self.template, branding=[])
        
        # Verify result
        assert result == "Formatted content"
    
    def test_format_with_format_type_not_found(self):
        """Test formatting MoM data when no template of the specified format type is found."""
        # Mock template manager
        template_manager = MagicMock()
        template_manager.get_templates.return_value = []
        
        # Format MoM data
        with pytest.raises(ValueError) as excinfo:
            self.formatter.format_with_format_type(
                self.mom_data, "nonexistent", template_manager
            )
        
        # Verify error message
        assert "No template found for format type: nonexistent" in str(excinfo.value)
    
    def test_register_formatter(self):
        """Test registering a formatter."""
        # Create mock formatter
        mock_formatter = MagicMock()
        
        # Register formatter
        self.formatter.register_formatter("test", mock_formatter)
        
        # Verify formatter was registered
        assert "test" in self.formatter.formatters
        assert self.formatter.formatters["test"] == mock_formatter
    
    def test_get_formatter(self):
        """Test getting a formatter."""
        # Create mock formatter
        mock_formatter = MagicMock()
        
        # Register formatter
        self.formatter.register_formatter("test", mock_formatter)
        
        # Get formatter
        formatter = self.formatter.get_formatter("test")
        
        # Verify formatter
        assert formatter == mock_formatter
        
        # Get nonexistent formatter
        formatter = self.formatter.get_formatter("nonexistent")
        
        # Verify result is None
        assert formatter is None
    
    def test_format_with_formatter(self):
        """Test formatting MoM data using a registered formatter."""
        # Create mock formatter
        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Formatted content"
        
        # Register formatter
        self.formatter.register_formatter("test", mock_formatter)
        
        # Format MoM data
        result = self.formatter.format_with_formatter(self.mom_data, "test")
        
        # Verify formatter.format was called with correct parameters
        mock_formatter.format.assert_called_once_with(self.mom_data)
        
        # Verify result
        assert result == "Formatted content"
    
    def test_format_with_formatter_not_found(self):
        """Test formatting MoM data when no formatter is registered for the specified format type."""
        # Format MoM data
        with pytest.raises(ValueError) as excinfo:
            self.formatter.format_with_formatter(self.mom_data, "nonexistent")
        
        # Verify error message
        assert "No formatter registered for format type: nonexistent" in str(excinfo.value)
    
    def test_format_analytics(self):
        """Test formatting analytics for inclusion in MoM output."""
        # Mock analytics formatter
        self.formatter.analytics_formatter = MagicMock()
        self.formatter.analytics_formatter.format_analytics.return_value = "Formatted analytics"
        
        # Format analytics
        analytics = {"test": "analytics"}
        result = self.formatter._format_analytics(analytics, "text")
        
        # Verify analytics_formatter.format_analytics was called with correct parameters
        self.formatter.analytics_formatter.format_analytics.assert_called_once_with(analytics, "text")
        
        # Verify result
        assert result == "Formatted analytics"
    
    def test_append_analytics_text(self):
        """Test appending analytics content to MoM content in text format."""
        # Append analytics
        content = "MoM content"
        analytics_content = "Analytics content"
        result = self.formatter._append_analytics(content, analytics_content, "text")
        
        # Verify result
        assert result.startswith("MoM content")
        assert result.endswith("Analytics content")
        assert "=" * 30 in result
    
    def test_append_analytics_html(self):
        """Test appending analytics content to MoM content in HTML format."""
        # Append analytics to HTML with body tag
        content = "<html><body>MoM content</body></html>"
        analytics_content = "<div>Analytics content</div>"
        result = self.formatter._append_analytics(content, analytics_content, "html")
        
        # Verify result
        assert result.startswith("<html><body>MoM content")
        assert result.endswith("</body></html>")
        assert "<div>Analytics content</div>" in result
        
        # Append analytics to HTML without body tag
        content = "<html>MoM content</html>"
        result = self.formatter._append_analytics(content, analytics_content, "html")
        
        # Verify result
        assert result.startswith("<html>MoM content</html>")
        assert result.endswith("<div>Analytics content</div>")
    
    @patch('app.formatter.analytics_formatter.AnalyticsFormatter.create_visualization_data')
    def test_create_visualization(self, mock_create_visualization_data):
        """Test creating visualization data for analytics."""
        # Mock create_visualization_data method
        mock_create_visualization_data.return_value = {
            "speaking_time": {"labels": ["John", "Jane"], "values": [60, 40]},
            "topics": {"labels": ["Topic 1", "Topic 2"], "values": [70, 30]}
        }
        
        # Create visualization data
        analytics = {"test": "analytics"}
        result = self.formatter.create_visualization(analytics, "speaking_time")
        
        # Verify create_visualization_data was called with correct parameters
        mock_create_visualization_data.assert_called_once_with(analytics)
        
        # Verify result
        assert result == {"labels": ["John", "Jane"], "values": [60, 40]}
        
        # Test with unsupported visualization type
        result = self.formatter.create_visualization(analytics, "unsupported")
        
        # Verify result is empty dictionary
        assert result == {}
    
    @patch('app.formatter.mom_formatter.MoMFormatter.format')
    def test_format_with_analytics_method(self, mock_format):
        """Test formatting MoM data with analytics using the format_with_analytics method."""
        # Mock format method
        mock_format.return_value = "Formatted content with analytics"
        
        # Format MoM data with analytics
        mom_data = {"meeting_title": "Test Meeting"}
        analytics = {"test": "analytics"}
        template = MagicMock()
        template.format_type = "text"
        
        result = self.formatter.format_with_analytics(mom_data, analytics, template, "text")
        
        # Verify format was called with correct parameters
        expected_mom_data = {"meeting_title": "Test Meeting", "analytics": analytics}
        mock_format.assert_called_once_with(expected_mom_data, template, include_analytics=True)
        
        # Verify result
        assert result == "Formatted content with analytics"