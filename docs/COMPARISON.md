# Original vs Improved Setup

Generated: 2026-06-14

## Summary

The original repository was a Claude Code workflow bundle. The improved version
is a portable Vibe Coding harness for Codex, Claude Code, Hermes, OpenClaw, and
similar hosts.

## Comparison

| Area | Original | Improved |
| --- | --- | --- |
| Host support | Claude Code oriented | Codex, Claude Code, Hermes, OpenClaw installers |
| Install behavior | Broad copy/overwrite | Preserve by default; targeted `--only` overwrite |
| Skill discovery | Some lowercase `skill.md`; broken `gstack` gitlink | Strict `SKILL.md`; gitlink replaced; validator added |
| Harness | Prompt-heavy workflow | Host adapter, state/evidence contracts, loop budgets |
| Bug loop | Broad autonomous guidance | localize -> repair -> validate before orchestration |
| Completion | Manual review expectation | `score_vibe_run.py` runtime score gate |
| Capability gaps | User had to ask or agent improvised | Phase 0 sensor plus findskill-compatible discovery |
| External skills | Not tracked | Candidate registry plus GitHub/ClawHub/Skills CLI discovery |
| Publish | Local-only install story | Commit/push verification and host-ready install path |

## Test Results

Baseline validation after the first iteration:

```text
python scripts/validate_setup.py
Skills: 156
OK: 156
Warnings: 0
Errors: 0
```

Codex install after the first iteration:

```text
python scripts/install-universal.py --host codex --mode preserve
installed=133 skipped=23 overwritten=0
```

This second iteration adds:

- `scripts/score_vibe_run.py`
- `scripts/find_skill_candidates.py`
- `skills/vibe-run-review`
- `config/skill-candidates.json`
- `docs/EXTERNAL_SKILL_CANDIDATES.md`
- targeted installer updates via `--only`

Second iteration verification:

```text
python -m py_compile scripts\install-universal.py scripts\validate_setup.py scripts\score_vibe_run.py scripts\find_skill_candidates.py
exit code: 0

python scripts\validate_setup.py
Skills: 157
OK: 157
Warnings: 0
Errors: 0
Notices: 113

python scripts\find_skill_candidates.py --capability security --query "claude code security skill" --limit 3 --min-stars 50 --timeout 10 --markdown
exit code: 0
Local registry candidates included BehiSecc/VibeSec-Skill and trailofbits/skills.
GitHub live search returned high-star security skill candidates.

python scripts\score_vibe_run.py --required testing,review,security,browser-qa,findskill --live-skill-search --search-limit 2 --markdown
Status: review
Total: 73/100
Capability coverage: 20/20
Maintainability: 20/20

python scripts\score_vibe_run.py --required testing,review,security,browser-qa,findskill --live-skill-search --search-limit 2 --evidence docs\COMPARISON.md --markdown
Status: pass
Total: 90/100
Diff: git diff --numstat HEAD + untracked
Verification evidence: 25/25
Capability coverage: 20/20
Maintainability: 20/20

python scripts\install-universal.py --host codex --mode overwrite --only codex-vibe-coding --only vibe-coding --only vibe-run-review --only continuous-agent-loop --dry-run
installed=1 skipped=0 overwritten=3
files: tool:installed, tool:installed, tool:installed, tool:installed, config:installed

python scripts\install-universal.py --host codex --mode overwrite --only codex-vibe-coding --only vibe-coding --only vibe-run-review --only continuous-agent-loop
installed=1 skipped=0 overwritten=3
files: tool:installed, tool:installed, tool:installed, tool:installed, config:installed

python $HOME\.codex\vibe-coding\scripts\score_vibe_run.py --root . --skills-dir $HOME\.codex\skills --required testing,review,security,browser-qa,findskill --evidence docs\COMPARISON.md --markdown
Status: pass
Total: 92/100

python $HOME\.codex\vibe-coding\scripts\find_skill_candidates.py --root . --capability findskill --query "OpenClaw findskill skill registry" --limit 3 --min-stars 50 --timeout 10 --markdown
exit code: 0
Local registry candidates included openclaw/clawhub and vercel-labs/skills.
```

The first score run intentionally had no evidence file, so it stayed at review.
The completion score passes once the verification evidence is supplied.

## Improvement From Iteration

The first iteration made the bundle installable and valid. The second iteration
turns quality and external-skill discovery into executable checks:

- capability needs are inferred from the task/diff
- missing capability coverage creates a candidate search path
- live discovery can call GitHub, the Skills CLI, ClawHub, or standalone
  findskill tools when available
- external imports stop at a user-approval boundary
- Codex can update only the changed entrypoint skills without overwriting the
  whole local skill directory

## Remaining Tradeoffs

- Live GitHub search can be rate limited without authentication.
- `npx skills find` and `npx clawhub search` are optional runtime tools; the
  script degrades to GitHub search and local registry if they are unavailable.
- Candidate quality still requires review. Stars and install counts are useful
  signals, not trust guarantees.
