"""
scripts/auto_push_daemon.py — J-NIS auto push daemon

Watches for a push trigger file (.execution_request) and pushes
only when validate_enforcement.py confirms JNIS_ENFORCEMENT_OK.

Trigger file: .execution_request
  - Created by Claude (or manually) to request a push
  - Deleted by this daemon after processing

Flow:
  trigger detected
      → validate_enforcement.py
      → if JNIS_ENFORCEMENT_OK: git push origin main
      → if FAIL: refuse push, log reason
      → clear trigger

Usage:
  python scripts/auto_push_daemon.py          # run once (check trigger now)
  python scripts/auto_push_daemon.py --watch  # watch mode (poll every 10s)
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRIGGER_FILE = ROOT / ".execution_request"
VALIDATE_SCRIPT = ROOT / "scripts" / "validate_enforcement.py"
LOG_FILE = ROOT / "logs" / "push_daemon.log"


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def run_validate() -> bool:
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    log(f"validate: {output}")
    return "JNIS_ENFORCEMENT_OK" in output


def run_push() -> bool:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "push", "origin", "main"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        log(f"push: SUCCESS — {result.stdout.strip() or 'pushed'}")
        return True
    else:
        log(f"push: FAILED — {result.stderr.strip()}")
        return False


def process_trigger() -> None:
    if not TRIGGER_FILE.exists():
        return

    reason = TRIGGER_FILE.read_text().strip() or "push_requested"
    log(f"trigger detected: {reason}")

    if run_validate():
        success = run_push()
        if success:
            log("push complete — trigger cleared")
        else:
            log("push failed — trigger cleared anyway")
    else:
        log("BLOCKED: validate_enforcement failed — push refused")

    TRIGGER_FILE.unlink()


def main() -> None:
    watch_mode = "--watch" in sys.argv

    if watch_mode:
        log("daemon started (watch mode, interval=10s)")
        while True:
            process_trigger()
            time.sleep(10)
    else:
        process_trigger()


if __name__ == "__main__":
    main()
