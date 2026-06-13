---
name: gstack
description: Compatibility shim for GStack-derived browser QA, review, design-review, and Codex/Claude host patterns bundled in this repository. Use when a workflow references gstack directly, or when porting GStack-style review and browser QA guidance across Claude Code, Codex, OpenClaw, Hermes, Cursor, or other coding-agent hosts.
---

# GStack Compatibility Shim

This repository used to track `skills/gstack` as a gitlink without a `.gitmodules`
mapping, which made ordinary clones install an empty, unusable skill. This shim
keeps the route discoverable while avoiding a broken submodule dependency.

## How To Use

When a workflow references `gstack`, route to the concrete skill that matches the
task:

| Need | Use |
| --- | --- |
| Browser or product QA | `browser-qa`, `e2e-testing`, `verify` |
| Code review | `review`, `caveman-review`, `requesting-code-review` |
| UI/design review | `design-review`, `ui-design-review`, `vibe-design-workflow` |
| Codex or Claude host mapping | `using-superpowers`, then the host-specific reference if present |
| Context compression | `compress` |
| Planning or phase control | `blueprint`, `gsd-plan-phase`, `gsd-execute-phase` |

## Portability Rule

Prefer host-native tools first. If a GStack instruction names a Claude-only tool,
translate it through the local host mapping before acting:

- `Task` -> Codex multi-agent tools when available
- `TodoWrite` -> Codex `update_plan`
- browser QA -> local browser plugin or Playwright
- shell commands -> native shell tool with the host's safety policy

## Quality Gate

Do not treat this shim as a full GStack install. If a task truly requires the
upstream GStack project, install or sync that project explicitly, then re-run
`scripts/validate_setup.py`.
