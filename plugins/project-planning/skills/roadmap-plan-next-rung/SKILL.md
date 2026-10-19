---
name: roadmap-plan-next-rung
description: Plan one rung of a risk-first roadmap just before building it. Writes a short rung design brief that deepens the system design only where this rung needs it (scope for the rung, requirements touched, components and interfaces with a highlighted diagram, open decisions, verification, guard rails, fold-back list), agrees it with the user, updates each design doc it touches (creating a subsystem doc only when a piece warrants one), then hands off to tasklist. Also folds a finished rung back into the design so the docs match what was built. Use whenever the user says "plan the next rung", "design this rung", "start rung L3", "what do I build next and how", "design before the tasklist", or has a roadmap and wants to begin implementing the next increment, even if they do not name this skill. Use `close` after a rung's tasks are done: it folds the rung back, runs its retrospective and re-plans the roadmap in one step (it offers a code-quality tidy of the rung's files first), and `retro` for the retrospective alone. `/rung` picks the step. Not for whole-system design (use system-design) or for ordering rungs (use risk-first-roadmap).
license: GPL-3.0-or-later
model: opus
---

# Roadmap: Plan the Next Rung

The system design starts as a thin outline on purpose: designing every component before the first rung runs produces detail that the early rungs then prove wrong. This skill adds design depth one rung at a time, just before that rung is built, and only for the parts the rung touches. After the rung, it folds what was built back into the design so the next rung starts from the truth.

Depth follows the rung, not completeness. Never design a component the rung does not touch, and never open a subsystem doc the rung does not touch.

Read [rung-brief-template.md](references/rung-brief-template.md) before drafting, [diagrams.md](references/diagrams.md) before drawing, and [presenting-for-review.md](references/presenting-for-review.md) before asking the user to rule on anything. Read the system-design skill's [subsystems.md](../system-design/references/subsystems.md) for when a piece gets its own design doc, how parent docs treat it, and how IDs are cited across docs.

## Invocation

- `/roadmap-plan-next-rung [L3]` plans a rung. With no ID, take the first rung in ladder order whose status is `in progress`, else the first `planned` one, and say which you chose.
- `/roadmap-plan-next-rung close [L3]` (alias: `fold-back`) closes a finished rung: fold-back, retrospective and re-plan (see [Close a rung](#close-a-rung)). Offer this unprompted when the rung's tasklist is fully closed or the user says the rung is done.
- `/roadmap-plan-next-rung retro [L3]` writes the rung's retrospective: design, run and quality pass in one report (see [Retrospective](#retrospective)).
- `/rung` chooses among these from the files on disk.

## Files

`DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one).

```
<DocDir>/Roadmap-<Topic>.md                          the ladder (risk-first-roadmap)
<DocDir>/SystemDesign/Overview.md                    thin whole-system outline (system-design)
<DocDir>/SystemDesign/<Subsystem>.md                 a subsystem's own design, same shape (system-design)
<DocDir>/SystemDesign/Rung-<RungId>-<ShortRungDescription>.md   this skill's brief
<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md            the rung's tasks (tasklist)
```

`ShortRungDescription` is 2–4 Snake_Case words from the rung title, the same in the brief and the tasklist (`Rung-L3-Grid_Text_Rendering.md`, `Tasklist-L3-Grid_Text_Rendering.md`). If the brief exists, read it and continue instead of overwriting.

IDs (`A`, `D`, `R`, `Q`, `FR`, `NFR`) are per document, never reused or renumbered. The brief cites design-doc IDs qualified by doc name (`Overview:FR2`, `Puzzle_Generator:R1`); its own rung-local decisions and assumptions use bare IDs local to the brief.

## Plan a rung

### 1. Inspect

Read the rung in the roadmap, the Overview, the subsystem docs for pieces the rung works inside, earlier rung briefs it depends on, and the current code for the touched components. Follow the `Parent:` chain only as far as the rung reaches. Do not ask for anything you can discover.

Read by section, not whole files. For the roadmap: the rung's ladder line and `###` section (`roadmap show <file> <RungId>`). For the Overview: its Components, the Decisions and Risks the rung names, and the Traceability rows for its requirements (`roadmap outline <Overview>`, then `roadmap section <Overview> <heading>`; the binary is `~/.cache/danny-agent-skills/bin/roadmap`; run the "Plan tool check" in the `risk-first-roadmap` skill first: it checks `roadmap --version` and installs the tool if it is missing or stale). Without it, `grep -n '^#'` and Read the line ranges. Read a whole file only when it is short or you are changing its structure. While reading, apply `risk-first-roadmap`'s "Tidy an existing roadmap or Overview" triggers once, and offer the pass before the brief if one fires.

- **No Overview?** Say so and offer to run the `system-design` skill in outline depth first (a few minutes for a small project). A legacy `<DocDir>/Design-<Topic>.md` can stand in; read it. Do not invent a system design inside a rung brief. If `system-design` is not installed, offer a minimal Overview skeleton instead (see [If a linked file or skill is missing](#if-a-linked-file-or-skill-is-missing)).
- **Rung still a one-line horizon item?** Write its question, slice, done-when, and if-no into the roadmap first, in the risk-first-roadmap rung format, and tell the user. That is the expansion the roadmap deferred until the rung became next.
- **Trivially small rung** (no open decisions, an obvious check, few components; decisions already recorded in a design or detail doc count as settled): say so in one line, skip the brief, and go straight to step 6. The tasklist's `Source:` then cites that doc.

### 2. Draft the whole brief in one pass

Fill every section of the template from what you read: Question and slice; Scope for this rung; Requirements touched; Design docs touched; Components and interfaces (with a diagram); Decisions; Verification; Guard rails for the task list; Fold-back. A concrete draft is faster to correct than a questionnaire. Where you must guess, propose the simplest default you would defend and flag it as an assumption (`A12 assumed`), never silently. When the guess is about an external system's behaviour or a property of real data (completeness, uniqueness, shape) and later tasks depend on it, check it now if a read-only look is cheap; otherwise the guard rails put one real call or query first, before those tasks, or say why not.

- Scope: name what is in this rung and what is out. Mention work that is in this version but not this rung only where it clarifies a boundary the task list could otherwise cross.
- Requirements: cite only the FR/NFR this rung touches, by qualified ID, and say what the rung proves of each.
- Design docs touched: each doc the rung changes, what changes in it, and depth before → after. A rung may span several subsystems.
- Components: list the ones the rung creates or changes, with the interface that crosses each touched boundary. Draw them highlighted, with only the neighbours needed for context. Draw a subsystem as one box, or, when the rung works inside it, draw its inner components with the neighbours outside it as single boxes. For each touched boundary, also name anything it shares with other components (error codes, identifiers, formats) and whether to reuse or reconcile it, and for a new endpoint or entry point, what it does when its input or configuration is absent.
- Decisions: a trivial or reversible one gets a proposed default and an assumption ID. One that is major (it shapes persistence, a public interface, migration, or work beyond this rung) and has real alternatives goes through the `decision-driven-design` skill, scoped to this rung; record its outcome here and in the design doc it belongs to.

### 3. Ask the few questions that matter

Ask at most 3–5 questions, only those whose answers would change the slice, the components touched, or a boundary. Put your recommended option first and say what it implies. If a structured question tool is available, use it. Everything else stays a flagged assumption the user can overturn.

Present them in the shape in [presenting-for-review.md](references/presenting-for-review.md): the questions, and any assumption or decision in the brief that is high impact or low confidence (an unchecked claim about an external system or real data counts as low confidence), go under "Needs your attention" with options and a pro and con for each; the rest of the brief's assumptions follow in one short list with their defaults.

### 4. Iterate until the user says it is good enough

After each answer, update the brief, move assumptions to `confirmed`, and fix anything the change invalidated in the same edit. Stop when the user says the brief is good enough to build from; set `Status: agreed (<date>)`. A brief is a means to a good rung, not a deliverable to polish.

### 5. Update the living design

Before handing off, make the agreed brief true in each design doc it touches, and only those:

- In each touched doc: depth tags `sketched → designed` for the components this brief designed, new components or edges in its diagram, decisions that change that doc's shape in its decision log, and its traceability table if requirements moved.
- A parent changes only when a subsystem's Contract changes (interface, allocated requirements, a risk that crosses the boundary). A change inside a subsystem edits only the subsystem's doc.
- When the rung must design a piece's internals and that piece meets a subsystem trigger but has no doc (`Doc: pending` or `none`), create its doc with the system-design skill's subsystem mode: outline only, just what this rung needs, in the standard shape. Do not grow the parent with those internals. A piece that meets no trigger stays a row, and its detail stays in this brief.

### 6. Hand off to the task list

Use the `tasklist` skill to write `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`, with `Source:` citing the rung ID and the brief. The brief's verification items become `Done when` checks, its guard rails become `Context` or `Non-goals` lines, and its decision IDs are cited in `Context`. Set the rung's roadmap status to `in progress`, and write `Base: <git rev-parse --short HEAD>` under the brief's `Status:` line (no brief: in the tasklist's `Source:` line), so fold-back and the tidy pass can diff the rung's work. End with the next step, as `Next: /rung → run <RungId> (<Model>: /model <alias>)`, on the orchestrator model from `tasklist-run`'s "Orchestrator model" (Sonnet 5.5, or Opus 5.5 when the list has `heavy` tasks; subagents still follow each task's `Model`); then `/rung` again closes the rung when the tasks are done. Log it as a `step` event (fields in `tasklist-run`'s metrics log).

## Rung 1 and build boundaries

When the Overview implies more than one build boundary that rung 1 must create (separate executables, a shared package, enforced layering between modules), rung 1's brief adds a **Build targets** section: each target, its allowed imports, and its build and test commands, drawn in the brief's diagram. Gate rung 1's implementation on the owner approving the brief, because the target layout is expensive to change later. With a single app target (a test target or one local package does not count), say so in one line. Each target is a subsystem candidate, but rung 1 only needs its boundary and Contract in the parent, not its own doc.

## Close a rung

Run after a rung's tasks are closed. It folds the rung back, runs the retrospective and re-plans the roadmap.

0. **Quality step.** Run `metrics signals --base <Base>` (or `--tasklist <the rung's tasklist>` when there is no `Base:`; see the `code-quality-pass` skill's "Metrics tool check"). Then offer, in one line, a tidy of the rung's files (`/code-quality-pass tidy <RungId>`): run, skip or defer. Run it first when accepted, because renames change what the docs below must name. If `<DocDir>/Quality/Status.md` exists, append the rung to `Since review:` and any fired trigger names to `Triggers pending:`; if it does not, the signals print a `no-baseline` line, which is the whole nudge. Never wait on this step.
1. Read the brief and the design docs it lists as touched (no brief, because the rung skipped it: compare against the doc the tasklist's `Source:` cites and the tasklist, and skip step 5's status), the rung's tasklist (in `<DocDir>/` or `<DocDir>/Completed/`), the commits for its tasks, and the code for the touched components.
2. Compare the brief with what was built: components, interfaces, decisions, assumptions, verification results.
3. Fix whichever side is wrong. When the code is right and the design was a guess, update the docs. When the code drifted for a bad reason, leave the docs and add a task to the tasklist, or propose a rung, to close the gap. Record each drift as a decision.
4. Update each touched design doc to as-built: depth tags `designed → built` for components the rung verified, diagram, decision log, assumptions (`confirmed` or refuted with what replaced them), risk register (retire what the rung answered, add what it uncovered), and traceability status in the doc that owns each requirement. Update a parent only where a Contract changed, or an allocated requirement is now fully proven, or to tag a subsystem box `built` once its doc's components are verified. Keep each decision, risk and traceability cell to one line (under about 400 characters) and link the brief for the reasoning. Work through the brief's fold-back list and tick each item.
5. Set the brief's status to `folded back (<date>)`, with a short "As built" note for each difference.
6. Tell the user what moved and why. Start the retrospective in a background subagent on Sonnet: its prompt names the RungId, tells it to follow [retrospective.md](references/retrospective.md) (give the absolute path of this skill's reference) and return only the report, applying nothing. If comparing the code showed a third or fourth copy of one shape (types or files that differ only in their subject), say so in the "As built" note and add `shape` to `Triggers pending:`.
7. Re-plan: follow `risk-first-roadmap`'s "Re-plan after each rung" (invoke the skill, or without it update the rung's roadmap status to `done`/`failed`/`changed` and the learning log by hand), which sets the rung's status and names the next rung. Inside close, the re-plan neither prints its `Next:` line nor logs its `step` event; step 8 does both once.
8. When the retro returns, show it after the re-plan summary, then end with `Next: /rung → plan <next rung ID> (Opus: /model opus)`. Log one `step` event for close, with `skill`, `model`, `target` (the RungId), `drift`, `next` and `next_model`.
9. If the session is long or the user stops after fold-back, say `/rung` picks up at the re-plan (the tool reports `replan` when the brief is folded back but the rung is still in progress).

After the first end-to-end data rung, widen step 2 to every affected design doc as a whole (the Overview and each subsystem the data passed through), not just the touched components, because that is where the early sketch most often diverges from reality.

## Retrospective

`retro [L3]`, or run inside close. One report for the whole rung: its design, its `tasklist-run` runs and its quality pass. Follow [retrospective.md](references/retrospective.md): build it from the brief, the touched design docs, the rung's tasklist, git history and `metrics summary <rung tasklist>`, not from memory; the standard short format, ending in one project-neutral feedback block for `/retro-feedback` (items tagged by plugin), or one line if nothing stands out. Apply nothing.

## If a linked file or skill is missing

This skill links to the `system-design` skill's references and hands off to `tasklist` and `decision-driven-design` (`task-workflow` plugin). When one is absent, do not stop: use the minimum below, and say once, in one or two lines, what is missing, how to install it, and how to recover.

- Install: `claude plugin install project-planning@danny-sung-agent-skills` or `claude plugin install task-workflow@danny-sung-agent-skills`; with the open installer, `npx skills add dannys42/agent-skills --skill <skill-name>` into the same skills directory, so relative links resolve.
- Recover: re-run the skipped step once it is installed. Existing docs are read and continued, never overwritten.
- No `system-design` (and no Overview): offer a minimal Overview with Summary, Scope (in / later / out), Headline requirements, Components (diagram and a table with depth and `Doc`), Decisions, Assumptions, Risks (ranked, cheapest experiment), Traceability. Recover by running `/system-design` on it to normalize it. Without `subsystems.md`, keep to: edit only touched docs; a parent sees a subsystem as one box and changes only with its Contract; IDs per doc, qualified across docs.
- No `diagrams.md`: Mermaid `flowchart`, quote every label, labels are component names, one class per depth (`sketched` dashed, `designed` thin, `built` bold) plus `touched`.
- No `tasklist`: write the tasks as a plain checklist at `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`, each with an ID, `Needs`, and `Done when`, and say the tasklist skill gives the richer format. Recover by asking `tasklist` to convert it.
- No `decision-driven-design`: ask the decision questions inline, one at a time, recommended option first.
- No `presenting-for-review.md`: list high-impact or low-confidence items first, each with why, what would settle it, and two or three options with a pro and con, recommended first; then every other item with its default.

## Judgment calls

- **Untouched means undesigned.** A component that only appears as a neighbour keeps its depth tag and gets no new detail, and a subsystem the rung does not work inside stays one box: do not open its doc, however tempting.
- **Interfaces before internals.** At a touched boundary, decide what crosses it (types, calls, events, file formats). Internals stay with the implementer unless they decide a risk.
- **The brief is short.** About a page, tables of per-component changes included: one line per component, and leave out what the tasks will not cite. If it grows past two, the rung is probably two rungs; say so and suggest splitting it in the roadmap.
- **Do not re-plan the ladder here.** If planning shows the rung is in the wrong place or answers two unknowns, tell the user and suggest re-running `risk-first-roadmap`.
