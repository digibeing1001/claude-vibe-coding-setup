---
name: vibe-run-review
description: Runtime scoring gate for Vibe Coding runs. Use before completion, before publish, or whenever the agent detects a missing capability and needs to propose external GitHub skills for user approval.
---

# Vibe Run Review

Use this skill as the final gate for a coding run and as the intake workflow for
missing capabilities.

## Run Score

From the repository root:

```bash
python scripts/score_vibe_run.py --live-skill-search --markdown
```

If repository scripts are unavailable, use the host-installed copy such as:

```bash
python ~/.codex/vibe-coding/scripts/score_vibe_run.py --skills-dir ~/.codex/skills --live-skill-search --markdown
```

For risky or UI work, pass explicit capabilities:

```bash
python scripts/score_vibe_run.py --required testing,review,security,browser-qa --live-skill-search --markdown
```

Score interpretation:

| Score | Meaning | Agent action |
| --- | --- | --- |
| 85-100 | pass | Report evidence and residual risk |
| 70-84 | review | Fix the weakest dimension or explain the accepted tradeoff |
| <70 | fail | Do not ship; reduce scope, add evidence, or cover gaps |

## Missing Capability Workflow

When the score reports a capability gap:

1. Search GitHub and findskill-compatible registries before writing a new skill.
2. Prefer official, curated, recently maintained, and narrowly scoped sources.
3. Compare each candidate against existing local skills to avoid duplicates.
4. Tell the user which skill should be added, why, license/maintenance notes,
   and what files or host behavior will change.
5. Wait for user approval before importing, installing, or overwriting skill
   code.
6. After import, run `scripts/validate_setup.py` and this score gate again.

Use `docs/EXTERNAL_SKILL_CANDIDATES.md` and
`config/skill-candidates.json` as the local candidate registry. Refresh GitHub
search results when the decision affects the current task.

The discovery command is:

```bash
python scripts/find_skill_candidates.py --capability <capability> --include-cli --markdown
```

Installed fallback:

```bash
python ~/.codex/vibe-coding/scripts/find_skill_candidates.py --capability <capability> --include-cli --markdown
```

The command may use GitHub search, `npx skills find`, `npx clawhub search`, or a
standalone `findskill` executable when available. It never installs anything.

## Review Dimensions

- Change containment: changed files and line delta fit the task.
- Verification evidence: current commands or observations exist.
- Capability coverage: required review/testing/security/UI/deploy skills exist.
- Maintainability: obvious debug markers, dead-end TODOs, and oversized files
  are reviewed.
- Context surface: instruction and skill changes remain bounded.
