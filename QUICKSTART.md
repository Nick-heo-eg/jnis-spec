# QUICKSTART — J-NIS in 10 Lines

> Requires no external dependencies.
> J-NIS can be implemented in under 10 lines — no framework, no package, no state object.
> Copy, run, validate.

The minimum viable J-NIS implementation. For an instant single-file demo, see [ZERO_SETUP.md](ZERO_SETUP.md).

---

## Step 1 — Define policy_input

```python
policy_input = {
    "embed_state":  "ACTIVE",   # ACTIVE | IDLE | STALE_IDLE | HEAVY | UNKNOWN | NOT_LOADED
    "embed_rss":    512,        # int MB, or None
    "embed_idle":   30,         # int seconds, or None
    "stale":        False,      # observation older than threshold?
    "collector_ok": True,       # did collection succeed?
}
```

Exactly 5 keys. This is the only input the gate reads.

---

## Step 2 — Call the gate

```python
ACTION_LEVELS = {
    "refresh_state": 1, "restart_embedding_service": 1, "unload_embedding_model": 1,
    "scale_down_idle_workers": 2, "pause_scheduler": 2, "resume_scheduler": 2,
    "freeze_policy": 2, "enter_safe_mode": 3, "kill_all_workers": 3,
}

def gate(action, policy_input):
    level = ACTION_LEVELS.get(action, 99)
    if not policy_input["collector_ok"]:
        return {"allowed": False, "reason": "NO_OBSERVATION", "action_level": level}
    if policy_input["embed_state"] in ("UNKNOWN", "NOT_LOADED"):
        return {"allowed": False, "reason": "UNKNOWN_STATE", "action_level": level}
    if policy_input["stale"] and level >= 2:
        return {"allowed": False, "reason": "STALE_STATE", "action_level": level}
    return {"allowed": True, "reason": "GATE_PASSED", "action_level": level}

result = gate("restart_embedding_service", policy_input)
# {"allowed": True, "reason": "GATE_PASSED", "action_level": 1}
```

The gate returns permissibility. No I/O. No side effects. Calling it changes nothing.

---

## Step 3 — Log action_decisions

```python
import json
from datetime import datetime, timezone

record = {
    "jnis_version":     "1.1.0",
    "timestamp":        datetime.now(timezone.utc).isoformat(),
    "policy_input":     policy_input,
    "action_decisions": [{"action": "restart_embedding_service", **result, "executed": False}],
    "proof":            {"actor": "my_system", "authority": "evidence_only", "decision_made": False},
}

with open("decisions.jsonl", "a") as f:
    f.write(json.dumps(record) + "\n")

# execution is your decision — the gate only evaluates
if result["allowed"] and your_condition:
    do_restart()
```

Write the record **before** you execute. The trace records the gate result, not the execution.

---

## Verify

```bash
python validate_non_interference.py decisions.jsonl
# JNIS_COMPLIANT — all records satisfy J-NIS guarantees
# JNIS_STANDARD_V1_1_OK
```

---

## What you have

You now have:
- a gate that records it did not execute
- a trace that records the evaluation boundary
- a validator that checks structural invariants

For a more complete integration, see [DROP_INTEGRATION.md](DROP_INTEGRATION.md).

If you need the complete reference implementation, see the [Contact section in README](README.md#contact).
