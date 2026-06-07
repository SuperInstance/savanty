"""
ternary_l — Ternary-Continuous Hybrid Conviction Mapping

Maps continuous solver-assignment quality metrics onto the **TernaryL trit gate**
space of {Sure (+1), Uncertain (0), Impossible (-1)} with a configurable
**Leminal Zone** deadband that rejects low-confidence or borderline solutions.

Inspired by the Hybrid Manifold's trit gates (market-manifold/FLEET-POLLINATION-MAP.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Trit Gate ──────────────────────────────────────────────────────────────────────


class TritGate:
    """Ternary logic gate: one of SURE (+1), UNCERTAIN (0), IMPOSSIBLE (-1)."""

    SURE = +1
    UNCERTAIN = 0
    IMPOSSIBLE = -1

    _LABELS = {+1: "Sure", 0: "Uncertain", -1: "Impossible"}

    @classmethod
    def label(cls, gate: int) -> str:
        return cls._LABELS.get(gate, f"Unknown({gate})")


# ── Leminal Zone ───────────────────────────────────────────────────────────────────


@dataclass
class LeminalZone:
    """Deadband region that maps borderline conviction scores to UNCERTAIN.

    Parameters
    ----------
    low : float
        Lower threshold (exclusive). Scores <= low map to IMPOSSIBLE.
    high : float
        Upper threshold (exclusive). Scores >= high map to SURE.
        Scores in (low, high) map to UNCERTAIN.
    """

    low: float = 0.30
    high: float = 0.70

    def classify(self, conviction: float) -> int:
        """Map a conviction score in [0, 1] to a trit gate."""
        if conviction >= self.high:
            return TritGate.SURE
        if conviction > self.low:
            return TritGate.UNCERTAIN
        return TritGate.IMPOSSIBLE


# ── Available defaults ─────────────────────────────────────────────────────────────

# The canonical leminal zone as defined in the Hybrid Manifold spec.
MANIFOLD_LEMINAL = LeminalZone(low=0.30, high=0.70)


# ── Per-assignment conviction ──────────────────────────────────────────────────────


@dataclass
class AssignmentConviction:
    """TernaryL rating for a single decision variable.

    Attributes
    ----------
    variable : str
        Decision variable name (e.g. "nurse_alice", "task_1").
    value : str
        Assigned value (e.g. "morning", "slot_3").
    conviction : float
        Raw continuous score in [0, 1] from the solver (assigned / total, or
        derived from objective contribution, slack, etc.).
    gate : int
        Trit gate from classify(conviction): +1 | 0 | -1.
    explanation : str
        Human-readable justification for the gate assignment.
    """

    variable: str
    value: str
    conviction: float
    gate: int
    explanation: str = ""


# ── TernaryL Result ────────────────────────────────────────────────────────────────


@dataclass
class TernaryLResult:
    """Overall ternary assessment of a solver result.

    Attributes
    ----------
    assignments : list[AssignmentConviction]
        Per-variable ternary ratings.
    aggregate_gate : int
        Overall trit gate for the entire solution:
        - SURE (+1)  —  every assignment is SURE.
        - IMPOSSIBLE (-1) — any assignment is IMPOSSIBLE.
        - UNCERTAIN (0) — otherwise.
    aggregate_conviction : float
        Mean conviction across all assignments.
    solution_infeasible : bool
        Whether the underlying solver declared infeasibility.
    """

    assignments: list[AssignmentConviction] = field(default_factory=list)
    aggregate_gate: int = TritGate.UNCERTAIN
    aggregate_conviction: float = 0.0
    solution_infeasible: bool = False


# ── TernaryL Engine ────────────────────────────────────────────────────────────────


class TernaryLEngine:
    """Core engine: maps solver outcomes to TernaryL trit gates.

    The engine computes per-variable conviction scores based on how many
    valid options exist in the decision space and whether the assignment
    is part of an optimal / feasible solution.
    """

    def __init__(self, leminal: LeminalZone | None = None):
        self.leminal = leminal or MANIFOLD_LEMINAL

    # ── Public API ────────────────────────────────────────────────────────────────

    def evaluate(
        self,
        assignment: dict[str, str] | None,
        domains: dict[str, list[str]] | None = None,
        infeasible: bool = False,
    ) -> TernaryLResult:
        """Evaluate a solver assignment and produce a TernaryL result.

        Parameters
        ----------
        assignment : dict[str, str] | None
            Var → value dict from the solver, or None if no assignment found.
        domains : dict[str, list[str]] | None
            Domain size per variable (optional — used for conviction score).
        infeasible : bool
            Whether the solver reported unsatisfiability.

        Returns
        -------
        TernaryLResult
        """
        if infeasible or assignment is None or not assignment:
            return self._infeasible_result()

        convictions: list[AssignmentConviction] = []
        for var, val in sorted(assignment.items()):
            domain_ratio = self._domain_conviction(var, val, domains)
            gate = self.leminal.classify(domain_ratio)
            explanation = self._explain(var, val, domain_ratio, gate, infeasible)
            convictions.append(
                AssignmentConviction(
                    variable=var,
                    value=val,
                    conviction=domain_ratio,
                    gate=gate,
                    explanation=explanation,
                )
            )

        agg_conv = (
            sum(c.conviction for c in convictions) / len(convictions)
            if convictions
            else 0.0
        )

        # Aggregate gate logic
        if not convictions:
            agg_gate = TritGate.IMPOSSIBLE
        elif any(c.gate == TritGate.IMPOSSIBLE for c in convictions):
            agg_gate = TritGate.IMPOSSIBLE
        elif all(c.gate == TritGate.SURE for c in convictions):
            agg_gate = TritGate.SURE
        else:
            agg_gate = TritGate.UNCERTAIN

        return TernaryLResult(
            assignments=convictions,
            aggregate_gate=agg_gate,
            aggregate_conviction=agg_conv,
            solution_infeasible=False,
        )

    # ── Internals ─────────────────────────────────────────────────────────────────

    def _infeasible_result(self) -> TernaryLResult:
        return TernaryLResult(
            assignments=[],
            aggregate_gate=TritGate.IMPOSSIBLE,
            aggregate_conviction=0.0,
            solution_infeasible=True,
        )

    def _domain_conviction(
        self,
        variable: str,
        value: str,
        domains: dict[str, list[str]] | None,
    ) -> float:
        """Compute a conviction score in [0, 1] for a single assignment.

        When domain size is known: conviction = 1 - (1/domain_size)
        (assigning from a singleton domain is trivially forced — low conviction;
         assigning from a large domain is highly committed — high conviction).

        When domain is unknown: defaults to 0.50.
        """
        if domains and variable in domains:
            sz = len(domains[variable])
            if sz <= 1:
                # Singleton domain: forced choice — low conviction.
                return 0.10
            return 1.0 - (1.0 / sz)
        return 0.50

    def _explain(
        self,
        var: str,
        val: str,
        conviction: float,
        gate: int,
        infeasible: bool,
    ) -> str:
        if infeasible:
            return "No valid assignment exists in the feasible space."
        label = TritGate.label(gate)
        dv = conviction
        if gate == TritGate.SURE:
            return (
                f"Assignment {var}={val} is {label} (conviction={dv:.3f}): "
                "strong commitment — chosen from a large decision space."
            )
        if gate == TritGate.UNCERTAIN:
            return (
                f"Assignment {var}={val} is {label} (conviction={dv:.3f}): "
                "in the leminal zone — weak commitment; may warrant human review."
            )
        return (
            f"Assignment {var}={val} is {label} (conviction={dv:.3f}): "
            "trivially forced or no valid option exists."
        )


# ── Convenience ────────────────────────────────────────────────────────────────────


def evaluate_solution(
    assignment: dict[str, str] | None,
    domains: dict[str, list[str]] | None = None,
    infeasible: bool = False,
    leminal: LeminalZone | None = None,
) -> TernaryLResult:
    """One-shot evaluation of a solver assignment through the TernaryL gate."""
    engine = TernaryLEngine(leminal=leminal)
    return engine.evaluate(assignment=assignment, domains=domains, infeasible=infeasible)
