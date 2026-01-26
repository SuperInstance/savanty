# Examples

Learn how to use Savanty through real-world optimization problems.

## Problem Categories

### [Staff Scheduling](scheduling.md)

Schedule employees for shifts with constraints like:

- Availability windows
- Skill requirements
- Maximum hours per week
- Consecutive shift limits

### [Route Planning](routing.md)

Optimize delivery and service routes with:

- Time windows
- Vehicle capacity
- Multiple stops
- Distance minimization

### [Resource Allocation](allocation.md)

Assign resources to tasks considering:

- Skills and qualifications
- Workload balancing
- Priority levels
- Dependencies

### [Event Seating](seating.md)

Arrange seating for events with:

- Relationship constraints (exes, feuding relatives)
- Accessibility requirements
- Group preferences
- Table capacities

### [Timetabling](timetabling.md)

Create schedules for courses or events:

- Room assignments
- Instructor availability
- Prerequisite ordering
- Conflict avoidance

### [Team Formation](team-formation.md)

Build teams with optimal composition:

- Skill coverage
- Leadership distribution
- Personality balance
- Experience levels

## Tips for Writing Problems

### Be Specific

Instead of:
> "I need to schedule workers"

Write:
> "Schedule 5 nurses (Alice, Bob, Carol, Dave, Eve) for morning, afternoon, and night shifts across Monday through Friday"

### List Constraints Clearly

Use bullet points or numbered lists:

```
Constraints:
1. Each shift needs exactly 2 nurses
2. No nurse works more than 4 shifts per week
3. No back-to-back shifts (night then morning)
4. Alice cannot work weekends
```

### Specify Objectives

Tell Savanty what "optimal" means:

- "Minimize total travel distance"
- "Maximize the number of tasks completed"
- "Balance workload evenly across workers"

### Provide Context

If terminology is domain-specific, explain it:

> "A 'split shift' means working morning and night but not afternoon on the same day. We want to minimize split shifts."
