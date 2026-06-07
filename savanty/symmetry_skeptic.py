"""
symmetry_skeptic — Topological Symmetry-Violation Detector

Flags ASP solutions that break topological symmetry — i.e., the solver's
assignment introduces an avoidable asymmetry in the underlying constraint graph.

The Skeptic inspects the **constraint graph** of the generated ASP program
(how variables are connected through shared constraints) and the **assignment**
produced by the solver. If the assignment does not respect the automorphism
symmetry of the constraint graph, it is flagged as a Symmetry Violation.

Two views are provided:

1. **Variable-swap symmetry** — identical variables (same domain, same neighbour
   structure) that were assigned different values, breaking an obvious symmetry
   that an optimal solution should preserve unless forced by other constraints.
2. **Wasserstein symmetry distance** — continuous measure of how much the
   assignment deviates from the symmetry classes, using an adaptation of
   Wasserstein distance on the constraint graph's orbit structure.

Inspired by the Symmetry Detection primitives from the Hybrid Manifold
(market-manifold/FLEET-POLLINATION-MAP.md).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


# ── Data structures ────────────────────────────────────────────────────────────────


@dataclass
class SymmetryViolation:
    """A single detected symmetry violation.

    Attributes
    ----------
    variable : str
        The variable that breaks symmetry.
    expected_value : str | None
        The symmetric-expectation value (the value that a symmetric partner
        received), or None if no partner exists.
    assigned_value : str | None
        The actual value assigned by the solver.
    orbit_name : str
        The symmetry orbit to which this variable belongs.
    severity : float
        0.0 = no violation, 1.0 = full symmetry violation.
    explanation : str
        Human-readable description.
    """

    variable: str
    expected_value: str | None
    assigned_value: str | None
    orbit_name: str
    severity: float
    explanation: str = ""


@dataclass
class SymmetrySkepticResult:
    """Overall result of a symmetry check.

    Attributes
    ----------
    passed : bool
        True if no symmetry violations detected.
    violations : list[SymmetryViolation]
        Detected violations.
    orbits : dict[str, list[str]]
        Detected symmetry orbits: orbit_name -> [variables].
    wasserstein_distance : float
        Aggregate Wasserstein distance across all orbits (0 = perfect symmetry).
    wasserstein_breakdown : dict[str, float]
        Per-orbit Wasserstein contributions.
    summary : str
        Human-readable summary.
    """

    passed: bool = True
    violations: list[SymmetryViolation] = field(default_factory=list)
    orbits: dict[str, list[str]] = field(default_factory=dict)
    wasserstein_distance: float = 0.0
    wasserstein_breakdown: dict[str, float] = field(default_factory=dict)
    summary: str = "No symmetry violations detected."


# ── Symmetry-Skeptic Engine ────────────────────────────────────────────────────────


class SymmetrySkeptic:
    """Detects topological symmetry violations in ASP solver assignments.

    The Skeptic works in two phases:

    1. **Orbit detection** — Group variables into symmetry orbits based on
       the constraint graph and domain structure. Variables in the same orbit
       are topologically equivalent (they could be swapped without changing
       the constraint structure).
    2. **Symmetry check** — Verify that all variables in the same orbit
       received the same assigned value. If they differ, the solution breaks
       symmetry.
    """

    # ── Public API ────────────────────────────────────────────────────────────────

    def check(
        self,
        assignment: dict[str, str] | None,
        domains: dict[str, list[str]] | None = None,
        constraint_edges: list[tuple[str, str]] | None = None,
    ) -> SymmetrySkepticResult:
        """Run the full symmetry-skeptic check.

        Parameters
        ----------
        assignment : dict[str, str] | None
            Var → value from the solver. Pass None or {} for an empty solution.
        domains : dict[str, list[str]] | None
            Domain per variable. Used to refine orbit detection (same domain
            is necessary for symmetry).
        constraint_edges : list[(str, str)] | None
            Pairs of variables that share a constraint (co-occurrence in an
            integrity constraint). If None, we assume a fully connected graph
            (conservative — only same-domain = symmetric).

        Returns
        -------
        SymmetrySkepticResult
        """
        if not assignment:
            return SymmetrySkepticResult(
                passed=True,
                summary="No assignment to check — no symmetry violations.",
            )

        # 1. Detect orbits
        orbits = self._detect_orbits(assignment, domains, constraint_edges)

        # 2. Check symmetry
        violations: list[SymmetryViolation] = []
        wasserstein_breakdown: dict[str, float] = {}

        for orbit_name, members in orbits.items():
            if len(members) <= 1:
                wasserstein_breakdown[orbit_name] = 0.0
                continue

            # Collect values assigned to each member
            values = [assignment.get(m) for m in members]

            # Check if all are identical
            unique_values = set(v for v in values if v is not None)
            if len(unique_values) <= 1:
                wasserstein_breakdown[orbit_name] = 0.0
                continue

            # Compute Wasserstein per-orbit
            # (fraction of members that disagree with the majority value)
            counts: dict[str, int] = defaultdict(int)
            for v in values:
                if v is not None:
                    counts[v] += 1
            majority_val = max(counts, key=counts.get)
            majority_count = counts[majority_val]
            total = sum(counts.values())
            wasserstein = 1.0 - (majority_count / total) if total > 0 else 0.0
            wasserstein_breakdown[orbit_name] = wasserstein

            # Report violations for members that disagree
            for member in members:
                assigned = assignment.get(member)
                if assigned != majority_val:
                    violations.append(
                        SymmetryViolation(
                            variable=member,
                            expected_value=majority_val,
                            assigned_value=assigned,
                            orbit_name=orbit_name,
                            severity=wasserstein,
                            explanation=(
                                f"Variable '{member}' (orbit '{orbit_name}') assigned "
                                f"'{assigned}' but symmetric partners received "
                                f"'{majority_val}'. This breaks topological symmetry."
                            ),
                        )
                    )

        passed = len(violations) == 0
        total_wasserstein = (
            sum(wasserstein_breakdown.values()) / len(wasserstein_breakdown)
            if wasserstein_breakdown
            else 0.0
        )

        if passed:
            summary = (
                f"Symmetry check passed: {len(orbits)} orbit(s), "
                f"Wasserstein={total_wasserstein:.4f}."
            )
        else:
            summary = (
                f"SYMMETRY VIOLATION: {len(violations)} violation(s) in "
                f"{len({v.orbit_name for v in violations})} orbit(s), "
                f"aggregate Wasserstein={total_wasserstein:.4f}."
            )

        return SymmetrySkepticResult(
            passed=passed,
            violations=violations,
            orbits=orbits,
            wasserstein_distance=total_wasserstein,
            wasserstein_breakdown=wasserstein_breakdown,
            summary=summary,
        )

    # ── Internals ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _detect_orbits(
        assignment: dict[str, str],
        domains: dict[str, list[str]] | None,
        constraint_edges: list[tuple[str, str]] | None,
    ) -> dict[str, list[str]]:
        """Group variables into symmetry orbits.

        Two variables are in the same orbit if:
        - They have the same domain (same allowed values), AND
        - They have the same constraint-neighbour structure (degree and adjacency)
          when constraint_edges are provided.

        If constraint_edges is None, we conservatively group only by domain.
        """
        variables = sorted(assignment.keys())

        # Assign each variable a signature — variables with identical signature
        # are in the same orbit.
        domain_lookup = domains or {}

        # Build neighbour sets if edges are available
        neighbours: dict[str, set[str]] = defaultdict(set)
        if constraint_edges:
            for a, b in constraint_edges:
                if a in variables and b in variables:
                    neighbours[a].add(b)
                    neighbours[b].add(a)

        signatures: dict[str, tuple] = {}
        for var in variables:
            dom = tuple(sorted(domain_lookup.get(var, [])))
            # Neighbour degree and sorted neighbour-list, both from the domain
            # perspective (we check domain-type, not exact identity).
            nbr_set = neighbours.get(var, set())
            nbr_degree = len(nbr_set)
            # Sort neighbour-domains as a structural identifier
            nbr_domains = tuple(
                sorted(tuple(sorted(domain_lookup.get(n, []))) for n in sorted(nbr_set))
            )
            signatures[var] = (dom, nbr_degree, nbr_domains)

        # Group by signature
        orbit_groups: dict[tuple, list[str]] = defaultdict(list)
        for var, sig in signatures.items():
            orbit_groups[sig].append(var)

        # Name orbits
        orbits: dict[str, list[str]] = {}
        for idx, (sig, members) in enumerate(orbit_groups.items()):
            if len(members) > 1:
                orbit_name = f"orbit_{idx}_dom={sig[0][:3]}...deg={sig[1]}"
            else:
                orbit_name = f"singleton_{idx}"
            orbits[orbit_name] = members

        return orbits


# ── Convenience ─────────────────────────────────────────────────────────────────────


def check_symmetry(
    assignment: dict[str, str] | None,
    domains: dict[str, list[str]] | None = None,
    constraint_edges: list[tuple[str, str]] | None = None,
) -> SymmetrySkepticResult:
    """One-shot symmetry-skeptic check."""
    skeptic = SymmetrySkeptic()
    return skeptic.check(
        assignment=assignment,
        domains=domains,
        constraint_edges=constraint_edges,
    )
