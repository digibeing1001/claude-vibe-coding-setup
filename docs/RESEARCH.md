# Research Notes: Portable Vibe Coding Harness

Generated: 2026-06-14

## Applied Findings

The repository now treats Vibe Coding as a host-portable harness rather than a
single prompt bundle. Research was converted into scripts, gates, and routing
rules.

## Skill Ecosystem Signals

| Source | Finding | Repository change |
| --- | --- | --- |
| [openclaw/clawhub](https://github.com/openclaw/clawhub) | OpenClaw has a public skill and plugin registry with `clawhub search`, inspect/install/pin flows, stars, comments, moderation, and vector search. | Added a findskill-compatible discovery chain and ClawHub candidate source. |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | The Skills CLI supports Codex, Claude Code, OpenClaw, and many other agents, and exposes `npx skills find`, `add --list`, `use`, and install targeting. | Added `scripts/find_skill_candidates.py` support for `npx skills find` and cross-agent discovery. |
| [anthropics/skills](https://github.com/anthropics/skills) | Canonical public Agent Skills examples and packaging references. | Kept as a reference source instead of bulk vendoring. |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Curated ecosystem index for skills, hooks, commands, MCP servers, and workflows. | Added to the candidate registry for gap-driven searches. |
| [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | Broad toolkit packaging across agents, skills, commands, hooks, and MCP configs. | Added as a discovery source, not a default bulk install. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production-engineering oriented skill examples. | Added as a review/testing/frontend candidate source. |
| [BehiSecc/VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill) | Security-oriented vibe coding candidate. | Added as a security gap candidate; import requires review. |
| [kenryu42/cc-safety-net](https://github.com/kenryu42/cc-safety-net) | Hook-based command safety pattern. | Added as a git/command safety candidate. |

## Papers And Best Practices

| Source | Finding | Repository change |
| --- | --- | --- |
| [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Skills should stay concise, use progressive disclosure, validate with realistic tasks, and rely on scripts for deterministic work. | Shortened main entry skills and added dependency-free validators/scorers. |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Project memory should be concise; hooks and skills should carry deterministic workflows; completion needs evidence. | Rewrote `CLAUDE.md` around runtime boundaries and evidence gates. |
| [SWE-agent](https://arxiv.org/abs/2405.15793) | Agent-computer interface design affects software engineering performance. | Added host adapter rules and a compact action/evidence interface. |
| [Agentless](https://arxiv.org/abs/2407.01489) | Localization, repair, and patch validation can solve many bugs without complex orchestration. | Made localize -> repair -> validate the default bug loop. |
| [OpenHands](https://arxiv.org/abs/2407.16741) | General coding agents need sandbox awareness, interaction tools, state, recovery, and evaluation hooks. | Added portable harness contracts and runtime scoring. |

## Implemented Mechanisms

- `scripts/install-universal.py`: host-aware install with preserve mode and
  targeted `--only` overwrites.
- `scripts/validate_setup.py`: strict skill bundle validation.
- `scripts/score_vibe_run.py`: runtime score for containment, evidence,
  capability coverage, maintainability, and instruction-surface changes.
- `scripts/find_skill_candidates.py`: live discovery through local registry,
  GitHub high-star search, `npx skills find`, `npx clawhub search`, and
  standalone `findskill` when available.
- `skills/vibe-run-review`: completion gate plus missing-capability intake.
- `skills/vibe-coding`: Phase 0 capability sensor that triggers discovery
  during the run rather than waiting for a separate user command.

## Guardrail Decision

External skills are treated as code supply-chain inputs. The harness discovers
and proposes them automatically when a gap appears, but it does not import,
install, or overwrite them without explicit user approval and post-import
validation.
