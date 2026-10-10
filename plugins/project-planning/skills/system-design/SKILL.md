---
name: system-design
description: Shape a high-level system design for a large or semi-ambiguous project by drafting it with flagged assumptions, then iterating with the user until they agree. Covers goals, scope and out-of-scope, functional and non-functional requirements, focus areas, key entities and data model, architecture, interfaces, technology direction, verification, and a ranked risk register. Tuned for Apple-platform apps (macOS, iOS, iPadOS, visionOS). Use whenever the user wants to start a new app, tool, or system from a vague idea ("make an app that...", "I want to build...", "help me think through the design of..."), asks for a system design, requirements, or architecture overview before any code exists, or says a project is too big or fuzzy to start. Use it even if they do not say "system design". Not for small, well-specified changes; use decision-driven-design when extending an existing system.
license: GPL-3.0-or-later
---

# System Design

Turn a vague project idea into a short, agreed, high-level design that is concrete enough to guide technical direction and honest about what is still unknown. The design is the input to a roadmap; its most valuable output is the **risk register**, because the roadmap is built from it.

Stay high level. Name the framework, pattern, or boundary and why, not class diagrams or full schemas. Add detail only where a wrong choice would be expensive to undo or where it decides a risk.

Read [design-template.md](references/design-template.md) before drafting; it defines each section and the file layout. When the project targets an Apple platform, or the platform is undecided and Apple is plausible, also read [apple-platforms.md](references/apple-platforms.md). It holds the platform defaults, decision points, and risks that Apple projects usually need.

## Workflow

### 1. Inspect before asking

Read the workspace for existing code, project rules, a docs directory, and earlier design files. Do not ask for anything you can discover. Find `DocDir`, the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one).

### 2. Draft the whole design in one pass

Write a complete first draft of every section from the idea alone. A draft the user can react to is faster and more reliable than a questionnaire, because people find it easier to correct a concrete proposal than to specify one from nothing.

Make assumptions where you must, but never silently. Every assumption gets an ID (`A1`, `A2`, ...) and is marked `assumed` until the user confirms it. Pick defaults you would defend: the simplest option that fits the stated idea, using the platform's native tools. When you suggest a technology, give a one-line reason and the main alternative you rejected.

Save the draft to `<DocDir>/Design-<Topic>.md`, where `Topic` is a short 2–3 word Snake_Case name such as `Sudoku_Printer`. The user may override `DocDir`, `Topic`, or the path. State the path. If the file exists, read it and continue from it instead of overwriting.

### 3. Ask the few questions that matter

After the draft, ask 3–5 questions, no more. Choose the ones where the answer would change the architecture, the scope, or the top risks. Skip anything with an obvious default; those stay as flagged assumptions the user can overturn later.

Good questions are about:
- who the users are and the one thing the project must do well,
- hard constraints (platform and minimum OS, distribution, offline, budget, existing code),
- scope boundaries the draft had to guess at,
- the user's own priorities when two goals conflict.

If a structured question tool is available, use it: put your recommended option first and say what it implies. Otherwise ask in plain markdown with a recommendation for each. Never ask a question whose answer you could state as a confident default.

### 4. Iterate to agreement

After each answer, update the file: change the section, move the assumption to `confirmed`, log the decision, and say in a line or two what changed downstream. When a change invalidates other parts of the design, fix them in the same edit instead of leaving the document inconsistent. Offer new suggestions where the conversation opened a gap, but keep proposing rather than interrogating.

Keep focus areas honest. Name the one to three parts that make or break the project and give them the most depth; deliberately leave the rest thin.

### 5. Confirm and hand off

The design is ready when:
- every must-have requirement and every major decision is `accepted` or `deferred` with a reason,
- no assumption that affects architecture is still `assumed`,
- out-of-scope is explicit,
- the risk register is ranked and each top risk says how it could be answered cheaply,
- the user has said, in so many words, that it is good enough to plan from.

Ask for that sign-off explicitly, summarize the top three risks, and suggest the `risk-first-roadmap` skill as the next step. Do not start building.

## Judgment calls

- **Depth follows risk.** A well-understood part (a settings screen) gets one line. A part nobody has proven (a puzzle generator, a rendering pipeline, a sync protocol) gets a section and a risk entry.
- **Non-functional requirements are only the ones that constrain this project.** Print fidelity matters for a printable-puzzle app; internationalization may not yet. A generic checklist adds noise.
- **Out-of-scope is a feature.** It protects the roadmap from drifting. Split it into *out* (not this project) and *later* (wanted, not now), so deferred ideas are not lost.
- **Be honest about unknowns.** If you do not know whether a framework can do something, say so and put it in the risk register instead of asserting it. Mark platform facts you are not sure of as "verify against current docs".
- **Do not invent requirements to look thorough.** A short design for a small project is correct.
- If the project is not an Apple-platform one, skip apple-platforms.md and apply the same method with that platform's norms.
