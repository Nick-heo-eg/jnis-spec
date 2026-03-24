---
name: "Evaluation Request: External System"
about: Request J-NIS compliance evaluation for an external system trace
title: "Evaluation: [system name or description]"
labels: evaluation-request
assignees: Nick-heo-eg
---

## System Description

_Brief description of the system to be evaluated._

## Trace Upload

Attach your `decisions.jsonl` trace file, or paste a representative sample (1–5 records):

```jsonl
<paste trace records here>
```

If your trace is too large to paste, describe its structure:
- Records per cycle:
- Approximate record count:
- `jnis_version` present: Yes / No

## Self-Evaluation Result (optional)

Run `python scripts/evaluate_system.py your_trace.jsonl` and paste the output:

```
<paste output here>
```

## Evaluation Goal

_What are you trying to verify? (e.g. compliance level, specific invariant, replay determinism)_

## Expected Compliance Level

- [ ] L0 — `decision_made: false` present
- [ ] L1 — `action_decisions` recorded
- [ ] L2 — trace reproducible
- [ ] L3 — all invariants satisfied

---

> Attach or link your trace file. No access to your source system is required for evaluation.
