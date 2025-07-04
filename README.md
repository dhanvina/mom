# AI-Powered Minutes of Meeting (MoM) Generator

## Overview

This project is an AI-powered Minutes of Meeting (MoM) generator that leverages [LangChain](https://python.langchain.com/docs/) and [Ollama](https://ollama.com/) to automatically extract and structure meeting summaries from raw transcripts. Designed with Object-Oriented Programming (OOP) principles, it ensures maintainability, scalability, and ease of collaboration for teams.

---

## Features
- **Automated MoM Extraction:** Generate structured MoM documents from meeting transcripts using AI.
- **Standardized Output:** Consistent sections: Meeting Title, Date & Time, Attendees, Agenda, Key Discussion Points, Action Items, Decisions Made, Next Steps.
- **Flexible Input/Output:** Supports various transcript formats and outputs (text, JSON, HTML).
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
2. **Run the application:**
   ```bash
   python main.py --transcript path/to/meeting.txt --output mom_output.txt
   ```
3. **View the generated MoM** in your specified output format.

---

## Project Roadmap & Task Breakdown

### Phase 1: Planning & Setup
- [ ] Define requirements and MoM sections
- [ ] Assign team roles
- [ ] Set up repository and environment

### Phase 2: Core Development
- [ ] Design and implement `TranscriptLoader` (loads/preprocesses transcripts)
- [ ] Design and implement `MoMExtractor` (LangChain + Ollama integration, prompt template)
- [ ] Design and implement `MoMFormatter` (formats output)
- [ ] Design and implement `MainApp` (workflow orchestration, CLI)

### Phase 3: Integration & Testing
- [ ] Integrate all components
- [ ] Write unit and integration tests
- [ ] Test with real and edge-case transcripts

### Phase 4: Documentation & Polish
- [ ] Document code and usage
- [ ] Add example input/output
- [ ] Polish CLI or UI

### Phase 5: Review & Delivery
- [ ] Code review and refactoring
- [ ] Final testing and release

#### **Kanban Board Columns**
- To Do
- In Progress
- Review
- Done

#### **Labels**
- `backend`, `frontend`, `AI`, `testing`, `documentation`, `enhancement`, `bug`, `refactor`

---

## Contribution Guidelines

1. Fork the repository and create your branch from `main`.
2. Write clear, modular code with docstrings and comments.
3. Add tests for new features or bug fixes.
4. Submit a pull request with a clear description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements
- [LangChain](https://python.langchain.com/docs/)
- [Ollama](https://ollama.com/)

---

## Contact
For questions or support, please open an issue in the repository.