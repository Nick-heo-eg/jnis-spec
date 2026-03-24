# TRACE_SPEC — J-NIS Trace Format

```
JNIS_VERSION = "1.1.0"
Status       = "Draft Standard"
```

Every J-NIS observation cycle produces one line in an append-only `.jsonl` file.
The trace is the record that the gate was evaluated and its result was captured.

Every record must include `"jnis_version": "1.1.0"` as the first field.

---

## Required Fields

```json
{
  "jnis_version":     "1.1.0",
  "timestamp":        "<ISO 8601 UTC>",
  "policy_input":     { ... },
  "action_decisions": [ ... ],
  "proof":            { ... }
}
```

Additional diagnostic fields are permitted. The five required fields must always be present.

This schema is minimal and sufficient for compliance verification.

---

## `policy_input`

Fixed 5-key evidence snapshot. This is the only input to the gate function.

```json
{
  "embed_state":  "ACTIVE | IDLE | STALE_IDLE | HEAVY | UNKNOWN | NOT_LOADED",
  "embed_rss":    "<int MB or null>",
  "embed_idle":   "<int seconds or null>",
  "stale":        "<bool>",
  "collector_ok": "<bool>"
}
```

**Constraints:**
- Exactly these 5 keys. No additions, no omissions.
- Must be frozen before the gate runs. The gate cannot modify it.
- `embed_rss` and `embed_idle` are `null` when the service is unreachable.

---

## `action_decisions`

Array of gate results, one per evaluated action.

```json
[
  {
    "action":       "<action_name>",
    "allowed":      "<bool>",
    "reason":       "<VALID_REASON>",
    "action_level": "<1 | 2 | 3 | 99>",
    "executed":     false
  }
]
```

**`reason` must be one of:**

| Reason | Meaning |
|---|---|
| `NO_OBSERVATION` | Collector failed — no reliable state |
| `UNKNOWN_STATE` | Service state is indeterminate |
| `STALE_STATE` | Observation is too old for this action level |
| `NOT_ALLOWED_IN_STATE` | Action is not in the allowlist for current state |
| `GATE_PASSED` | All gate rules passed |

**`action_level` values:**

| Value | Meaning |
|---|---|
| `1` | Low restriction — blocked only by NO_OBSERVATION, UNKNOWN_STATE, NOT_ALLOWED_IN_STATE |
| `2` | Medium restriction — also blocked by STALE_STATE |
| `3` | High restriction |
| `99` | Action not in the defined ACTION_LEVELS map |

**Constraints:**
- `executed` is always `false` in J-NIS compliant records. This field records that the gate entry was written before execution, not that execution did not occur.
- `allowed: true` and `executed: false` are independent facts. `allowed: true` does not imply execution occurred.
- `reason` must be from the declared set. Unknown reasons are flagged by the validator.

---

## `proof`

Per-cycle non-interference assertion.

```json
{
  "actor":          "<system_id>",
  "mode":           "SAFE",
  "authority":      "evidence_only",
  "decision_made":  false
}
```

**Field notes:**
- `mode` is optional. Not defined in the core spec; implementations may include it for diagnostic purposes.
- `decision_made` must be `false` in all J-NIS compliant records.
- `authority` must be `"evidence_only"`.
- Any record with `decision_made: true` indicates the system was operating outside J-NIS compliance.

---

## Invariants

| Invariant | Rule |
|---|---|
| Non-interference | `proof.decision_made` is always `false` |
| Field separation | `executed` is always `false` in gate records |
| Schema stability | `policy_input` always has exactly 5 keys |
| Ordering | Trace record is written before execution occurs |
| Append-only | No record is modified or deleted after writing |

### Normative Invariants (MUST)

- `decision_made` **MUST** be `false` — the trace records that decision authority was not exercised
- `allowed` and `executed` **MUST** be separate fields — gate result and execution status are independent
- Trace **MUST** be sufficient for replay verification — given stored `policy_input`, gate output is reproducible

---

## Replay Invariant

Given any trace record, re-running the gate function with:

```
gate(action, record["policy_input"])
```

must produce the same `allowed` and `reason` for every entry in `action_decisions` that does not carry a service-internal reason.

A gate that produces different results on the same input fails L2 verification.

**Note:** Replay verification requires the gate function definition. The trace alone is not sufficient for L2.

---

## Replay Requirement

The trace must be sufficient to reconstruct `policy_input` and `action_decisions` independently.

Specifically:

1. `policy_input` must be stored verbatim in every record
2. `action_decisions` must include `action`, `allowed`, `reason`, `action_level`, and `executed` per entry
3. Re-running the gate function on stored `policy_input` must produce the same `allowed` and `reason`

This requirement enables gate determinism verification without access to the original system's runtime.

```bash
python scripts/replay_demo.py decisions.jsonl
# PASS — L2 (trace reproducible) + L3 (invariants verified)
```

---

## OpenTelemetry Attribute Mapping

J-NIS fields map to the `gen_ai.non_interference.*` OTel namespace:

| J-NIS field | OTel attribute | Type |
|---|---|---|
| `proof.decision_made` | `gen_ai.non_interference.decision_made` | boolean |
| count of `allowed=True` decisions | `gen_ai.non_interference.allowed_actions` | int |
| count of `allowed=False` decisions | `gen_ai.non_interference.blocked_actions` | int |
| `proof.mode` (optional) | `gen_ai.non_interference.mode` | string |
| `jnis_version` | `gen_ai.non_interference.spec_version` | string |
| `policy_input.embed_state` | `gen_ai.non_interference.embed_state` | string |
| `policy_input.collector_ok` | `gen_ai.non_interference.collector_ok` | boolean |

Filter on `gen_ai.non_interference.decision_made = false` to verify J-NIS compliance across all cycles in any OTel-compatible backend.

---

## Validation

A compliant trace file must pass:

```bash
python validate_non_interference.py decisions.jsonl
# JNIS_COMPLIANT — all records satisfy J-NIS guarantees
# JNIS_STANDARD_V1_1_OK
```
