# Resource Allocation

Assign resources, tasks, or equipment to workers or time slots while balancing workload and respecting constraints.

## Basic Example

### Problem Description

```
Assign 5 support tickets to 3 agents.

Tickets:
- Ticket 1: billing issue, estimated 30 min
- Ticket 2: technical problem, estimated 60 min
- Ticket 3: account setup, estimated 20 min
- Ticket 4: technical problem, estimated 45 min
- Ticket 5: billing issue, estimated 25 min

Agents and skills:
- Alice: billing, account setup
- Bob: technical, billing
- Carol: technical, account setup

Rules:
- Each ticket assigned to exactly one agent
- Agent must have skill for ticket type
- Balance workload as evenly as possible
```

### Sample Solution

```
Alice: Ticket 1 (30 min), Ticket 3 (20 min) = 50 min
Bob: Ticket 2 (60 min), Ticket 5 (25 min) = 85 min
Carol: Ticket 4 (45 min) = 45 min
```

## Advanced Example: Project Assignment

### Problem Description

```
Assign team members to projects for the next quarter.

Team:
- Alice: senior developer, Python, JavaScript, available 40 hrs/week
- Bob: developer, Python, Java, available 40 hrs/week
- Carol: developer, JavaScript, React, available 30 hrs/week (part-time)
- Dave: junior developer, Python, available 40 hrs/week

Projects:
- Project Alpha: needs 80 hrs/week Python, 40 hrs/week JavaScript
- Project Beta: needs 60 hrs/week Java, 20 hrs/week Python
- Project Gamma: needs 50 hrs/week React, 30 hrs/week JavaScript

Constraints:
1. Each person works on at most 2 projects
2. Each project has at least 2 people assigned
3. Senior developers should not be on more than 1 project
4. Meet skill requirements for each project
5. Maximize project coverage while respecting availability
```

### Key Considerations

**Skill Matching:** Assignments must match required skills

**Capacity:** Don't over-allocate anyone's hours

**Coverage:** Meet minimum staffing per project

**Experience:** Balance senior/junior distribution

## Variations

### Equipment Allocation

```
Assign 4 machines to 6 jobs over the week.

Machines:
- Machine A: can do cutting, drilling
- Machine B: can do drilling, welding
- Machine C: can do cutting, welding, finishing
- Machine D: can do finishing

Jobs and requirements:
- Job 1: cutting (2 hours)
- Job 2: drilling (3 hours)
- Job 3: welding (4 hours)
- Job 4: finishing (2 hours)
- Job 5: cutting then finishing (3 hours total)
- Job 6: drilling then welding (5 hours total)

Minimize total machine idle time.
```

### Budget Allocation

```
Allocate $100,000 budget across 5 departments.

Departments and requests:
- Marketing: requests $35,000, minimum need $20,000
- Engineering: requests $45,000, minimum need $30,000
- Sales: requests $25,000, minimum need $15,000
- Support: requests $20,000, minimum need $10,000
- Admin: requests $15,000, minimum need $10,000

Rules:
- Total allocation must equal $100,000
- Meet all minimum needs
- Distribute remaining funds proportionally to requests
```

### Room Assignment

```
Assign 8 meetings to 3 conference rooms.

Rooms:
- Room A: capacity 10, has projector
- Room B: capacity 6, has whiteboard
- Room C: capacity 20, has projector and video conferencing

Meetings:
- Meeting 1: 8 people, needs projector, 9am-10am
- Meeting 2: 4 people, needs whiteboard, 9am-11am
- Meeting 3: 15 people, needs video conferencing, 10am-12pm
...

No room double-booked. All requirements met.
```

## Tips

1. **List all resources** with their capabilities
2. **Specify task requirements** clearly
3. **Define "fair" distribution** if balancing workload
4. **Distinguish hard constraints** from preferences
