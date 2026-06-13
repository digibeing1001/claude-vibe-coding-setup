# Original vs Improved Setup

Generated: 2026-06-14

## Summary

The original repository was a useful Claude Code workflow bundle. The improved
version turns it into a portable Vibe Coding harness for Claude Code, Codex,
Hermes, OpenClaw, and similar hosts.

## Test Results

Validated on Windows PowerShell in this repository:

```text
python scripts/validate_setup.py
Skills: 156
OK: 156
Warnings: 0
Errors: 0
```

Codex install dry run:

```text
python scripts/install-universal.py --host codex --mode preserve --dry-run
installed=133 skipped=23 overwritten=0
```

Codex real install:

```text
python scripts/install-universal.py --host codex --mode preserve
installed=133 skipped=23 overwritten=0
```

Post-install discovery checks passed for:

- `~/.codex/skills/codex-vibe-coding/SKILL.md`
- `~/.codex/skills/vibe-coding/SKILL.md`
- `~/.codex/skills/continuous-agent-loop/SKILL.md`

Codex skill directory after install: 190 skill directories.

## Comparison

| Area | Original | Improved |
| --- | --- | --- |
| Host support | Claude Code only | `install-universal.py` supports Codex, Claude, Hermes, OpenClaw |
| Install safety | Copy/overwrite behavior | `preserve` by default; `overwrite` requires explicit flag and creates backups |
| Main entrypoints | Some key skills stored as lowercase `skill.md` | Standard `SKILL.md` paths for strict discovery |
| Broken dependency | `skills/gstack` gitlink without `.gitmodules` | Real `gstack` compatibility shim |
| Skill validity | Missing frontmatter in some skills | Frontmatter added and validator catches regressions |
| Loop behavior | Broad autonomous guidance | Budgets, stop conditions, localize-repair-validate, de-sloppify, recovery |
| Harness behavior | Claude-specific crons/memory/tools | Portable capability detection and host adapter rules |
| Token discipline | Implied by some skills | Explicit priority: progressive disclosure, local reuse, minimal context |
| Verification | Manual expectation | `scripts/validate_setup.py` plus fresh evidence rules |
| Codex usage | Not directly configured | New `codex-vibe-coding` skill and Codex install path |

## Concrete Before/After Findings

Before:

- `skills/vibe-coding/skill.md` and `skills/vibe-design-workflow/skill.md`
  used lowercase filenames.
- `skills/gstack` was a `160000` gitlink, but `.gitmodules` was missing.
- `skills/debug-pro-1.0.0/SKILL.md` and
  `skills/test-runner-1.0.0/SKILL.md` started with headings instead of YAML
  frontmatter.
- README described a Claude-only install path.

After:

- strict `SKILL.md` entrypoints exist
- no validation errors or warnings
- `gstack` is a real compatibility shim
- Codex install uses preserve mode and keeps existing local skills
- loop and harness guidance now include budgets, stop conditions, recovery, and
  token discipline

## Tradeoffs

Original strengths:

- Large skill surface already collected.
- Easy Claude Code mental model.
- Strong product/design/engineering ambition.

Improved strengths:

- Safer install behavior.
- Works across more hosts.
- Easier to validate before publishing.
- Better token economics.
- Lower risk of unbounded agent loops.
- More explicit path from research to production quality gates.

Remaining tradeoffs:

- The bundle is still large; future work should prune duplicate skills after
  observing real Codex usage.
- External high-star skill repositories were not vendored directly; they should
  be evaluated one by one before import.
- Hooks are still Claude-shaped. Cross-host hook installation needs separate
  host-specific adapters once Hermes/OpenClaw hook formats are confirmed.
