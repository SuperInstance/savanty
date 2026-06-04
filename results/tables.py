"""Aggregate results/rows.jsonl into summary tables + LaTeX, with B5-vs-B4 significance.

Usage:  .venv/bin/python -m results.tables
Writes: results/metrics.csv, results/summary.txt, results/tables.tex
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
ROWS_PATH = ROOT / "results" / "rows.jsonl"
RESULTS_DIR = ROOT / "results"

SYSTEM_ORDER = [
    "B1_llm_direct",
    "B2_llm_cot",
    "B3_savanty_norepair",
    "B4_logiclm_style",
    "B5_savanty_typed_core",
]
SYSTEM_LABEL = {
    "B1_llm_direct": "LLM-direct",
    "B2_llm_cot": "LLM-CoT",
    "B3_savanty_norepair": "Savanty (no repair)",
    "B4_logiclm_style": "Logic-LM-style repair",
    "B5_savanty_typed_core": "Savanty (typed+core)",
}


def load_rows() -> list[dict]:
    if not ROWS_PATH.exists():
        raise SystemExit(f"No rows at {ROWS_PATH}; run experiments.run_eval first.")
    return [json.loads(ln) for ln in ROWS_PATH.read_text().splitlines() if ln.strip()]


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def aggregate(rows, by_model=False):
    """Return {(model?, system): metrics}. metrics over the relevant instance subsets."""
    groups = defaultdict(list)
    for r in rows:
        key = (r["model"], r["system"]) if by_model else (r["system"],)
        groups[key].append(r)

    table = {}
    for key, rs in groups.items():
        feas = [r for r in rs if r["gt_feasible"]]
        infeas = [r for r in rs if not r["gt_feasible"]]
        opt = [r for r in rs if r["optimality_gap"] is not None]
        table[key] = {
            "n": len(rs),
            "feasible_acc": _mean([r["feasible_correct"] for r in rs]),
            "csr_feasible": _mean([r["csr"] for r in feas]),
            "spurious_unsat": _mean([r["spurious_unsat"] for r in feas]) if feas else float("nan"),
            "false_feasible": _mean([r["false_feasible"] for r in infeas]) if infeas else float("nan"),
            "opt_gap": _mean([r["optimality_gap"] for r in opt]) if opt else float("nan"),
            "repair_iters": _mean([r["repair_iters"] for r in rs]),
            "latency": _mean([r["latency_s"] for r in rs]),
            "tokens": _mean([r["llm_tokens"] for r in rs]),
        }
    return table


def paired_mcnemar_like(rows):
    """Paired comparison B5 vs B4 on feasible_correct, per (model, problem). Returns
    (n_b5_only, n_b4_only, two-sided sign-test p-value)."""
    idx = {}
    for r in rows:
        if r["system"] in ("B4_logiclm_style", "B5_savanty_typed_core"):
            idx[(r["model"], r["problem_id"], r["system"])] = r["feasible_correct"]
    b5_only = b4_only = both = neither = 0
    seen = {(m, p) for (m, p, s) in idx}
    for (m, p) in seen:
        b4 = idx.get((m, p, "B4_logiclm_style"))
        b5 = idx.get((m, p, "B5_savanty_typed_core"))
        if b4 is None or b5 is None:
            continue
        if b5 and not b4:
            b5_only += 1
        elif b4 and not b5:
            b4_only += 1
        elif b4 and b5:
            both += 1
        else:
            neither += 1
    # Two-sided sign test on discordant pairs.
    n = b5_only + b4_only
    k = min(b5_only, b4_only)
    p = 1.0
    if n > 0:
        p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))
    return {"b5_only": b5_only, "b4_only": b4_only, "both": both, "neither": neither, "p": p}


def fmt(x, pct=False):
    if isinstance(x, float) and math.isnan(x):
        return "--"
    return f"{100 * x:.1f}" if pct else f"{x:.2f}"


def write_csv(table_by_model):
    with (RESULTS_DIR / "metrics.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "system", "n", "feasible_acc", "csr_feasible",
                    "spurious_unsat", "false_feasible", "opt_gap", "repair_iters",
                    "latency_s", "tokens"])
        for (model, system), m in sorted(table_by_model.items()):
            w.writerow([model, system, m["n"], f"{m['feasible_acc']:.4f}",
                        f"{m['csr_feasible']:.4f}", f"{m['spurious_unsat']:.4f}",
                        f"{m['false_feasible']:.4f}", f"{m['opt_gap']:.4f}",
                        f"{m['repair_iters']:.3f}", f"{m['latency']:.3f}",
                        f"{m['tokens']:.0f}"])


def summary_text(overall, sig):
    lines = ["=== Overall (pooled across models) ===",
             f"{'system':<24} {'feas_acc%':>9} {'CSR%':>7} {'spurUNSAT%':>11} "
             f"{'falseFEAS%':>11} {'optGAP':>7} {'iters':>6}"]
    for s in SYSTEM_ORDER:
        m = overall.get((s,))
        if not m:
            continue
        lines.append(
            f"{SYSTEM_LABEL[s]:<24} {fmt(m['feasible_acc'], 1):>9} {fmt(m['csr_feasible'], 1):>7} "
            f"{fmt(m['spurious_unsat'], 1):>11} {fmt(m['false_feasible'], 1):>11} "
            f"{fmt(m['opt_gap']):>7} {fmt(m['repair_iters']):>6}"
        )
    lines.append("")
    lines.append("=== B5 (typed+core) vs B4 (Logic-LM-style), paired on feasible_correct ===")
    lines.append(f"B5 wins only: {sig['b5_only']}   B4 wins only: {sig['b4_only']}   "
                 f"both: {sig['both']}   neither: {sig['neither']}   sign-test p={sig['p']:.4g}")
    return "\n".join(lines)


def write_tex(overall):
    rows = []
    for s in SYSTEM_ORDER:
        m = overall.get((s,))
        if not m:
            continue
        rows.append(
            f"{SYSTEM_LABEL[s]} & {fmt(m['feasible_acc'],1)} & {fmt(m['csr_feasible'],1)} & "
            f"{fmt(m['spurious_unsat'],1)} & {fmt(m['false_feasible'],1)} & "
            f"{fmt(m['opt_gap'])} & {fmt(m['repair_iters'])} \\\\"
        )
    body = "\n".join(rows)
    tex = (
        "\\begin{tabular}{lrrrrrr}\n\\toprule\n"
        "System & Feas.\\ acc. & CSR & Spur.\\ UNSAT & False feas. & Opt.\\ gap & Iters \\\\\n"
        "\\midrule\n" + body + "\n\\bottomrule\n\\end{tabular}\n"
    )
    (RESULTS_DIR / "tables.tex").write_text(tex)


def aggregate_by_variant(rows):
    """Feasibility accuracy per (system, variant) — shows where the core helps."""
    groups = defaultdict(list)
    for r in rows:
        groups[(r["system"], r["variant"])].append(r)
    return {k: _mean([r["feasible_correct"] for r in rs]) for k, rs in groups.items()}


def write_variant_tex(by_variant):
    variants = ["feasible", "tight", "infeasible"]
    head = " & ".join(v.capitalize() for v in variants)
    rows = []
    for s in SYSTEM_ORDER:
        cells = " & ".join(fmt(by_variant.get((s, v), float("nan")), 1) for v in variants)
        rows.append(f"{SYSTEM_LABEL[s]} & {cells} \\\\")
    tex = (
        "\\begin{tabular}{lrrr}\n\\toprule\n"
        f"System & {head} \\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n"
    )
    (RESULTS_DIR / "tables_variant.tex").write_text(tex)


def main():
    rows = load_rows()
    overall = aggregate(rows, by_model=False)
    by_model = aggregate(rows, by_model=True)
    by_variant = aggregate_by_variant(rows)
    sig = paired_mcnemar_like(rows)
    write_csv(by_model)
    write_tex(overall)
    write_variant_tex(by_variant)
    txt = summary_text(overall, sig)
    (RESULTS_DIR / "summary.txt").write_text(txt)
    print(txt)
    print("\n=== Feasibility accuracy by variant (%) ===")
    for s in SYSTEM_ORDER:
        cells = "  ".join(
            f"{v}={fmt(by_variant.get((s, v), float('nan')), 1)}"
            for v in ("feasible", "tight", "infeasible")
        )
        print(f"  {SYSTEM_LABEL[s]:<24} {cells}")
    print(f"\nWrote metrics.csv, summary.txt, tables.tex, tables_variant.tex to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
