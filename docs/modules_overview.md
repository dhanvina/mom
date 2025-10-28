# Modules Overview

This document provides a comprehensive overview of all Python modules in the MinutesAI application. For architectural details, see [architecture.md](./architecture.md).

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
The core module contains the main application logic and entry point for the MinutesAI application.

### Files and Classes
| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`main_app.py`](../app/core/main_app.py) | `MinutesAIApp`, `run_app()`, `setup_logging()` | Main application class and startup functions |

### Public API
#### `MinutesAIApp` Class
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
| [`sentiment_analyzer.py`](../app/analyzer/sentiment_analyzer.py) | `SentimentAnalyzer`, `SentimentResults` | Performs sentiment analysis on meeting content |
| [`action_item_detector.py`](../app/analyzer/action_item_detector.py) | `ActionItemDetector`, `ActionItem` | Identifies and extracts action items from transcripts |

### Public API
#### `EfficiencyAnalyzer` Class
- **Purpose:** Calculate meeting efficiency metrics
- **Key Methods:**
  - `analyze()` - Computes efficiency scores
  - `generate_report()` - Creates detailed efficiency report
  - `get_recommendations()` - Provides actionable suggestions

#### `SentimentAnalyzer` Class
- **Purpose:** Analyze emotional tone and sentiment
- **Key Methods:**
  - `analyze_transcript()` - Overall sentiment analysis
  - `analyze_by_speaker()` - Per-speaker sentiment breakdown
  - `detect_conflict_points()` - Identifies potential disagreements

#### `ActionItemDetector` Class
- **Purpose:** Extract and structure action items
- **Key Methods:**
  - `extract_action_items()` - Identifies action items
  - `assign_owners()` - Maps action items to responsible parties
  - `set_priorities()` - Determines task priorities

### Dependencies
- **Standard Library:** `re`, `datetime`, `collections`
- **External:** `numpy`, `sklearn`, `transformers`
- **Internal:** `utils.text_processing`, `utils.nlp_helpers`

### Extension Points
- Custom metric calculators
- Pluggable sentiment models
- Action item classification rules

---

## Extractor Module
**Location:** [`app/extractor/`](../app/extractor/)

### Overview
Handles extraction of structured meeting minutes sections from raw transcripts using AI/LLM integration.

### Files and Classes
| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`minutesai_extractor.py`](../app/extractor/minutesai_extractor.py) | `MinutesAIExtractor`, `ExtractionResult` | Main extraction engine using LangChain |
| [`transcript_loader.py`](../app/extractor/transcript_loader.py) | `TranscriptLoader`, `LoadedTranscript` | Loads and preprocesses various transcript formats |
| [`prompt_templates.py`](../app/extractor/prompt_templates.py) | `PromptManager`, Template constants | Manages AI prompts for extraction |

### Public API
#### `MinutesAIExtractor` Class
- **Purpose:** Extract structured meeting minutes using AI
- **Key Methods:**
  - `extract()` - Main extraction method
  - `extract_section()` - Extract specific section
  - `validate_extraction()` - Quality check results
  - `retry_failed_sections()` - Retry failed extractions

#### `TranscriptLoader` Class
- **Purpose:** Load and preprocess transcripts
- **Key Methods:**
  - `load()` - Load transcript from file
  - `preprocess()` - Clean and normalize text
  - `detect_speakers()` - Identify speakers if present
  - `segment_transcript()` - Break into logical sections

#### `PromptManager` Class
- **Purpose:** Manage AI prompt templates
- **Key Methods:**
  - `get_prompt()` - Retrieve prompt by name
  - `customize_prompt()` - Modify prompts dynamically
  - `validate_template()` - Check prompt structure

### Dependencies
- **Standard Library:** `json`, `pathlib`, `typing`
- **External:** `langchain`, `ollama`, `docx`, `pdfplumber`
- **Internal:** `utils.file_handlers`, `utils.validators`

### Extension Points
- Custom prompt templates
- Alternative LLM providers
- Additional file format support
- Custom preprocessing pipelines

---

## Formatter Module
**Location:** [`app/formatter/`](../app/formatter/)

### Overview
Formats extracted meeting minutes data into various output formats (text, JSON, HTML, PDF, etc.).

### Files and Classes
| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`minutesai_formatter.py`](../app/formatter/minutesai_formatter.py) | `MinutesAIFormatter`, `FormatterConfig` | Main formatting orchestrator |
| [`text_formatter.py`](../app/formatter/text_formatter.py) | `TextFormatter` | Plain text output formatting |
| [`json_formatter.py`](../app/formatter/json_formatter.py) | `JSONFormatter` | JSON output formatting |
| [`html_formatter.py`](../app/formatter/html_formatter.py) | `HTMLFormatter` | HTML output with templates |
| [`pdf_formatter.py`](../app/formatter/pdf_formatter.py) | `PDFFormatter` | PDF generation |

### Public API
#### `MinutesAIFormatter` Class
- **Purpose:** Format meeting minutes to desired output format
- **Key Methods:**
  - `format()` - Main formatting method
  - `format_as_text()` - Text output
  - `format_as_json()` - JSON output
  - `format_as_html()` - HTML output
  - `format_as_pdf()` - PDF output
  - `save_to_file()` - Write formatted output to file

#### Format-Specific Formatters
Each format has dedicated formatter class:
- **TextFormatter**: Simple, readable text format
- **JSONFormatter**: Structured JSON with schema validation
- **HTMLFormatter**: Styled HTML with customizable templates
- **PDFFormatter**: Professional PDF documents with branding

### Dependencies
- **Standard Library:** `json`, `io`, `datetime`
- **External:** `jinja2`, `reportlab`, `markdown2`
- **Internal:** `utils.template_engine`, `utils.validators`

### Extension Points
- Custom output formats
- Template customization
- Brand/theme support
- Export plugins

---

## Utils Module
**Location:** [`app/utils/`](../app/utils/)

### Overview
Provides utility functions and classes used across the application.

### Files and Classes
| File | Classes/Functions | Description |
|------|------------------|-------------|
| [`file_handlers.py`](../app/utils/file_handlers.py) | `FileHandler`, `FileValidator` | File I/O operations and validation |
| [`validators.py`](../app/utils/validators.py) | Various validation functions | Data validation utilities |
| [`config_manager.py`](../app/utils/config_manager.py) | `ConfigManager`, `Config` | Configuration management |
| [`logger.py`](../app/utils/logger.py) | `Logger`, logging utilities | Application logging setup |
| [`text_processing.py`](../app/utils/text_processing.py) | `TextProcessor` | Advanced text processing capabilities |

### Public API
#### `FileHandler` Class
- **Purpose:** Handle file I/O operations
- **Key Methods:**
  - `read_file()` - Read file contents
  - `write_file()` - Write data to file
  - `validate_path()` - Validate file paths
  - `detect_encoding()` - Detect file encoding

#### `ConfigManager` Class
- **Purpose:** Manage application configuration
- **Key Methods:**
  - `load_config()` - Load configuration files
  - `get_setting()` - Retrieve specific settings
  - `update_setting()` - Modify configuration
  - `validate_config()` - Check configuration validity

#### `TextProcessor` Class
- **Purpose:** Advanced text manipulation
- **Key Methods:**
  - `clean_text()` - Remove unwanted characters
  - `normalize_whitespace()` - Standardize spacing
  - `extract_entities()` - Named entity recognition
  - `summarize()` - Generate text summaries

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
The MinutesAI application supports extensibility through several mechanisms:

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
