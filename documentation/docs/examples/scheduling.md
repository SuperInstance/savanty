# Staff Scheduling

Schedule employees for shifts while respecting constraints like availability, skills, and workload limits.

## Basic Example

### Problem Description

```
Schedule 4 nurses (Alice, Bob, Carol, Dave) for 3 shifts
(morning, afternoon, night) over 7 days.

Constraints:
- Each shift needs exactly 1 nurse
- No nurse works more than 5 shifts per week
- No nurse works two consecutive shifts
- Alice cannot work night shifts
```

### What Savanty Does

1. **Parses** the problem to identify entities (nurses, shifts, days) and constraints
2. **Generates** an ASP program encoding the rules
3. **Solves** to find an assignment satisfying all constraints
4. **Visualizes** the schedule in a readable format

### Sample Solution

| Day | Morning | Afternoon | Night |
|-----|---------|-----------|-------|
| Mon | Alice | Bob | Carol |
| Tue | Dave | Alice | Bob |
| Wed | Carol | Dave | Alice |
| ... | ... | ... | ... |

### Generated ASP Code

```prolog
% Entities
nurse(alice). nurse(bob). nurse(carol). nurse(dave).
shift(morning). shift(afternoon). shift(night).
day(1..7).

% Assignment rule: exactly 1 nurse per shift per day
1 { assign(N, D, S) : nurse(N) } 1 :- day(D), shift(S).

% Constraint: max 5 shifts per nurse
:- nurse(N), #count { D,S : assign(N, D, S) } > 5.

% Constraint: no consecutive shifts
consecutive(morning, afternoon).
consecutive(afternoon, night).
:- assign(N, D, S1), assign(N, D, S2), consecutive(S1, S2).

% Constraint: Alice no nights
:- assign(alice, D, night).
```

## Advanced Example: Hospital Ward

### Problem Description

```
Schedule nurses for a hospital ward with the following requirements:

Staff:
- 6 nurses: Alice (senior), Bob (senior), Carol, Dave, Eve, Frank
- Senior nurses have 5+ years experience

Shifts:
- Day shift: 7am-3pm
- Evening shift: 3pm-11pm
- Night shift: 11pm-7am

Rules:
1. Each shift needs exactly 2 nurses
2. At least 1 senior nurse must be on each shift
3. No nurse works more than 40 hours per week (5 shifts)
4. Minimum 8 hours between shifts for each nurse
5. Carol and Dave prefer not to work together (soft constraint)
6. Weekend shifts (Sat/Sun) pay 1.5x - minimize weekend coverage cost

Schedule for 2 weeks (14 days).
```

### Key Constraints Encoded

**Hard Constraints:**

- Shift coverage (exactly 2 nurses)
- Senior nurse requirement
- Maximum hours
- Rest period between shifts

**Soft Constraints (Optimization):**

- Minimize Carol-Dave pairings
- Minimize weekend costs

### Sample Output

The solver finds a schedule that:

- Covers all shifts with 2 nurses each
- Ensures senior coverage on every shift
- Respects all rest and hour limits
- Minimizes the soft constraint violations

## Variations

### Part-Time Workers

```
Workers:
- Full-time: Alice, Bob, Carol (max 40 hours/week)
- Part-time: Dave, Eve (max 20 hours/week)

Schedule all workers fairly while respecting their hour limits.
```

### Skill-Based Scheduling

```
Workers and skills:
- Alice: reception, billing
- Bob: reception, technical support
- Carol: billing, technical support

Shifts need:
- Morning: 1 reception, 1 technical support
- Afternoon: 1 billing, 1 reception
- Evening: 1 technical support

Assign workers to shifts matching required skills.
```

### Rotating Schedules

```
Create a 4-week rotating schedule where:
- Each nurse works the same pattern each week
- Pattern rotates through all shifts fairly
- No permanent night shift assignments
```

## Tips

1. **Define time periods clearly** - "7 days" vs "Monday through Sunday"
2. **Specify shift lengths** if relevant for hour calculations
3. **Distinguish hard vs soft constraints** - must-have vs nice-to-have
4. **Name your workers** for clearer output
