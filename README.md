# J-NIS — Judgment Non-Interference Specification

> **Status: Under active reconstruction**
>
> This repository is currently frozen while we validate boundary enforcement and proof cases.
> Current contents are not intended for production or compliance use.

---

## Upcoming release will include

- Verifiable enforcement demo
- Decision-commit boundary implementation
- Trace-level evidence of blocked actions
- Validated domain cases

Public-facing release will resume after proof validation.

---

## What this is

J-NIS defines a boundary-oriented approach for separating AI evaluation from externally controlled execution. This repository is being restructured around proof-first validation.

---

## Specification documents

| Document | Status |
|---|---|
| [SPEC_NON_INTERFERENCE.md](SPEC_NON_INTERFERENCE.md) | Draft |
| [TRACE_SPEC.md](TRACE_SPEC.md) | Draft |
| [COMPLIANCE.md](COMPLIANCE.md) | Draft |
| [ANNEX_FINANCE.md](ANNEX_FINANCE.md) | Exploratory |
| [WHY.md](WHY.md) | Draft |

---

## Demo and trace evidence

Demo and trace evidence will be added after proof validation.

See [TODO_PROOF.md](TODO_PROOF.md) for the current proof validation checklist.

---

`JNIS_VERSION: 1.1.0` · `Status: Frozen for proof validation`

---

## Execution control layers

Execution is restricted at two layers:

1. **CLI-level permission controls** (Claude Code settings) — the AI cannot attempt `git commit` or `git push`
2. **Repository-level enforcement** via J-NIS hooks and trace validation — commit is blocked without a valid trace, regardless of who attempts it

This ensures both prevention and verifiable non-interference.

All execution (commit/push) is restricted by permission layer and J-NIS enforcement layer. AI cannot execute actions and cannot bypass this constraint. Execution occurs only through validated system triggers.

Hooks are repository-scoped (no global hooks are used)
