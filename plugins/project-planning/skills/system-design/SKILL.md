---
name: system-design
description: Agree a system design for a large or fuzzy project with its owner, starting from the owner's own vision doc or a first pass, and only as deep as the current milestone needs: subsystems, seams, data model, names, threat and privacy, decisions and ranked risks, each marked settled or working. Also adopts an existing codebase as-is, runs architecture checkpoints and writes a retro. Tuned for Apple-platform apps. Use when the user says "I want to build...", "make an app that...", "here's my vision, design it", asks for a system design, architecture or data model, says a project is too big or fuzzy to start, or wants to "adopt this codebase", "document the architecture" or "review the architecture". Not for small, well-specified changes (use decision-driven-design).
license: GPL-3.0-or-later
model: opus
---

# System Design

Agree, with the owner, the structure of a project (or of an existing codebase) that the current milestone will be built on: concrete enough to plan the milestone's work, honest about what is still unknown, and shaped so later milestones grow it by adding rather than restructuring. The owner sets the shape; the agent fills in, checks and proposes.

The system design is bounded by the current milestone, not by a page count. Agree structure, not internals: inside the agreed seams, internal types, algorithms, thresholds, output formats and UI detail are decided later, when milestone planning writes the rung briefs. Terms (system design, additive check, reviewable surfaces, `settled`/`working`, `owner`/`proposed`, milestone, first pillar, end-of-goal rule, provisional code, manual stand-in, owner preference) are defined in [terms.md](references/terms.md); use them as defined there.

Read [overview-template.md](references/overview-template.md) before drafting; it defines the file, each section, the marks and the depth tags. Read [subsystems.md](references/subsystems.md) for when a piece warrants its own doc and how IDs are cited across docs; use [subsystem-template.md](references/subsystem-template.md) to write one. For diagrams, follow [diagrams.md](../roadmap-plan-next-rung/references/diagrams.md) in the `roadmap-plan-next-rung` skill (Mermaid by default; node labels are the component names; one depth class per component). When the project targets an Apple platform, or the platform is undecided and Apple is plausible, also read [apple-platforms.md](references/apple-platforms.md).

## Layout and modes

```
<DocDir>/SystemDesign/
  Overview.md                                 this skill: the system design (the path stays Overview.md)
  <Subsystem>.md                              this skill, subsystem mode: one piece, same shape, Parent: header
  Rung-<RungId>-<ShortRungDescription>.md     per-rung brief (roadmap-plan-next-rung)
  Rung-<RungId>-Checkpoint.md                 a checkpoint's record (this skill, checkpoint mode)
```

`DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one). The user may override any path.

- **New** (default): the workflow below.
- **Adopt**: an as-is system design of an existing codebase (below).
- **Subsystem**: `/system-design <Subsystem>`, or when a rung promotes a piece. The same workflow scoped to one subsystem doc, starting from its Contract in the parent; afterwards the parent changes only for that box, its tag, and the Contract. Details in [subsystems.md](references/subsystems.md).
- **Checkpoint**: `/system-design checkpoint [L44]`, for a `Kind: checkpoint` rung that `risk-first-roadmap` placed; `/rung` routes here (below).
- **Retro**: `/system-design retro`, also offered after sign-off (see [Retrospective](#retrospective)).

A piece is a **subsystem** when it is a separate build target (app, library or package, extension, service, CLI), has its own lifecycle or owner, has its own requirements and risks that would clutter the parent, or has more than about five inner components. Otherwise it stays a row in its parent.

## Workflow

### 1. Inspect before asking

Read the workspace: code, the project rules file (`CLAUDE.md` or equivalent), the owner preferences file `~/.local/state/danny-agent-skills/owner-preferences.md` if it exists, `<DocDir>/Taxonomy.md`, the docs directory and earlier design files. Do not ask for anything you can discover.

- `<DocDir>/SystemDesign/Overview.md` exists: read it and continue from it, keeping its IDs. IDs are per document; cite another doc's as `Puzzle_Generator:R1`.
- A legacy `<DocDir>/Design-<Topic>.md` exists: read it and offer to migrate it into `SystemDesign/Overview.md` (mapping in the template). Write the new file beside it; never overwrite or delete the legacy file.
- Substantial code exists and no design does: use adopt mode.
- An owner document exists (a vision, goal or strategy doc the owner wrote): it is the starting point for step 2.

### 2. Start from the owner's sketch or a first pass

With an owner document, start from it and say which file you used. Without one, ask once: "Sketch it yourself, or shall I take a first pass?" A sketch the owner then gives (in chat or a file) is treated as an owner document. Either way, fill the gaps: an item taken from the owner's words is `owner`, an item you add is `proposed`. A first pass applies the owner preferences and project rules before anything else, otherwise picks defaults you would defend (the simplest option that fits, using the platform's native tools), and stops at the additive check like any system design. When you suggest a technology, give a one-line reason and the main alternative you rejected; name things by what they do (terms.md, "Names and labels").

### 3. Draft for the current milestone

Name the current milestone with an outcome sentence (for a new project, the first: foundation first, under the end-of-goal rule) and each later milestone in one line, `proposed` unless the owner's document gives them. Then draft, for the current milestone only, every section of the template: subsystems with their build targets, the seams and interfaces between them, the data model as entities and relationships, names, a short threat and privacy section (data handled, where it goes, secrets, trust boundaries), requirements that constrain the design, decisions, ranked risks with the cheapest experiment, open questions and traceability. Tag every component `sketched`; mark one `Doc: pending` when it already meets a subsystem trigger, but do not write subsystem docs now.

- **Field level only for reviewable surfaces**, and only for what this milestone builds. Write nothing about other internals.
- **Additive check** for each later milestone's line: if it can be added as new entities, endpoints or symbols, stop there; if not, decide that seam now as a decision, at the smallest depth that makes the later change additive.
- **Agreement marks:** propose `settled` or `working` for each item; a `working` item names what would make us revisit it.
- **Provisional code and manual stand-ins:** list each piece of kept spike code and each hand step the milestone relies on in its table (a new project usually has none).

### 4. Offer to tighten owner wording, then save

Each time the owner supplies wording (a sketch, a milestone outcome, an exit criterion, a name), offer once, before saving it, to tighten it: list each ambiguity (a vague term, a name not in or clashing with `Taxonomy.md`, an exit criterion nobody can check, a conflict with an agreed item) and show a tightened version beside the original. The owner accepts, edits or keeps the original. Never rewrite owner text silently. Then save to `<DocDir>/SystemDesign/Overview.md` and state the path. Choose `Topic`, a short 2–3 word Snake_Case name such as `Sudoku_Printer`, and record the future roadmap path (`Roadmap-<Topic>.md`) in the header so the roadmap uses the same name.

### 5. Review with the owner

Present the `proposed` items in the shape in [presenting-for-review.md](../roadmap-plan-next-rung/references/presenting-for-review.md). Show reviewable surfaces field by field; everything else at the level of subsystems, seams and entities, never field by field. Present the names as one item, reviewed as a set against `Taxonomy.md`. Ask only what would change the subsystems, seams, data model or the milestone's scope; never ask what you could state as a confident default.

### 6. Iterate to agreement

After each ruling, update the file: an item accepted unchanged loses `proposed` and keeps its `settled` or `working` mark; an item the owner wrote or edited is `owner`. Fix everything the change invalidates in the same edit, and say in a line or two what changed downstream. Keep proposing rather than interrogating. Resist deepening: when the conversation dives into internals, record the decision that matters and leave the detail for milestone planning. Minutiae (thresholds, exact output shape, polish, internal names) go on the "decide after it runs" list (terms.md): in the roadmap once it exists, until then under Open questions marked `after it runs`. A piece that clearly warrants its own design is marked `Doc: pending` rather than growing this doc.

### 7. Confirm and hand off

The system design is ready when nothing the current milestone builds is still `proposed`, every subsystem, seam, entity and reviewable surface it builds is `settled` or `working` (with a revisit note), every later milestone's line passes the additive check or has its seam decided, the threat and privacy section is filled, and the risk register is ranked with a cheapest experiment for each top risk. Then ask the owner whether it is good enough to plan the milestones, summarize the top three risks, and set `Status: agreed (<date>)`. Add the agreed names to `<DocDir>/Taxonomy.md` (create it if missing). Commit the system design (and any doc it created), staged by explicit path, as `System design: <project>`; every mode commits its agreed docs the same way, a checkpoint at its step 5. End with a plain sentence saying the next step orders the milestone's work by risk, then `Next: /rung (Opus: /model opus)`. Log it as a `step` event with `skill` `system-design 0.11.2` (other fields in `tasklist-run`'s metrics log). Do not start building. Then offer a retrospective.

## Adopt mode

For an existing project ("document the architecture of this project", "adopt this codebase into the workflow", "where is this project headed"). The goal is a truthful starting point, then a recorded direction.

1. **Inspect the code.** Build targets, packages and modules, entry points, persistence and file formats, external services, tests, existing docs, and recent history for the direction work has been taking.
2. **Draft the as-is Overview.** Derive the component diagram from the code: one node per real module, named as the code names it, edges for real dependencies. List each separate build target and major module as one component with `Doc: pending`; do not write their subsystem docs up front, but offer to adopt the one the user cares about first in subsystem mode. Tag components `built` when they exist and have tests or visible behaviour, `designed` when partly present, `sketched` when only planned. Infer requirements from behaviour and mark them `assumed`. Seed the risk register with what is fragile or unverified (untested areas, tangled dependencies, unproven platform claims). Set `Mode: as-is (adopted <date>)`.
3. **Review it with the user** until they agree it describes the system as it is, in the shape in [presenting-for-review.md](../roadmap-plan-next-rung/references/presenting-for-review.md): flag inferred requirements and component tags you are least sure of. Correct the docs, not the code.
4. **Record the direction.** Ask where the project is headed. Record each desired change of direction as a decision of kind `shift`, stating from what to what and why, and mark the components it affects. Leave the as-is diagram as it is; shifts are planned work, not current fact.
5. **Hand off** to `risk-first-roadmap` (next step: `/risk-first-roadmap` on Opus, `/model opus`), which must cover every accepted `shift` with a rung or horizon item.

## Checkpoint mode

A checkpoint asks whether the architecture that exists holds for the milestone ahead, before that milestone is built on it. `risk-first-roadmap` places checkpoint rungs; this mode runs one in a single session. With no ID, take the first `planned` or `in progress` rung whose section says `Kind: checkpoint`. Write the record to `SystemDesign/Rung-<RungId>-Checkpoint.md` (about a page) and set the rung `in progress`; if the record exists, continue it (with `Status: done`, go straight to step 5's re-plan).

1. **Look back.** Use a `code-quality-pass review` report written since the previous checkpoint (or since the first end-to-end run) if there is one. Otherwise run `/code-quality-pass review` now, with trigger `checkpoint`. Then compare the Overview and subsystem docs as a whole with the code, as adopt mode's step 2 does, and list each drift. If the design lives in more than one place (a legacy `Design-*.md` or `Architecture-*.md` beside the Overview), propose folding it into the Overview and subsystem docs, verbatim where it is still true.
2. **Look forward.** From the milestone's line, its Horizon items and its `ParkedIdeas-<Topic>.md` entries, list the components the milestone will add or change. For each one, ask whether the current shape holds: boundaries, data model and persistence, interfaces, shared names. Where it does not, write a proposal: a `refactor-rung` before the milestone's first feature rung, a decision, or a new `shape` unknown for the risk register. Name new components at `sketched` depth and no deeper; the rung briefs design them later.
3. **Present** the review's proposals, the drifts and the forward proposals as one list, in the shape in [presenting-for-review.md](../roadmap-plan-next-rung/references/presenting-for-review.md). For a refactor rung, the recommended option places it ahead of the milestone's first feature rung, because growing on a shape that will not hold is what the checkpoint exists to prevent.
4. **Apply** what the owner accepted: decisions in the Overview's decision log, diagram and depth tags, drifts fixed in whichever side is wrong (as fold-back does), a docs fold-in as a move-only commit, new risks in the register. Record the rulings in the review report so the re-plan finds them, and finish that review's steps 6 and 7 (conventions, fitness tests, `Status.md`, events).
5. **Close.** Set the record's `Status: done (<date>)`. Invoke `risk-first-roadmap`'s re-plan, which places accepted refactor rungs and tasks, sets the checkpoint rung `done` with a one-line learning-log entry (proposals accepted, deferred, rejected), and ends with the `Next:` line. Log a `step` event with `skill` `system-design 0.11.2`, `target` the RungId and `kind` `checkpoint`.

A checkpoint never blocks: the owner may skip it (see `rung`), and a proposal the owner defers stays in the review report for the next one.

## Retrospective

Offered after sign-off, or `retro` any time. Follow the `roadmap-plan-next-rung` skill's [retrospective.md](../roadmap-plan-next-rung/references/retrospective.md), built from the system design, any subsystem docs written, and their git history, not from memory. Apply nothing. If that file is missing, give a few evidence lines (detail written beyond what the current milestone needs, the share of `proposed` items the owner accepted unchanged, owner wording tightened or kept, subsystem rows marked `pending` and why), then one project-neutral fenced feedback block headed `retro feedback`, with skill versions from `../../.claude-plugin/plugin.json`, an evidence tier and a `[project-planning]` tag per point (`measured`, `observed`, `guess`), what to keep and suggested edits, preceded by the line "Paste this block into /retro-feedback in danny-agent-skills:". If nothing stands out, say so in one line.

## If a linked file or skill is missing

This skill links to the `roadmap-plan-next-rung` skill's `diagrams.md`, `retrospective.md` and `presenting-for-review.md`, and hands off to `risk-first-roadmap`. When one is absent, do not stop: use the minimum here, and say once, in one or two lines, what is missing, how to install it (`claude plugin install project-planning@danny-sung-agent-skills`, or `npx skills add dannys42/agent-skills --skill <skill-name>` into the same skills directory so relative links resolve), and how to recover.

- No `diagrams.md`: Mermaid `flowchart`, quote every label, labels are the component names, one class per depth (`sketched` dashed, `designed` thin, `built` bold), subsystems as single boxes.
- No `presenting-for-review.md`: group items as important (at most 5, hard to reverse or wide reach, costliest first), notable and small; give every decision two or three options with a plain example and a pro and con each, then a recommendation; end with one question asking for the important rulings and only the other items the owner would change.
- No `risk-first-roadmap`: the agreed system design is still the input; tell the user to install it and run it, and do not write a roadmap here.
- Recover: re-run the skipped step once installed. Existing docs are read and continued, never overwritten; re-check diagrams against the full rules.

## Judgment calls

- **Depth stops at the additive check.** A part nobody has proven (a generator, a rendering pipeline, a sync protocol) gets a risk entry with its cheapest experiment, not a design.
- **Requirements are only the ones that constrain this milestone.** Print fidelity matters for a printable-puzzle app; internationalization may not yet. Do not invent requirements to look thorough; a short system design for a small milestone is correct.
- **Be honest about unknowns.** If you do not know whether a framework can do something, say so and put it in the risk register. Mark platform facts you are unsure of as "verify against current docs".
- If the project is not an Apple-platform one, skip apple-platforms.md and apply the same method with that platform's norms.
