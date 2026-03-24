# J-NIS v1.1.0 (Draft Standard – Ready for use)

> **AI must not execute decisions, only evaluate boundaries.**

This draft is ready for use for non-interference tracing.

`[J-NIS Compliant]` · No dependencies · Open standard · No system redesign needed

```
Category:   AI Safety Standard
Layer:      Decision Boundary & Non-Interference
Type:       Constraint-based Specification
Capability: Trace Recording & Compliance Verification
```

Tags: `AI Safety` · `Governance` · `Decision Boundary` · `Compliance`

---

## Definition

J-NIS defines a trace structure for AI systems where decision authority is explicitly excluded.

This standard separates evaluation from execution as recorded fields, and defines verifiable invariants over those records.

---

## TL;DR

An AI system that implements J-NIS records — through its trace — that it evaluated without deciding.

```
observe → evaluate → record
                  ↑
          never execute
```

Three structural rules:
1. The gate is a pure function. It returns permissibility — it does not execute.
2. `decision_made` is always `false` in the trace.
3. `allowed` and `executed` are always separate fields.

> **J-NIS defines constraints on the trace record, not on underlying system behavior.**

If your system outputs `decision_made: false`, it satisfies J-NIS trace compliance.

**Try J-NIS in 30 seconds → [ZERO_SETUP.md](ZERO_SETUP.md)**

---

**Without J-NIS:** implicit decisions, no verifiable boundary between evaluation and execution.
**With J-NIS:** separated trace fields, verifiable invariants, independently checkable records.

---

## Input / Output Contract

```
policy_input  →  action_decisions  →  proof
(5 keys)         (allowed + executed  (decision_made
 evidence only)   always separate)     always false)
```

| Stage | Input | Output | Constraint |
|---|---|---|---|
| Gate | `policy_input` | `action_decisions` | Returns permissibility only, no side effects |
| Trace | `action_decisions` | `proof` block | `decision_made: false`, always |
| Validate | trace `.jsonl` | `JNIS_STANDARD_V1_1_OK` | Structural invariants, not behavioral |

---

## Traditional AI vs J-NIS

| | Traditional AI control | J-NIS compliant |
|---|---|---|
| Evaluation + execution | Same code path | Recorded as separate fields |
| Decision record | Post-hoc log (if any) | Pre-execution trace record |
| `decision_made` field | Not tracked | Always `false`, always present |
| Gate function | Stateful, may trigger | Returns permissibility only |
| Audit trail | Reconstructed | Recorded before execution |
| Non-interference | Convention | Trace-recorded assertion |

---

## Core Components

| Component | Role |
|---|---|
| `policy_input` | Fixed 5-key evidence snapshot. The only input to the gate. |
| `action_gate` | Returns `{allowed, reason, action_level}`. Does not execute. |
| `action_decisions` | Gate results per action. `allowed` and `executed` are always separate fields. |
| `proof` | Per-cycle record. `decision_made: false`. |

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

After validation, you may request access to a full reference implementation.
See the [Contact](#contact) section below.

---

## Documentation

| Document | Purpose |
|---|---|
| [SPEC_NON_INTERFERENCE.md](SPEC_NON_INTERFERENCE.md) | The five principles, gate contract, compliance levels |
| [TRACE_SPEC.md](TRACE_SPEC.md) | Trace field definitions, constraints, OTel mapping |
| [DROP_INTEGRATION.md](DROP_INTEGRATION.md) | 3-step guide: add J-NIS to any existing system |
| [WHY.md](WHY.md) | Why implicit AI decisions are difficult to audit |
| [QUICKSTART.md](QUICKSTART.md) | Minimal 10-line implementation |
| [ZERO_SETUP.md](ZERO_SETUP.md) | 30-second single-file demo |
| [ADOPTION_FLOW.md](ADOPTION_FLOW.md) | 5-step adoption loop |
| [COMPLIANCE.md](COMPLIANCE.md) | Compliance levels L0–L3 with verification methods |

---

## Annexes

Domain-specific annexes extend the core specification without modifying it.

| Annex | Domain |
|---|---|
| [ANNEX_FINANCE.md](ANNEX_FINANCE.md) | Financial systems: trading, credit, fraud, risk, AML/KYC |

Each annex preserves the core MUST/MUST NOT invariants.

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

Any system's trace can be evaluated against J-NIS compliance levels without internal access.

**J-NIS defines a measurable trace boundary.**

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

**Compliance must be verifiable without access to the original system's runtime.**

The trace record alone — `policy_input` + `action_decisions` + `proof` — is sufficient to verify structural invariants (L0–L1) and gate determinism (L2) given the gate function definition.

```bash
# L2 + L3 combined verification
python scripts/replay_demo.py decisions.jsonl
# PASS — L2 (trace reproducible) + L3 (invariants verified)
# VERIFIED — this trace satisfies that requirement.
```

---

## Normative Statement

An AI system is J-NIS compliant if:

- `decision_made` is always `false` in the trace
- `action_decisions` are explicitly recorded with `executed: false`
- execution is externally controlled
- trace is reproducible from stored `policy_input`

J-NIS compliance is determined by trace invariant satisfaction.

**Scope:** J-NIS verifies what the trace records. Whether the system actually withheld execution is outside the trace boundary and must be ensured by system architecture and operator controls.

---

## Compliance Definition

J-NIS compliance = `action_decisions` present + `decision_made: false` + `executed: false` + trace reproducible.

No certification. No approval process. No integration fee.

**A system that produces `action_decisions` with `decision_made: false` satisfies J-NIS trace compliance.**

Verify:
```bash
python validate_non_interference.py your_decisions.jsonl
# JNIS_COMPLIANT
# JNIS_STANDARD_V1_1_OK
```

Compliance does not require the reference implementation. The spec and validator are sufficient.

---

## Reference Implementation

A reference implementation exists:

- **echo-control-tower** (private repository, early-stage)

Demonstrates: action gating · deterministic trace · per-cycle `proof` block · Streamlit UI · OTel trace

If you need a reference implementation, see the [Contact](#contact) section.

---

## Why This Matters

When an AI system evaluates and executes in the same code path, there is no structural record of what the system considered before it acted. Audits reconstruct rather than verify.

J-NIS makes the evaluation record a required trace artifact — written before execution, independently verifiable. See [WHY.md](WHY.md) for the full argument.

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

If you need a reference implementation:

- [Open a GitHub issue](../../issues/new/choose) — use the **"Request: J-NIS reference access"** template
- Or contact via profile: [github.com/Nick-heo-eg](https://github.com/Nick-heo-eg)

For evaluation requests, use the **"Evaluation Request: External System"** issue template.

---

## Version

`JNIS_VERSION: v1.1.0` · `Status: Draft Standard`
