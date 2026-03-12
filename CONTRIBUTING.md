# Contributing to LambdaX

Thank you for your interest in contributing to LambdaX! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/Monishwaran45/lambdax.git
cd lambdax
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Code Style

We use the following tools to maintain code quality:

- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all checks:
```bash
black src tests
isort src tests
flake8 src tests
mypy src
```

## Testing

Run tests with pytest:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=lambdax --cov-report=html
```

## Adding a New Guard

1. Create a new file in `src/lambdax/guards/`:
```python
from lambdax.core.guard import Guard
from lambdax.core.context import RequestContext

class MyGuard(Guard):
    async def inspect_input(self, text: str, context: RequestContext):
        # Implementation
        pass

    async def inspect_output(self, text: str, context: RequestContext):
        # Implementation
        pass
```

2. Register in `pyproject.toml`:
```toml
[project.entry-points."lambdax.guards"]
my_guard = "lambdax.guards.my_guard:MyGuard"
```

3. Add tests in `tests/unit/test_guards.py`

4. Update documentation

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests and linters
5. Commit with clear messages
6. Push to your fork
7. Open a pull request

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
