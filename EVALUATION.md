# EVALUATION — J-NIS External Evaluation Protocol

> Any system's trace can be evaluated against J-NIS compliance levels without internal access.
> Input: a trace file. Output: compliance level, violations, summary.

---

## Purpose

J-NIS defines a measurable trace boundary.
This protocol enables independent evaluation of any system's trace against J-NIS compliance levels.

---

## Required Inputs

| Input | Format | Required |
|---|---|---|
| `trace.jsonl` | Newline-delimited JSON, one record per line | Yes |

Each record must be a single JSON object. Records without `policy_input` or `proof` are evaluated as violations.

---

## Evaluation Steps

### Step 1 — Check `decision_made`

For each record: `proof.decision_made` must be `false`.

Failure → L0 violation. The record does not carry a non-interference assertion.

### Step 2 — Check `action_decisions`

For each record: `action_decisions` must be present, non-empty, and contain `action`, `allowed`, `reason`, `action_level`, `executed` per entry.

`executed` must be `false` in all entries.
`reason` must be from the declared `VALID_REASONS` set.

Failure → L1 violation. Gate results were not recorded, execution was flagged, or an unrecognized reason was used.

### Step 3 — Check invariant set

For each record:
- `policy_input` must have exactly 5 required keys
- `jnis_version` must be present

Failure → L3 violation. Structural invariants not satisfied.

### Step 4 — Assign compliance level

| Result | Level |
|---|---|
| No violations, all records pass replay | `L3` |
| No structural violations, replay not checked | `L2` |
| `action_decisions` present, no execution flags | `L1` |
| Only `decision_made: false` verified | `L0` |
| Any violation | `NON_COMPLIANT` |

---

## Output Format

```json
{
  "compliant": true,
  "level": "L3",
  "records_checked": 5,
  "violations": [],
  "summary": "All 5 records satisfy J-NIS invariants. Compliance level: L3."
}
```

On violation:

```json
{
  "compliant": false,
  "level": "NON_COMPLIANT",
  "records_checked": 3,
  "violations": [
    "[2026-01-01T00:00:00+00:00] L0 VIOLATION: proof.decision_made = true"
  ],
  "summary": "1 violation found across 3 records. System does not satisfy J-NIS compliance."
}
```

---

## Usage

```bash
python scripts/evaluate_system.py path/to/trace.jsonl
```

No access to the evaluated system is required. The trace is sufficient for L0–L1 and L3.
L2 (replay) requires the gate function definition.

---

## Three Verification Paths

| Tool | What it verifies | When to use |
|---|---|---|
| `validate_non_interference.py` | Internal invariant check (L3) | Your own system's trace |
| `scripts/replay_demo.py` | Trace reconstruction (L2 + L3) | Determinism verification |
| `scripts/evaluate_system.py` | External system assessment | Any system's trace |

This protocol is domain-agnostic.
Financial traces may be evaluated with additional domain-specific requirements.
See [ANNEX_FINANCE.md](ANNEX_FINANCE.md) for domain-specific compliance mapping and audit procedure.
