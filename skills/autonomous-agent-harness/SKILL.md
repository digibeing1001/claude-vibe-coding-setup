---
name: autonomous-agent-harness
description: Design and operate portable autonomous coding-agent harnesses across Claude Code, Codex, Hermes, OpenClaw, Cursor, OpenCode, and similar hosts. Use when building scheduled agents, long-running Vibe Coding loops, task queues, memory-backed workflows, multi-agent orchestration, computer/browser automation, or production-grade agent evaluation and recovery systems.
origin: ECC
---

# Autonomous Agent Harness

Use this skill to turn a coding assistant into a controlled engineering
harness. The harness must be portable, scoped, observable, and easy to stop.

## First Principles

1. **Consent first.** Autonomous operation, schedules, external posts, computer
   control, and memory writes require explicit user approval for the current
   target.
2. **Small action space.** Prefer a few reliable actions with clear outputs over
   many overlapping tools.
3. **Progressive disclosure.** Keep host rules short. Load skills, references,
   logs, and code only when they are needed.
4. **Evidence before claims.** Fresh verification output beats confidence.
5. **Stop on repeated failure.** Re-plan after the same failure repeats twice.
6. **No prompt bloat as a quality strategy.** Add deterministic scripts, tests,
   and checklists before adding more prose.

## Host Capability Detection

Before enabling the harness, create a capability table:

| Capability | Detect | Fallback |
| --- | --- | --- |
| Skills | host skills directory exists | install missing skills with preserve mode |
| Shell | run a harmless version command | provide manual command |
| Git | `git status --short` | read-only review mode |
| Browser/UI QA | Browser plugin or Playwright available | screenshot/manual checklist |
| Multi-agent | host agent tools available | sequential loop |
| Memory | explicit memory tool or files | local state file |
| Scheduling | automation/cron tool available | manual queue |
| GitHub | connector or `gh auth status` | local patch only |

Never assume Claude-only tool names on Codex, Hermes, or OpenClaw. Translate
through the host adapter.

## Portable Directory Contract

Use these paths when the host has no stronger convention:

```text
.agent/
  queue.md              # user-approved pending work
  state.md              # current loop state
  evidence/             # command outputs, screenshots, reports
  decisions.md          # stable decisions only
  logs/                 # append-only run logs
```

For Codex projectless work, use the workspace `work/` folder for temporary
state and `outputs/` only for user-facing deliverables.

## Task Queue Contract

Each queued task must have:

```markdown
## <task id>
Status: pending|running|blocked|done
Owner: host or agent name
Scope: files, repo, or system boundary
Acceptance:
- measurable criterion
Budget: max iterations/time/failures
Allowed side effects: local files|git branch|PR|external post|schedule
Evidence:
- command or observation required before done
```

Tasks without acceptance criteria stay in `pending` until clarified.

## Loop Contract

Every autonomous loop must declare:

- trigger: manual, schedule, webhook, CI, file watch
- scope: repo/path/account boundaries
- allowed tools and side effects
- budget: iterations, time, failure repeats, token/cost if available
- verification: command or observation required
- recovery: what happens on failure
- stop condition: when it halts and reports

If any field is unknown, run a dry-run plan instead of enabling automation.

## Quality Harness

Use a tiered gate instead of a single giant checklist:

| Tier | Use For | Required Gates |
| --- | --- | --- |
| quick | tiny edits | diff review + scoped verification |
| standard | normal feature | tests + lint/type/build when available + review |
| high-risk | auth, data, payment, infra, migration | standard + security + rollback plan |
| UI | frontend/user-facing | standard + browser/screenshot + accessibility |
| release | PR/deploy | standard/high-risk gates + CI + post-ship monitoring |

## Observation Format

All deterministic tools and scripts should return:

```json
{
  "status": "success|warning|error",
  "summary": "one line",
  "artifacts": ["paths or URLs"],
  "next_actions": ["specific follow-up"],
  "stop_reason": "optional stop condition"
}
```

This makes recovery cheaper than re-reading logs.

## Memory Rules

- Write memory only when the user explicitly asks or a configured workflow has
  explicit permission.
- Store durable preferences, decisions, and reusable patterns, not transient
  logs.
- Mark imported ad-hoc notes or external research as such.
- Keep memory short enough to load without crowding task context.

## GitHub And Release Rules

For publish workflows:

1. Verify clean baseline or document existing failures.
2. Use an isolated branch/worktree when possible.
3. Commit focused changes.
4. Push and verify the remote branch/commit exists.
5. Create or update PR when requested.
6. Do not claim upload success until remote state is confirmed.

## Missing Pieces To Watch For

These gaps usually prevent production-grade Vibe Coding:

- no standard skill validation before install
- broken gitlinks or missing `SKILL.md`
- install scripts that silently overwrite personal host rules
- no host adapter for Codex/Hermes/OpenClaw
- no loop budgets or stop conditions
- no de-sloppify/review pass after implementation
- no fresh verification evidence before completion
- no state file for long loops
- no security path for secrets, auth, payments, migrations, or external writes

## Setup Checklist

1. Run `scripts/validate_setup.py`.
2. Install into the target host with `scripts/install-universal.py --mode preserve`.
3. Confirm the host can discover `vibe-coding` and `codex-vibe-coding` when
   applicable.
4. Run a dry-run task with no external side effects.
5. Run one small real task and capture evidence.
6. Review token overhead and remove duplicated skills where local versions are
   better.
