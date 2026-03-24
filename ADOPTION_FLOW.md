# ADOPTION_FLOW — J-NIS Adoption Path

```
┌─────────────────────────────────────────────────────────────────┐
│                    J-NIS Adoption Loop                          │
└─────────────────────────────────────────────────────────────────┘

  Step 1: Read README
  ┌─────────────────────────────────────────┐
  │  "AI must not execute decisions,        │
  │   only evaluate boundaries."           │
  │                                         │
  │  Understand: policy_input, gate,        │
  │  action_decisions, proof                │
  └────────────────────┬────────────────────┘
                       │
                       ▼
  Step 2: Follow QUICKSTART
  ┌─────────────────────────────────────────┐
  │  10 lines of code.                      │
  │  No framework. No package.              │
  │                                         │
  │  policy_input → gate() → log record     │
  └────────────────────┬────────────────────┘
                       │
                       ▼
  Step 3: Run validate_non_interference.py
  ┌─────────────────────────────────────────┐
  │  python validate_non_interference.py \  │
  │         decisions.jsonl                 │
  │                                         │
  │  → JNIS_COMPLIANT                       │
  │                                         │
  │  Your trace satisfies structural        │
  │  invariants.                            │
  └────────────────────┬────────────────────┘
                       │
                       ▼
  Step 4: Compare with reference implementation
  ┌─────────────────────────────────────────┐
  │  A reference implementation exists      │
  │  (early-stage, internal use).           │
  │                                         │
  │  It adds:                               │
  │  - system state collector               │
  │  - real-time Streamlit UI               │
  │  - deterministic replay verification    │
  │  - append-only trace with OTel mapping  │
  │                                         │
  │  (private repository)                   │
  └────────────────────┬────────────────────┘
                       │
                       ▼
  Step 5: Request access for advanced use
  ┌─────────────────────────────────────────┐
  │  If you need the full implementation:   │
  │                                         │
  │  Contact via GitHub:                    │
  │  → github.com/Nick-heo-eg               │
  │                                         │
  │  Reference implementation available     │
  │  upon request.                          │
  └─────────────────────────────────────────┘
```

---

## What each step adds

| Step | What you gain |
|---|---|
| README | Conceptual model — understand the separation |
| QUICKSTART | Working gate — implement J-NIS in your own codebase |
| validate | Verification — machine-checkable trace invariants |
| Reference | Completeness — fuller implementation with replay and UI |
| Request | Access — full reference with OTel trace |

The loop is designed so that each step is useful independently of the reference implementation. By step 3, your system produces a J-NIS-compliant trace without the reference code.
