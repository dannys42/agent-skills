---
name: risk-first-roadmap
description: Turn a system design or a vague project idea into a roadmap of small end-to-end increments, each one a working, observable capability that answers the riskiest remaining unknown. Orders work by risk instead of by layer, so the project proves its hardest assumptions first and keeps a runnable app at every step. Tuned for Apple-platform apps. Use whenever the user wants a roadmap, build order, milestones, or "what should I build first" for a new or large project, has just finished a system design (SystemDesign/Overview.md, or a legacy Design-*.md), has adopted an existing codebase and recorded a change of direction, or says a project is too big to know where to start. Also use to re-plan an existing roadmap after an increment taught something new. Not for designing or breaking down one increment (use roadmap-plan-next-rung, then tasklist) or for product-strategy roadmaps with stakeholders and quarters.
license: GPL-3.0-or-later
model: opus
---

# Risk-First Roadmap

Build the project as a ladder of increments. Each rung is a complete, end-to-end slice that runs and can be seen, and each rung exists to **answer the riskiest unknown you can answer from where you are now**. Early rungs find and prove the shape of the system with the least that runs end to end; later rungs grow it, one milestone (an outcome the owner can use) at a time. Failing a rung early is cheap, which is the point.

Read [roadmap-example.md](references/roadmap-example.md) before writing the first rung. It shows the format and a worked ladder. For Apple-platform projects also read [apple-rungs.md](references/apple-rungs.md).

## Input

Look for the system design: `<DocDir>/SystemDesign/Overview.md`, where `DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one). If only a legacy `<DocDir>/Design-<Topic>.md` exists, use that. Read its risk register, focus areas, scope, headline requirements, component depth tags, and any decisions of kind `shift`. Also read the risk registers of any subsystem docs beside it (`SystemDesign/<Subsystem>.md`). IDs are per document, so cite them qualified by doc name (`Puzzle_Generator:R3`, `Overview:FR1`) in `De-risks` and traceability. A rung may span several subsystems.

A `shift` decision comes from adopting an existing codebase: it is a change of direction the user wants, not yet built. Treat each accepted shift as work the roadmap must deliver, with its own unknowns (can the new shape coexist with the old one, can data migrate), and give it a rung or horizon item.

If no design exists, say so and offer two paths: run the `system-design` skill first (best when the project is large or the unknowns are many), or build a short risk list with the user right now (fine for a small project). Do not invent a roadmap from nothing; the ordering is only as good as the list of unknowns.

## How to order the rungs

1. **List the unknowns.** Take the risk register and add anything the design missed. For each, write the cheapest experiment that would answer it, expressed as something that visibly works, and give it a class:
   - **shape**: its answer would change the components, boundaries, data flow or persistence model.
   - **clock**: each day of delay loses something that cannot be recovered (data that cannot be backfilled, an external window, an archive with no copy).
   - **breadth**: more of a shape that is already proven.
2. **Find what each one needs.** An experiment depends on things existing: a running app before you can draw, a canvas before you can test fonts. These dependencies are what force an order.
3. **Order by class, then by risk.** After the skeleton:
   1. shape unknowns, until the shape has run end to end once;
   2. clock items: start each clock at its earliest slice, and finish its coverage before breadth or work for a later milestone;
   3. breadth, milestone by milestone.

   Within a class, among unknowns whose prerequisites already exist, choose the one with the highest impact × uncertainty, and take the smallest slice that answers it. If its prerequisites do not exist, the next rung is the cheapest slice that builds them.
4. **Always start with the walking skeleton.** The first rung is the most basic version of the product that builds, runs, and shows something. Its question is "can I build and run the most basic thing at all?"
5. **Tie-break** toward the rung that unlocks the most later rungs, then toward the cheaper one.
6. **Repeat** until the remaining rungs are low-risk completion work (more of what is proven), then stop being precise about them.

**Shape first, then grow.** Prove the shape with the minimum that runs end to end, then grow it. An app with a database needs its first table early, because that table proves the persistence model (shape). It does not need the whole schema: each later table arrives with the rung that needs it (breadth). A prerequisite of the current milestone is never breadth to put off. Experiments need the data they read, so finishing that ingestion comes before deepening the experiment workflow, and sooner still when the data cannot be backfilled (clock).

A sound ladder reads like a series of questions: can I run an app, can I draw, can I control the drawing finely, can I produce the core logic, can I see its result, can I scale it. Reordering these should feel wrong because each one needs the last.

## Write each rung

Use this shape, and keep it short:

```markdown
### L3: Control text rendering in the grid
Question: Do fonts, size, color, and style render legibly at screen and print scale?
Slice: Draw digits 1–9 in the fixed grid with chosen font and weight; export a PDF.
Done when: The PDF opens with crisp, correctly sized digits, and a printed page is readable.
De-risks: R2 (text fidelity)
Depends on: L2
Milestone: M1
Class: shape
If no: Try a different font stack or draw digits as paths; record in the design.
Status: planned
```

- **Question** is the unknown, phrased so the rung can fail.
- **Slice** is what the user can run and see. If you cannot demo it, it is not a rung.
- **Done when** is observable and checkable, with the command or action to check it.
- **De-risks** links to the design's risk IDs (`R`), so the register shrinks as rungs complete. Rungs use their own prefix, `L` (ladder), so they never collide with risk IDs.
- **Milestone** names the milestone the rung serves, and **Class** is `shape`, `clock` or `breadth` (see above). A `Kind: refactor` rung takes the milestone it unblocks.
- **If no** is the fallback or the decision to revisit. A rung that cannot fail is not testing anything.
- A rung that comes from an accepted code-quality proposal adds `Kind: refactor` and asks whether the new shape holds without changing behaviour ("Can the three derivers share one protocol with every existing test still green?").

## Milestones

Risk orders the work inside a goal; value orders the goals. Group the rungs under **milestones**: outcomes the owner can use, such as `M1 — I can see every app's data on one timeline`. They go one line each in the roadmap's `## Milestones` section, with the capabilities each needs and a status (`planned`, `current`, `done`, `deferred`, `dropped`). Milestone IDs (`M1`, `M2`, ...) are never reused.

- Draft the milestones from the design's success criteria and scope. The first is the thinnest path from the skeleton to something the owner would use.
- Order milestones by value, once their prerequisites are met. Exactly one is `current`.
- Rungs are ordered by the rules above inside the current milestone. A shape or clock rung may serve a later milestone early; nothing else may.

## Detail horizon

Write the first three or four rungs of the current milestone in full. List the rest of it as one-line **horizon** items in rough order, with no slice or done-when yet. A later milestone is its one line in `## Milestones` and has no rungs yet, apart from any shape or clock rungs it already holds. Later rungs depend on what earlier ones teach, so detailing them now creates false confidence and waste. Expand a horizon item only when it becomes next.

A horizon item is one line. Detail the owner has already given goes, verbatim and dated, into `<DocDir>/ParkedIdeas-<Topic>.md` under its milestone, and the horizon line points there. It is read again when the rung is planned.

## New requests mid-roadmap

When the owner asks for something new between rungs, do not design it yet:

1. Map it to a milestone, or propose a new one.
2. List what it needs that is not built, and class each item. A clock item goes on the ladder now.
3. Add one horizon line per new rung, or one line to the milestone.
4. Park the request and any detail the owner gave in `ParkedIdeas-<Topic>.md`, as above.

Say in one or two lines where it landed and what, if anything, it moved.

## Rung 1 and build boundaries

The skeleton rung otherwise decides the target layout implicitly. When the design implies **more than one build boundary that rung 1 must create** (separate executables, a shared package, or an enforced layering between modules), say so in rung 1's slice. The build targets, their allowed imports, a diagram of them, and their build and test commands are then decided in rung 1's brief (written by `roadmap-plan-next-rung`), not in a separate up-front document or a rung of its own. Gate rung 1's implementation on the owner approving that brief.

With a single app target (a test target or one local package does not count as a second boundary), say so in one line in the roadmap. The traceability check below and the drift checkpoint apply either way.

## Check the ladder before showing it

Fix these smells first:

- **Layer-by-layer rungs** ("build the data model", then "build the UI", then "add persistence"). These deliver nothing visible and defer risk. Slice vertically instead.
- **A rung nobody can see run.** Add the thinnest visible output, even a log line or a plain list.
- **A rung that answers two unknowns.** Split it, so a failure points at one cause.
- **Polish before proof.** Styling, settings, and onboarding come after the core risks are retired.
- **Setup rungs with no demo** ("configure CI", "set up architecture"). Fold setup into the first rung that needs it.
- **A requirement no rung proves.** Every must-have FR/NFR maps to a rung or horizon item, or is listed as an explicit gap the user has seen. Each design doc owns the traceability of its own requirements: fill in the Overview's table (`L4, via Puzzle_Generator` when allocated to a subsystem, `L4, via Puzzle_Generator (doc pending)` while that doc is not written) and each existing subsystem doc's table, and list gaps with qualified IDs (`Puzzle_Generator:NFR1`). A legacy design without a table gets a small one in the roadmap file.
- **A shift no rung delivers.** Every accepted `shift` decision in the Overview maps to a rung or horizon item.
- **A big unknown buried late** because its prerequisite looked expensive. Pull it forward by building the cheapest stand-in for the prerequisite.
- **A clock item ranked behind breadth or a later milestone.** Every day of delay loses something; pull it forward.
- **A rung for a later milestone while the current one is open**, unless it is shape or clock work. Move it to its milestone's horizon.
- **A whole layer designed up front** ("the full schema", "every endpoint"). Take the slice the current rung needs; the rest is breadth.

## Review with the user

Show the milestones first, one line each, then the ladder as a short numbered list of one-line questions, so the order is easy to judge, and the detail for the first rungs after. Explain the ordering by naming the risk each early rung buys down. Invite changes: the user may know something about risk that the design does not. Before the invitation, call out the ordering choices that deserve a second look, in the shape in `roadmap-plan-next-rung`'s [presenting-for-review.md](../roadmap-plan-next-rung/references/presenting-for-review.md): a rung placed on a guessed risk ranking, an inferred dependency, or an early rung whose cost is unclear, each with alternative orderings and a pro and con for each (without the file: those items first, each with why and two or three options, recommended first). When they reorder, re-check dependencies, update, and tell them what the change does to the early risk exposure.

Save to `<DocDir>/Roadmap-<Topic>.md`, using the `Topic` named in the Overview's `Roadmap:` line (or the legacy design's `Topic`). State the path. If the file exists, read it and continue its IDs (a roadmap over about 30 KB is read by section, see [Keep the roadmap small](#keep-the-roadmap-small)). If it has no `## Milestones` section, offer once, at the next re-plan, a one-time pass: draft the milestones, tag each open rung's milestone and class, and show the reorder that would follow. Apply it only on a yes. IDs (`L1`, `L2`, ...) are document-wide, never reused or renumbered, even when a rung is dropped or split.

## Keep the roadmap small

The roadmap holds the live ladder, open risks and current decisions. Closed history moves out, verbatim, so every read stays cheap and nothing is lost.

- **Learning-log entries** are one or two lines, at most about 600 characters: the measured answer and a pointer to where the detail lives (the rung brief's "As built" note, or the design doc that now states it). Raw facts, owner decisions and measured results go in full into that design doc, not into the log.
- **A finished rung's detail** (`done`, `failed`, `obsolete`): at re-plan, move its `### <RungId>` section unchanged to `<DocDir>/Completed/Roadmap-<Topic>-Rungs.md` and end its ladder line with `detail: Completed/Roadmap-<Topic>-Rungs.md` after the bracketed status (see [the ladder line format](references/roadmap-example.md)). The ladder line stays, so the ID still resolves. Do the move in the same commit as the status change, and check it with `git diff --color-moved`.
- **An old learning log**: past about 15 entries, move entries older than the last re-plan unchanged to `<DocDir>/Roadmap-<Topic>-Log.md` and leave one link line under `## Learning log`.
- **Layout that allows partial reads**: one `###` section per rung, headings unchanged once written, ladder lines and table cells short (under about 400 characters; the reasoning goes in the brief and the cell links to it). A line over about 1,500 characters cannot be read in part.
- **Reading**: do not read the whole file to find one rung. With the `roadmap` tool (`~/.cache/danny-agent-skills/bin/roadmap`, built by the `task-workflow` plugin; see [Plan tool check](#plan-tool-check)): `roadmap status <file>`, `roadmap show <file> <RungId>`, `roadmap outline <file>`, `roadmap section <file> <heading>`, and `roadmap lint <file>` after editing. Without it, `grep -n '^#'` the file and Read the lines you need.

### Tidy an existing roadmap or Overview

Never rewrite an existing file unasked. But when you read a roadmap or Overview for any reason (a re-plan, `roadmap-plan-next-rung`, a fold-back), check it once per session, and if a trigger fires, offer one tidy pass, stating what it would do and the bytes it would save. Wait for a yes.

Triggers (with the `roadmap` tool, `roadmap lint <file>` and `roadmap outline <file>` give all of them):
- the file is over about 40 KB, or finished rungs and the learning log are over half of it: move finished rung sections and the old log out, as above
- a ladder line has no recognised status, or `lint` reports duplicate IDs or a rung section with no ladder entry: fix the line to the format below (status only, in brackets; the `Status:` line of its section tells you what it is)
- the file is still over about 40 KB with nothing above left to move: move the dated bullets under `## Why this order` that describe earlier re-plans (not the current order's reasoning) unchanged to the Log file, leaving one link line
- a Horizon item runs past one line: move its detail verbatim into `ParkedIdeas-<Topic>.md` and leave the one line with a pointer
- a line is over about 1,500 characters, or table or log cells run past about 400 or 600: shorten the cell, move the reasoning into the rung brief or design doc, and link it
- an Overview (no tool support: judge from `grep -n '^#'` sizes): a risk, decision or traceability cell that is a paragraph, a retired risk still in the open register, or a decision log entry whose reasoning duplicates a rung brief: shorten to one line and link

Do the pass as a move-only commit, separate from content changes, and verify it with `git diff --color-moved` and `roadmap lint`. Never change an ID, a heading or a status in a tidy pass, except to repair a malformed status line, and say which lines you repaired. Offer a pass at most once per session unless the user asks again.

### Plan tool check

Before the first `roadmap` call in a session, run `~/.cache/danny-agent-skills/bin/roadmap --version`. If it fails or is not `0.5.1`, install it without asking: `sh "$(ls -td ~/.claude/plugins/cache/*/task-workflow/*/tools/plantools/build.sh | head -n 1)"` (the `task-workflow` plugin's build script; if that finds nothing, the plugin is not installed, so skip the tool). If `swift` is missing or the build fails, say so in one line, do not retry, and read by hand. Do not fall back to `grep`, `awk` or `sed` while an install is still untried. `roadmap-plan-next-rung` uses the same check.

## Hand off to implementation

A roadmap is not a task list. When the user is ready to build the next rung, run `/roadmap-plan-next-rung` for just that rung: it writes a short design brief for the parts the rung touches, agrees it with the user, and hands off to the `tasklist` skill, which writes `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`; `tasklist-run` executes it. `/rung` runs the whole cycle: plan, run, close. Do not pre-expand later rungs.

End a new roadmap (and any re-plan) with the next step, as `Next: /rung → plan <rung ID> (Opus: /model opus)`, because planning designs the rung against the code and settles the open decisions. Name the rung ID so the user can paste the line. Log it as a `step` event (fields in `tasklist-run`'s metrics log).

## Re-plan after each rung

This normally runs as the last part of `/rung close` (`roadmap-plan-next-rung`'s "Close a rung"), after fold-back. After a rung finishes, fold it back first (`/roadmap-plan-next-rung close L3` does it), so the affected design docs (the Overview and any subsystem docs the rung touched), with their risk registers and decision logs, describe what was actually built. Then update the roadmap before starting the next rung:

- Set its status (`done`, `failed`, `changed`) and record what was learned in one or two lines, including the measured answer to its question.
- Update the affected design docs' risk registers and decision logs if re-planning changed them beyond what fold-back recorded.
- **After the first end-to-end data rung**, make sure that rung's fold-back compared every affected design doc as a whole with what was built, not just the components it touched. Record any drift in the decision log and fix whichever side is wrong.
- **Code quality** (`code-quality-pass` skill): if `<DocDir>/Quality/Review-<date>.md` or a `Quality/Proposals-<RungId>.md` (a tidy's, with accepted defects as `task`s, reproducing test first) has accepted entries, place them: a `refactor-rung` becomes a rung (`Kind: refactor`) ordered by the rules above, never ahead of a feature rung unless the user puts it there; a `task`, `conventions` or `fitness-test` becomes a task in the next rung's tasklist or a small `Tasklist-Refactor-<Short_Name>.md`. Mark each placed proposal with its rung or task in the report. Then, if `Quality/Status.md`'s `Since review:` has reached `Every:` or `Triggers pending:` is not `none`, offer `/code-quality-pass review` in one line (run, skip or defer); with no `Status.md`, the fold-back signals already nudged, so say nothing more. This step never holds up the next rung.
- **A "no" trims its branch.** If the rung answered no to the premise of a milestone (its outcome cannot be reached as planned), set that milestone's remaining open rungs to `deferred` and ask the owner to keep, reshape or drop it. Do not detail more of its rungs until they answer.
- When every rung of the current milestone is done, mark it `done`, make the next milestone `current`, and expand its first rungs.
- Re-rank the remaining risks and promote or demote horizon items. Add new rungs for newly discovered unknowns; mark rungs that became unnecessary `obsolete` instead of deleting them.
- Tell the user what moved and why, then end with the next step: `/roadmap-plan-next-rung <next rung ID>` on Opus (`/model opus`), logged as a `step` event.

Statuses: `planned`, `in progress`, `done`, `failed` (answered "no", fallback taken), `changed`, `obsolete`, `deferred`.

## If a linked skill is missing

This skill hands off to `system-design`, `roadmap-plan-next-rung` (`project-planning` plugin) and `tasklist` (`task-workflow` plugin). When one is absent, do not stop: use the fallback below, and say once, in one or two lines, what is missing, how to install it (`claude plugin install project-planning@danny-sung-agent-skills`, `claude plugin install task-workflow@danny-sung-agent-skills`, or `npx skills add dannys42/agent-skills --skill <skill-name>`), and how to recover.

- No `system-design`: build the short risk list with the user (see Input).
- No `roadmap-plan-next-rung`: expand the rung straight into tasks with `tasklist`, citing the rung ID; skip fold-back and update the design's risk register by hand when re-planning.
- No `tasklist`: write the rung's tasks as a plain checklist at `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`, each with an ID, `Needs`, and `Done when`.
- Recover: once installed, run the skipped step (`/roadmap-plan-next-rung` for the current rung, or `tasklist` to convert the plain checklist). Existing files are read and continued, never overwritten.
