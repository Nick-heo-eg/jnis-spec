# SPEC_NON_INTERFERENCE — J-NIS Specification

```
JNIS_VERSION = "1.1.0"
Status       = "Draft Standard"
```

> Every trace record carries `"jnis_version": "1.1.0"`.
> This identifier links the log evidence to the exact spec version that governed it.
>
> **J-NIS defines a trace structure for systems where execution authority is excluded from the AI system.**

---

## Definition

A J-NIS-compliant system is one where:

> The system records whether an action *would be* permissible.
> The system does not determine whether an action *will* happen.

The distinction is structural: evaluation and execution are recorded as separate fields. Whether they are separate in execution is the operator's responsibility and is not verifiable from the trace alone.

---

## The Five Principles

### 1. Observation is separate from decision

The system collects evidence about the world (`policy_input`). This evidence is frozen before the gate runs. The gate cannot modify it. No inference, no weighting, no model output — only directly observable state.

### 2. Actions are evaluated, not executed

The gate function receives an action name and a `policy_input`. It returns `{allowed, reason, action_level}`. The return value is a statement about permissibility, not an instruction.

**Note:** Purity of the gate function (no I/O, no side effects) is a specification requirement. It cannot be verified from trace output alone — it requires source code review or replay testing.

### 3. `decision_made` must always be `false`

Every observation cycle produces a `proof` block. The field `decision_made` is `false` in compliant records. It records that the system did not exercise decision authority in this cycle.

```json
{
  "proof": {
    "actor": "<system_id>",
    "authority": "evidence_only",
    "decision_made": false
  }
}
```

### 4. `allowed` and `executed` must be separate fields

Gate results and execution outcomes must be recorded as separate fields. A system that sets `executed = allowed` is not J-NIS compliant.

```json
{
  "action":       "restart_embedding_service",
  "allowed":      true,
  "reason":       "GATE_PASSED",
  "action_level": 1,
  "executed":     false
}
```

`allowed: true` records that preconditions were met. `executed: false` records that the trace was written before execution. These are independent fields.

### 5. All outputs must be traceable

Every cycle must write a trace record. The trace is the record that the gate was evaluated and its result was captured. An implementation that writes the trace after execution does not satisfy this principle.

---

## Required Fields

Every J-NIS trace record must contain:

| Field | Type | Constraint |
|---|---|---|
| `jnis_version` | string | `"1.1.0"` |
| `policy_input` | object | Exactly 5 keys (see TRACE_SPEC) |
| `action_decisions` | array | Each entry has `action`, `allowed`, `reason`, `action_level`, `executed` |
| `proof` | object | Must contain `decision_made: false` |

---

## Requirements

The following constraints MUST be satisfied for J-NIS compliance:

- `decision_made` **MUST** be `false` in every trace record
- `action_decisions` **MUST** be recorded; each entry **MUST** have `executed: false`
- Trace **MUST** be written before execution occurs
- Trace **MUST** be reproducible: re-running the gate on stored `policy_input` yields the same `allowed` and `reason`
- `reason` **MUST** be from the declared `VALID_REASONS` set

Violation of any requirement constitutes non-compliance.

**Scope:** These requirements apply to the trace record. Whether the system actually withheld execution cannot be determined from the trace alone. J-NIS verifies the recorded claims, not the underlying system behavior.

---

## The Gate Contract

The gate function should satisfy:

1. **Pure** — no external I/O, no state mutation, no time-dependent functions
2. **Deterministic** — same `(action, policy_input)` always returns same result
3. **Bounded** — output `reason` must be from `VALID_REASONS`
4. **Non-executing** — calling the gate changes no external state

Gate purity is verified by replay testing (`scripts/replay_demo.py`), not by trace inspection. A gate that is non-deterministic will fail L2 verification. A gate that calls external services before returning cannot be detected from trace output alone.

---

## Compliance Levels

| Level | What is verified | How |
|---|---|---|
| **L0** | `decision_made: false` present | trace inspection |
| **L1** | `action_decisions` recorded, `executed: false` | trace inspection |
| **L2** | Gate is deterministic; replay matches stored results | `replay_demo.py` |
| **L3** | All invariants hold across full trace | `validate_non_interference.py` |

---

## Non-Goals

J-NIS does not define:

- How to collect system state
- What actions are valid in a given system
- When to execute allowed actions (that is the operator's responsibility)
- How to store or query the trace log
- Whether execution actually occurred — that is outside the trace boundary
