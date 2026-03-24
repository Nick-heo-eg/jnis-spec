"""
forbidden_decision_semantics.py — invalid example: decision semantics in trace.

This file demonstrates a FORBIDDEN pattern under the J-NIS non_interference contract.
Using "allow" or "deny" keywords in trace violates inv_no_decision_semantics.
"""
import json
from pathlib import Path

TRACE_PATH = Path("trace.jsonl")


def write_bad_trace():
    # FORBIDDEN: trace record contains decision semantic keywords "allow" and "deny"
    record = {
        "trace_id": "bad-trace-001",
        "contract_hash": "placeholder",
        "execution_id": "exec-bad",
        "verdict": "allow",       # FORBIDDEN: decision semantic keyword
        "fallback": "deny",       # FORBIDDEN: decision semantic keyword
    }
    with open(TRACE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    write_bad_trace()
