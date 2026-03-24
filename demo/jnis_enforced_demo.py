"""
demo/jnis_enforced_demo.py — J-NIS enforced execution demo

Demonstrates the full enforcement path:
  1. AI system evaluates actions via gate
  2. Trace is written to logs/trace.jsonl
  3. Commit is attempted via jnis_exec.py (the only allowed path)
  4. Direct git commit is never called from this script

The AI layer cannot call git directly. Only jnis_exec.py may do so,
and only after gate validation passes.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Project root
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TRACE_PATH = ROOT / "logs" / "trace.jsonl"
TRACE_PATH.parent.mkdir(exist_ok=True)

ACTION_LEVELS = {
    "refresh_state": 1, "restart_embedding_service": 1, "unload_embedding_model": 1,
    "scale_down_idle_workers": 2, "pause_scheduler": 2, "resume_scheduler": 2,
    "freeze_policy": 2, "enter_safe_mode": 3, "kill_all_workers": 3,
}


def gate(action: str, pi: dict) -> dict:
    level = ACTION_LEVELS.get(action, 99)
    if not pi["collector_ok"]:
        return {"allowed": False, "reason": "NO_OBSERVATION", "action_level": level}
    if pi["embed_state"] in ("UNKNOWN", "NOT_LOADED"):
        return {"allowed": False, "reason": "UNKNOWN_STATE", "action_level": level}
    if pi["stale"] and level >= 2:
        return {"allowed": False, "reason": "STALE_STATE", "action_level": level}
    return {"allowed": True, "reason": "GATE_PASSED", "action_level": level}


def main() -> None:
    print("=== J-NIS Enforced Demo ===\n")

    # Step 1: AI evaluates state
    policy_input = {
        "embed_state":  "ACTIVE",
        "embed_rss":    512,
        "embed_idle":   30,
        "stale":        False,
        "collector_ok": True,
    }
    actions = ["restart_embedding_service", "pause_scheduler"]
    decisions = [{"action": a, **gate(a, policy_input), "executed": False} for a in actions]

    print("Step 1 — AI evaluates actions:")
    for d in decisions:
        print(f"  {d['action']}: allowed={d['allowed']}, reason={d['reason']}")

    # Step 2: Write trace BEFORE any execution attempt
    record = {
        "jnis_version":     "1.1.0",
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "policy_input":     policy_input,
        "action_decisions": decisions,
        "proof":            {"actor": "enforced_demo", "authority": "evidence_only", "decision_made": False},
    }
    with open(TRACE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    print(f"\nStep 2 — Trace written to {TRACE_PATH}")
    print(f"  decision_made: {record['proof']['decision_made']}")
    print(f"  executed:      {[d['executed'] for d in decisions]}")

    # Step 3: Attempt commit via jnis_exec.py (the only allowed path)
    # The AI layer does NOT call git directly. Ever.
    print("\nStep 3 — Attempting commit via jnis_exec.py (external executor):")
    result = subprocess.run(
        [sys.executable, str(ROOT / "enforcement" / "jnis_exec.py"),
         "--action", "commit",
         "--commit-message", "demo: enforced commit via jnis_exec"],
        capture_output=False,
    )

    if result.returncode == 0:
        print("\nRESULT: Commit executed by external executor.")
    elif result.returncode == 1:
        print("\nRESULT: BLOCKED_BY_JNIS — gate did not pass.")
    else:
        print(f"\nRESULT: Execution error (exit {result.returncode})")

    print("\n=== Demo complete ===")
    print("The AI layer never called git directly.")
    print("Run: python scripts/validate_enforcement.py")


if __name__ == "__main__":
    main()
