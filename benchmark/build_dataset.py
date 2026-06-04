"""Generate the benchmark: label every spec with ground truth and write JSON files.

Run:  .venv/bin/python -m benchmark.build_dataset
"""

from __future__ import annotations

import json
from pathlib import Path

from benchmark.generators import all_instances
from benchmark.reference import ground_truth

PROBLEMS_DIR = Path(__file__).parent / "problems"


def build(write: bool = True) -> list[dict]:
    specs = all_instances()
    labelled = []
    mismatches = []
    for spec in specs:
        gt = ground_truth(spec)
        spec["feasible"] = gt["feasible"]
        spec["optimal_value"] = gt["optimal_value"]
        # Keep a reference witness for debugging (not shown to any solver).
        spec["_reference_witness"] = gt["witness"]

        variant = spec["variant"]
        if variant == "infeasible" and gt["feasible"]:
            mismatches.append(f"{spec['id']}: labelled infeasible but a solution exists")
        if variant in ("feasible", "tight", "stress", "xl") and not gt["feasible"]:
            mismatches.append(f"{spec['id']}: labelled {variant} but is infeasible")
        labelled.append(spec)

    if mismatches:
        raise SystemExit("Variant/ground-truth mismatches:\n  " + "\n  ".join(mismatches))

    if write:
        PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
        for spec in labelled:
            (PROBLEMS_DIR / f"{spec['id']}.json").write_text(json.dumps(spec, indent=2))

    return labelled


def summary(labelled: list[dict]) -> str:
    from collections import Counter

    by_domain = Counter(s["domain"] for s in labelled)
    by_variant = Counter(s["variant"] for s in labelled)
    n_opt = sum(1 for s in labelled if s["optimal_value"] is not None)
    lines = [f"Total instances: {len(labelled)}"]
    lines.append("By domain: " + ", ".join(f"{k}={v}" for k, v in sorted(by_domain.items())))
    lines.append("By variant: " + ", ".join(f"{k}={v}" for k, v in sorted(by_variant.items())))
    lines.append(f"Optimisation instances (with optimum): {n_opt}")
    return "\n".join(lines)


if __name__ == "__main__":
    labelled = build(write=True)
    print(summary(labelled))
    print(f"\nWrote {len(labelled)} problems to {PROBLEMS_DIR}")
