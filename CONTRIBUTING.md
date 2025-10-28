# Contributing to mom
Thank you for your interest in contributing to this project! We welcome contributions from the community and appreciate your efforts to improve the project.

## Table of Contents
- [Getting Started](#getting-started)
- [Pre-commit Hooks Setup](#pre-commit-hooks-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue References](#issue-references)
- [Community Standards](#community-standards)
- [Running Tests](#running-tests)

## Getting Started

### Fork the Repository
1. Fork the repository by clicking the "Fork" button at the top right of the repository page
2. Clone your forked repository to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mom.git
   cd mom
   ```
3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/dhanvina/mom.git
   ```

### Create a Branch
Always create a new branch for your work. Never commit directly to the `main` branch.
```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - for new features
- `bugfix/` - for bug fixes
- `hotfix/` - for urgent fixes
- `docs/` - for documentation changes
- `refactor/` - for code refactoring

## Pre-commit Hooks Setup

This project uses pre-commit hooks to ensure code quality and consistency. These hooks automatically run checks before each commit to catch issues early.

### Installing Pre-commit

1. **Install pre-commit** (if you haven't already):
   ```bash
   # Using pip
   pip install pre-commit
   
   # Using conda
   conda install -c conda-forge pre-commit
   
   # Using homebrew (macOS)
   brew install pre-commit
   ```

2. **Install the git hook scripts**:
   ```bash
   pre-commit install
   ```

3. **Verify installation**:
   ```bash
   pre-commit --version
   ```

### What the Pre-commit Hooks Do

Our `.pre-commit-config.yaml` includes several tools that will automatically run on your code:

- **Black**: Automatically formats Python code to ensure consistent style
- **isort**: Sorts and organizes import statements
- **Flake8**: Checks for Python syntax errors and style issues
- **Bandit**: Scans for common security issues
- **MyPy**: Performs static type checking
- **General hooks**: Check for trailing whitespace, file endings, YAML syntax, etc.

### Running Pre-commit Hooks Manually

- **Run on all files**:
  ```bash
  pre-commit run --all-files
  ```

- **Run on staged files only** (what happens during commit):
  ```bash
  pre-commit run
  ```

- **Run a specific hook**:
  ```bash
  pre-commit run black
  pre-commit run flake8
  ```

### Automatic Execution

Once installed, pre-commit hooks run automatically:
- **Before each commit**: Hooks run on staged files
- **If any hook fails**: The commit is blocked until issues are fixed
- **Auto-fixes**: Some hooks (like Black, isort) automatically fix issues

### Skipping Hooks (Not Recommended)

In rare cases where you need to skip hooks:
```bash
# Skip all hooks
git commit -m "your message" --no-verify

# Skip specific hooks
SKIP=flake8,mypy git commit -m "your message"
```

**Note**: Skipping hooks is discouraged as it bypasses quality checks.

### Troubleshooting

- **Hook installation issues**: Try `pre-commit clean` then `pre-commit install`
- **Outdated hooks**: Run `pre-commit autoupdate` to update hook versions
- **Cache issues**: Use `pre-commit clean` to clear the cache

## How to Contribute
1. **Find or create an issue**: Before starting work, check if an issue exists for what you want to do. If not, create one to discuss your proposed changes.
2. **Fork and branch**: Fork the repository and create a feature branch from `main`.
3. **Set up pre-commit hooks**: Follow the [Pre-commit Hooks Setup](#pre-commit-hooks-setup) guide above.
4. **Make your changes**: Implement your feature or fix with clear, commented code.
5. **Write/modify tests**: Ensure your changes are covered by tests (see [Testing Requirements](#testing-requirements)).
6. **Test locally**: Run all tests locally to ensure nothing is broken (see [Running Tests](#running-tests)).
7. **Run pre-commit checks**: Ensure all pre-commit hooks pass before committing.
8. **Commit your changes**: Use clear, descriptive commit messages.
9. **Push to your fork**: Push your branch to your forked repository.
10. **Submit a pull request**: Create a PR against the main repository's `main` branch.
11. **Respond to feedback**: Address any review comments promptly.

## Code Style Guidelines

### Python Code Style
We follow PEP 8 with some modifications:
- Use Black for formatting (configured in `.pre-commit-config.yaml`)
- Maximum line length: 88 characters (Black's default)
- Use isort for import organization
- Use type hints where appropriate

### General Practices
- Write clear, self-documenting code
- Add comments for complex logic
- Use descriptive variable and function names
- Follow existing patterns in the codebase

## Testing Requirements

### Writing Tests
- Write unit tests for new features
- Maintain or improve test coverage
- Test edge cases and error conditions
- Use descriptive test names

### Test Structure
```python
def test_descriptive_name():
    # Arrange
    # Set up test data
    
    # Act
    # Execute the code being tested
    
    # Assert
    # Verify the results
```

## Pull Request Process

### Before Submitting
1. ✅ All tests pass locally
2. ✅ Pre-commit hooks pass
3. ✅ Code follows style guidelines
4. ✅ Documentation is updated (if applicable)
5. ✅ Commit messages are clear

### PR Description
Your PR should include:
- **What**: Description of changes
- **Why**: Reason for changes
- **How**: Approach taken
- **Testing**: How you tested the changes
- **Related Issues**: Link to relevant issues

### Review Process
- PRs require at least one approving review
- Address all review comments
- Keep PRs focused and reasonably sized
- Be responsive to feedback

## Issue References

When referencing issues in commits or PRs:
- `Fixes #123` - Closes the issue automatically
- `Closes #123` - Also closes the issue
- `Related to #123` - Links without closing
- `Addresses #123` - Links without closing

## Community Standards

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on the code, not the person

### Communication
- Use clear, professional language
- Be patient with contributors
- Ask questions when unclear
- Share knowledge and help others

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_specific.py
```

### Run with Coverage
```bash
pytest --cov=mom --cov-report=html
```

### Run in Verbose Mode
```bash
pytest -v
```

---

Thank you for contributing to mom! Your efforts help make this project better for everyone. 🎉
