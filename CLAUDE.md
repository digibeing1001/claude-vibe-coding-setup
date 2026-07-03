# VibeCoding Setup Rules

This file is advisory project memory. Deterministic checks live in scripts,
hooks, tests, and the loop controller.

## Host Rules

- Support Claude Code, Codex, Hermes, OpenClaw, and similar hosts.
- In Codex, route through `codex-vibe-coding`, then `vibe-coding`.
- Translate tool names through the current host adapter before acting.
- Install with `scripts/install-universal.py --mode preserve` by default.
- Use `--mode overwrite --only <skill>` for deliberate targeted updates.

## Loop Engineering

All iterative work runs as Loop Engineering, not as one-shot prompts. The
three-layer nested feedback architecture governs how work flows:

| Layer | Name | Time Scale | Driver |
| --- | --- | --- | --- |
| L1 | Agentic Coding Loop | minutes | AI Agent |
| L2 | Developer Feedback Loop | hours | Developer |
| L3 | External Feedback Loop | days/weeks | Real Users |

The bottleneck migrates outward. Faster L1 makes L2/L3 quality more
decisive. Optimizing only L1 produces "complete-looking" versions in the
wrong direction.

### Core Mechanisms (non-negotiable)

1. **Deterministic controller.** AI suggests next state; the controller
   decides and executes state transitions across 8 states
   (continue/replan/retry/wait_human/complete/fail/cancel/budget_exhausted).
   See `loops/controller.md` and the `loop-controller` skill.
2. **State spine.** Every loop maintains STATE.md — read at run start,
   write at run end, prune resolved items every run. See
   `loops/state-management.md` and the `loop-state` skill.
3. **Budget and kill switch.** Every loop declares a budget
   (max runs/tokens/sub-agents/retries/cost per day). Kill switch pauses all
   loops. See `loops/budget-management.md` and the `loop-budget` skill.
4. **Maker/Checker separation.** The executor cannot mark own work complete.
   The verifier is a physically separate entity using "find reasons to
   reject" instructions. See `loops/maker-checker.md` and the
   `maker-checker` skill.
5. **Safety guardrails.** Path Denylist, auto-merge policy, MCP minimal
   permissions, risk scoring. Enforced at every Context node. See
   `loops/safety-guardrails.md` and the `loop-constraints` skill.
6. **Readiness levels.** New loops start at L1 report-only for 1-2 weeks,
   then L2 assisted, then L3 unattended. See `loops/readiness-levels.md`.
7. **Failure mode coverage.** Every loop must cover the failure modes
   listed in `loops/failure-modes.md` for its target readiness level.
8. **Post-Run Critique.** Every run writes a critique (noise, false
   positives, one improvement) before completion. See
   `loops/self-correction.md`.
9. **Task loop vs system iteration.** Task rework may auto-loop within
   approved scope. Changes to skills/rules/workflows/souls require an
   iteration proposal and human approval. See `loops/self-correction.md`.

### Loop Selection

Pick the smallest loop that can produce evidence:

| Situation | Loop |
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

Full catalog: `loops/patterns/README.md`.

### Loop Audit Gate

Before running any new loop at L2 or L3:

```bash
python scripts/loop_audit.py --pattern <pattern> --suggest
```

L1 requires score >= 38, L2 >= 58, L3 >= 78.

### Loop State Gate

Before reporting loop work complete:

```bash
python scripts/loop_state.py write --pattern <pattern> --outcome complete
python scripts/loop_state.py append-log --pattern <pattern> --outcome complete --tokens <n>
```

## Runtime Controls

1. **Context boundary.** Load the smallest relevant set of files, diffs,
   logs, and skills for the current phase. Prefer indexed/code search when
   available.
2. **Change boundary.** Keep edits tied to the user request and the
   existing project pattern. Avoid unrelated formatting and speculative
   abstractions.
3. **Loop boundary.** Bugs start with localize -> repair -> validate.
   Escalate to long loops only after repeated localization failure or broad
   impact. Any loop >1 iteration must run through the controller.
4. **Evidence boundary.** Completion claims require fresh command output or
   direct observation from the current workspace.
5. **Review boundary.** Run a de-sloppify pass before final verification:
   remove dead code, duplicated logic, unnecessary layers, stale comments,
   and broad changes that no longer serve the task.
6. **Capability boundary.** When a needed capability is missing, search
   GitHub for suitable skills first. Present candidates, reasons,
   license/maintenance notes, and install impact to the user. Import only
   after approval.

## Score Gate

Before reporting work complete, run:

```bash
python scripts/score_vibe_run.py --markdown
```

If this repository is not present, use the installed host copy, for example:

```bash
python ~/.codex/vibe-coding/scripts/score_vibe_run.py --skills-dir ~/.codex/skills --markdown
```

For risky work, pass explicit capabilities:

```bash
python scripts/score_vibe_run.py --required testing,review,security,browser-qa --markdown
```

Interpretation:

| Score | Result | Action |
| --- | --- | --- |
| 85-100 | pass | Report evidence and remaining risk |
| 70-84 | review | Fix the weakest dimension or explain why it is acceptable |
| <70 | fail | Do not ship; reduce scope or add missing evidence/capability |

## Phase Routing

| Phase | Default skills |
| --- | --- |
| Host adapter | `codex-vibe-coding`, `autonomous-agent-harness` |
| Loop entry | `loop-engineering`, `loop-controller`, `loop-state` |
| Discovery | `codebase-onboarding`, `search-first`, `blueprint` |
| Requirements | `brainstorming`, `grill-me`, `grill-with-docs` |
| Design/UI | `vibe-design-workflow`, `design-review`, `ui-design-review` |
| Implementation | `tdd-workflow`, `coding-standards`, `executing-plans` |
| Debugging | `continuous-agent-loop`, `diagnose`, `debug-pro-1.0.0` |
| Verification | `verification-loop`, `maker-checker`, `browser-qa` |
| Review | `vibe-run-review`, `review`, `cso`, `security-review` |
| Ship | `gsd-ship`, `deployment-patterns`, `canary-watch` |

## Non-Negotiables

- Do not overwrite user-local skills without a deliberate overwrite command.
- Do not claim a GitHub upload until the remote commit is verified.
- Do not create a new skill for a runtime gap until external candidates have
  been checked and the user has approved the intended import.
- Do not use long-lived autonomous loops without scope, budget, verification,
  recovery, and stop conditions.
- Do not let AI self-claim completion — Maker/Checker must be physically
  separated.
- Do not skip the loop controller — AI suggests, controller decides state
  transitions.
- Do not start a new loop at L3 — always progress L1 -> L2 -> L3.
- Do not let a loop touch denylist paths — `loop-constraints` enforces this
  every run.
- Do not change system rules (skills/rules/workflows/souls) without an
  iteration proposal and human approval.
