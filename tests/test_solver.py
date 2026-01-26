"""Tests for the Savanty optimization solver."""

from unittest.mock import MagicMock, patch

import pytest

from savanty.solver import (
    ProblemSolverResult,
    generate_asp_program,
    generate_clorm_predicates,
    solve_optimization_problem,
    validate_and_parse_problem,
)


@patch("savanty.solver._ensure_lm_configured")
@patch("savanty.solver.InteractiveProblemSolver")
def test_validate_and_parse_problem(mock_problem_solver, mock_ensure_lm):
    """Test validating and parsing an optimization problem."""
    # Mock the InteractiveProblemSolver forward method
    mock_result = MagicMock()
    mock_result.program.program_components = '{"predicates": [{"name": "Variable", "fields": {"name": "ConstantField", "value": "IntegerField"}}], "facts": ["variable(x)", "variable(y)"], "constraints": ["x >= 0", "y >= 0", "x + y <= 10"], "optimize": "minimize x + y"}'
    mock_result.needs_more_info = False

    mock_instance = MagicMock()
    mock_instance.forward.return_value = mock_result
    mock_problem_solver.return_value = mock_instance

    description = "Minimize x+y subject to x>=0, y>=0, x+y<=10"
    result = validate_and_parse_problem(description)

    # Check that we get the expected structure
    assert "predicates" in result
    assert "facts" in result
    assert "constraints" in result
    assert "optimize" in result


@patch("savanty.solver._ensure_lm_configured")
@patch("savanty.solver.InteractiveProblemSolver")
def test_validate_and_parse_problem_needs_info(mock_problem_solver, mock_ensure_lm):
    """Test validating and parsing an optimization problem that needs more info."""
    # Mock the InteractiveProblemSolver forward method for a problem that needs more info
    mock_result = MagicMock()
    mock_result.needs_more_info = True
    mock_result.questions = ["What is the objective function?", "What are the constraints?"]

    mock_instance = MagicMock()
    mock_instance.forward.return_value = mock_result
    mock_problem_solver.return_value = mock_instance

    description = "Solve some problem"

    # This should raise a ValueError with the questions
    with pytest.raises(ValueError) as exc_info:
        validate_and_parse_problem(description)

    assert "NEEDS_MORE_INFO:" in str(exc_info.value)


def test_generate_clorm_predicates():
    """Test generating Clorm predicates."""
    predicates = [
        {
            "name": "Task",
            "fields": {
                "name": "ConstantField",
                "duration": "IntegerField",
                "priority": "IntegerField",
            },
        }
    ]

    code = generate_clorm_predicates(predicates)
    assert "class Task(Predicate):" in code
    assert "name = ConstantField" in code
    assert "duration = IntegerField" in code
    assert "priority = IntegerField" in code


def test_generate_asp_program():
    """Test generating ASP program."""
    problem_info = {
        "predicates": [],
        "facts": [],
        "constraints": ["{task(T)} :- task(T)."],
        "optimize": "#maximize {P,T : task(T), priority(T,P)}.",
    }

    asp_program = generate_asp_program(problem_info)
    assert "{task(T)} :- task(T)." in asp_program
    assert "#maximize {P,T : task(T), priority(T,P)}." in asp_program
    assert "#show." in asp_program


@patch("savanty.solver.validate_and_parse_problem")
def test_solve_optimization_problem_success(mock_validate):
    """Test solving an optimization problem successfully."""
    # Mock the validation to return a valid problem structure
    mock_validate.return_value = {
        "predicates": [
            {"name": "Variable", "fields": {"name": "ConstantField", "value": "IntegerField"}}
        ],
        "facts": ["variable(x)"],
        "constraints": ["x >= 0"],
        "optimize": "minimize x",
    }

    # We'll mock the exec and globals functions to avoid ASP execution
    with patch("savanty.solver.exec"), patch("savanty.solver.globals", return_value={}):
        result = solve_optimization_problem("Minimize x subject to x>=0")
        assert isinstance(result, ProblemSolverResult)
        assert not result.needs_more_info
        # We expect an error because we mocked the ASP execution
        assert result.error is not None


@patch("savanty.solver.check_problem_suitability")
@patch("savanty.solver.validate_and_parse_problem")
def test_solve_optimization_problem_needs_info(mock_validate, mock_suitability):
    """Test solving an optimization problem that needs more info."""
    # Mock suitability check to pass
    mock_suitability.return_value = {"is_suitable": "yes"}

    # Mock the validation to raise the needs more info error
    mock_validate.side_effect = ValueError('NEEDS_MORE_INFO:["What is the objective function?"]')

    result = solve_optimization_problem("Solve some problem")
    assert isinstance(result, ProblemSolverResult)
    assert result.needs_more_info
    assert len(result.questions) > 0
    assert "What is the objective function?" in result.questions
