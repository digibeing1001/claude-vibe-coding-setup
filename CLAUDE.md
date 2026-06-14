# Portable Vibe Coding Rules

This file is advisory project memory. Deterministic checks live in scripts,
hooks, and tests.

## Host Rules

- Support Claude Code, Codex, Hermes, OpenClaw, and similar hosts.
- In Codex, route through `codex-vibe-coding`, then `vibe-coding`.
- Translate tool names through the current host adapter before acting.
- Install with `scripts/install-universal.py --mode preserve` by default.
- Use `--mode overwrite --only <skill>` for deliberate targeted updates.

## Runtime Controls

1. **Context boundary.** Load the smallest relevant set of files, diffs, logs,
   and skills for the current phase. Prefer indexed/code search when available.
2. **Change boundary.** Keep edits tied to the user request and the existing
   project pattern. Avoid unrelated formatting and speculative abstractions.
3. **Loop boundary.** Bugs start with localize -> repair -> validate. Escalate
   to long loops only after repeated localization failure or broad impact.
4. **Evidence boundary.** Completion claims require fresh command output or
   direct observation from the current workspace.
5. **Review boundary.** Run a de-sloppify pass before final verification:
   remove dead code, duplicated logic, unnecessary layers, stale comments, and
   broad changes that no longer serve the task.
6. **Capability boundary.** When a needed capability is missing, search GitHub
   for suitable skills first. Present candidates, reasons, license/maintenance
   notes, and install impact to the user. Import only after approval.

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
| Discovery | `codebase-onboarding`, `search-first`, `blueprint` |
| Requirements | `brainstorming`, `grill-me`, `grill-with-docs` |
| Design/UI | `vibe-design-workflow`, `design-review`, `ui-design-review` |
| Implementation | `tdd-workflow`, `coding-standards`, `executing-plans` |
| Debugging | `continuous-agent-loop`, `diagnose`, `debug-pro-1.0.0` |
| Verification | `verification-loop`, `verification-before-completion`, `browser-qa` |
| Review | `vibe-run-review`, `review`, `cso`, `security-review` |
| Ship | `gsd-ship`, `deployment-patterns`, `canary-watch` |

## Non-Negotiables

- Do not overwrite user-local skills without a deliberate overwrite command.
- Do not claim a GitHub upload until the remote commit is verified.
- Do not create a new skill for a runtime gap until external candidates have
  been checked and the user has approved the intended import.
- Do not use long-lived autonomous loops without scope, budget, verification,
  recovery, and stop conditions.
