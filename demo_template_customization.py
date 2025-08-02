#!/usr/bin/env python3
"""
Demo script for Template Customization functionality.

This script demonstrates the template customization features implemented
for the AI-powered MoM generator.
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.template.template_model import Template, BrandingElement, TemplateManager
from app.template.template_customizer import TemplateCustomizer
from app.template.branding_manager import BrandingManager
from app.formatter.mom_formatter import MoMFormatter

def main():
    """Demonstrate template customization functionality."""
    print("=== AI-Powered MoM Generator - Template Customization Demo ===\n")
    
    # Sample MoM data
    mom_data = {
        "meeting_title": "Weekly Team Standup",
        "date_time": "2023-12-15 10:00 AM",
        "attendees": [
            "John Doe (Product Manager)",
            "Jane Smith (Developer)",
            "Bob Johnson (Designer)",
            "Alice Brown (QA Engineer)"
        ],
        "agenda": [
            "Sprint progress review",
            "Blockers and challenges",
            "Next week planning"
        ],
        "discussion_points": [
            "Frontend development is 80% complete",
            "API integration facing some delays",
            "Design mockups approved by stakeholders",
            "Testing environment setup completed"
        ],
        "action_items": [
            {
                "task": "Fix API integration issues",
                "assignee": "Jane Smith",
                "due": "2023-12-18"
            },
            {
                "task": "Complete frontend testing",
                "assignee": "Alice Brown", 
                "due": "2023-12-20"
            }
        ],
        "decisions": [
            "Move sprint deadline by 2 days",
            "Add extra QA resource for next sprint"
        ],
        "next_steps": [
            "Schedule follow-up meeting for Monday",
            "Update project timeline",
            "Communicate changes to stakeholders"
        ]
    }
    
    # Initialize components
    print("1. Initializing Template Manager...")
    template_manager = TemplateManager()
    template_manager.create_default_templates()
    
    print("2. Initializing Template Customizer...")
    customizer = TemplateCustomizer()
    
    print("3. Initializing Branding Manager...")
    branding_manager = BrandingManager()
    branding_manager.create_default_branding_sets()
    
    print("4. Initializing MoM Formatter...")
    formatter = MoMFormatter()
    
    print("\n=== Available Templates ===")
    templates = template_manager.get_templates()
    for template in templates:
        print(f"- {template.name} ({template.format_type}): {template.description}")
    
    print("\n=== Available Branding Sets ===")
    branding_sets = branding_manager.get_branding_sets()
    for name, elements in branding_sets.items():
        print(f"- {name}: {len(elements)} elements")
    
    # Demonstrate basic template application
    print("\n=== Demo 1: Basic Template Application ===")
    available_templates = template_manager.get_templates()
    if available_templates:
        # Use the first available template
        template = available_templates[0]
        result = customizer.apply(template, mom_data)
        print(f"Generated MoM using '{template.name}' template (first 500 characters):")
        print(result[:500] + "..." if len(result) > 500 else result)
    
    # Demonstrate custom sections
    print("\n=== Demo 2: Custom Sections ===")
    custom_sections = ["meeting_title", "date_time", "attendees", "action_items"]
    if available_templates:
        template = available_templates[0]
        result = customizer.apply(template, mom_data, sections=custom_sections)
        print("Generated MoM with custom sections (first 300 characters):")
        print(result[:300] + "..." if len(result) > 300 else result)
    
    # Demonstrate branding application
    print("\n=== Demo 3: Branding Application ===")
    html_templates = [t for t in available_templates if t.format_type == "html"]
    corporate_branding = branding_manager.get_branding_set("Corporate")
    
    if html_templates and corporate_branding:
        html_template = html_templates[0]
        result = customizer.apply(html_template, mom_data, branding=corporate_branding)
        print(f"Generated HTML MoM using '{html_template.name}' with corporate branding (first 500 characters):")
        print(result[:500] + "..." if len(result) > 500 else result)
    
    # Demonstrate MoM Formatter integration
    print("\n=== Demo 4: MoM Formatter Integration ===")
    try:
        # Use one of the available templates
        available_templates = template_manager.get_templates()
        if available_templates:
            template_name = available_templates[0].name
            result = formatter.format_with_template_name(
                mom_data, 
                template_name, 
                template_manager,
                language="en"
            )
            print(f"Generated MoM using MoM Formatter with '{template_name}' template (first 400 characters):")
            print(result[:400] + "..." if len(result) > 400 else result)
        else:
            print("No templates available")
    except Exception as e:
        print(f"Error with MoM Formatter: {e}")
    
    # Demonstrate custom template creation
    print("\n=== Demo 5: Custom Template Creation ===")
    custom_template = Template(
        name="Brief Summary",
        description="Brief meeting summary template",
        format_type="text",
        content="""
MEETING SUMMARY

Title: {meeting_title}
Date: {date_time}

Attendees: {attendees}

Key Decisions:
{decisions}

Action Items:
{action_items}

Next Meeting: TBD
        """.strip(),
        sections=["meeting_title", "date_time", "attendees", "decisions", "action_items"]
    )
    
    result = customizer.apply(custom_template, mom_data)
    print("Generated MoM using custom template:")
    print(result)
    
    print("\n=== Demo Complete ===")
    print("Template customization functionality is working correctly!")

if __name__ == "__main__":
    main()