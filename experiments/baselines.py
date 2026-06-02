"""Systems under evaluation. Each maps a problem spec -> a canonical assignment.

All systems receive the SAME natural-language description. The LLM baselines are additionally
handed an answer template (the decision-variable names + allowed values) so they can only fail
on the *reasoning*, never on the output format — this makes our advantage conservative.

Return contract for every system:
    SystemOutput(assignment: dict|None, infeasible: bool, error: str|None,
                 repair_iters: int, final_failure_type: str|None)
- assignment is a {var: value} dict when the system commits to a solution.
- infeasible=True means the system declared the problem has no solution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import dspy

from savanty.solver import solve_optimization_problem


@dataclass
class SystemOutput:
    assignment: dict | None = None
    infeasible: bool = False
    error: str | None = None
    repair_iters: int = 0
    final_failure_type: str | None = None
    extra: dict = field(default_factory=dict)


# --- LLM baselines (no symbolic solver) --------------------------------------------


class DirectSolve(dspy.Signature):
    """Solve the constraint/optimization problem and output the solution directly.

    Assign each listed decision variable exactly one allowed value so that ALL stated
    requirements hold (and the objective, if any, is optimized). If no assignment can
    satisfy all requirements, declare the problem infeasible.
    """

    problem = dspy.InputField(desc="Natural-language problem description")
    variables = dspy.InputField(desc="Comma-separated decision-variable names to assign")
    allowed_values = dspy.InputField(desc="Allowed values, per variable")
    answer = dspy.OutputField(
        desc='STRICT JSON: {"assignment": {"var": "value", ...}} OR {"infeasible": true}'
    )


def _answer_to_output(raw: str) -> SystemOutput:
    text = raw.strip()
    if "```" in text:
        # strip code fences
        seg = text.split("```")
        text = max(seg, key=len)
        text = text[text.find("{") :] if "{" in text else text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return SystemOutput(error="no JSON in answer")
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        return SystemOutput(error=f"bad JSON: {e}")
    if data.get("infeasible") is True:
        return SystemOutput(infeasible=True)
    assignment = data.get("assignment")
    if not isinstance(assignment, dict):
        return SystemOutput(error="no assignment in answer")
    return SystemOutput(assignment={str(k): str(v) for k, v in assignment.items()})


def _variables_blurb(spec: dict) -> tuple[str, str]:
    variables = ", ".join(spec["variables"])
    doms = spec.get("domains", {})
    # Compress: if all domains identical, state once.
    uniq = {tuple(v) for v in doms.values()}
    if len(uniq) == 1:
        allowed = "all variables take one of: " + ", ".join(map(str, next(iter(uniq))))
    else:
        allowed = "; ".join(f"{k}: {{{', '.join(map(str, v))}}}" for k, v in doms.items())
    return variables, allowed


def run_llm_direct(spec: dict, cot: bool = False) -> SystemOutput:
    variables, allowed = _variables_blurb(spec)
    module = dspy.ChainOfThought(DirectSolve) if cot else dspy.Predict(DirectSolve)
    try:
        pred = module(problem=spec["nl_description"], variables=variables, allowed_values=allowed)
    except Exception as e:  # noqa: BLE001
        return SystemOutput(error=f"llm error: {e}")
    return _answer_to_output(pred.answer)


# --- savanty variants ---------------------------------------------------------------


def _run_savanty(spec: dict, enable_repair: bool, repair_mode: str) -> SystemOutput:
    res = solve_optimization_problem(
        spec["nl_description"],
        enable_repair=enable_repair,
        max_repair_iters=3,
        repair_mode=repair_mode,
    )
    if res.error and not res.infeasible:
        return SystemOutput(
            error=res.error,
            repair_iters=res.repair_iters,
            final_failure_type=res.final_failure_type,
            extra={"repair_trace": res.repair_trace},
        )
    return SystemOutput(
        assignment=res.assignment if not res.infeasible else None,
        infeasible=res.infeasible,
        repair_iters=res.repair_iters,
        final_failure_type=res.final_failure_type,
        extra={"repair_trace": res.repair_trace},
    )


# Registry: name -> callable(spec) -> SystemOutput
SYSTEMS = {
    "B1_llm_direct": lambda spec: run_llm_direct(spec, cot=False),
    "B2_llm_cot": lambda spec: run_llm_direct(spec, cot=True),
    "B3_savanty_norepair": lambda spec: _run_savanty(spec, False, "typed_core"),
    "B4_logiclm_style": lambda spec: _run_savanty(spec, True, "generic"),
    "B5_savanty_typed_core": lambda spec: _run_savanty(spec, True, "typed_core"),
}
