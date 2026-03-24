# COMPLIANCE — J-NIS Compliance Levels

> Compliance is verified by trace invariant satisfaction.
> Each level is independently verifiable from trace logs alone.
>
> **Scope:** J-NIS verifies what the trace records. Whether execution actually occurred is outside
> the trace boundary and must be ensured by system architecture.

---

## Compliance Levels

### Level 0 — Non-Interference Assertion

**Requirement:** `proof.decision_made` is `false` in every trace record.

This is the minimum recorded assertion. It states that the system recorded non-decision for this cycle.

```json
{ "proof": { "decision_made": false } }
```

**Verified by:** presence and value of `proof.decision_made`

---

### Level 1 — Gate Evaluation Recorded

**Requirement:** `action_decisions` is present and non-empty, with `action`, `allowed`, `reason`, `action_level`, and `executed` fields per entry. All `executed` values are `false`.

This confirms that gate results are recorded in the trace with separated fields.

```json
{
  "action_decisions": [
    { "action": "restart_embedding_service", "allowed": true, "reason": "GATE_PASSED", "action_level": 1, "executed": false }
  ]
}
```

**Verified by:** presence and schema of `action_decisions`

---

### Level 2 — Trace Reproducible

**Requirement:** Given stored `policy_input` and `action_decisions`, re-running the gate function produces the same `allowed` and `reason` for every entry.

This confirms that the gate is deterministic and the stored results match what the gate would produce from the same input.

**Verified by:** `scripts/replay_demo.py` — `gate(action, policy_input)` matches stored results

**Note:** Replay requires the gate function definition. The trace alone is not sufficient for L2 verification.

---

### Level 3 — Invariant Verifiable

**Requirement:** All of the following invariants hold across the entire trace:

| Invariant | Rule |
|---|---|
| Non-interference | `proof.decision_made` is always `false` |
| Execution isolation | No `action_decisions` entry has `executed: true` |
| Schema stability | `policy_input` has exactly 5 required keys |
| Version traceability | `jnis_version` is present in every record |
| Reason validity | `reason` is from the declared `VALID_REASONS` set |

**Verified by:** `python validate_non_interference.py <trace.jsonl>`

---

## Summary

| Level | What it verifies | Tool |
|---|---|---|
| L0 | `decision_made: false` recorded | trace inspection |
| L1 | `action_decisions` recorded with separated fields | trace inspection |
| L2 | gate is deterministic; replay matches stored results | `replay_demo.py` |
| L3 | all invariants hold across full trace | `validate_non_interference.py` |

A system satisfying L3 satisfies all lower levels.

---

## Key Statement

> **Compliance must be verifiable without access to the original system's runtime.**
>
> The trace record alone is sufficient for L0 and L1. L2 requires the gate function definition.
> L3 verifies all structural invariants.

---

## Three Verification Paths

| Tool | Verifies | Level |
|---|---|---|
| `validate_non_interference.py` | Structural invariants | L3 |
| `scripts/replay_demo.py` | Gate determinism + invariants | L2 + L3 |
| `scripts/evaluate_system.py` | Any system's trace | L0 – L3 |
