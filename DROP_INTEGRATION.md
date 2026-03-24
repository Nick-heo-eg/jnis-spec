# DROP_INTEGRATION — Add J-NIS to Any System in 3 Steps

> This guide assumes you have an existing system that evaluates and potentially executes actions.
> No framework required. No package to install. Copy two files, call two functions.

---

## What you're adding

A structural gate between evaluation and execution — with a per-cycle trace that proves nothing executed without gate evaluation first.

Before J-NIS:
```
state → evaluate → execute
```

After J-NIS:
```
state → policy_input → gate → action_decisions → [your execution logic]
                                      ↓
                               trace written here
                               (before execution)
```

---

## Files to copy

From [echo-control-tower](https://github.com/Nick-heo-eg/echo-control-tower):

```
runtime/control_tower/action_gate.py    # the gate function
runtime/control_tower/export_api.py     # the two public functions
runtime/control_tower/policy_input.py   # state → policy_input
runtime/control_tower/engine/config.py  # ACTION_LEVELS (edit for your actions)
runtime/control_tower/engine/models.py  # state dataclasses
```

---

## Step 1 — Build policy_input from your state

`policy_input` is the only thing the gate reads. It has exactly 5 keys.

**Option A: use `get_policy_input` (if your state matches the schema)**

```python
from runtime.control_tower.export_api import get_policy_input

policy_input = get_policy_input(your_state)
```

**Option B: build it directly (if your state has a different shape)**

```python
policy_input = {
    "embed_state":  "ACTIVE",    # ACTIVE | IDLE | STALE_IDLE | HEAVY | UNKNOWN | NOT_LOADED
    "embed_rss":    512,         # int MB, or None if unknown
    "embed_idle":   30,          # int seconds, or None if unknown
    "stale":        False,       # True if observation is >60s old
    "collector_ok": True,        # True if collection succeeded
}
```

There are exactly 5 keys. Do not add or remove any.

---

## Step 2 — Run the gate

```python
from runtime.control_tower.export_api import get_action_decisions

actions = ["restart_service", "pause_scheduler", "enter_safe_mode"]
decisions = get_action_decisions(policy_input, actions)
```

Result:

```python
[
    {"action": "restart_service",  "allowed": True,  "reason": "GATE_PASSED",    "action_level": 1, "executed": False},
    {"action": "pause_scheduler",  "allowed": False, "reason": "STALE_STATE",    "action_level": 2, "executed": False},
    {"action": "enter_safe_mode",  "allowed": False, "reason": "NO_OBSERVATION", "action_level": 3, "executed": False},
]
```

`executed` is always `False` here. The gate does not execute anything.

---

## Step 3 — Record action_decisions (before you execute)

Write the trace record **before** you decide whether to execute.

```python
import json
from datetime import datetime, timezone

record = {
    "jnis_version":     "v1.0.1",
    "timestamp":        datetime.now(timezone.utc).isoformat(),
    "policy_input":     policy_input,
    "action_decisions": decisions,
    "proof": {
        "actor":         "your_system_id",
        "authority":     "evidence_only",
        "decision_made": False,
    },
}

with open("decisions.jsonl", "a") as f:
    f.write(json.dumps(record) + "\n")

# NOW you may choose to execute — based on your own logic
for d in decisions:
    if d["allowed"] and your_condition:
        your_execute_function(d["action"])
        # if you log execution separately, set executed=True in your own record
```

The trace exists before execution. If execution never happens, the trace still records the gate result.

---

## Configuring your actions

Edit `ACTION_LEVELS` in `engine/config.py`:

```python
ACTION_LEVELS = {
    "restart_service":    1,   # auto-eligible, blocked by NO_OBSERVATION/UNKNOWN only
    "pause_scheduler":    2,   # also blocked when state is stale
    "enter_safe_mode":    3,   # operator note required in ACTIVE mode
}
```

| Level | Blocked by |
|---|---|
| 1 | `NO_OBSERVATION`, `UNKNOWN_STATE`, `NOT_ALLOWED_IN_STATE` |
| 2 | Level 1 reasons + `STALE_STATE` |
| 3 | Level 2 reasons + requires `operator_note` |

---

## Minimum integration (no state object, no file copying)

If you only need gate evaluation:

```python
# Copy just action_gate.py and engine/config.py
from runtime.control_tower.action_gate import allow_action

policy_input = {
    "embed_state": "ACTIVE", "embed_rss": 400, "embed_idle": 10,
    "stale": False, "collector_ok": True,
}

result = allow_action("restart_service", policy_input)
# {"allowed": True, "reason": "GATE_PASSED", "action_level": 1}
```

`allow_action` is a pure function. No external dependencies beyond `engine/config.py`.

---

## Invariants you must maintain

| Rule | Why |
|---|---|
| Write trace before execution | The log is evidence of what the gate said *before* action |
| `proof.decision_made` always `False` | The system evaluated — it did not decide |
| `policy_input` has exactly 5 keys | The gate will not accept partial input |
| `executed` reflects reality | Gate result and execution are structurally separate |

---

## Verify your integration

```bash
python scripts/validate_non_interference.py path/to/your/decisions.jsonl
# OK — all records satisfy J-NIS guarantees
```

Reference validator: [echo-control-tower/scripts/validate_non_interference.py](https://github.com/Nick-heo-eg/echo-control-tower/blob/main/scripts/validate_non_interference.py)
