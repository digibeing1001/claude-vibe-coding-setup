---
name: loop-triage
description: Scheduled triage loop patterns (daily-triage, ci-sweeper, issue-triage, post-merge-cleanup). Watchlist-empty early-exit, collision detection via acting_on field, shared human inbox with dedup, and Post-Run Critique. Use for any loop that runs on a schedule (cron/webhook) rather than on-demand.
---

# Loop Triage

Scheduled triage loops scan CI failures, issues, commits, and state on a cadence. They prioritize low-cost observation over action: **watchlist empty → early exit <5k tokens**.

## When to Use

- Daily or periodic triage
- CI failure auto-fix
- Issue classification
- Post-merge cleanup
- Any loop triggered by cron or webhook (not on-demand)

## Patterns

| Pattern | Cadence | Risk | Default Readiness | What it does |
| --- | --- | --- | --- | --- |
| daily-triage | 1d | Low | L1 report | Scan + report, no action |
| ci-sweeper | 5-15m | Medium | L2 assisted | Scan + small fixes + verify |
| issue-triage | 2h-1d | Low | L1 propose | Scan + classify + propose |
| post-merge-cleanup | 1d-6h | Low | L1 | Clean dead code, docs, archive |

Full details: [`loops/patterns/`](../../loops/patterns/)

## Common Cycle

All triage loops share the same cycle:

```
1. Schedule trigger (cron/webhook)
2. Triage skill ingest (CI failures / issues / commits / old state)
3. Classify (high-priority / watch / noise)
4. IF state says "no actionable items":
5.   Early exit, this run <5k tokens, no sub-agent spawned
6. ELSE:
7.   (L2+) Spawn sub-agent for small fixes
8.   (L2+) Run Maker/Checker
9.   (L2+) Create PR (no auto-merge)
10. Update STATE.md
11. Prune resolved/merged items
12. Write Post-Run Critique
```

## Watchlist-Empty Early Exit

The most important cost optimization:

```text
IF watchlist is empty:
    early exit
    consume <5k tokens
    do NOT spawn any sub-agent
    log "empty watchlist, early exit"
    transition to complete
ELSE:
    proceed with action
```

Burning tokens on empty watchlist is the biggest waste. Only spawn sub-agents when state says actionable.

## Collision Detection

Multiple action loops may operate on the same branch/PR. Detect collisions before acting.

### acting_on field

Each action loop writes `acting_on` to STATE.md:

```markdown
## Current Action
acting_on: branch/fix-ci-failure-123
acting_since: 2026-07-03T14:30:00+08:00
```

### Pre-spawn check

Before spawning a sub-agent, any action loop must:

1. Read all other loops' STATE.md
2. Extract their `acting_on` fields
3. If target branch/PR conflicts with any active loop:
   - skip this round
   - log "collision with <other_loop> on <branch>"
   - try next cycle

## Shared Human Inbox

All loops' escalations enter a shared inbox to avoid notification flooding:

```markdown
## High Priority (waiting on human)
- [ci-sweeper] branch/fix-ci-failure-123 — waiting since 14:30 — CI failure root cause unknown
- [pr-babysitter] PR #456 — waiting since 15:00 — merge conflict needs human
- [dependency-sweeper] CVE-2026-1234 — waiting since 16:00 — major version bump needed
```

### Notification Dedup

Multiple loops escalating the same branch/PR/issue merge into one notification:

```text
[Loop Escalation] branch/fix-ci-failure-123
- ci-sweeper: CI failure root cause unknown
- pr-babysitter: same PR merge conflict
Action needed: <link>
```

### >24h Alert

Any High Priority item waiting >24h triggers an alert:

```text
[Loop Overdue] <item> has been waiting for <hours>h
Loop: <pattern>
Branch/PR: <acting_on>
Reason: <reason>
```

## Post-Run Critique

Every run writes a critique before completion:

```markdown
## Post-Run Critique
- High noise items: <items that were noise, filter next run>
- False positives: <items flagged high-priority but were actually fine>
- Should downgrade: <items that should be lower priority>
- One improvement for next run: <one sentence, one thing to improve>
```

### Rules

1. **Every run must write** — not optional, mandatory output of Evaluate node
2. **Only actionable** — not "be careful next time" but "change X threshold from N to M"
3. **Honest** — admit false positives and noise, don't cover up
4. **One improvement** — commit to one thing per run, don't overreach

## L1 → L2 → L3 Progression

New triage loops always start at L1 report-only:

### L1 (report-only)
- Scan and classify
- Write to STATE.md
- Generate report
- No code changes, no PRs, no auto-merge

### L2 (assisted)
- L1 everything
- Spawn sub-agents for small fixes (typo, lint, import order, obvious bugs)
- Run Maker/Checker
- Create PRs (no auto-merge)

### L3 (unattended)
- L2 everything
- Auto-merge (allowlist non-behavior changes only)
- Scheduled deploy (staging only)

Upgrade conditions: [`loops/readiness-levels.md`](../../loops/readiness-levels.md)

## Budget per Pattern

| Pattern | Max runs/day | Max tokens/day | Max sub-agent spawns/run |
| --- | --- | --- | --- |
| daily-triage | 1-12 | 100,000 | 0 (L1) / 3 (L2) |
| ci-sweeper | 96 | 200,000 | 3 |
| issue-triage | 1-12 | 50,000 | 0 (L1) / 2 (L2) |
| post-merge-cleanup | 1-4 | 100,000 | 2 |

## State Layout

```
.agent/
├── state/
│   ├── STATE.md                    # main state (shared High Priority)
│   ├── loop-run-log.md             # shared run history
│   ├── daily-triage.state.md
│   ├── ci-sweeper.state.md
│   ├── issue-triage.state.md
│   └── post-merge-cleanup.state.md
```

Full specs: [`loops/patterns/`](../../loops/patterns/) and [`loops/multi-loop-coordination.md`](../../loops/multi-loop-coordination.md)
