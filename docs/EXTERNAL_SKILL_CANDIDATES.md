# External Skill Candidates

Generated: 2026-06-14

This registry is used when a Vibe Coding run discovers a missing capability.
External repositories are not vendored automatically. The agent must search
GitHub, compare candidates, explain the reason for adding one, and wait for user
approval before import.

## Intake Checklist

1. Is there already a local skill that covers the need?
2. Is the candidate maintained and licensed for reuse?
3. Is the candidate narrow enough to import without broad prompt bloat?
4. Does it work across Codex, Claude Code, Hermes, and OpenClaw, or can it be
   adapted cleanly?
5. Can it be validated by `scripts/validate_setup.py` after import?

## Current Candidate Sources

| Capability | Candidate | Why it is useful | Intake status |
| --- | --- | --- | --- |
| Findskill | [openclaw/clawhub](https://github.com/openclaw/clawhub) | OpenClaw public skill and plugin registry with search, inspect/install/pin flows, stars, comments, and moderation. | Use for live discovery during capability gaps; inspect before install. |
| Findskill | [vercel-labs/skills](https://github.com/vercel-labs/skills) | Cross-agent Skills CLI with `npx skills find`, list/use/add/update, and Codex/OpenClaw/Claude Code support. | Use for discovery and inspection; install only after approval. |
| Skill packaging | [anthropics/skills](https://github.com/anthropics/skills) | Public Agent Skills examples and packaging conventions. | Reference first; import only small validated patterns. |
| Discovery | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Curated index for skills, hooks, MCP servers, commands, and workflows. | Use as a search index during gaps. |
| Discovery | [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | Broad toolkit layout covering skills, agents, hooks, commands, and MCP configs. | Evaluate individual items only. |
| Review | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production-engineering skill examples for review, testing, frontend, and web quality. | Compare against local review skills before import. |
| Security | [BehiSecc/VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill) | Security-focused vibe coding candidate for secure implementation review. | Add only if local security skills are insufficient for the task. |
| Security | [trailofbits/skills](https://github.com/trailofbits/skills) | Security research and vulnerability detection skill source from Trail of Bits. | Strong candidate for audit workflows; import narrowly after license review. |
| Command safety | [kenryu42/cc-safety-net](https://github.com/kenryu42/cc-safety-net) | Safety hook pattern for dangerous commands. | Adapt per host hook format after approval. |
| Multi-host skills | [refly-ai/refly](https://github.com/refly-ai/refly) | Treats skills as reusable infrastructure across multiple agent hosts. | Reference for lifecycle and packaging patterns. |
| Spec/memory | [withkynam/vibecode-pro-max-kit](https://github.com/withkynam/vibecode-pro-max-kit) | Spec and memory oriented vibe coding kit. | Evaluate when planning/memory flow is insufficient. |
| Skill catalog | [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Large catalog for specialized skill discovery. | Use as catalog, not as bulk import. |

## Runtime Link

`scripts/score_vibe_run.py` reads `config/skill-candidates.json` and emits
candidate proposals when required capabilities are missing.

For live discovery:

```bash
python scripts/find_skill_candidates.py --capability security --include-cli --markdown
```
