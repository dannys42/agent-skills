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

Since 0.5.0 the rung retro also reads the task-workflow metrics log through `metrics summary` (run numbers against the median of earlier rungs) and `quality`/`quality_outcome` events from `code-quality-pass`. Otherwise evidence comes from the retrospective's feedback block (`retrospective.md` in `roadmap-plan-next-rung`): design-doc line counts before and after, questions asked and answers that changed the draft, assumptions overturned at fold-back, drift between brief and code, `Found during`/`INVALID`/`SUPERSEDED` tasks and raised `Model` tiers in the rung's tasklist, subsystem promotions, diagram render failures, missing-sibling notices.

## Change log (hypotheses under test)

| Version | Change | Hypothesis | Evidence | Judge by | Status |
| --- | --- | --- | --- | --- | --- |
| 0.5.0 | `code-quality-pass`: Tier 1 tidy at fold-back, Tier 2 review every `Every:` rungs or on a trigger, both optional and never blocking | Periodic cleanup keeps later rungs cheaper (fewer rounds, smaller diffs) at a cost the user can see | guess (owner request; one project at 17 rungs with no review) | `quality` events: cost per pass; `metrics summary` rounds, lines and implementer tools on the 3 rungs before versus after; accepted-proposal share in `quality_outcome` | untested |
| 0.5.0 | Signals and triggers from `metrics signals` (no tokens): interval, no-baseline, rung diff over 2x median, fourth file of one shape, new mirrored types, new subsystem doc | Cheap detection of when a review is due, including on adopted projects | observed (first real run: both known mirrored pairs found; rung-size fired on a 2,571-line rung against a 968 threshold; per-feature families like `*Runner` need `Accepted shapes`) | triggers fired versus proposals accepted from the review they prompted | untested |
| 0.5.0 | One rung retro (design, runs, quality) in a fixed one-screen format; "none" lines omitted; tooling line with the 8%/3% rule | Retros easier to read and act on | observed (owner request) | retro length; share of retros ending in a single line | untested |
| 0.3.0 | Outline-first: `system-design` writes a one-page Overview by default | A thin outline is enough to order a roadmap; detail written up front is mostly wasted or wrong | guess (user preference against top-heavy specs) | Overview lines at sign-off; rungs re-planned because the outline missed something | untested |
| 0.3.0 | Subsystem docs on demand, parents see only the Contract | Bounded docs stay read and updated; no doc grows forever | measured (1 run: new subsystem doc 93 lines, met a trigger; Overview +2) | Overview lines across rungs; subsystem promotions that met a trigger versus ones that did not; parent edits outside Contract changes | supported (3 runs, weak: Overview +1, subsystem doc 93 to 98; run 4: new subsystem doc 74 lines, Overview +2 across plan and fold-back; trigger status not reported) |
| 0.3.0 | Per-rung brief before the tasklist | The brief prevents tasks from guessing scope and interfaces, at less cost than a full design | measured (1 run: brief 121 lines, 14 tasks, 13 passed review first time, 1 correction round, 2 backfills, 0 invalid/superseded/tier raises) | `Found during` tasks and rework per rung; brief length; questions that changed the draft | supported (run 3: 16 tasks, 6 added after first real run, 0 invalid/superseded, all 7 assumptions and 3 decisions confirmed; rework traced to one unverified external-behaviour assumption; brief 123 lines, over a page again; run 4: brief 87 lines, 2 tasks added, one from an unchecked data-shape assumption, correction was one decision row; the second run in a row where rework traced to an unverified assumption) |
| 0.3.2 | Brief Components step names shared vocabulary (codes, ids, formats) and absent-input behaviour for new endpoints | Two brief gaps seen in one run (unreconciled error codes, unspecified no-connection behaviour) would have landed in the first tasks instead of a backfill | observed gap (1 run: 1 of 14 tasks was a backfill for it); fix effect is guess | `Found during` tasks about shared vocabulary or missing-input behaviour on rungs with a new boundary; brief length (no growth beyond a line or two) | untested |
| 0.3.1 | Trivial-rung skip no longer limited to one component; decisions recorded in a detail doc count as settled | The intent is "no open decisions", not component count; skipping the brief is safe then | observed (1 run: 4 tasks, 0 correction rounds, 0 `Found during`, 0 tier raises; tasklist Context carried all decisions) | Skipped-brief rungs: `Found during` tasks, correction rounds, questions asked after build | supported (1 run, weak) |
| 0.3.1 | Fold-back with no brief compares against cited doc and tasklist | Fold-back should not assume a brief exists | observed (1 run) | Drift found in no-brief fold-backs versus brief ones | untested |
| 0.3.0 | Fold-back after each rung | Docs stay true to the code, so the next brief starts from fact | observed (run 1: 1 real drift, 4 gaps the design had not specified; Overview +1 line, architecture doc +12). measured (run 2: 5 detail drifts, 0 structural, all fixed in docs; Overview +2 lines; 5 docs edited) | drift found per fold-back; assumptions overturned; whether the next brief had to correct the docs | supported (3 runs; run 3: 4 detail drifts, all fixed in docs, one reversed a guard rail) |
| 0.3.3 | Unverified assumption about an external system that later tasks depend on gets one real call as the first task, or a stated reason not to | Building dependent logic before the first real call is what caused the rework in one run | observed (1 run: overturned assumption, 6 of 16 tasks added after the first real run); fix effect is guess | `Found during` tasks about external behaviour on rungs with an unverified external assumption; whether the first-call task appeared and its result | untested |
| 0.3.4 | The 0.3.3 first-real-call rule also covers a property of real data; check now when a read-only look is cheap | A data-shape claim stated as fact was overturned by the first real run, the same failure as the external-behaviour one | observed (run 4, 0.3.2: "every day has a row" never checked; 1 of 2 assumptions overturned, 1 of 2 added tasks); fix effect is guess | `Found during` tasks from a data-property assumption; whether the planner checked or tagged it before agreement | untested |
| 0.3.3 | "The brief is short" counts per-component tables toward the page, one line per component | Brief overruns come from tables; tasks do not cite every row | measured (2 runs: 121 and 123 lines vs about a page); fix effect is guess | Brief lines on the next rungs (target under about 100); `Found during` tasks about interfaces the brief omitted | untested |
| 0.3.0 | IDs per document, qualified across docs (`Puzzle_Generator:R3`) | Avoids a folder-wide counter while keeping citations unambiguous | guess | ID collisions or broken citations reported | untested |
| 0.3.0 | Retrospective with a project-neutral feedback block | Gives this ledger evidence without project detail | guess | share of retros with `measured` points; feedback blocks received | untested |
| 0.3.0 | Graceful fallback when a sibling skill or linked file is missing | Standalone installs keep working | guess | missing-sibling notices and whether the fallback output needed rework | untested |
| 0.3.0 | Cross-doc traceability: each doc owns its requirements; `(doc pending)` coarse coverage | Requirements stay traceable without the Overview growing | guess | gaps found late; `(doc pending)` rows left unrefined after the subsystem doc exists | untested |

## Collect next run

Claims that need evidence before any change. Each: claim, tier, source version, what would settle it.

- Does skipping the brief hold on rungs with open decisions or three or more components? Need `Found during`/correction counts from a skipped-brief rung of that size. (observed, 0.3.0)
- Do fold-back drift tables inflate the architecture doc? Run 1 +12 lines; run 3 Overview +1, subsystem doc +5, so growth looks small. Keep one more count before dropping this. (measured, 0.3.2)
- Did the user-visible gap found after the rung (error code dropped on a 404) belong in the rung's verification? Check whether skipped-brief rungs miss verification items a brief would list. (observed, 0.3.0)
- Brief length: 121 and 123 lines in two runs against "about a page"; run 4 was 87 at planning and 94 after fold-back (written before the 0.3.3 nudge). Are some lines unused by the tasks? Count brief lines and the sections the tasks cited after the 0.3.3 nudge. (measured, 0.3.2)
- Early read-only dry run of new logic on real data, before the surfaces are built, when a rung ends in a real-data run: a refusal rule tuned on synthetic data failed only at the user step, after API, CLI and client were built. Overlaps the 0.3.3/0.3.4 first-real-call rule; see whether that rule alone moves the real run early. If real-data runs still land last on a rung with a 0.3.4 brief, add a Verification line. (observed, 0.3.2)
- "Requirements touched" duplicating the roadmap rung's requirement list, proposed to collapse to one line. The pasted rationale was truncated and no counts were given. Need: lines of that section and whether tasks or fold-back cited it, on the next two briefs. Section says what the rung proves of each requirement, which the roadmap does not. (guess, 0.3.2)
- Guard rails that freeze a contract: one was reversed at fold-back (resolved by updating docs, no rework). Proposed fix was to state what evidence would lift the freeze. Does a reversal cost anything beyond a drift line? Repeat before adding a rule. (observed, 0.3.2)
- "Reuse X" lines in a brief hid a visibility change on the reused symbol. Repeat before adding a rule (observed, 0.3.1).
- Fold-back inputs: whether numbers observed in a real-data verification belong in fold-back as an explicit input. No evidence yet that docs were wrong for lack of them; step 2 already compares verification results. (guess, 0.3.1)

## Parked

- Tasklist-side suggestions (reviewer tier for additive migrations, auto-computed metrics lines/files, a "visible gap noted, not scheduled" field): belong to task-workflow, not this plugin; send through `/tasklist-feedback`. Reviewer-tier claim is observed, 1 run.
- Committing planning files before the first batch (guess): not a rule.

## Rejected

- None yet.

## Feedback received

Append one line per feedback drop: date, source (skill and version, project kind, rung or design retro), what was taken, what was parked.

- 2026-10-15, roadmap-plan-next-rung 0.3.0 and risk-first-roadmap 0.3.0, adopted macOS client plus server, rung retro: took the trivial-rung wording and no-brief fold-back (0.3.1); parked tasklist-run items for `/tasklist-feedback`.
- 2026-10-15, roadmap-plan-next-rung 0.3.1, adopted local server plus client app, design retro (second run): took one merged line on shared vocabulary and absent-input behaviour (0.3.2); collected brief length, "reuse" visibility, and architecture-doc growth; did not take the fold-back "observed numbers" edit (no evidence). The pasted block was truncated in several lines; the summary was used for the missing facts. Questions asked were not observed, so the question-count hypotheses stay untested.
- 2026-10-16, roadmap-plan-next-rung 0.3.2, adopted Swift server plus macOS client, rung retro (third run): took the first-real-call-for-unverified-external-assumption rule and the brief-tables nudge (0.3.3); collected the frozen-contract evidence idea; the guess that a first call removes most rework stays a guess. Block was truncated in one line. Tasklist and tasklist-run were named but no suggestions given.
- 2026-10-16, roadmap-plan-next-rung 0.3.2, adopted Swift server plus macOS client, rung retro (fourth run, a later rung, still on 0.3.2): took the real-data-property clause on the first-real-call rule (0.3.4); collected the early dry-run and the "Requirements touched" collapse. Owner answers (3, all confirming a default) were a guess, so question-count hypotheses stay untested. Keep points (assumption IDs, fold-back checklist, pure-function guard rail) support the brief and fold-back rows. Block truncated in several lines; the third suggestion's rationale was lost. Tasklist named, version unknown, no suggestions.

## Open questions

- Is a one-page Overview enough for adopt mode on a large codebase, or does the `Doc: pending` list itself grow too long?
- Does the 3–5 question limit fit rung briefs, or do most rungs need fewer?
