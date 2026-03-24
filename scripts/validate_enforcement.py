"""
scripts/validate_enforcement.py — J-NIS enforcement validator

Reads logs/trace.jsonl and checks that no AI-path record
has executed=True in any action_decisions entry.

Exit 0 = JNIS_ENFORCEMENT_OK
Exit 1 = FAIL
"""
from __future__ import annotations

import json
import pathlib
import sys

TRACE_PATH = pathlib.Path(__file__).parent.parent / "logs" / "trace.jsonl"


def main() -> None:
    if not TRACE_PATH.exists():
        print("FAIL: trace file not found", file=sys.stderr)
        sys.exit(1)

    failures = []
    total = 0

    with open(TRACE_PATH, encoding="utf-8") as f:
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
            for ad in record.get("action_decisions", []):
                if ad.get("executed") is True:
                    failures.append(
                        f"[{ts}] FAIL: action '{ad.get('action')}' has executed=True in AI-path trace"
                    )

    print(f"Records checked: {total}")

    if not failures:
        print("JNIS_ENFORCEMENT_OK — no executed=True found in AI-path trace")
        sys.exit(0)
    else:
        print(f"FAIL — {len(failures)} violation(s):")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
