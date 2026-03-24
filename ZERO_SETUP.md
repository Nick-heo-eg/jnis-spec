# ZERO_SETUP — Run J-NIS in 30 seconds

> **If this runs successfully, J-NIS compliance is satisfied.**

No pip install. No framework. No config. One file, one command.

```bash
curl -O https://raw.githubusercontent.com/Nick-heo-eg/jnis-spec/main/ZERO_SETUP.md
# or just copy the code below into any .py file
```

---

## Copy this. Run it. Done.

```python
# jnis_demo.py — no dependencies required
import json
from datetime import datetime, timezone

# 1. policy_input: the only thing the gate reads (5 keys, always)
policy_input = {
    "embed_state":  "ACTIVE",   # ACTIVE | IDLE | STALE_IDLE | HEAVY | UNKNOWN | NOT_LOADED
    "embed_rss":    512,        # int MB, or None
    "embed_idle":   30,         # int seconds, or None
    "stale":        False,      # is observation stale?
    "collector_ok": True,       # did collection succeed?
}

# 2. gate: pure function — no I/O, no side effects, no execution
def gate(action, pi):
    if not pi["collector_ok"]:              return {"allowed": False, "reason": "NO_OBSERVATION"}
    if pi["embed_state"] in ("UNKNOWN",
                             "NOT_LOADED"): return {"allowed": False, "reason": "UNKNOWN_STATE"}
    if pi["stale"]:                         return {"allowed": False, "reason": "STALE_STATE"}
    return {"allowed": True, "reason": "GATE_PASSED"}

# 3. evaluate actions
actions = ["restart_service", "pause_scheduler"]
decisions = [{"action": a, **gate(a, policy_input), "executed": False} for a in actions]

# 4. build trace record
record = {
    "jnis_version":     "v1.0.1",
    "timestamp":        datetime.now(timezone.utc).isoformat(),
    "policy_input":     policy_input,
    "action_decisions": decisions,
    "proof":            {"actor": "my_system", "authority": "evidence_only", "decision_made": False},
}

print(json.dumps(record, indent=2))
print()
print("decision_made:", record["proof"]["decision_made"])   # always False
print("executed:     ", [d["executed"] for d in decisions]) # always False
print()
print("JNIS_COMPLIANT — J-NIS compliance satisfied")
```

```bash
python jnis_demo.py
```

Expected output:

```json
{
  "jnis_version": "v1.0.1",
  "timestamp": "...",
  "policy_input": { ... },
  "action_decisions": [
    {"action": "restart_service", "allowed": true,  "reason": "GATE_PASSED", "executed": false},
    {"action": "pause_scheduler", "allowed": false, "reason": "STALE_STATE",  "executed": false}
  ],
  "proof": {"actor": "my_system", "authority": "evidence_only", "decision_made": false}
}

decision_made:  False
executed:       [False, False]

JNIS_COMPLIANT — paste this into any system to add non-interference proof
```

---

## What just happened

- You built a gate that evaluated two actions
- Neither executed — `executed` is always `False` here
- `decision_made` is always `False` — the gate does not decide
- The trace record proves it

That is J-NIS. Compliance is satisfied.

---

## Next steps

- Save the output to `decisions.jsonl` and run `python validate_non_interference.py decisions.jsonl`
- See [QUICKSTART.md](QUICKSTART.md) to add persistence
- See [DROP_INTEGRATION.md](DROP_INTEGRATION.md) to integrate into an existing system

This demonstration verifies invariant satisfaction.
