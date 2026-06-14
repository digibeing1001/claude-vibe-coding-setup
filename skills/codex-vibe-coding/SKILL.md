---
name: codex-vibe-coding
description: Codex-specific entrypoint for this portable Vibe Coding setup. Use when Codex builds, implements, designs, refactors, debugs, reviews, or ships code with the portable Vibe Coding harness.
---

# Codex Vibe Coding

Use this as the Codex host adapter for `vibe-coding`.

## Runtime Behavior

1. Map host tools before acting: `update_plan`, shell, Browser, GitHub, memory,
   codegraph, and local file access.
2. Load task-relevant files and skills only; prefer indexed search or `rg`
   before broad reads.
3. Reuse existing local skills when they are stronger or newer than bundled
   copies.
4. For bugs, run `continuous-agent-loop` with localize -> repair -> validate.
5. For features, keep a coherent implementation slice and run scoped
   verification before review.
6. Before completion, run `vibe-run-review` or:

```bash
python scripts/score_vibe_run.py --live-skill-search --markdown
```

If this repository is not present in the current workspace, use:

```bash
python ~/.codex/vibe-coding/scripts/score_vibe_run.py --skills-dir ~/.codex/skills --live-skill-search --markdown
```

## Capability Sensor

If the task needs a capability that is not covered by local skills:

1. Run live discovery:

```bash
python scripts/find_skill_candidates.py --capability <capability> --include-cli --markdown
```

Installed Codex fallback:

```bash
python ~/.codex/vibe-coding/scripts/find_skill_candidates.py --capability <capability> --include-cli --markdown
```

2. Use the output to propose GitHub/ClawHub/Skills CLI candidates.
3. Explain why the candidate should be added and what it would change.
4. Wait for user approval before importing, installing, or overwriting any
   external skill code.

## Codex Tool Mapping

| Need | Codex behavior |
| --- | --- |
| Task tracking | Use `update_plan` for multi-step work |
| Code search | Prefer codegraph if available; otherwise use `rg` |
| Parallel file reads | Use parallel tool calls where safe |
| Browser QA | Use the Browser plugin or Playwright after frontend changes |
| GitHub publish | Use local `git`/`gh` or the GitHub app, then verify remote state |
| Memory update | Only write memory when the user explicitly asks |

## Installation Expectations

Install with:

```bash
python scripts/install-universal.py --host codex --mode preserve
```

Use targeted overwrite for known updates:

```bash
python scripts/install-universal.py --host codex --mode overwrite --only codex-vibe-coding
```
