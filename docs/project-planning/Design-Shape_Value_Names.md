# Design: shape, value and names in the project-planning plugin

Status: agreed (2026-10-26), owner-directed, not from a retro
Touches: `risk-first-roadmap`, `roadmap-plan-next-rung`, `rung`, `system-design`, `code-quality-pass` (project-planning 0.8.9)

## Problems

1. **No forward look at the architecture.** Rung briefs design only what a rung touches, and `code-quality-pass review` looks back at code already built. Nothing asks "does this shape hold for what comes next?" before the next area is built on it. AppStorePortal: five refactor rungs (L22, L23, L34, L35, L42) found after the fact; design spread over `Architecture-`, `Design-`, `Overview.md` and `SystemDesign/`.
2. **Ordering misses two forces, and goals go too deep too early.**
   - *Perishability.* L3's "Why this order" already records that "analytics data cannot be backfilled", yet finishing ingestion for the other apps (L15) moved ahead only on 2026-10-26, after L6, L12a, L12b, L13a, L27–L30. The ranking is impact × uncertainty, with no cost-of-delay term.
   - *Shape versus completion.* The method says "smallest slice", but it never says which unknowns change the system's shape (and so come first) and which are breadth inside a proven shape (and so grow later). Right: a database app does not need its whole schema first. Wrong: experimentation went deep before its prerequisite (complete ingestion) was in place.
   - *A "no" never trims a branch.* L6 found that experiments could not detect effects at this traffic, and L20 found impressions "marginal". The experimentation branch kept growing anyway.
   - *Requests arrive as designs.* Mid-roadmap owner requests land in the Horizon as design paragraphs (17 KB of a 47 KB roadmap).
3. **Value is not ordered at all.** Risk-first ordering never asks "what is the thinnest path to something the owner can use?"
4. **Names are coined without review.** New database, domain, wire and type names reach code before the owner sees them (ledger: "new public names", "names-review glossary").

## Principles (owner, 2026-10-26)

- Find the components that decide the shape of the system, and answer those first.
- Then do the absolute minimum to exercise that shape end to end.
- Grow organically from there, one milestone at a time.
- Work that loses value with every day of delay (data that cannot be backfilled, an external window) is pulled forward. Completing it beats depth on a later goal.
- A checkpoint is offered as the default next step, and the user can always override it.

## Changes

### A. Ordering (`risk-first-roadmap`, "How to order the rungs")

Tag each unknown with one of three classes:

- **shape**: its answer would change components, boundaries, data flow or the persistence model.
- **clock**: delay loses something that cannot be recovered.
- **breadth**: more of a shape that is already proven.

New order:

1. Skeleton.
2. **Shape** unknowns, each at its cheapest slice, until the shape has run end to end once.
3. **Clock** items: start each clock at its earliest slice, and finish coverage before breadth or later milestones.
4. **Breadth**, milestone by milestone.

Impact × uncertainty still ranks within a class.

The database case becomes the worked counter-example. The first table is shape, because it proves the persistence model. The rest of the schema is breadth, added by the rungs that need it.

**Branch trimming.** When a rung answers "no" to the premise of a milestone, the re-plan demotes that milestone's remaining rungs to `deferred` and asks the owner to keep, reshape or drop the milestone. It does not keep detailing those rungs.

### B. Milestones (value)

- **Where they live.** The roadmap gets a `## Milestones` section. Each milestone is one line: an outcome the owner can use ("I can see 12 months of every app's data"), the capabilities it needs, and its status.
- **Ordering.** Milestones go by value, after their prerequisites. Rungs go risk-first inside the current milestone. Each rung carries `Milestone: M<n>`.
- **Detail horizon.** Only the current milestone's rungs are detailed. Later milestones stay one line, with no rungs listed yet.
- **New smell.** A rung that serves a later milestone while the current milestone is still open is a smell, unless the rung is shape or clock work.
- **Next step.** After the skeleton, the roadmap names the thinnest path to milestone 1.

### C. Intake for new requests

A request that arrives mid-roadmap goes through four steps:

1. Map it to a milestone, or propose a new milestone.
2. List its prerequisites and classify them (shape, clock or breadth).
3. Add one Horizon line.
4. Put any design detail the owner already gave in `ParkedIdeas-<Topic>.md`, unedited, so nothing is lost and nothing gets designed early.

Horizon items are capped at one line, which applies the "Horizon growth" item already in the ledger.

### D. Checkpoint rungs

- **Shape.** A checkpoint is a rung with `Kind: checkpoint` and the question "Does the current architecture hold for milestone M<n>?"
- **Placement.** The roadmap places one when shape work is done (the first full end-to-end run), and one before each new milestone starts. A fired `code-quality-pass` review trigger also prompts one.
- **What it does.** It runs `code-quality-pass review` (backward-looking) plus a forward pass over the next milestone's components. The output is decisions, a reconciled Overview (one design home, not several), and refactor rungs placed by the usual rules.
- **How it is offered.** `/rung` and the re-plan's `Next:` line offer it as the default (`Next: /rung → checkpoint L44 (or skip: /rung → plan L45)`). Skipping it is a one-word override and is logged.

### E. Names (small now, glossary later)

Every new name of these four kinds goes under "Needs your attention" in the brief, as a flagged assumption:

- database schema names
- domain terms
- wire fields
- type names

Each flagged name comes with 2–3 candidates, the nearest existing name, and any synonym or overloaded clash. Internal identifiers are never flagged.

Whether a project glossary (AppStorePortal's `Taxonomy.md`) becomes a plugin standard waits until it has been used for a few rungs.

## Decisions (owner, 2026-10-26)

- **D1: who runs a checkpoint.** A new `checkpoint` mode in `system-design`, which owns the Overview and already has adopt mode. It calls `code-quality-pass review` as input.
- **D2: the ideas file.** `<DocDir>/ParkedIdeas-<Topic>.md`.
- **D3: roadmaps that already exist.** Offer a one-time re-plan that adds milestones and classes. Never apply it silently.

## Ship plan

- **0.9.0** brings A, B, C and E:
  - `risk-first-roadmap` SKILL.md and roadmap-example.md: the classes, milestones and the database counter-example.
  - `roadmap-plan-next-rung` and presenting-for-review.md: the names flag.
  - The `roadmap` tool lint has to accept the new `## Milestones` section and the `Milestone:` line. Check this before shipping.
- **0.10.0** brings D: checkpoint rungs (`risk-first-roadmap`, `rung` routing, `system-design`, `code-quality-pass`).
- **Cost.** These add rules that run every time (ledger rule 3). To offset them, cut the "Why this order" prose in roadmap-example.md, since the classes now carry that reasoning.
- **Dry run.** Before shipping, re-plan AppStorePortal's roadmap on paper under 0.9.0 (no file changes) and check that:
  - ingestion completion (L15, L10b, L38–L40) sorts ahead of further experimentation work;
  - L6's and L20's "no" answers would have trimmed the experimentation branch;
  - the milestones read as things the owner can use.

## Dry run: AppStorePortal under 0.9.0 (paper, 2026-10-26)

No project files changed.

- **Milestones, drafted from `Goal.md`.**
  - M1: I can see every app's App Store data on one timeline ("one data layer").
  - M2: I can record and conclude a manual experiment honestly.
  - M3: semi-automated and PPO.
- **Clock items found:**
  - analytics for every app (L15; Apple keeps no backfill);
  - price snapshots (L39; Apple keeps no price history);
  - backup of Raw (L11; the archive of unrecoverable data has no copy).

  Under the new order, all three rank ahead of L12a, L12b, L13a and L27–L30.
- **Breadth:** reviews (L10a; Apple keeps the history), subscriptions derived from Raw (L10b), the coverage report (L40), and most of the catalog (L38).
- **Branch trimming:** L6's "not at this traffic" would have deferred M2's open rungs and asked the owner to rule. The owner may well have reshaped M2 into "record and conclude honestly" (which is what L12b became), but with a ruling instead of by drift.
- **Result:** criteria 1 and 3 pass. Criterion 2 passes as "forces a ruling", not as "blocks".
- **Open point.** Classing was not always obvious. L38 mixes current-state catalog data (breadth) with anything Apple drops over time (clock). Expect owner rulings on class at the one-time re-plan.

## Judge by

| Change | Signal |
| --- | --- |
| A | Clock items and their completion rank ahead of later-milestone breadth. Whether refactor rungs per milestone fall over the next ~5 rungs. |
| B | Rungs serving a later milestone while the current one is open. Owner reorders at review. |
| C | Horizon size as a share of the roadmap. Design detail written for items more than one milestone ahead. |
| D | Checkpoints taken or skipped. Refactor rungs found by a checkpoint versus found later by a tidy. |
| E | Names renamed after the build. Flagged names per brief (target: a handful, not dozens). |
