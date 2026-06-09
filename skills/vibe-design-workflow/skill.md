---
name: vibe-design-workflow
description: >
  Orchestrate all UI/UX design skills in the vibe coding workflow.
  Use this skill when building, reviewing, or beautifying any web UI component,
  page, application, or interface during vibe coding sessions.
  Triggers on: "design this", "make it look good", "beautify", "polish UI",
  "design review", "UX audit", "check accessibility", "improve design",
  "create component", "landing page", "dashboard design", or any visual/UI request.
metadata:
  version: "2.0.0"
  author: "Vibe Design Collective"
  requires:
    - frontend-design-3-0.1.0
    - frontend-design-direction
    - design-system
    - coding-standards
    - ui-design-review
    - product-lens
    - motion-foundations
    - motion-patterns
    - motion-advanced
---

# Vibe Coding Design Workflow

**The complete design orchestration system for vibe coding.**

This skill coordinates all design-related skills into a unified workflow. It ensures every UI/UX output during vibe coding meets production-grade standards while maintaining creative boldness and user-centered quality.

## Philosophy

> **Design is not decoration — it's problem-solving through intentional visual decisions.**

In vibe coding, design happens iteratively and rapidly. This workflow provides guardrails without slowing you down. Each phase has clear entry/exit criteria, so you know when to move forward and when to pause for quality gates.

---

## Workflow Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. STRATEGY    │───▶│ 2. IMPLEMENTATION│───▶│  3. REVIEW      │───▶│  4. OPTIMIZE    │
│  (Why & What)   │    │  (How)           │    │  (Quality Gate) │    │  (Polish)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Phase 1: Design Strategy (Always Start Here)
**Duration:** 1-2 minutes of thinking
**Goal:** Define the design direction before writing any code

**Before coding, answer these questions:**

1. **Purpose**: What problem does this interface solve? Who uses it?
2. **Tone**: Pick an extreme aesthetic direction:
   - Brutally minimal / Maximalist chaos
   - Retro-futuristic / Organic-natural
   - Luxury-refined / Playful-toy-like
   - Editorial-magazine / Brutalist-raw
   - Art deco-geometric / Soft-pastel
   - Industrial-utilitarian
3. **Constraints**: Technical requirements (framework, performance, accessibility needs)
4. **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?
5. **User Context**: Are users experts or novices? What's their emotional state?

**Engagement Design (if applicable):**
- What internal trigger drives usage? (boredom, loneliness, FOMO, confusion)
- What's the simplest core action? (should complete in < 60 seconds)
- What variable reward keeps users coming back? (social validation, discovery, mastery)
- What investment loads the next trigger? (data, content, social capital)

**Output:** A 2-3 sentence design direction statement.

**Example:** *"A brutalist dashboard for power users. High information density, monospace fonts, aggressive contrasts. The unforgettable element: real-time data pulses as a living grid. Users are experts who value speed over hand-holding."*

---

### Phase 2: Design Implementation
**Goal:** Build the UI with intentional aesthetic and technical excellence

#### Step 2a: Visual Foundation
Apply the **frontend-design-3-0.1.0** and **frontend-design-direction** skill principles:

**Typography:**
- Choose distinctive fonts — never default to Inter, Roboto, Arial, or system fonts
- Pair a display font with a refined body font
- Use `font-variant-numeric: tabular-nums` for numbers
- Apply `text-wrap: balance` or `text-pretty` on headings
- Use ellipsis `…` not three dots `...`
- Use curly quotes `"` `"` not straight `"`

**Color & Theme:**
- Commit to a cohesive palette with CSS variables
- Dominant colors + sharp accents > timid, evenly-distributed palettes
- NEVER use purple gradients on white (the ultimate AI slop)
- Define dark mode with `color-scheme: dark` on `<html>`
- Set `<meta name="theme-color">` matching page background

**Spatial Composition:**
- Unexpected layouts: asymmetry, overlap, diagonal flow, grid-breaking
- Generous negative space OR controlled density (commit to one)
- Use flex/grid over JS measurement for layout
- Handle long content: `truncate`, `line-clamp-*`, or `break-words`
- Flex children need `min-w-0` to allow text truncation

**Backgrounds & Visual Details:**
- Create atmosphere: gradient meshes, noise textures, geometric patterns
- Layered transparencies, dramatic shadows, decorative borders
- Custom cursors, grain overlays for texture
- Match complexity to aesthetic vision (maximalist = elaborate code)

#### Step 2b: Component Architecture
Apply **frontend-design-3-0.1.0** and **design-system** principles:

- Use composition over inheritance
- Build compound components for complex UI (tabs, modals, dropdowns)
- Implement proper prop interfaces with TypeScript
- Keep components focused and single-responsibility
- Handle empty states explicitly

#### Step 2c: Motion & Animation
Apply **motion-foundations**, **motion-patterns**, and **motion-advanced** principles:

**Performance Rules:**
- Animate `transform` and `opacity` only (compositor-friendly)
- NEVER use `transition: all` — list properties explicitly
- Set correct `transform-origin`
- Honor `prefers-reduced-motion` (provide reduced variant or disable)
- Animations must be interruptible — respond to user input mid-animation

**Critical Performance Rules (from motion-foundations + motion-patterns):**
- NEVER interleave layout reads and writes in the same frame
- NEVER animate layout continuously on large surfaces
- NEVER drive animation from scrollTop/scrollY/scroll events
- NEVER use requestAnimationFrame loops without stop condition
- NEVER mix multiple animation systems that measure/mutate layout

**Implementation:**
- CSS-only animations for simple HTML
- Motion library for React when available
- One well-orchestrated page load > scattered micro-interactions
- Use scroll-triggering and hover states that surprise
- SVG transforms on `<g>` wrapper with `transform-box: fill-box; transform-origin: center`
- Prefer Scroll/View Timelines for scroll-linked motion
- Use IntersectionObserver for visibility and pausing
- Pause/stop animations when off-screen
- Keep blur animation small (<=8px), use only for short one-time effects
- NEVER animate blur continuously or on large surfaces

#### Step 2d: Accessibility Foundation
Apply accessibility principles (non-negotiable):

**Semantic HTML First:**
```
1. Is there a native HTML element for this? Use it.
2. If native element has gaps, enhance with ARIA.
3. Only if no native element exists, build custom widget with ARIA.
```

**Mandatory Checks:**
- `<html lang="en">` (or matching content language)
- All images have `alt` (`alt=""` for decorative)
- Every form input has associated `<label>`
- Links have descriptive text — no "click here", "read more"
- Headings hierarchical `<h1>`–`<h6>`, never skip levels
- All interactive elements keyboard accessible
- No `tabindex` values > 0
- Touch targets minimum 44×44px

**ARIA Rules:**
- Never `role="button"` on `<button>`, `role="link"` on `<a>`
- Never `aria-label` on non-interactive elements (`<p>`, `<div>`, `<span>`)
- Verify all ARIA reference IDs exist (`aria-labelledby`, `aria-describedby`)
- Use `aria-hidden="true"` on decorative icons

**Focus Management:**
- All interactive elements need visible focus indicator
- Use `:focus-visible` over `:focus`
- Never `outline: none` without replacement
- Minimum 3:1 contrast for focus indicators
- Focus trap in modals, return focus on close

**Color Contrast (WCAG 2.2 AA):**
- Normal text: 4.5:1 minimum
- Large text (24px+): 3:1 minimum
- UI components/borders: 3:1 minimum
- Form field borders: always check explicitly

#### Step 2e: Interaction Design
Apply **design-system** and **coding-standards** interaction principles:

**Forms:**
- Inputs need `autocomplete` and meaningful `name`
- Use correct `type` (`email`, `tel`, `url`, `number`) and `inputmode`
- Never block paste (`onPaste` + `preventDefault`)
- Labels clickable (`htmlFor` or wrapping control)
- Disable spellcheck on emails, codes, usernames
- Submit button stays enabled until request starts; spinner during request
- Errors inline next to fields; focus first error on submit
- Placeholders end with `…` and show example pattern

**Navigation & State:**
- URL reflects state (filters, tabs, pagination in query params)
- Links use `<a>`/`<Link>` (not `<div onClick>`)
- Deep-link all stateful UI
- Destructive actions need confirmation or undo

**Touch & Interaction:**
- `touch-action: manipulation` (prevents double-tap zoom delay)
- `-webkit-tap-highlight-color` set intentionally
- `overscroll-behavior: contain` in modals/drawers
- During drag: disable text selection, `inert` on dragged elements
- `autoFocus` sparingly — desktop only, single primary input

**Hover & States:**
- Buttons/links need `hover:` state
- Interactive states increase contrast
- Never hide critical info behind hover-only states

**Content & Copy:**
- Active voice: "Install the CLI" not "The CLI will be installed"
- Title Case for headings/buttons
- Numerals for counts: "8 deployments" not "eight"
- Specific button labels: "Save API Key" not "Continue"
- Error messages include fix/next step
- Second person; avoid first person

---

### Phase 3: Design Review (Quality Gate)
**Goal:** Catch issues before they become problems

#### Review A: Visual Design Audit (frontend-design-3-0.1.0 + design-system)
- [ ] Aesthetic direction is clear and intentional
- [ ] Typography is distinctive and readable
- [ ] Color palette is cohesive and memorable
- [ ] Layout has clear visual hierarchy
- [ ] No generic AI aesthetics (purple gradients, overused fonts)
- [ ] Visual details create atmosphere (not just solid colors)

#### Review B: Usability Audit (ui-design-review, product-lens)
Score the interface 0-10 on each heuristic:

**Krug's Laws:**
- [ ] **Don't Make Me Think** (3/10): Is everything self-evident?
- [ ] **Clicks Don't Matter** (3/10): Is each click painless and obvious?
- [ ] **Half the Words** (2/10): Is copy concise and scannable?
- [ ] **Trunk Test** (2/10): Can users orient themselves instantly?

**Nielsen's Heuristics:**
- [ ] Visibility of system status (loading, progress, confirmations)
- [ ] Match between system and real world (plain language, familiar metaphors)
- [ ] User control and freedom (undo, back buttons, escape hatches)
- [ ] Consistency and standards (same words = same meanings)
- [ ] Error prevention (constraints, defaults, validation)
- [ ] Recognition rather than recall (show options, don't require memory)
- [ ] Flexibility and efficiency (shortcuts for experts)
- [ ] Aesthetic and minimalist design (every element earns its place)
- [ ] Help users recognize, diagnose, recover from errors
- [ ] Help and documentation (searchable, task-focused)

**Severity Rating:**
- 0 = Not a problem | 1 = Cosmetic | 2 = Minor | 3 = Major | 4 = Catastrophic

**Common Mistakes to Flag:**
- [ ] Mystery meat navigation (icons without labels)
- [ ] Too many choices (decision paralysis)
- [ ] No "you are here" indicator
- [ ] No inline validation
- [ ] Wall of text
- [ ] Hover-only information
- [ ] Poor error messages
- [ ] Low contrast text
- [ ] Inconsistent nav location
- [ ] Broken back button

#### Review C: Accessibility Audit (accessibility checklist + design-system)
Run the complete accessibility checklist:

- [ ] `html lang` attribute present
- [ ] All images have `alt` attributes
- [ ] Every input has associated `<label>`
- [ ] Form errors use `aria-invalid` + `aria-describedby`
- [ ] All interactive elements keyboard accessible
- [ ] No `tabindex` > 0
- [ ] Links have descriptive text
- [ ] Headings hierarchical, no skips
- [ ] All ARIA reference IDs exist
- [ ] No prohibited ARIA patterns
- [ ] Focus management for dynamic content
- [ ] Live regions use correct `aria-live` value
- [ ] Color contrast meets WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Form field borders meet 3:1
- [ ] Focus indicators visible and meet 3:1
- [ ] Icon-only buttons have `aria-label`
- [ ] Interactive elements have keyboard handlers
- [ ] `<button>` for actions, `<a>` for navigation
- [ ] `aria-live="polite"` for async updates
- [ ] Semantic HTML before ARIA
- [ ] Headings hierarchical with skip link
- [ ] `scroll-margin-top` on heading anchors
- [ ] `focus-visible` rings on interactive elements
- [ ] Never `outline: none` without replacement
- [ ] `prefers-reduced-motion` honored
- [ ] `overscroll-behavior: contain` in modals

#### Review D: Technical Quality (design-system + coding-standards + motion-foundations)
- [ ] Images have explicit `width` and `height`
- [ ] Below-fold images: `loading="lazy"`
- [ ] Above-fold images: `priority` or `fetchpriority="high"`
- [ ] Large lists (>50 items): virtualized
- [ ] No layout reads in render (`getBoundingClientRect`, etc.)
- [ ] Prefer uncontrolled inputs; controlled must be cheap
- [ ] `<link rel="preconnect">` for CDN domains
- [ ] Critical fonts preloaded with `font-display: swap`
- [ ] Hydration-safe inputs (`value` + `onChange` or `defaultValue`)
- [ ] Dates/numbers use `Intl.*` APIs, not hardcoded
- [ ] Brand names have `translate="no"`
- [ ] `user-scalable=no` NOT used
- [ ] No inline `onClick` navigation without `<a>`
- [ ] No large arrays `.map()` without virtualization
- [ ] **Animation Performance:**
  - [ ] No interleaved layout reads/writes
  - [ ] No layout animation on large surfaces
  - [ ] No scroll-driven animation from scroll events
  - [ ] No rAF loops without stop condition
  - [ ] No multiple animation systems mixing
  - [ ] `transform` and `opacity` only for continuous motion
  - [ ] Blur <=8px, only short one-time effects
  - [ ] Scroll-linked motion uses Scroll/View Timelines
  - [ ] Animations paused when off-screen

---

### Phase 4: Optimization & Polish
**Goal:** Elevate from good to exceptional

#### Polish Checklist:
- [ ] **Typography refinements**: Kerning, line-height, letter-spacing tuned
- [ ] **Micro-interactions**: Hover states, transitions, feedback animations
- [ ] **Loading states**: Skeleton screens, spinners, progress indicators
- [ ] **Empty states**: Designed, not afterthoughts
- [ ] **Error states**: Helpful, specific, actionable
- [ ] **Responsive behavior**: Tested at all breakpoints
- [ ] **Dark mode**: Fully implemented and tested
- [ ] **Performance**: No jank, smooth 60fps animations
- [ ] **Copy polish**: Every word earns its place, active voice, specific labels
- [ ] **Edge cases**: Long content, empty data, network errors

#### Final Questions:
- Would I be proud to show this to a designer?
- Does every element earn its place?
- Is the core action completable in < 60 seconds?
- Would users know where they are without thinking?
- Can someone use this with only a keyboard?
- Does it work with screen readers?
- Is motion respectful of user preferences?
- Are animations smooth at 60fps?

---

## Skill Invocation Reference

### When to Invoke Which Skill

| Situation | Primary Skill | Supporting Skills |
|-----------|--------------|-------------------|
| "Design a landing page" | **frontend-design-3-0.1.0** | ui-design-review, design-system |
| "Make this look better" | **frontend-design-3-0.1.0** | design-system |
| "Review my UI code" | **coding-standards** | ui-design-review, design-system |
| "Check accessibility" | **design-system** | coding-standards |
| "UX audit" | **ui-design-review** | design-system |
| "Add animations" | **motion-patterns** | motion-foundations, motion-advanced |
| "Animation is janky" | **motion-foundations** | motion-patterns |
| "Design a dashboard" | **frontend-design-3-0.1.0** | frontend-design-direction, ui-design-review |
| "Build a form" | **frontend-design-direction** | design-system, coding-standards |
| "Create a component" | **frontend-design-direction** | frontend-design-3-0.1.0, design-system |
| "Improve engagement" | **product-lens** | ui-design-review |
| "Polish the UI" | **vibe-design-workflow** (this skill) | All design skills |

### Quick Decision Tree

```
User asks for UI/UX work
        │
        ▼
┌───────────────────┐
│ Is this NEW design?│
└───────────────────┘
   │              │
  YES            NO
   │              │
   ▼              ▼
┌──────────┐  ┌─────────────────┐
│ Phase 1  │  │ Is this REVIEW? │
│ STRATEGY │  └─────────────────┘
│          │     │            │
│ Define   │    YES          NO
│ aesthetic│     │            │
│ direction│     ▼            ▼
└──────────┘  ┌────────┐  ┌──────────┐
       │      │ Phase 3│  │ Phase 4  │
       ▼      │ REVIEW │  │ OPTIMIZE │
┌──────────┐  └────────┘  └──────────┘
│ Phase 2  │       │            │
│ IMPLEMENT│       ▼            ▼
└──────────┘  ┌────────────┐  ┌──────────┐
       │      │ usability  │  │ polish   │
       ▼      │ a11y       │  │ refine   │
┌──────────┐  │ technical  │  │ finalize │
│ Phase 3  │  └────────────┘  └──────────┘
│ REVIEW   │
└──────────┘
       │
       ▼
┌──────────┐
│ Phase 4  │
│ OPTIMIZE │
└──────────┘
```

---

## Anti-Patterns (Never Do These)

### Visual Design
- ❌ Generic AI aesthetics (purple gradients, Inter font, glassmorphism)
- ❌ Cliched color schemes without context
- ❌ Predictable layouts and component patterns
- ❌ Cookie-cutter design lacking character
- ❌ `transition: all`
- ❌ `outline: none` without replacement

### UX
- ❌ Mystery meat navigation (icons without labels)
- ❌ Too many choices causing decision paralysis
- ❌ No "you are here" indicator
- ❌ Wall of text
- ❌ Hover-only critical information
- ❌ Broken back button
- ❌ Forced continuity or roach motel patterns

### Accessibility
- ❌ `role="button"` on actual `<button>`
- ❌ `aria-label` on non-interactive elements
- ❌ Missing `alt` on images
- ❌ Form inputs without labels
- ❌ `tabindex` > 0
- ❌ Keyboard traps
- ❌ Low contrast text (< 4.5:1)
- ❌ Missing focus indicators

### Technical
- ❌ Layout reads during render
- ❌ Images without dimensions
- ❌ Large arrays without virtualization
- ❌ Blocking paste on inputs
- ❌ `autoFocus` on mobile
- ❌ Hardcoded date/number formats
- ❌ `user-scalable=no`
- ❌ Inline `onClick` navigation without `<a>`

### Animation Performance
- ❌ Interleaved layout reads/writes
- ❌ Layout animation on large surfaces
- ❌ Scroll-driven animation from scroll events
- ❌ rAF loops without stop condition
- ❌ Multiple animation systems mixing
- ❌ Animating blur continuously
- ❌ Blur on large surfaces
- ❌ `transition: all`

---

## Design Quality Scorecard

Rate each project 1-10:

| Dimension | Weight | Score |
|-----------|--------|-------|
| **Visual Distinctiveness** | 20% | /10 |
| **Usability** | 25% | /10 |
| **Accessibility** | 20% | /10 |
| **Technical Quality** | 15% | /10 |
| **Motion & Polish** | 10% | /10 |
| **Copy & Content** | 10% | /10 |
| **TOTAL** | 100% | /10 |

**Pass threshold:** 7.5/10 minimum for production
**Exceptional:** 9.0/10+

---

## Example Workflow

### Scenario: "Build a signup page"

**Phase 1 — Strategy:**
> "A playful, approachable signup for a creative tool. Maximalist with bold colors and unexpected shapes. Tone: friendly but professional. Core action: complete signup in under 30 seconds. Variable reward: instant preview of personalized dashboard."

**Phase 2 — Implementation:**
- Typography: Display font = Space Grotesk (wait, frontend-design-3-0.1.0 says avoid overused... use Cabinet Grotesk instead), Body = Satoshi
- Colors: Electric coral (#FF4D6D) + deep navy (#0A192F) + warm cream (#FFF8F0)
- Layout: Asymmetric split, left side illustration, right side form
- Animation: Staggered entrance, bouncy button micro-interaction
- Accessibility: Semantic form, focus rings, error handling with `aria-describedby`

**Phase 3 — Review:**
- Usability: Score 8/10 — clear labels, single primary CTA, progress not needed for simple form
- Accessibility: All checklist items pass, contrast 7.2:1
- Technical: Images sized, no layout reads, form uses correct input types

**Phase 4 — Polish:**
- Add loading state with playful animation
- Refine error copy to be specific ("Email looks incomplete" not "Invalid")
- Add `prefers-reduced-motion` variant
- Test keyboard-only navigation

---

## Resources

### Design Skills (Invoke These)
- `frontend-design-3-0.1.0` — Aesthetic direction and visual design
- `frontend-design-direction` — Design direction and vision
- `ui-design-review` — Usability evaluation framework
- `product-lens` — Engagement and product thinking
- `design-system` — Visual consistency and component standards
- `coding-standards` — Technical design rules and review
- `motion-foundations` — Animation tokens and performance
- `motion-patterns` — Animation implementation patterns
- `motion-advanced` — Advanced animation techniques

### Reference Libraries
- [Refactoring UI](https://refactoringui.com/) — Visual design principles
- [Don't Make Me Think](https://sensible.com/dont-make-me-think/) — Usability fundamentals
- [Hooked](https://www.nirandfar.com/hooked) — Habit-forming products
- [WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/) — Accessibility standards
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) — Accessible component patterns

---

## Summary

**The Vibe Coding Design Workflow ensures:**
1. ✅ Every design starts with intention and strategy
2. ✅ Visual output is distinctive, not generic
3. ✅ Usability is evaluated systematically
4. ✅ Accessibility is non-negotiable
5. ✅ Technical quality meets production standards
6. ✅ Animation performance is optimized
7. ✅ Polish elevates good to exceptional

**Golden Rule:** If you wouldn't proudly show it to a designer, it's not done.

**Remember:** Claude is capable of extraordinary creative work. Don't hold back — commit fully to a distinctive vision and execute with precision.
