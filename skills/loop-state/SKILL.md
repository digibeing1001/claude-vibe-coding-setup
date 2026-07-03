---
name: loop-state
description: Loop state spine management. Manages STATE.md (read at run start, write at run end, prune resolved items), loop-run-log.md (append-only run history), and versioned context handoff packages with hash verification. Use for any loop that needs cross-run memory, multi-agent handoff, or checkpoint recovery.
---

# Loop State

State management is the memory system for loops. Without persistent state, every run starts from scratch and loses goals/evidence across agent handoffs. This skill makes "don't lose goals/evidence/decisions on handoff" a verifiable protocol, not chat-memory-dependent.

## When to Use

- Any loop running more than one iteration
- Any multi-agent handoff
- Any loop that needs to resume from checkpoint
- Any loop that needs to track progress across runs

## STATE.md — Loop Memory Spine

STATE.md is the persistent spine outside the loop. Read at run start, write at run end, prune resolved items every run. It is the most important artifact a loop produces — it answers "what are we doing now / what did we try last / who are we waiting on".

### Template

```markdown
# Loop State

Last run: <ISO timestamp>
Run ID: <uuid>
Pattern: <pattern name>
Readiness: <L1|L2|L3>

## Goal
<mechanically verifiable goal for this loop>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>

## High Priority (waiting on human)
- <item> — waiting since <time> — <reason>

## Watch List
- <item> — last action <action> — <status>

## Recent Noise (pruned next run)
- <item> — <why noise>

## Current Evidence
<command output / observations / test results from this round>

## Decisions
- <decision> — <reason> — <time>

## Failed Attempts
- <attempt> — <root cause hypothesis> — <retryable?>

## Next Smallest Step
<one smallest next step>

## Post-Run Critique
- High noise items: <items>
- False positives: <items>
- Should downgrade: <items>
- One improvement for next run: <improvement>
```

### State File Rules

1. **Read at run start** — load historical decisions and failed attempts, avoid repeat trial-and-error
2. **Write at run end** — record what happened this round
3. **Prune every run** — resolved/merged items move to Recent Noise, deleted next run
4. **Not a diary** — only facts needed to resume the loop
5. **`acting_on` field** — for multi-loop, records current branch/PR ID for collision detection

## loop-run-log.md — Append-Only Run History

Shared run history across all loops. Append one entry per run:

```markdown
## Run <run_id>
- Time: <start-end>
- Pattern: <pattern>
- Duration: <duration>
- Items found: <count>
- Actions taken: <count>
- Escalations: <count>
- Tokens estimate: <count>
- Outcome: <complete|fail|cancel|budget_exhausted>
- Notes: <one sentence>
```

This file is for cross-run trend analysis (noise, false positive rate, token burn rate), not for replaying history.

## Versioned Context Handoff

Multi-agent handoffs must use versioned handoff packages, not chat memory.

### Handoff Schema

```json
{
  "context_id": "<stable across same intent chain>",
  "task_id": "<single task>",
  "handoff_id": "<single handoff, dedup>",
  "context_version": <incrementing integer>,
  "context_hash": "<SHA-256 of context content>",
  "from_agent": "<agent id>",
  "to_agent": "<agent id>",
  "goal": "<goal>",
  "acceptance_criteria": ["<criteria>"],
  "decisions": [{"decision": "<decision>", "reason": "<reason>", "timestamp": "<time>"}],
  "evidence": [{"claim": "<claim>", "evidence": "<evidence>", "fresh": true}],
  "failed_attempts": [{"attempt": "<attempt>", "root_cause_hypothesis": "<hypothesis>"}],
  "next_step": "<next step>",
  "references": [{"path": "<file>", "hash": "<file hash>", "reason": "<why referenced>"}],
  "unknowns": ["<what's unknown>"],
  "budget_used": {"iterations": <n>, "tokens": <n>, "cost_microunits": <n>}
}
```

### Three ID Types

| ID | Purpose | Lifecycle |
| --- | --- | --- |
| `context_id` | Stable across same intent chain | Task lifetime |
| `task_id` | Single task | Single task |
| `handoff_id` | Single handoff, dedup | Single handoff |

### Receiver Confirmation Protocol

Receiver must explicitly confirm; unconfirmed is not complete:

- `accept` — receive and continue
- `request_context` — context insufficient, request more
- `reject` — context has problems, refuse

### Forbidden Content

- Private chain of thought
- Passwords, keys, tokens
- Other tenant data
- "Summary of summary" (large files referenced by path + hash, not re-summarized)

## Large File Reference Passing

Never inline large files into handoff packages:

1. Large files stored once, referenced by path + hash + reason
2. Receiver reads on demand, no preloading
3. References must include hash; receiver verifies file unchanged
4. No "summary of summary" — always reference original

## Checkpoints and Recovery

### Checkpoints

Each run maintains a checkpoint directory:

```
.agent/runs/<run_id>/checkpoints/
├── cp-001.json
├── cp-002.json
└── current.json
```

Checkpoint content: current node, decisions, budget used, artifact pointers, context hash.

### Recovery Protocol

1. Load only confirmed context delta + current decision + raw references
2. **Do not replay full chat history**
3. Side effects must be idempotent / dedupable / explicitly confirmed
4. No full re-runs; redo only the minimum redoable unit
5. First round after recovery must run Context node to verify state

## Terminal Immutability

Terminal tasks (complete/fail/cancel/budget_exhausted) are immutable. Future improvements create a new run, reuse the same `context_id`, but generate a new `task_id` and `run_id`.

This rule ensures history is auditable — past failures cannot be silently modified; improvements are explicit new actions.

## Multi-Loop State Layout

```
.agent/
├── state/
│   ├── STATE.md                    # main state file
│   ├── loop-run-log.md             # shared run history
│   ├── daily-triage.state.md       # per-pattern state
│   ├── ci-sweeper.state.md
│   └── ...
├── runs/
│   └── <run_id>/
│       ├── run.json
│       ├── ledger.jsonl
│       └── checkpoints/
```

## CLI

```bash
# Read current state
python scripts/loop_state.py read

# Write state (after run)
python scripts/loop_state.py write --pattern <pattern> --outcome <outcome>

# Prune resolved items
python scripts/loop_state.py prune

# Create checkpoint
python scripts/loop_state.py checkpoint --run-id <run_id>

# Recover from checkpoint
python scripts/loop_state.py recover --run-id <run_id>
```

Full spec: [`loops/state-management.md`](../../loops/state-management.md)
