# ASP Primer

Answer Set Programming (ASP) is a declarative programming paradigm for solving combinatorial search problems. This primer explains the basics so you can understand Savanty's generated code.

## What is ASP?

ASP is a form of logic programming where you:

1. **Declare** the problem structure (entities, relationships)
2. **Specify** constraints (rules that must hold)
3. **Let the solver** find solutions that satisfy everything

You describe *what* you want, not *how* to find it.

## Basic Syntax

### Facts

Facts are things that are true:

```prolog
% These are facts
nurse(alice).
nurse(bob).
shift(morning).
shift(evening).
```

### Rules

Rules derive new facts from existing ones:

```prolog
% If N is a nurse and S is a shift, then N can_work S
can_work(N, S) :- nurse(N), shift(S).
```

The `:-` means "if". Read right to left: "can_work(N, S) is true if nurse(N) and shift(S) are both true."

### Choice Rules

Choice rules allow the solver to decide:

```prolog
% For each nurse N and shift S, maybe assign N to S
{ assign(N, S) } :- nurse(N), shift(S).
```

The solver can choose to include or exclude each `assign(N, S)` fact.

### Constraints

Constraints forbid certain combinations:

```prolog
% It's forbidden for Alice to work the night shift
:- assign(alice, night).

% It's forbidden for the same nurse to work two shifts
:- assign(N, S1), assign(N, S2), S1 != S2.
```

A constraint with no head (just `:-`) means "this combination is forbidden."

### Cardinality Constraints

Limit how many things can be true:

```prolog
% Exactly 1 nurse per shift
1 { assign(N, S) : nurse(N) } 1 :- shift(S).

% At least 2 nurses per shift
2 { assign(N, S) : nurse(N) } :- shift(S).

% At most 3 shifts per nurse
{ assign(N, S) : shift(S) } 3 :- nurse(N).
```

### Aggregates

Count, sum, or compare:

```prolog
% Count shifts per nurse, forbid if > 5
:- nurse(N), #count { S : assign(N, S) } > 5.

% Sum of task durations per worker
total_work(W, T) :- worker(W), T = #sum { D : assign(W, Task), duration(Task, D) }.
```

### Optimization

Find the best solution:

```prolog
% Minimize total cost
#minimize { C : assign(W, T), cost(W, T, C) }.

% Maximize total value
#maximize { V : select(I), value(I, V) }.
```

## Complete Example

A simple nurse scheduling problem:

```prolog
% === FACTS ===
nurse(alice). nurse(bob). nurse(carol).
shift(morning). shift(evening).
day(monday). day(tuesday). day(wednesday).

% === DECISION VARIABLE ===
% For each nurse, day, and shift, we may assign them
{ assign(N, D, S) } :- nurse(N), day(D), shift(S).

% === CONSTRAINTS ===

% Each shift on each day needs exactly 1 nurse
1 { assign(N, D, S) : nurse(N) } 1 :- day(D), shift(S).

% No nurse works both shifts on the same day
:- assign(N, D, morning), assign(N, D, evening).

% Alice can't work evenings
:- assign(alice, D, evening).

% === SHOW ===
% Only display the assignments in the answer
#show assign/3.
```

## Reading Savanty's Output

When Savanty shows ASP code, you'll see:

1. **Facts section:** Your entities (nurses, shifts, tasks, etc.)
2. **Choice/Generation rules:** What decisions can be made
3. **Constraints:** What combinations are forbidden
4. **Optimization:** What to minimize/maximize (if any)
5. **Show directives:** What to display in the solution

## Common Patterns

### Exactly One Assignment

```prolog
1 { assign(X, Y) : option(Y) } 1 :- item(X).
```

### No Conflicts

```prolog
:- assign(X, T), assign(Y, T), X != Y, conflict(X, Y).
```

### Precedence

```prolog
:- assign(X, T1), assign(Y, T2), T1 >= T2, before(X, Y).
```

### Resource Capacity

```prolog
:- time(T), #sum { S : assign(J, T), size(J, S) } > Capacity, capacity(Capacity).
```

## Learn More

- [Potassco Guide](https://potassco.org/doc/start/) - Official ASP tutorial
- [ASP Core-2 Standard](https://www.mat.unical.it/aspcomp2013/ASPStandardization) - Language specification
- [Clingo Documentation](https://potassco.org/clingo/) - Solver details
