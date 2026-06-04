"""Tests for the Savanty solver: oracle, ASP runtime, failure taxonomy, repair loop.

These tests run entirely offline (no LLM); the LLM-facing steps are mocked.
"""

from unittest.mock import patch

import pytest

from benchmark.reference import ground_truth
from benchmark.verify import verify
from savanty.solver import (
    ProblemSolverResult,
    assemble_program,
    compile_and_solve,
    minimal_unsat_core,
    solve_optimization_problem,
)


def _triangle(k):
    colors = [f"c{i}" for i in range(1, k + 1)]
    return {
        "facts": [f"node(n{i})." for i in (1, 2, 3)] + [f"color({c})." for c in colors],
        "rules": [
            "1 { assign(N,C) : color(C) } 1 :- node(N).",
            ":- assign(n1,C), assign(n2,C).",
            ":- assign(n2,C), assign(n3,C).",
            ":- assign(n1,C), assign(n3,C).",
        ],
        "optimize": "",
    }


# --- oracle -------------------------------------------------------------------------


def test_oracle_knapsack():
    spec = {
        "variables": ["i1", "i2"],
        "domains": {"i1": ["in", "out"], "i2": ["in", "out"]},
        "constraints": [
            {"type": "weighted_capacity", "weights": {"i1": 5, "i2": 6}, "selected_value": "in", "bound": 10}
        ],
        "objective": {"sense": "max", "weights": {"i1": {"in": 10, "out": 0}, "i2": {"in": 12, "out": 0}}},
    }
    good = verify(spec, {"i1": "out", "i2": "in"})
    assert good.feasible and good.csr == 1.0 and good.objective == 12
    bad = verify(spec, {"i1": "in", "i2": "in"})  # weight 11 > 10
    assert not bad.feasible and bad.csr < 1.0


# --- ASP runtime + failure taxonomy -------------------------------------------------


def test_compile_ok():
    out = compile_and_solve(_triangle(3))
    assert out.failure_type == "ok"
    assert len(out.assignment) == 3
    assert set(out.assignment) == {"n1", "n2", "n3"}


def test_compile_unsat_and_minimal_core():
    out = compile_and_solve(_triangle(2))
    assert out.failure_type == "unsat"
    # K3 is minimally non-2-colourable: all three edge constraints are needed.
    assert len(out.unsat_core) == 3


def test_minimal_core_is_minimal():
    # A redundant constraint must NOT appear in the minimal core.
    comp = _triangle(2)
    comp["rules"].append(":- assign(n1,c1), assign(n1,c1).")  # trivially redundant
    core = minimal_unsat_core(comp)
    assert len(core) == 3


def test_compile_syntax_error():
    out = compile_and_solve({"facts": ["node(n1)."], "rules": ["this :: not asp -"], "optimize": ""})
    assert out.failure_type == "syntax_error"
    assert out.solver_feedback


def test_compile_empty():
    out = compile_and_solve({"facts": ["foo(1)."], "rules": ["bar(X) :- foo(X)."], "optimize": ""})
    assert out.failure_type == "empty"


def test_assemble_adds_show():
    prog = assemble_program(_triangle(3))
    assert "#show assign/2." in prog


# --- reference ground truth ---------------------------------------------------------


def test_reference_ground_truth():
    spec_inf = {
        "id": "t2", "domain": "graph_coloring", "variables": ["n1", "n2", "n3"],
        "domains": {v: ["c1", "c2"] for v in ["n1", "n2", "n3"]},
        "constraints": [
            {"type": "not_equal", "a": "n1", "b": "n2"},
            {"type": "not_equal", "a": "n2", "b": "n3"},
            {"type": "not_equal", "a": "n1", "b": "n3"},
        ],
        "objective": None,
    }
    assert ground_truth(spec_inf)["feasible"] is False
    spec_feas = {**spec_inf, "domains": {v: ["c1", "c2", "c3"] for v in ["n1", "n2", "n3"]}}
    assert ground_truth(spec_feas)["feasible"] is True


# --- repair loop (LLM steps mocked) -------------------------------------------------


@patch("savanty.solver.check_problem_suitability", return_value={"is_suitable": "yes"})
@patch("savanty.solver.validate_and_parse_problem")
def test_repair_loop_terminates_and_reports_infeasible(mock_validate, _mock_suit):
    # Initial encoding is a genuinely unsatisfiable 2-colouring.
    mock_validate.return_value = _triangle(2)
    repair_calls = {"n": 0}

    def fake_repair(problem_description, components, outcome, repair_mode, decision_schema=""):
        repair_calls["n"] += 1
        return _triangle(2), "stay unsat"  # repair never fixes it

    with patch("savanty.solver._repair", side_effect=fake_repair):
        res = solve_optimization_problem("colour a triangle", max_repair_iters=3)
    assert isinstance(res, ProblemSolverResult)
    assert res.infeasible is True
    assert res.repair_iters == 3
    assert repair_calls["n"] == 3
    assert res.final_failure_type == "unsat"


@patch("savanty.solver.check_problem_suitability", return_value={"is_suitable": "yes"})
@patch("savanty.solver.validate_and_parse_problem")
def test_norepair_single_attempt(mock_validate, _mock_suit):
    mock_validate.return_value = _triangle(2)
    with patch("savanty.solver._repair") as mock_repair:
        res = solve_optimization_problem("colour a triangle", enable_repair=False)
    assert res.infeasible is True
    assert res.repair_iters == 0
    mock_repair.assert_not_called()


@patch("savanty.solver.check_problem_suitability", return_value={"is_suitable": "yes"})
@patch("savanty.solver.validate_and_parse_problem")
def test_repair_fixes_on_second_try(mock_validate, _mock_suit):
    mock_validate.return_value = _triangle(2)  # starts unsat

    def fake_repair(problem_description, components, outcome, repair_mode, decision_schema=""):
        return _triangle(3), "added a colour"  # repair makes it solvable

    with patch("savanty.solver._repair", side_effect=fake_repair):
        res = solve_optimization_problem("colour a triangle", max_repair_iters=3)
    assert res.final_failure_type == "ok"
    assert res.assignment and len(res.assignment) == 3
    assert res.repair_iters == 1


@pytest.mark.parametrize("mode", ["typed_core", "generic"])
@patch("savanty.solver.check_problem_suitability", return_value={"is_suitable": "yes"})
@patch("savanty.solver.validate_and_parse_problem")
def test_both_repair_modes_run(mock_validate, _mock_suit, mode):
    mock_validate.return_value = _triangle(3)  # already ok -> no repair needed
    res = solve_optimization_problem("colour a triangle", repair_mode=mode)
    assert res.final_failure_type == "ok"
