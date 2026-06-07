"""Savanty: An intelligent optimization problem solver using LLMs and ASP.

Now a **Topologically-Aware Constraint Engine** with Hybrid Manifold post-processing:
  1. TernaryL Gate — maps solver conviction onto {Sure (+1), Uncertain (0), Impossible (-1)}
  2. SAEP Veto Layer — governance hierarchy (Room → Sector → Portfolio → Market)
  3. Symmetry-Skeptic — topological symmetry-violation detection
"""

__version__ = "0.3.0"
__author__ = "Dipankar Sarkar"
__email__ = "me@dipankar.name"

# Core solver
from savanty.solver import (
    ProblemSolverResult,
    solve_optimization_problem,
    generate_visualization,
)

# Ternary Logic (TernaryL)
from savanty.ternary_l import (
    TernaryLEngine,
    TernaryLResult,
    AssignmentConviction,
    TritGate,
    LeminalZone,
    evaluate_solution,
)

# SAEP Veto Layer
from savanty.saep_veto import (
    VetoEngine,
    VetoResult,
    VetoEvent,
    SAEPConstraint,
    SAEPTier,
    veto_solution,
)

# Symmetry-Skeptic
from savanty.symmetry_skeptic import (
    SymmetrySkeptic,
    SymmetrySkepticResult,
    SymmetryViolation,
    check_symmetry,
)

__all__ = [
    # Core solver
    "solve_optimization_problem",
    "generate_visualization",
    "ProblemSolverResult",
    # TernaryL
    "TernaryLEngine",
    "TernaryLResult",
    "AssignmentConviction",
    "TritGate",
    "LeminalZone",
    "evaluate_solution",
    # SAEP Veto
    "VetoEngine",
    "VetoResult",
    "VetoEvent",
    "SAEPConstraint",
    "SAEPTier",
    "veto_solution",
    # Symmetry-Skeptic
    "SymmetrySkeptic",
    "SymmetrySkepticResult",
    "SymmetryViolation",
    "check_symmetry",
]
