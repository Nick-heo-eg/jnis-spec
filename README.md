# J-NIS (Judgment Non-Interference Standard)

> **J-NIS defines how AI systems must NOT make decisions.**

J-NIS is a structural standard that separates **observation**, **evaluation**, and **execution** in AI-adjacent control systems. A system that implements J-NIS can prove — through its trace log — that it evaluated without deciding.

---

## TL;DR

AI systems should never execute decisions.
They should only evaluate whether execution *would be* allowed.

```
observe → evaluate → record
                  ↑
             never execute
```

---

## Core Components

| Component | Role |
|---|---|
| `policy_input` | Fixed 5-key evidence snapshot. The only thing the gate reads. |
| `action_gate` | Pure function. Returns `{allowed, reason}`. No side effects. |
| `action_decisions` | List of gate results per action. `executed` is always separate from `allowed`. |
| `proof` | Per-cycle machine-readable non-interference assertion. `decision_made: false`. |

---

## Why

Modern AI systems implicitly make decisions. When an autonomous process acts on an evaluation, there is no structural boundary between "the system considered X" and "the system did X". This creates:

- **Auditability gaps** — impossible to reconstruct what was evaluated vs. what was executed
- **Responsibility ambiguity** — unclear whether the AI or the operator decided
- **Governance failure** — no verifiable record that non-interference was maintained

J-NIS solves this by enforcing explicit structural separation. See [WHY.md](WHY.md) for the full argument.

---

## Usage

See [DROP_INTEGRATION.md](DROP_INTEGRATION.md) — add J-NIS to an existing system in 3 steps.

---

## Trace Format

See [TRACE_SPEC.md](TRACE_SPEC.md) — every J-NIS cycle produces a verifiable trace record.

---

## Specification

See [SPEC_NON_INTERFERENCE.md](SPEC_NON_INTERFERENCE.md) — the five principles and required fields.

---

## Reference Implementation

**[echo-control-tower](https://github.com/Nick-heo-eg/echo-control-tower)** — a complete J-NIS implementation with Streamlit UI, gate evaluator, and append-only trace log.

```bash
git clone https://github.com/Nick-heo-eg/echo-control-tower
python scripts/health_check.py
python scripts/validate_non_interference.py
```

---

## Version

`JNIS_VERSION: v1.0.1`
