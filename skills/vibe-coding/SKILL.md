---
name: vibe-coding
description: Unified portable Vibe Coding orchestrator. Use for build, design, prototype, implementation, debugging, review, and shipping requests across Codex, Claude Code, Hermes, OpenClaw, and similar hosts. Routes all iterative work through Loop Engineering.
---

# Vibe Coding Orchestrator

This skill routes a coding request through the smallest workflow that can
produce evidence. All iterative work runs as Loop Engineering — the
three-layer nested feedback architecture governs how work flows from AI
coding loops (L1) through developer feedback (L2) to external user feedback
(L3).

## Phase 0: Vibe Check

Before implementation, determine:

1. What is being built or fixed?
2. Is this a bug, feature, UI task, refactor, release, or research task?
3. Is the target a new project or an existing codebase?
4. Is this a single-pass task or an iterative loop? If iterative, which loop
   pattern fits?
5. Which capabilities are required: testing, review, security, browser QA,
   accessibility, deployment, design, git safety, or agent harness?
6. Which local skills cover those capabilities?

If a required capability is missing, trigger the capability sensor:

```bash
python scripts/find_skill_candidates.py --capability <capability> --include-cli --markdown
```

If the repository scripts are unavailable, use the installed host copy such as
`~/.codex/vibe-coding/scripts/find_skill_candidates.py`.

Present the best candidates and wait for user approval before import.

## Loop Engineering Entry

For any task that needs more than one pass (bug fix requiring iteration,
feature work, refactor, scheduled task, autonomous loop), load the
`loop-engineering` skill and route through the loop controller:

| Situation | Loop Pattern | Default Readiness |
| --- | --- | --- |
| Tiny edit | fast path: edit -> scoped verification -> review | L1 |
| Bug/regression | localize-repair-validate | L1 |
| Focused feature | sequential-quality-loop | L1 |
| UI work | design pass -> implementation -> browser/a11y verification | L1 |
| Broad spec | rfc-dag-loop | L2 |
| Multiple creative directions | parallel-generation-loop | L2 |
| Release/PR | continuous-pr-loop | L2 |
| Daily scan & report | daily-triage | L1 |
| CI failure auto-fix | ci-sweeper | L2 |
| Issue classification | issue-triage | L1 |
| Post-merge cleanup | post-merge-cleanup | L1 |

For any loop >1 iteration, the `loop-controller` skill enforces the
four-node cycle (Context -> Decide -> Act -> Evaluate) and the 8 state
transitions. The `loop-state` skill maintains STATE.md. The `loop-budget`
skill enforces budget and kill switch. The `maker-checker` skill enforces
Maker/Checker physical separation. The `loop-constraints` skill enforces
safety guardrails at every Context node.

## Workflow Selection

For single-pass tasks (tiny edits, quick lookups), skip the loop
controller and use the fast path:

| Situation | Workflow |
| --- | --- |
| Tiny edit | fast path: edit -> scoped verification -> review |
| Quick lookup | read -> answer |

Escalate to multi-agent or long-running loops only when the task needs it.
Any loop >1 iteration must run through the controller.

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
