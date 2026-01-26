# Contributing

Thank you for your interest in contributing to Savanty!

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ (for frontend development)
- Git

### Clone and Install

```bash
git clone https://github.com/skelf-research/savanty.git
cd savanty

# Install Python dependencies
uv sync

# Install dev dependencies
uv sync --extra dev

# Install desktop app dependencies (optional)
uv sync --extra desktop

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running in Development

```bash
# Set your API key
export OPENAI_API_KEY=your_key_here

# Run the web server
uv run savanty --web

# In another terminal, run frontend dev server
cd frontend
npm run dev

# Or run the desktop app
uv run savanty-desktop
```

## Project Structure

```
savanty/
├── savanty/               # Core Python package
│   ├── __init__.py        # Package metadata
│   ├── solver.py          # Main solver logic
│   ├── dspy_modules.py    # DSPy LLM signatures
│   ├── cli.py             # CLI and FastAPI app
│   └── logging_config.py  # Logging setup
├── desktop/               # Desktop application
│   ├── main.py            # Entry point
│   └── ui/                # Slint UI files
├── frontend/              # Vue.js web interface
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── composables/   # Vue composables
│   │   └── utils/         # Utilities
│   └── package.json
├── tests/                 # Test suite
├── documentation/         # MkDocs documentation
├── examples/              # Usage examples
└── pyproject.toml         # Project configuration
```

## Code Quality

### Linting and Formatting

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### Pre-commit Hooks

Install pre-commit hooks to run checks automatically:

```bash
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=savanty

# Run specific test
uv run pytest tests/test_solver.py::test_name
```

## Making Changes

### Creating a Branch

```bash
git checkout -b feature/your-feature-name
```

### Commit Messages

Follow conventional commits:

```
type(scope): description

feat(solver): add support for soft constraints
fix(cli): handle timeout errors gracefully
docs(api): update ProblemSolverResult documentation
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Push and open a PR
5. Address review feedback
6. Merge after approval

## Areas for Contribution

### Good First Issues

- Documentation improvements
- Additional examples
- Test coverage
- Error message improvements

### Feature Requests

- Additional LLM provider support
- New visualization types
- Performance optimizations
- UI/UX improvements

### Bug Fixes

Check the [issue tracker](https://github.com/skelf-research/savanty/issues) for open bugs.

## Documentation

### Building Docs Locally

```bash
cd documentation
pip install mkdocs-material
mkdocs serve
```

Open [http://localhost:8000](http://localhost:8000) to preview.

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep the audience in mind (users vs developers)

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Mock external dependencies (OpenAI API)

### Test Example

```python
from unittest.mock import patch
from savanty.solver import ProblemSolverResult

@patch('savanty.cli.solve_optimization_problem')
def test_solve_returns_solution(mock_solve):
    mock_solve.return_value = ProblemSolverResult(
        solution="assign(a, b)"
    )
    # Test code here
```

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Report issues responsibly

## Questions?

- Open a [GitHub Discussion](https://github.com/skelf-research/savanty/discussions)
- Check existing issues for similar questions
- Read the documentation first

Thank you for contributing!
