#!/usr/bin/env python3
"""
Basic usage examples for Savanty optimization problem solver.
"""

from savanty.solver import solve_optimization_problem


def example_task_scheduling():
    """Example of a task scheduling problem."""
    print("=== Task Scheduling Problem ===")

    problem_description = """
    We have a task scheduling problem. Each task has a name, duration, and priority.
    We need to schedule tasks within a maximum time of 10 units.
    Tasks cannot overlap.
    We want to maximize the total priority of scheduled tasks.

    Available tasks are:
    Task1: duration 3, priority 5
    Task2: duration 2, priority 3
    Task3: duration 4, priority 7
    Task4: duration 1, priority 2
    """

    result = solve_optimization_problem(problem_description)

    if result.needs_more_info:
        print("Please provide more information:")
        for question in result.questions:
            print(f"- {question}")
    elif result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Solution: {result.solution}")


def example_knapsack():
    """Example of a knapsack problem."""
    print("\n=== Knapsack Problem ===")

    problem_description = """
    Knapsack with capacity 10.
    Item1 (weight 5, value 10),
    Item2 (weight 4, value 7),
    Item3 (weight 6, value 12),
    Item4 (weight 2, value 3).
    Maximize value without exceeding capacity.
    """

    result = solve_optimization_problem(problem_description)

    if result.needs_more_info:
        print("Please provide more information:")
        for question in result.questions:
            print(f"- {question}")
    elif result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Solution: {result.solution}")


if __name__ == "__main__":
    # Run examples
    example_task_scheduling()
    example_knapsack()
