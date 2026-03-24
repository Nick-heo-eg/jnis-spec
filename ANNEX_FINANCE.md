# Annex A: Financial Systems Application

> **This annex is a conceptual extension under validation and does not represent regulatory compliance, legal guidance, or production readiness.**
>
> This annex is exploratory. It illustrates how J-NIS structural patterns may apply in financial system contexts.
> It is not a normative extension of the core specification and does not create compliance obligations.

---

## Note on Language

This annex uses exploratory and descriptive language.
Expressions such as *may*, *intended to*, *under validation*, and *experimental* reflect the current status of this mapping.
Normative requirements are defined in SPEC_NON_INTERFERENCE.md only.
This annex is an exploratory mapping, not a normative extension.

---

## Definition

J-NIS may apply to financial systems by providing a structural pattern for separating evaluation from execution.

In financial systems, the AI judgment layer may record whether conditions and boundaries for an action are met.
Execution — order placement, credit issuance, blocking enforcement, risk limit activation — is intended to be handled by an external component separate from the AI judgment layer.
The trace is intended to record that the gate evaluated without executing.

**Scope:** This annex describes structural patterns, not verified implementations. Actual separation of execution authority must be ensured by system architecture and is not verifiable from the trace alone.

---

## Scope

Domains to which this annex may apply (under validation):

- Trading and order management
- Credit and lending decisioning
- Fraud detection and prevention
- Risk management and limit enforcement
- Investment advisory and portfolio recommendations
- AML/KYC screening and compliance

---

## Evaluation Boundaries (Exploratory)

This table illustrates how J-NIS structural patterns may map to financial domain boundaries. These mappings are under validation.

| Domain | Evaluation (gate records) | Execution (external) | Intended Structural Pattern |
|---|---|---|---|
| **Trading** | Signal generation, order feasibility assessment | Order placement, trade submission | The AI judgment system is intended to have no capability to submit orders (`executed` may remain `false`) |
| **Credit** | Risk scoring, eligibility assessment | Loan issuance, credit line activation | The AI judgment system is intended to have no capability to issue credit (`executed` may remain `false`) |
| **Fraud detection** | Anomaly scoring, pattern classification | Transaction blocking, account suspension | The AI judgment system is intended to have no capability to enforce blocking (`executed` may remain `false`) |
| **Risk management** | Limit proximity assessment, exposure evaluation | Limit activation, position unwinding | The AI judgment system is intended to have no capability to trigger limit activation (`executed` may remain `false`) |
| **Advisory** | Portfolio fit assessment, suitability scoring | Trade execution, allocation change | The AI judgment system is intended to have no capability to execute allocations (`executed` may remain `false`) |
| **AML/KYC** | Pattern scoring, flag generation | Case escalation, account restriction | The AI judgment system is intended to have no capability to restrict accounts (`executed` may remain `false`) |

---

## Compliance Mapping (Exploratory)

This mapping illustrates how financial controls may align with J-NIS structural patterns. Under validation.

| Financial Control | Intended J-NIS Pattern |
|---|---|
| Trading audit trail | `decision_made` may remain `false` in every cycle |
| Credit approval separation | `executed` may remain `false` in gate records; execution may be handled by an external component |
| Fraud blocking isolation | `executed` may remain `false`; blocking is intended to be outside the AI judgment layer |
| Risk limit enforcement | Gate evaluation is intended to be separate from execution; it does not trigger execution |
| AML escalation | `action_decisions` may be recorded before any escalation occurs |
| Regulatory reproducibility | Trace may be sufficient for post-hoc reconstruction of gate evaluation |

---

## Trace Pattern in Finance (Exploratory)

Financial systems using J-NIS may produce trace logs intended for post-hoc review.

Intended pattern:

- Each evaluation cycle may produce a record containing `policy_input`, `action_decisions`, and `proof`
- `proof.decision_made` may remain `false`
- The trace is intended to be append-only
- The trace is intended to be sufficient to reconstruct gate evaluation without access to the live system

A financial system that cannot produce a verifiable trace may not be considered aligned with this annex.

**Note:** A trace confirms that gate results were recorded with `executed: false`. It does not verify whether execution occurred outside the recorded fields. Architectural controls are intended to ensure actual execution separation.

---

## Audit Pattern (Exploratory)

This section illustrates a possible audit approach using J-NIS trace tooling. Under validation.

**Input:**

```
trace.jsonl   — append-only log of evaluation cycles
```

**Execution:**

```bash
python scripts/evaluate_system.py path/to/trace.jsonl --json
```

**Example output:**

```json
{
  "compliant": true,
  "level": "L3",
  "records_checked": 1000,
  "violations": [],
  "summary": "All 1000 records satisfy J-NIS invariants. Compliance level: L3."
}
```

This output reflects trace invariant satisfaction only. It is not a regulatory audit result.

Suggested review steps:
1. Check `compliant: true`
2. Check `level` (L3 is intended as a practical baseline for financial contexts)
3. Check `violations` is empty
4. Separately verify architectural controls for actual execution separation

---

## Regulatory Alignment (Non-normative, Exploratory)

> This section is non-normative and exploratory.
> References to regulatory frameworks are provided for orientation only.
> J-NIS does not claim conformance with or certification under any regulatory framework.

| Framework | Relevant principle | Possible J-NIS structural alignment |
|---|---|---|
| **Basel III/IV** | Model risk management, auditability of decision models | Trace-based record; gate determinism may enable evaluation reconstruction |
| **SOX (Sarbanes-Oxley)** | Internal controls over financial reporting | `proof.decision_made = false` may provide a per-cycle recorded assertion |
| **DORA (EU)** | ICT risk management, operational resilience, auditability | Append-only trace; independent verification without system access |
| **MiFID II** | Best execution, audit trail requirements | Pre-execution trace may record gate state at time of evaluation |
| **SR 11-7 (Fed)** | Model validation, governance of model outputs | Replay-based verification may enable independent gate output validation |

These are structural observations under validation, not compliance claims.
Legal and regulatory compliance determination requires jurisdiction-specific assessment.
This annex does not replace any regulatory requirements; it only provides a structural pattern that may support auditability.

---

## Minimal Sequence (Illustrative)

The following pseudocode illustrates the structural pattern J-NIS describes. Under validation.

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

The gate has no reference to `external_executor`. Execution authority is intended to be held by an external component.
The AI judgment layer is intended to have no direct execution capability or reference to execution systems.
