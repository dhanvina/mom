# MinutesAI (Meeting Output Manager) Architecture
This document provides a comprehensive overview of the MinutesAI system architecture, including components, data flow, and technical infrastructure.
## Overview
MinutesAI is designed as a modular, scalable system for processing meeting transcripts and generating structured Minutes of Meeting documents. The architecture follows microservices principles with clear separation of concerns.
## System Components
### 1. Core Processing Engine
The heart of the MinutesAI system responsible for transcript processing and content extraction.
#### TranscriptLoader
- **Purpose**: Loads and preprocesses meeting transcripts
- **Supported Formats**: .txt, .doc, .docx, .mp3, .wav
- **Features**: 
  - File format detection and validation
  - Text preprocessing and cleaning
  - Audio transcription (via Whisper/speech-to-text)
  - Encoding detection and normalization
#### MinutesAIExtractor
- **Purpose**: Extracts structured meeting minutes sections using AI
- **Technology**: LangChain + Ollama integration
- **Capabilities**:
  - Natural Language Processing
  - Context-aware section identification
  - Entity recognition (attendees, action items, decisions)
  - Sentiment analysis and key point extraction
#### MinutesAIFormatter
- **Purpose**: Formats extracted data into various output formats
- **Output Formats**: Text, JSON, HTML, PDF, Markdown
- **Features**:
  - Template-based formatting
  - Custom styling and branding
  - Multi-language support
  - Export customization
### 2. User Interfaces
#### CLI Interface
- **Technology**: Python Click framework
- **Features**:
  - Command-line processing
  - Batch operations
  - Configuration management
  - Progress indicators and verbose logging
#### Streamlit Web UI
- **Technology**: Streamlit framework
- **Features**:
  - File upload interface
  - Real-time processing status
  - Interactive result viewing
  - Configuration panel
  - Export functionality
### 3. Data Storage
#### Configuration Management
- **Format**: YAML-based configuration files
- **Scope**: Application settings, AI model parameters, output templates
- **Features**: Environment-specific configs, validation schemas
#### Processing Cache
- **Technology**: File-based caching system
- **Purpose**: Store intermediate processing results
- **Benefits**: Faster reprocessing, recovery from failures
#### Output Storage
- **Location**: Configurable output directories
