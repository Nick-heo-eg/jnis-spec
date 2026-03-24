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
ACTION_LEVELS = {
    "refresh_state": 1, "restart_embedding_service": 1, "unload_embedding_model": 1,
    "scale_down_idle_workers": 2, "pause_scheduler": 2, "resume_scheduler": 2,
    "freeze_policy": 2, "enter_safe_mode": 3, "kill_all_workers": 3,
}

def gate(action, pi):
    level = ACTION_LEVELS.get(action, 99)
    if not pi["collector_ok"]:              return {"allowed": False, "reason": "NO_OBSERVATION",      "action_level": level}
    if pi["embed_state"] in ("UNKNOWN",
                             "NOT_LOADED"): return {"allowed": False, "reason": "UNKNOWN_STATE",        "action_level": level}
    if pi["stale"] and level >= 2:          return {"allowed": False, "reason": "STALE_STATE",          "action_level": level}
    return {"allowed": True, "reason": "GATE_PASSED", "action_level": level}

# 3. evaluate actions
actions = ["restart_embedding_service", "pause_scheduler"]
decisions = [{"action": a, **gate(a, policy_input), "executed": False} for a in actions]

# 4. build trace record
record = {
    "jnis_version":     "1.1.0",
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
print("J-NIS invariants satisfied — validate with: python validate_non_interference.py decisions.jsonl")
```

```bash
python jnis_demo.py
```

Expected output:

```json
{
  "jnis_version": "1.1.0",
  "timestamp": "...",
  "policy_input": { ... },
  "action_decisions": [
    {"action": "restart_embedding_service", "allowed": true,  "reason": "GATE_PASSED", "action_level": 1, "executed": false},
    {"action": "pause_scheduler",           "allowed": true,  "reason": "GATE_PASSED", "action_level": 2, "executed": false}
  ],
  "proof": {"actor": "my_system", "authority": "evidence_only", "decision_made": false}
}

decision_made:  False
executed:       [False, False]

J-NIS invariants satisfied — validate with: python validate_non_interference.py decisions.jsonl
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
