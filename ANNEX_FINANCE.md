# Annex A: Financial Systems Application

> This annex is normative for J-NIS compliance in financial systems.
> It extends the core specification without modifying it.
>
> Financial systems must satisfy both SPEC_NON_INTERFERENCE.md and this annex.
> Non-financial systems need only satisfy the core specification.

## Note on Language

This annex uses descriptive and structural language rather than normative (MUST/SHOULD) statements.
Normative requirements are defined in SPEC_NON_INTERFERENCE.md. This annex shows how those requirements apply in financial system contexts.

---

## Definition

J-NIS applies to financial systems by requiring recorded separation between evaluation and execution layers.

In financial systems, the AI judgment layer records whether conditions and boundaries for an action are met.
Execution — order placement, credit issuance, blocking enforcement, risk limit activation — is handled by an external component separate from the AI judgment layer.
The trace records that the gate evaluated without executing.

**Scope:** J-NIS verifies the recorded separation in the trace. Whether actual execution was externally controlled must be ensured by system architecture and is not verifiable from the trace alone.

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

For each domain, the table defines the evaluation boundary and the J-NIS structural expectation.

| Domain | Evaluation (gate records) | Execution (external) | J-NIS Structural Expectation |
|---|---|---|---|
| **Trading** | Signal generation, order feasibility assessment | Order placement, trade submission | The AI judgment system has no capability to submit orders (`executed` remains `false`) |
| **Credit** | Risk scoring, eligibility assessment | Loan issuance, credit line activation | The AI judgment system has no capability to issue credit (`executed` remains `false`) |
| **Fraud detection** | Anomaly scoring, pattern classification | Transaction blocking, account suspension | The AI judgment system has no capability to enforce blocking (`executed` remains `false`) |
| **Risk management** | Limit proximity assessment, exposure evaluation | Limit activation, position unwinding | The AI judgment system has no capability to trigger limit activation (`executed` remains `false`) |
| **Advisory** | Portfolio fit assessment, suitability scoring | Trade execution, allocation change | The AI judgment system has no capability to execute allocations (`executed` remains `false`) |
| **AML/KYC** | Pattern scoring, flag generation | Case escalation, account restriction | The AI judgment system has no capability to restrict accounts (`executed` remains `false`) |

---

## Compliance Mapping

Each financial control maps to a J-NIS structural expectation.

| Financial Control | J-NIS Structural Expectation |
|---|---|
| Trading audit trail | `decision_made` is expected to remain `false` in every cycle |
| Credit approval separation | `executed` is expected to remain `false` in gate records; execution is handled by an external component |
| Fraud blocking isolation | `executed` is expected to remain `false`; blocking is not performed by the AI judgment layer |
| Risk limit enforcement | Gate evaluation is not performed by the AI judgment layer; it does not trigger execution |
| AML escalation | `action_decisions` are expected to be recorded before any escalation occurs |
| Regulatory reproducibility | Trace is expected to be sufficient for post-hoc reconstruction of gate evaluation |

---

## Trace Requirement in Finance

Financial systems are expected to produce trace logs sufficient for post-hoc audit and independent verification.

Specifically:

- Every evaluation cycle is expected to produce a record containing `policy_input`, `action_decisions`, and `proof`
- `proof.decision_made` is expected to remain `false`
- The trace is expected to be append-only — no record is modified after writing
- The trace is expected to be sufficient to reconstruct gate evaluation without access to the live system

A financial system that cannot produce a verifiable trace may not be considered compliant under this annex.

**Note:** A verifiable trace confirms that gate results were recorded with `executed: false`. It does not verify whether execution occurred outside the recorded fields. Architectural controls are expected to ensure actual execution separation.

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

The output constitutes a machine-verifiable compliance record for the trace invariants.

**Auditor responsibilities:**

1. Verify `compliant: true`
2. Verify `level` meets the required threshold (L3 recommended for financial systems)
   L3 is recommended as a practical baseline for financial audit scenarios
3. Verify `violations` is empty
4. Retain the `evaluate_system.py` output as an audit artifact
5. Separately verify architectural controls for actual execution separation

---

## Regulatory Alignment (Non-normative)

> This section is non-normative. References to regulatory frameworks are provided for orientation only.
> J-NIS does not claim conformance with or certification under any regulatory framework.
> Normative language is not used in this section.

| Framework | Relevant principle | J-NIS structural alignment |
|---|---|---|
| **Basel III/IV** | Model risk management, auditability of decision models | Trace-based record; gate determinism enables evaluation reconstruction |
| **SOX (Sarbanes-Oxley)** | Internal controls over financial reporting | `proof.decision_made = false` provides a per-cycle recorded assertion |
| **DORA (EU)** | ICT risk management, operational resilience, auditability | Append-only trace; independent verification without system access |
| **MiFID II** | Best execution, audit trail requirements | Pre-execution trace records gate state at time of evaluation |
| **SR 11-7 (Fed)** | Model validation, governance of model outputs | Replay-based verification enables independent gate output validation |

These alignments are structural observations, not compliance claims.
Legal and regulatory compliance determination requires jurisdiction-specific assessment.
This annex does not replace any regulatory requirements; it only provides a structural pattern that may support auditability.

---

## Minimal Sequence (Non-normative)

The following pseudocode illustrates the structural separation J-NIS describes in a financial system.
The gate records evaluation results. Execution is performed by an external component.

```
# 1. Collect observable state
policy_input = collect_state()          # 5 keys, evidence only

# 2. Evaluate — gate returns permissibility, not instruction
action_decisions = gate(policy_input, candidate_actions)
# action_decisions[*].executed = False  ← always, at this stage

# 3. Append trace before any execution
trace.append({
    "policy_input":     policy_input,
    "action_decisions": action_decisions,
    "proof":            {"decision_made": False}
})

# 4. External executor decides and acts
for decision in action_decisions:
    if decision["allowed"] and external_authorization(decision):
        external_executor.run(decision["action"])
        # executed=True recorded by executor in its own log, not by the gate
```

The gate has no reference to `external_executor`. Execution authority is held by an external component.
The AI judgment layer has no direct execution capability or reference to execution systems.

---

## Audit Baseline (Non-normative)

For financial systems, L3 compliance (invariants verified + replayable trace) is the recommended baseline.
