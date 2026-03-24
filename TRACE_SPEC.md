# TRACE_SPEC — J-NIS Trace Format

```
JNIS_VERSION = "1.1.0"
Status       = "Draft Standard"
```

Every J-NIS observation cycle produces one line in an append-only `.jsonl` file.
The trace is the verifiable record that non-interference was maintained.

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

Additional diagnostic fields are permitted. The four required fields must always be present.

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
    "action_level": "<1 | 2 | 3>",
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

**Constraints:**
- `executed` is always `false` in SAFE/compliant mode.
- `allowed: true` does not imply execution. These fields are structurally independent.
- `reason` must be from the declared set. Unknown reasons indicate an implementation error.

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

**Constraints:**
- `decision_made` must be `false` in all J-NIS compliant cycles.
- `authority` must be `"evidence_only"`.
- Any record with `decision_made: true` indicates the system was operating outside J-NIS compliance.

---

## Invariants

| Invariant | Rule |
|---|---|
| Non-interference | `proof.decision_made` is always `false` |
| No silent execution | `executed` is always `false` in SAFE mode |
| Schema stability | `policy_input` always has exactly 5 keys |
| Ordering | Trace record is written before any execution |
| Append-only | No record is modified or deleted after writing |

---

## Replay Invariant

Given any trace record, re-running the gate function with:

```
gate(action, record["policy_input"])
```

must produce the same `allowed` and `reason` for every entry in `action_decisions` that does not carry a service-internal reason.

This is the **determinism guarantee** of J-NIS. A gate that produces different results on replay is not compliant.

---

## OpenTelemetry Attribute Mapping

J-NIS fields map to the `gen_ai.non_interference.*` OTel namespace:

| J-NIS field | OTel attribute | Type |
|---|---|---|
| `proof.decision_made` | `gen_ai.non_interference.decision_made` | boolean |
| count of `allowed=True` decisions | `gen_ai.non_interference.allowed_actions` | int |
| count of `allowed=False` decisions | `gen_ai.non_interference.blocked_actions` | int |
| `proof.mode` | `gen_ai.non_interference.mode` | string |
| `jnis_version` | `gen_ai.non_interference.spec_version` | string |
| `policy_input.embed_state` | `gen_ai.non_interference.embed_state` | string |
| `policy_input.collector_ok` | `gen_ai.non_interference.collector_ok` | boolean |

Filter on `gen_ai.non_interference.decision_made = false` to verify J-NIS compliance across all cycles in any OTel-compatible backend.

---

## Validation

A compliant trace file must pass:

```bash
python scripts/validate_non_interference.py
# OK — all records satisfy J-NIS guarantees
```

Reference validator: [echo-control-tower/scripts/validate_non_interference.py](https://github.com/Nick-heo-eg/echo-control-tower/blob/main/scripts/validate_non_interference.py)
