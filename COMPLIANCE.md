# COMPLIANCE — J-NIS Compliance Levels

> Compliance is verified by invariant satisfaction, not system behavior.
> Each level is independently verifiable from trace logs alone.

---

## Compliance Levels

### Level 0 — Non-Interference Assertion

**Requirement:** `proof.decision_made` is `false` in every trace record.

This is the minimum assertion. It states that the system did not make a decision in this cycle.

```json
{ "proof": { "decision_made": false } }
```

**Verified by:** presence and value of `proof.decision_made`

---

### Level 1 — Gate Evaluation Recorded

**Requirement:** `action_decisions` is present and non-empty, with `action`, `allowed`, `reason`, `action_level`, and `executed` fields per entry.

This confirms that the gate was evaluated and its result was recorded before any execution occurred.

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

**Requirement:** Given stored `policy_input` and `action_decisions`, re-running the gate function produces the same result.

This confirms that the gate is deterministic and the trace is not retroactively constructed.

**Verified by:** replay — `gate(action, policy_input)` matches stored `allowed` and `reason`

---

### Level 3 — Invariant Verifiable

**Requirement:** All of the following invariants hold across the entire trace:

| Invariant | Rule |
|---|---|
| Non-interference | `proof.decision_made` is always `false` |
| Execution isolation | No `action_decisions` entry has `executed: true` |
| Schema stability | `policy_input` has exactly 5 required keys |
| Version traceability | `jnis_version` is present in every record |

**Verified by:** `python validate_non_interference.py <trace.jsonl>`

---

## Summary

| Level | What it verifies | Tool |
|---|---|---|
| L0 | `decision_made: false` present | manual inspection |
| L1 | `action_decisions` recorded | manual inspection |
| L2 | gate is deterministic, trace reproducible | `replay_demo.py` |
| L3 | all invariants hold across full trace | `validate_non_interference.py` |

A system satisfying L3 satisfies all lower levels.

---

## Key Statement

> **Compliance must be verifiable without access to the original system.**
>
> The trace log alone is sufficient to verify J-NIS compliance at all four levels.

Compliance must be externally verifiable and independently measurable.

---

## Three Verification Paths

| Tool | Verifies | Level |
|---|---|---|
| `validate_non_interference.py` | Internal invariant check | L3 |
| `scripts/replay_demo.py` | Trace reconstruction | L2 + L3 |
| `scripts/evaluate_system.py` | External system assessment | L0 – L3 |
