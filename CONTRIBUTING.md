# Contributing to confluence-engine

Thank you for your interest in contributing! This guide covers setup and the development workflow.

## Development Setup

### Clone and create a virtual environment

```bash
git clone https://github.com/Rustam335/confluence-engine.git
cd confluence-engine
python -m venv .venv
```

### Activate the virtual environment

**On Linux/macOS:**
```bash
source .venv/bin/activate
```

**On Windows:**
```bash
.venv\Scripts\activate
```

### Install in development mode

```bash
pip install -e ".[dev]"
```

This installs the package and its dev dependencies: pytest, pytest-cov, and ruff.

## Running Tests

```bash
pytest
```

To see coverage:

```bash
pytest --cov=confluence_engine
```

## Code Quality

We use `ruff` for linting:

```bash
ruff check .
```

To auto-fix issues:

```bash
ruff check . --fix
```

## Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and add tests if you're implementing new functionality
3. Run `pytest` and `ruff check .` — both must pass
4. Push and open a PR with a clear description of the changes

Thank you for contributing!
