"""Programmatic ground-truth oracle for the Savanty constraint-reasoning benchmark.

Every system under evaluation (Savanty's ASP pipeline and the LLM baselines) maps its
output to a single canonical representation: an *assignment* mapping each decision
variable to a value, i.e. a dict ``{var: value}``.  This module scores such an
assignment against a machine-checkable problem ``spec`` *independently of the system
that produced it* — it never trusts model output.

A ``spec`` is a plain dict (loaded from ``benchmark/problems/*.json``):

    {
      "id": str, "domain": str, "size": int,
      "feasible": bool,                 # ground truth: does a valid assignment exist?
      "optimal_value": float | None,    # ground truth optimum (optimisation instances)
      "nl_description": str,            # the natural-language problem (LLM input)
      "variables": [str, ...],          # decision variables
      "domains": {var: [value, ...]},   # allowed values per variable
      "constraints": [ {"type": ..., ...}, ... ],
      "objective": {"sense": "max"|"min", "weights": {var: {value: number}}} | None
    }

Values are compared as strings throughout (ASP constants are strings); the objective
weights are numbers.  Keeping a single ``assign(Var, Value)`` relation lets every domain
(graph colouring, scheduling, seating, knapsack, ...) share one oracle.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

# Canonical assignment parsing lives with the clingo runtime; re-exported for convenience.
from savanty.asp_runtime import parse_assign_atoms  # noqa: F401

Assignment = dict[str, str]


@dataclass
class VerifyResult:
    """Outcome of scoring one assignment against a spec."""

    hard_satisfied: int
    hard_total: int
    feasible: bool
    objective: float | None
    violations: list[str] = field(default_factory=list)
    # True iff every decision variable received an in-domain value.
    fully_assigned: bool = True

    @property
    def csr(self) -> float:
        """Constraint-Satisfaction Rate in [0, 1] (1.0 when there are no constraints)."""
        if self.hard_total == 0:
            return 1.0 if self.fully_assigned else 0.0
        return self.hard_satisfied / self.hard_total


def _val(assignment: Assignment, var: str) -> str | None:
    v = assignment.get(var)
    return None if v is None else str(v)


# --- individual constraint checkers -------------------------------------------------
# Each returns (ok: bool, detail: str).  ``detail`` is only used when ok is False.


def _c_all_different(a: Assignment, c: dict) -> tuple[bool, str]:
    vals = [_val(a, v) for v in c["vars"]]
    present = [v for v in vals if v is not None]
    ok = len(present) == len(set(present))
    return ok, f"all_different({c['vars']}) violated: values={vals}"


def _c_not_equal(a: Assignment, c: dict) -> tuple[bool, str]:
    va, vb = _val(a, c["a"]), _val(a, c["b"])
    ok = va is None or vb is None or va != vb
    return ok, f"not_equal({c['a']},{c['b']}) violated: both={va}"


def _c_equal(a: Assignment, c: dict) -> tuple[bool, str]:
    va, vb = _val(a, c["a"]), _val(a, c["b"])
    ok = va is None or vb is None or va == vb
    return ok, f"equal({c['a']},{c['b']}) violated: {va}!={vb}"


def _c_forbidden(a: Assignment, c: dict) -> tuple[bool, str]:
    ok = _val(a, c["var"]) != str(c["value"])
    return ok, f"forbidden: {c['var']} must not be {c['value']}"


def _c_required(a: Assignment, c: dict) -> tuple[bool, str]:
    ok = _val(a, c["var"]) == str(c["value"])
    return ok, f"required: {c['var']} must be {c['value']} (is {_val(a, c['var'])})"


def _c_capacity(a: Assignment, c: dict) -> tuple[bool, str]:
    """At most ``max`` variables (restricted to ``vars`` if given) take ``value``."""
    scope = c.get("vars") or list(a.keys())
    n = sum(1 for v in scope if _val(a, v) == str(c["value"]))
    ok = n <= c["max"]
    return ok, f"capacity({c['value']}<= {c['max']}) violated: count={n}"


def _c_min_count(a: Assignment, c: dict) -> tuple[bool, str]:
    scope = c.get("vars") or list(a.keys())
    n = sum(1 for v in scope if _val(a, v) == str(c["value"]))
    ok = n >= c["min"]
    return ok, f"min_count({c['value']}>= {c['min']}) violated: count={n}"


def _c_exact_count(a: Assignment, c: dict) -> tuple[bool, str]:
    scope = c.get("vars") or list(a.keys())
    n = sum(1 for v in scope if _val(a, v) == str(c["value"]))
    ok = n == c["count"]
    return ok, f"exact_count({c['value']}=={c['count']}) violated: count={n}"


def _c_weighted_capacity(a: Assignment, c: dict) -> tuple[bool, str]:
    """Sum of ``weights[var]`` over vars assigned ``selected_value`` must be <= bound."""
    sel = str(c["selected_value"])
    total = sum(c["weights"].get(v, 0) for v in c["weights"] if _val(a, v) == sel)
    ok = total <= c["bound"]
    return ok, f"weighted_capacity(<= {c['bound']}) violated: total={total}"


_CHECKERS = {
    "all_different": _c_all_different,
    "not_equal": _c_not_equal,
    "equal": _c_equal,
    "forbidden": _c_forbidden,
    "required": _c_required,
    "capacity": _c_capacity,
    "min_count": _c_min_count,
    "exact_count": _c_exact_count,
    "weighted_capacity": _c_weighted_capacity,
}


def objective_value(spec: dict, assignment: Assignment) -> float | None:
    """Compute the objective of an assignment, or None if the spec has no objective."""
    obj = spec.get("objective")
    if not obj:
        return None
    weights = obj.get("weights", {})
    total = 0.0
    for var, per_value in weights.items():
        val = _val(assignment, var)
        if val is not None and val in per_value:
            total += per_value[val]
    return total


def verify(spec: dict, assignment: Assignment | None) -> VerifyResult:
    """Score ``assignment`` against ``spec``. The single ground-truth oracle."""
    if assignment is None:
        assignment = {}
    variables = spec.get("variables", [])
    domains = spec.get("domains", {})

    violations: list[str] = []

    # 1) Domain / coverage check: every variable must get an in-domain value.
    fully_assigned = True
    for var in variables:
        val = _val(assignment, var)
        if val is None:
            fully_assigned = False
            violations.append(f"unassigned: {var}")
        elif var in domains and val not in [str(d) for d in domains[var]]:
            fully_assigned = False
            violations.append(f"out_of_domain: {var}={val} not in {domains[var]}")

    # 2) Declared hard constraints.
    constraints = spec.get("constraints", [])
    hard_total = len(constraints)
    hard_satisfied = 0
    for c in constraints:
        checker = _CHECKERS.get(c["type"])
        if checker is None:
            raise ValueError(f"Unknown constraint type: {c['type']}")
        ok, detail = checker(assignment, c)
        if ok:
            hard_satisfied += 1
        else:
            violations.append(detail)

    feasible = fully_assigned and hard_satisfied == hard_total
    obj = objective_value(spec, assignment) if feasible else None

    return VerifyResult(
        hard_satisfied=hard_satisfied,
        hard_total=hard_total,
        feasible=feasible,
        objective=obj,
        violations=violations,
        fully_assigned=fully_assigned,
    )


def domain_value_counts(assignment: Assignment) -> dict[str, int]:
    """Helper for debugging/analysis: how many vars take each value."""
    return dict(Counter(str(v) for v in assignment.values()))


