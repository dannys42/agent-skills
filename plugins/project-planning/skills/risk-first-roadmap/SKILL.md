---
name: risk-first-roadmap
description: Turn a system design or a vague project idea into a milestone map, capability layers ordered foundation first, each with a plain-language outcome and exit criteria, and inside the current milestone a ladder of small end-to-end rungs ordered riskiest unknown first, so a runnable app exists at every step. Use whenever the user wants a roadmap, milestones, build order or "what should I build first" for a new or large project, has just finished a system design (SystemDesign/Overview.md, or a legacy Design-*.md), has adopted an existing codebase and recorded a change of direction, or says a project is too big to know where to start. Also use to re-plan when a rung fails or answers a different question, an owner request lands in the current milestone or a settled seam must change, and at milestone close for the next milestone. Tuned for Apple-platform apps. Not for designing or breaking down one rung (use plan-milestone, then tasklist) or for product-strategy roadmaps with stakeholders and quarters.
license: GPL-3.0-or-later
model: opus
---

# Risk-First Roadmap

Value orders the goals; risk orders the work inside one. The roadmap is a **milestone map**: capability layers ordered foundation first, with only the current milestone broken into rungs. Each rung is a complete, end-to-end slice that runs and can be seen, and exists to answer the riskiest unknown the current milestone can answer from where it stands. Failing a rung early is cheap, which is the point.

Use the terms in `system-design`'s [terms.md](../system-design/references/terms.md) as defined there (milestone, foundation, pillar, end-of-goal rule, spike, provisional code, manual stand-in, `Touches:`, detail by distance, re-plan triggers). Read [roadmap-example.md](references/roadmap-example.md) before writing the map; for Apple-platform projects also read [apple-rungs.md](references/apple-rungs.md).

## Input

Read the system design: `<DocDir>/SystemDesign/Overview.md`, where `DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one), or a legacy `<DocDir>/Design-<Topic>.md`. Read its Scope and milestones table (outcomes and additive checks), headline requirements, component depth tags, Provisional code and Manual stand-ins tables, risks, Open questions marked `after it runs`, and decisions of kind `shift`. Also read the risk registers of subsystem docs beside it (`SystemDesign/<Subsystem>.md`). IDs are per document, so cite them qualified (`Puzzle_Generator:R3`, `Overview:FR1`).

A `shift` decision comes from adopting an existing codebase: a change of direction not yet built. Each accepted shift is work the map must deliver, with its own unknowns (can the new shape coexist with the old one, can data migrate).

If no design exists, offer two paths: run `system-design` first (large project, many unknowns), or build a short risk list with the user now (small project). Do not invent a roadmap from nothing.

## The milestone map

1. **Milestones are capability layers, ordered foundation first**: what the goal stands on (data, the core model) before the goal itself, e.g. data in one place → see it → record changes → grade changes. Take them from the system design's Scope and milestones table.
2. **The first milestone is thin.** It is the thinnest foundation the next milestone stands on, or the first pillar: the thinnest end-to-end slice that proves the goal's most fundamental capability across several subsystems at minimal depth, with manual stand-ins for what is not built yet. It builds no machinery a later pillar will rebuild, and the foundation only as deep as the next pillar needs; extending the foundation for a later pillar is new work in a later milestone, not before. E.g. the simplest method that can be measured, not a second method to compare, a threshold sweep or extra reports: those become later one-line milestones or "decide after it runs" items. When the system design's current milestone is wider than this, propose the split as a decision.
3. **End-of-goal rule.** The goal's own machinery waits until its foundation milestones are done, except the thin first pillar ("thin": nothing a later pillar will rebuild). A **spike** (`Kind: spike`) may run earlier to answer "is it feasible?"; it builds none of the goal's machinery, and a "no" goes to the owner as a refuted premise.
4. **Kept spike code** is provisional code: marked `PROVISIONAL(<RungId>): replace at <MilestoneId> (<milestone name>)`, added to the system design's Provisional code table and kept behind a seam. When foundation code must depend on it, the owner promotes it to a `working` item or the dependency waits. Prefer it to a manual stand-in; each stand-in is a row in the Manual stand-ins table beside it. The milestone each row names schedules the replacement in its planning.
5. **Each milestone has** an outcome sentence in the owner's plain language (you draft it, marked `proposed` until the owner accepts it), the subsystems it touches, exit criteria the owner accepts at a demo, and its rungs. When the owner supplies an outcome or exit criterion, offer once to tighten it as `system-design` does (an exit criterion nobody can check, a vague term, a name clashing with `Taxonomy.md`), showing both versions; never rewrite owner text silently.
6. **The owner sets the order.** Propose it, flag each dependency problem (a milestone that needs one placed after it, a clock item, such as data that cannot be backfilled, in a late milestone), and apply the owner's order. At a pillar boundary, propose the next-pillar options with their dependencies and costs; the owner picks.

Milestone IDs (`M1`, `M2`, ...) are never reused. Statuses: `planned`, `current` (exactly one), `done`, `deferred`, `dropped`. The line format, with its `Exit:`, `Additive check:` and `Close:` sub-bullets, is in [roadmap-example.md](references/roadmap-example.md); `Close:` exists only while a milestone close is in progress and is removed when it ends.

Do not add checkpoint rungs: the look-back runs at the start of milestone planning. An older roadmap whose next rung is `Kind: checkpoint` runs it through `system-design`'s checkpoint alias, which sets it `done`.

## Order the rungs of the current milestone

Risk classes apply only inside the current milestone; the owner can pin an order.

1. **List the unknowns** the milestone must answer: its risks from the system design plus anything it missed. For each, write the cheapest experiment that would answer it as something that visibly works, and class it:
   - **shape**: its answer would change the components, boundaries, data flow or persistence model;
   - **clock**: each day of delay loses something that cannot be recovered (data that cannot be backfilled, an external window);
   - **breadth**: more of a shape already proven.
2. **Find what each needs.** An experiment depends on things existing (a running app before drawing); these dependencies force the order.
3. **Start with the walking skeleton** in the first milestone: the most basic version that builds, runs and shows something.
4. **Order by class, then by risk:** shape until the milestone's shape has run end to end once; clock items started at their earliest slice, their coverage finished before breadth; then breadth. Within a class, among unknowns whose prerequisites exist, take the highest impact × uncertainty in the smallest slice that answers it; if the prerequisites do not exist, the next rung is the cheapest slice that builds them. Tie-break toward the rung that unlocks the most, then the cheaper.

Prove the shape with the minimum that runs end to end, then grow it: the first table, not the whole schema; each later table arrives with the rung that needs it. A sound ladder reads like a series of questions where each needs the last: can I run an app, can I draw, can I produce the core logic, can I see its result.

## Write each rung

```markdown
### L3: Control text rendering in the grid
Question: Do fonts, size, color, and style render legibly at screen and print scale?
Slice: Draw digits 1–9 in the fixed grid with chosen font and weight; export a PDF.
Done when: The PDF opens with crisp, correctly sized digits, and a printed page is readable.
De-risks: R2 (text fidelity)
Depends on: L2
Milestone: M1
Touches: Grid_View, Print_Export
Class: shape
If no: Try a different font stack or draw digits as paths; record in the system design.
```

- **Question** is the unknown, phrased so the rung can fail. **If no** is the fallback; a rung that cannot fail tests nothing.
- **Slice** is what the user can run and see. If you cannot demo it, it is not a rung.
- **Done when** is observable, with the command or action to check it. A target to reproduce an existing result exactly holds only once both paths are known to read the same input; until then write "compare and explain each difference".
- **De-risks** cites the design's risk IDs (`R`); rungs use `L` (ladder) so they never collide.
- **Touches** names the subsystems the rung changes, on every rung.
- **Class** is `shape`, `clock` or `breadth`. `Kind: spike` marks a feasibility spike; `Kind: refactor` marks a rung from an accepted code-quality proposal, asking whether the new shape holds without changing behaviour, and takes the milestone it unblocks.
- The status lives only in the ladder line's bracket. An older section's `Status:` line: change it with the bracket, or delete it (`roadmap lint` flags a pair that disagrees).

## Detail by distance

- **Current milestone:** every rung on the ladder with a section as above. Milestone planning then writes each rung's brief, kept short because the seams are agreed.
- **Next milestone:** its line plus its additive-check verdict from the system design. No rungs.
- **Later milestones:** a name and one line. No rungs.

The `## Horizon` holds one-line rungs not yet detailed: a current-milestone rung a re-plan added, or one whose slice waits on an earlier rung's answer. Detail the owner gave for later work goes verbatim and dated into `<DocDir>/ParkedIdeas-<Topic>.md` under its milestone; the line points there.

**"Decide after it runs" list.** The roadmap's `## Decide after it runs` section is the project's home for minutiae (thresholds, exact output shape, polish, internal names), each filed under the rung or milestone that settles it. When the roadmap is first written, move the system design's Open questions marked `after it runs` here. Fold-back checks the items a rung was to settle.

## New requests and deferrals

When the owner asks for something new between rungs, do not design it yet. Map it to a milestone, or propose a new one. If it lands in the current milestone, that is a re-plan trigger: list what it needs, class each item, and add the rungs. If it lands in a later milestone, rewrite that milestone's line if needed and park the detail as above; a clock item is flagged to the owner as an order problem. Say in one or two lines where it landed and what it moved.

When the owner defers work: set the rung `[deferred: <what it waits on>]`, change its `Milestone:` to the one it now serves (propose one when none fits), rewrite the affected milestone lines, and add one learning-log entry. In the design docs, mark the question or decision `deferred` with its reason, and move what only it would have added to a later milestone's line.

## Rung 1 and build targets

The system design agrees the build targets. When the current milestone needs **more than one build boundary that rung 1 must create** (separate executables, a shared package, an enforced layering between modules), say so in rung 1's slice; their allowed imports, diagram, and build and test commands go in rung 1's brief, gated on the owner approving it. With a single app target (a test target or one local package does not count), say so in one line in the roadmap.

## Check the map before showing it

Fix these first:

- **A wide first milestone**: it builds machinery a later pillar will rebuild, or foundation deeper than the next pillar needs (e.g. comparing methods, tuning thresholds). Cut it to the thinnest version and move the rest to later lines.
- **Goal machinery before its foundation** outside the thin first pillar, or a spike that builds machinery.
- **Rungs or slices for a later milestone**, or detail on one beyond its line.
- **Layer-by-layer rungs** ("build the data model", then "the UI"). Slice vertically.
- **A rung nobody can see run.** Add the thinnest visible output, even a log line.
- **A rung that answers two unknowns.** Split it, so a failure points at one cause.
- **Polish before proof**, or **setup rungs with no demo** ("configure CI"): fold setup into the first rung that needs it.
- **A rung without `Touches:`**, or kept spike code with no Provisional code row.
- **A requirement no rung proves.** Every must-have FR/NFR of the current milestone maps to a rung, or is an explicit gap the owner has seen. Each design doc owns its traceability table (`L4, via Puzzle_Generator`, or `(doc pending)` while that doc is unwritten); list gaps with qualified IDs. A legacy design without a table gets a small one in the roadmap.
- **A shift no milestone delivers.**
- **A big unknown buried late** because its prerequisite looked expensive: build the cheapest stand-in for the prerequisite.
- **A clock item behind breadth.** Pull it forward.
- **A whole layer designed up front** ("the full schema"). Take the slice the rung needs.

## Review with the owner

Show the milestone list whole first, one line each with the outcome, then the current milestone's ladder as one-line questions, then the first rungs' detail. Name each ID with its short name (`M1 (data in one place)`, `L3 (text in the grid)`). Explain the order by the risk each early rung buys down. Then present every decision in the shape in `plan-milestone`'s [presenting-for-review.md](../plan-milestone/references/presenting-for-review.md): the milestone order, each `proposed` outcome and exit criteria, the first milestone's cut, and rung-order choices resting on a guessed ranking, an inferred dependency or an unclear cost. Without that file: group them Important, Notable, Small; give every decision two or three options, each with a pro and con and the recommended one first; end with one question. When the owner reorders, re-check dependencies and say what it does to early risk exposure.

## Save and keep the roadmap small

Save to `<DocDir>/Roadmap-<Topic>.md`, using the `Topic` in the system design's `Roadmap:` line (or the legacy design's `Topic`), and state the path. If the file exists, read it and continue its IDs. Rung IDs (`L1`, `L2`, ...) are document-wide, never reused or renumbered.

The roadmap holds the map, the live ladder and current decisions. Closed history moves out verbatim, so every read stays cheap:

- **`Updated:`** holds one date. Earlier dates and their history paragraph go to `<DocDir>/Roadmap-<Topic>-Log.md`.
- **Learning-log entries** are one or two lines, at most about 600 characters: the measured answer and a pointer to the brief's "As built" note or the design doc that now states it.
- **A finished rung's detail** (`done`, `failed`, `changed`, `obsolete`): at re-plan or milestone close, move its `### <RungId>` section unchanged to `<DocDir>/Completed/Roadmap-<Topic>-Rungs.md` and end its ladder line with `detail: Completed/Roadmap-<Topic>-Rungs.md` after the status. `roadmap archive <file> <RungId>...` does both (`--dry-run` shows the diff); without the tool, do it by hand, in the same commit as the status change, checked with `git diff --color-moved`.
- **An old learning log**: past about 15 entries, move entries older than the last re-plan unchanged to the Log file, leaving one link line under `## Learning log`.
- **Partial reads**: one `###` section per rung, headings unchanged once written, ladder lines and cells under about 400 characters (reasoning goes in the brief, linked). A line over about 1,500 characters cannot be read in part.
- **Reading**: do not read the whole file to find one rung. With the `roadmap` tool (`~/.cache/danny-agent-skills/bin/roadmap`): `roadmap status|outline|lint <file>`, `roadmap show <file> <RungId>`, `roadmap section <file> <heading>`, and `lint` after editing. Without it, `grep -n '^#'` and Read the lines you need. `Map.md` (milestones and rungs one line each with `Touches`) is generated by the tool, never written by hand: after saving or re-planning, run the tool's map command (`roadmap map <file>` writes `<DocDir>/Map.md` beside the roadmap; `--print` only prints it). `roadmap name <file> <ID>...` prints IDs with their names, e.g. `L4 (Folder suggestions)`.

### Tidy an existing roadmap or Overview

Never rewrite an existing file unasked. When you read one for any reason, check it once per session, and if a trigger fires, offer one tidy pass, stating what it would do and the bytes it saves. Wait for a yes.

Triggers (`roadmap lint` and `roadmap outline` give them):
- over about 40 KB, or finished rungs and the learning log over half of it: move them out as above
- a ladder line with no recognised status, duplicate IDs, or a rung section with no ladder entry: fix the line to the format (an older section's `Status:` line tells you the status)
- still over about 40 KB: move `## Why this order` bullets about earlier re-plans, and an `Updated:` history paragraph, unchanged to the Log file, leaving one link line
- a Horizon item past one line: move its detail verbatim into `ParkedIdeas-<Topic>.md`, leaving the line and a pointer
- a line over about 1,500 characters, or cells past about 400 or 600: shorten and link the reasoning
- an Overview (judge from `grep -n '^#'` sizes): a risk, decision or traceability cell that is a paragraph, a retired risk in the open register, or a decision whose reasoning duplicates a brief: shorten to one line and link

Do the pass as a move-only commit, verified with `git diff --color-moved` and `roadmap lint`. Never change an ID, heading or status in a tidy pass, except to repair a malformed status line (say which). Offer at most once per session unless asked again.

Two things are deleted, not moved, each in a commit of its own: a closed question whose answer is now a decision row, and a design doc's notes for the roadmap once their rungs are on the ladder. Folded-back briefs and `Completed/` tasklists are kept until the milestone's retro has run; then offer to delete them (git keeps them), first moving any reasoning a design doc links to into one line of that doc.

### Plan tool check

Before the first `roadmap` call in a session, run `~/.cache/danny-agent-skills/bin/roadmap --version`. If it fails or is older than `0.7.0`, install it without asking: `sh "$(ls -td ~/.claude/plugins/cache/*/task-workflow/*/tools/plantools/build.sh | head -n 1)"` (if that finds nothing, the plugin is not installed: skip the tool). If `swift` is missing or the build fails, say so in one line, do not retry, and read by hand. Do not fall back to `grep`, `awk` or `sed` while an install is untried.

## Hand off

A roadmap is not a task list. The next step after a new map is milestone planning for the current milestone: the look-back, the design delta, every rung's brief and the tasklists, on Opus. End with a sentence saying so, then `Next: /rung (Opus: /model opus)`; never a rung or milestone ID on the `Next:` line. In the closing summary every milestone or rung you mention carries its name (`system-design`'s terms.md, "An ID shown to the owner carries its name"). Log it as a `step` event with `skill` `risk-first-roadmap 1.0.1` (other fields in `tasklist-run`'s metrics log).

## Re-plan

Re-plan inside a milestone only on a trigger: a rung fails, a rung answers a different question than it asked, an owner request lands in the current milestone, or a `settled` seam must change. Otherwise the next brief already exists and the next rung just runs. Milestone close also runs this, for the next milestone.

- Set the rung's status (`done`, `failed`, `changed`) with a learning-log line holding the measured answer; `changed` says what it answered instead. Update the design docs' risks and decisions if re-planning changed them beyond fold-back.
- **A "no" trims its branch.** If a rung refutes a milestone's premise, set the milestone's open rungs `deferred` and ask the owner to keep, reshape or drop it. Detail nothing more of it until they answer.
- **Deferred rungs come back here.** When the wait is over, set the rung `planned` and update its milestone. After a "no", or with no rung `planned`, ask about each deferred rung of the milestone: keep, reshape (rewrite question, slice and done-when), keep waiting, or drop (`obsolete: dropped by owner`; a milestone with nothing left becomes `dropped`). One learning-log entry records the answers.
- **Code quality** (`code-quality-pass`): accepted entries in `<DocDir>/Quality/Review-<date>.md` or `Quality/Proposals-<MilestoneId|RungId>.md` are placed: a `refactor-rung` becomes a `Kind: refactor` rung, ahead of the milestone's first feature rung when a look-back accepted it, otherwise ordered by the rules above; a `task` or `fitness-test` goes to `<DocDir>/Tasklist-Refactor-<Short_Name>.md`, which `/rung` runs before the next rung. Mark each placed proposal. If `Quality/Status.md`'s `Since review:` reached `Every:` or `Triggers pending:` is not `none`, offer `/code-quality-pass review` in one line. Never hold up the next rung for it.
- **At milestone close**, after the owner accepts the demo: mark it `done`, make the next milestone in the owner's order `current`, list its rungs as above, and move what is now next to its one-line-plus-additive-check form. Its rungs' briefs wait for its milestone planning.
- Re-rank the remaining unknowns. Add rungs for newly discovered ones, including those a rung that answered a different question revealed; mark rungs that became unnecessary `obsolete` instead of deleting them.
- **With no rung `planned`**: bring back a deferred rung (above), detail the next horizon item of the current milestone, or drop it; with none left, the milestone goes to milestone close.
- A `replan` handoff note in `<DocDir>/Handoff/` (a design session leaves one) is read first and deleted once the re-plan is committed, unless `/rung` already did.
- Tell the owner what moved and why, then end as in [Hand off](#hand-off), with the `Next:` model the next step needs.

Commit a new roadmap, or a re-plan run on its own, staged by explicit path (the roadmap, design docs it changed, a `Completed/` move, a refactor list), as `Roadmap: <what changed>`.

Rung statuses: `planned`, `in progress`, `done`, `failed` (answered "no", fallback taken), `changed`, `obsolete`, `deferred` (with what it waits on). The roadmap is finished only when no rung is `planned`, `in progress`, `deferred` or on the horizon and no milestone is `planned` or `current`.

## If a linked skill is missing

This skill hands off to `system-design` and `plan-milestone` (`project-planning` plugin) and `tasklist` (`task-workflow` plugin). When one is absent, do not stop: use the fallback below, and say once what is missing, how to install it (`claude plugin install project-planning@danny-sung-agent-skills`, `claude plugin install task-workflow@danny-sung-agent-skills`, or `npx skills add dannys42/agent-skills --skill <skill-name>`), and how to recover.

- No `system-design`: build the short risk list with the user (see Input), and the milestone list with it.
- No `plan-milestone`: expand each rung straight into tasks with `tasklist`, citing the rung ID; update the design's risks by hand at re-plan.
- No `tasklist`: write a rung's tasks as a plain checklist at `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`, each with an ID, `Needs` and `Done when`.
- Recover: once installed, run the skipped step. Existing files are read and continued, never overwritten.
