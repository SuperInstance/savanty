"""Deterministic spec -> canonical ASP encoder + ground-truth computation.

This is the *trusted* path: it maps a structured ``spec`` (not the natural-language
text) to ASP, so the feasibility/optimum labels it produces are correct by construction.
It is used (a) at dataset-generation time to label each instance, and (b) as the gold
reference for the optimality gap.  It is intentionally independent of the LLM pipeline.

All decision variables become a single ``assign(Var, Value)`` relation via choice rules,
exactly matching the canonical representation the oracle (``verify.py``) consumes.
"""

from __future__ import annotations

from benchmark.verify import objective_value, parse_assign_atoms
from savanty.asp_runtime import run_clingo


def _t(x) -> str:
    """Render a spec id/value as a safe ASP constant term (lowercase identifier)."""
    s = str(x)
    return s


def spec_to_asp(spec: dict, with_objective: bool = True) -> str:
    """Translate a structured spec to canonical ASP over ``assign/2``."""
    lines: list[str] = []
    domains = spec["domains"]

    # Choice rules: each variable takes exactly one value from its domain.
    for var in spec["variables"]:
        dom = domains[var]
        choices = "; ".join(f"assign({_t(var)},{_t(v)})" for v in dom)
        lines.append(f"1 {{ {choices} }} 1.")

    for i, c in enumerate(spec.get("constraints", [])):
        lines.extend(_constraint_to_asp(i, c))

    if with_objective and spec.get("objective"):
        lines.extend(_objective_to_asp(spec["objective"]))

    lines.append("#show assign/2.")
    return "\n".join(lines)


def _constraint_to_asp(i: int, c: dict) -> list[str]:
    t = c["type"]
    out: list[str] = []
    if t == "all_different":
        vs = c["vars"]
        for a in range(len(vs)):
            for b in range(a + 1, len(vs)):
                out.append(f":- assign({_t(vs[a])},C), assign({_t(vs[b])},C).")
    elif t == "not_equal":
        out.append(f":- assign({_t(c['a'])},C), assign({_t(c['b'])},C).")
    elif t == "equal":
        out.append(f":- assign({_t(c['a'])},Ca), assign({_t(c['b'])},Cb), Ca!=Cb.")
    elif t == "forbidden":
        out.append(f":- assign({_t(c['var'])},{_t(c['value'])}).")
    elif t == "required":
        out.append(f":- not assign({_t(c['var'])},{_t(c['value'])}).")
    elif t in ("capacity", "min_count", "exact_count"):
        scope = c.get("vars")
        if scope:
            for v in scope:
                out.append(f"scope{i}({_t(v)}).")
            count = f"#count{{ V : assign(V,{_t(c['value'])}), scope{i}(V) }}"
        else:
            count = f"#count{{ V : assign(V,{_t(c['value'])}) }}"
        if t == "capacity":
            out.append(f":- {count} > {c['max']}.")
        elif t == "min_count":
            out.append(f":- {count} < {c['min']}.")
        else:
            out.append(f":- not {count} = {c['count']}.")
    elif t == "weighted_capacity":
        sel = _t(c["selected_value"])
        for v, w in c["weights"].items():
            out.append(f"w{i}({_t(v)},{w}).")
        out.append(
            f":- #sum{{ W,V : assign(V,{sel}), w{i}(V,W) }} > {c['bound']}."
        )
    else:
        raise ValueError(f"Unknown constraint type for ASP encoding: {t}")
    return out


def _objective_to_asp(obj: dict) -> list[str]:
    out: list[str] = []
    for var, per_value in obj["weights"].items():
        for value, w in per_value.items():
            out.append(f"objw({_t(var)},{_t(value)},{w}).")
    directive = "#maximize" if obj["sense"] == "max" else "#minimize"
    out.append(f"{directive}{{ W,V,Val : assign(V,Val), objw(V,Val,W) }}.")
    return out


def ground_truth(spec: dict) -> dict:
    """Compute (feasible, optimal_value, witness) for a spec via the reference encoder."""
    res = run_clingo(spec_to_asp(spec, with_objective=True))
    if res.error:
        raise RuntimeError(f"reference encoding failed for {spec.get('id')}: {res.error}")
    if not res.sat:
        return {"feasible": False, "optimal_value": None, "witness": None}
    witness = parse_assign_atoms(res.symbols)
    opt = objective_value(spec, witness)
    return {"feasible": True, "optimal_value": opt, "witness": witness}
