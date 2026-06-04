"""Figures for the paper from results/rows.jsonl (primary model gemma4:31b).

Usage:  .venv/bin/python -m results.plot
Writes: ../savanty-paper/figures/feasibility_by_tier.pdf
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).parent.parent
ROWS = ROOT / "results" / "rows.jsonl"
FIGDIR = ROOT.parent / "savanty-paper" / "figures"
MODEL = "gemma4:31b"

SYS = ["B1_llm_direct", "B2_llm_cot", "B3_savanty_norepair",
       "B4_logiclm_style", "B5_savanty_typed_core"]
LABEL = {
    "B1_llm_direct": "Direct",
    "B2_llm_cot": "Chain-of-thought",
    "B3_savanty_norepair": "ASP, no repair",
    "B4_logiclm_style": "ASP, generic repair",
    "B5_savanty_typed_core": "ASP, typed+core",
}
COLORS = ["#9aa0a6", "#4c78a8", "#bcd2e8", "#e0a458", "#3b7a57"]
TIERS = [("small", "Small"), ("stress", "Stress"), ("xl", "XL")]


def tier(v):
    return v if v in ("stress", "xl") else "small"


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(ln) for ln in ROWS.read_text().splitlines() if ln.strip()]
    rows = [r for r in rows if r["model"] == MODEL]

    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    x = range(len(TIERS))
    width = 0.16
    for i, s in enumerate(SYS):
        ys = []
        for tkey, _ in TIERS:
            rs = [r for r in rows if r["system"] == s and tier(r["variant"]) == tkey]
            ys.append(100 * mean([r["feasible_correct"] for r in rs]))
        ax.bar([xx + (i - 2) * width for xx in x], ys, width,
               label=LABEL[s], color=COLORS[i])
    ax.set_xticks(list(x))
    ax.set_xticklabels([t[1] for t in TIERS])
    ax.set_ylabel("Feasibility accuracy (%)")
    ax.set_ylim(0, 105)
    ax.legend(fontsize=7, ncol=2, loc="lower center")
    ax.set_title(f"{MODEL}: accuracy by problem-size tier", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGDIR / "feasibility_by_tier.pdf")
    plt.close(fig)
    print(f"Wrote {FIGDIR/'feasibility_by_tier.pdf'}")


if __name__ == "__main__":
    main()
