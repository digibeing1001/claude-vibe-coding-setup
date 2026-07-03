---
name: loop-engineering
description: Loop Engineering 总入口。加载三层嵌套反馈架构（L1 AI 编码循环 / L2 开发者反馈 / L3 外部用户反馈）和核心机制（确定性控制器、状态脊柱、预算、Maker/Checker、安全护栏、就绪度、失败模式、多 loop 协调、自我修正）。Use for any iterative coding work, autonomous loops, scheduled tasks, or when designing a new loop.
---

# Loop Engineering

Use this skill as the entry point for all Loop Engineering work. It loads the three-layer nested feedback architecture and the core mechanisms that make loops safe, observable, and self-correcting.

## When to Use

- Any iterative coding work (bug fixes, features, refactors)
- Autonomous or scheduled loops
- Designing a new loop pattern
- Reviewing or auditing an existing loop
- Multi-agent coordination
- When a task needs scope, budget, verification, recovery, and stop conditions

## Three-Layer Architecture

Loop Engineering is three nested control systems at different time scales:

| Layer | Name | Time Scale | Driver |
| --- | --- | --- | --- |
| L1 | Agentic Coding Loop | minutes | AI Agent |
| L2 | Developer Feedback Loop | hours | Developer |
| L3 | External Feedback Loop | days/weeks | Real Users |

**Key insight**: The bottleneck migrates outward. Faster L1 makes L2/L3 quality more decisive. Optimizing only L1 produces "complete-looking" versions in the wrong direction.

Full design: [`loops/three-layer-architecture.md`](../../loops/three-layer-architecture.md)

## Core Mechanisms

Each mechanism has a strict contract. They are not advisory text — they are enforced by the controller and scripts.

| Mechanism | Skill | Doc |
| --- | --- | --- |
| Deterministic controller | `loop-controller` | [`loops/controller.md`](../../loops/controller.md) |
| State spine | `loop-state` | [`loops/state-management.md`](../../loops/state-management.md) |
| Budget & kill switch | `loop-budget` | [`loops/budget-management.md`](../../loops/budget-management.md) |
| Maker/Checker separation | `maker-checker` | [`loops/maker-checker.md`](../../loops/maker-checker.md) |
| Safety guardrails | `loop-constraints` | [`loops/safety-guardrails.md`](../../loops/safety-guardrails.md) |
| Readiness levels | (this skill) | [`loops/readiness-levels.md`](../../loops/readiness-levels.md) |
| Failure modes | (this skill) | [`loops/failure-modes.md`](../../loops/failure-modes.md) |
| Multi-loop coordination | (this skill) | [`loops/multi-loop-coordination.md`](../../loops/multi-loop-coordination.md) |
| Self-correction | (this skill) | [`loops/self-correction.md`](../../loops/self-correction.md) |

## Loop Patterns

Pick the smallest loop that can produce evidence:

| Situation | Pattern |
| --- | --- |
| Bug or failing test | localize-repair-validate |
| Single focused feature | sequential-quality-loop |
| Large spec, decomposable | rfc-dag-loop |
| Need creative variants | parallel-generation-loop |
| PR/CI automation | continuous-pr-loop |
| Daily scan & report | daily-triage |
| CI failure auto-fix | ci-sweeper |
| Issue classification | issue-triage |
| Post-merge cleanup | post-merge-cleanup |

Full catalog: [`loops/patterns/README.md`](../../loops/patterns/README.md)

## Operating Discipline

1. **L1 must have evolvable Evals** — not one-time tests; Evals enter the L2 loop
2. **L2 has a fixed review cadence** — daily or every-other-day deep review
3. **L3 starts low-cost collection early** — structured interview templates + automated telemetry
4. **New loops always start L1 report-only for 1-2 weeks**, then L2 assisted, then L3 unattended
5. **Start small** — pick a low-risk narrow scenario for the first week

## Non-Negotiables

- Do not run a loop without scope, budget, verification, recovery, and stop conditions
- Do not let AI self-claim completion — Maker/Checker must be physically separated
- Do not skip the controller — AI suggests, controller decides state transitions
- Do not start a new loop at L3 — always progress L1 → L2 → L3
- Do not let a loop touch denylist paths — `loop-constraints` enforces this every run
- Do not change system rules without an iteration proposal (task loop vs system iteration)

## Entry Flow

```text
1. Identify the task type (bug / feature / refactor / research / scheduled)
2. Pick the smallest loop pattern that can produce evidence
3. Determine readiness level (default L1 for new loops)
4. Load the controller, state, budget, constraints skills
5. Declare budget and stop conditions
6. Run the four-node cycle: Context → Decide → Act → Evaluate
7. Maker/Checker separation for any code change
8. Post-Run Critique before completion
9. Escalate to L2 review at fixed cadence
10. Escalate to L3 collection when ready
```

## Related Skills

- `continuous-agent-loop` — legacy L1 entry, now subsumed by this skill
- `vibe-coding` — main orchestrator, routes through this skill for iterative work
- `vibe-run-review` — L1 completion gate
- `verification-loop` — Checker responsibilities
- `using-git-worktrees` — worktree isolation for Maker/Checker
