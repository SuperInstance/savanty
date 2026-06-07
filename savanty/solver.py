"""Core solver module for Savanty.

Pipeline: natural language --(LLM, DSPy)--> ASP encoding over a canonical ``assign(Var,Value)``
relation --(clingo)--> answer set. The novel piece is a **solver-grounded self-repair loop**:
when clingo reports a failure, the solver builds *typed, localized* diagnostics — in particular a
**minimal unsatisfiable core** over the model's own constraints — and asks the LLM to repair the
encoding. A ``generic`` repair mode (raw error message only) reproduces Logic-LM-style refinement
as a baseline.

The solver is now a **topologically-aware constraint engine**: after each ASP result, optional
post-processing applies:

1. **TernaryL Gate** — maps solver conviction onto {Sure (+1), Uncertain (0), Impossible (-1)}
   with a Leminal Zone deadband.
2. **SAEP Veto Layer** — checks the assignment against a 4-tier governance hierarchy
   (Room → Sector → Portfolio → Market).
3. **Symmetry-Skeptic** — flags solutions that break topological symmetry in the
   constraint graph.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import dspy

from savanty.asp_runtime import parse_assign_atoms, run_clingo
from savanty.dspy_modules import (
    ASPRepair,
    ASPRepairGeneric,
    InteractiveProblemSolver,
    ProblemSuitabilityCheck,
    SolutionVisualization,
)
from savanty.logging_config import logger
from savanty.ternary_l import TernaryLEngine, TernaryLResult, TritGate, LeminalZone
from savanty.saep_veto import VetoEngine, VetoResult, SAEPConstraint, SAEPTier
from savanty.symmetry_skeptic import SymmetrySkeptic, SymmetrySkepticResult

# LLM configuration (lazy initialization)
_lm_instance = None

OLLAMA_BASE_URL = "https://ollama.com/v1"
DEFAULT_OLLAMA_MODEL = "gemma4:31b"


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""

    pass


def _get_configured_lm():
    """Build a DSPy LM. Prefers Ollama Cloud (OpenAI-compatible); falls back to OpenAI.

    Env:
      SAVANTY_LLM_MODEL : model tag (e.g. "gemma4:31b-cloud"); default depends on backend.
      OLLAMA_API_KEY    : bearer key for Ollama Cloud (https://ollama.com/v1).
      OPENAI_API_KEY    : used only when OLLAMA_API_KEY is absent.
    """
    ollama_key = os.getenv("OLLAMA_API_KEY")
    if ollama_key:
        model = os.getenv("SAVANTY_LLM_MODEL", DEFAULT_OLLAMA_MODEL)
        # DSPy/LiteLLM "openai/<model>" provider routed at Ollama's OpenAI-compatible endpoint.
        lm_id = model if model.startswith("openai/") else f"openai/{model}"
        logger.debug(f"Configuring Ollama Cloud LM: {lm_id} @ {OLLAMA_BASE_URL}")
        # Reasoning models (qwen3.5, deepseek-v3.2) emit long reasoning before the answer;
        # a small completion budget truncates them mid-thought and yields empty output.
        max_tokens = int(os.getenv("SAVANTY_MAX_TOKENS", "16000"))
        return dspy.LM(
            lm_id,
            api_key=ollama_key,
            api_base=OLLAMA_BASE_URL,
            model_type="chat",
            temperature=0.0,
            max_tokens=max_tokens,
        )

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ConfigurationError(
            "Set OLLAMA_API_KEY (for Ollama Cloud) or OPENAI_API_KEY. "
            "e.g. export OLLAMA_API_KEY=your_key_here"
        )
    model = os.getenv("SAVANTY_LLM_MODEL", "openai/gpt-4o")
    logger.debug(f"Configuring OpenAI LM: {model}")
    return dspy.LM(model, api_key=openai_api_key)


def _ensure_lm_configured():
    """Ensure the LLM is configured before use."""
    global _lm_instance
    if _lm_instance is None:
        _lm_instance = _get_configured_lm()
        dspy.settings.configure(lm=_lm_instance)
        logger.info("LLM configured successfully")


class ProblemSolverResult:
    """Wrapper class for problem solver results."""

    def __init__(
        self,
        needs_more_info: bool = False,
        questions: list[str] = None,
        solution: str = None,
        asp_code: str = None,
        visualization_html: str = None,
        error: str = None,
        not_suitable: bool = False,
        suggested_tool: str = None,
        suitability_reason: str = None,
        assignment: dict[str, str] | None = None,
        infeasible: bool = False,
        repair_trace: list[dict] | None = None,
        repair_iters: int = 0,
        final_failure_type: str | None = None,
        # ── Hybrid Manifold post-processing ─────────────────────────────────────
        ternary_result: TernaryLResult | None = None,
        veto_result: VetoResult | None = None,
        symmetry_result: SymmetrySkepticResult | None = None,
        topological_scores: dict[str, float] | None = None,
    ):
        self.needs_more_info = needs_more_info
        self.questions = questions or []
        self.solution = solution
        self.asp_code = asp_code
        self.visualization_html = visualization_html
        self.error = error
        self.not_suitable = not_suitable
        self.suggested_tool = suggested_tool
        self.suitability_reason = suitability_reason
        # Canonical assignment + repair instrumentation (used by the eval harness).
        self.assignment = assignment
        self.infeasible = infeasible
        self.repair_trace = repair_trace or []
        self.repair_iters = repair_iters
        self.final_failure_type = final_failure_type
        # Hybrid Manifold post-processing
        self.ternary_result = ternary_result
        self.veto_result = veto_result
        self.symmetry_result = symmetry_result
        self.topological_scores = topological_scores or {}


# --- ASP assembly + solving --------------------------------------------------------


@dataclass
class SolveOutcome:
    """Structured result of compiling + solving one ASP encoding."""

    failure_type: str  # ok | syntax_error | unsat | empty
    assignment: dict[str, str] = field(default_factory=dict)
    asp_code: str = ""
    solver_feedback: str = ""
    unsat_core: list[str] = field(default_factory=list)
    optimal: bool = False


def _split_rules(rules: list[str]) -> tuple[list[str], list[str]]:
    """Partition rules into integrity constraints (start with ':-') and base rules."""
    constraints, base = [], []
    for r in rules:
        (constraints if r.strip().startswith(":-") else base).append(r)
    return constraints, base


def assemble_program(components: dict[str, Any], with_optimize: bool = True) -> str:
    """Assemble a full ASP program string from {facts, rules, optimize}."""
    facts = components.get("facts", []) or []
    rules = components.get("rules", []) or []
    optimize = (components.get("optimize") or "").strip() if with_optimize else ""
    parts = list(facts) + list(rules)
    if optimize:
        parts.append(optimize)
    parts.append("#show assign/2.")
    return "\n".join(parts)


def minimal_unsat_core(components: dict[str, Any]) -> list[str]:
    """Deletion-filtering minimal unsatisfiable subset over the integrity constraints.

    Operates only on the model's *own* constraints (no ground-truth leakage). Optimisation
    is dropped — this is a pure satisfiability question. Returns a minimal subset of
    constraints that is still unsatisfiable together with the base rules/facts; removing any
    one of them would make the program satisfiable.
    """
    facts = components.get("facts", []) or []
    constraints, base = _split_rules(components.get("rules", []) or [])
    base_prog = "\n".join(list(facts) + list(base))

    def sat(subset: list[str]) -> bool:
        prog = base_prog + "\n" + "\n".join(subset) + "\n#show assign/2."
        res = run_clingo(prog)
        # Treat a syntax error as "satisfiable" here so we don't wrongly blame a constraint
        # for a parse failure elsewhere; UNSAT only counts as genuine unsatisfiability.
        return res.error is not None or res.sat

    if sat(constraints):  # base+all-constraints is actually SAT -> no core
        return []
    core = list(constraints)
    for c in list(constraints):
        trial = [x for x in core if x != c]
        if not sat(trial):  # still UNSAT without c -> c is not needed in the core
            core = trial
    return core


def compile_and_solve(components: dict[str, Any]) -> SolveOutcome:
    """Compile {facts, rules, optimize} to ASP, solve with clingo, classify the outcome."""
    program = assemble_program(components, with_optimize=True)
    res = run_clingo(program)

    if res.error:
        return SolveOutcome(
            failure_type="syntax_error", asp_code=program, solver_feedback=res.error.strip()
        )

    if not res.sat:
        core = minimal_unsat_core(components)
        return SolveOutcome(
            failure_type="unsat",
            asp_code=program,
            unsat_core=core,
            solver_feedback="clingo found no answer set (unsatisfiable).",
        )

    assignment = parse_assign_atoms(res.symbols)
    if not assignment:
        return SolveOutcome(
            failure_type="empty",
            asp_code=program,
            solver_feedback="The program is satisfiable but emitted no assign/2 atoms.",
        )

    return SolveOutcome(
        failure_type="ok", assignment=assignment, asp_code=program, optimal=res.optimal
    )


def _build_feedback(outcome: SolveOutcome, repair_mode: str) -> str:
    """Construct the repair feedback string for a failure outcome."""
    if repair_mode == "generic":
        # Logic-LM-style: just hand back the raw solver message, no taxonomy, no core.
        return outcome.solver_feedback

    # typed_core (ours): typed guidance + minimal conflicting constraints when UNSAT.
    if outcome.failure_type == "syntax_error":
        return (
            f"clingo could not ground/parse the program. Error:\n{outcome.solver_feedback}\n"
            "Fix the offending rule; ensure all rules are valid ASP and variables are safe."
        )
    if outcome.failure_type == "unsat":
        if outcome.unsat_core:
            core_txt = "\n".join(f"  - {c}" for c in outcome.unsat_core)
            return (
                "The following integrity constraints are JOINTLY UNSATISFIABLE (a minimal "
                f"conflicting set):\n{core_txt}\n"
                "Exactly these constraints cannot all hold together. If one of them "
                "misformalizes the problem, correct or remove it. If the problem is genuinely "
                "infeasible, leave the encoding unchanged."
            )
        return "The program is unsatisfiable. Reconsider whether a constraint is too strong."
    if outcome.failure_type == "empty":
        return (
            "The program solved but produced no assign(Var,Value) decisions. Add the choice "
            "rule that generates assign/2 for every decision variable."
        )
    return outcome.solver_feedback


# --- public pipeline ---------------------------------------------------------------


def check_problem_suitability(problem_description: str) -> dict:
    """Check if a problem is suitable for ASP solving."""
    _ensure_lm_configured()
    logger.debug("Checking problem suitability for ASP")
    checker = dspy.Predict(ProblemSuitabilityCheck)
    result = checker(problem_description=problem_description)
    return {
        "is_suitable": result.is_suitable.lower(),
        "problem_type": result.problem_type,
        "reasoning": result.reasoning,
        "suggested_tool": result.suggested_tool,
        "confidence": result.confidence,
    }


def build_decision_schema(variables=None, domains=None) -> str:
    """Render the exact assign/2 namespace (variable ids + allowed values) for the LLM.

    All systems (Savanty and the LLM baselines) are given this same template, so the
    comparison is fair and every produced assignment lands in one canonical namespace.
    """
    if not variables:
        return (
            "Use the decision-variable identifiers exactly as they appear in the problem text "
            "(do not rename or renumber them) as the first argument of assign/2."
        )
    doms = domains or {}
    uniq = {tuple(v) for v in doms.values()} if doms else set()
    if len(uniq) == 1:
        allowed = "all variables take one of: " + ", ".join(map(str, next(iter(uniq))))
    elif doms:
        allowed = "; ".join(f"{k}: {{{', '.join(map(str, v))}}}" for k, v in doms.items())
    else:
        allowed = "as stated in the problem"
    return (
        "Decision variables (use these EXACT identifiers as the first argument of assign/2): "
        f"{', '.join(variables)}. Allowed values (second argument): {allowed}."
    )


def validate_and_parse_problem(
    description: str, additional_info: str = None, decision_schema: str = ""
) -> dict[str, Any]:
    """Validate and parse the problem into ASP components {facts, rules, optimize}."""
    _ensure_lm_configured()
    logger.debug("Validating and parsing problem")
    solver = InteractiveProblemSolver()
    try:
        result = solver(
            problem_description=description,
            additional_info=additional_info,
            decision_schema=decision_schema,
        )
        if result.needs_more_info:
            raise ValueError("NEEDS_MORE_INFO:" + json.dumps(result.questions))
        return _parse_components(result.program.program_components)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse program components: {e}")
        raise ValueError(f"Failed to parse program components from LLM output: {str(e)}") from e
    except Exception as e:
        if str(e).startswith("NEEDS_MORE_INFO:"):
            raise
        logger.error(f"Error in DSPy processing: {e}")
        raise ValueError(f"Error in DSPy processing: {str(e)}") from e


def _parse_components(raw: str) -> dict[str, Any]:
    """Parse a (possibly fenced) JSON object into {facts, rules, optimize}."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1] if "```" in text[3:] else text.strip("`")
        text = text[text.find("{") :] if "{" in text else text
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    data = json.loads(text)
    return {
        "facts": data.get("facts", []) or [],
        "rules": data.get("rules", []) or [],
        "optimize": data.get("optimize", "") or "",
    }


def _repair(problem_description, components, outcome, repair_mode, decision_schema=""):
    """Invoke the LLM repair step, returning new components (or raises ValueError)."""
    feedback = _build_feedback(outcome, repair_mode)
    current = json.dumps(components)
    if repair_mode == "generic":
        pred = dspy.Predict(ASPRepairGeneric)(
            problem_description=problem_description,
            decision_schema=decision_schema,
            current_program_components=current,
            solver_feedback=feedback,
        )
    else:
        pred = dspy.Predict(ASPRepair)(
            problem_description=problem_description,
            decision_schema=decision_schema,
            current_program_components=current,
            failure_type=outcome.failure_type,
            solver_feedback=feedback,
        )
    return _parse_components(pred.repaired_program_components), feedback


def _post_process(
    assignment: dict[str, str] | None,
    domains: dict[str, list[str]] | None,
    infeasible: bool,
    constraint_edges: list[tuple[str, str]] | None,
    saep_constraints: list[SAEPConstraint] | None,
    leminal_zone: LeminalZone | None,
) -> tuple[TernaryLResult | None, VetoResult | None, SymmetrySkepticResult | None, dict[str, float]]:
    """Run the Hybrid Manifold post-processing layers.

    Returns (ternary, veto, symmetry, scores_dict).
    """
    scores: dict[str, float] = {}

    # 1. TernaryL Gate
    ternary_engine = TernaryLEngine(leminal=leminal_zone)
    ternary_result = ternary_engine.evaluate(
        assignment=assignment, domains=domains, infeasible=infeasible
    )
    scores["ternary_aggregate_gate"] = float(ternary_result.aggregate_gate)
    scores["ternary_aggregate_conviction"] = ternary_result.aggregate_conviction

    # 2. SAEP Veto Layer
    veto_engine = VetoEngine(constraints=saep_constraints or [])
    veto_result = veto_engine.check(assignment=assignment)
    scores["veto_passed"] = 1.0 if veto_result.passed else 0.0

    # 3. Symmetry-Skeptic
    skeptic = SymmetrySkeptic()
    symmetry_result = skeptic.check(
        assignment=assignment,
        domains=domains,
        constraint_edges=constraint_edges,
    )
    scores["symmetry_passed"] = 1.0 if symmetry_result.passed else 0.0
    scores["symmetry_wasserstein"] = symmetry_result.wasserstein_distance

    return ternary_result, veto_result, symmetry_result, scores


def solve_optimization_problem(
    problem_description: str,
    additional_info: str = None,
    enable_repair: bool = True,
    max_repair_iters: int = 3,
    repair_mode: str = "typed_core",
    variables=None,
    domains=None,
    # ── Hybrid Manifold options ────────────────────────────────────────────────
    enable_topological_post: bool = True,
    saep_constraints: list[SAEPConstraint] | None = None,
    constraint_edges: list[tuple[str, str]] | None = None,
    leminal_zone: LeminalZone | None = None,
) -> ProblemSolverResult:
    """Solve a problem from its description.

    repair_mode: "typed_core" (ours — typed feedback + minimal UNSAT core) or
                 "generic" (Logic-LM-style — raw solver message only).
    variables/domains: optional decision-variable template (ids + allowed values) that the
                 generated assign/2 atoms must use; given identically to all baselines.

    Hybrid Manifold (topological post-processing) options:
    - enable_topological_post: run TernaryL, SAEP Veto, Symmetry-Skeptic after solving.
    - saep_constraints: additional governance constraints for the SAEP Veto Layer.
    - constraint_edges: variable pairs sharing a constraint (for symmetry detection).
    - leminal_zone: custom LeminalZone deadband thresholds.
    """
    logger.info("Starting optimization problem solving")
    decision_schema = build_decision_schema(variables, domains)
    try:
        suitability = check_problem_suitability(problem_description)
        if suitability["is_suitable"] == "no":
            logger.info(f"Problem not suitable for ASP: {suitability['reasoning']}")
            return ProblemSolverResult(
                not_suitable=True,
                suggested_tool=suitability.get("suggested_tool"),
                suitability_reason=suitability["reasoning"],
                error=f"This problem is better suited for a different tool. {suitability['reasoning']}",
            )

        components = validate_and_parse_problem(
            problem_description, additional_info, decision_schema
        )

        repair_trace: list[dict] = []
        outcome = compile_and_solve(components)
        iters = 0
        while enable_repair and outcome.failure_type != "ok" and iters < max_repair_iters:
            try:
                new_components, feedback = _repair(
                    problem_description, components, outcome, repair_mode, decision_schema
                )
            except Exception as e:  # repair generation failed; stop looping
                logger.warning(f"Repair step failed: {e}")
                break
            repair_trace.append(
                {
                    "iter": iters,
                    "failure_type": outcome.failure_type,
                    "unsat_core_size": len(outcome.unsat_core),
                    "feedback": feedback[:500],
                }
            )
            components = new_components
            outcome = compile_and_solve(components)
            iters += 1

        full_asp_code = outcome.asp_code

        # ── Hybrid Manifold post-processing ────────────────────────────────────────
        ternary_result: TernaryLResult | None = None
        veto_result: VetoResult | None = None
        symmetry_result: SymmetrySkepticResult | None = None
        topological_scores: dict[str, float] = {}

        if enable_topological_post:
            assignment_for_post = (
                outcome.assignment if outcome.failure_type == "ok" else None
            )
            ternary_result, veto_result, symmetry_result, topological_scores = _post_process(
                assignment=assignment_for_post,
                domains=domains,
                infeasible=(outcome.failure_type == "unsat"),
                constraint_edges=constraint_edges,
                saep_constraints=saep_constraints,
                leminal_zone=leminal_zone,
            )

        if outcome.failure_type == "ok":
            solution_str = "; ".join(f"{k}={v}" for k, v in sorted(outcome.assignment.items()))
            logger.info(f"Solved with {len(outcome.assignment)} assignments (iters={iters})")
            return ProblemSolverResult(
                solution=solution_str,
                asp_code=full_asp_code,
                assignment=outcome.assignment,
                repair_trace=repair_trace,
                repair_iters=iters,
                final_failure_type="ok",
                ternary_result=ternary_result,
                veto_result=veto_result,
                symmetry_result=symmetry_result,
                topological_scores=topological_scores,
            )

        if outcome.failure_type == "unsat":
            # Report infeasibility (the correct answer for over-constrained problems).
            logger.info(f"Reported infeasible after {iters} repair iters")
            return ProblemSolverResult(
                solution="UNSATISFIABLE",
                asp_code=full_asp_code,
                infeasible=True,
                repair_trace=repair_trace,
                repair_iters=iters,
                final_failure_type="unsat",
                ternary_result=ternary_result,
                veto_result=veto_result,
                symmetry_result=symmetry_result,
                topological_scores=topological_scores,
            )

        # syntax_error / empty that repair did not fix.
        return ProblemSolverResult(
            error=f"Could not produce a valid encoding ({outcome.failure_type}): "
            f"{outcome.solver_feedback}",
            asp_code=full_asp_code,
            repair_trace=repair_trace,
            repair_iters=iters,
            final_failure_type=outcome.failure_type,
            ternary_result=ternary_result,
            veto_result=veto_result,
            symmetry_result=symmetry_result,
            topological_scores=topological_scores,
        )

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        return ProblemSolverResult(error=str(e))
    except ValueError as e:
        if str(e).startswith("NEEDS_MORE_INFO:"):
            questions = json.loads(str(e)[16:])
            logger.info(f"Problem needs more info: {len(questions)} questions")
            return ProblemSolverResult(needs_more_info=True, questions=questions)
        logger.error(f"Validation error: {e}")
        return ProblemSolverResult(error=str(e))
    except Exception as e:
        logger.error(f"Error solving optimization problem: {e}", exc_info=True)
        return ProblemSolverResult(error=f"Error solving optimization problem: {str(e)}")


def generate_visualization(problem_description: str, solution: str) -> str:
    """Generate an HTML visualization of the solution using DSPy."""
    _ensure_lm_configured()
    try:
        visualizer = dspy.Predict(SolutionVisualization)
        result = visualizer(problem_description=problem_description, solution=solution)
        return result.visualization_html
    except Exception as e:
        logger.warning(f"Visualization generation failed: {e}")
        return f"<pre>{solution}</pre>"
