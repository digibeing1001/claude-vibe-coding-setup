---
name: verify
description: Verify that a code change actually does what it's supposed to by running the app and observing behavior. Use when asked to verify a PR, confirm a fix works, test a change manually, check that a feature works, or validate local changes before pushing.
---

# Verify

Verify that a code change actually does what it's supposed to by running the app and observing behavior.

## When to Use

- After implementing a feature — does it work end-to-end?
- After fixing a bug — is the bug actually fixed?
- Before pushing — do all the changes work together?
- After a refactor — does behavior remain the same?

## Process

### 1. Understand What to Verify
Read the PR description, commit messages, or PLAN.md to understand:
- What was the intended change?
- What should work now that didn't before?
- What should stay the same?

### 2. Start the Application
```bash
# Detect and run the appropriate dev server
npm run dev / yarn dev / bun dev / pnpm dev
# Or for other stacks, detect the appropriate command
```

### 3. Test Each Change Manually
For each claimed change:
1. Navigate to the relevant page/feature
2. Perform the action described
3. Verify the expected outcome
4. Check for regressions in adjacent areas

### 4. Check Edge Cases
- Empty states (no data)
- Error states (invalid input)
- Boundary values (max length, zero, negative)
- Mobile viewport (responsive)
- Keyboard navigation (tab order)

### 5. Report Results
```
✅ Feature X works as expected
✅ Bug Y is fixed
❌ Feature Z has issue: [description]
⚠️ Edge case: [description]
```

## Rules

- **Observe, don't assume.** Actually run the code and interact with it.
- **Test what changed, not everything.** Focus on the diff's scope.
- **Report failures honestly.** Don't gloss over issues.
- **Stop at blockers.** If the app won't start, report that first.
