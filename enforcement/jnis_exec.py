"""
enforcement/jnis_exec.py — J-NIS external executor

The only path through which git commit may be performed.
All execution is gated by jnis_gate.allow_execution().

Usage:
    python enforcement/jnis_exec.py --action commit --commit-message "your message"

Exit codes:
    0 — execution allowed and completed
    1 — blocked by J-NIS gate
    2 — usage error
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from enforcement.jnis_gate import allow_execution, load_latest_trace

ALLOWED_ACTIONS = {"commit"}


def main() -> None:
    parser = argparse.ArgumentParser(description="J-NIS external executor")
    parser.add_argument("--action", required=True, choices=ALLOWED_ACTIONS,
                        help="Action to execute")
    parser.add_argument("--commit-message", required=False,
                        help="Commit message (required for --action commit)")
    args = parser.parse_args()

    if args.action == "commit" and not args.commit_message:
        print("ERROR: --commit-message is required for --action commit", file=sys.stderr)
        sys.exit(2)

    # Gate check
    trace = load_latest_trace()
    allowed, reason = allow_execution(trace)

    if not allowed:
        print(f"BLOCKED_BY_JNIS: {reason}")
        sys.exit(1)

    # Execute
    if args.action == "commit":
        cmd = ["git", "commit", "-m", args.commit_message]
        print(f"JNIS_EXEC: gate passed ({reason}) — running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"JNIS_EXEC: git exited with code {result.returncode} (not a gate block)")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
