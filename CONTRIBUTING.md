# Contributing to mom

Thank you for your interest in contributing to this project! We welcome contributions from the community and appreciate your efforts to improve the project.

## Table of Contents

- [Getting Started](#getting-started)
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

## How to Contribute

1. **Find or create an issue**: Before starting work, check if an issue exists for what you want to do. If not, create one to discuss your proposed changes.
2. **Fork and branch**: Fork the repository and create a feature branch from `main`.
3. **Make your changes**: Implement your feature or fix with clear, commented code.
4. **Write/modify tests**: Ensure your changes are covered by tests (see [Testing Requirements](#testing-requirements)).
5. **Test locally**: Run all tests locally to ensure nothing is broken (see [Running Tests](#running-tests)).
6. **Commit your changes**: Use clear, descriptive commit messages.
7. **Push to your fork**: Push your branch to your forked repository.
8. **Open a pull request**: Submit a PR to the main repository with a clear description.

## Code Style Guidelines

Please follow these coding standards to maintain consistency across the project:

### General Guidelines

- Write clean, readable, and maintainable code
- Use meaningful variable and function names
- Keep functions small and focused on a single task
- Add comments for complex logic, but strive for self-documenting code
- Remove commented-out code and debug statements before committing

### Language-Specific Guidelines

**Python:**
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length of 88 characters (Black formatter standard)
- Use type hints where appropriate

**JavaScript/TypeScript:**
- Follow ESLint configuration provided in the project
- Use 2 spaces for indentation
- Use semicolons
- Prefer `const` over `let`, avoid `var`

### Formatting

- Run the project's formatter before committing (if applicable)
- Ensure there are no trailing whitespaces
- End files with a newline character

## Testing Requirements

**All new features and bug fixes must include tests.**

### Writing Tests

- Write unit tests for individual functions and components
- Write integration tests for feature workflows
- Ensure tests are deterministic and don't depend on external services
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Test edge cases and error conditions

### Modifying Existing Tests

- If you modify existing code, update corresponding tests
- Don't delete tests without justification
- If tests become obsolete, document why in your PR

### Test Coverage

- Aim for at least 80% code coverage for new code
- Check coverage reports after running tests
- Don't decrease overall project coverage with your changes

## Pull Request Process

### Before Submitting

1. **Sync with upstream**: Ensure your branch is up-to-date with the main repository
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
2. **Run all tests**: Verify all tests pass locally
3. **Run linters**: Fix any linting errors
4. **Review your changes**: Do a self-review of your code

### Submitting Your PR

1. **Create a descriptive title**: Use a clear, concise title that summarizes the change
2. **Fill out the PR template**: Provide all requested information
3. **Reference related issues**: Use "Fixes #123" or "Closes #123" syntax (see [Issue References](#issue-references))
4. **Describe your changes**: Explain what you changed and why
5. **Add screenshots/demos**: If applicable, include visual evidence of changes
6. **Mark as draft**: If the PR is not ready for review, mark it as a draft

### PR Review Process

- **Be responsive**: Respond to reviewer comments promptly
- **Be open to feedback**: Accept constructive criticism gracefully
- **Make requested changes**: Address all reviewer feedback
- **Request re-review**: After making changes, request another review
- **CI must pass**: All CI checks must pass before merging
- **Approvals required**: At least one approval from a maintainer is required

### After Approval

- A maintainer will merge your PR
- Your branch will be deleted automatically
- You can safely delete your local branch after merging

## Issue References

When working on issues, reference them properly in commits and PRs:

### In Commit Messages

```bash
git commit -m "Fix authentication bug (#123)"
git commit -m "Add user profile feature (relates to #456)"
```

### In Pull Requests

Use GitHub keywords to automatically link and close issues:

- `Fixes #123` - Closes the issue when PR is merged
- `Closes #123` - Same as "Fixes"
- `Resolves #123` - Same as "Fixes"
- `Relates to #123` - Links to issue without closing it
- `Part of #123` - Indicates partial implementation

Multiple issues can be referenced:
```
Fixes #123, fixes #456, relates to #789
```

## Community Standards

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors.

#### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members
- Helping newcomers get started

**Unacceptable behaviors include:**
- Use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

#### Enforcement

- Project maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, issues, and other contributions that do not align with these standards
- Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers
- All complaints will be reviewed and investigated promptly and fairly

### Respectful Communication

- **Be patient**: Not everyone has the same level of experience
- **Be constructive**: Provide helpful feedback, not just criticism
- **Be humble**: Everyone makes mistakes; learn from them
- **Be explicit**: Clearly communicate your intentions and expectations
- **Be considerate**: Your work will be used by others, and you depend on others' work

## Running Tests

### Running Tests Locally

Before submitting your PR, ensure all tests pass on your local machine.

#### Prerequisites

Install dependencies:
```bash
npm install
# or
pip install -r requirements.txt
# or
yarn install
```

#### Run All Tests

```bash
npm test
# or
python -m pytest
# or
yarn test
```

#### Run Specific Tests

```bash
npm test -- path/to/test/file
# or
pytest path/to/test/file.py
```

#### Run Tests with Coverage

```bash
npm test -- --coverage
# or
pytest --cov=src tests/
```

#### Run Linters

```bash
npm run lint
# or
flake8 .
black --check .
mypy .
```

### Continuous Integration (CI)

All pull requests automatically trigger CI pipelines that run:

1. **Automated tests**: All test suites across different environments
2. **Linting**: Code style and quality checks
3. **Coverage checks**: Ensure test coverage meets minimum thresholds
4. **Build verification**: Ensure the project builds successfully

#### CI Pipeline Details

- **Test environments**: Tests run on multiple OS versions and language versions
- **Required checks**: All CI checks must pass before merging
- **Status checks**: You can view CI results directly in your PR
- **Failure handling**: If CI fails, review the logs, fix issues, and push updates

#### Viewing CI Results

1. Navigate to your pull request
2. Scroll to the "Checks" section at the bottom
3. Click on failed checks to view detailed logs
4. Fix issues locally and push changes to re-trigger CI

### Debugging Test Failures

- **Read error messages carefully**: They usually indicate what went wrong
- **Run tests locally**: Reproduce failures on your machine
- **Check test logs**: Review full output for context
- **Isolate the problem**: Run only the failing test
- **Ask for help**: If stuck, ask in the PR comments or discussions

## Questions?

If you have questions or need help:

1. Check existing issues and discussions
2. Read the project documentation
3. Open a new issue with the "question" label
4. Reach out to maintainers in discussions

Thank you for contributing to mom! 🎉
