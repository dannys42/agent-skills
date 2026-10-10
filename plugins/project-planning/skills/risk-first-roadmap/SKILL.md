---
name: risk-first-roadmap
description: Turn a system design or a vague project idea into a roadmap of small end-to-end increments, each one a working, observable capability that answers the riskiest remaining unknown. Orders work by risk instead of by layer, so the project proves its hardest assumptions first and keeps a runnable app at every step. Tuned for Apple-platform apps. Use whenever the user wants a roadmap, build order, milestones, or "what should I build first" for a new or large project, has just finished a system design (Design-*.md), or says a project is too big to know where to start. Also use to re-plan an existing roadmap after an increment taught something new. Not for breaking one increment into tasks (use tasklist) or for product-strategy roadmaps with stakeholders and quarters.
license: GPL-3.0-or-later
---

# Risk-First Roadmap

Build the project as a ladder of increments. Each rung is a complete, end-to-end slice that runs and can be seen, and each rung exists to **answer the riskiest unknown you can answer from where you are now**. Early rungs prove that the project is possible; later rungs make it complete. Failing a rung early is cheap, which is the point.

Read [roadmap-example.md](references/roadmap-example.md) before writing the first rung. It shows the format and a worked ladder. For Apple-platform projects also read [apple-rungs.md](references/apple-rungs.md).

## Input

Look for the system design: `<DocDir>/Design-<Topic>.md`, where `DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one). Read its risk register, focus areas, scope, and verification strategy.

If no design exists, say so and offer two paths: run the `system-design` skill first (best when the project is large or the unknowns are many), or build a short risk list with the user right now (fine for a small project). Do not invent a roadmap from nothing; the ordering is only as good as the list of unknowns.

## How to order the rungs

1. **List the unknowns.** Take the risk register and add anything the design missed. For each, write the cheapest experiment that would answer it, expressed as something that visibly works.
2. **Find what each one needs.** An experiment depends on things existing: a running app before you can draw, a canvas before you can test fonts. These dependencies are what force an order.
3. **Pick the next rung.** Among unknowns whose prerequisites already exist, choose the one with the highest impact × uncertainty, and take the smallest slice that answers it. If its prerequisites do not exist, the next rung is the cheapest slice that builds them.
4. **Always start with the walking skeleton.** The first rung is the most basic version of the product that builds, runs, and shows something. Its question is "can I build and run the most basic thing at all?"
5. **Tie-break** toward the rung that unlocks the most later rungs, then toward the cheaper one.
6. **Repeat** until the remaining rungs are low-risk completion work (more of what is proven), then stop being precise about them.

A sound ladder reads like a series of questions: can I run an app, can I draw, can I control the drawing finely, can I produce the core logic, can I see its result, can I scale it. Reordering these should feel wrong because each one needs the last.

## Write each rung

Use this shape, and keep it short:

```markdown
### R3: Control text rendering in the grid
Question: Do fonts, size, color, and style render legibly at screen and print scale?
Slice: Draw digits 1–9 in the fixed grid with chosen font and weight; export a PDF.
Done when: The PDF opens with crisp, correctly sized digits, and a printed page is readable.
De-risks: R2 (text fidelity)
Depends on: R2
If no: Try a different font stack or draw digits as paths; record in the design.
Status: planned
```

- **Question** is the unknown, phrased so the rung can fail.
- **Slice** is what the user can run and see. If you cannot demo it, it is not a rung.
- **Done when** is observable and checkable, with the command or action to check it.
- **De-risks** links to the risk IDs, so the register shrinks as rungs complete.
- **If no** is the fallback or the decision to revisit. A rung that cannot fail is not testing anything.

## Detail horizon

Write the first three or four rungs in full. List the rest as one-line **horizon** items in rough order, with no slice or done-when yet. Later rungs depend on what earlier ones teach, so detailing them now creates false confidence and waste. Expand a horizon item only when it becomes next.

## Check the ladder before showing it

Fix these smells first:

- **Layer-by-layer rungs** ("build the data model", then "build the UI", then "add persistence"). These deliver nothing visible and defer risk. Slice vertically instead.
- **A rung nobody can see run.** Add the thinnest visible output, even a log line or a plain list.
- **A rung that answers two unknowns.** Split it, so a failure points at one cause.
- **Polish before proof.** Styling, settings, and onboarding come after the core risks are retired.
- **Setup rungs with no demo** ("configure CI", "set up architecture"). Fold setup into the first rung that needs it.
- **A big unknown buried late** because its prerequisite looked expensive. Pull it forward by building the cheapest stand-in for the prerequisite.

## Review with the user

Show the ladder first as a short numbered list of one-line questions, so the order is easy to judge, and the detail for the first rungs after. Explain the ordering by naming the risk each early rung buys down. Invite changes: the user may know something about risk that the design does not. When they reorder, re-check dependencies, update, and tell them what the change does to the early risk exposure.

Save to `<DocDir>/Roadmap-<Topic>.md`, using the same `Topic` as the design. State the path. If the file exists, read it and continue its IDs. IDs (`R1`, `R2`, ...) are document-wide, never reused or renumbered, even when a rung is dropped or split.

## Hand off to implementation

A roadmap is not a task list. When the user is ready to build the next rung, expand just that one into tasks. If the `tasklist` skill is available, use it to write `<DocDir>/TODO-<Topic>.md` for that rung, citing the rung ID, and `tasklist-run` to execute it. Do not pre-expand later rungs.

## Re-plan after each rung

After a rung finishes, update the roadmap before starting the next:

- Set its status (`done`, `failed`, `changed`) and record what was learned in one or two lines, including the measured answer to its question.
- Update the design's risk register and decision log if the answer changed them.
- Re-rank the remaining risks and promote or demote horizon items. Add new rungs for newly discovered unknowns; mark rungs that became unnecessary `obsolete` instead of deleting them.
- Tell the user what moved and why.

Statuses: `planned`, `in progress`, `done`, `failed` (answered "no", fallback taken), `changed`, `obsolete`, `deferred`.
