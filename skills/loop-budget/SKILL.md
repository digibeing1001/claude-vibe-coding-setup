---
name: loop-budget
description: Loop budget management and kill switch. Enforces per-loop daily caps (max runs, max tokens, max sub-agent spawns, max retries, max cost), watchlist-empty early-exit optimization, and global kill switch (label/flag/env var). Use for any loop that must avoid token burn, infinite retries, or unbounded cost.
---

# Loop Budget

Budgets are the hard guardrails of Loop Engineering. Without budgets, loops burn tokens indefinitely for "completion feel" or retry the same error repeatedly. Budgets are not advice — they are hard constraints enforced by the controller.

## When to Use

- Any loop running autonomously or on a schedule
- Any loop that consumes tokens or cost
- Any loop that could get stuck retrying

## Budget Table Template

Every loop must declare its budget in `loop-budget.md` before starting:

```markdown
# Loop Budget

| Loop | Max runs/day | Max tokens/day | Max sub-agent spawns/run | Max retries/cause | Max cost (microunits)/day |
| --- | --- | --- | --- | --- | --- |
| daily-triage | 24 | 100,000 | 0 | 2 | 500,000 |
| ci-sweeper | 96 | 200,000 | 3 | 2 | 1,000,000 |
| pr-babysitter | 96 | 150,000 | 2 | 2 | 750,000 |
| continuous-pr-loop | 1 | 500,000 | 5 | 3 | 2,500,000 |
| sequential-quality-loop | 1 | 300,000 | 3 | 3 | 1,500,000 |
| localize-repair-validate | 1 | 100,000 | 0 | 2 | 500,000 |
```

### Budget Dimensions

| Dimension | Meaning | Default |
| --- | --- | --- |
| Max runs/day | Daily loop triggers | per pattern |
| Max tokens/day | Daily token consumption | per pattern |
| Max sub-agent spawns/run | Sub-agents per loop | 3 |
| Max retries/cause | Retries per root cause | 2 |
| Max cost (microunits)/day | Daily cost cap | per pattern |
| Max stagnant cycles | No-progress rounds | 3 |
| Max iterations | Max iterations per loop | 3 |

## Budget Exceeded Flow

When any dimension exceeds, the controller:

1. **Pause scheduler** — stop next trigger for this loop
2. **Append run log** — record overflow event in `loop-run-log.md`
3. **Open maintainer issue** — create human-visible ticket (which dimension, by how much)
4. **Transition to `budget_exhausted`** — current run terminates

Overflow is not failure — it's a normal cost-control signal. Humans decide whether to raise budget, fix root cause (why burning so fast), or stop the loop.

## Kill Switch — Pause All Loops

Global kill switch via a label or flag. All loops must check kill switch at Context node; hit → immediate `cancel`.

### Implementation Options

**Option 1: Git label (for repo-backed loops)**

```bash
git label loop-pause-all
git push origin loop-pause-all

# resume
git label -d loop-pause-all
git push origin :loop-pause-all
```

**Option 2: STATE.md flag (for local loops)**

```markdown
# Loop State

## Kill Switch
status: PAUSED  # change to ACTIVE to resume
reason: <reason>
paused_at: <time>
```

**Option 3: Env var (for CI)**

```bash
export LOOP_PAUSE_ALL=1  # any non-empty value pauses
```

### Kill Switch Rules

- All loops check kill switch at Context node first thing
- Hit → immediate `cancel`, no Act runs
- Kill switch can only be cleared by humans; AI cannot self-clear
- After clearing, next loop run resumes — not immediate

## Watchlist-Empty Early Exit

The most important cost optimization: **watchlist empty → early exit <5k tokens**.

```text
Daily Triage cycle:
1. Schedule trigger
2. Triage skill ingest (CI failures / issues / commits / old state)
3. High-priority items enter state
4. IF state says "no actionable items":
5.   Early exit, this run <5k tokens, no sub-agent spawned
6. ELSE:
7.   Spawn sub-agent to handle high-priority items
```

Only spawn sub-agents when state says actionable. Burning tokens on empty watchlist is the biggest waste.

## Cost Estimation

Estimate token cost before scheduling; don't start runs that exceed budget.

### Estimation Formula

```
estimated_tokens = base_tokens(pattern) + items_count * per_item_tokens
estimated_cost = estimated_tokens * model_rate
```

### Baseline Tokens

| Pattern | Base tokens | Per-item tokens |
| --- | --- | --- |
| daily-triage | 2,000 | 3,000 |
| ci-sweeper | 1,500 | 5,000 |
| pr-babysitter | 1,000 | 4,000 |
| issue-triage | 1,500 | 2,000 |
| post-merge-cleanup | 1,000 | 2,000 |
| localize-repair-validate | 3,000 | 0 |
| sequential-quality-loop | 5,000 | 0 |

### Estimate Command

```bash
python scripts/loop_audit.py --estimate-cost --pattern daily-triage --items 5
```

## Budget Persistence

Every run must persist usage; the controller uses this to check overflow:

```json
{
  "run_id": "<uuid>",
  "loop_pattern": "daily-triage",
  "date": "2026-07-03",
  "runs_today": 3,
  "tokens_used_today": 45000,
  "sub_agent_spawns_this_run": 2,
  "retries_this_cause": 1,
  "cost_microunits_today": 225000,
  "stagnant_cycles": 0,
  "iterations_this_run": 1
}
```

## Controller Contract

Controller checks budget before every state transition:

```text
IF any budget dimension exceeded:
    transition to budget_exhausted
    pause scheduler
    append run log
    open maintainer issue
ELSE IF kill_switch active:
    transition to cancel
ELSE:
    proceed with AI's suggested transition
```

AI cannot bypass budget checks — budgets are the controller's hard guardrail, not AI's suggestion.

Full spec: [`loops/budget-management.md`](../../loops/budget-management.md)
