---
name: system-design
description: Shape a high-level system design for a large or semi-ambiguous project as a living, incremental design. By default writes a one-page outline (summary and success criteria, version scope, headline requirements, focus areas, a component diagram with depth tags, decisions, assumptions, a ranked risk register, and requirement-to-rung traceability) by drafting it with flagged assumptions and iterating with the user, then deepens it only rung by rung later. Pieces that warrant it (a separate app, library, or service, or a major subsystem) get their own design doc of the same shape, which the parent treats as one component. Adopt mode documents an existing codebase as-is and records where it should head next; `retro` writes a retrospective for the skills' maintainer. Tuned for Apple-platform apps (macOS, iOS, iPadOS, visionOS). Use whenever the user wants to start a new app, tool, or system from a vague idea ("make an app that...", "I want to build...", "help me think through the design of..."), asks for a system design, requirements, or architecture overview, says a project is too big or fuzzy to start, or wants to "document the architecture of this project", "review the architecture", "adopt this codebase into the workflow", or decide "where this project is headed". Use it even if they do not say "system design". Not for small, well-specified changes; use decision-driven-design when extending one part of an existing system.
license: GPL-3.0-or-later
---

# System Design

Turn a vague project idea, or an existing codebase, into a short, agreed outline of the whole system that is concrete enough to order a roadmap and honest about what is still unknown. Its most valuable output is the **risk register**, because the roadmap is built from it.

Keep it thin and bounded. Designing every component up front produces detail that the first working rungs prove wrong, and a design doc that grows forever stops being read and stops being updated. The outline names components, boundaries, and the decisions that would be expensive to undo; the rest is designed later, one rung at a time, by the `roadmap-plan-next-rung` skill, just before that rung is built. When a piece needs a design of its own, it becomes a **subsystem** with its own doc, and every other doc treats it as one component.

Read [overview-template.md](references/overview-template.md) before drafting; it defines the file, each section, and the depth tags. Read [subsystems.md](references/subsystems.md) for when a piece warrants its own doc, how parent and child docs relate, and how IDs are cited across docs; use [subsystem-template.md](references/subsystem-template.md) to write one. For diagrams, follow [diagrams.md](../roadmap-plan-next-rung/references/diagrams.md) in the `roadmap-plan-next-rung` skill (Mermaid by default; node labels are the component names; one depth class per component). When the project targets an Apple platform, or the platform is undecided and Apple is plausible, also read [apple-platforms.md](references/apple-platforms.md).

## Layout and depth

```
<DocDir>/SystemDesign/
  Overview.md                                 this skill: the whole system, about one page
  <Subsystem>.md                              this skill, subsystem mode: one piece, same shape, Parent: header
  Rung-<RungId>-<ShortRungDescription>.md     per-rung brief (roadmap-plan-next-rung)
```

`DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one). The user may override any path.

- **Outline** (default): the Overview only. Use it for every new project unless the user asks for more.
- **Full**: the Overview plus the "deepen on demand" sections from the template, up front. Only when the user asks, or an outside party needs the whole design before any building starts.
- **Adopt**: an as-is Overview of an existing codebase (below).
- **Subsystem**: `/system-design <Subsystem>`, or when a rung promotes a piece. The same outline workflow scoped to one subsystem doc, starting from its Contract in the parent; afterwards the parent changes only for that box, its tag, and the Contract. Details in [subsystems.md](references/subsystems.md).
- **Retro**: `/system-design retro`, also offered after sign-off (see [Retrospective](#retrospective)).

A piece is a **subsystem** when it is a separate build target (app, library or package, extension, service, CLI), has its own lifecycle or owner, has its own requirements and risks that would clutter the parent, or has more than about five inner components. Otherwise it stays a row in its parent.

## Workflow

### 1. Inspect before asking

Read the workspace: code, project rules, the docs directory, and earlier design files. Do not ask for anything you can discover.

- `<DocDir>/SystemDesign/Overview.md` exists: read it and continue from it, keeping its IDs. IDs are per document; cite another doc's as `Puzzle_Generator:R1`.
- A legacy `<DocDir>/Design-<Topic>.md` exists: read it and offer to migrate it into `SystemDesign/Overview.md` (mapping in the template). Write the new file beside it; never overwrite or delete the legacy file.
- Substantial code exists and no design does: use adopt mode.

### 2. Draft the whole outline in one pass

Write a complete first draft of every Overview section from the idea alone: Summary with success criteria; Scope (in this version / later / out); Headline requirements; Focus areas; Components (diagram and a table with responsibility, depth, and `Doc`); Subsystems index; Decisions; Assumptions; Risks (ranked, with the cheapest experiment); Open questions; Traceability. A draft the user can react to is faster and more reliable than a questionnaire, because people find it easier to correct a concrete proposal than to specify one from nothing.

Make assumptions where you must, but never silently. Every assumption gets an ID (`A1`, `A2`, ...) and is marked `assumed` until the user confirms it. Pick defaults you would defend: the simplest option that fits the idea, using the platform's native tools. When you suggest a technology, give a one-line reason and the main alternative you rejected. Tag every component `sketched`. Start every component as a row; mark one `Doc: pending` when it already meets a subsystem trigger (a separate build target, for instance), but do not write subsystem docs now. They are written when a rung needs that piece's internals, or when the user asks.

Save to `<DocDir>/SystemDesign/Overview.md` and state the path. Also choose `Topic`, a short 2–3 word Snake_Case name such as `Sudoku_Printer`, and record the future roadmap path (`Roadmap-<Topic>.md`) in the Overview header so the roadmap uses the same name.

### 3. Ask the few questions that matter

After the draft, ask 3–5 questions, no more. Choose the ones where the answer would change the components, the scope, or the top risks: who the users are and the one thing the project must do well; hard constraints (platform and minimum OS, distribution, offline, budget, existing code); scope boundaries the draft had to guess; the user's priority when two goals conflict.

If a structured question tool is available, use it: put your recommended option first and say what it implies. Otherwise ask in plain markdown with a recommendation for each. Never ask a question whose answer you could state as a confident default.

### 4. Iterate to agreement

After each answer, update the file: change the section, move the assumption to `confirmed`, log the decision, and say in a line or two what changed downstream. Fix everything the change invalidates in the same edit. Keep proposing rather than interrogating.

Resist deepening. When the conversation dives into one component's internals, record the decision that matters, note the question with a `Q` ID, and leave the detail for the rung that builds it. If the piece clearly warrants its own design, note it as `Doc: pending` rather than growing this doc.

### 5. Confirm and hand off

The outline is ready when every must-have requirement and every decision that would be expensive to undo is `accepted` or `deferred` with a reason, no assumption that changes the components is still `assumed`, scope is explicit, and the risk register is ranked with a cheapest experiment for each top risk.

Ask the user whether it is good enough to start a roadmap, summarize the top three risks, and set `Status: agreed (<date>)`. Suggest the `risk-first-roadmap` skill next, and explain that detail arrives per rung through `/roadmap-plan-next-rung`. Do not start building. Then offer a retrospective.

## Adopt mode

For an existing project ("document the architecture of this project", "adopt this codebase into the workflow", "where is this project headed"). The goal is a truthful starting point, then a recorded direction.

1. **Inspect the code.** Build targets, packages and modules, entry points, persistence and file formats, external services, tests, existing docs, and recent history for the direction work has been taking.
2. **Draft the as-is Overview.** Derive the component diagram from the code: one node per real module, named as the code names it, edges for real dependencies. List each separate build target and major module as one component with `Doc: pending`; do not write their subsystem docs up front, but offer to adopt the one the user cares about first in subsystem mode. Tag components `built` when they exist and have tests or visible behaviour, `designed` when partly present, `sketched` when only planned. Infer requirements from behaviour and mark them `assumed`. Seed the risk register with what is fragile or unverified (untested areas, tangled dependencies, unproven platform claims). Set `Mode: as-is (adopted <date>)`.
3. **Review it with the user** until they agree it describes the system as it is. Correct the docs, not the code.
4. **Record the direction.** Ask where the project is headed. Record each desired change of direction as a decision of kind `shift`, stating from what to what and why, and mark the components it affects. Leave the as-is diagram as it is; shifts are planned work, not current fact.
5. **Hand off** to `risk-first-roadmap`, which must cover every accepted `shift` with a rung or horizon item.

## Retrospective

Offered after sign-off, or `retro` any time. Follow the `roadmap-plan-next-rung` skill's [retrospective.md](../roadmap-plan-next-rung/references/retrospective.md), built from the Overview, any subsystem docs written, and their git history, not from memory. Apply nothing. If that file is missing, give a few evidence lines (Overview length against about a page, questions asked and answers that changed the draft, assumptions overturned, subsystem rows marked `pending` and why), then one project-neutral fenced feedback block with skill versions from `../../.claude-plugin/plugin.json`, an evidence tier per point (`measured`, `observed`, `guess`), what to keep, suggested edits, and the closing line "In danny-agent-skills, run /roadmap-feedback and paste this block." If nothing stands out, say so in one line.

## If a linked file or skill is missing

This skill links to the `roadmap-plan-next-rung` skill's `diagrams.md` and `retrospective.md`, and hands off to `risk-first-roadmap`. When one is absent, do not stop: use the minimum here, and say once, in one or two lines, what is missing, how to install it (`claude plugin install project-planning@danny-sung-agent-skills`, or `npx skills add dannys42/agent-skills --skill <skill-name>` into the same skills directory so relative links resolve), and how to recover.

- No `diagrams.md`: Mermaid `flowchart`, quote every label, labels are the component names, one class per depth (`sketched` dashed, `designed` thin, `built` bold), subsystems as single boxes.
- No `risk-first-roadmap`: the agreed Overview is still the input; tell the user to install it and run it, and do not write a roadmap here.
- Recover: re-run the skipped step once installed. Existing docs are read and continued, never overwritten; re-check diagrams against the full rules.

## Judgment calls

- **Depth follows risk.** A well-understood part gets one line in the component table. A part nobody has proven (a puzzle generator, a rendering pipeline, a sync protocol) gets a focus area and a risk entry, not a design.
- **Non-functional requirements are only the ones that constrain this project.** Print fidelity matters for a printable-puzzle app; internationalization may not yet.
- **Scope is a feature.** It protects the roadmap from drifting. Split what is out into *later* (wanted, not this version) and *out* (not this project), so deferred ideas are not lost.
- **Be honest about unknowns.** If you do not know whether a framework can do something, say so and put it in the risk register. Mark platform facts you are unsure of as "verify against current docs".
- **Do not invent requirements to look thorough.** A short outline for a small project is correct.
- If the project is not an Apple-platform one, skip apple-platforms.md and apply the same method with that platform's norms.
