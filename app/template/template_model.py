"""
Template model module for AI-powered MoM generator.

This module provides data models for template customization.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BrandingElement:
    """
    Represents a branding element for templates.
    
    Attributes:
        name (str): Name of the branding element
        type (str): Type of branding element (logo, color, font, header, footer, etc.)
        value (str): Value of the branding element (path, hex code, font name, etc.)
        description (str): Description of the branding element
        position (str): Position of the element (top, bottom, left, right, etc.)
        size (str): Size of the element (small, medium, large, etc.)
        css_class (str): CSS class for the element
        html_attributes (Dict[str, str]): Additional HTML attributes for the element
        format_specific (Dict[str, str]): Format-specific settings
    """
    name: str
    type: str
    value: str
    description: str = ""
    position: str = ""
    size: str = ""
    css_class: str = ""
    html_attributes: Dict[str, str] = field(default_factory=dict)
    format_specific: Dict[str, str] = field(default_factory=dict)


@dataclass
class Template:
    """
    Represents a template for MoM formatting.
    
    Attributes:
        name (str): Name of the template
        description (str): Description of the template
        format_type (str): Format type (text, html, pdf, etc.)
        content (str): Template content with placeholders
        sections (List[str]): List of sections to include
        branding (List[BrandingElement]): List of branding elements
        metadata (Dict[str, Any]): Additional metadata
        language (str): Language code (e.g., 'en', 'es', 'fr')
        translations (Dict[str, str]): Dictionary of translated content by language code
    """
    name: str
    description: str
    format_type: str
    content: str
    sections: List[str] = field(default_factory=list)
    branding: List[BrandingElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    language: str = "en"
    translations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the template
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """
        Create template from dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the template
            
        Returns:
            Template: Template instance
        """
        # Extract branding elements
        branding_data = data.pop('branding', [])
        branding = [
            BrandingElement(**element) for element in branding_data
        ]
        
        # Create template
        return cls(**data, branding=branding)
    
    def to_json(self) -> str:
        """
        Convert template to JSON string.
        
        Returns:
            str: JSON string representation of the template
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Template':
        """
        Create template from JSON string.
        
        Args:
            json_str (str): JSON string representation of the template
            
        Returns:
            Template: Template instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save(self, path: str) -> None:
        """
        Save template to file.
        
        Args:
            path (str): Path to save the template
        """
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, path: str) -> 'Template':
        """
        Load template from file.
        
        Args:
            path (str): Path to the template file
            
        Returns:
            Template: Template instance
        """
        with open(path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())


class TemplateManager:
    """
    Manages templates for MoM formatting.
    
    This class provides methods for loading, saving, and managing templates.
    
    Attributes:
        templates_dir (str): Directory for storing templates
        templates (Dict[str, Template]): Dictionary of templates
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the TemplateManager with optional templates directory.
        
        Args:
            templates_dir (str, optional): Directory for storing templates
        """
        self.templates_dir = templates_dir or os.path.join(os.path.dirname(__file__), 'templates')
        self.templates: Dict[str, Template] = {}
        self._load_templates()
        logger.info("TemplateManager initialized")
    
    def _load_templates(self) -> None:
        """Load templates from templates directory."""
        try:
            # Create templates directory if it doesn't exist
            os.makedirs(self.templates_dir, exist_ok=True)
            
            # Load templates from files
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    try:
                        path = os.path.join(self.templates_dir, filename)
                        template = Template.load(path)
                        self.templates[template.name] = template
                        logger.info(f"Loaded template: {template.name}")
                    except Exception as e:
                        logger.warning(f"Error loading template {filename}: {e}")
        
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def get_template(self, name: str, language: str = "en") -> Optional[Template]:
        """
        Get a template by name and language.
        
        Args:
            name (str): Template name
            language (str, optional): Language code. Defaults to "en".
            
        Returns:
            Optional[Template]: Template instance, or None if not found
        """
        template = self.templates.get(name)
        
        if not template:
            return None
            
        # If the template is already in the requested language, return it
        if template.language == language:
            return template
            
        # If the template has a translation for the requested language, create a new template with that content
        if language in template.translations:
            # Create a copy of the template with the translated content
            translated_template = Template(
                name=template.name,
                description=template.description,
                format_type=template.format_type,
                content=template.translations[language],
                sections=template.sections,
                branding=template.branding,
                metadata=template.metadata,
                language=language,
                translations=template.translations
            )
            return translated_template
            
        # If no translation is available, return the original template
        return template
    
    def get_templates(self, format_type: Optional[str] = None) -> List[Template]:
        """
        Get all templates, optionally filtered by format type.
        
        Args:
            format_type (str, optional): Format type to filter by
            
        Returns:
            List[Template]: List of templates
        """
        if format_type:
            return [t for t in self.templates.values() if t.format_type == format_type]
        else:
            return list(self.templates.values())
    
    def add_template(self, template: Template) -> None:
        """
        Add a template.
        
        Args:
            template (Template): Template to add
        """
        self.templates[template.name] = template
        
        # Save template to file
        path = os.path.join(self.templates_dir, f"{template.name.lower().replace(' ', '_')}.json")
        template.save(path)
        
        logger.info(f"Added template: {template.name}")
    
    def remove_template(self, name: str) -> bool:
        """
        Remove a template.
        
        Args:
            name (str): Template name
            
        Returns:
            bool: True if template was removed, False otherwise
        """
        if name in self.templates:
            # Remove template from memory
            template = self.templates.pop(name)
            
            # Remove template file
            path = os.path.join(self.templates_dir, f"{name.lower().replace(' ', '_')}.json")
            if os.path.exists(path):
                os.remove(path)
            
            logger.info(f"Removed template: {name}")
            return True
        
        return False
    
    def create_default_templates(self) -> None:
        """Create default templates if they don't exist."""
        # Check if we already have templates
        if self.templates:
            return
        
        # Create default text template in English
        text_template = Template(
            name="Default Text",
            description="Default text template for MoM",
            format_type="text",
            language="en",
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
                     "discussion_points", "action_items", "decisions", "next_steps"],
            translations={
                "es": """
ACTA DE REUNIÓN

Título de la Reunión: {meeting_title}
Fecha y Hora: {date_time}

Asistentes:
{attendees}

Agenda:
{agenda}

Puntos Clave de Discusión:
{discussion_points}

Elementos de Acción:
{action_items}

Decisiones Tomadas:
{decisions}

Próximos Pasos:
{next_steps}
                """.strip(),
                "fr": """
COMPTE RENDU DE RÉUNION

Titre de la Réunion: {meeting_title}
Date et Heure: {date_time}

Participants:
{attendees}

Ordre du Jour:
{agenda}

Points Clés de Discussion:
{discussion_points}

Éléments d'Action:
{action_items}

Décisions Prises:
{decisions}

Prochaines Étapes:
{next_steps}
                """.strip(),
                "de": """
SITZUNGSPROTOKOLL

Besprechungstitel: {meeting_title}
Datum & Uhrzeit: {date_time}

Teilnehmer:
{attendees}

Tagesordnung:
{agenda}

Wichtige Diskussionspunkte:
{discussion_points}

Aktionspunkte:
{action_items}

Getroffene Entscheidungen:
{decisions}

Nächste Schritte:
{next_steps}
                """.strip(),
                "it": """
VERBALE DI RIUNIONE

Titolo della Riunione: {meeting_title}
Data e Ora: {date_time}

Partecipanti:
{attendees}

Ordine del Giorno:
{agenda}

Punti Chiave di Discussione:
{discussion_points}

Elementi d'Azione:
{action_items}

Decisioni Prese:
{decisions}

Prossimi Passi:
{next_steps}
                """.strip(),
                "pt": """
ATA DE REUNIÃO

Título da Reunião: {meeting_title}
Data e Hora: {date_time}

Participantes:
{attendees}

Pauta:
{agenda}

Pontos-Chave de Discussão:
{discussion_points}

Itens de Ação:
{action_items}

Decisões Tomadas:
{decisions}

Próximos Passos:
{next_steps}
                """.strip(),
                "ja": """
議事録

会議タイトル: {meeting_title}
日時: {date_time}

出席者:
{attendees}

議題:
{agenda}

主要な議論点:
{discussion_points}

アクションアイテム:
{action_items}

決定事項:
{decisions}

次のステップ:
{next_steps}
                """.strip(),
                "zh": """
会议纪要

会议标题: {meeting_title}
日期和时间: {date_time}

与会者:
{attendees}

议程:
{agenda}

关键讨论点:
{discussion_points}

行动项目:
{action_items}

做出的决定:
{decisions}

下一步:
{next_steps}
                """.strip(),
                "ru": """
ПРОТОКОЛ ВСТРЕЧИ

Название Встречи: {meeting_title}
Дата и Время: {date_time}

Участники:
{attendees}

Повестка Дня:
{agenda}

Ключевые Моменты Обсуждения:
{discussion_points}

Задачи:
{action_items}

Принятые Решения:
{decisions}

Следующие Шаги:
{next_steps}
                """.strip()
            }
        )
        self.add_template(text_template)
        
        # Create default HTML template in English
        html_template = Template(
            name="Default HTML",
            description="Default HTML template for MoM",
            format_type="html",
            language="en",
            content="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meeting_title}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        
        header {
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #2c3e50;
            margin: 0 0 10px 0;
        }
        
        h2 {
            color: #3498db;
            margin: 0 0 10px 0;
        }
        
        h3 {
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        
        .date-time {
            color: #7f8c8d;
            font-style: italic;
        }
        
        section {
            margin-bottom: 20px;
        }
        
        .content {
            padding-left: 15px;
        }
        
        footer {
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.8em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Minutes of Meeting</h1>
            <h2>{meeting_title}</h2>
            <p class="date-time">{date_time}</p>
        </header>
        
        <section>
            <h3>Attendees</h3>
            <div class="content">
                {attendees}
            </div>
        </section>
        
        <section>
            <h3>Agenda</h3>
            <div class="content">
                {agenda}
            </div>
        </section>
        
        <section>
            <h3>Key Discussion Points</h3>
            <div class="content">
                {discussion_points}
            </div>
        </section>
        
        <section>
            <h3>Action Items</h3>
            <div class="content">
                {action_items}
            </div>
        </section>
        
        <section>
            <h3>Decisions Made</h3>
            <div class="content">
                {decisions}
            </div>
        </section>
        
        <section>
            <h3>Next Steps</h3>
            <div class="content">
                {next_steps}
            </div>
        </section>
        
        <footer>
            <p>Generated by AI-Powered MoM Generator</p>
        </footer>
    </div>
</body>
</html>
            """.strip(),
            sections=["meeting_title", "date_time", "attendees", "agenda", 
                     "discussion_points", "action_items", "decisions", "next_steps"],
            translations={
                "es": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meeting_title}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        
        header {
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #2c3e50;
            margin: 0 0 10px 0;
        }
        
        h2 {
            color: #3498db;
            margin: 0 0 10px 0;
        }
        
        h3 {
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        
        .date-time {
            color: #7f8c8d;
            font-style: italic;
        }
        
        section {
            margin-bottom: 20px;
        }
        
        .content {
            padding-left: 15px;
        }
        
        footer {
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.8em;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Acta de Reunión</h1>
            <h2>{meeting_title}</h2>
            <p class="date-time">{date_time}</p>
        </header>
        
        <section>
            <h3>Asistentes</h3>
            <div class="content">
                {attendees}
            </div>
        </section>
        
        <section>
            <h3>Agenda</h3>
            <div class="content">
                {agenda}
            </div>
        </section>
        
        <section>
            <h3>Puntos Clave de Discusión</h3>
            <div class="content">
                {discussion_points}
            </div>
        </section>
        
        <section>
            <h3>Elementos de Acción</h3>
            <div class="content">
                {action_items}
            </div>
        </section>
        
        <section>
            <h3>Decisiones Tomadas</h3>
            <div class="content">
                {decisions}
            </div>
        </section>
        
        <section>
            <h3>Próximos Pasos</h3>
            <div class="content">
                {next_steps}
            </div>
        </section>
        
        <footer>
            <p>Generado por Generador de Actas con IA</p>
        </footer>
    </div>
</body>
</html>
                """
            }
        )
        self.add_template(html_template)
        
        # Create default Markdown template in English
        markdown_template = Template(
            name="Default Markdown",
            description="Default Markdown template for MoM",
            format_type="markdown",
            language="en",
            content="""
# Minutes of Meeting: {meeting_title}

**Date & Time:** {date_time}

## Attendees

{attendees}

## Agenda

{agenda}

## Key Discussion Points

{discussion_points}

## Action Items

{action_items}

## Decisions Made

{decisions}

## Next Steps

{next_steps}
            """.strip(),
            sections=["meeting_title", "date_time", "attendees", "agenda", 
                     "discussion_points", "action_items", "decisions", "next_steps"],
            translations={
                "es": """
# Acta de Reunión: {meeting_title}

**Fecha y Hora:** {date_time}

## Asistentes

{attendees}

## Agenda

{agenda}

## Puntos Clave de Discusión

{discussion_points}

## Elementos de Acción

{action_items}

## Decisiones Tomadas

{decisions}

## Próximos Pasos

{next_steps}
                """.strip(),
                "fr": """
# Compte Rendu de Réunion: {meeting_title}

**Date et Heure:** {date_time}

## Participants

{attendees}

## Ordre du Jour

{agenda}

## Points Clés de Discussion

{discussion_points}

## Éléments d'Action

{action_items}

## Décisions Prises

{decisions}

## Prochaines Étapes

{next_steps}
                """.strip(),
                "de": """
# Sitzungsprotokoll: {meeting_title}

**Datum & Uhrzeit:** {date_time}

## Teilnehmer

{attendees}

## Tagesordnung

{agenda}

## Wichtige Diskussionspunkte

{discussion_points}

## Aktionspunkte

{action_items}

## Getroffene Entscheidungen

{decisions}

## Nächste Schritte

{next_steps}
                """.strip()
            }
        )
        self.add_template(markdown_template)
        
        logger.info("Created default templates")
        
    def add_template_translation(self, template_name: str, language: str, translated_content: str) -> bool:
        """
        Add a translation to an existing template.
        
        Args:
            template_name (str): Name of the template to add translation to
            language (str): Language code for the translation
            translated_content (str): Translated template content
            
        Returns:
            bool: True if translation was added, False otherwise
        """
        if template_name not in self.templates:
            logger.warning(f"Template '{template_name}' not found")
            return False
            
        template = self.templates[template_name]
        
        # Add or update translation
        template.translations[language] = translated_content
        
        # Save template to file
        path = os.path.join(self.templates_dir, f"{template_name.lower().replace(' ', '_')}.json")
        template.save(path)
        
        logger.info(f"Added {language} translation to template: {template_name}")
        return True
        
    def get_supported_languages(self, template_name: str) -> List[str]:
        """
        Get list of supported languages for a template.
        
        Args:
            template_name (str): Name of the template
            
        Returns:
            List[str]: List of supported language codes
        """
        if template_name not in self.templates:
            return []
            
        template = self.templates[template_name]
        
        # Start with the template's primary language
        languages = [template.language]
        
        # Add all languages from translations
        languages.extend(template.translations.keys())
        
        return languages