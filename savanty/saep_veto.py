"""
saep_veto — SAEP Governance Veto Layer

A post-processor that checks ASP solutions against a 4-tier governance hierarchy:

    Room → Sector → Portfolio → Market

Each tier enforces safety constraints that the solver may not know about.
If a solution violates any tier's constraint, the VetoEngine rejects it
with a specific veto reason and tier attribution.

Inspired by the SAEP Governance model (market-manifold/FLEET-POLLINATION-MAP.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


# ── Tier definitions ───────────────────────────────────────────────────────────────


class SAEPTier(Enum):
    """The four governance tiers in increasing scope."""

    ROOM = "room"
    SECTOR = "sector"
    PORTFOLIO = "portfolio"
    MARKET = "market"

    def __lt__(self, other: "SAEPTier") -> bool:
        order = [SAEPTier.ROOM, SAEPTier.SECTOR, SAEPTier.PORTFOLIO, SAEPTier.MARKET]
        return order.index(self) < order.index(other)

    def __le__(self, other: "SAEPTier") -> bool:
        return self == other or self < other


# ── Constraint descriptors ─────────────────────────────────────────────────────────


@dataclass
class SAEPConstraint:
    """A single governance constraint within a tier.

    Parameters
    ----------
    tier : SAEPTier
        Which governance tier this constraint belongs to.
    name : str
        Human-readable name (e.g. "max_workload", "no_conflict_of_interest").
    check : Callable[[dict[str, str]], bool]
        Predicate that returns True if the assignment *satisfies* the constraint.
        Receives the full {var: value} assignment dict.
    description : str
        Human-readable description of what this constraint enforces.
    violation_message : str
        Message to include when this constraint is violated.
    """

    tier: SAEPTier
    name: str
    check: Callable[[dict[str, str]], bool]
    description: str = ""
    violation_message: str = "Constraint violation."

    # ── Constraint factories ────────────────────────────────────────────────────

    @staticmethod
    def max_value_constraint(
        tier: SAEPTier,
        name: str,
        pattern: str,
        max_count: int,
        description: str = "",
    ) -> "SAEPConstraint":
        """Create a constraint that limits how many variables can match a value pattern.

        Parameters
        ----------
        tier : SAEPTier
        name : str
        pattern : str
            Substring to match in the assigned value.
        max_count : int
            Maximum number of variables allowed to match.
        description : str
        """
        desc = description or f"At most {max_count} assignments matching '{pattern}'."

        def check(assignment: dict[str, str]) -> bool:
            count = sum(1 for v in assignment.values() if pattern in v)
            return count <= max_count

        return SAEPConstraint(
            tier=tier,
            name=name,
            check=check,
            description=desc,
            violation_message=(
                f"Constraint '{name}': more than {max_count} assignments "
                f"matched '{pattern}'."
            ),
        )

    @staticmethod
    def unique_value_constraint(
        tier: SAEPTier,
        name: str,
        variables: list[str] | None = None,
        description: str = "",
    ) -> "SAEPConstraint":
        """Create a constraint ensuring specified variables get unique values.

        Parameters
        ----------
        tier : SAEPTier
        name : str
        variables : list[str] | None
            Subset of variables to check. None = all variables.
        description : str
        """
        desc = description or "Specified variables must have distinct values."

        def check(assignment: dict[str, str]) -> bool:
            relevant = {
                k: v for k, v in assignment.items()
                if variables is None or k in variables
            }
            return len(set(relevant.values())) == len(relevant)

        return SAEPConstraint(
            tier=tier,
            name=name,
            check=check,
            description=desc,
            violation_message=(
                f"Constraint '{name}': duplicate values found among "
                f"{'all' if variables is None else 'specified'} variables."
            ),
        )

    @staticmethod
    def custom_constraint(
        tier: SAEPTier,
        name: str,
        check_fn: Callable[[dict[str, str]], bool],
        description: str = "",
        violation_message: str = "Custom constraint violation.",
    ) -> "SAEPConstraint":
        """Create a fully custom governance constraint."""
        return SAEPConstraint(
            tier=tier,
            name=name,
            check=check_fn,
            description=description or f"Custom constraint '{name}'.",
            violation_message=violation_message,
        )


# ── Veto result ────────────────────────────────────────────────────────────────────


@dataclass
class VetoEvent:
    """A single veto triggered by a governance constraint.

    Attributes
    ----------
    tier : SAEPTier
        The governance tier that raised the veto.
    constraint_name : str
        The SAEPConstraint name.
    violation_message : str
        Explanation of what was violated.
    """

    tier: SAEPTier
    constraint_name: str
    violation_message: str


@dataclass
class VetoResult:
    """Outcome of checking a solution against the SAEP veto hierarchy.

    Attributes
    ----------
    passed : bool
        True if all active constraints pass (no vetoes).
    vetoes : list[VetoEvent]
        List of veto events, empty if passed.
    highest_offending_tier : SAEPTier | None
        The highest-tier that raised a veto, or None if all passed.
    summary : str
        Human-readable summary of the veto check.
    """

    passed: bool = True
    vetoes: list[VetoEvent] = field(default_factory=list)
    highest_offending_tier: SAEPTier | None = None
    summary: str = "All governance constraints passed."


# ── Veto Engine ─────────────────────────────────────────────────────────────────────


class VetoEngine:
    """SAEP Veto Engine: checks an assignment against a hierarchy of governance tiers.

    The engine applies constraints tier-by-tier (Room → Sector → Portfolio → Market).
    Higher-tier violations are reported first; all violations across all tiers are
    collected before returning.
    """

    def __init__(self, constraints: list[SAEPConstraint] | None = None):
        self.constraints: list[SAEPConstraint] = constraints or []

    # ── Constraint registration ───────────────────────────────────────────────────

    def add_constraint(self, constraint: SAEPConstraint) -> None:
        """Register a single governance constraint."""
        self.constraints.append(constraint)

    def add_constraints(self, constraints: list[SAEPConstraint]) -> None:
        """Register multiple governance constraints."""
        self.constraints.extend(constraints)

    # ── Core check ────────────────────────────────────────────────────────────────

    def check(self, assignment: dict[str, str] | None) -> VetoResult:
        """Run the full veto hierarchy against a solved assignment.

        Parameters
        ----------
        assignment : dict[str, str] | None
            The variable → value mapping from the solver. If None or empty,
            triggers a MARKET-level veto (no solution to govern).

        Returns
        -------
        VetoResult
        """
        if not assignment:
            return VetoResult(
                passed=False,
                vetoes=[
                    VetoEvent(
                        tier=SAEPTier.MARKET,
                        constraint_name="null_solution",
                        violation_message="No assignment to govern — veto by default.",
                    )
                ],
                highest_offending_tier=SAEPTier.MARKET,
                summary="VETO: No solution to govern.",
            )

        # Sort constraints by tier precedence (Room first, Market last)
        sorted_constraints = sorted(
            self.constraints, key=lambda c: list(SAEPTier).index(c.tier)
        )

        vetoes: list[VetoEvent] = []
        highest_tier: SAEPTier | None = None

        for constraint in sorted_constraints:
            try:
                passed = constraint.check(assignment)
            except Exception as exc:
                # A crashing constraint is treated as a veto
                passed = False
                msg = (
                    f"Constraint '{constraint.name}' raised an exception: {exc}"
                )

            if not passed:
                msg = constraint.violation_message
                event = VetoEvent(
                    tier=constraint.tier,
                    constraint_name=constraint.name,
                    violation_message=msg,
                )
                vetoes.append(event)
                if highest_tier is None or constraint.tier > highest_tier:
                    highest_tier = constraint.tier

        passed = len(vetoes) == 0
        if passed:
            summary = "All governance constraints passed."
        else:
            tier_labels = ", ".join(
                sorted({v.tier.value for v in vetoes}, reverse=True)
            )
            summary = (
                f"VETO: {len(vetoes)} constraint(s) violated "
                f"(offending tiers: {tier_labels})."
            )

        return VetoResult(
            passed=passed,
            vetoes=vetoes,
            highest_offending_tier=highest_tier,
            summary=summary,
        )


# ── Convenience ─────────────────────────────────────────────────────────────────────


def veto_solution(
    assignment: dict[str, str] | None,
    constraints: list[SAEPConstraint] | None = None,
) -> VetoResult:
    """One-shot SAEP veto check against a solved assignment."""
    engine = VetoEngine(constraints=constraints)
    return engine.check(assignment)
