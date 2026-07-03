---
name: maker-checker
description: Maker/Checker physical separation. Maker (executor) cannot mark own work complete; Checker (verifier) must be a separate agent/session using "find reasons to reject" instructions, a stronger-or-equal model, and an isolated worktree. Runs the 6-stage verification (Build→TypeCheck→Lint→Test→Security→Diff Review). Use for any code change that needs trustworthy verification.
---

# Maker/Checker

Maker/Checker separation is the most important structural pattern for reliable loops. The executor (Maker) cannot mark its own work complete. The verifier (Checker) must be a physically separate entity — different agent/session, different instructions, isolated worktree.

## When to Use

- Any code change that needs trustworthy verification
- Any loop running at L2 or L3 readiness
- Any PR that will be merged
- Any change where AI self-approval is not acceptable

## Why Physical Separation

Same agent writing and verifying has three failure modes:

1. **Self-confirmation bias** — agent believes its own code, looks for "pass reasons" not "reject reasons"
2. **Context pollution** — writing mindset carries into verification, blind spots persist
3. **Verifier Theater** — verification exists in name only, rubber-stamps everything

## Maker Responsibilities

### Hard Constraints

- **Cannot mark own work complete** — must hand off to Checker
- **Cannot run final verification** — local test debugging is fine, but "passed local tests" is not completion evidence
- **Must produce Checker-readable artifacts** — code + diff + test commands + expected behavior
- **Must declare assumptions** — what I assumed, what's uncertain, what's a known risk

### Maker Output Format

```markdown
## Maker Report
Goal: <goal>
Changed: <file list + line delta>
Tests added: <test list>
Assumptions: <assumption list>
Known risks: <known risks>
Commands to verify: <commands Checker should run>
Expected behavior: <expected results>
```

## Checker Responsibilities

### Hard Constraints

- **Must be a separate entity** — different agent, different session, or different script
- **Uses "find reasons to reject" instructions** — not "verify this is correct" but "find reasons to reject this"
- **Uses a stronger or equal model** — Checker cannot be weaker than Maker
- **Runs in isolated worktree** — does not pollute Maker's working directory
- **Must report raw output** — not "tests passed" but the raw stdout/stderr

### Checker Instruction Template

```markdown
You are an independent Verifier. Your job is to find reasons to REJECT this change, not to confirm it correct.

Change:
<Maker's diff>

Acceptance criteria:
<acceptance criteria>

Execute:
1. Run tests: <commands>
2. Run type check: <type check>
3. Run lint: <lint>
4. Run security scan: <security scan>
5. Review diff: find unrelated changes, dead code, over-abstraction, missing tests
6. Run end-to-end (if applicable): <e2e>

Output:
## Verifier Verdict
- Verdict: APPROVE | REJECT | REQUEST_CHANGES
- Blockers: <must-fix-before-merge issues>
- Concerns: <non-blocking but noteworthy issues>
- Evidence: <raw command output>
- Missing: <unverified parts and why>
```

## 6-Stage Verification

Checker runs 6 stages by default. Deterministic checks primary, AI review secondary.

```
Build → TypeCheck → Lint → Test → Security → Diff Review
```

### 1. Build
```bash
npm run build  # or language-equivalent
```
Build must pass. Failure → REJECT.

### 2. TypeCheck
```bash
npx tsc --noEmit  # or language-equivalent
```
Type check must pass. Failure → REJECT.

### 3. Lint
```bash
npx eslint .  # or language-equivalent
```
Lint must pass. Failure → REJECT.

### 4. Test
```bash
npm test
npx playwright test  # E2E if applicable
```
Tests must be green. Failure → REJECT.

### 5. Security
```bash
npm audit --audit-level=moderate
git diff --cached | grep -iE "(api_key|secret|password|token).*=.*['\"]"
```
Security scan must pass. Failure → REJECT.

### 6. Diff Review
AI reviews diff for:
- Unrelated changes (outside task scope)
- Dead code (removed but not cleaned up)
- Over-abstraction (unnecessary interfaces/layers)
- Missing tests (changed behavior without tests)
- Inconsistency (doesn't match project patterns)

Diff Review outputs REQUEST_CHANGES, not REJECT — advisory, not blocking.

## Verifier Theater Anti-Patterns

| Anti-pattern | Symptom | Fix |
| --- | --- | --- |
| Same session | Maker and Checker in same conversation | Force different session/agent |
| Same model | Maker and Checker use same model | Checker uses stronger/equal model |
| Find-pass-reasons | Checker instruction is "verify correct" | Change to "find reasons to reject" |
| Re-run Maker's tests | Checker re-runs Maker's tests | Checker runs independent test set |
| No raw output | Checker reports "tests passed" | Must attach raw stdout/stderr |
| Partial verification | Only build, no test | Run all 6 stages (or declare skip reason) |

## Isolated Worktree

Checker must verify in an isolated worktree:

```bash
git worktree add ../verify-<run_id> <branch>
cd ../verify-<run_id>
npm ci
npm test
npm run build
cd ..
git worktree remove ../verify-<run_id>
```

## Retry Limit

Same PR/change auto-fix has a hard limit: **3 attempts → escalate to human**.

```text
Attempt 1: Maker writes → Checker rejects → feedback to Maker
Attempt 2: Maker fixes → Checker rejects → feedback to Maker
Attempt 3: Maker fixes → Checker rejects → escalate to human
```

Record attempt count in STATE.md. Same PR >3 auto-fix attempts with no progress → stop, transition to `wait_human`.

## Controller Contract

Checker's verdict is input to the controller's state transition:

| Verdict | Controller Action |
| --- | --- |
| APPROVE | Transition to `complete` (if budget and acceptance all pass) |
| REJECT | Transition to `retry` (attempts < 3) or `wait_human` (attempts >= 3) |
| REQUEST_CHANGES | Transition to `retry` with Checker's concerns |

AI cannot override Checker's verdict. Maker cannot directly transition to `complete`; must wait for Checker's APPROVE.

Full spec: [`loops/maker-checker.md`](../../loops/maker-checker.md)
