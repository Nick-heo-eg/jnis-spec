"""
scripts/evaluate_system.py — J-NIS External System Evaluator

Evaluates any system's trace file against J-NIS compliance levels.
No access to the evaluated system is required.

Input:  trace.jsonl (one JSON record per line)
Output: {"compliant": bool, "level": str, "violations": [], "summary": str}

Usage:
    python scripts/evaluate_system.py path/to/trace.jsonl
    python scripts/evaluate_system.py path/to/trace.jsonl --json   # JSON output only

Exit 0 = compliant, Exit 1 = non-compliant or error
"""
from __future__ import annotations

import json
import pathlib
import sys

REQUIRED_PI_KEYS = frozenset({"embed_state", "embed_rss", "embed_idle", "stale", "collector_ok"})
VALID_REASONS = frozenset({
    "NO_OBSERVATION", "UNKNOWN_STATE", "STALE_STATE", "NOT_ALLOWED_IN_STATE", "GATE_PASSED",
})
SERVICE_INTERNAL_REASONS = {"AUTO_LEVEL_RESTRICTED"}


# ── Gate replay (inline, no external dependency) ─────────────────────────────

def _gate_replay(action: str, policy_input: dict) -> dict:
    ACTION_LEVELS = {
        "refresh_state": 1, "restart_embedding_service": 1, "unload_embedding_model": 1,
        "scale_down_idle_workers": 2, "pause_scheduler": 2, "resume_scheduler": 2,
        "freeze_policy": 2, "enter_safe_mode": 3, "kill_all_workers": 3,
    }
    STATE_ALLOWLIST = {"STALE_IDLE": frozenset({"unload_embedding_model"})}
    level       = ACTION_LEVELS.get(action, 99)
    collector   = policy_input.get("collector_ok", False)
    embed_state = policy_input.get("embed_state", "UNKNOWN")
    stale       = policy_input.get("stale", True)

    if not collector:
        return {"allowed": False, "reason": "NO_OBSERVATION"}
    if embed_state in ("UNKNOWN", "NOT_LOADED"):
        return {"allowed": False, "reason": "UNKNOWN_STATE"}
    if stale and level >= 2:
        return {"allowed": False, "reason": "STALE_STATE"}
    if embed_state in STATE_ALLOWLIST and action not in STATE_ALLOWLIST[embed_state]:
        return {"allowed": False, "reason": "NOT_ALLOWED_IN_STATE"}
    return {"allowed": True, "reason": "GATE_PASSED"}


# ── Per-record evaluation ─────────────────────────────────────────────────────

def _evaluate_record(record: dict, ts: str) -> list[str]:
    violations = []

    # L0: decision_made must be false
    proof = record.get("proof")
    if proof is None:
        violations.append(f"[{ts}] L0 VIOLATION: missing 'proof' field")
    elif proof.get("decision_made") is not False:
        violations.append(
            f"[{ts}] L0 VIOLATION: proof.decision_made = {proof.get('decision_made')!r}"
        )

    # L1: action_decisions must be present and no executed=True
    ads = record.get("action_decisions")
    if ads is None:
        violations.append(f"[{ts}] L1 VIOLATION: missing 'action_decisions' field")
    else:
        for ad in ads:
            if not all(k in ad for k in ("action", "allowed", "reason", "executed")):
                violations.append(
                    f"[{ts}] L1 VIOLATION: action_decisions entry missing required fields: {ad}"
                )
            if ad.get("executed") is True:
                violations.append(
                    f"[{ts}] L1 VIOLATION: action '{ad.get('action')}' has executed=True"
                )
            reason = ad.get("reason", "")
            if reason and reason not in VALID_REASONS and reason not in SERVICE_INTERNAL_REASONS:
                violations.append(
                    f"[{ts}] L1 VIOLATION: action '{ad.get('action')}' has unrecognized reason: {reason!r}"
                )

    # L2: replay determinism
    pi = record.get("policy_input")
    if pi and ads:
        for ad in ads:
            reason = ad.get("reason", "")
            if reason in SERVICE_INTERNAL_REASONS:
                continue
            action = ad.get("action", "")
            replayed = _gate_replay(action, pi)
            if replayed["allowed"] != ad.get("allowed") or replayed["reason"] != reason:
                violations.append(
                    f"[{ts}] L2 VIOLATION: action='{action}' "
                    f"stored=({ad.get('allowed')},{reason!r}) "
                    f"replay=({replayed['allowed']},{replayed['reason']!r})"
                )

    # L3: structural invariants
    if pi is None:
        violations.append(f"[{ts}] L3 VIOLATION: missing 'policy_input' field")
    elif frozenset(pi.keys()) != REQUIRED_PI_KEYS:
        missing = sorted(REQUIRED_PI_KEYS - frozenset(pi.keys()))
        extra   = sorted(frozenset(pi.keys()) - REQUIRED_PI_KEYS)
        msg = f"[{ts}] L3 VIOLATION: policy_input key mismatch"
        if missing: msg += f" — missing: {missing}"
        if extra:   msg += f" — extra: {extra}"
        violations.append(msg)

    if "jnis_version" not in record:
        violations.append(f"[{ts}] L3 VIOLATION: missing 'jnis_version' field")

    return violations


# ── Compliance level assignment ───────────────────────────────────────────────

def _assign_level(violations: list[str]) -> str:
    if not violations:
        return "L3"
    has = {
        "L0": any("L0 VIOLATION" in v for v in violations),
        "L1": any("L1 VIOLATION" in v for v in violations),
        "L2": any("L2 VIOLATION" in v for v in violations),
        "L3": any("L3 VIOLATION" in v for v in violations),
    }
    if has["L0"] or has["L1"]:
        return "NON_COMPLIANT"
    if has["L2"]:
        return "L1"
    if has["L3"]:
        return "L2"
    return "NON_COMPLIANT"


# ── Main ─────────────────────────────────────────────────────────────────────

def evaluate(path: pathlib.Path) -> dict:
    if not path.exists():
        return {
            "compliant": False, "level": "NON_COMPLIANT", "records_checked": 0,
            "violations": [f"Trace file not found: {path}"],
            "summary": f"Trace file not found: {path}",
        }

    all_violations: list[str] = []
    total = 0

    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                all_violations.append(f"Line {lineno}: JSON parse error — {e}")
                continue
            ts = record.get("timestamp", f"line {lineno}")
            all_violations.extend(_evaluate_record(record, ts))

    level     = _assign_level(all_violations)
    compliant = level not in ("NON_COMPLIANT",) and not all_violations

    if compliant:
        summary = f"All {total} records satisfy J-NIS invariants. Compliance level: {level}."
    else:
        summary = f"{len(all_violations)} violation(s) found across {total} records. System does not satisfy J-NIS compliance."

    return {
        "compliant":       compliant,
        "level":           level,
        "records_checked": total,
        "violations":      all_violations,
        "summary":         summary,
    }


def main():
    json_only = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not args:
        print("Usage: python scripts/evaluate_system.py <trace.jsonl> [--json]")
        sys.exit(1)

    result = evaluate(pathlib.Path(args[0]))

    if json_only:
        print(json.dumps(result, indent=2))
    else:
        print(f"Trace: {args[0]}")
        print(f"Records checked: {result['records_checked']}")
        print(f"Compliant: {result['compliant']}")
        print(f"Compliance Level: {result['level']}")
        if result["violations"]:
            print(f"Violations ({len(result['violations'])}):")
            for v in result["violations"]:
                print(f"  {v}")
        print(f"Summary: {result['summary']}")
        if result["compliant"]:
            print("J-NIS defines a measurable boundary, not a conceptual one.")
            print("Any system can be evaluated using J-NIS without internal access.")

    sys.exit(0 if result["compliant"] else 1)


if __name__ == "__main__":
    main()
