---
name: loop-controller
description: Deterministic loop controller. AI suggests next state, controller decides and executes state transitions across 8 states (continue/replan/retry/wait_human/complete/fail/cancel/budget_exhausted). Enforces max_stagnant_cycles and max_retry_per_cause hard guards. Use for any loop that must avoid infinite self-reflection, state ambiguity, or AI self-claiming completion.
---

# Loop Controller

The controller is the hard spine of any loop: **AI suggests, controller decides**. The model can propose the next action, but only the deterministic controller can transition between the 8 states. This prevents infinite self-reflection, state ambiguity, and AI self-claiming completion.

## When to Use

- Any loop running more than one iteration
- Any loop where AI might get stuck or self-approve
- Any loop that needs auditable state transitions
- Any loop that must respect hard budgets

## Four-Node Cycle

Every loop runs the four-node cycle. Simple tasks may skip Decide, but Context/Act/Evaluate are mandatory.

```
Context → Decide → Act → Evaluate → (back to Context or terminal)
```

### Context

Load the minimum trusted context for the next step:
- Large files referenced by path + hash, not inlined
- `unknowns` declared explicitly
- Load STATE.md for historical decisions and failed attempts
- Verify context hash unchanged

### Decide

Form a structured decision, plan, risks, and next-action contract:
- Output: decision + route + risks + next action
- Skippable for simple tasks
- Decision must be mechanically verifiable by Evaluate

### Act

Invoke agents, skills, and tools; record observations and artifacts:
- Record: tool calls, budget consumed, artifacts produced
- Side effects must be idempotent / dedupable / explicitly confirmed
- Hit denylist or high-risk action → immediate pause

### Evaluate

Judge results by evidence, acceptance criteria, progress, and budget:
- Evidence first, deterministic checks primary, AI review secondary
- Compare against Evals/acceptance criteria, not "feels right"
- Progress: did this round actually advance the goal?
- Budget: is remaining budget enough for another round?

## 8 States

| State | Trigger | Controller Action |
| --- | --- | --- |
| `continue` | Evaluate passed, budget remains | Back to Context |
| `replan` | New info requires plan change | Back to Decide, drop old plan |
| `retry` | Failed but root cause known and retryable | Back to Act with new context (max 3) |
| `wait_human` | High-impact gap / goal drift / evidence conflict / high-risk irreversible | Pause, notify human |
| `complete` | Acceptance passed, artifacts accessible | Terminal, archive run |
| `fail` | Permanent failure or hard requirement unmet | Terminal, record root cause |
| `cancel` | User cancelled | Terminal, archive run |
| `budget_exhausted` | Budget depleted | Terminal, record consumption |

## Transition Rules

- AI may "suggest" any state, but only the controller "executes" the transition
- Terminals (complete/fail/cancel/budget_exhausted) are immutable; future improvements create a new run
- `retry` same root cause max 3 times; 4th forces `wait_human`
- `replan` does not reset budget, only the plan

## Hard Guards

Two hard guards enforced by the controller, AI cannot bypass:

### max_stagnant_cycles (progress stagnation limit)

Default 3. Consecutive N rounds where STATE.md's "Next Smallest Step" unchanged, or Evaluate reports "no progress" → auto-transition to `budget_exhausted` or `fail`.

### max_retry_per_cause (retry limit per root cause)

Default 3. Same root cause retried 3 times → 4th forces `wait_human`.

## Human Gates

Two types of human gates. AI may request, but only the control system can freeze/resume:

### Pre-Act Context Gate

- Intent restatement (AI rephrases the task in its own words)
- 3 first-principles questions (What is the irreducible core? Is acceptance mechanically verifiable? What are the failure modes?)
- Readiness threshold (context hash verified, unknowns declared, budget set)
- Hash confirmation (context unchanged → release)

### Mid-Act Precision Interrupt

Pause only on:
- High-impact gap (missing critical capability or permission)
- Goal drift (actual work deviates from spec)
- Evidence conflict (AI claims done but verification fails)
- High-risk irreversible action (production deploy, DB migration, deletion)

Intent change invalidates prior confirmation automatically.

## Recovery Protocol

When recovering from a checkpoint:

1. Load only confirmed context delta + current decision + raw references
2. **Do not replay full chat history**
3. Side effects must be idempotent / dedupable / explicitly confirmed
4. No full re-runs; redo only the minimum redoable unit
5. First round after recovery must run Context node to verify state

## AI Contract

AI must output every round:

```markdown
## Loop Status
Node: <context|decide|act|evaluate>
Suggested next state: <continue|replan|retry|wait_human|complete|fail|cancel|budget_exhausted>
Reason: <one sentence>
Evidence: <command output or observation>
Budget used: <used/limit>
Progress: <what this round advanced, or "no progress">
```

The controller uses this report + hard guard rules to decide the actual transition. AI's "suggested next state" is advisory; the controller may override.

## State Machine (machine-readable)

```json
{
  "states": ["context", "decide", "act", "evaluate"],
  "terminals": ["complete", "fail", "cancel", "budget_exhausted"],
  "transitions": {
    "context": ["decide", "act", "wait_human", "cancel"],
    "decide": ["act", "replan", "wait_human", "cancel"],
    "act": ["evaluate", "wait_human", "cancel", "budget_exhausted"],
    "evaluate": ["continue", "replan", "retry", "wait_human", "complete", "fail", "budget_exhausted"]
  },
  "hard_guards": {
    "max_stagnant_cycles": 3,
    "max_retry_per_cause": 3
  }
}
```

Full spec: [`loops/controller.md`](../../loops/controller.md)
