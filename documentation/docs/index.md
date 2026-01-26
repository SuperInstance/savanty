# Savanty

**Optimization for everyone. No coding required.**

Savanty is an AI-powered optimization solver that understands your planning and scheduling problems in plain English and delivers guaranteed correct solutions using Answer Set Programming (ASP).

```bash
# Try it now
uvx --from 'savanty[desktop]' savanty-desktop
```

## Why Savanty?

Traditional optimization requires mathematical expertise and programming skills. ChatGPT and Claude can understand your problems but often produce incorrect solutions. Savanty bridges this gap:

| Feature | ChatGPT/Claude | Savanty |
|---------|---------------|---------|
| Understands plain English | Yes | Yes |
| Guaranteed correct solutions | No | **Yes** |
| Shows its work (ASP code) | No | **Yes** |
| Handles complex constraints | Unreliable | **Reliable** |

## Key Features

- **Natural Language Input** - Describe your problem in plain English
- **Guaranteed Correct Solutions** - Mathematical proof that all constraints are satisfied
- **Multiple Interfaces** - Desktop app, web interface, CLI, or Python API
- **Transparent Logic** - See the ASP code that solves your problem

## Perfect For

- **Staff & Shift Scheduling** - Handle availability, skills, and cost constraints
- **Delivery & Route Planning** - Optimize routes with time windows and capacity limits
- **Appointment Booking** - Schedule appointments with equipment and skill requirements
- **Event Seating** - Arrange seating with relationship constraints
- **Resource Allocation** - Assign resources with skill matching requirements
- **University Timetabling** - Schedule courses with room and professor constraints

## Quick Example

```
Schedule 4 nurses (Alice, Bob, Carol, Dave) for 3 daily shifts
(morning, afternoon, night) over 7 days.

Constraints:
- Each shift needs exactly 1 nurse
- No nurse works more than 5 shifts per week
- No nurse works two consecutive shifts
- Alice can't work nights
```

Savanty will:

1. Ask clarifying questions if needed
2. Generate an ASP program encoding all constraints
3. Find a schedule that satisfies every requirement
4. Visualize the result in an easy-to-read format

## Get Started

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } **5 minute quickstart**

    ---

    Get your first optimization problem solved in under 5 minutes

    [:octicons-arrow-right-24: Getting Started](getting-started.md)

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install Savanty via pip, uvx, or from source

    [:octicons-arrow-right-24: Installation](installation.md)

-   :material-book-open-variant:{ .lg .middle } **Examples**

    ---

    Learn from real-world scheduling and planning examples

    [:octicons-arrow-right-24: Examples](examples/index.md)

-   :material-cog:{ .lg .middle } **API Reference**

    ---

    Integrate Savanty into your applications

    [:octicons-arrow-right-24: API Reference](reference/api.md)

</div>
