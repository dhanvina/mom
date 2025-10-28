# AI-Powered MinutesAI Generator

## Overview
This project is an AI-powered meeting minutes generator (MinutesAI) that leverages [LangChain](https://python.langchain.com/docs/) and [Ollama](https://ollama.com/) to automatically extract and structure meeting summaries from raw transcripts. Designed with Object-Oriented Programming (OOP) principles, it ensures maintainability, scalability, and ease of collaboration for teams.

---

## Features
- **Automated Meeting Minutes Extraction:** Generate structured meeting minutes documents from meeting transcripts using AI.
- **Standardized Output:** Consistent sections: Meeting Title, Date & Time, Attendees, Agenda, Key Discussion Points, Action Items, Decisions Made, Next Steps.
- **Input:** Supports .txt, .doc, .mp3
- **Output** Supports .pdf
- **Extensible OOP Design:** Modular classes for easy extension and testing.
- **CLI Interface:** Simple command-line interface for ease of use.

---

## Architecture
```
TranscriptLoader  -->  MinutesAIExtractor  -->  MinutesAIFormatter  -->  MinutesAIApp
      |                     |                          |                      |
  (Loads &             (Extracts meeting          (Formats              (Orchestrates
  preprocesses)        minutes sections using     structured             the workflow)
  transcript)          LangChain+Ollama)          output)
```

### Main Classes
- **TranscriptLoader:** Loads and preprocesses meeting transcripts.
- **MinutesAIExtractor:** Uses LangChain and Ollama to extract meeting minutes sections via prompt templates.
- **MinutesAIFormatter:** Formats extracted data into text, JSON, or HTML.
- **MinutesAIApp:** Orchestrates the workflow and user interface.

---

## Quick Start
🚀 **New contributors**: Get up and running quickly with our comprehensive [Quickstart Guide](docs/quickstart_guide.md)

The quickstart guide covers:
- Step-by-step installation and setup
- Testing procedures
- CLI and Streamlit UI usage
- Development workflow with pre-commit hooks
- Sample configurations and examples
- System architecture overview

## Setup

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.com/) installed and running
- Install required model:
```bash
ollama pull llama2
```

### Installation
1. Clone the repository:
```bash
git clone https://github.com/dhanvina/mom.git
cd mom
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install pre-commit hooks (optional but recommended):
```bash
pre-commit install
```

---

## Usage

### CLI Usage
```bash
python -m app.cli --transcript path/to/transcript.txt --output path/to/output.txt
```

### Streamlit UI
Launch the Streamlit web interface:
```bash
streamlit run app/streamlit_app.py
```

---

## Documentation
- [Quickstart Guide](docs/quickstart_guide.md) - Get started quickly
- [Architecture Documentation](docs/architecture.md) - System design and components
- [Modules Overview](docs/modules_overview.md) - Detailed module information
- [API Reference](docs/api.md) - API documentation
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute

---

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
The project uses pre-commit hooks for code quality:
```bash
pre-commit install
pre-commit run --all-files
```

### Project Structure
```
minutesai/
├── src/minutesai/       # Main source code
│   ├── core/           # Core business logic
│   ├── cli/            # Command-line interface
│   └── ui/             # Streamlit UI components
├── tests/              # Test suite
├── docs/               # Documentation
├── config/             # Configuration files
└── requirements.txt    # Dependencies
```

---

## Contributing
We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support
- 📚 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/dhanvina/mom/issues)
- 💬 [Discussions](https://github.com/dhanvina/mom/discussions)
- ❓ [FAQ](docs/faq.md)
