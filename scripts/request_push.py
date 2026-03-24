"""
scripts/request_push.py — push trigger creator

Claude runs this instead of git push.
Creates .execution_request trigger file.
auto_push_daemon.py detects and processes it.

Usage:
    python scripts/request_push.py
    python scripts/request_push.py --reason "post-demo push"
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRIGGER_FILE = ROOT / ".execution_request"


def main() -> None:
    reason = "push_requested"
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--reason" and i + 1 < len(sys.argv) - 1:
            reason = sys.argv[i + 2]

    TRIGGER_FILE.write_text(f"{reason}\n{time.strftime('%Y-%m-%dT%H:%M:%S')}")
    print(f"TRIGGER_CREATED: .execution_request")
    print(f"Reason: {reason}")
    print(f"Run: python scripts/auto_push_daemon.py")
    print(f"(or daemon will pick it up if running in --watch mode)")


if __name__ == "__main__":
    main()
