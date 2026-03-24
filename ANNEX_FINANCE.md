# Annex A: Financial Systems Application

> This annex is normative for J-NIS compliance in financial systems.
> It extends the core specification without modifying it.

---

## Definition

J-NIS applies to financial systems by enforcing separation between evaluation and execution layers.

In financial systems, the AI system evaluates conditions and boundaries.
Execution — order placement, credit issuance, blocking enforcement, risk limit activation — is externally controlled and MUST NOT be performed by the AI system.

---

## Scope

Domains to which this annex applies:

- Trading and order management
- Credit and lending decisioning
- Fraud detection and prevention
- Risk management and limit enforcement
- Investment advisory and portfolio recommendations
- AML/KYC screening and compliance

---

## Evaluation Boundaries

For each domain, the table defines the evaluation boundary and the separation requirement.

| Domain | Evaluation (AI performs) | Execution (external) | J-NIS Structural Requirement |
|---|---|---|---|
| **Trading** | Signal generation, order feasibility assessment | Order placement, trade submission | Gate MUST NOT submit orders; execution is external |
| **Credit** | Risk scoring, eligibility assessment | Loan issuance, credit line activation | Gate MUST NOT issue credit; execution is external |
| **Fraud detection** | Anomaly scoring, pattern classification | Transaction blocking, account suspension | Gate MUST NOT enforce blocking; `executed` MUST be `false` |
| **Risk management** | Limit proximity assessment, exposure evaluation | Limit activation, position unwinding | Gate evaluation MUST NOT trigger execution |
| **Advisory** | Portfolio fit assessment, suitability scoring | Trade execution, allocation change | Gate MUST NOT execute allocations; execution is external |
| **AML/KYC** | Pattern scoring, flag generation | Case escalation, account restriction | Gate MUST NOT restrict accounts; execution is external |

---

## Compliance Mapping

Each financial control maps to a J-NIS invariant.

| Financial Control | J-NIS Invariant |
|---|---|
| Trading audit trail | `decision_made` MUST be `false` in every cycle |
| Credit approval separation | Execution MUST be externally controlled |
| Fraud blocking isolation | AI MUST NOT enforce blocking — `executed` MUST be `false` |
| Risk limit enforcement | Evaluation MUST NOT trigger execution |
| AML escalation | `action_decisions` MUST be recorded before any escalation occurs |
| Regulatory reproducibility | Trace MUST be sufficient for post-hoc reconstruction |

---

## Trace Requirement in Finance

Financial systems MUST produce trace logs sufficient for post-hoc audit and independent verification.

Specifically:

- Every evaluation cycle MUST produce a record containing `policy_input`, `action_decisions`, and `proof`
- `proof.decision_made` MUST be `false`
- The trace MUST be append-only — no record is modified after writing
- The trace MUST be sufficient to reconstruct the gate evaluation without access to the live system

A financial system that cannot produce a verifiable trace does not satisfy J-NIS compliance requirements.

---

## Audit Procedure

J-NIS provides a standardized audit procedure for financial systems.

**Inputs required from the audited system:**

```
trace.jsonl   — append-only log of evaluation cycles
```

No access to the live system, model weights, or internal logic is required.

**Audit execution:**

```bash
python scripts/evaluate_system.py path/to/trace.jsonl --json
```

**Audit output:**

```json
{
  "compliant": true,
  "level": "L3",
  "records_checked": 1000,
  "violations": [],
  "summary": "All 1000 records satisfy J-NIS invariants. Compliance level: L3."
}
```

The output constitutes a machine-verifiable compliance record.

**Auditor responsibilities:**

1. Verify `compliant: true`
2. Verify `level` meets the required threshold (typically L3 for financial systems)
3. Verify `violations` is empty
4. Retain the `evaluate_system.py` output as an audit artifact

---

## Regulatory Alignment (Non-normative)

> This section is non-normative. References to regulatory frameworks are provided for orientation only.
> J-NIS does not claim conformance with or certification under any regulatory framework.
> MUST language is not used in this section.

| Framework | Relevant principle | J-NIS structural alignment |
|---|---|---|
| **Basel III/IV** | Model risk management, auditability of decision models | Trace-based audit; gate determinism enables model behavior reconstruction |
| **SOX (Sarbanes-Oxley)** | Internal controls over financial reporting | `proof.decision_made = false` provides a per-cycle control assertion |
| **DORA (EU)** | ICT risk management, operational resilience, auditability | Append-only trace; independent verification without system access |
| **MiFID II** | Best execution, audit trail requirements | Pre-execution trace records gate state at time of evaluation |
| **SR 11-7 (Fed)** | Model validation, governance of model outputs | Replay-based verification enables independent model output validation |

These alignments are structural observations, not compliance claims.
Legal and regulatory compliance determination requires jurisdiction-specific assessment.

---

## Minimal Sequence (Non-normative)

The following pseudocode illustrates the structural separation J-NIS enforces in a financial system.
AI performs evaluation only. Execution is performed exclusively by an external component.

```
# 1. Collect observable state
policy_input = collect_state()          # 5 keys, evidence only

# 2. Evaluate — AI boundary ends here
action_decisions = gate(policy_input, candidate_actions)
# action_decisions[*].executed = False  ← always, at this stage

# 3. Append trace before any execution
trace.append({
    "policy_input":     policy_input,
    "action_decisions": action_decisions,
    "proof":            {"decision_made": False}
})

# 4. External executor decides and records
for decision in action_decisions:
    if decision["allowed"] and external_authorization(decision):
        external_executor.run(decision["action"])
        decision["executed"] = True     # set by executor, not AI
```

The AI system has no reference to `external_executor`. Execution authority is structurally absent.

---

## Trace Significance (Non-normative)

Financial audits require post-hoc verifiability independent of the originating system.
The trace should be sufficient for regulator review without system access.

---

## Audit Baseline (Non-normative)

For financial systems, L3 compliance (invariants verified + replayable trace) is recommended as baseline.
