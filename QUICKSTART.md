# QUICKSTART — J-NIS in 10 Lines

> **No dependencies required. Compliant by default.**
> This takes under 30 seconds and requires no dependencies.
> You can implement J-NIS in under 10 lines — no framework, no package, no state object.
> Copy, run, validate.

The minimum viable J-NIS implementation. For instant zero-setup demo, see [ZERO_SETUP.md](ZERO_SETUP.md).

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
def gate(action, policy_input):
    if not policy_input["collector_ok"]:
        return {"allowed": False, "reason": "NO_OBSERVATION"}
    if policy_input["embed_state"] in ("UNKNOWN", "NOT_LOADED"):
        return {"allowed": False, "reason": "UNKNOWN_STATE"}
    if policy_input["stale"]:
        return {"allowed": False, "reason": "STALE_STATE"}
    return {"allowed": True, "reason": "GATE_PASSED"}

result = gate("restart_service", policy_input)
# {"allowed": True, "reason": "GATE_PASSED"}
```

Pure function. No I/O. No side effects. Calling it changes nothing.

---

## Step 3 — Log action_decisions

```python
import json
from datetime import datetime, timezone

record = {
    "jnis_version":     "v1.0.1",
    "timestamp":        datetime.now(timezone.utc).isoformat(),
    "policy_input":     policy_input,
    "action_decisions": [{"action": "restart_service", **result, "executed": False}],
    "proof":            {"actor": "my_system", "authority": "evidence_only", "decision_made": False},
}

with open("decisions.jsonl", "a") as f:
    f.write(json.dumps(record) + "\n")

# execution is your decision — the gate only evaluates
if result["allowed"] and your_condition:
    do_restart()
```

Write the record **before** you execute. The trace is the proof.

---

## Verify

```bash
python validate_non_interference.py decisions.jsonl
# OK — all records satisfy J-NIS guarantees
```

---

## That's it

You now have:
- a gate that proves it didn't execute
- a trace that proves non-interference was evaluated
- a validator that confirms compliance

For a full production-grade implementation, see [DROP_INTEGRATION.md](DROP_INTEGRATION.md).

If you need the complete reference implementation, see the [Contact section in README](README.md#contact).
