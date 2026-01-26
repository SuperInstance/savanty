# Savanty

[![PyPI version](https://img.shields.io/pypi/v/savanty.svg)](https://pypi.org/project/savanty/)
[![Python Versions](https://img.shields.io/pypi/pyversions/savanty.svg)](https://pypi.org/project/savanty/)
[![CI](https://github.com/skelf-research/savanty/actions/workflows/ci.yml/badge.svg)](https://github.com/skelf-research/savanty/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Natural language to constraint solver. Describe optimization problems in English, get mathematically guaranteed solutions.**

Savanty combines LLM understanding with Answer Set Programming (ASP) to solve scheduling, allocation, and planning problems. The LLM translates your problem into formal constraints; the solver guarantees correctness.

## Quick Start

```bash
pip install savanty
export OPENAI_API_KEY=your_key_here
```

### Python API

```python
from savanty import solve_optimization_problem

result = solve_optimization_problem("""
    Schedule 4 nurses (Alice, Bob, Carol, Dave) for morning/evening shifts
    over 5 days. Each shift needs 1 nurse. Max 4 shifts per person.
""")

print(result.solution)      # The assignment
print(result.asp_code)      # Generated ASP (for debugging)
```

### CLI

```bash
savanty -p "Assign 5 tasks to 3 workers, balance workload"
```

### Web Server

```bash
savanty --web  # REST API at http://localhost:8000
```

## Installation

```bash
# Core package
pip install savanty

# With desktop GUI
pip install 'savanty[desktop]'

# Development
pip install 'savanty[dev]'
```

**Requirements:** Python 3.10+ and an [OpenAI API key](https://platform.openai.com/api-keys)

## API Reference

### `solve_optimization_problem(problem, additional_info=None)`

Returns a `ProblemSolverResult` with:

| Attribute | Type | Description |
|-----------|------|-------------|
| `solution` | `str` | The solution if found |
| `asp_code` | `str` | Generated ASP program |
| `visualization_html` | `str` | HTML visualization |
| `needs_more_info` | `bool` | True if clarification needed |
| `questions` | `list[str]` | Clarifying questions |
| `error` | `str` | Error message if failed |
| `not_suitable` | `bool` | True if problem doesn't fit ASP |

### Handling Results

```python
result = solve_optimization_problem("Schedule my team")

if result.needs_more_info:
    # Solver needs clarification
    print("Questions:", result.questions)
    # Re-call with answers
    result = solve_optimization_problem(
        "Schedule my team",
        additional_info="5 people, morning/evening shifts, 7 days"
    )

elif result.not_suitable:
    # Wrong tool for this problem
    print(f"Try: {result.suggested_tool}")

elif result.error:
    print(f"Error: {result.error}")

else:
    # Success
    print(result.solution)
```

## REST API

```bash
savanty --web --port 8000
```

### Endpoints

**POST /solve**
```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "Assign 3 tasks to 2 workers"}'
```

**GET /health** — Health check
**GET /ready** — Readiness check (verifies API key)

OpenAPI docs at `/docs` when server is running.

## What It Solves

Savanty excels at **discrete constraint satisfaction**:

| Good Fit | Not a Good Fit |
|----------|----------------|
| Shift scheduling | Continuous optimization |
| Task assignment | Machine learning |
| Route planning | Statistical analysis |
| Resource allocation | Real-time streaming |
| Seating arrangements | Simple arithmetic |
| Timetabling | |

When a problem doesn't fit, Savanty tells you and suggests alternatives (scipy, sklearn, etc.).

## How It Works

```
English description → LLM extracts constraints → ASP solver → Guaranteed solution
```

1. **LLM (GPT-4o)** parses your problem into entities, constraints, objectives
2. **Gap detection** identifies missing info and asks clarifying questions
3. **Code generation** produces Answer Set Programming (ASP) code
4. **Clingo solver** exhaustively searches for valid solutions
5. **Visualization** renders results as tables/charts

The key: LLMs understand language but hallucinate solutions. ASP solvers guarantee correctness but can't parse English. Savanty uses each for what it's good at.

## Configuration

```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional
export SAVANTY_LLM_MODEL=openai/gpt-4o    # Default model
export SAVANTY_PORT=8000                   # Web server port
export SAVANTY_LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
export SAVANTY_SOLVE_TIMEOUT=120           # Timeout in seconds
```

See [.env.example](.env.example) for all options.

## Development

```bash
git clone https://github.com/skelf-research/savanty.git
cd savanty
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check .
uv run ruff format .

# Run locally
uv run savanty --web
```

### Project Structure

```
savanty/
├── savanty/
│   ├── solver.py          # Core solver logic
│   ├── dspy_modules.py    # LLM prompts (DSPy signatures)
│   ├── cli.py             # CLI + FastAPI server
│   └── logging_config.py  # Logging setup
├── frontend/              # Vue.js web interface
├── desktop/               # Slint desktop app
├── tests/
└── documentation/         # MkDocs site
```

## Tech Stack

- **[Clingo](https://potassco.org/clingo/)** — ASP solver (correctness guarantee)
- **[DSPy](https://github.com/stanfordnlp/dspy)** — LLM orchestration
- **[FastAPI](https://fastapi.tiangolo.com/)** — REST API
- **[Vue.js](https://vuejs.org/)** — Web frontend
- **[Slint](https://slint.dev/)** — Desktop GUI

## License

MIT — see [LICENSE](LICENSE)

## Links

- [Documentation](https://docs.skelfresearch.com/savanty)
- [PyPI](https://pypi.org/project/savanty/)
- [GitHub](https://github.com/skelf-research/savanty)
- [Issues](https://github.com/skelf-research/savanty/issues)
