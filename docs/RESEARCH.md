# Research Notes: Portable Vibe Coding Harness

Generated: 2026-06-14

## What Changed From Research

This repository now optimizes for a portable, low-token, high-quality coding
harness rather than a Claude-only prompt bundle.

## Skill And Ecosystem Signals

GitHub discovery showed the current ecosystem moving toward installable bundles
of skills, commands, hooks, MCP configs, and host adapters rather than one large
prompt file. Relevant examples:

| Source | Why It Matters |
| --- | --- |
| [anthropics/skills](https://github.com/anthropics/skills) | Public Agent Skills repository and canonical skill packaging reference. |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Curated index for skills, hooks, commands, orchestrators, and plugins. |
| [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | Demonstrates broad toolkit packaging with agents, skills, commands, hooks, rules, MCP configs. |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production engineering skill focus; useful as a future source to evaluate before copying patterns. |
| [kenryu42/cc-safety-net](https://github.com/kenryu42/cc-safety-net) | Cross-host safety hook pattern for dangerous commands. |
| [refly-ai/refly](https://github.com/refly-ai/refly) | Treats skills as infrastructure and targets multiple agent hosts. |
| [BehiSecc/VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill) | Security-specific vibe coding skill signal; should be evaluated before importing any rules. |

Decision: do not vendor large external bundles blindly. Record them as
recommended sources, then import only patterns that pass validation and avoid
duplicating stronger local skills.

## Papers And Best Practices

| Source | Finding | Repository Change |
| --- | --- | --- |
| [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Keep skills concise, use progressive disclosure, validate with realistic tasks, prefer scripts for deterministic operations. | Added `scripts/validate_setup.py`; tightened harness guidance around progressive disclosure and deterministic scripts. |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | Use concise `CLAUDE.md`, skills for on-demand workflows, hooks for deterministic actions, scoped exploration, and evidence before completion. | Added universal installer with preserve mode; reduced reliance on global rules; emphasized fresh verification. |
| [SWE-agent](https://arxiv.org/abs/2405.15793) | Agent-computer interface design affects software engineering agent performance. | Added host capability detection, action-space guidance, and standard observation format. |
| [Agentless](https://arxiv.org/abs/2407.01489) | Simple localization, repair, and patch validation can outperform complex agents at low cost on SWE-bench Lite. | Added localize-repair-validate as the default bug loop before heavy orchestration. |
| [OpenHands](https://arxiv.org/abs/2407.16741) | Generalist coding agents need command-line/browser interaction, sandboxing, multi-agent coordination, and evaluation hooks. | Added portable harness contract: sandbox/host detection, queue/state/evidence directories, budgets, and evaluation gates. |

## Practical Review Conclusions

The previous setup had useful content, but several issues blocked production use:

- Claude-only install flow; no Codex, Hermes, or OpenClaw target.
- Install scripts overwrote skills by default and did not preserve local rules.
- `vibe-coding` and `vibe-design-workflow` were lowercase `skill.md`, so strict
  skill discovery could miss the main entrypoints.
- `debug-pro-1.0.0` and `test-runner-1.0.0` had no YAML frontmatter.
- `skills/gstack` was a broken gitlink without `.gitmodules`.
- Loop guidance lacked budgets, stop conditions, recovery contracts, and
  token-saving defaults.
- No repository-level validation script existed.

## New Design Principles

1. Codex/Hermes/OpenClaw/Claude compatibility is part of done.
2. Default install mode is `preserve`, not overwrite.
3. The main loop starts simple: localize, repair, validate.
4. Heavy multi-agent workflows require a written scope, budgets, and stop
   conditions.
5. Token savings come from progressive disclosure, local skill reuse, scoped
   searches, and deterministic scripts.
6. Quality comes from tests, browser verification, security checks for risky
   areas, diff review, and fresh evidence.
