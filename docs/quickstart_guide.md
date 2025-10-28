# MinutesAI Quickstart Guide

Welcome to MinutesAI! This guide will help new contributors get up and running quickly with local development, testing, and usage.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Installation](#local-installation)
- [Testing](#testing)
- [Usage](#usage)
  - [CLI Interface](#cli-interface)
  - [Streamlit UI](#streamlit-ui)
- [Development Workflow](#development-workflow)
  - [Pre-commit Hooks](#pre-commit-hooks)
  - [CI Checks](#ci-checks)
- [Sample Configuration](#sample-configuration)
- [System Flow Diagram](#system-flow-diagram)
- [Next Steps](#next-steps)

## Prerequisites
- Python 3.8 or higher
- Git
- pip or conda
- Virtual environment tool (recommended)

## Local Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/dhanvina/mom.git
cd mom
```

### Step 2: Create and Activate Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n minutesai python=3.8
conda activate minutesai
```

### Step 3: Install Dependencies
```bash
# Install main dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Step 4: Environment Setup
```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit configuration as needed
vim config/config.yaml  # or your preferred editor
```

## Testing

### Step 1: Run Unit Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=minutesai --cov-report=html

# Run specific test file
pytest tests/test_extractor.py

# Run tests with verbose output
pytest -v
```

### Step 2: Run Integration Tests
```bash
# Run integration tests
pytest tests/integration/

# Run end-to-end tests
pytest tests/e2e/
```

### Step 3: Check Code Quality
```bash
# Run linters
flake8 app/

# Check type hints
mypy app/

# Format code
black app/ tests/

# Run all pre-commit checks
pre-commit run --all-files
```

## Usage

### CLI Interface

The MinutesAI CLI provides a command-line interface for processing meeting transcripts.

#### Basic Usage
```bash
# Process a single transcript
python -m app.cli --transcript examples/sample_transcript.txt --output output.txt

# Specify output format
python -m app.cli --transcript examples/sample_transcript.txt --output output.json --format json

# Use custom config
python -m app.cli --transcript examples/sample_transcript.txt --config config/custom.yaml
```

#### CLI Options
```bash
python -m app.cli --help

Options:
  --transcript PATH   Input transcript file (required)
  --output PATH       Output file path (default: stdout)
  --format TEXT       Output format: text, json, html, pdf (default: text)
  --config PATH       Configuration file path
  --verbose          Enable verbose logging
  --version          Show version and exit
  --help             Show this message and exit
```

#### Examples
```bash
# Process audio file
python -m app.cli --transcript meeting.mp3 --output meeting_minutes.txt

# Generate PDF output
python -m app.cli --transcript transcript.txt --output minutes.pdf --format pdf

# Process with verbose logging
python -m app.cli --transcript transcript.txt --output minutes.txt --verbose
```

### Streamlit UI

The Streamlit UI provides an interactive web interface for MinutesAI.

#### Starting the UI
```bash
streamlit run app/streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`.

#### Features
- **File Upload**: Drag-and-drop or browse for transcript files
- **Real-time Processing**: Watch progress as MinutesAI extracts information
- **Interactive Results**: View and edit extracted meeting minutes
- **Multiple Formats**: Export results in various formats
- **Configuration**: Adjust settings without editing config files

#### UI Workflow
1. Upload your transcript file (supported: .txt, .doc, .docx, .mp3, .wav)
2. Configure extraction settings (optional)
3. Click "Process" to generate meeting minutes
4. Review and edit the extracted information
5. Export results in your preferred format

## Development Workflow

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality before commits.

#### Installed Hooks
- `black`: Code formatting
- `flake8`: Linting
- `mypy`: Type checking
- `isort`: Import sorting
- `trailing-whitespace`: Remove trailing whitespace
- `end-of-file-fixer`: Ensure files end with newline

#### Running Pre-commit
```bash
# Run on staged files (automatic on commit)
pre-commit run

# Run on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### CI Checks

All pull requests must pass CI checks before merging:

#### Automated Checks
- **Tests**: All unit and integration tests must pass
- **Coverage**: Minimum 80% code coverage required
- **Linting**: No flake8 violations
- **Type Checking**: No mypy errors
- **Security**: Bandit security scan
- **Dependencies**: Safety check for vulnerable packages

#### Local CI Simulation
```bash
# Run the same checks as CI
./scripts/ci_checks.sh

# Or manually:
pytest --cov=minutesai --cov-report=term-missing
flake8 app/
mypy app/
bandit -r app/
safety check
```

## Sample Configuration

Here's a sample configuration file (`config/config.yaml`):

```yaml
# MinutesAI Configuration

# Application settings
app:
  name: MinutesAI
  version: "1.0.0"
  debug: false

# LLM settings
llm:
  provider: ollama
  model: llama2
  temperature: 0.7
  max_tokens: 2000

# Extraction settings
extraction:
  sections:
    - meeting_title
    - date_time
    - attendees
    - agenda
    - discussion_points
    - action_items
    - decisions
    - next_steps

# Output settings
output:
  default_format: text
  include_timestamp: true
  include_metadata: true

# Logging settings
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    console:
      enabled: true
    file:
      enabled: true
      path: logs/minutesai.log
      max_bytes: 10485760  # 10MB
      backup_count: 5

# Module-specific logging levels
loggers:
  minutesai.core: INFO
  minutesai.extractor: DEBUG
  minutesai.formatter: INFO
  minutesai.analyzer: INFO
```

## System Flow Diagram

```
┌─────────────────┐
│  Input Sources  │
│  (.txt, .doc,   │
│   .mp3, .wav)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ TranscriptLoader│
│  - Load files   │
│  - Preprocess   │
│  - Normalize    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│MinutesAI        │
│  Extractor      │
│  - LangChain    │
│  - Ollama LLM   │
│  - Extract info │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Analyzers     │
│  - Efficiency   │
│  - Sentiment    │
│  - Action Items │
└────────┬────────┘
         │
         v
┌─────────────────┐
│MinutesAI        │
│  Formatter      │
│  - Text/JSON    │
│  - HTML/PDF     │
│  - Templates    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Output Files   │
│  (various       │
│   formats)      │
└─────────────────┘
```

## Next Steps

After completing this quickstart guide:

1. **Read the Documentation**
   - [Architecture Overview](./architecture.md)
   - [Modules Overview](./modules_overview.md)
   - [API Reference](./api.md)

2. **Explore Examples**
   - Check the `examples/` directory for sample transcripts
   - Try processing different input formats
   - Experiment with different output formats

3. **Contribute**
   - Read [CONTRIBUTING.md](../CONTRIBUTING.md)
   - Check [open issues](https://github.com/dhanvina/mom/issues)
   - Submit your first pull request

4. **Join the Community**
   - Star the repository
   - Join discussions
   - Share your feedback

---

## Troubleshooting

### Common Issues

#### Issue: Import errors
```bash
# Solution: Ensure you're in the project root and venv is activated
cd /path/to/mom
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue: Ollama connection error
```bash
# Solution: Make sure Ollama is running
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama2
```

#### Issue: Tests failing
```bash
# Solution: Install dev dependencies and check test database
pip install -r requirements-dev.txt
pytest -v  # Run with verbose output to see specific failures
```

#### Issue: Pre-commit hooks failing
```bash
# Solution: Run the hooks manually to see errors
pre-commit run --all-files

# Fix issues and try again
black app/ tests/
flake8 app/
```

### Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: [Report bugs](https://github.com/dhanvina/mom/issues)
- **Discussions**: [Ask questions](https://github.com/dhanvina/mom/discussions)
- **Email**: Contact maintainers

---

Happy coding with MinutesAI! 🚀
