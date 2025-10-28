# AI-Powered Minutes of Meeting Generator

## Overview
This project is an AI-powered Minutes of Meeting (MoM) generator that leverages [LangChain](https://python.langchain.com/docs/) and [Ollama](https://ollama.com/) to automatically extract and structure meeting summaries from raw transcripts. Designed with Object-Oriented Programming (OOP) principles, it ensures maintainability, scalability, and ease of collaboration for teams.

---

## Features
- **Automated MoM Extraction:** Generate structured MoM documents from meeting transcripts using AI.
- **Standardized Output:** Consistent sections: Meeting Title, Date & Time, Attendees, Agenda, Key Discussion Points, Action Items, Decisions Made, Next Steps.
- **Input:** Supports .txt, .doc, .mp3
- **Output** Supports .pdf
- **Extensible OOP Design:** Modular classes for easy extension and testing.
- **CLI Interface:** Simple command-line interface for ease of use.

---

## Architecture
```
TranscriptLoader  -->  MoMExtractor  -->  MoMFormatter  -->  MainApp
      |                 |                  |                |
  (Loads &         (Extracts MoM        (Formats         (Orchestrates
  preprocesses)    sections using      structured        the workflow)
  transcript)      LangChain+Ollama)   output)
```

### Main Classes
- **TranscriptLoader:** Loads and preprocesses meeting transcripts.
- **MoMExtractor:** Uses LangChain and Ollama to extract MoM sections via prompt templates.
- **MoMFormatter:** Formats extracted data into text, JSON, or HTML.
- **MainApp:** Orchestrates the workflow and user interface.

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
- [LangChain](https://python.langchain.com/docs/) Python package

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd mom

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage
1. **Prepare your meeting transcript** (e.g., `meeting.txt`).
2. **Run the CLI tool:**
   ```bash
   python main.py --input meeting.txt --output mom_output.txt
   ```
3. **View your structured Minutes of Meeting.**

### CLI Options
- `--input`: Path to the meeting transcript file
- `--output`: Path for the generated MoM file
- `--format`: Output format (txt, json, html, pdf)
- `--verbose`: Enable detailed logging

### Streamlit UI
For a user-friendly web interface:
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
mom/
├── src/mom/             # Main source code
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
