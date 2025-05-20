# Contributing to RiskBench Suite

Thank you for your interest in contributing to RiskBench Suite! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Create a branch: `git checkout -b feat/your-feature`
3. Install development dependencies:
   ```bash
   poetry install --with dev
   ```
4. Run tests:
   ```bash
   poetry run pytest
   ```

## Development Setup

1. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

2. Start the dashboard in development mode:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

## Code Style

- Python code follows PEP 8
- TypeScript/React code follows the project's ESLint configuration
- Use type hints in Python and TypeScript
- Write docstrings in NumPy format

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` a new feature
- `fix:` a bug fix
- `docs:` documentation only changes
- `chore:` build process or auxiliary tools changes
- `refactor:` code change that neither fixes a bug nor adds a feature
- `test:` adding missing tests or correcting existing tests
- `style:` changes that do not affect the meaning of the code

## Pull Request Process

1. Update documentation for any new features
2. Add or update tests as needed
3. Ensure all tests pass and linting is clean
4. Update the CHANGELOG.md
5. Submit a PR with a clear title and description
6. Request reviews from maintainers

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_specific.py

# Run with coverage
poetry run pytest --cov=riskbench_core
```

## Building Documentation

```bash
cd docs
make html
```

## Questions or Problems?

- Open an issue for bugs
- Join our community chat for questions
- Tag maintainers in PRs that are ready for review

Thank you for contributing to RiskBench Suite!
