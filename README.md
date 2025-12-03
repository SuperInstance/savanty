# Savanty

[![PyPI version](https://badge.fury.io/py/savanty.svg)](https://badge.fury.io/py/savanty)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Optimization for everyone. No coding required.**

Describe your scheduling, planning, or allocation problem in plain English. Savanty figures out the constraints and delivers a *guaranteed* correct solution—not a guess, not an approximation, but a mathematically proven answer.

## Try It Now

```bash
# One command, no installation needed
uvx --from 'savanty[desktop]' savanty-desktop
```

That's it. A desktop app opens where you can describe your problem and get solutions.

> **Requires:** Python 3.10+ and an [OpenAI API key](https://platform.openai.com/api-keys) (`export OPENAI_API_KEY=your_key`)

## What Can Savanty Solve?

Real problems with hard constraints that can't be violated:

### Staff & Shift Scheduling
> "Schedule 5 retail employees for next week. Maria is a student (max 25 hrs). Jake can work any day. Aisha is team lead and must be present daily. Weekend shifts cost 1.5x—minimize those."

Savanty handles availability, labor rules, skill requirements, and cost optimization.

### Delivery & Route Planning
> "Plan routes for 2 bakery vans. 7 orders with specific time windows. Hospital needs delivery by 7am, cafe between 8-9am. Each van holds 50 boxes max."

Time windows, vehicle capacity, travel times—all constraints are guaranteed satisfied.

### Appointment Booking
> "Schedule 9 salon appointments across 3 stylists. Anna does cuts and color. Carla is senior (highlights only). Mrs. Chen needs highlights before 1pm. The twins need cuts at the same time but different stylists."

Equipment constraints, stylist skills, customer preferences—no double-bookings, ever.

### Event & Seating Planning
> "Wedding reception seating for 42 guests at 6 tables. Keep feuding aunts apart. Grandma needs accessible seating. College friends want to sit together but Jake and Emma are exes."

Relationship constraints, accessibility needs, group preferences—all balanced automatically.

### Team & Resource Allocation
> "Form 3 engineering teams of 4 from 12 people. Each team needs leadership, frontend, and backend skills. Alice and Bob work well together. Carol and Frank don't."

Skill matching, interpersonal dynamics, balanced expertise distribution.

### Sports League Scheduling
> "8-week youth soccer schedule for 6 teams. Round-robin format. Rockets and Comets have siblings—never same time slot. Lightning coach can't do 9am games."

Fair matchups, family logistics, venue availability—all respected.

---

## Why Not Just Use ChatGPT?

LLMs are great at *understanding* your problem. They're terrible at *solving* it correctly.

Ask ChatGPT to create a nurse schedule and it'll give you something plausible-looking. But check carefully: a nurse works 7 days straight, two people are scheduled for the same slot, or a constraint you specified is quietly ignored.

**Savanty is different:**

| | ChatGPT / Claude | Savanty |
|---|---|---|
| Understands your problem | ✅ | ✅ |
| Generates valid solutions | ❌ Often hallucinates | ✅ Mathematically proven |
| Respects ALL constraints | ❌ Quietly violates | ✅ Guaranteed |
| Finds optimal answer | ❌ Guesses | ✅ Provably best |
| Shows the logic | ❌ Black box | ✅ Full transparency |

Savanty uses an LLM to *understand* your problem, then hands it to a constraint solver (Clingo) that *guarantees* correctness. Best of both worlds.

---

## Installation Options

### Desktop App (Recommended)

```bash
# Run directly (no install, downloads temporarily)
uvx --from 'savanty[desktop]' savanty-desktop

# Or install as a tool for regular use
uv tool install 'savanty[desktop]'
savanty-desktop

# Or with pip
pip install 'savanty[desktop]'
savanty-desktop
```

### Web Interface

```bash
pip install savanty
savanty --web
# Open http://localhost:8000
```

### Command Line

```bash
pip install savanty
savanty -p "Schedule 4 nurses across 3 daily shifts for a week. Night shifts need 2 people."
```

### Python API

```python
from savanty import solve_optimization_problem

result = solve_optimization_problem("""
    Assign 20 support tickets to 5 agents.
    Senior agents handle escalations.
    Balance workload across the team.
""")

if result.needs_more_info:
    for question in result.questions:
        print(question)
else:
    print(result.solution)
```

---

## How It Works

```
You describe          Savanty asks           Solver finds           You get
your problem    →     clarifying       →     guaranteed       →     visual
in English            questions              optimal solution       results
```

Under the hood:

1. **LLM Understanding** — GPT-4 extracts entities, constraints, and goals from your description
2. **Smart Clarification** — Agent identifies missing info and asks targeted questions
3. **Code Generation** — Automatically generates Answer Set Programming (ASP) code
4. **Constraint Solving** — Clingo solver explores the solution space exhaustively
5. **Visualization** — Results rendered as schedules, charts, and tables

The key insight: LLMs are great at translation (English → formal logic) but bad at search (finding valid solutions). Savanty uses each tool for what it's good at.

---

## Configuration

```bash
# Required: OpenAI API key
export OPENAI_API_KEY=your_key_here

# Optional: Change model (default: gpt-4o)
export SAVANTY_LLM_MODEL=gpt-4-turbo

# Optional: Change web port (default: 8000)
export SAVANTY_PORT=3000
```

---

## What Savanty Is (and Isn't) Good At

### Perfect for:
- **Scheduling** — shifts, appointments, meetings, courses, sports leagues
- **Allocation** — tasks, resources, rooms, equipment, budgets
- **Assignment** — teams, seating charts, delivery routes
- **Planning** — meals, events, itineraries, production runs

### Not the right tool for:
- **Continuous optimization** — use scipy or cvxpy for calculus-based problems
- **Machine learning** — use sklearn/pytorch for prediction tasks
- **Simple arithmetic** — use a spreadsheet for basic calculations
- **Real-time systems** — Savanty needs a few seconds to think

When you try a problem that's better suited for another tool, Savanty will tell you and suggest alternatives.

---

## For Developers

### Python API

```python
from savanty import solve_optimization_problem

# Basic usage
result = solve_optimization_problem("Your problem description")

# With follow-up information
result = solve_optimization_problem(
    "Schedule my team for next week",
    additional_info="5 people, 3 shifts per day, max 5 shifts each"
)

# Result object
result.solution           # The answer
result.asp_code           # Generated logic program (for debugging)
result.visualization_html # Ready-to-embed HTML
result.needs_more_info    # True if clarification needed
result.questions          # List of clarifying questions
result.error              # Error message if failed
```

### FastAPI Integration

```python
from fastapi import FastAPI
from savanty import solve_optimization_problem

app = FastAPI()

@app.post("/solve")
async def solve(problem: str, context: str = ""):
    result = solve_optimization_problem(problem, additional_info=context)
    return {
        "status": "needs_info" if result.needs_more_info else "solved",
        "questions": result.questions,
        "solution": result.solution,
        "visualization": result.visualization_html
    }
```

### Project Structure

```
savanty/
├── savanty/              # Core Python package
│   ├── solver.py         # Main solver + visualization
│   ├── dspy_modules.py   # LLM interaction (DSPy)
│   └── cli.py            # CLI + FastAPI server
├── desktop/              # Native desktop app
│   ├── main.py           # Python entry point
│   └── ui/app.slint      # Slint UI definition
├── frontend/             # Web interface (Vue.js)
│   └── src/
└── pyproject.toml
```

### Development Setup

```bash
# Clone and install
git clone https://github.com/terraprompt/savanty.git
cd savanty
uv sync

# Run backend
uv run savanty --web

# Run frontend (separate terminal, hot reload)
cd frontend && npm install && npm run dev

# Run desktop
uv sync --extra desktop
uv run python desktop/main.py
```

---

## Technical Stack

- **[Clingo](https://potassco.org/clingo/)** — Answer Set Programming solver (the mathematical engine)
- **[DSPy](https://github.com/stanfordnlp/dspy)** — LLM orchestration framework
- **[Slint](https://slint.dev/)** — Native desktop UI toolkit
- **[Vue.js](https://vuejs.org/)** — Web interface
- **[FastAPI](https://fastapi.tiangolo.com/)** — API server

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and commit
4. Open a PR

## License

MIT License — see [LICENSE](LICENSE)

## Links

- **PyPI**: https://pypi.org/project/savanty/
- **GitHub**: https://github.com/terraprompt/savanty
- **Issues**: https://github.com/terraprompt/savanty/issues
