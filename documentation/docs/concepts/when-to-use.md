# When to Use Savanty

Savanty excels at certain types of problems but isn't the right tool for everything. This guide helps you understand when Savanty will help and when to use alternatives.

## Ideal Use Cases

### Scheduling and Timetabling

- Employee shift scheduling
- Course/exam timetabling
- Appointment booking
- Meeting room allocation
- Sports league fixtures

**Why Savanty works:** Discrete time slots, assignment constraints, conflict avoidance

### Assignment and Allocation

- Task-to-worker assignment
- Resource allocation
- Team formation
- Project staffing
- Equipment assignment

**Why Savanty works:** Matching problems with skill requirements and capacity limits

### Planning and Sequencing

- Delivery route planning
- Job shop scheduling
- Production sequencing
- Workflow ordering

**Why Savanty works:** Ordering constraints, precedence rules, resource conflicts

### Configuration and Selection

- Product configuration
- Menu planning
- Package selection
- Feature bundling

**Why Savanty works:** Compatibility constraints, required/forbidden combinations

### Logic Puzzles

- Sudoku, kakuro, nonograms
- Constraint satisfaction puzzles
- Combinatorial puzzles

**Why Savanty works:** Pure constraint satisfaction with discrete values

## Characteristics of Good Problems

Your problem is a good fit if it has:

| Characteristic | Example |
|----------------|---------|
| Discrete choices | Assign nurse to shift (not "how many hours") |
| Finite options | Choose from 5 workers (not infinite possibilities) |
| Clear constraints | "No more than 5 shifts" (not "be reasonable") |
| Combinatorial nature | Many ways to combine, need to find valid one |
| Binary decisions | Include/exclude, assign/don't assign |

## When NOT to Use Savanty

### Continuous Optimization

**Problem:** "Minimize f(x) = x² + 2x + 1 for real x"

**Why not:** Variables are continuous, needs calculus-based methods

**Use instead:** SciPy, CVXPY, or calculus

### Machine Learning

**Problem:** "Predict house prices from features"

**Why not:** Statistical/learning problem, not constraint satisfaction

**Use instead:** scikit-learn, TensorFlow, PyTorch

### Simple Calculations

**Problem:** "What's 15% of $200?"

**Why not:** Overkill - just arithmetic

**Use instead:** Calculator, spreadsheet, Python

### Real-Time Streaming

**Problem:** "Continuously assign incoming orders to drivers"

**Why not:** ASP solves static problems, not streams

**Use instead:** Online algorithms, event-driven systems

### Simulation

**Problem:** "Simulate traffic flow in a city"

**Why not:** Needs dynamic state evolution, not constraint solving

**Use instead:** SimPy, AnyLogic, custom simulation

### Large-Scale Numerical

**Problem:** "Solve this system of 10,000 linear equations"

**Why not:** Better solved with numerical linear algebra

**Use instead:** NumPy, SciPy, specialized solvers

## Edge Cases

### Optimization with Soft Constraints

**Can work:** "Minimize violations of preferences"

ASP supports optimization, but problems with many soft constraints may be slow.

### Graph Problems

**Can work:** Graph coloring, cliques, paths with constraints

**May be slow:** Very large graphs (1000s of nodes)

### Planning with Actions

**Can work:** Simple sequential planning

**Better alternatives:** PDDL planners for complex planning domains

## Quick Decision Guide

```
Is your problem about finding a combination/assignment?
├── No → Probably not a good fit
└── Yes → Are the choices discrete (finite options)?
    ├── No → Use continuous optimization (SciPy, CVXPY)
    └── Yes → Are there clear constraints to satisfy?
        ├── No → May need ML or heuristics
        └── Yes → Is the problem size reasonable (<1000 entities)?
            ├── No → May need specialized solver
            └── Yes → Savanty is a good fit! ✓
```

## What Savanty Suggests

When your problem isn't suitable, Savanty recommends alternatives:

| Problem Type | Suggested Tool |
|--------------|----------------|
| Continuous optimization | SciPy (`scipy.optimize`) |
| Convex optimization | CVXPY |
| Machine learning | scikit-learn |
| Data analysis | pandas |
| Simple math | Calculator/spreadsheet |

## Still Unsure?

Try Savanty! If your problem isn't suitable, Savanty will tell you and suggest alternatives. There's no harm in asking.
