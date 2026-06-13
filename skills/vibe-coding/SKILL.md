---
name: vibe-coding
description: >
  The unified vibe coding orchestrator. Automatically coordinates all design,
  engineering, and shipping skills into a seamless flow-state workflow.
  Use when user says "vibe coding", "let's build", "create an app",
  "design this", "prototype this", "start a project", or any creative
  /build/design/implement request. Also triggers proactively when the user
  describes a feature, component, page, or product they want to build.
  This is the PRIMARY entry point for all vibe coding sessions.
---

# Vibe Coding — Unified Orchestrator

**The complete flow-state workflow for AI-assisted creation.**

This skill coordinates gstack, mattpocock, superpowers, GSD, and ECC skills into a unified pipeline. It eliminates decision fatigue by automatically routing to the right sub-skills at each phase.

## Current Priority

Optimize for **token efficiency and production quality together**:

- Reuse local host skills before loading bundled duplicates.
- Load only the skills and references needed for the current phase.
- Prefer deterministic scripts and verification commands over long prose.
- Keep changes small, cohesive, and aligned with the existing codebase.
- Add a de-sloppify/review pass before completion to remove overgrown,
  redundant, or unmaintainable code.
- Do not claim success without fresh verification evidence.

## Host Adapter

If running in Codex, first apply `codex-vibe-coding` for tool mapping, memory
rules, and preserve-mode installation expectations. If running in Hermes,
OpenClaw, Claude Code, Cursor, or another host, translate tool names through the
host's native capabilities before acting.

## Auto-Trigger Conditions

Activate this skill when the user:
- Says "vibe coding", "let's build", "create", "design", "prototype"
- Describes a feature, component, page, app, or product to build
- Mentions "make it look good", "polish UI", "improve design"
- Asks to "start a project", "new milestone", "new phase"
- Provides a vague creative idea without a clear plan

## Phase 0: Vibe Check (Always Run First)

Before any work begins, assess the vibe:

1. **What is the user trying to build?** (app, website, component, feature, tool)
2. **What is the vibe/tone?** (playful, professional, brutalist, luxury, minimal)
3. **Does this involve UI/UX?** (yes/no → routes to design skills or pure engineering)
4. **Is this a new project or existing codebase?** (new → gsd-new-project; existing → context-gathering)
5. **What is the scope?** (trivial/quick task, single feature, multi-phase project)
6. **What is the cheapest quality loop?** (localize-repair-validate, sequential, RFC DAG, PR loop)

**Decision:**
- Scope ≤ 15 min → Fast path (Phase 1b)
- Scope > 15 min + UI involved → Full path with design (Phase 1a → 2 → 3 → 4 → 5)
- Scope > 15 min + no UI → Engineering path (Phase 1a → 3 → 4 → 5)
- Bug/regression → Localize → repair → validate before any heavy orchestration

---

## Phase 1a: Ideation & Requirements (Full Path)

**Goal:** Understand what to build before building it.

**Automatic skill routing:**

- New project, no existing context → Invoke `gsd-new-project`
- Existing project, new feature → Invoke `brainstorming`
- Need deep requirements understanding → Invoke `brainstorming` + `product-lens`
- Have docs to discuss → Invoke `gsd-ingest-docs`
- Need visual exploration → Invoke `prototype` or `frontend-design-3-0.1.0`
- Startup/product strategy → Invoke `product-lens` + `plan-orchestrate`
- Architecture decisions → Invoke `architecture-designer-0.1.0` or `gsd-discuss-phase`

**Output:** Clear requirements + spec + design direction.

---

## Phase 1b: Fast Path (Quick Tasks)

**For trivial tasks (≤ 15 min):**

1. Skip formal planning
2. Invoke `gsd-fast` or `caveman` mode
3. Execute immediately
4. One-shot verification
5. Done

---

## Phase 2: Design & Prototyping (UI Projects)

**Goal:** Define the visual direction before writing production code.

**Automatic skill routing:**

- No design system exists → Invoke `design-system`
- Need to explore visual options → Invoke `prototype` or `frontend-design-3-0.1.0`
- Have a design direction, need to prototype → Invoke `prototype`
- Need design review/audit → Invoke `ui-design-review` or `vibe-design-workflow`
- Building any UI component/page → Invoke `vibe-design-workflow`

**Output:** DESIGN.md or design spec + prototype + approved direction.

---

## Phase 3: Planning & Architecture

**Goal:** Create a clear implementation plan.

**Automatic skill routing:**

- Multi-step implementation → Invoke `writing-plans`
- Need architecture decisions → Invoke `architecture-designer-0.1.0` or `gsd-discuss-phase`
- Need CEO/strategy review → Invoke `product-lens` or `plan-orchestrate`
- Full review pipeline → Invoke `blueprint` or `gsd-plan-phase`
- Need PRD → Invoke `to-prd`
- GSD project management → Invoke `gsd-plan-phase`

**Output:** PLAN.md with clear tasks, file paths, and verification steps.

---

## Phase 4: Implementation

**Goal:** Execute the plan with quality gates.

**Automatic skill routing:**

- Start feature work → Invoke `using-git-worktrees`
- Implement with tests → Invoke `test-driven-development` or `tdd-workflow`
- Debug issues → Invoke `systematic-debugging`, `debug-pro-1.0.0`, or `gsd-debug`
- Execute plan tasks → Invoke `executing-plans` or `subagent-driven-development`
- Parallel tasks → Invoke `dispatching-parallel-agents`
- Need browser testing → Invoke `browser-qa` or `gstack`
- Architecture improvement → Invoke `improve-codebase-architecture`
- Need to zoom out / reassess → Invoke `blueprint` or `gsd-explore`

**Rules:**
- RED-GREEN-REFACTOR for all features
- Atomic commits
- Context-save checkpoints every 15-30 min
- If tests or verification fail twice for the same reason, stop and re-plan
- After implementation, run de-sloppify before final verification

---

## Phase 5: Review & Quality Gates

**Goal:** Ensure output meets standards before shipping.

**Automatic skill routing:**

- Code review → Invoke `requesting-code-review` or `caveman-review` or `plankton-code-quality`
- Design audit → Invoke `ui-design-review` or `vibe-design-workflow`
- QA testing → Invoke `browser-qa`, `e2e-testing`, `ai-regression-testing`, or `verify`
- Security audit → Invoke `security-review`, `security-auditor-1.0.0`, or `security-scan`
- Verification → Invoke `verification-before-completion` or `verification-loop`
- GSD code review → Invoke `gsd-code-review`
- Cross-AI review → Invoke `gsd-review`

**Quality Scorecard (minimum 7.5/10):**
- [ ] All tests pass
- [ ] No slop patterns
- [ ] Accessibility checks pass
- [ ] Design matches spec (if UI)
- [ ] Performance acceptable
- [ ] Code review complete

---

## Phase 6: Ship & Deploy

**Goal:** Deliver the work.

**Automatic skill routing:**

- Create PR → Invoke `gsd-ship` or `finishing-a-development-branch`
- Deploy → Invoke `deployment-patterns` or `gsd-ship`
- Post-deploy monitoring → Invoke `canary-watch` or `production-audit`
- Update docs → Invoke `gsd-docs-update`
- Archive milestone → Invoke `gsd-complete-milestone`

---

## Emergency Skills (Invoke Anytime)

| Situation | Skill |
|-----------|-------|
| Lost/confused | `blueprint` or `gsd-explore` |
| Bug during implementation | `systematic-debugging`, `debug-pro-1.0.0`, or `gsd-debug` |
| Scope creep | `product-lens` or `plan-orchestrate` |
| Need to pause | `gsd-pause-work` or `handoff` |
| Resume later | `gsd-resume-work` |
| Too many tokens | `caveman` or `compress` |
| Session handoff | `handoff` |
| Security concern | `security-review`, `security-auditor-1.0.0`, or `security-scan` |

---

## Communication Style

**Default:** caveman wenyan (文言文) mode — terse, technical, precise.

**Exceptions:**
- Security warnings → Full clarity
- User asks for explanation → Expand as needed
- Multi-step sequences → Numbered steps for clarity

---

## Summary

```
User says "build X"
    │
    ▼
Phase 0: Vibe Check
    │
    ├─→ Trivial? → Fast Path (Phase 1b) → Done
    │
    └─→ Substantial? → Full Path
        │
        Phase 1: Ideation (brainstorming / gsd-new-project / product-lens)
        │
        Phase 2: Design (prototype / frontend-design-3-0.1.0 / vibe-design-workflow)
        │
        Phase 3: Planning (writing-plans / architecture-designer-0.1.0 / blueprint / gsd-plan-phase)
        │
        Phase 4: Implementation (tdd-workflow / executing-plans / subagent-driven-development)
        │
        Phase 5: Review (requesting-code-review / caveman-review / ui-design-review / browser-qa / verification-loop)
        │
        Phase 6: Ship (gsd-ship / deployment-patterns / canary-watch)
```

**Golden Rule:** Never skip Phase 0. Always understand the vibe before choosing the path.
