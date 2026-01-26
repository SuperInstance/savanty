"""Tests for the CLI interface."""

from unittest.mock import patch

from click.testing import CliRunner

from savanty.cli import main
from savanty.solver import ProblemSolverResult


def test_cli_help():
    """Test that the CLI provides help text."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Savanty CLI" in result.output


def test_cli_without_args():
    """Test that the CLI shows basic info when run without args."""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Savanty" in result.output
    assert "optimization problem solver" in result.output


@patch("savanty.cli.solve_optimization_problem")
def test_cli_with_problem(mock_solve):
    """Test that the CLI can solve a problem."""
    # Mock the solver to return a successful result
    mock_result = ProblemSolverResult(solution="Solution found")
    mock_solve.return_value = mock_result

    runner = CliRunner()
    result = runner.invoke(main, ["-p", "Minimize x+y subject to x>=0, y>=0"])

    assert result.exit_code == 0
    assert "Solution found" in result.output
    mock_solve.assert_called_once_with("Minimize x+y subject to x>=0, y>=0", "")


@patch("savanty.cli.solve_optimization_problem")
def test_cli_with_invalid_problem(mock_solve):
    """Test that the CLI handles invalid problems gracefully."""
    # Mock the solver to return an error result
    mock_result = ProblemSolverResult(error="Invalid problem")
    mock_solve.return_value = mock_result

    runner = CliRunner()
    result = runner.invoke(main, ["-p", "This is not a valid optimization problem"])

    assert result.exit_code == 1
    assert "Error:" in result.output


@patch("savanty.cli.solve_optimization_problem")
def test_cli_with_needs_info_problem(mock_solve):
    """Test that the CLI handles problems that need more info."""
    # Mock the solver to first return needs more info, then a solution
    mock_result1 = ProblemSolverResult(needs_more_info=True, questions=["What is the objective?"])
    mock_result2 = ProblemSolverResult(solution="Solution found")

    mock_solve.side_effect = [mock_result1, mock_result2]

    runner = CliRunner()
    result = runner.invoke(main, ["-p", "Solve something"], input="Minimize x\n")

    assert result.exit_code == 0
    assert "I need more information" in result.output
    assert "Solution found" in result.output
    assert mock_solve.call_count == 2
