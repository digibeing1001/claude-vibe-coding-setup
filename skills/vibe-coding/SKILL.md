---
name: vibe-coding
description: Unified portable Vibe Coding orchestrator. Use for build, design, prototype, implementation, debugging, review, and shipping requests across Codex, Claude Code, Hermes, OpenClaw, and similar hosts.
---

# Vibe Coding Orchestrator

This skill routes a coding request through the smallest workflow that can
produce evidence.

## Phase 0: Vibe Check

Before implementation, determine:

1. What is being built or fixed?
2. Is this a bug, feature, UI task, refactor, release, or research task?
3. Is the target a new project or an existing codebase?
4. Which capabilities are required: testing, review, security, browser QA,
   accessibility, deployment, design, git safety, or agent harness?
5. Which local skills cover those capabilities?

If a required capability is missing, trigger the capability sensor:

```bash
python scripts/find_skill_candidates.py --capability <capability> --include-cli --markdown
```

If the repository scripts are unavailable, use the installed host copy such as
`~/.codex/vibe-coding/scripts/find_skill_candidates.py`.

Present the best candidates and wait for user approval before import.

## Workflow Selection

| Situation | Loop |
| --- | --- |
| Tiny edit | fast path: edit -> scoped verification -> review |
| Bug/regression | localize -> repair -> validate |
| Focused feature | sequential quality loop |
| UI work | design pass -> implementation -> browser/a11y verification |
| Broad spec | dependency graph of small work units |
| Release/PR | verification -> review -> CI/publish evidence |

Escalate to multi-agent or long-running loops only when the task needs it.

## Phase Routing

| Phase | Default skills |
| --- | --- |
| Host adapter | `codex-vibe-coding`, `autonomous-agent-harness` |
| Discovery | `codebase-onboarding`, `search-first`, `blueprint` |
| Requirements | `brainstorming`, `grill-me`, `grill-with-docs` |
| Design/UI | `vibe-design-workflow`, `design-review`, `ui-design-review` |
| Implementation | `tdd-workflow`, `coding-standards`, `executing-plans` |
| Debugging | `continuous-agent-loop`, `diagnose`, `debug-pro-1.0.0` |
| Verification | `verification-loop`, `verification-before-completion`, `browser-qa` |
| Review | `vibe-run-review`, `review`, `cso`, `security-review` |
| Ship | `gsd-ship`, `deployment-patterns`, `canary-watch` |

## Implementation Rules

- Keep the working set bounded to the current phase.
- Prefer existing project patterns and helpers.
- Add tests near the behavior being changed.
- Run the closest verification command first, then broader checks as risk
  increases.
- After implementation, remove redundant logic, stale comments, dead code,
  speculative abstractions, and unrelated churn.
- Do not report completion without current evidence.

## Completion Gate

Run:

```bash
python scripts/score_vibe_run.py --live-skill-search --markdown
```

If the repository scripts are unavailable, use the installed host copy such as
`~/.codex/vibe-coding/scripts/score_vibe_run.py --skills-dir ~/.codex/skills`.

For risky work, pass required capabilities:

```bash
python scripts/score_vibe_run.py --required testing,review,security,browser-qa --live-skill-search --markdown
```

If the score is below 85, either fix the weakest dimension or explain the
accepted tradeoff. If the score is below 70, do not ship.
