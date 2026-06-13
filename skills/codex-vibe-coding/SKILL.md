---
name: codex-vibe-coding
description: Codex-specific entrypoint for this portable Vibe Coding setup. Use when the user asks Codex to build, implement, design, refactor, debug, review, or ship code with Vibe Coding, especially when token savings and production quality are both required.
---

# Codex Vibe Coding

Use this as the Codex host adapter for `vibe-coding`.

## Priorities

1. Save tokens by using progressive disclosure, focused file reads, codegraph or
   indexed search when available, and existing local skills before bundled
   duplicates.
2. Protect quality with tests, browser verification, review, and fresh evidence
   before completion claims.
3. Avoid unmaintainable code. Prefer small cohesive changes, existing patterns,
   and de-sloppify passes over broad rewrites.

## Codex Tool Mapping

| Need | Codex behavior |
| --- | --- |
| Task tracking | Use `update_plan` for multi-step work |
| Code search | Prefer codegraph if available; otherwise use `rg` |
| Parallel file reads | Use parallel tool calls where safe |
| Browser QA | Use the Browser plugin or Playwright after frontend changes |
| GitHub publish | Use local `git`/`gh` or the GitHub app, then verify remote state |
| Memory update | Only write memory when the user explicitly asks |

## Workflow

1. Trigger `vibe-coding` for build/design/implementation requests.
2. Load only the task-relevant supporting skills.
3. For bugs, use `continuous-agent-loop` localize-repair-validate before
   escalating to heavy orchestration.
4. For feature work, use `tdd-workflow`, `coding-standards`, and
   `verification-loop`.
5. For UI work, use `vibe-design-workflow` and browser verification.
6. For completion, use `verification-before-completion`: evidence before
   claims.

## Installation Expectations

Install with:

```bash
python scripts/install-universal.py --host codex --mode preserve
```

`preserve` is the default because the user's local Codex skills may contain
newer or personal rules. Use `--mode overwrite` only after reviewing backups.
