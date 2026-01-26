# API Reference

Complete reference for Savanty's Python API.

## Main Function

### `solve_optimization_problem()`

```python
def solve_optimization_problem(
    problem_description: str,
    additional_info: str = None
) -> ProblemSolverResult
```

Solves an optimization problem described in natural language.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `problem_description` | `str` | Yes | The problem in plain English |
| `additional_info` | `str` | No | Answers to clarifying questions |

**Returns:** `ProblemSolverResult`

**Raises:**

- `ConfigurationError` - If `OPENAI_API_KEY` is not set

**Example:**

```python
from savanty import solve_optimization_problem

result = solve_optimization_problem(
    "Schedule 3 nurses for 2 shifts over 5 days",
    additional_info="Nurses are Alice, Bob, Carol"
)
```

## Result Class

### `ProblemSolverResult`

Container for solver results with multiple possible outcomes.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `solution` | `str \| None` | The solution if found |
| `asp_code` | `str \| None` | Generated ASP program |
| `visualization_html` | `str \| None` | HTML visualization |
| `needs_more_info` | `bool` | True if clarification needed |
| `questions` | `list[str]` | Clarifying questions to answer |
| `error` | `str \| None` | Error message if failed |
| `not_suitable` | `bool` | True if problem doesn't fit ASP |
| `suggested_tool` | `str \| None` | Alternative tool suggestion |
| `suitability_reason` | `str \| None` | Why problem isn't suitable |

**Result States:**

```python
# Success
if result.solution:
    print(result.solution)
    print(result.asp_code)

# Needs more info
elif result.needs_more_info:
    for q in result.questions:
        print(q)

# Not suitable
elif result.not_suitable:
    print(f"Use {result.suggested_tool} instead")
    print(result.suitability_reason)

# Error
elif result.error:
    print(f"Error: {result.error}")
```

## Exceptions

### `ConfigurationError`

```python
from savanty.solver import ConfigurationError
```

Raised when required configuration is missing or invalid.

**Common causes:**

- `OPENAI_API_KEY` environment variable not set
- Invalid API key format
- Network connectivity issues

**Example:**

```python
from savanty import solve_optimization_problem
from savanty.solver import ConfigurationError

try:
    result = solve_optimization_problem("...")
except ConfigurationError as e:
    print(f"Please set OPENAI_API_KEY: {e}")
```

## Module Exports

### `savanty`

The main package exports:

```python
from savanty import (
    solve_optimization_problem,  # Main solver function
    __version__,                  # Package version string
)
```

### `savanty.solver`

Lower-level access:

```python
from savanty.solver import (
    solve_optimization_problem,
    ProblemSolverResult,
    ConfigurationError,
    check_problem_suitability,
    generate_visualization,
)
```

## Type Hints

Full type annotations are available:

```python
from savanty.solver import ProblemSolverResult

def my_solver(problem: str) -> ProblemSolverResult:
    ...
```

## Thread Safety

- The solver function is **not** thread-safe by default
- For concurrent usage, use separate processes or async patterns
- The LLM client is initialized lazily on first use

## Async Usage

Wrap in `asyncio.to_thread` for async applications:

```python
import asyncio
from savanty import solve_optimization_problem

async def solve_async(problem: str):
    return await asyncio.to_thread(
        solve_optimization_problem, problem
    )
```
