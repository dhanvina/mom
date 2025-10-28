# Modules Overview

This document provides a comprehensive overview of all Python modules in the MOM (Meeting Organization Manager) application. For architectural details, see [architecture.md](./architecture.md).

## Table of Contents

- [Core Module](#core-module)
- [Analyzer Module](#analyzer-module)
- [Extractor Module](#extractor-module)
- [Formatter Module](#formatter-module)
- [Utils Module](#utils-module)
- [Configuration](#configuration)
- [Extension Points](#extension-points)

---

## Core Module

**Location:** [`app/core/`](../app/core/)

### Overview
The core module contains the main application logic and entry point for the MOM application.

### Files and Classes

| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`main_app.py`](../app/core/main_app.py) | `MOMApp`, `run_app()`, `setup_logging()` | Main application class and startup functions |

### Public API

#### `MOMApp` Class
- **Purpose:** Main application orchestrator
- **Key Methods:**
  - `initialize()` - Sets up application components
  - `process_meeting()` - Main meeting processing pipeline
  - `shutdown()` - Clean application shutdown

#### Functions
- `run_app()` - Application entry point
- `setup_logging()` - Configures application logging

### Dependencies
- **Standard Library:** `logging`, `asyncio`, `pathlib`
- **External:** `streamlit`, `pydantic`
- **Internal:** `analyzer`, `extractor`, `formatter`, `utils`

### Extension Points
- Plugin system for custom meeting processors
- Configurable logging handlers
- Custom UI components integration

---

## Analyzer Module

**Location:** [`app/analyzer/`](../app/analyzer/)

### Overview
Handles analysis of meeting content including efficiency metrics, sentiment analysis, and action item extraction.

### Files and Classes

| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`efficiency_analyzer.py`](../app/analyzer/efficiency_analyzer.py) | `EfficiencyAnalyzer`, `MeetingMetrics` | Analyzes meeting efficiency and generates metrics |
| [`sentiment_analyzer.py`](../app/analyzer/sentiment_analyzer.py) | `SentimentAnalyzer`, `EmotionDetector` | Natural language sentiment analysis |
| [`action_item_analyzer.py`](../app/analyzer/action_item_analyzer.py) | `ActionItemExtractor`, `TaskClassifier` | Extracts and classifies action items |
| [`topic_analyzer.py`](../app/analyzer/topic_analyzer.py) | `TopicModeler`, `KeywordExtractor` | Topic modeling and keyword extraction |

### Public API

#### `EfficiencyAnalyzer` Class
- **Purpose:** Analyze meeting efficiency and productivity
- **Key Methods:**
  - `analyze_meeting(transcript)` - Generate efficiency metrics
  - `calculate_participation_ratio()` - Measure participant engagement
  - `detect_time_wasters()` - Identify inefficient segments

#### `SentimentAnalyzer` Class
- **Purpose:** Analyze emotional tone and sentiment
- **Key Methods:**
  - `analyze_sentiment(text)` - Get sentiment scores
  - `detect_emotions(text)` - Identify specific emotions
  - `track_mood_changes()` - Monitor sentiment evolution

### Dependencies
- **Standard Library:** `re`, `collections`, `statistics`
- **External:** `nltk`, `spacy`, `transformers`, `scikit-learn`
- **Internal:** `utils.text_processing`, `utils.ml_helpers`

### Extension Points
- Custom analysis algorithms via plugin interface
- Configurable sentiment models
- Custom metric calculation functions
- Integration with external AI services

---

## Extractor Module

**Location:** [`app/extractor/`](../app/extractor/)

### Overview
Extraction layer for processing various media types including audio, video, text, and documents.

### Files and Classes

| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`audio_extractor.py`](../app/extractor/audio_extractor.py) | `AudioExtractor`, `TranscriptionService` | Audio processing and speech-to-text conversion |
| [`video_extractor.py`](../app/extractor/video_extractor.py) | `VideoExtractor`, `FrameAnalyzer` | Video processing and visual content extraction |
| [`text_extractor.py`](../app/extractor/text_extractor.py) | `TextExtractor`, `DocumentParser` | Text and document content extraction |
| [`metadata_extractor.py`](../app/extractor/metadata_extractor.py) | `MetadataExtractor`, `FileInfoParser` | File metadata and properties extraction |

### Public API

#### `AudioExtractor` Class
- **Purpose:** Process audio files and extract transcriptions
- **Key Methods:**
  - `extract_audio(file_path)` - Extract audio from various formats
  - `transcribe_speech(audio_data)` - Convert speech to text
  - `identify_speakers()` - Speaker diarization
  - `extract_audio_features()` - Audio characteristic analysis

#### `VideoExtractor` Class
- **Purpose:** Process video content and extract relevant information
- **Key Methods:**
  - `extract_frames(video_path)` - Extract key frames
  - `detect_slides()` - Identify presentation slides
  - `extract_text_from_video()` - OCR on video content

### Dependencies
- **Standard Library:** `os`, `tempfile`, `subprocess`
- **External:** `ffmpeg-python`, `whisper`, `opencv-python`, `pytesseract`
- **Internal:** `utils.file_handlers`, `utils.audio_utils`

### Extension Points
- Support for additional media formats
- Custom transcription services integration
- Pluggable audio/video processing pipelines
- External API integration for enhanced processing

---

## Formatter Module

**Location:** [`app/formatter/`](../app/formatter/)

### Overview
Formatting and output generation layer supporting multiple output formats including HTML, PDF, Word, and Markdown.

### Files and Classes

| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`base_formatter.py`](../app/formatter/base_formatter.py) | `BaseFormatter`, `FormatterInterface` | Abstract base class for all formatters |
| [`html_formatter.py`](../app/formatter/html_formatter.py) | `HTMLFormatter`, `HTMLTemplate` | HTML output generation |
| [`pdf_formatter.py`](../app/formatter/pdf_formatter.py) | `PDFFormatter`, `PDFGenerator` | PDF document generation |
| [`word_formatter.py`](../app/formatter/word_formatter.py) | `WordFormatter`, `DocxGenerator` | Microsoft Word document generation |
| [`markdown_formatter.py`](../app/formatter/markdown_formatter.py) | `MarkdownFormatter`, `MDGenerator` | Markdown output generation |
| [`json_formatter.py`](../app/formatter/json_formatter.py) | `JSONFormatter`, `DataSerializer` | JSON data export |
| [`template_manager.py`](../app/formatter/template_manager.py) | `TemplateManager`, `ThemeLoader` | Template and theme management |

### Public API

#### `BaseFormatter` Class
- **Purpose:** Abstract base for all output formatters
- **Key Methods:**
  - `format(data)` - Abstract method for formatting data
  - `validate_data(data)` - Input validation
  - `apply_styling()` - Apply formatting styles

#### `HTMLFormatter` Class
- **Purpose:** Generate HTML output with styling
- **Key Methods:**
  - `generate_report(meeting_data)` - Create HTML meeting report
  - `apply_template(template_name)` - Apply HTML template
  - `add_interactive_elements()` - Add JavaScript interactions

### Dependencies
- **Standard Library:** `json`, `xml.etree.ElementTree`, `datetime`
- **External:** `jinja2`, `weasyprint`, `python-docx`, `reportlab`
- **Internal:** `utils.template_helpers`, `utils.styling`

### Extension Points
- Custom output format support
- Template system extensibility
- Custom styling and theming
- Integration with external document services

---

## Utils Module

**Location:** [`app/utils/`](../app/utils/)

### Overview
Utility functions and helper classes used across the application.

### Files and Classes

| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`audio_utils.py`](../app/utils/audio_utils.py) | `AudioProcessor`, `format_converter()` | Audio processing utilities |
| [`config_loader.py`](../app/utils/config_loader.py) | `ConfigLoader`, `SettingsManager` | Configuration management |
| [`file_handlers.py`](../app/utils/file_handlers.py) | `FileManager`, `PathValidator` | File system operations |
| [`logger.py`](../app/utils/logger.py) | `Logger`, `setup_logger()` | Logging configuration |
| [`text_processing.py`](../app/utils/text_processing.py) | `TextProcessor`, `sanitize_text()` | Text processing utilities |
| [`validators.py`](../app/utils/validators.py) | `DataValidator`, `validate_input()` | Input validation functions |

### Public API

#### Utility Functions
- `format_converter(input_format, output_format)` - Convert between audio formats
- `sanitize_text(text)` - Clean and normalize text input
- `validate_input(data, schema)` - Validate data against schema
- `setup_logger(name, level)` - Configure application logging

#### Helper Classes
- `ConfigLoader` - Centralized configuration management
- `FileManager` - File system operations with error handling
- `TextProcessor` - Advanced text processing capabilities

### Dependencies
- **Standard Library:** `pathlib`, `logging`, `configparser`, `re`
- **External:** `pydantic`, `jsonschema`, `python-magic`
- **Internal:** Cross-module utilities

### Extension Points
- Custom validation rules
- Additional file format support
- Extended text processing algorithms
- Custom configuration sources

---

## Configuration

**Location:** [`app/main.py`](../app/main.py)

### Overview
Main application entry point and global configuration.

### Key Components
- Application bootstrapping
- Dependency injection setup
- Global error handling
- Streamlit app configuration

### Dependencies
- **All modules:** Core orchestration of all application components
- **External:** `streamlit`, `asyncio`, `sys`

---

## Extension Points

### Plugin System
The MOM application supports extensibility through several mechanisms:

#### 1. Custom Analyzers
- Extend `BaseAnalyzer` class in the analyzer module
- Register new analyzers through the plugin system
- Support for external AI/ML services integration

#### 2. Format Support
- Implement `FormatterInterface` for new output formats
- Add support for custom templates and themes
- Integration with external document services

#### 3. Data Sources
- Custom extractors for new media types
- Integration with meeting platforms (Zoom, Teams, etc.)
- Support for real-time streaming data

#### 4. Processing Pipeline
- Middleware system for request/response processing
- Custom preprocessing and postprocessing steps
- Event-driven architecture for component communication

### Configuration
Extension points are configurable through:
- Environment variables
- Configuration files (`config/`)
- Runtime plugin registration
- Feature flags and toggles

---

## Related Documentation

- [Architecture Overview](./architecture.md) - System architecture and design patterns
- [API Documentation](./api.md) - REST API endpoints and usage
- [Installation Guide](./installation.md) - Setup and deployment instructions
- [User Guide](./user_guide.md) - End-user documentation

---

## Contributing

When adding new modules:
1. Follow the established package structure
2. Implement appropriate base classes and interfaces
3. Add comprehensive docstrings and type hints
4. Update this overview document
5. Add appropriate tests in the corresponding test modules

For more information on contributing, see [CONTRIBUTING.md](../CONTRIBUTING.md).
