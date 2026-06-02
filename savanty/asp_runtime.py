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


def run_clingo(program: str, time_limit: float | None = None) -> ClingoResult:
    """Ground and solve an ASP program; return the (optimal, if any) model.

    For optimisation programs (``#minimize``/``#maximize``) clingo enumerates improving
    models; the last one found is optimal and ``optimal`` is set when search is exhausted.
    """
    args = ["--opt-mode=opt", "--models=0"]
    try:
        # Silence clingo's stderr warnings/info (e.g. "no atoms over signature"); we classify
        # outcomes ourselves and keep batch eval output clean.
        ctl = clingo.Control(args, logger=lambda code, msg: None, message_limit=0)
        ctl.add("base", [], program)
        ctl.ground([("base", [])])
    except RuntimeError as exc:
        # Syntax / grounding error (undefined operation, parse failure, ...).
        return ClingoResult(sat=False, error=str(exc))

    best_symbols: list[Any] = []
    best_cost: list[int] | None = None
    found = False
    try:
        with ctl.solve(yield_=True, async_=False) as handle:
            for model in handle:
                found = True
                best_symbols = list(model.symbols(shown=True))
                best_cost = list(model.cost) if model.cost else None
            result = handle.get()
    except RuntimeError as exc:
        return ClingoResult(sat=False, error=str(exc))

    return ClingoResult(
        sat=found,
        symbols=best_symbols,
        cost=best_cost,
        optimal=bool(found and result.satisfiable and result.exhausted),
    )


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
