"""Backend smoke test for Ollama Cloud.

1) confirm the chosen model tags are live via GET /api/tags
2) run a 1-call DSPy completion through Savanty's LM factory

Usage:  .venv/bin/python -m experiments.smoke
Requires OLLAMA_API_KEY (read from environment or a .env file).
"""

from __future__ import annotations

import os
import urllib.request

from dotenv import load_dotenv

load_dotenv()

WANT = ["gemma4:31b-cloud", "deepseek-v3.2:cloud", "qwen3.5:397b-cloud"]


def list_models() -> list[str]:
    key = os.environ["OLLAMA_API_KEY"]
    req = urllib.request.Request(
        "https://ollama.com/api/tags", headers={"Authorization": f"Bearer {key}"}
    )
    import json

    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return [m.get("name") or m.get("model") for m in data.get("models", [])]


def main() -> None:
    if not os.getenv("OLLAMA_API_KEY"):
        raise SystemExit("OLLAMA_API_KEY not set (export it or put it in .env).")

    try:
        available = list_models()
        print(f"/api/tags returned {len(available)} models")
        for w in WANT:
            base = w.replace(":cloud", "")
            hit = any(w == a or base in (a or "") for a in available)
            print(f"  {'OK ' if hit else 'MISSING'} {w}")
    except Exception as e:  # noqa: BLE001
        print(f"/api/tags check failed (continuing to chat test): {e}")

    import dspy

    import savanty.solver as solver_mod

    os.environ.setdefault("SAVANTY_LLM_MODEL", "gemma4:31b-cloud")
    solver_mod._lm_instance = None
    solver_mod._ensure_lm_configured()
    out = dspy.settings.lm("Reply with the single word: pong")
    print("chat test reply:", out)


if __name__ == "__main__":
    main()
