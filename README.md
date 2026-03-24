# J-NIS v1.1.0 (Draft Standard – Ready for use)

> **AI must not execute decisions, only evaluate boundaries.**

This draft is production-usable for non-interference enforcement.

`[J-NIS Compliant]` · No dependencies · Open standard · No system redesign needed

```
Category:   AI Safety Standard
Layer:      Decision Boundary & Non-Interference
Type:       Constraint-based Specification
Capability: Evaluation & Compliance Verification
```

Tags: `AI Safety` · `Governance` · `Decision Boundary` · `Compliance`

---

## Definition

J-NIS defines a constraint-based boundary for AI systems where decision authority is explicitly excluded.

This standard separates evaluation from execution and enforces non-interference.

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

> **J-NIS defines constraints, not capabilities.**

If your system outputs `decision_made: false`, it satisfies J-NIS compliance.

**Try J-NIS in 30 seconds → [ZERO_SETUP.md](ZERO_SETUP.md)**

---

**Without J-NIS:** implicit decisions, no proof of non-interference.
**With J-NIS:** provable non-interference, verifiable trace, structural separation.

---

## Input / Output Contract

```
policy_input  →  action_decisions  →  proof
(5 keys)         (allowed + executed  (decision_made
 evidence only)   always separate)     always false)
```

| Stage | Input | Output | Constraint |
|---|---|---|---|
| Gate | `policy_input` | `action_decisions` | Pure function, no side effects |
| Trace | `action_decisions` | `proof` block | `decision_made: false`, always |
| Validate | trace `.jsonl` | `JNIS_STANDARD_V1_1_OK` | Structural, not behavioral |

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
# JNIS_STANDARD_V1_1_OK
```

After validation, you may request access to a full production-grade reference implementation.
See the [Contact](#contact) section below.

---

## Documentation

| Document | Purpose |
|---|---|
| [SPEC_NON_INTERFERENCE.md](SPEC_NON_INTERFERENCE.md) | The five principles, gate contract, compliance levels |
| [TRACE_SPEC.md](TRACE_SPEC.md) | Trace field definitions, constraints, OTel mapping |
| [DROP_INTEGRATION.md](DROP_INTEGRATION.md) | 3-step guide: add J-NIS to any existing system |
| [WHY.md](WHY.md) | Why implicit AI decisions fail at scale |
| [QUICKSTART.md](QUICKSTART.md) | Minimal 10-line implementation |
| [ZERO_SETUP.md](ZERO_SETUP.md) | 30-second single-file demo |
| [ADOPTION_FLOW.md](ADOPTION_FLOW.md) | 5-step adoption loop |
| [COMPLIANCE.md](COMPLIANCE.md) | Compliance levels L0–L3 with verification methods |

---

## Compliance Levels

| Level | Requirement | Verified by |
|---|---|---|
| L0 | `decision_made: false` present | trace inspection |
| L1 | `action_decisions` recorded | trace inspection |
| L2 | gate is deterministic, trace reproducible | `scripts/replay_demo.py` |
| L3 | all invariants hold across full trace | `validate_non_interference.py` |

A system satisfying L3 satisfies all lower levels.
See [COMPLIANCE.md](COMPLIANCE.md) for full definitions.

---

## Evaluation

J-NIS can be used to evaluate external systems.

Any system can be evaluated using J-NIS without internal access.

**J-NIS defines a measurable boundary, not a conceptual one.**

```bash
python scripts/evaluate_system.py path/to/any_trace.jsonl
# Compliant: True
# Compliance Level: L3
# Summary: All N records satisfy J-NIS invariants.
```

See [EVALUATION.md](EVALUATION.md) for the full evaluation protocol and output format.

---

## Three Verification Paths

| Path | Tool | What it verifies |
|---|---|---|
| 1 — Internal invariant check | `validate_non_interference.py` | Structural invariants (L3) |
| 2 — Trace reconstruction | `scripts/replay_demo.py` | Gate determinism (L2 + L3) |
| 3 — External system assessment | `scripts/evaluate_system.py` | Any system's trace (L0–L3) |

All three tools operate on trace files only. No access to the source system is required.

---

## Reproducibility

J-NIS compliance must be independently verifiable from trace logs.

**Compliance must be verifiable without access to the original system.**

The trace record alone — `policy_input` + `action_decisions` + `proof` — is sufficient to verify compliance at all four levels.

```bash
# L2 + L3 combined verification
python scripts/replay_demo.py decisions.jsonl
# PASS — L2 (trace reproducible) + L3 (invariants verified)
# VERIFIED — this trace satisfies that requirement.
```

---

## Normative Statement

An AI system is J-NIS compliant if:

- `decision_made` is always `false`
- `action_decisions` are explicitly recorded
- execution is externally controlled
- trace is reproducible

J-NIS compliance is determined by invariant satisfaction, not system behavior.

---

## Compliance Definition

J-NIS compliance = `action_decisions` present + `decision_made: false` + trace reproducible.

No certification. No approval process. No integration fee.

**A system that produces `action_decisions` with `decision_made: false` satisfies J-NIS compliance.**

Verify:
```bash
python validate_non_interference.py your_decisions.jsonl
# JNIS_COMPLIANT
# JNIS_STANDARD_V1_1_OK
# You are already J-NIS compliant
# No further integration required

# or instantly, no file needed:
python validate_non_interference.py --quick-test
# JNIS_STANDARD_V1_1_OK
```

Compliance does not require the reference implementation. The spec and validator are sufficient.

---

## Reference Implementation

A full reference implementation exists:

- **echo-control-tower** (private repository)

Demonstrates: action gating · deterministic trace · per-cycle `proof` block · Streamlit UI · OTel trace

Early-stage reference exists and is actively used internally.
Minimal systems have already validated J-NIS compliance internally.

If you need a production-grade implementation, see the [Contact](#contact) section.

---

## Why This Matters

When an AI system evaluates and executes in the same code path, there is no structural boundary between "the system considered X" and "the system did X." Responsibility becomes ambiguous. Audits reconstruct rather than verify.

J-NIS makes non-interference a structural property — not a convention. See [WHY.md](WHY.md) for the full argument.

---

## No Adoption Barrier

J-NIS is an open standard and requires no permission for use.

- No registration
- No approval process
- No dependency installation
- No system redesign

Copy the gate function from [ZERO_SETUP.md](ZERO_SETUP.md), run it, validate. You are compliant.

---

## Adoption Path

See [ADOPTION_FLOW.md](ADOPTION_FLOW.md) — the full 5-step loop from concept to production.

---

## Contact

You don't need to contact anyone to use J-NIS. The spec, validator, and quickstart are fully self-contained.

If you need a production-grade implementation:

- [Open a GitHub issue](../../issues/new/choose) — use the **"Request: J-NIS reference access"** template
- Or contact via profile: [github.com/Nick-heo-eg](https://github.com/Nick-heo-eg)

A full reference implementation (Streamlit UI, deterministic replay, OTel trace) may be made available.

For evaluation requests, use the **"Evaluation Request: External System"** issue template.

---

## Version

`JNIS_VERSION: v1.1.0` · `Status: Draft Standard`
