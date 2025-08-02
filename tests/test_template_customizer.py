"""
Unit tests for the TemplateCustomizer class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.template.template_customizer import TemplateCustomizer
from app.template.template_model import Template, BrandingElement

class TestTemplateCustomizer:
    """Test cases for TemplateCustomizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.customizer = TemplateCustomizer()
        
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

{if notes}
Notes:
{notes}
{endif}

Key Discussion Points:
{discussion_points}

Action Items:
{action_items}

Decisions Made:
{decisions}

Next Steps:
{next_steps}

Logo: {branding.logo}
            """.strip(),
            sections=["meeting_title", "date_time", "attendees", "agenda", 
                     "discussion_points", "action_items", "decisions", "next_steps"],
            branding=[
                BrandingElement(name="logo", type="image", value="default-logo.png", description="Default logo")
            ]
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
        customizer = TemplateCustomizer()
        assert customizer.config == {}
        
        # Custom config
        custom_config = {"format": "custom"}
        customizer = TemplateCustomizer(config=custom_config)
        assert customizer.config == custom_config
    
    def test_apply(self):
        """Test applying a template to MoM data."""
        # Apply template
        result = self.customizer.apply(self.template, self.mom_data)
        
        # Verify result
        assert "Meeting Title: Test Meeting" in result
        assert "Date & Time: 2023-01-01 10:00" in result
        assert "John Doe" in result
        assert "Jane Smith" in result
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Discussion 1" in result
        assert "Discussion 2" in result
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Decision 1" in result
        assert "Decision 2" in result
        assert "Step 1" in result
        assert "Step 2" in result
        assert "Logo: default-logo.png" in result
        
        # Verify optional section is not included (no 'notes' in mom_data)
        assert "Notes:" not in result
    
    def test_apply_with_optional_section(self):
        """Test applying a template with optional section."""
        # Add notes to MoM data
        mom_data_with_notes = self.mom_data.copy()
        mom_data_with_notes["notes"] = ["Note 1", "Note 2"]
        
        # Apply template
        result = self.customizer.apply(self.template, mom_data_with_notes)
        
        # Verify optional section is included
        assert "Notes:" in result
        assert "Note 1" in result
        assert "Note 2" in result
    
    def test_apply_with_custom_sections(self):
        """Test applying a template with custom sections."""
        # Apply template with custom sections
        result = self.customizer.apply(
            self.template, 
            self.mom_data, 
            sections=["meeting_title", "date_time", "attendees"]
        )
        
        # Verify included sections
        assert "Meeting Title: Test Meeting" in result
        assert "Date & Time: 2023-01-01 10:00" in result
        assert "John Doe" in result
        assert "Jane Smith" in result
        
        # Verify excluded sections are empty
        assert "Agenda:\n" in result
        assert "Key Discussion Points:\n" in result
        assert "Action Items:\n" in result
        assert "Decisions Made:\n" in result
        assert "Next Steps:\n" in result
    
    def test_apply_with_custom_branding(self):
        """Test applying a template with custom branding."""
        # Create custom branding
        custom_branding = [
            BrandingElement(name="logo", type="image", value="custom-logo.png", description="Custom logo")
        ]
        
        # Apply template with custom branding
        result = self.customizer.apply(
            self.template, 
            self.mom_data, 
            branding=custom_branding
        )
        
        # Verify custom branding is applied
        assert "Logo: custom-logo.png" in result
    
    def test_apply_with_template_name(self):
        """Test applying a template by name."""
        # Mock template manager
        template_manager = MagicMock()
        template_manager.get_template.return_value = self.template
        
        # Apply template by name
        result = self.customizer.apply_with_template_name(
            "Test Template", 
            self.mom_data, 
            template_manager
        )
        
        # Verify template manager was called
        template_manager.get_template.assert_called_once_with("Test Template", "en")
        
        # Verify result
        assert "Meeting Title: Test Meeting" in result
    
    def test_apply_with_template_name_not_found(self):
        """Test applying a template by name when template is not found."""
        # Mock template manager
        template_manager = MagicMock()
        template_manager.get_template.return_value = None
        
        # Apply template by name
        with pytest.raises(ValueError) as excinfo:
            self.customizer.apply_with_template_name(
                "Nonexistent Template", 
                self.mom_data, 
                template_manager
            )
        
        # Verify error message
        assert "Template 'Nonexistent Template' not found" in str(excinfo.value)
    
    def test_format_section_string(self):
        """Test formatting a string section."""
        result = self.customizer._format_section("Test section")
        assert result == "Test section"
    
    def test_format_section_list_of_strings(self):
        """Test formatting a list of strings section."""
        result = self.customizer._format_section(["Item 1", "Item 2"])
        assert result == "Item 1\nItem 2"
    
    def test_format_section_list_of_dicts(self):
        """Test formatting a list of dictionaries section."""
        data = [
            {"task": "Task 1", "assignee": "John"},
            {"task": "Task 2", "assignee": "Jane"}
        ]
        result = self.customizer._format_section(data)
        assert "task: Task 1" in result
        assert "assignee: John" in result
        assert "task: Task 2" in result
        assert "assignee: Jane" in result
    
    def test_format_section_dict(self):
        """Test formatting a dictionary section."""
        data = {"key1": "value1", "key2": "value2"}
        result = self.customizer._format_section(data)
        assert "key1: value1" in result
        assert "key2: value2" in result
    
    def test_customize_template(self):
        """Test creating a customized copy of a template."""
        # Create custom sections and branding
        custom_sections = ["meeting_title", "date_time", "attendees"]
        custom_branding = [
            BrandingElement(name="logo", type="image", value="custom-logo.png", description="Custom logo")
        ]
        custom_metadata = {"custom_key": "custom_value"}
        
        # Customize template
        custom_template = self.customizer.customize_template(
            self.template,
            sections=custom_sections,
            branding=custom_branding,
            metadata=custom_metadata
        )
        
        # Verify custom template
        assert custom_template.name == "Custom Test Template"
        assert custom_template.description == "Customized version of Test Template"
        assert custom_template.format_type == self.template.format_type
        assert custom_template.content == self.template.content
        assert custom_template.sections == custom_sections
        assert custom_template.branding == custom_branding
        assert custom_template.metadata["custom_key"] == "custom_value"