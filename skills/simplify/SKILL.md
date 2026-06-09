---
name: simplify
description: Review changed code for reuse, simplification, efficiency, and altitude cleanups, then apply the fixes. Quality only — it does not hunt for bugs; use code-review for that. Use when asked to simplify, clean up, reduce complexity, or make code more readable.
---

# Simplify

Review the changed code for **quality cleanups only** — reuse, simplification, efficiency, and altitude. This skill does NOT hunt for bugs; use `code-review` for that.

## Scope

Only review lines that were changed in the current diff. Do not touch adjacent code.

## Review Dimensions

### 1. Reduce Nesting
- Convert nested if/else chains to early returns (guard clauses)
- Replace nested loops with flatMap, reduce, or helper functions
- Extract deeply nested callbacks into named functions
- Target: maximum 3 levels of indentation in any function

### 2. Reuse Existing Code
- Check if a utility function already exists before writing new code
- Replace duplicated logic with shared helpers
- Use language/framework built-ins instead of reinventing them
- Check if a library function does what the custom code does

### 3. Simplify Logic
- Replace complex boolean expressions with well-named variables
- Convert switch statements to object lookups or maps when simple
- Remove unnecessary else blocks after return statements
- Merge consecutive if statements with logical operators
- Replace imperative loops with declarative array methods (map, filter, reduce)

### 4. Altitude Cleanups
- Remove dead code paths (unreachable branches, unused variables)
- Eliminate unnecessary type assertions (trust the type system)
- Remove redundant null checks when types already guarantee non-null
- Simplify over-abstracted code (single-use abstractions → inline)
- Remove speculative code that handles impossible scenarios

### 5. Efficiency
- Move invariant computations out of loops
- Replace O(n²) with O(n) when a Map/Set would work
- Use lazy evaluation where appropriate
- Avoid unnecessary object allocations in hot paths

## Process

1. Read the current diff
2. For each changed hunk, check all 5 dimensions above
3. Apply fixes directly — do not just suggest
4. Commit each logical fix separately

## Rules

- **Quality only.** This skill does not find bugs.
- **Only touch changed lines.** Do not refactor adjacent code.
- **Match existing style.** Don't introduce new patterns.
- **Every change traces to a dimension above.** No cosmetic-only edits.
