# project-planning feedback ledger

The standing brief for refining `system-design`, `risk-first-roadmap`, and `roadmap-plan-next-rung` (in `plugins/project-planning/`) from real-run feedback. The `/roadmap-feedback` skill reads this first and updates it after every round. Keep it short and factual; it is working state.

## Objective

Keep system design thin, incremental, and accurate, at low token cost. Thin: design docs stay about a page each and no doc grows without bound. Incremental: detail arrives per rung, only for what the rung touches. Accurate: the docs describe what was built (fold-back), and the brief carries enough that the rung's tasks do not have to guess. Cost: every line in a skill is read on every run, and every question asked costs the user time.

## Rules for changing the skills

1. **Evidence tiers.** Tag every incoming claim `measured` (counted from docs, tasklists, or git), `observed` (seen in one session), or `guess`. Guesses never become rules; at most they become something to collect.
2. **One run is a hypothesis.** A change backed by one run ships only if it is cheap (a line or two), reversible, and has a named "Judge by" signal. Otherwise collect and wait for a second run.
3. **Every rule costs tokens in every run.** Prefer deleting or tightening a rule over adding one.
4. **Protect accuracy.** Do not thin the brief, skip fold-back, or drop a question category to save tokens without evidence that tasks did not have to fill the gap (no rise in `Found during` tasks, rework, or drift).
5. **Prefer collect over apply** when waiting one run is cheap. Claims that need evidence go under "Collect next run".
6. **No scripts or mandatory fields** without measured savings.
7. **Ship mechanics.** Bump the version in all four `plugins/project-planning` manifests (`.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `gemini-extension.json`) and in `.claude-plugin/marketplace.json`; add a `CHANGELOG.md` entry; record the change below with its "Judge by" signal.

## Signals available

No metrics log. Evidence comes from the retrospective's feedback block (`retrospective.md` in `roadmap-plan-next-rung`): design-doc line counts before and after, questions asked and answers that changed the draft, assumptions overturned at fold-back, drift between brief and code, `Found during`/`INVALID`/`SUPERSEDED` tasks and raised `Model` tiers in the rung's tasklist, subsystem promotions, diagram render failures, missing-sibling notices.

## Change log (hypotheses under test)

| Version | Change | Hypothesis | Evidence | Judge by | Status |
| --- | --- | --- | --- | --- | --- |
| 0.3.0 | Outline-first: `system-design` writes a one-page Overview by default | A thin outline is enough to order a roadmap; detail written up front is mostly wasted or wrong | guess (user preference against top-heavy specs) | Overview lines at sign-off; rungs re-planned because the outline missed something | untested |
| 0.3.0 | Subsystem docs on demand, parents see only the Contract | Bounded docs stay read and updated; no doc grows forever | guess | Overview lines across rungs; subsystem promotions that met a trigger versus ones that did not; parent edits outside Contract changes | untested |
| 0.3.0 | Per-rung brief before the tasklist | The brief prevents tasks from guessing scope and interfaces, at less cost than a full design | guess | `Found during` tasks and rework per rung; brief length; questions that changed the draft | untested |
| 0.3.1 | Trivial-rung skip no longer limited to one component; decisions recorded in a detail doc count as settled | The intent is "no open decisions", not component count; skipping the brief is safe then | observed (1 run: 4 tasks, 0 correction rounds, 0 `Found during`, 0 tier raises; tasklist Context carried all decisions) | Skipped-brief rungs: `Found during` tasks, correction rounds, questions asked after build | supported (1 run, weak) |
| 0.3.1 | Fold-back with no brief compares against cited doc and tasklist | Fold-back should not assume a brief exists | observed (1 run) | Drift found in no-brief fold-backs versus brief ones | untested |
| 0.3.0 | Fold-back after each rung | Docs stay true to the code, so the next brief starts from fact | observed (1 run: 1 real drift, 4 gaps the design had not specified; Overview +1 line, architecture doc +12) | drift found per fold-back; assumptions overturned; whether the next brief had to correct the docs | supported (1 run) |
| 0.3.0 | IDs per document, qualified across docs (`Puzzle_Generator:R3`) | Avoids a folder-wide counter while keeping citations unambiguous | guess | ID collisions or broken citations reported | untested |
| 0.3.0 | Retrospective with a project-neutral feedback block | Gives this ledger evidence without project detail | guess | share of retros with `measured` points; feedback blocks received | untested |
| 0.3.0 | Graceful fallback when a sibling skill or linked file is missing | Standalone installs keep working | guess | missing-sibling notices and whether the fallback output needed rework | untested |
| 0.3.0 | Cross-doc traceability: each doc owns its requirements; `(doc pending)` coarse coverage | Requirements stay traceable without the Overview growing | guess | gaps found late; `(doc pending)` rows left unrefined after the subsystem doc exists | untested |

## Collect next run

Claims that need evidence before any change. Each: claim, tier, source version, what would settle it.

- Does skipping the brief hold on rungs with open decisions or three or more components? Need `Found during`/correction counts from a skipped-brief rung of that size. (observed, 0.3.0)
- Do fold-back drift tables inflate the architecture doc (+12 lines here)? Track doc growth per fold-back; consider capping the table to contradictions. (measured, 0.3.0)
- Did the user-visible gap found after the rung (error code dropped on a 404) belong in the rung's verification? Check whether skipped-brief rungs miss verification items a brief would list. (observed, 0.3.0)

## Parked

- Tasklist-side suggestions (reviewer tier for additive migrations, auto-computed metrics lines/files, a "visible gap noted, not scheduled" field): belong to task-workflow, not this plugin; send through `/tasklist-feedback`. Reviewer-tier claim is observed, 1 run.
- Committing planning files before the first batch (guess): not a rule.

## Rejected

- None yet.

## Feedback received

Append one line per feedback drop: date, source (skill and version, project kind, rung or design retro), what was taken, what was parked.

- 2026-10-15, roadmap-plan-next-rung 0.3.0 and risk-first-roadmap 0.3.0, adopted macOS client plus server, rung retro: took the trivial-rung wording and no-brief fold-back (0.3.1); parked tasklist-run items for `/tasklist-feedback`.

## Open questions

- Is a one-page Overview enough for adopt mode on a large codebase, or does the `Doc: pending` list itself grow too long?
- Does the 3–5 question limit fit rung briefs, or do most rungs need fewer?
