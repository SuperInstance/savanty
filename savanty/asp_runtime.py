"""Thin, robust wrapper around the clingo Python API.

Both the benchmark's ground-truth reference encoder and Savanty's solve path run ASP
text through here.  Using raw clingo (rather than the legacy clorm ``exec``-based path)
makes failure modes observable and removes arbitrary code execution: grounding/parse
errors surface as ``error`` instead of raising into the caller.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import clingo


@dataclass
class ClingoResult:
    sat: bool
    symbols: list[Any] = field(default_factory=list)  # shown symbols of the best model
    cost: list[int] | None = None  # clingo internal cost vector (best model)
    optimal: bool = False  # search exhausted -> optimum proven
    error: str | None = None  # grounding/parse error text (=> malformed program)

    @property
    def is_error(self) -> bool:
        return self.error is not None


SOLVE_TIME_LIMIT = 20.0  # seconds; safety net so no pathological instance stalls the eval


def run_clingo(program: str, time_limit: float | None = None) -> ClingoResult:
    """Ground and solve an ASP program; return one model (optimal for optimisation).

    Satisfaction programs request a single answer set (``--models=1``) — enumerating all
    models is needless and explodes on large solution spaces. Optimisation programs
    (``#minimize``/``#maximize``) run to exhaustion so the last (optimal) model is returned.
    Solving is bounded by ``time_limit`` (default ``SOLVE_TIME_LIMIT``); on timeout the result
    carries ``error`` so callers treat it as "could not decide", never as UNSAT.
    """
    limit = time_limit if time_limit is not None else SOLVE_TIME_LIMIT
    is_opt = "#minimize" in program or "#maximize" in program
    # Optimisation: cap reported models — clingo reaches the optimum within a few improving
    # steps; without a cap it enumerates every tied-optimal model (explodes under symmetry).
    args = ["--opt-mode=opt", "--models=300"] if is_opt else ["--models=1"]
    try:
        # Silence clingo's stderr warnings/info; we classify outcomes ourselves.
        ctl = clingo.Control(args, logger=lambda code, msg: None, message_limit=0)
        ctl.add("base", [], program)
        ctl.ground([("base", [])])
    except RuntimeError as exc:
        # Syntax / grounding error (undefined operation, parse failure, ...).
        return ClingoResult(sat=False, error=str(exc))

    best: dict[str, Any] = {"symbols": [], "cost": None, "found": False}

    def on_model(model):
        best["found"] = True
        best["symbols"] = list(model.symbols(shown=True))
        best["cost"] = list(model.cost) if model.cost else None

    try:
        handle = ctl.solve(on_model=on_model, async_=True)
        finished = handle.wait(limit)
        if not finished:
            handle.cancel()
            return ClingoResult(
                sat=False, error=f"solve timeout after {limit:g}s", optimal=False
            )
        result = handle.get()
    except RuntimeError as exc:
        return ClingoResult(sat=False, error=str(exc))

    found = best["found"]
    optimal = bool(found and result.satisfiable and (result.exhausted or not is_opt))
    return ClingoResult(sat=found, symbols=best["symbols"], cost=best["cost"], optimal=optimal)


def _symbol_text(sym: Any) -> str:
    """String form of a clingo Symbol argument (strip quotes from string symbols)."""
    text = str(sym)
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1]
    return text


def parse_assign_atoms(symbols: list[Any]) -> dict[str, str]:
    """Extract a ``{var: value}`` assignment from clingo ``assign(Var, Value)`` atoms.

    ``symbols`` is a list of clingo Symbol objects (e.g. ``model.symbols(shown=True)``).
    Atoms not named ``assign/2`` are ignored; the last write for a variable wins.
    """
    assignment: dict[str, str] = {}
    for s in symbols:
        if getattr(s, "name", None) == "assign" and len(getattr(s, "arguments", [])) == 2:
            var, val = s.arguments
            assignment[_symbol_text(var)] = _symbol_text(val)
    return assignment
