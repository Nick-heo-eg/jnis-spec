"""
validate_non_interference.py — J-NIS trace validator

Verifies that every record in a .jsonl trace file satisfies
the structural guarantees of Judgment Non-Interference:

  1. proof.decision_made == False
  2. No action_decisions entry has executed == True
  3. policy_input has exactly the required 5 keys
  4. jnis_version field is present (warn only for pre-v1.1.0 records)

Usage:
    python validate_non_interference.py decisions.jsonl

Exit 0 = OK, Exit 1 = FAIL
"""
from __future__ import annotations

import json
import pathlib
import sys

REQUIRED_PI_KEYS = frozenset({"embed_state", "embed_rss", "embed_idle", "stale", "collector_ok"})


def validate(path: pathlib.Path):
    if not path.exists():
        return False, [f"Trace file not found: {path}"], [], 0

    failures: list[str] = []
    warnings: list[str] = []
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
                failures.append(f"Line {lineno}: JSON parse error — {e}")
                continue

            ts = record.get("timestamp", f"line {lineno}")

            # ── Check 1: proof.decision_made == False ────────────────────────
            proof = record.get("proof")
            if proof is None:
                failures.append(f"[{ts}] FAIL: missing 'proof' field")
            elif proof.get("decision_made") is not False:
                failures.append(
                    f"[{ts}] FAIL: proof.decision_made = {proof.get('decision_made')!r} (expected false)"
                )

            # ── Check 2: no action_decisions entry has executed == True ──────
            for ad in record.get("action_decisions", []):
                if ad.get("executed") is True:
                    failures.append(
                        f"[{ts}] FAIL: action '{ad.get('action')}' has executed=True"
                    )

            # ── Check 3: policy_input has exactly the required 5 keys ────────
            pi = record.get("policy_input")
            if pi is None:
                failures.append(f"[{ts}] FAIL: missing 'policy_input' field")
            else:
                actual_keys = frozenset(pi.keys())
                if actual_keys != REQUIRED_PI_KEYS:
                    missing = REQUIRED_PI_KEYS - actual_keys
                    extra   = actual_keys - REQUIRED_PI_KEYS
                    msg = f"[{ts}] FAIL: policy_input key mismatch"
                    if missing:
                        msg += f" — missing: {sorted(missing)}"
                    if extra:
                        msg += f" — extra: {sorted(extra)}"
                    failures.append(msg)

            # ── Check 4: jnis_version present (warn only for pre-v1.1.0 records)
            if "jnis_version" not in record:
                warnings.append(f"[{ts}] WARN: missing 'jnis_version' (pre-v1.1.0 record)")

    return (len(failures) == 0), failures, warnings, total


_MOCK_RECORD = {
    "jnis_version": "v1.0.1",
    "timestamp": "2026-01-01T00:00:00+00:00",
    "policy_input": {
        "embed_state": "ACTIVE", "embed_rss": 512, "embed_idle": 30,
        "stale": False, "collector_ok": True,
    },
    "action_decisions": [{"action": "restart_service", "allowed": True,
                           "reason": "GATE_PASSED", "executed": False}],
    "proof": {"actor": "quick_test", "authority": "evidence_only", "decision_made": False},
}


def _quick_test():
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(_MOCK_RECORD) + "\n")
        tmp = f.name
    ok, failures, warnings, total = validate(pathlib.Path(tmp))
    os.unlink(tmp)
    print("Quick test (mock policy_input)")
    print(f"Records checked: {total}")
    if ok:
        print("JNIS_COMPLIANT — all records satisfy J-NIS guarantees")
        print("For full reference implementation, see README Contact section:")
        print("  https://github.com/Nick-heo-eg/jnis-spec#contact")
        sys.exit(0)
    else:
        print(f"JNIS_VIOLATION — {len(failures)} violation(s):")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--quick-test":
        _quick_test()
        return

    if len(sys.argv) < 2:
        print("Usage: python validate_non_interference.py <decisions.jsonl>")
        print("       python validate_non_interference.py --quick-test")
        sys.exit(1)

    path = pathlib.Path(sys.argv[1])
    ok, failures, warnings, total = validate(path)

    print(f"Trace: {path}")
    print(f"Records checked: {total}")

    for w in warnings:
        print(f"  {w}")

    if ok:
        print("JNIS_COMPLIANT — all records satisfy J-NIS guarantees")
        print("For full reference implementation, see README Contact section:")
        print("  https://github.com/Nick-heo-eg/jnis-spec#contact")
        sys.exit(0)
    else:
        print(f"JNIS_VIOLATION — {len(failures)} violation(s):")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
