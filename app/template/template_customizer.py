"""
Template customizer module for AI-powered MoM generator.

This module provides functionality for customizing templates.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Set, Union
from .template_model import Template, BrandingElement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateCustomizer:
    """
    Customizes templates for MoM formatting.
    
    This class provides methods for customizing templates, including
    section inclusion/exclusion, branding application, and content formatting.
    
    Attributes:
        config (Dict): Configuration options for the customizer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TemplateCustomizer with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the customizer
        """
        self.config = config or {}
        logger.info("TemplateCustomizer initialized")
    
    def apply(self, template: Template, mom_data: Dict[str, Any], 
              sections: Optional[List[str]] = None, 
              branding: Optional[List[BrandingElement]] = None) -> str:
        """
        Apply a template to MoM data.
        
        Args:
            template (Template): Template to apply
            mom_data (Dict[str, Any]): MoM data to format
            sections (List[str], optional): List of sections to include. If None, all sections are included.
            branding (List[BrandingElement], optional): List of branding elements to apply.
            
        Returns:
            str: Formatted MoM content
        """
        # Get template content
        content = template.content
        
        # Apply branding if provided
        if branding:
            content = self._apply_branding(content, branding)
        elif template.branding:
            content = self._apply_branding(content, template.branding)
        
        # Determine which sections to include
        included_sections = sections or template.sections
        
        # Format content with MoM data
        formatted_content = self._format_content(content, mom_data, included_sections)
        
        return formatted_content
    
    def apply_with_template_name(self, template_name: str, mom_data: Dict[str, Any], 
                                template_manager: Any, language: str = "en",
                                sections: Optional[List[str]] = None, 
                                branding: Optional[List[BrandingElement]] = None) -> str:
        """
        Apply a template by name to MoM data.
        
        Args:
            template_name (str): Name of the template to apply
            mom_data (Dict[str, Any]): MoM data to format
            template_manager (Any): Template manager instance
            language (str, optional): Language code. Defaults to "en".
            sections (List[str], optional): List of sections to include. If None, all sections are included.
            branding (List[BrandingElement], optional): List of branding elements to apply.
            
        Returns:
            str: Formatted MoM content
            
        Raises:
            ValueError: If the template is not found
        """
        # Get template
        template = template_manager.get_template(template_name, language)
        
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Apply template
        return self.apply(template, mom_data, sections, branding)
    
    def _apply_branding(self, content: str, branding: List[BrandingElement]) -> str:
        """
        Apply branding elements to template content.
        
        Args:
            content (str): Template content
            branding (List[BrandingElement]): List of branding elements to apply
            
        Returns:
            str: Template content with branding applied
        """
        branded_content = content
        
        # Create a dictionary of branding elements by name
        branding_dict = {element.name: element for element in branding}
        
        # Replace branding placeholders in content
        for name, element in branding_dict.items():
            # Basic placeholder replacement
            placeholder = f"{{branding.{name}}}"
            if placeholder in branded_content:
                branded_content = branded_content.replace(placeholder, element.value)
            
            # Advanced placeholder replacement with attributes
            placeholder_pattern = f"{{branding.{name}.(.*?)}}"
            matches = re.finditer(placeholder_pattern, branded_content)
            
            for match in matches:
                attr_name = match.group(1)
                attr_value = ""
                
                # Get attribute value based on name
                if attr_name == "value":
                    attr_value = element.value
                elif attr_name == "type":
                    attr_value = element.type
                elif attr_name == "position":
                    attr_value = element.position
                elif attr_name == "size":
                    attr_value = element.size
                elif attr_name == "css_class":
                    attr_value = element.css_class
                elif attr_name in element.html_attributes:
                    attr_value = element.html_attributes[attr_name]
                elif attr_name in element.format_specific:
                    attr_value = element.format_specific[attr_name]
                
                # Replace placeholder with attribute value
                branded_content = branded_content.replace(match.group(0), attr_value)
        
        # Process special branding elements
        branded_content = self._process_special_branding_elements(branded_content, branding)
        
        return branded_content
    
    def _process_special_branding_elements(self, content: str, branding: List[BrandingElement]) -> str:
        """
        Process special branding elements like logos, headers, and footers.
        
        Args:
            content (str): Template content
            branding (List[BrandingElement]): List of branding elements to apply
            
        Returns:
            str: Template content with special branding elements applied
        """
        processed_content = content
        
        # Check for HTML content
        is_html = "<html" in content.lower()
        is_markdown = "# " in content or "## " in content
        
        # Process logo
        logo_elements = [e for e in branding if e.type.lower() == "logo"]
        if logo_elements and is_html:
            logo = logo_elements[0]
            logo_html = self._create_logo_html(logo)
            
            # Insert logo in header
            if "<header" in processed_content:
                processed_content = re.sub(
                    r"(<header[^>]*>)",
                    f"\\1\n{logo_html}",
                    processed_content
                )
            # Or at the beginning of body
            elif "<body" in processed_content:
                processed_content = re.sub(
                    r"(<body[^>]*>)",
                    f"\\1\n<div class=\"logo-container\">{logo_html}</div>",
                    processed_content
                )
        
        # Process header
        header_elements = [e for e in branding if e.type.lower() == "header"]
        if header_elements:
            header = header_elements[0]
            
            if is_html:
                header_html = self._create_header_html(header)
                # Insert custom header
                if "<header" in processed_content:
                    processed_content = re.sub(
                        r"<header[^>]*>.*?</header>",
                        header_html,
                        processed_content,
                        flags=re.DOTALL
                    )
                # Or at the beginning of body
                elif "<body" in processed_content:
                    processed_content = re.sub(
                        r"(<body[^>]*>)",
                        f"\\1\n{header_html}",
                        processed_content
                    )
            elif is_markdown:
                # For markdown, replace the first heading
                header_md = f"# {header.value}\n\n"
                processed_content = re.sub(r"^#\s+.*?\n", header_md, processed_content)
        
        # Process footer
        footer_elements = [e for e in branding if e.type.lower() == "footer"]
        if footer_elements:
            footer = footer_elements[0]
            
            if is_html:
                footer_html = self._create_footer_html(footer)
                # Replace existing footer
                if "<footer" in processed_content:
                    processed_content = re.sub(
                        r"<footer[^>]*>.*?</footer>",
                        footer_html,
                        processed_content,
                        flags=re.DOTALL
                    )
                # Or add at the end of body
                elif "</body>" in processed_content:
                    processed_content = processed_content.replace(
                        "</body>",
                        f"{footer_html}\n</body>"
                    )
            elif is_markdown:
                # For markdown, add footer at the end
                footer_md = f"\n\n---\n\n{footer.value}\n"
                processed_content += footer_md
        
        # Process color scheme
        color_elements = [e for e in branding if e.type.lower() == "color" or e.type.lower() == "color_scheme"]
        if color_elements and is_html:
            # Extract primary, secondary, and accent colors
            colors = {}
            for color in color_elements:
                if "." in color.name:
                    color_type = color.name.split(".")[-1]
                    colors[color_type] = color.value
                else:
                    colors["primary"] = color.value
            
            # Create CSS for colors
            css = self._create_color_css(colors)
            
            # Insert CSS in head
            if "<head" in processed_content:
                processed_content = re.sub(
                    r"(</head>)",
                    f"{css}\n\\1",
                    processed_content
                )
        
        # Process font
        font_elements = [e for e in branding if e.type.lower() == "font"]
        if font_elements and is_html:
            font = font_elements[0]
            font_css = self._create_font_css(font)
            
            # Insert CSS in head
            if "<head" in processed_content:
                processed_content = re.sub(
                    r"(</head>)",
                    f"{font_css}\n\\1",
                    processed_content
                )
        
        return processed_content
    
    def _create_logo_html(self, logo: BrandingElement) -> str:
        """
        Create HTML for logo.
        
        Args:
            logo (BrandingElement): Logo branding element
            
        Returns:
            str: HTML for logo
        """
        position = logo.position or "left"
        size = logo.size or "medium"
        css_class = logo.css_class or "logo"
        
        # Determine size in pixels
        size_px = "100px"  # Default medium size
        if size == "small":
            size_px = "50px"
        elif size == "large":
            size_px = "150px"
        
        # Create style based on position
        style = f"max-height: {size_px}; max-width: 100%;"
        container_style = ""
        
        if position == "left":
            container_style = "text-align: left;"
        elif position == "right":
            container_style = "text-align: right;"
        elif position == "center":
            container_style = "text-align: center;"
        
        # Create HTML attributes string
        html_attrs = ""
        for attr, value in logo.html_attributes.items():
            html_attrs += f' {attr}="{value}"'
        
        return f'<div class="logo-container" style="{container_style}"><img src="{logo.value}" alt="Logo" class="{css_class}" style="{style}"{html_attrs}></div>'
    
    def _create_header_html(self, header: BrandingElement) -> str:
        """
        Create HTML for header.
        
        Args:
            header (BrandingElement): Header branding element
            
        Returns:
            str: HTML for header
        """
        css_class = header.css_class or "custom-header"
        
        # Create HTML attributes string
        html_attrs = ""
        for attr, value in header.html_attributes.items():
            html_attrs += f' {attr}="{value}"'
        
        return f'<header class="{css_class}"{html_attrs}>{header.value}</header>'
    
    def _create_footer_html(self, footer: BrandingElement) -> str:
        """
        Create HTML for footer.
        
        Args:
            footer (BrandingElement): Footer branding element
            
        Returns:
            str: HTML for footer
        """
        css_class = footer.css_class or "custom-footer"
        
        # Create HTML attributes string
        html_attrs = ""
        for attr, value in footer.html_attributes.items():
            html_attrs += f' {attr}="{value}"'
        
        return f'<footer class="{css_class}"{html_attrs}>{footer.value}</footer>'
    
    def _create_color_css(self, colors: Dict[str, str]) -> str:
        """
        Create CSS for colors.
        
        Args:
            colors (Dict[str, str]): Dictionary of color types and values
            
        Returns:
            str: CSS for colors
        """
        css = "<style>\n:root {\n"
        
        if "primary" in colors:
            css += f"  --primary-color: {colors['primary']};\n"
        if "secondary" in colors:
            css += f"  --secondary-color: {colors['secondary']};\n"
        if "accent" in colors:
            css += f"  --accent-color: {colors['accent']};\n"
        if "background" in colors:
            css += f"  --background-color: {colors['background']};\n"
        if "text" in colors:
            css += f"  --text-color: {colors['text']};\n"
        
        css += "}\n\n"
        
        # Apply colors to elements
        if "primary" in colors:
            css += "h1, h2, h3 { color: var(--primary-color); }\n"
        if "background" in colors:
            css += "body { background-color: var(--background-color); }\n"
        if "text" in colors:
            css += "body { color: var(--text-color); }\n"
        
        css += "</style>"
        return css
    
    def _create_font_css(self, font: BrandingElement) -> str:
        """
        Create CSS for font.
        
        Args:
            font (BrandingElement): Font branding element
            
        Returns:
            str: CSS for font
        """
        font_family = font.value
        
        css = "<style>\n"
        css += f"body, html {{ font-family: {font_family}, sans-serif; }}\n"
        css += "</style>"
        
        return css
    
    def _format_content(self, content: str, mom_data: Dict[str, Any], included_sections: List[str]) -> str:
        """
        Format template content with MoM data.
        
        Args:
            content (str): Template content
            mom_data (Dict[str, Any]): MoM data to format
            included_sections (List[str]): List of sections to include
            
        Returns:
            str: Formatted content
        """
        formatted_content = content
        
        # Handle the special {{content}} placeholder
        if "{{content}}" in formatted_content:
            # Generate a formatted representation of the entire MoM data
            full_content = self._generate_full_content(mom_data)
            formatted_content = formatted_content.replace("{{content}}", full_content)
        
        # Format included sections
        for section in included_sections:
            if section in mom_data:
                placeholder = f"{{{section}}}"
                section_content = self._format_section(mom_data[section])
                formatted_content = formatted_content.replace(placeholder, section_content)
            else:
                # If section is not in mom_data, replace with empty string
                placeholder = f"{{{section}}}"
                formatted_content = formatted_content.replace(placeholder, "")
        
        # Find and remove optional sections that are not included
        optional_pattern = r"\{if\s+(\w+)\}(.*?)\{endif\}"
        matches = re.finditer(optional_pattern, formatted_content, re.DOTALL)
        
        for match in matches:
            section_name = match.group(1)
            section_content = match.group(2)
            
            if section_name in mom_data and mom_data[section_name]:
                # Format the section content with the data
                formatted_section_content = section_content
                placeholder = f"{{{section_name}}}"
                if placeholder in formatted_section_content:
                    section_data = self._format_section(mom_data[section_name])
                    formatted_section_content = formatted_section_content.replace(placeholder, section_data)
                
                # Replace the conditional with its formatted content
                formatted_content = formatted_content.replace(match.group(0), formatted_section_content)
            else:
                # Remove the conditional and its content
                formatted_content = formatted_content.replace(match.group(0), "")
        
        return formatted_content
        
    def _generate_full_content(self, mom_data: Dict[str, Any]) -> str:
        """
        Generate a complete formatted representation of the MoM data.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            
        Returns:
            str: Formatted content
        """
        sections = []
        
        # Title
        if 'meeting_title' in mom_data:
            title = mom_data['meeting_title']
            # Clean up any placeholder text
            if title.startswith("**") or "[" in title:
                title = "Client Meeting"
            sections.append(f"MINUTES OF MEETING: {title}")
        else:
            sections.append("MINUTES OF MEETING: Client Meeting")
        
        # Date and time - don't use placeholder values
        if 'date_time' in mom_data:
            date_time = mom_data['date_time']
            # Clean up any placeholder text
            if date_time.startswith("**") or "[" in date_time:
                from datetime import datetime
                date_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            sections.append(f"DATE & TIME: {date_time}")
        
        # Location
        if 'location' in mom_data:
            location = mom_data['location']
            # Clean up any placeholder text
            if location.startswith("**") or "[" in location:
                location = "Virtual Meeting"
            sections.append(f"LOCATION: {location}")
        
        # Attendees
        if 'attendees' in mom_data and mom_data['attendees']:
            sections.append("ATTENDEES:")
            if isinstance(mom_data['attendees'], list):
                for attendee in mom_data['attendees']:
                    if isinstance(attendee, dict):
                        name = attendee.get('name', '')
                        role = attendee.get('role', '')
                        if role:
                            sections.append(f"- {name} ({role})")
                        else:
                            sections.append(f"- {name}")
                    else:
                        sections.append(f"- {attendee}")
            else:
                sections.append(str(mom_data['attendees']))
        
        # Agenda
        if 'agenda' in mom_data and mom_data['agenda']:
            sections.append("AGENDA:")
            if isinstance(mom_data['agenda'], list):
                for item in mom_data['agenda']:
                    sections.append(f"- {item}")
            else:
                sections.append(str(mom_data['agenda']))
        
        # Discussion points
        if 'discussion_points' in mom_data and mom_data['discussion_points']:
            sections.append("DISCUSSION POINTS:")
            if isinstance(mom_data['discussion_points'], list):
                for point in mom_data['discussion_points']:
                    sections.append(f"- {point}")
            else:
                sections.append(str(mom_data['discussion_points']))
        
        # Action items
        if 'action_items' in mom_data and mom_data['action_items']:
            sections.append("ACTION ITEMS:")
            if isinstance(mom_data['action_items'], list):
                for item in mom_data['action_items']:
                    if isinstance(item, dict):
                        desc = item.get('description', '')
                        assignee = item.get('assignee', '')
                        deadline = item.get('deadline', '')
                        if assignee and deadline:
                            sections.append(f"- {desc} (Assigned to: {assignee}, Due: {deadline})")
                        elif assignee:
                            sections.append(f"- {desc} (Assigned to: {assignee})")
                        else:
                            sections.append(f"- {desc}")
                    else:
                        sections.append(f"- {item}")
            else:
                sections.append(str(mom_data['action_items']))
        
        # Decisions
        if 'decisions' in mom_data and mom_data['decisions']:
            sections.append("DECISIONS:")
            if isinstance(mom_data['decisions'], list):
                for decision in mom_data['decisions']:
                    if isinstance(decision, dict):
                        sections.append(f"- {decision.get('decision', '')}")
                    else:
                        sections.append(f"- {decision}")
            else:
                sections.append(str(mom_data['decisions']))
        
        # Next steps
        if 'next_steps' in mom_data and mom_data['next_steps']:
            sections.append("NEXT STEPS:")
            if isinstance(mom_data['next_steps'], list):
                for step in mom_data['next_steps']:
                    sections.append(f"- {step}")
            else:
                sections.append(str(mom_data['next_steps']))
        
        # Join all sections with double newlines
        return "\n\n".join(sections)
    
    def _format_section(self, section_data: Any) -> str:
        """
        Format a section of MoM data.
        
        Args:
            section_data (Any): Section data to format
            
        Returns:
            str: Formatted section content
        """
        if isinstance(section_data, str):
            return section_data
        elif isinstance(section_data, list):
            if all(isinstance(item, str) for item in section_data):
                return "\n".join(section_data)
            else:
                # Format list of dictionaries or complex objects
                return "\n".join(self._format_complex_item(item) for item in section_data)
        elif isinstance(section_data, dict):
            return self._format_complex_item(section_data)
        else:
            return str(section_data)
    
    def _format_complex_item(self, item: Any) -> str:
        """
        Format a complex item (dictionary or object).
        
        Args:
            item (Any): Item to format
            
        Returns:
            str: Formatted item content
        """
        if isinstance(item, dict):
            # Format dictionary
            parts = []
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    parts.append(f"{key}:\n{self._format_section(value)}")
                else:
                    parts.append(f"{key}: {value}")
            return "\n".join(parts)
        else:
            # Format other object types
            return str(item)
    
    def customize_template(self, template: Template, 
                          sections: Optional[List[str]] = None, 
                          branding: Optional[List[BrandingElement]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Template:
        """
        Create a customized copy of a template.
        
        Args:
            template (Template): Template to customize
            sections (List[str], optional): List of sections to include. If None, all sections are included.
            branding (List[BrandingElement], optional): List of branding elements to apply.
            metadata (Dict[str, Any], optional): Additional metadata for the template.
            
        Returns:
            Template: Customized template
        """
        # Create a new template with customized attributes
        custom_template = Template(
            name=f"Custom {template.name}",
            description=f"Customized version of {template.name}",
            format_type=template.format_type,
            content=template.content,
            sections=sections or template.sections,
            branding=branding or template.branding,
            metadata={**(template.metadata or {}), **(metadata or {})},
            language=template.language,
            translations=template.translations
        )
        
        return custom_template