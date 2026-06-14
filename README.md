# Portable Vibe Coding Setup

[中文](README.zh-CN.md) | English

This repository packages a portable coding-agent workflow for Claude Code,
Codex, Hermes, OpenClaw, and similar hosts.

The setup is intentionally built around mechanisms:

- host-aware installation with preserve-by-default behavior
- strict `SKILL.md` discovery validation
- scoped context loading through on-demand skills
- localize -> repair -> validate as the default bug loop
- runtime scoring before completion
- proactive findskill-compatible discovery when a capability gap appears

## Install

```bash
git clone https://github.com/digibeing1001/claude-vibe-coding-setup.git
cd claude-vibe-coding-setup
python scripts/validate_setup.py
python scripts/install-universal.py --host codex --mode preserve
```

Supported hosts:

| Host | Skill directory | Command |
| --- | --- | --- |
| Codex | `~/.codex/skills` | `python scripts/install-universal.py --host codex --mode preserve` |
| Claude Code | `~/.claude/skills` | `python scripts/install-universal.py --host claude --mode preserve --install-rules --install-hooks` |
| Hermes | `~/.hermes/skills` | `python scripts/install-universal.py --host hermes --mode preserve` |
| OpenClaw | `~/.openclaw/skills` | `python scripts/install-universal.py --host openclaw --mode preserve` |
| All | multiple | `python scripts/install-universal.py --host all --mode preserve` |

Use `--mode overwrite` only after reviewing what will be replaced. Backups are
created under the target host directory.

To update only selected skills:

```bash
python scripts/install-universal.py --host codex --mode overwrite --only codex-vibe-coding --only vibe-coding --only vibe-run-review
```

## Validate

```bash
python scripts/validate_setup.py
python scripts/score_vibe_run.py --required testing,review,agent-harness --live-skill-search --markdown
```

`validate_setup.py` checks packaging correctness:

- every bundled skill has a strict `SKILL.md`
- frontmatter includes `name` and `description`
- missing or broken gitlinks are reported
- non-standard skill paths are caught before install

`score_vibe_run.py` checks the current run:

- change containment
- verification evidence
- required capability coverage
- maintainability signals
- context-surface discipline
- external skill candidates for missing capabilities

`find_skill_candidates.py` is the live discovery layer:

```bash
python scripts/find_skill_candidates.py --capability security --include-cli --markdown
```

It can use the local registry, GitHub high-star search, `npx skills find`,
`npx clawhub search`, or a standalone `findskill` executable when available.
It never installs anything.

When installed globally, the same tools are copied to:

```text
~/<host>/vibe-coding/scripts/
~/<host>/vibe-coding/config/
```

For Codex, that means `~/.codex/vibe-coding/scripts`.

## Main Entry Points

| Skill | Use |
| --- | --- |
| `codex-vibe-coding` | Codex host adapter and tool mapping |
| `vibe-coding` | Main build/design/debug/review orchestrator |
| `continuous-agent-loop` | Controlled iterative loops with stop conditions |
| `autonomous-agent-harness` | Portable harness design across hosts |
| `vibe-run-review` | Runtime scoring and external skill gap workflow |

## Runtime Flow

1. Select the host adapter.
2. Read only the project files and skills needed for the current phase.
3. For bugs, start with localize -> repair -> validate.
4. For feature work, choose the smallest loop that can produce evidence.
5. Run scoped tests, lint/type/build/browser checks when available.
6. Run `vibe-run-review` or `scripts/score_vibe_run.py` before completion.
7. If a required capability is missing, search GitHub first, present candidates
   and reasons to the user, then install only after approval.

## External Skill Intake

Useful external skill repositories are tracked in
[`docs/EXTERNAL_SKILL_CANDIDATES.md`](docs/EXTERNAL_SKILL_CANDIDATES.md) and
`config/skill-candidates.json`.

The runtime policy is:

1. prefer an existing local skill when it covers the job
2. if a gap remains, search GitHub before writing a new skill
3. compare candidate license, maintenance, host fit, and overlap
4. ask the user before importing or installing external skill code
5. validate again after import

## Research Basis

The iteration is grounded in:

- Anthropic skill guidance: concise skills, progressive disclosure, realistic
  validation, deterministic scripts
- Claude Code guidance: hooks for non-negotiable automation and concise project
  memory
- Agentless: localization, repair, and patch validation as a simple default loop
- SWE-agent: agent-computer interface design matters for coding performance
- OpenHands-style harnesses: controlled state, sandbox awareness, evaluation,
  and recovery for long-running work

See [`docs/RESEARCH.md`](docs/RESEARCH.md) and
[`docs/COMPARISON.md`](docs/COMPARISON.md).
