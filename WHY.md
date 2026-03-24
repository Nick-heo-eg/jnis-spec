# WHY — The Case for Judgment Non-Interference

---

## What Breaks Without J-NIS

| What breaks | Why |
|---|---|
| **No record of evaluation** | Without a pre-execution trace, there is no artifact showing what the system considered before acting |
| **Logs cannot confirm ordering** | Post-hoc logs show what happened; they cannot confirm the gate was evaluated before execution |
| **Audit reconstructs rather than verifies** | Without a pre-execution trace, auditors reconstruct events from outcomes — not from a captured decision boundary |
| **Mode collapse** | Systems that can switch between observe and execute modes without structural enforcement have no independently verifiable boundary |
| **Stale-state execution** | Without an explicit staleness check in the gate, systems may act on outdated observations with no record of the staleness |
| **Retroactive justification** | "We acted because X" is a reconstruction — not a record that X was evaluated before the action occurred |

This standard is implemented in a reference control system (early-stage, internal use).

---

## The Problem

Today's AI-adjacent control systems have a structural gap: **evaluation and execution share the same code path, with no required record of the boundary.**

A typical autonomous loop looks like this:

```
observe → evaluate → execute
```

There is no required record of what the system considered before it acted. There is no required artifact confirming evaluation and execution are distinct operations. When something goes wrong:

- Was it the evaluation logic?
- Was it the execution condition?
- Did the system act on stale data?
- Was the gate evaluated at all?

These questions may not be answerable, because the system may never have recorded the boundary.

---

## The Specific Failure Modes

### 1. Implicit decisions

A system that calls `if should_restart(): restart()` has combined evaluation and execution in a single stack frame. There is no required record that `should_restart()` returned `true` before `restart()` was called. There is no artifact capturing the gate state.

### 2. Retroactive justification

Without a pre-execution trace, any post-hoc explanation of why an action was taken is a reconstruction, not a record. The system can say "we restarted because X" — but cannot produce a record showing "at time T, the gate evaluated X and returned GATE_PASSED."

### 3. Mode collapse

When a system can switch between "observe mode" and "execute mode" at runtime without structural enforcement, the boundary is a convention — not an independently verifiable property.

---

## The J-NIS Answer

J-NIS requires the separation to be recorded:

**The gate function is a pure function.** It returns permissibility. Calling it changes nothing. The return value is not a trigger.

**The trace is written before any execution.** The record exists regardless of what happens next. If execution never occurs, the trace still records that the gate evaluated and produced a result.

**`decision_made` is always `false` in the trace.** Every cycle records that the AI system did not exercise decision authority in that cycle.

**`allowed` and `executed` are separate fields.** They are recorded independently. `allowed: true, executed: false` is the normal state of a J-NIS compliant record — the gate passed, nothing was executed, and the record captures both facts.

**J-NIS does not prevent execution.** It requires that execution authority is held by an external component, and that the gate evaluation is recorded before execution occurs. Whether execution actually took place is outside the trace boundary.

---

## What J-NIS Enables

An AI system that implements J-NIS can answer the following questions from its trace:

| Question | Answer source |
|---|---|
| Did the system evaluate this action? | `action_decisions[].action` |
| What was the state when it evaluated? | `policy_input` |
| Did the gate pass or block? | `action_decisions[].allowed + reason` |
| Was anything recorded as executed? | `action_decisions[].executed` |
| Did the system record a decision? | `proof.decision_made` |

These questions are answerable from the trace. The answers are independently verifiable.

**What J-NIS cannot answer from the trace:** whether execution actually occurred outside the recorded fields. That verification requires operator controls and system architecture review.

---

## Who Needs This

Any system where:

- An AI model or rule engine evaluates actions
- Those actions have real-world consequences
- There is a regulatory, legal, or operational requirement to record the evaluation boundary

Potential application domains: autonomous infrastructure management, financial risk evaluation systems, LLM-based operations automation, AI-assisted triage systems.

---

## The Claim

J-NIS defines a trace structure for recording the separation between AI evaluation and execution — with a verifiable format, a deterministic gate contract, and a validator that checks structural invariants.

The claim is not "AI can't make decisions." The claim is: **if you want to record that AI did not make a decision, this is the trace structure that makes that record independently verifiable.**

---

## Adoption Path

J-NIS is designed to be adopted incrementally. Any system at any stage can move toward compliance:

```
Small system
    │
    ▼
Add policy_input
    Convert your state into a fixed 5-key evidence snapshot.
    No gate yet — just structure your observations.
    │
    ▼
Add gate
    Write a pure function: (action, policy_input) → {allowed, reason, action_level}.
    It returns permissibility. It does not execute.
    │
    ▼
Add trace
    Write a record before execution: policy_input + action_decisions + proof.
    decision_made: false. Always.
    │
    ▼
Full non-interference system
    Gate is deterministic. Trace is append-only. Replay is verifiable.
    Run validate_non_interference.py → JNIS_COMPLIANT.
```

Each step adds a structural record independently of the others. A system that only adds `policy_input` is more auditable than one that doesn't. A system that only adds the trace has more verifiable output than one that doesn't.

J-NIS is not all-or-nothing. It is a direction.
