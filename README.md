# J-NIS (Judgment Non-Interference Standard)

> **AI must not execute decisions, only evaluate boundaries.**

`J-NIS compliant` · Reference implementation available (private)

---

## TL;DR

An AI system that implements J-NIS can prove — through its trace — that it evaluated without deciding.

```
observe → evaluate → record
                  ↑
          never execute
```

Three structural rules:
1. The gate is a pure function. It cannot execute anything.
2. `decision_made` is always `false` in the trace.
3. `allowed` and `executed` are always separate fields.

---

## Traditional AI vs J-NIS

| | Traditional AI control | J-NIS compliant |
|---|---|---|
| Evaluation + execution | Same code path | Structurally separated |
| Decision record | Post-hoc log (if any) | Pre-execution trace |
| `decision_made` field | Not tracked | Always `false`, always present |
| Gate function | Stateful, may trigger | Pure function, no side effects |
| Audit trail | Reconstructed | Verifiable |
| Non-interference proof | Convention | Structural guarantee |

---

## Core Components

| Component | Role |
|---|---|
| `policy_input` | Fixed 5-key evidence snapshot. The only input to the gate. |
| `action_gate` | Pure function → `{allowed, reason}`. No execution. |
| `action_decisions` | Gate results per action. `allowed` and `executed` are always separate. |
| `proof` | Per-cycle machine-readable assertion. `decision_made: false`. |

---

## Quickstart

See [QUICKSTART.md](QUICKSTART.md) — implement J-NIS in 10 lines of code.

---

## Validate compliance

```bash
python validate_non_interference.py decisions.jsonl
# Records checked: 1
# JNIS_COMPLIANT — all records satisfy J-NIS guarantees
```

After validation, you may request access to a full production-grade reference implementation.

---

## Documentation

| Document | Purpose |
|---|---|
| [SPEC_NON_INTERFERENCE.md](SPEC_NON_INTERFERENCE.md) | The five principles, gate contract, compliance levels |
| [TRACE_SPEC.md](TRACE_SPEC.md) | Trace field definitions, constraints, OTel mapping |
| [DROP_INTEGRATION.md](DROP_INTEGRATION.md) | 3-step guide: add J-NIS to any existing system |
| [WHY.md](WHY.md) | Why implicit AI decisions fail at scale |
| [QUICKSTART.md](QUICKSTART.md) | Minimal 10-line implementation |

---

## Reference Implementation

A full reference implementation exists:

- **echo-control-tower** (private repository)

This implementation demonstrates:
- action gating with a pure-function gate
- deterministic trace with per-cycle `proof` block
- non-interference proof via `validate_non_interference.py`
- Streamlit UI for real-time observation

This standard is already implemented and operational in a production-grade control system.

Access may be provided upon request.

---

## Why This Matters

When an AI system evaluates and executes in the same code path, there is no structural boundary between "the system considered X" and "the system did X." Responsibility becomes ambiguous. Audits reconstruct rather than verify.

J-NIS makes non-interference a structural property — not a convention. See [WHY.md](WHY.md) for the full argument.

---

## Compliance

If your system produces `decision_made: false` with a valid trace, it is J-NIS compliant.

Verify with:
```bash
python validate_non_interference.py your_decisions.jsonl
# JNIS_COMPLIANT
```

Compliance does not require the reference implementation. The spec and validator are sufficient.

---

## Adoption Path

See [ADOPTION_FLOW.md](ADOPTION_FLOW.md) — the full 5-step loop from concept to production.

---

## Version

`JNIS_VERSION: v1.0.1`
