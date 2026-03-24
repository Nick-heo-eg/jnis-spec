"""
scripts/replay_demo.py — J-NIS replay-based invariant verifier

Reads a .jsonl trace file and verifies each record by replaying the gate function
against stored policy_input. Checks that the replay result matches the stored
action_decisions — without access to the original system.

This implements Level 2 and Level 3 compliance verification.

Usage:
    python scripts/replay_demo.py decisions.jsonl

Exit 0 = PASS, Exit 1 = FAIL
"""
from __future__ import annotations

import json
import pathlib
import sys

REQUIRED_PI_KEYS = frozenset({"embed_state", "embed_rss", "embed_idle", "stale", "collector_ok"})

SERVICE_INTERNAL_REASONS = {"AUTO_LEVEL_RESTRICTED"}


# ── Inline gate function (no external dependency) ────────────────────────────
# This is a standalone reimplementation of the J-NIS gate for replay verification.
# It is intentionally independent of any reference implementation.

def _gate_replay(action: str, policy_input: dict) -> dict:
    """
    Minimal J-NIS gate for replay. Pure function.
    Matches the gate contract in SPEC_NON_INTERFERENCE.md.
    """
    collector_ok = policy_input.get("collector_ok", False)
    embed_state  = policy_input.get("embed_state", "UNKNOWN")
    stale        = policy_input.get("stale", True)

    # Level thresholds — actions not in this map get level 99
    ACTION_LEVELS = {
        "refresh_state": 1, "restart_embedding_service": 1, "unload_embedding_model": 1,
        "scale_down_idle_workers": 2, "pause_scheduler": 2, "resume_scheduler": 2,
        "freeze_policy": 2, "enter_safe_mode": 3, "kill_all_workers": 3,
    }
    level = ACTION_LEVELS.get(action, 99)

    # State allowlist — only STALE_IDLE has action restrictions
    STATE_ALLOWLIST = {
        "STALE_IDLE": frozenset({"unload_embedding_model"}),
    }

    if not collector_ok:
        return {"allowed": False, "reason": "NO_OBSERVATION", "action_level": level}
    if embed_state in ("UNKNOWN", "NOT_LOADED"):
        return {"allowed": False, "reason": "UNKNOWN_STATE", "action_level": level}
    if stale and level >= 2:
        return {"allowed": False, "reason": "STALE_STATE", "action_level": level}
    if embed_state in STATE_ALLOWLIST and action not in STATE_ALLOWLIST[embed_state]:
        return {"allowed": False, "reason": "NOT_ALLOWED_IN_STATE", "action_level": level}
    return {"allowed": True, "reason": "GATE_PASSED", "action_level": level}


# ── Invariant checks ─────────────────────────────────────────────────────────

def _check_invariants(record: dict, ts: str) -> list[str]:
    """L3: structural invariant checks."""
    failures = []
    proof = record.get("proof", {})

    if proof.get("decision_made") is not False:
        failures.append(f"[{ts}] L3 FAIL: proof.decision_made = {proof.get('decision_made')!r}")

    for ad in record.get("action_decisions", []):
        if ad.get("executed") is True:
            failures.append(f"[{ts}] L3 FAIL: action '{ad.get('action')}' has executed=True")

    pi = record.get("policy_input")
    if pi is None:
        failures.append(f"[{ts}] L3 FAIL: missing policy_input")
    elif frozenset(pi.keys()) != REQUIRED_PI_KEYS:
        failures.append(f"[{ts}] L3 FAIL: policy_input key mismatch")

    return failures


def _check_replay(record: dict, ts: str) -> list[str]:
    """L2: replay determinism check."""
    failures = []
    pi = record.get("policy_input")
    if pi is None:
        return failures

    for ad in record.get("action_decisions", []):
        reason = ad.get("reason", "")
        if reason in SERVICE_INTERNAL_REASONS:
            continue  # service-internal, not reproducible by gate alone

        action = ad.get("action", "")
        stored_allowed = ad.get("allowed")
        stored_reason  = ad.get("reason")

        replayed = _gate_replay(action, pi)

        if replayed["allowed"] != stored_allowed or replayed["reason"] != stored_reason:
            failures.append(
                f"[{ts}] L2 FAIL: action='{action}' "
                f"stored=({stored_allowed},{stored_reason!r}) "
                f"replay=({replayed['allowed']},{replayed['reason']!r})"
            )

    return failures


# ── Main ─────────────────────────────────────────────────────────────────────

def run(path: pathlib.Path):
    if not path.exists():
        print(f"Trace file not found: {path}")
        sys.exit(1)

    total = 0
    all_failures: list[str] = []

    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                all_failures.append(f"Line {lineno}: JSON parse error — {e}")
                continue

            ts = record.get("timestamp", f"line {lineno}")
            all_failures.extend(_check_invariants(record, ts))
            all_failures.extend(_check_replay(record, ts))

    print(f"Trace: {path}")
    print(f"Records checked: {total}")

    if not all_failures:
        print("PASS — L2 (trace reproducible) + L3 (invariants verified)")
        print("Compliance must be verifiable without access to the original system.")
        print("VERIFIED — this trace satisfies that requirement.")
        sys.exit(0)
    else:
        print(f"FAIL — {len(all_failures)} violation(s):")
        for f in all_failures:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--finance-sample":
        _sample = pathlib.Path(__file__).parents[1] / "samples" / "finance_trace.jsonl"
        if not _sample.exists():
            print(f"Finance sample not found: {_sample}")
            sys.exit(1)
        print("Finance sample trace replay")
        run(_sample)
    elif len(sys.argv) < 2:
        print("Usage: python scripts/replay_demo.py <decisions.jsonl>")
        print("       python scripts/replay_demo.py --finance-sample")
        sys.exit(1)
    else:
        run(pathlib.Path(sys.argv[1]))
