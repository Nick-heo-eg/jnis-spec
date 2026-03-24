"""
enforcement/jnis_gate.py — J-NIS enforcement gate

Reads the latest trace record from logs/trace.jsonl and determines
whether execution is permitted based on J-NIS invariants.

Returns True only if:
  - trace file exists and is non-empty
  - last record has policy_input, action_decisions, proof
  - proof.decision_made is False
  - no action_decisions entry has executed == True

Used by jnis_exec.py and the git pre-commit hook.
"""
from __future__ import annotations

import json
import pathlib
import sys

TRACE_PATH = pathlib.Path(__file__).parent.parent / "logs" / "trace.jsonl"


def load_latest_trace() -> dict | None:
    if not TRACE_PATH.exists():
        return None
    lines = [l.strip() for l in TRACE_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return None


def allow_execution(trace: dict | None) -> tuple[bool, str]:
    if trace is None:
        return False, "NO_TRACE: trace file missing or empty"

    if "policy_input" not in trace:
        return False, "INVALID_TRACE: missing policy_input"
    if "action_decisions" not in trace:
        return False, "INVALID_TRACE: missing action_decisions"
    if "proof" not in trace:
        return False, "INVALID_TRACE: missing proof"

    proof = trace["proof"]
    if proof.get("decision_made") is not False:
        return False, f"DECISION_MADE_VIOLATION: proof.decision_made = {proof.get('decision_made')!r}"

    for ad in trace.get("action_decisions", []):
        if ad.get("executed") is True:
            return False, f"EXECUTED_VIOLATION: action '{ad.get('action')}' has executed=True in trace"

    return True, "GATE_PASSED"


def main() -> None:
    trace = load_latest_trace()
    allowed, reason = allow_execution(trace)
    if allowed:
        print(f"JNIS_GATE: {reason}")
        sys.exit(0)
    else:
        print(f"JNIS_GATE BLOCKED: {reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
