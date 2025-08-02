"""
MoM formatter module for AI-powered MoM generator.

This module provides functionality for formatting MoM data.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from app.template.template_model import Template, BrandingElement
from app.template.template_customizer import TemplateCustomizer
from app.formatter.analytics_formatter import AnalyticsFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoMFormatter:
    """
    Formats MoM data using templates.
    
    This class provides methods for formatting MoM data using templates.
    
    Attributes:
        config (Dict): Configuration options for the formatter
        template_customizer (TemplateCustomizer): Template customizer instance
        formatters (Dict): Dictionary of formatters by format type
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MoMFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        self.config = config or {}
        self.template_customizer = TemplateCustomizer(self.config.get("template", {}))
        self.analytics_formatter = AnalyticsFormatter(self.config.get("analytics", {}))
        
        # Initialize template manager
        from app.template.template_model import TemplateManager
        templates_dir = self.config.get("templates_dir")
        self.template_manager = TemplateManager(templates_dir)
        
        # Create default templates if needed
        if self.config.get("create_default_templates", True):
            self.template_manager.create_default_templates()
        
        # Initialize branding elements
        self.default_branding = self._initialize_branding()
        
        self.formatters = {}
        self._initialize_formatters()
        logger.info("MoMFormatter initialized")
    
    def _initialize_formatters(self):
        """Initialize formatters for different output formats."""
        try:
            # Import formatters
            from .text_formatter import TextFormatter
            from .html_formatter import HtmlFormatter
            from .json_formatter import JsonFormatter
            from .pdf_formatter import PdfFormatter
            from .markdown_formatter import MarkdownFormatter
            from .email_formatter import EmailFormatter
            from .docx_formatter import DocxFormatter
            
            # Register formatters
            self.register_formatter('text', TextFormatter(self.config.get('text', {})))
            self.register_formatter('html', HtmlFormatter(self.config.get('html', {})))
            self.register_formatter('json', JsonFormatter(self.config.get('json', {})))
            self.register_formatter('pdf', PdfFormatter(self.config.get('pdf', {})))
            self.register_formatter('markdown', MarkdownFormatter(self.config.get('markdown', {})))
            self.register_formatter('email', EmailFormatter(self.config.get('email', {})))
            self.register_formatter('docx', DocxFormatter(self.config.get('docx', {})))
            
            logger.info(f"Initialized formatters for output formats: {', '.join(self.formatters.keys())}")
        
        except ImportError as e:
            logger.warning(f"Could not initialize all formatters: {e}")
            # Initialize with basic formatters that don't have external dependencies
            try:
                from .text_formatter import TextFormatter
                from .json_formatter import JsonFormatter
                
                self.register_formatter('text', TextFormatter(self.config.get('text', {})))
                self.register_formatter('json', JsonFormatter(self.config.get('json', {})))
                
                logger.info("Initialized basic formatters only")
            except ImportError:
                logger.warning("Could not initialize any formatters")
    
    def format(self, mom_data: Dict[str, Any], template: Template, 
              sections: Optional[List[str]] = None, 
              branding: Optional[List[BrandingElement]] = None,
              include_analytics: bool = False) -> str:
        """
        Format MoM data using a template.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            template (Template): Template to use for formatting
            sections (List[str], optional): List of sections to include. If None, all sections are included.
            branding (List[BrandingElement], optional): List of branding elements to apply.
            include_analytics (bool, optional): Whether to include analytics in the output. Defaults to False.
            
        Returns:
            str: Formatted MoM content
        """
        # Format MoM content using template
        formatted_content = self.template_customizer.apply(template, mom_data, sections, branding)
        
        # Add analytics if requested
        if include_analytics and "analytics" in mom_data:
            analytics_content = self._format_analytics(mom_data["analytics"], template.format_type)
            formatted_content = self._append_analytics(formatted_content, analytics_content, template.format_type)
        
        return formatted_content
    
    def format_with_template_name(self, mom_data: Dict[str, Any], template_name: str, 
                                 template_manager: Any, language: str = "en",
                                 sections: Optional[List[str]] = None, 
                                 branding: Optional[List[BrandingElement]] = None) -> str:
        """
        Format MoM data using a template by name.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            template_name (str): Name of the template to use
            template_manager (Any): Template manager instance
            language (str, optional): Language code. Defaults to "en".
            sections (List[str], optional): List of sections to include. If None, all sections are included.
            branding (List[BrandingElement], optional): List of branding elements to apply.
            
        Returns:
            str: Formatted MoM content
            
        Raises:
            ValueError: If the template is not found
        """
        return self.template_customizer.apply_with_template_name(
            template_name, mom_data, template_manager, language, sections, branding
        )
    
    def _initialize_branding(self) -> List[BrandingElement]:
        """
        Initialize default branding elements from configuration.
        
        Returns:
            List[BrandingElement]: List of default branding elements
        """
        branding_elements = []
        
        # Get branding configuration
        branding_config = self.config.get("branding", {})
        
        # Create branding elements from configuration
        if "logo" in branding_config:
            logo_config = branding_config["logo"]
            if isinstance(logo_config, str):
                # Simple logo path
                branding_elements.append(
                    BrandingElement(
                        name="logo",
                        type="logo",
                        value=logo_config,
                        position="left",
                        size="medium"
                    )
                )
            elif isinstance(logo_config, dict):
                # Detailed logo configuration
                branding_elements.append(
                    BrandingElement(
                        name="logo",
                        type="logo",
                        value=logo_config.get("path", ""),
                        position=logo_config.get("position", "left"),
                        size=logo_config.get("size", "medium"),
                        css_class=logo_config.get("css_class", "logo"),
                        html_attributes=logo_config.get("html_attributes", {})
                    )
                )
        
        # Add color scheme
        if "colors" in branding_config:
            colors = branding_config["colors"]
            for color_name, color_value in colors.items():
                branding_elements.append(
                    BrandingElement(
                        name=f"color.{color_name}",
                        type="color",
                        value=color_value
                    )
                )
        
        # Add font
        if "font" in branding_config:
            font_config = branding_config["font"]
            if isinstance(font_config, str):
                # Simple font name
                branding_elements.append(
                    BrandingElement(
                        name="font",
                        type="font",
                        value=font_config
                    )
                )
            elif isinstance(font_config, dict):
                # Detailed font configuration
                branding_elements.append(
                    BrandingElement(
                        name="font",
                        type="font",
                        value=font_config.get("family", ""),
                        format_specific=font_config.get("format_specific", {})
                    )
                )
        
        # Add header
        if "header" in branding_config:
            header_config = branding_config["header"]
            if isinstance(header_config, str):
                # Simple header content
                branding_elements.append(
                    BrandingElement(
                        name="header",
                        type="header",
                        value=header_config
                    )
                )
            elif isinstance(header_config, dict):
                # Detailed header configuration
                branding_elements.append(
                    BrandingElement(
                        name="header",
                        type="header",
                        value=header_config.get("content", ""),
                        css_class=header_config.get("css_class", "custom-header"),
                        html_attributes=header_config.get("html_attributes", {})
                    )
                )
        
        # Add footer
        if "footer" in branding_config:
            footer_config = branding_config["footer"]
            if isinstance(footer_config, str):
                # Simple footer content
                branding_elements.append(
                    BrandingElement(
                        name="footer",
                        type="footer",
                        value=footer_config
                    )
                )
            elif isinstance(footer_config, dict):
                # Detailed footer configuration
                branding_elements.append(
                    BrandingElement(
                        name="footer",
                        type="footer",
                        value=footer_config.get("content", ""),
                        css_class=footer_config.get("css_class", "custom-footer"),
                        html_attributes=footer_config.get("html_attributes", {})
                    )
                )
        
        return branding_elements
    
    def format_with_format_type(self, mom_data: Dict[str, Any], format_type: str, 
                               template_manager: Any = None, language: str = "en",
                               branding: Optional[List[BrandingElement]] = None) -> str:
        """
        Format MoM data using a template of a specific format type.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            format_type (str): Format type (text, html, markdown, etc.)
            template_manager (Any, optional): Template manager instance. If None, uses self.template_manager.
            language (str, optional): Language code. Defaults to "en".
            branding (List[BrandingElement], optional): List of branding elements to apply.
            
        Returns:
            str: Formatted MoM content
            
        Raises:
            ValueError: If no template of the specified format type is found
        """
        # Use provided template manager or default
        template_manager = template_manager or self.template_manager
        
        # Get templates of the specified format type
        templates = template_manager.get_templates(format_type)
        
        if not templates:
            raise ValueError(f"No template found for format type: {format_type}")
        
        # Use the first template of the specified format type
        template = template_manager.get_template(templates[0].name, language)
        
        # Use provided branding or default
        branding_to_apply = branding or self.default_branding
        
        return self.format(mom_data, template, branding=branding_to_apply)
    
    def register_formatter(self, format_type: str, formatter: Any) -> None:
        """
        Register a formatter for a specific format type.
        
        Args:
            format_type (str): Format type (text, html, markdown, etc.)
            formatter (Any): Formatter instance
        """
        self.formatters[format_type] = formatter
        logger.info(f"Registered formatter for format type: {format_type}")
    
    def get_formatter(self, format_type: str) -> Optional[Any]:
        """
        Get a formatter for a specific format type.
        
        Args:
            format_type (str): Format type (text, html, markdown, etc.)
            
        Returns:
            Optional[Any]: Formatter instance, or None if not found
        """
        return self.formatters.get(format_type)
    
    def format_with_formatter(self, mom_data: Dict[str, Any], format_type: str) -> Any:
        """
        Format MoM data using a registered formatter.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            format_type (str): Format type (text, html, markdown, etc.)
            
        Returns:
            Any: Formatted MoM content
            
        Raises:
            ValueError: If no formatter is registered for the specified format type
        """
        formatter = self.get_formatter(format_type)
        
        if not formatter:
            raise ValueError(f"No formatter registered for format type: {format_type}")
        
        return formatter.format(mom_data)
    
    def detect_format_type(self, file_path: str) -> str:
        """
        Detect the format type from a file path.
        
        Args:
            file_path (str): Path to the output file
            
        Returns:
            str: Format type (text, html, markdown, etc.)
            
        Raises:
            ValueError: If the file extension is not supported
        """
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().lstrip('.')
        
        # Map file extensions to format types
        format_map = {
            'txt': 'text',
            'html': 'html',
            'htm': 'html',
            'md': 'markdown',
            'json': 'json',
            'pdf': 'pdf',
            'docx': 'docx',
            'doc': 'docx',
            'eml': 'email'
        }
        
        # Get format type from extension
        format_type = format_map.get(ext)
        
        if not format_type:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return format_type
    
    def format_to_file(self, mom_data: Dict[str, Any], file_path: str, 
                     template_name: Optional[str] = None,
                     language: str = "en",
                     branding: Optional[List[BrandingElement]] = None) -> None:
        """
        Format MoM data and save to a file.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            file_path (str): Path to the output file
            template_name (str, optional): Name of the template to use. If None, a template will be selected based on format type.
            language (str, optional): Language code. Defaults to "en".
            branding (List[BrandingElement], optional): List of branding elements to apply.
            
        Raises:
            ValueError: If the file extension is not supported or if formatting fails
        """
        try:
            # Detect format type from file extension
            format_type = self.detect_format_type(file_path)
            
            # Use provided branding or default
            branding_to_apply = branding or self.default_branding
            
            # Format MoM data
            if template_name:
                # Use specified template
                output = self.format_with_template_name(
                    mom_data, template_name, self.template_manager, language, branding=branding_to_apply
                )
            else:
                # Use template based on format type
                output = self.format_with_format_type(
                    mom_data, format_type, self.template_manager, language, branding=branding_to_apply
                )
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save to file
            if isinstance(output, bytes):
                with open(file_path, 'wb') as f:
                    f.write(output)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output)
            
            logger.info(f"Saved formatted MoM to {file_path}")
        
        except Exception as e:
            error_msg = f"Error saving formatted MoM to {file_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _format_analytics(self, analytics: Dict[str, Any], format_type: str) -> str:
        """
        Format analytics for inclusion in MoM output.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            format_type (str): Output format type
            
        Returns:
            str: Formatted analytics content
        """
        return self.analytics_formatter.format_analytics(analytics, format_type)
    
    def _append_analytics(self, content: str, analytics_content: str, format_type: str) -> str:
        """
        Append analytics content to MoM content.
        
        Args:
            content (str): MoM content
            analytics_content (str): Formatted analytics content
            format_type (str): Output format type
            
        Returns:
            str: Combined content
        """
        if format_type == "html":
            # For HTML, insert analytics before the closing body tag
            if "</body>" in content:
                return content.replace("</body>", f"{analytics_content}</body>")
            else:
                return f"{content}\n{analytics_content}"
        else:
            # For other formats, simply append with a separator
            return f"{content}\n\n{'=' * 30}\n\n{analytics_content}"
    
    def format_with_analytics(self, mom_data: Dict[str, Any], analytics: Dict[str, Any], 
                             template: Template, format_type: str) -> str:
        """
        Format MoM data with analytics.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            analytics (Dict[str, Any]): Meeting analytics
            template (Template): Template to use for formatting
            format_type (str): Output format type
            
        Returns:
            str: Formatted MoM content with analytics
        """
        # Add analytics to MoM data
        mom_data_with_analytics = mom_data.copy()
        mom_data_with_analytics["analytics"] = analytics
        
        # Format with analytics included
        return self.format(mom_data_with_analytics, template, include_analytics=True)
    
    def create_visualization(self, analytics: Dict[str, Any], visualization_type: str) -> Dict[str, Any]:
        """
        Create visualization data for analytics.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            visualization_type (str): Type of visualization to create
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        # Get visualization data
        visualization_data = self.analytics_formatter.create_visualization_data(analytics)
        
        # Return data for the requested visualization type
        if visualization_type in visualization_data:
            return visualization_data[visualization_type]
        else:
            logger.warning(f"Unsupported visualization type: {visualization_type}")
            return {}
    
    def format_with_options(self, mom_data: Dict[str, Any], format_type: str, options: Dict[str, Any]) -> str:
        """
        Format MoM data with options.
        
        Args:
            mom_data (Dict[str, Any]): MoM data to format
            format_type (str): Format type (text, html, markdown, etc.)
            options (Dict[str, Any]): Formatting options
            
        Returns:
            str: Formatted MoM content
            
        Raises:
            ValueError: If the format type is not supported
        """
        # Get formatter for the specified format type
        formatter = self.get_formatter(format_type)
        
        if not formatter:
            raise ValueError(f"No formatter registered for format type: {format_type}")
        
        # Get template
        template_name = options.get('template')
        try:
            if template_name:
                template = self.template_manager.get_template(template_name)
            else:
                # Get default template for the format type
                templates = self.template_manager.get_templates(format_type)
                if not templates:
                    # Create a simple default template if none exists
                    from app.template.template_model import Template
                    template = Template(
                        name=f"Default {format_type.capitalize()} Template",
                        format_type=format_type,
                        content="{{content}}",
                        description=f"Default template for {format_type} format"
                    )
                else:
                    template = templates[0]
        except Exception as e:
            logger.warning(f"Error getting template: {e}. Using simple formatter.")
            # Use the formatter directly without a template
            return formatter.format(mom_data)
        
        # Get branding
        branding = self.default_branding
        
        # Get sections to include
        sections = None  # Include all sections by default
        
        # Check if analytics should be included
        include_analytics = options.get('include_analytics', False)
        
        # Format MoM data
        return self.format(mom_data, template, sections, branding, include_analytics)