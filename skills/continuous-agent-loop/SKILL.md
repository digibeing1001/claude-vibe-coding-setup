---
name: continuous-agent-loop
description: Production patterns for continuous autonomous coding-agent loops with explicit scope, token and cost budgets, verification gates, failure recovery, CI/PR controls, and stop conditions. Use when running iterative Vibe Coding, long-horizon implementation, autonomous repair, multi-agent coding, or any loop that must avoid churn and produce production-quality code.
origin: ECC
---

# Continuous Agent Loop

Use this skill to run Vibe Coding as a controlled engineering loop, not an
unbounded prompt loop. The default goal is **minimum useful context plus maximum
fresh verification evidence**.

## Non-Negotiables

1. Set a stop condition before the loop starts: max iterations, max time, max
   failures, max token/cost budget, or explicit acceptance criteria.
2. Keep the working set small. Load only the relevant plan, files, diffs, test
   output, and skill references for the current iteration.
3. Use the simple path first: localize -> patch -> validate. Escalate to
   multi-agent orchestration only when the task actually needs it.
4. Verify every success claim with fresh command output or direct observation.
5. Stop and re-plan after repeated failures. Do not retry the same error with
   the same context.

## Research-Backed Operating Model

- Agent Skills best practice: use progressive disclosure. Keep `SKILL.md`
  compact and move details into references or scripts that load only when
  needed.
- Agentless-style repair: for many bugs, a simple localize -> repair -> patch
  validation loop is cheaper and easier to audit than a free-running agent.
- SWE-agent-style harness design: give the agent a small, reliable action space
  and strong observations: file search, edit, command execution, and tests.
- OpenHands-style deployment: use sandboxing, event logs, multi-agent
  coordination, and evaluation hooks when tasks become long-running or risky.

## Loop Selection Flow

```text
Start with the smallest loop that can prove the work.

Bug or failing test?
  -> localize-repair-validate

Single focused feature?
  -> sequential-quality-loop

Large spec with independent work units?
  -> rfc-dag-loop

Need many creative variants?
  -> parallel-generation-loop

Need PR, CI, or deployment automation?
  -> continuous-pr-loop
```

## Loop Patterns

### 1. Localize-Repair-Validate

Use for most bugs and regressions.

1. Reproduce the failure with the smallest command.
2. Localize by file, symbol, and edit location.
3. Patch the smallest correct surface.
4. Run the original failing command.
5. Run the adjacent regression or smoke test.
6. Record what changed and why.

Escalate only if localization fails twice or the patch touches shared
architecture.

### 2. Sequential Quality Loop

Use for a focused feature or refactor.

1. Read only the relevant plan and files.
2. Implement one coherent slice.
3. Run scoped tests, lint/type checks where available.
4. Run a de-sloppify pass: remove redundant checks, dead code, overbroad
   abstractions, and tests of framework behavior.
5. Run verification again.
6. Commit or checkpoint only after evidence is fresh.

### 3. RFC DAG Loop

Use for a written spec that can be decomposed.

1. Decompose into work units with real dependency edges.
2. Keep tests with the implementation unit.
3. Run independent units in isolated worktrees or host-native task spaces.
4. Land low-overlap units first.
5. Rebase and re-test before merging each unit.
6. Evict conflicting or failing units with exact failure context.

### 4. Parallel Generation Loop

Use for prototypes, design alternatives, or research candidates.

1. Assign each agent a unique direction and output path.
2. Make uniqueness explicit; do not ask agents to self-differentiate.
3. Compare outputs with a rubric.
4. Promote one path into the sequential quality loop.

### 5. Continuous PR Loop

Use only when CI and repository permissions are ready.

1. Create an isolated branch/worktree.
2. Implement one PR-sized iteration.
3. Run local quality gates.
4. Push and wait for CI.
5. Feed failing CI logs into one repair attempt.
6. Stop after configured retry budget.

## Budgets

Set budgets at loop start:

| Budget | Default | Stop When |
| --- | --- | --- |
| Iterations | 3 | same acceptance criterion still fails |
| Failure repeats | 2 | same root cause appears again |
| Time | task-dependent | verification cannot run within budget |
| Context | minimal | unrelated files or old logs dominate context |
| Cost/tokens | conservative | extra agent would not reduce risk |

## State File

For loops longer than one iteration, keep a small state file such as
`work/vibe-loop-state.md` or `.agent/vibe-loop-state.md`:

```markdown
## Goal

## Acceptance Criteria

## Current Evidence

## Decisions

## Failed Attempts

## Next Smallest Step
```

Do not turn this file into a diary. Keep only facts needed to resume.

## Quality Gates

Before calling work complete:

- scoped test or reproduction command passes
- type/lint/build gate passes when the project provides it
- diff review finds no unrelated churn
- UI work has browser/screenshot verification
- security-sensitive work gets secret/input/auth checks
- docs/install changes are tested in dry-run mode

## Failure Modes

- Loop churn without measurable progress.
- Retrying the same failure with the same prompt.
- Parallel agents editing overlapping files without merge strategy.
- Huge context from stale logs, full docs, or irrelevant skills.
- False completion claims based on confidence instead of evidence.
- CI repair loops that burn budget without new information.

## Recovery Protocol

1. Freeze the loop.
2. Summarize the last failing command, exit code, and root cause hypothesis.
3. Reduce the task to the smallest failing unit.
4. Drop stale context and reload only relevant files.
5. Re-run localize -> repair -> validate once.
6. If still failing, ask for scope adjustment or human decision.

## Output Format

When reporting loop status, include:

```markdown
Loop: <pattern>
Budget: <iterations/time/failure budget>
Evidence: <commands or observations>
Changed: <files or PRs>
Risks: <remaining risks>
Next: <one smallest next step or complete>
```
