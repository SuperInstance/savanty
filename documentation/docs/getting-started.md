# Getting Started

Get your first optimization problem solved in under 5 minutes.

## Prerequisites

- Python 3.10 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## Quick Start

### 1. Set your API key

```bash
export OPENAI_API_KEY=your_api_key_here
```

### 2. Choose your interface

=== "Desktop App (Recommended)"

    The desktop app provides the best experience with a visual interface.

    ```bash
    uvx --from 'savanty[desktop]' savanty-desktop
    ```

    This downloads and runs Savanty without permanent installation.

=== "Web Interface"

    Start a local web server with a browser-based interface.

    ```bash
    pip install savanty
    savanty --web
    ```

    Then open [http://localhost:8000](http://localhost:8000) in your browser.

=== "Command Line"

    Solve problems directly from your terminal.

    ```bash
    pip install savanty
    savanty -p "Schedule 3 employees for 2 shifts each day for 5 days"
    ```

=== "Python API"

    Integrate Savanty into your Python applications.

    ```python
    from savanty import solve_optimization_problem

    result = solve_optimization_problem(
        "Assign 5 tasks to 3 workers, each task takes 1-3 hours"
    )

    if result.solution:
        print(result.solution)
    ```

### 3. Describe your problem

Enter your optimization problem in plain English. For example:

```
I need to schedule 4 nurses (Alice, Bob, Carol, Dave) for morning,
afternoon, and night shifts over the next week.

Rules:
- Each shift must have exactly one nurse
- No one can work more than 5 shifts per week
- No back-to-back shifts for anyone
- Alice cannot work night shifts
```

### 4. Answer clarifying questions

If Savanty needs more information, it will ask targeted questions:

- "How many days are in the schedule?"
- "Can a nurse work the same shift type on consecutive days?"

Provide the answers, and Savanty will continue solving.

### 5. Get your solution

Savanty returns:

- **Solution** - The optimal assignment that satisfies all constraints
- **ASP Code** - The logic program used to find the solution
- **Visualization** - A visual representation of the result

## Understanding the Results

### Solution

The raw output showing which assignments were made:

```
assign(alice, monday, morning)
assign(bob, monday, afternoon)
assign(carol, monday, night)
...
```

### ASP Code

The Answer Set Programming code that encodes your problem:

```prolog
% Facts
nurse(alice). nurse(bob). nurse(carol). nurse(dave).
shift(morning). shift(afternoon). shift(night).
day(monday). day(tuesday). ...

% Rules
1 { assign(N, D, S) : nurse(N) } 1 :- day(D), shift(S).

% Constraints
:- assign(N, D, S1), assign(N, D, S2), S1 != S2.
```

### Visualization

A formatted display of your solution, such as a schedule table or assignment chart.

## Next Steps

- [Installation Guide](installation.md) - Permanent installation options
- [User Guide](user-guide/index.md) - Learn all interface options
- [Examples](examples/index.md) - See more problem types
- [When to Use Savanty](concepts/when-to-use.md) - Understand problem suitability
