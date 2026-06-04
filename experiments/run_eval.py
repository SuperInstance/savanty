"""Evaluation harness: problems x systems x models -> scored rows + metrics.

Usage:
  .venv/bin/python -m experiments.run_eval --limit 3 --models gemma4:31b-cloud
  .venv/bin/python -m experiments.run_eval            # full run, all models/systems

Requires OLLAMA_API_KEY in the environment. Rows are appended to results/rows.jsonl and
completed (model, system, problem) tuples are skipped on re-run (experiment-level caching).
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import dspy
from dotenv import load_dotenv

import savanty.solver as solver_mod
from benchmark.verify import objective_value, verify
from experiments.baselines import SYSTEMS

load_dotenv()  # pick up OLLAMA_API_KEY / SAVANTY_LLM_MODEL from a .env file if present

ROOT = Path(__file__).parent.parent
PROBLEMS_DIR = ROOT / "benchmark" / "problems"
RESULTS_DIR = ROOT / "results"
ROWS_PATH = RESULTS_DIR / "rows.jsonl"

DEFAULT_MODELS = ["gemma4:31b", "deepseek-v3.2", "qwen3.5:397b"]


def load_problems(limit: int | None) -> list[dict]:
    specs = [json.loads(p.read_text()) for p in sorted(PROBLEMS_DIR.glob("*.json"))]
    return specs[:limit] if limit else specs


def configure_model(model: str) -> None:
    """Point both Savanty and the bare DSPy baselines at `model` on Ollama Cloud."""
    os.environ["SAVANTY_LLM_MODEL"] = model
    solver_mod._lm_instance = None
    solver_mod._ensure_lm_configured()  # sets dspy.settings.lm globally


def optimality_gap(spec: dict, assignment: dict) -> float | None:
    obj = spec.get("objective")
    opt = spec.get("optimal_value")
    if not obj or opt is None:
        return None
    val = objective_value(spec, assignment)
    if val is None:
        return None
    denom = abs(opt) if opt else 1.0
    regret = (opt - val) if obj["sense"] == "max" else (val - opt)
    return max(0.0, regret / denom)


def score(spec: dict, out) -> dict:
    gt_feasible = spec["feasible"]
    row: dict = {
        "gt_feasible": gt_feasible,
        "gt_optimal": spec.get("optimal_value"),
        "reported": "error" if out.error else ("infeasible" if out.infeasible else "solution"),
        "repair_iters": out.repair_iters,
        "final_failure_type": out.final_failure_type,
        "csr": 0.0,
        "feasible_correct": False,
        "spurious_unsat": False,
        "false_feasible": False,
        "optimality_gap": None,
        "error": out.error,
    }
    if gt_feasible:
        if out.infeasible:
            row["spurious_unsat"] = True
        elif out.assignment is not None:
            vr = verify(spec, out.assignment)
            row["csr"] = round(vr.csr, 4)
            row["feasible_correct"] = vr.feasible
            if vr.feasible:
                row["optimality_gap"] = optimality_gap(spec, out.assignment)
    else:  # ground truth is infeasible -> correct behaviour is to declare infeasible
        if out.infeasible:
            row["feasible_correct"] = True
            row["csr"] = 1.0
        elif out.assignment is not None:
            row["false_feasible"] = True
    return row


def already_done() -> set[tuple]:
    done = set()
    if ROWS_PATH.exists():
        for line in ROWS_PATH.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["model"], r["system"], r["problem_id"]))
    return done


def lm_usage_snapshot() -> tuple[int, int]:
    """(num_calls, total_tokens) from the active DSPy LM history."""
    hist = getattr(dspy.settings.lm, "history", []) or []
    tokens = 0
    for h in hist:
        u = h.get("usage") or {}
        tokens += int(u.get("total_tokens", 0) or 0)
    return len(hist), tokens


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--models", nargs="*", default=DEFAULT_MODELS)
    ap.add_argument("--systems", nargs="*", default=list(SYSTEMS))
    args = ap.parse_args()

    if not os.getenv("OLLAMA_API_KEY"):
        raise SystemExit("OLLAMA_API_KEY is not set. Export it before running the eval.")

    RESULTS_DIR.mkdir(exist_ok=True)
    problems = load_problems(args.limit)
    done = already_done()
    print(f"{len(problems)} problems x {len(args.systems)} systems x {len(args.models)} models")
    print(f"(skipping {len(done)} already-completed rows)")

    with ROWS_PATH.open("a") as fh:
        for model in args.models:
            configure_model(model)
            for spec in problems:
                for sysname in args.systems:
                    key = (model, sysname, spec["id"])
                    if key in done:
                        continue
                    calls0, toks0 = lm_usage_snapshot()
                    t0 = time.time()
                    try:
                        out = SYSTEMS[sysname](spec)
                    except Exception as e:  # noqa: BLE001
                        from experiments.baselines import SystemOutput

                        out = SystemOutput(error=f"crash: {e}")
                    latency = round(time.time() - t0, 3)
                    calls1, toks1 = lm_usage_snapshot()
                    row = {
                        "model": model,
                        "system": sysname,
                        "problem_id": spec["id"],
                        "domain": spec["domain"],
                        "variant": spec["variant"],
                        "size": spec["size"],
                        "latency_s": latency,
                        "llm_calls": calls1 - calls0,
                        "llm_tokens": toks1 - toks0,
                        **score(spec, out),
                    }
                    fh.write(json.dumps(row) + "\n")
                    fh.flush()
                    flag = (
                        "OK" if row["feasible_correct"] else
                        ("spurUNSAT" if row["spurious_unsat"] else
                         ("falseFEAS" if row["false_feasible"] else "wrong"))
                    )
                    print(
                        f"[{model:>18}] {sysname:>22} {spec['id']:<26} "
                        f"csr={row['csr']:.2f} {flag:<10} it={row['repair_iters']} {latency}s"
                    )
    print(f"\nDone. Rows -> {ROWS_PATH}")


if __name__ == "__main__":
    main()
