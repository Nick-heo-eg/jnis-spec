# SPEC_NON_INTERFERENCE — J-NIS Specification

```
JNIS_VERSION = "1.1.0"
Status       = "Draft Standard"
```

> Every trace record carries `"jnis_version": "1.1.0"`.
> This identifier links the log evidence to the exact spec version that governed it.
>
> **J-NIS does not introduce new capabilities. It restricts existing ones.**

---

## Definition

A J-NIS-compliant system is one where:

> The system evaluates whether an action *would be* permissible.
> The system does not determine whether an action *will* happen.

The distinction is structural, not behavioral. It must be enforced in code, not by convention.

**This restriction is enforceable without modifying system capabilities.**
Adding a gate function and a trace record is sufficient for compliance.

---

## The Five Principles

### 1. Observation is separate from decision

The system collects evidence about the world (`policy_input`). This evidence is frozen before the gate runs. The gate cannot modify it. No inference, no weighting, no model output — only directly observable state.

### 2. Actions are evaluated, not executed

The gate function receives an action name and a `policy_input`. It returns `{allowed, reason}`. It does not call, schedule, enqueue, or trigger anything. The return value is a statement about permissibility, not an instruction.

### 3. `decision_made` must always be `false`

Every observation cycle produces a `proof` block. The field `decision_made` is structurally `false` in compliant mode. It is not a flag that can be set to `true` through evaluation logic.

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

Gate results and execution outcomes must never collapse into a single field. A system that sets `executed = allowed` is not J-NIS compliant.

```json
{
  "action":   "restart_service",
  "allowed":  true,
  "reason":   "GATE_PASSED",
  "executed": false
}
```

`allowed: true` means preconditions were met. `executed: false` means nothing happened. These are independent facts.

### 5. All outputs must be traceable

Every cycle must write a trace record before any execution occurs. The trace is the evidence that non-interference was maintained. An implementation that acts before writing the trace is not J-NIS compliant.

---

## Required Fields

Every J-NIS trace record must contain:

| Field | Type | Constraint |
|---|---|---|
| `policy_input` | object | Exactly 5 keys (see TRACE_SPEC) |
| `action_decisions` | array | Each entry has `action`, `allowed`, `reason`, `executed` |
| `proof` | object | Must contain `decision_made: false` |

---

## Requirements

The following constraints MUST be satisfied for J-NIS compliance:

- `decision_made` **MUST** be `false` in every trace record
- `action_decisions` **MUST** be recorded before any execution occurs
- Execution **MUST NOT** be performed by the AI system — it is externally controlled
- Trace **MUST** be reproducible: re-running the gate on stored `policy_input` yields the same result

Violation of any requirement constitutes non-compliance.

---

## The Gate Contract

The gate function must satisfy:

1. **Pure** — no external I/O, no state mutation, no time functions
2. **Deterministic** — same `(action, policy_input)` always returns same result
3. **Bounded** — output `reason` must be from a fixed, declared set (`VALID_REASONS`)
4. **Non-executing** — calling the gate function changes nothing in the world

Any function that violates these properties is not a J-NIS gate.

---

## Compliance Levels

| Level | Requirement |
|---|---|
| **Structural** | `allowed` and `executed` are separate fields; `proof.decision_made = false` |
| **Behavioral** | Gate is a pure function; `executed` reflects reality (not gate result) |
| **Auditable** | Trace is append-only; every cycle is recorded before execution |

A reference implementation satisfies all three levels.

---

## Non-Goals

J-NIS does not define:

- How to collect system state
- What actions are valid in a given system
- When to execute allowed actions (that is the operator's responsibility)
- How to store or query the trace log
