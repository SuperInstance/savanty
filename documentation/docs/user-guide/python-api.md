# Python API

Integrate Savanty into your Python applications with the programmatic API.

## Installation

```bash
pip install savanty
```

## Basic Usage

```python
from savanty import solve_optimization_problem

result = solve_optimization_problem(
    "Schedule 3 workers for morning and evening shifts over 5 days"
)

if result.solution:
    print(result.solution)
elif result.needs_more_info:
    print("Questions:", result.questions)
elif result.error:
    print("Error:", result.error)
```

## API Reference

### `solve_optimization_problem()`

Main function for solving optimization problems.

```python
def solve_optimization_problem(
    problem_description: str,
    additional_info: str = None
) -> ProblemSolverResult
```

**Parameters:**

- `problem_description` - The problem in plain English
- `additional_info` - Optional answers to clarifying questions

**Returns:** `ProblemSolverResult` object

### `ProblemSolverResult`

Result object with the following attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `solution` | `str` | The solution if found |
| `asp_code` | `str` | Generated ASP program |
| `visualization_html` | `str` | HTML visualization |
| `needs_more_info` | `bool` | Whether questions are needed |
| `questions` | `list[str]` | Clarifying questions |
| `error` | `str` | Error message if failed |
| `not_suitable` | `bool` | Whether problem suits ASP |
| `suggested_tool` | `str` | Alternative tool suggestion |
| `suitability_reason` | `str` | Why not suitable |

## Handling Different Results

### Successful Solution

```python
result = solve_optimization_problem("Assign 3 tasks to 2 workers")

if result.solution:
    print("Solution found!")
    print(result.solution)
    print("\nASP Code:")
    print(result.asp_code)
```

### Needs More Information

```python
result = solve_optimization_problem("Schedule nurses")

if result.needs_more_info:
    print("Please answer these questions:")
    for q in result.questions:
        print(f"  - {q}")

    # Provide answers and retry
    answers = "4 nurses, 3 shifts, 7 days"
    result = solve_optimization_problem(
        "Schedule nurses",
        additional_info=answers
    )
```

### Not Suitable for ASP

```python
result = solve_optimization_problem("Calculate the derivative of x^2")

if result.not_suitable:
    print(f"Try: {result.suggested_tool}")
    print(f"Reason: {result.suitability_reason}")
```

### Error Handling

```python
result = solve_optimization_problem("Invalid problem")

if result.error:
    print(f"Error: {result.error}")
```

## Complete Example

```python
from savanty import solve_optimization_problem

def solve_with_followup(problem: str) -> str:
    """Solve a problem, handling follow-up questions."""
    result = solve_optimization_problem(problem)

    # Handle problems not suitable for ASP
    if result.not_suitable:
        return f"Not suitable: {result.suitability_reason}"

    # Handle follow-up questions (simplified)
    if result.needs_more_info:
        # In real app, you'd prompt the user
        additional = input("Provide more info: ")
        result = solve_optimization_problem(problem, additional)

    # Handle errors
    if result.error:
        return f"Error: {result.error}"

    # Return solution
    return result.solution

# Usage
solution = solve_with_followup("""
    Schedule 4 nurses for hospital shifts.
    Morning, afternoon, and night shifts.
    7 days, each shift needs 1 nurse.
    No one works more than 5 shifts.
""")

print(solution)
```

## Integration with FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from savanty import solve_optimization_problem

app = FastAPI()

class ProblemRequest(BaseModel):
    description: str
    additional_info: str = ""

@app.post("/solve")
async def solve(request: ProblemRequest):
    result = solve_optimization_problem(
        request.description,
        request.additional_info
    )

    if result.error:
        raise HTTPException(400, result.error)

    return {
        "solution": result.solution,
        "asp_code": result.asp_code,
        "visualization": result.visualization_html,
    }
```

## Configuration

Set environment variables before importing:

```python
import os
os.environ["OPENAI_API_KEY"] = "your_key_here"
os.environ["SAVANTY_LLM_MODEL"] = "openai/gpt-4o"

from savanty import solve_optimization_problem
```

## Error Types

The API may raise:

- `ConfigurationError` - Missing API key or invalid config
- `ValueError` - Invalid input or parsing failure

```python
from savanty.solver import ConfigurationError

try:
    result = solve_optimization_problem("...")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```
