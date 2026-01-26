# Route Planning

Optimize delivery routes and service visits with time windows, capacity constraints, and distance minimization.

## Basic Example

### Problem Description

```
Plan deliveries for a bakery with one delivery van.

Locations:
- Bakery (start/end point)
- Cafe A: needs delivery by 9am
- Restaurant B: needs delivery by 10am
- Hotel C: needs delivery between 8am-11am
- Office D: needs delivery by 9:30am

Travel times (minutes):
- Bakery to A: 15
- Bakery to B: 20
- Bakery to C: 25
- Bakery to D: 10
- A to B: 10
- A to C: 15
- A to D: 20
- B to C: 8
- B to D: 15
- C to D: 12

Van leaves bakery at 7:30am.
Find a route that meets all delivery windows.
```

### What Savanty Does

1. **Identifies** all locations and time windows
2. **Encodes** travel times and constraints
3. **Finds** a feasible route order
4. **Calculates** arrival times at each stop

### Sample Solution

```
Route: Bakery -> D -> A -> B -> C -> Bakery
- Leave Bakery: 7:30am
- Arrive D: 7:40am (deadline: 9:30am) ✓
- Arrive A: 8:00am (deadline: 9:00am) ✓
- Arrive B: 8:10am (deadline: 10:00am) ✓
- Arrive C: 8:18am (window: 8am-11am) ✓
- Return Bakery: 8:43am
```

## Advanced Example: Multi-Vehicle Fleet

### Problem Description

```
Plan deliveries for a distribution company.

Fleet:
- Van 1: capacity 100 units
- Van 2: capacity 150 units
- Van 3: capacity 80 units

Deliveries needed:
- Customer A: 40 units, 9am-12pm window
- Customer B: 60 units, 10am-2pm window
- Customer C: 30 units, 8am-10am window
- Customer D: 50 units, 11am-3pm window
- Customer E: 45 units, 9am-1pm window
- Customer F: 35 units, 2pm-5pm window

Depot opens at 7am. All vans must return by 6pm.
Minimize total distance traveled.

Distance matrix (km):
[Depot to each customer and between customers]
```

### Key Constraints

**Capacity:** Each route's total delivery volume ≤ van capacity

**Time Windows:** Arrive within customer's specified window

**Fleet:** Each van makes one route starting/ending at depot

**Objective:** Minimize total kilometers driven

## Variations

### With Priorities

```
Deliveries with priority levels:
- Priority 1 (must deliver today): Customers A, C
- Priority 2 (preferred today): Customers B, D
- Priority 3 (can wait): Customers E, F

Deliver all Priority 1, as many Priority 2 as possible.
```

### Service Time

```
Each delivery takes:
- Small package: 5 minutes
- Large package: 15 minutes
- Pallet: 30 minutes

Include service time when calculating arrival at next stop.
```

### Return Trips

```
Some customers have pickups:
- Customer A: deliver 20 units, pick up 10 units
- Customer B: deliver 30 units, pick up 25 units

Ensure van capacity isn't exceeded at any point in the route.
```

## Tips

1. **Specify time format** - 24-hour or AM/PM
2. **Include travel time units** - minutes, hours
3. **Define the objective** - minimize time, distance, or vehicles used
4. **Clarify constraints** - hard deadlines vs. preferences
