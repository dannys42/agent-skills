# Planning terms

The shared vocabulary of the project-planning skills. Each term is defined once here; skill text uses it without redefining it.

## The blueprint

- **Blueprint.** The project's design doc, kept at `<DocDir>/SystemDesign/Overview.md`. It holds what the owner and agent agreed: subsystems, the seams and interfaces between them, the data model as entities and relationships, build targets, names (which seed `Taxonomy.md`) and a short threat and privacy section. It covers the current milestone only; each later milestone gets one line on what it will add. Its size is bounded by that milestone, not by a page count. Example: a blueprint for "data in one place" agrees the `Store` and `Importer` subsystems and the `App`, `Sale` and `Review` entities, and says of the next milestone only "adds a dashboard that reads `Sale`".
- **Additive check.** The stopping rule for blueprint depth. For each later milestone's one line, ask: can it be added as new entities, endpoints or symbols without restructuring what exists? If yes, stop. If no, decide that seam now, at the smallest depth that makes the future change additive. Example: while planning "record changes", the next milestone's line says "grade changes" will link each change to a metric window, so the `Change` entity gets a timestamp now; the grading model waits.
- **Reviewable surfaces.** The only places the owner reviews field by field: database schema, REST and wire APIs, and a library's public symbols. Everything else (internal types, algorithms, thresholds, output formats, UI detail) is the agent's to decide inside the agreed seams. Example: the owner reviews the columns of the `sales` table; the agent picks the parsing algorithm.

## Agreement states and marks

- **`settled`.** An agreed item expected to hold. Changing it is a re-plan trigger. Example: "Importer writes only through `Store`'s public API" (`settled`).
- **`working`.** An agreed item good enough to start, with rework expected. It carries a revisit note naming what would make us revisit it. Reworking it as the note foresaw is planned work, not drift. Example: "one SQLite file per project (`working`; revisit if two apps need to share data)".
- **`owner` and `proposed`.** Who an item came from. `owner` items are the owner's own words or rulings; `proposed` items are the agent's, waiting for the owner to accept, edit or reject them. A first pass marks everything it adds `proposed`. Example: a milestone outcome the agent drafted reads `proposed` until the owner accepts it.

## Milestones

- **Milestone.** A capability layer of the project, with an outcome sentence in the owner's plain language, the subsystems it touches, exit criteria the owner accepts at a demo, and its rungs. Example: "M2 (see it): I can open one page and see every app's downloads and ratings for the last 90 days."
- **Foundation-first order.** Milestones are ordered so that what the goal stands on (data, the core model) is built before the goal itself. The owner sets the order; the agent proposes it and flags dependency problems. Example: data in one place, then see it, then record changes, then grade changes.
- **End-of-goal rule.** Until the goal's foundation milestones are done, work on the goal's own outcome runs only as a spike. Example: before data collection is solid, "can we detect a 10–30% effect at this traffic?" may run; building the experiment loop may not.
- **Spike.** A rung that answers "is it feasible?" and builds none of the goal's own machinery. A spike that answers "no" goes to the owner as a refuted premise. Its code may be kept as provisional code when useful across milestones.
- **Provisional code.** Kept spike code. It stays behind a seam, so foundation code does not depend on its internals; if foundation code must depend on it, the owner either promotes it to a `working` blueprint item or the dependency waits. Each piece is:
  - marked in the code with one greppable form: `PROVISIONAL(<RungId>): replace at <MilestoneId> (<milestone name>)`, e.g. `// PROVISIONAL(L6): replace at M4 (grade changes)`;
  - listed in the blueprint's **Provisional code** table, with columns: what it is, where it lives, the milestone that replaces it, what depends on it.

  The named milestone's planning schedules the replacement. `metrics signals` counts the markers at zero tokens and flags one whose milestone is already done.
- **`Map.md`.** A one-page view the `roadmap` tool generates at zero tokens: milestones, and their rungs one line each with name, status and `Touches`. It is the owner's big-picture view; the roadmap file stays the source.
- **`Touches:`** One line on each rung naming the subsystems it changes, e.g. `Touches: Importer, Store`. `Map.md` uses it now; parallel rungs will use it later.

## Rungs and detail

- **Rung.** One increment inside the current milestone. Rungs are ordered riskiest unknown first, but only among the current milestone's rungs, and the owner can pin an order.
- **Detail by distance.** How much is written about work depends on how far away it is:

  | Distance | Detail |
  | --- | --- |
  | Current rung | Full brief |
  | Rest of the current milestone | Short brief, written at milestone planning |
  | Next milestone | One line plus its additive-check line |
  | Later milestones | A name and one line |

- **"Decide after it runs" list.** A project-level list of minutiae (thresholds, exact output shape, polish, internal names), each filed under the milestone or rung that will settle it. Fold-back checks the items a rung was to settle. Example: "minimum confidence to suggest a folder: settle at L7 (folder suggestions) after a run on real files".

## Cadence

- **Milestone planning.** One Opus session at the start of a milestone: a look back at the built code against the blueprint, the blueprint delta for this milestone (including the threat and privacy pass for its new seams), every rung's brief, names reviewed as a set against `Taxonomy.md`, and the tasklists. Example: "M2 (see it) planning wrote the briefs and tasklists for its four rungs in one session."
- **Automatic fold-back.** The mechanical and comparison part of closing a rung, run at the end of the same Sonnet session right after `tasklist-run` commits the rung's last task:
  1. Run the checks (the full suite, or only the touched test targets when the suite is slow: over the project rules' value if they set one, otherwise over about 5 minutes on the last full run) and confirm the rung added a regression test. A failure stops here.
  2. Compare the reviewable surfaces in the rung's diff against the brief and blueprint, and check the brief's `Done when` results and the "decide after it runs" items the rung was to settle.
  3. Classify each difference: as agreed (tick it); internal only, or a `working` item reworked as its revisit note foresaw (one "As built" line); anything else escalates.
  4. Update the docs for the clean cases and commit as `Fold back rung <RungId>`.
  5. Report one line, log a metrics event, and end with `Next: /rung run <next rung>`.

  It never decides which side of a drift is wrong, changes a decision, adds or reorders rungs, or retires a risk on a partial answer.
- **Escalation.** What the automatic fold-back does with anything it may not judge: a reviewable surface or `settled` item that differs, a deferred item with no answer, a `Done when` that did not pass, or a new `PROVISIONAL` marker not in the blueprint. It stops, records what differs, and routes `/rung` to a close session on Opus. Example: "L9 (daily import) renamed the `units` column → escalated to close (Opus)."
- **Milestone close.** One Opus session at the end of a milestone: the full test suite if fold-backs ran only part of it, a re-read of every fold-back in the milestone together, an owner demo against the exit criteria ruled accept, accept with follow-ups or reject, one retro, proposed owner-preference additions, and the re-plan of the next milestone.
- **Re-plan triggers.** Inside a milestone, re-plan only when a rung fails, a rung answers a different question than it asked, an owner request lands in the current milestone, or a `settled` seam must change. Otherwise the next brief already exists and the next rung just runs.

## Names and labels

- **An ID shown to the owner carries its name.** In chat, cards, `Next:` lines, the learning log and `Map.md`, every ID is followed by its short name the first time it appears in a message. Inside design docs, a cross-doc citation keeps the ID and adds the name where it would otherwise be opaque. Example: "L4 (architecture check before folder suggestions)", never "L4" alone.
- **Names say what the thing does,** in the owner's words: no general words (Manager, Engine, Helper, Handler), no metaphors missing from `Taxonomy.md`, no role names ("gate", "stage", "spine"). Example: `Sales_Importer`, not `Data_Engine`.
- **Names are reviewed as a set** against `Taxonomy.md`, at the blueprint and at milestone planning. A name added mid-milestone is flagged when it is added.

## Owner preferences

- **Owner preference.** A taste of the owner's that the agent applies to every first pass (blueprint, milestone outcomes, names, rung briefs) before drafting. Each line holds the preference, one example and the date. Example: "Prefer a small command-line lab for experiments before building them into the app (e.g. a throwaway tool that tests confidence thresholds, 2026-11-01)."
- **Where.** Tastes that hold across projects go in `~/.local/state/danny-agent-skills/owner-preferences.md`; project-specific ones (credential limits, domain principles) go in the project's rules file (`CLAUDE.md` or equivalent).
- **What is not one.** A single ruling (that is a decision in the design docs) and feedback on how the skills behave (that goes to the ledger).
- **Two-overrides rule.** A preference enters only after the owner overrides the same kind of `proposed` item twice, or states it outright. One ruling is a hypothesis. Milestone close and the promote step of `design-session` (the skill for working a design out with the owner; its promote step moves agreed items into the blueprint) propose additions, one line each; the owner accepts or declines.

## Terms that change or retire

- **Overview** keeps its path and file name but is called the blueprint in skill text, and is scoped to the current milestone instead of "about a page".
- **Checkpoint rung** (`Kind: checkpoint`) retires as a separate rung. Its look back becomes the first part of milestone planning, and its look forward becomes the blueprint delta plus the additive check.
- **Per-rung plan session** retires: milestone planning writes every rung's brief, and a rung is planned on its own only after a re-plan trigger.
- **Rung close** (`/rung close`) is no longer a per-rung session. Its mechanical and comparison work moves to the automatic fold-back; the close session on Opus runs only as the escalation path.
- **Fold-back** now normally runs automatically at the end of the run session on Sonnet, not in a separate Opus close session.
- **Re-plan after every rung** retires; re-plans run only on a re-plan trigger and at milestone close.
- **Per-rung retro** retires; there is one retro per milestone, plus a short one for an unusual rung (failed, re-planned or drifted).
- **Depth tags** keep their meaning (`sketched`, `designed`, `built`). `designed` is now set when milestone planning writes the briefs; `built` is still set at fold-back.
- **The brief's `Deferred:` line** becomes the project-level "decide after it runs" list.
