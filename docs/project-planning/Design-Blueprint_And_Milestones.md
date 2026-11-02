# Design: system design, milestones and owner-led design for large projects

Status: draft (2026-11-01), owner-directed, not from a retro
Touches: `system-design`, `risk-first-roadmap`, `roadmap-plan-next-rung`, `rung`, `code-quality-pass` (project-planning 0.11.2); `tasklist`, `tasklist-run`, `metrics` and `roadmap` tools (task-workflow 0.17.2); `.claude/skills/retro-feedback`; a new design-session skill
Supersedes in part: [Design-Shape_Value_Names.md](Design-Shape_Value_Names.md) (its classes, milestones and checkpoints stay; its ordering moves inside a milestone)

## Problems

The skills implement one approach: a thin design, a ladder ordered by risk and picked by the agent, and design depth added one rung at a time. That fits an exploratory project. For a large project the owner wants the reverse: agree the structure first, let the owner shape it, and grow toward the goal on a foundation. The symptoms:

1. **The agent picks where to go deep, and goes too deep.** FileOrganizerHero: the agent proposed the `foh` CLI and kept detailing it. The owner had to stop it, redirect it to `fohlab` and narrow the design to something manageable. The Overview is 22.6 KB and the Experiment_Lab subsystem doc is 21.3 KB, against "about a page". There is a rule for where to start deepening, but none for where to stop.
2. **The goal's end is reached for before its foundation exists.** AppStorePortal: the agent pushed into the marketing-experiment loop before data collection was solid. The feasibility rung ran 9th (L6, how many weeks to detect a 10–30% effect: "not at this traffic"). The loop itself came about 24th (L12b, record and conclude an experiment). Collecting analytics for the other apps (L15) moved ahead only after that. There were 8 refactor rungs and 2 quality tasklists in 47 ladder lines.
3. **No big-picture view.** The owner sees one rung at a time. Ladder IDs no longer match the order (FileOrganizerHero: L12, L13, L4, L7, L3; milestone M5 before M3), and the roadmap header is a paragraph of re-plan history.
4. **Too many sessions.** Each rung takes a plan session (Opus), a run (Sonnet) and a close session (Opus), then a retro and a re-plan. Over 20–40 rungs that is heavy for the owner and the budget.
5. **The agent drafts and the owner reacts.** The strongest documents in both projects were written by the owner outside the skills (`Vision.txt`, `Strategy/`, `Goal.md`). There is no mode for working a design out together: every answer becomes a formal doc edit, and questions are capped at 3–5. FileOrganizerHero's L11 (confidence bar) was a design session squeezed into a rung.
6. **Labels without names.** "L1 still needs to be decided" and "QR18, QR19, L28 TP5 and TP6, before L10a" can only be read by someone who already knows every ID.
7. **Names are general, inaccurate or esoteric** ("Lab spine", "gate", "stage").
8. **Model choice is unmeasured.** The metrics log has 33 `step` events and none carries a token count. Only build batches are measured (21.0M implementer and 5.8M reviewer tokens over 368 batches). Nothing supports or refutes Opus for planning.
9. **Retro feedback takes manual steps.** The owner asks for the block, copies it and pastes it into another session, possibly on another machine.
10. **Rules pile up untested.** About 40 ledger rows are `untested`. Many patch the "deepen per rung" model.

## Principles (owner, 2026-11-01)

- Agree structure and architecture first. The outcome is the eventual goal.
- Agree only what the current milestone needs, as long as later milestones can grow it by adding, not restructuring.
- Agreement is not permanent. Sometimes the point is to get something going and rework it as the future unfolds.
- Foundation before goal: build what the goal stands on (data, the core model) before the goal itself.
- The owner sets the shape and the order. The agent fills in, checks and proposes.
- Plan once per milestone. Re-plan in the middle only when something breaks the plan.
- Keep long-term token and cost efficiency: little churn, the right model per step, reviews sized to the risk, and feedback the skills can learn from.

## The model: three levels

### 1. System design (`system-design`, replaces the thin Overview)

**Agreed:** subsystems; the seams and interfaces between them; the data model as entities and relationships; build targets; names (seeds `Taxonomy.md`); a short threat and privacy section.

**Field-level review, only for:** database schema, REST and wire APIs, and a library's public symbols. Everything else (internal types, algorithms, thresholds, output formats, UI detail) is the agent's, inside the agreed seams.

**Scope:** the current milestone only. The stopping rule is the **additive check**. Each later milestone keeps one line on what it will add. For each one, ask: can it be added as new entities, endpoints or symbols without restructuring what exists? If yes, stop. If no, decide that seam now, at the smallest depth that makes the future change additive.

**Agreement states:**
- `settled`: expected to hold.
- `working`: good enough to start, rework expected. It names what would make us revisit it.

Reworking a `working` item is planned work, not drift.

**Owner's sketch or agent's first pass, the owner's choice.** When the workspace already holds an owner document (a vision, goal or strategy doc), the skill starts from it. Otherwise it asks once: "sketch it yourself, or shall I take a first pass?" Either way it fills the gaps and marks each item `owner` or `proposed`. A first pass follows the owner preferences (see [Owner preferences](#owner-preferences)) and stops at the additive check like any system design.

**Size:** the system design is bounded by the current milestone, not by a page count. Later milestones are one line each.

**Owner text is checked before saving.** Whenever the owner supplies wording (a sketch, a milestone outcome, exit criteria, a name), the agent offers once to tighten it before saving. It lists each ambiguity: a vague term, a name not in or clashing with `Taxonomy.md`, an exit criterion nobody can check, a conflict with an agreed item. It shows a tightened version beside the original. The owner accepts, edits or keeps the original. The agent never rewrites owner text silently.

### Owner preferences

The agent learns the owner's tastes the way the skills learn from retros: from rulings, with evidence, kept short.

- **Where** (owner, 2026-11-01): a user-level file, `~/.local/state/danny-agent-skills/owner-preferences.md`, for tastes that hold across projects (depth, foundation-first order, small command-line labs, naming style, how options are presented, framework defaults). The project's rules file (`CLAUDE.md` or equivalent) holds project-specific ones (credential limits, domain principles).
- **What is not a preference:** a single ruling (that is a decision in the design docs), and feedback on how the skills behave (that goes to the ledger).
- **What goes in:** a preference enters only after the owner overrides the same kind of `proposed` item twice, or states it outright. Each line has the preference, one example and the date. One ruling is a hypothesis, not a preference.
- **Who writes it:** milestone close and `design-session`'s promote step propose additions in one line each. The owner accepts or declines.
- **Used by:** every first pass (system design, milestone outcomes, names, rung briefs) reads it before drafting.
- **Judged by:** the share of `proposed` items the owner accepts unchanged, per milestone. It should rise as preferences accumulate. Retros report it, so `/retro-feedback` can tell a skill gap from a missing preference.

### 2. Milestone map (`risk-first-roadmap`)

**Milestones are capability layers, ordered foundation first.** AppStorePortal, for example: data in one place → see it → record changes → grade changes.

**Foundation and pillars.** The foundation is the shared base the pillars stand on (the data store, the core model); a pillar is a group of milestones (sometimes one) that together deliver one end-to-end capability toward the goal. The first pillar is the thinnest end-to-end slice that proves the goal's most fundamental capability, spanning several subsystems at minimal depth with manual stand-ins for what is not built yet. Later pillars deepen an existing pillar or add a new direction; at a pillar boundary the agent proposes the next-pillar options with their dependencies and costs, and the owner picks. E.g. a key-value store as a service: sign-in by hand-added API key, the data store, and REST `get` form one pillar; a fuller REST API is the second. The foundation is built only as deep as the next pillar needs, under the same depth limit as the system design; once a pillar is good enough, the foundation is extended for the next pillar as new work in a later milestone, not before. (Owner, 2026-11-01.)

**Each milestone has:**
- an outcome sentence in plain language the owner would use (the agent proposes it, marked `proposed` until the owner accepts it),
- the subsystems it touches,
- exit criteria the owner accepts at a demo,
- its rungs.

**Order.** The owner sets the milestone order. The agent proposes it and flags dependency problems.

**End-of-goal rule.** The goal's own machinery waits until its foundation milestones are done, except a thin end-to-end slice (the first pillar) that uses manual stand-ins or provisional code. "Thin" means no machinery a later pillar will have to rebuild. A **spike**, answering "is it feasible?", may run before that and builds none of the goal's machinery. A spike that answers "no" goes to the owner, as a refuted premise does today.

**Spike code may be kept.** It does not have to be thrown away when it is useful for several milestones. Kept spike code is:
- **marked in the code** with one greppable form: `PROVISIONAL(<RungId>): replace at <MilestoneId> (<milestone name>)`;
- **listed in the system design's "Provisional code" table**: what it is, where it lives, the milestone that replaces it, and what depends on it;
- **kept behind a seam**, so foundation code does not depend on its internals. When foundation code must depend on it, the owner either promotes it to a `working` system design item or the dependency waits.

**Manual stand-ins.** A manual or fake step that replaces a capability a later pillar will build, so the first pillar can run end to end (e.g. an API key added to the database by hand; sets done by hand in the database). Provisional code is preferred when possible: code kept behind a seam beats a hand step. Each stand-in is listed in the system design beside the Provisional code table, one row each: what it replaces, the milestone that replaces it, and how it is done by hand. It is replaced on purpose, by that milestone's planning.

The named milestone's planning session schedules the replacement. `metrics signals` counts the markers at zero tokens and flags a marker whose milestone is already done.

**One sequential order for now.** Each rung carries `Touches: <subsystems>`. That is one line, used by the map view now and needed by parallel rungs later (see [Parallel rungs](#parallel-rungs-later)).

**`Map.md`.** One page generated by the `roadmap` tool at zero tokens: milestones, their rungs as one line each with a name, status and `Touches`. This is the owner's big-picture view. The roadmap file stays the source; the `Updated:` history paragraph goes to the log.

### 3. Rungs (inside the current milestone)

Risk ordering (shape, clock, breadth) applies only inside the current milestone. The owner can pin an order.

**Detail by distance:**

| Distance | Detail |
| --- | --- |
| Current rung | Full brief |
| Rest of the current milestone | Brief written at milestone planning, kept short because the seams are agreed |
| Next milestone | One line plus its additive-check line |
| Later milestones | A name and one line |

**"Decide after it runs" list.** Questions about minutiae (thresholds, exact output shape, polish, internal names) go on a project-level list, filed under the milestone or rung that will settle them. This generalises the rung brief's `Deferred:` line from 0.11.0.

## Cadence

| | Now | Proposed |
| --- | --- | --- |
| Milestone start | Checkpoint rung | Milestone planning session (Opus): checkpoint look-back, design delta for this milestone, every rung's brief, tasklists |
| Each rung | Plan (Opus), run (Sonnet), close (Opus) with retro and re-plan | Run (Sonnet), then an automatic fold-back at the end of the same session (Sonnet), plus metrics |
| Milestone end | Nothing distinct | Milestone close (Opus): re-read, then owner demo and acceptance, one retro, re-plan of the next milestone; it pauses at the demo and, after the owner rules, the next `/rung` resumes the same close, possibly in a new session |
| Re-plan inside a milestone | After every rung | Only when a rung fails, a rung answers a different question, an owner request lands in the current milestone, or a `settled` seam must change |

### Automatic fold-back

Today's close session does three kinds of work in one Opus session:
- **Mechanical:** run the checks, tick the fold-back list, move depth tags, record answers.
- **Comparison:** what was agreed against what was built.
- **Judgment:** which side is wrong, what a drift means for later rungs, re-ranking.

The automatic fold-back keeps the first two in the run session and sends only judgment to an Opus session.

**When:** right after `tasklist-run` commits the rung's last task, in the same Sonnet session, which already holds the tasklist and the run's outcomes.

**Steps:**
1. **Checks.** Run the full test suite, or, when it is slow, only the test targets the rung touched; the full suite then runs at milestone close (owner, 2026-11-01). "Slow" is the project rules' value if they set one, else over about 5 minutes on the last full run. Confirm the rung added a regression test. A failure stops here.
2. **Compare the reviewable surfaces.** Database schema, REST and wire APIs, and public symbols, against the brief and system design. Use the rung's diff (`<Base>..HEAD`); a tool extracts what it can at zero tokens. Also check the brief's `Done when` results and each item on the "decide after it runs" list the rung was to settle.
3. **Classify each difference:**

   | Difference | Action |
   | --- | --- |
   | As agreed | Tick it |
   | Internal only (private types, algorithms, file layout) | One "As built" line; no question |
   | A `working` item reworked as its revisit note foresaw | One "As built" line |
   | A reviewable surface or `settled` item differs; a deferred item has no answer; a `Done when` did not pass; a new `PROVISIONAL` marker not in the system design | **Escalate**: stop, record what differs in an escalation marker on the rung; the next `/rung` runs an Opus review (internal route `escalation`, no owner-facing name) |

4. **Update the docs for the clean cases.** Depth tags, traceability, risks the rung's passed `Done when` answers, answered deferred items, names already agreed into `Taxonomy.md`, and the rung's status in the roadmap. Commit as `Fold back rung <RungId>`.
5. **Report and continue.** One summary line to the owner, a metrics event, and `Next: /rung`. The next brief already exists from milestone planning, so there is no re-plan unless a trigger fired.

**What it never does:** decide which side of a drift is wrong, change a decision, add or reorder rungs, or retire a risk on a partial answer. Those escalate.

**Safety net:** milestone close re-reads every fold-back in the milestone together on Opus, as the first end-to-end fold-back does today. A drift the automatic step missed is caught there at the latest. The escaped-defects metric and the Sonnet-versus-Opus comparison show whether that is too late.

**Expected effect.** Opus sessions go from about two per rung to about two per milestone, plus one per mid-milestone re-plan. This is judged by the metrics below, not assumed.

## Model choice

1. **Measure first.** Extend `metrics tokens` to log planning, close and design sessions from their transcripts, keyed to the `step` event. Zero tokens. Fix the malformed `skill` stamps seen in the log (`0.16.2` with no name, `roadmap-plan-next-rung 0018`).
2. **Hypothesis:**
   - Opus: system design, milestone planning, milestone close, design sessions.
   - Sonnet: rung briefs written against a `settled` system design, fold-back, mid-milestone re-plans that only re-order.
3. **Test.** Plan 2–3 rungs' briefs on Sonnet in the pilot. Compare `Found during` tasks, correction rounds and drift at fold-back with the Opus-planned rungs.

## Names and labels

- **No bare labels for the owner.** In chat, cards, `Next:` lines, the learning log and `Map.md`, every ID is followed by its short name the first time it appears in a message, e.g. "L4 (architecture check before folder suggestions)". Inside design docs, a cross-doc citation keeps the ID and adds the name where it would otherwise be opaque. The `roadmap` tool gains a lookup so the agent does not have to read sections to get names.
- **Titles and component names say what they do**, in the owner's words. Avoid general words (Manager, Engine, Helper, Handler), metaphors not in `Taxonomy.md`, and role names ("gate", "stage", "spine").
- **Names are reviewed as a set** at the system design and milestone planning, against `Taxonomy.md`. This replaces one flag per new name per rung, except for names added mid-milestone.

## Design sessions (new skill)

A separate skill for working a design out with the owner. It can be used at any time: before the system design, during milestone planning, or in the middle of a milestone.

- **It explores without recording.** It writes to a scratch notes file (`<DocDir>/SystemDesign/Sessions/<date>-<topic>.md`), not to the system design. No IDs, statuses or question cap.
- **The owner leads.** The agent offers 2–3 alternative shapes with diagrams, reflects the owner's sketch back, traces consequences (including the additive check against later milestones), catches contradictions and offers a throwaway spike when only running something will settle a question.
- **It ends with a promote step.** The owner picks what goes into the system design (`settled` or `working`), what is parked for a later milestone and what is dropped. Promotion is a normal system design edit and commit. The notes file is then deleted (git keeps it).
- **Model:** Opus.

Name: `design-session` (owner, 2026-11-01).

## Retro feedback inbox

1. **Retros write to an inbox.** `~/.local/state/danny-agent-skills/feedback/inbox/<utc-timestamp>-<skill>.md`, project-neutral as today. A retro prints one line: `retro feedback saved (<n> pending)`. The block is shown only on request.
2. **`/retro-feedback` with no argument reads the inbox.** It processes every pending item and moves each to `feedback/processed/` with the ledger line that handled it. Processed items older than 90 days are purged. Pasting a block still works.
3. **Other machines:**
   - `/retro-feedback export` writes every pending item into one file and moves them to `exported/`. `/retro-feedback import <file>` reads it into the inbox on the other machine.
   - An environment variable for the state directory (for example `DANNY_SKILLS_STATE_DIR`) lets the owner point it at a synced folder instead. The metrics log moves with it.
4. **Cadence.** One retro per milestone plus metrics captured per rung. An unusual rung (failed, re-planned or drifted) still gets a short retro.

## Open items from the last review

| Item | Change |
| --- | --- |
| Regression test per rung | Each rung's tasklist includes at least one test that fails without the rung's change (a tasklist guard rail). Fold-back runs the full suite; a failure stops the automatic fold-back. |
| Threat and privacy pass | A system design section (data handled, where it goes, secrets, trust boundaries), re-checked at milestone planning for the milestone's new seams. |
| Owner accepts the outcome | Milestone close: a demo against the exit criteria, ruled accept, accept with follow-ups or reject. Not per rung. |
| Escaped-defects metric | A bug task cites `Escaped from: <RungId>`; `metrics` counts escapes per rung and per milestone. Collected, not a gate. |
| Untested ledger rules | Reviewed as part of this change. Each row is kept, folded into the new model or retired as obsolete, with one line of reason. |
| Scenario suite | See below. |

## Parallel rungs (later)

Not built now. When the owner asks for parallel rungs in worktrees:
- the roadmap allows several rungs `in progress` and `roadmap next` returns a set;
- rungs run in parallel only when their `Touches` sets do not overlap and the seams between them are `settled`;
- a running rung writes only its own brief and tasklist;
- fold-backs into shared docs (system design, Taxonomy, roadmap) and merges run one at a time, in fold-back order;
- `/rung` may take a rung argument as an alias; no `Next:` line shows one.

This is a change to the tool and `rung`, not to the planning skills. `tasklist-run` already supports worktrees inside one tasklist.

## One command (owner, 2026-11-01)

The owner will not manage several kinds of "close". Every `Next:` line is `/rung` (plus the model switch when the step needs Opus), with prose before it saying what the step is and why. The `roadmap` routes are internal labels. State lives in files (escalation marker on the rung, the handoff note at each wait point, the paused milestone close), and `roadmap next` returns route, one-line reason and model. `/rung` states the model first and stops on the wrong one. A non-interactive step that needs a specific model (escalation review, milestone-close re-read) runs as a subagent on that model inside the current session when that is cheaper than a new session; steps that talk with the owner still need a session on the right model. `/rung` chooses per step by expected context size, says which in one line, and the wrong-model stop applies only when it picks a session.

## Scenario suite

`claude plugin eval` cases in `plugins/project-planning/evals/`. Each case has a fully synthetic fixture project (owner, 2026-11-01; the repo is public), an opening prompt, scripted owner answers and graders. A case is a test of the skills, not a change to them. Running one is one agent session.

The owner reviews each case's scripted answers and pass criteria before its first run, because they encode the owner's judgment. Later cases come from real use. When `/retro-feedback` processes an item that reports an owner redirect or a refuted rule, it proposes a regression case for it alongside the skill edit.

- **Deterministic checks:** files written, doc sizes, question counts, bare IDs, routing.
- **Rubric checks:** a cheap judge model.

First two cases, written before the skill changes:

| Case | Fixture | Passes if |
| --- | --- | --- |
| Over-detail trap | A vision doc for a classifier app, with a tempting deep area (a full evaluation CLI) | The system design covers M1 only; the deep area is one line or parked; no algorithm or field detail outside DB, API and public symbols |
| Foundation before goal | A goal doc for an analytics-driven experiment tool | M1 is data collection; work on the experiment loop appears only as a spike before the foundation milestones are done |

More cases are added from the pilot: owner sketch kept, not replaced; a rung fails; a request lands mid-milestone; a design session promotes some decisions and drops others.

The suite runs at release (with `--ablation none`, since a no-plugin baseline says little here) and costs roughly tens to a couple of hundred thousand tokens per case.

## Rollout

1. Owner reviews this spec.
2. Write the two scenario cases and run them on 0.11.2 for a baseline.
3. Write the new skill text, and review the ledger's untested rows in the same pass. This is a major version: project-planning 1.0.0, with task-workflow bumped for the tool and metrics changes.
4. Run the cases on the new version.
5. Pilot on FileOrganizerHero at its next step: the checkpoint before M2 becomes the first milestone planning session, writing the system design for M2 from the existing Overview, Experiment_Lab doc and `Strategy/`.
6. AppStorePortal follows through adopt mode into a system design, once the pilot has run one milestone.

**Migration.** Existing Overviews and roadmaps are read as they are. The first milestone planning session converts them (system design sections, milestone fields, `Touches` lines, `Map.md`) in a move-mostly commit. IDs never change.

## Judge by

- Owner redirects of over-detailed design per milestone (should fall toward 0).
- Refactor rungs per milestone.
- Opus sessions per rung and per milestone.
- Tokens per planning, close and design session (now measured).
- `Found during` tasks and drift on Sonnet-planned briefs versus Opus-planned ones.
- Escaped defects per milestone.
- Bare-ID messages, from the scenario graders.
- Feedback items processed from the inbox versus pasted.

## Open questions

None. Next step: rollout step 2 (write the two scenario cases for owner review).

## Eval results

Label `g2` (after the system-design rewrite and design-session; the roadmap skill is not yet rewritten), 3 runs per case, judge Sonnet. Baseline is 0.11.2, with the tightened milestone-order grader for foundation-before-goal. Passes out of 3. Cost of g2: $10.84 including the lost runs (the over-detail-trap re-run, $3.95, replaced three runs lost to a usage-limit error).

Label `g3` (after T8, T9, T10, T14, T32 and T33), same settings. Cost of g3: $13.97 including the lost runs (the first full run, $9.56, lost two over-detail-trap runs to a weekly usage-limit error, and the over-detail-trap re-run, $4.41, replaced all three of that case's runs). `demo-stop-handoff` is new in g3 and has no earlier column: close-paused 3/3, handoff-gitignore 3/3, handoff-resumable 3/3, handoff-written 3/3, handoff-ignored 3/3, stop-message 0/3, score (mean) 0.82. These are the re-scored values: the g3 run first read handoff-ignored 0/3, stop-message 1/3 and mean 0.79, because the grader lacked `min: 0` (see g3 findings).

| Case | Grader | Baseline | g2 | g3 |
| --- | --- | --- | --- | --- |
| over-detail-trap | design-depth | 0/3 | 1/3 | 0/3 |
| over-detail-trap | milestone-scope | 0/3 | 0/3 | 2/3 |
| over-detail-trap | design-skill-used | 3/3 | 3/3 | 3/3 |
| over-detail-trap | files-written | 3/3 | 3/3 | 3/3 |
| over-detail-trap | summary-names-ids | 2/3 | 3/3 | 1/3 |
| over-detail-trap | score (mean) | 0.33 | 0.50 | 0.47 |
| foundation-before-goal | milestone-order | 0/3 | 2/3 | 3/3 |
| foundation-before-goal | perishable-first | 1/3 | 2/3 | 3/3 |
| foundation-before-goal | summary-names-ids | 1/3 | 1/3 | 2/3 |
| foundation-before-goal | design-skill-used | 3/3 | 3/3 | 3/3 |
| foundation-before-goal | files-written | 3/3 | 3/3 | 3/3 |
| foundation-before-goal | score (mean) | 0.37 | 0.67 | 0.93 |

No grader regressed (g2). Still failing, and the failures are real:
- **milestone-scope 0/3.** All three roadmaps make M1 the whole measurement lab (two methods, combined score, threshold sweep, sibling confusion), and two add architecture-checkpoint rungs the new planning terms no longer use. Likely cause (a reading of the outputs): the design itself sizes M1 from the vision's FR3/FR4, and the unrewritten roadmap skill keeps the old rung and checkpoint rules.
- **design-depth 1/3.** Runs 0 and 2 design a combiner and a threshold sweep inside M1 and fix a weighted sum (D8); run 1 passed. Likely cause: the design's M1 is too wide, so "only the current milestone" is applied to an oversized M1. Narrowing M1 is a roadmap and design-session concern, not a design-depth detail problem.
- **summary-names-ids 1/3 (foundation-before-goal)** is unchanged; cause not investigated (the closing summary is the roadmap skill's, which G2 did not touch).

Judge doubt (g2): foundation-before-goal milestone-order run 0 failed 1 pass to 2 fail, but M1 there is data collection and the only offender is L7, a read-only readout spike over collected data tagged M3 ("L7 - Spike: on days with no known change, how often does a before-and-after comparison 'find' an effect..."), which the grader's last bullet allows. Treat that FAIL as a judge error. The milestone-order grader is not too strict after the fbg2 tightening: the other two runs passed 3 of 3 votes.


### g3 findings

Regressions against g2 (both on over-detail-trap, n=3 so partly noise; causes marked speculative are guesses, not checked):
- **summary-names-ids 3/3 to 1/3.** Run 0 passed; run 1 and run 2 failed. Run 2's summary says "moved to M2 (decision D9 in the system design)" with D9 and M2 given no name, a real failure. Run 1's FAIL is a confirmed judge error (all three votes FAIL): the only identifiers in its summary are D10 and Q1, and each comes with its meaning at first mention (the milestone-2 move of title keywords, combined score, threshold sweep and sibling confusion, then "recorded as decision D10"; "does contacting a bookmarked site count as 'leaving the Mac'? This is open question Q1"); every milestone is named. So the real count is likely 2/3, not 1/3. Cause of run 2's failure (speculative): the closing summary is the roadmap skill's, which is still unrewritten.
- **design-depth 1/3 to 0/3.** All three Overview.md docs failed. Read by hand: run 1 fails rightly (line 64 gives Title Keyword "weighted by how distinctive a word is across folders", and line 87 signs `CombinedSuggester(parts: [FolderSuggester])`, both M2 detail). Run 0 is borderline: R7 spells out a tuning procedure ("tune on half the filed bookmarks and measure on the other half") and D5 plans thresholds. Run 2 looks like a wrong FAIL (my judgment, not confirmed): line 66 "M1: Domain Method only (D9)", the field-level surfaces on line 85 and 86 are M1 only, later methods are one-line milestone rows, and the only later-scope extras are the glossary terms "Auto-file threshold" and "Threshold sweep" (lines 108 and 109). The grader notes that LLM judges are noisy on long files. Cause (speculative): M1 is now narrow (D9, D10) but the design still sketches later suggesters; narrowing M1 improved milestone-scope (0/3 to 2/3) without fixing depth.

Improvements: milestone-scope 0/3 to 2/3, milestone-order 2/3 to 3/3, perishable-first 2/3 to 3/3, summary-names-ids on foundation-before-goal 1/3 to 2/3.

demo-stop-handoff, re-run after the grader fix (a fresh sample, not a re-score of the original g3 runs):
- **handoff-ignored was a grader defect, now fixed.** The grader (evals/demo-stop-handoff/graders/handoff-ignored.md) is `type: tool_used`, `tool: Bash`, `input_match: 'git\s+(add|commit)[^"&;|\n]*Handoff'`, `max: 0`. It had no `min`, so the range 1..0 could never be met; the g3 runs all read "Bash called 0x (expected 1..0)". `min: 0` is now set, and the re-run reads "Bash called 0x (expected 0..0)" and passes 3/3. The g3 traces were no longer on disk and the CLI has no re-grade command, so the case was re-run with `--case` (results in plugins/project-planning/evals/results/g3-dsh.json, untracked). Re-run cost: $1.35 for the runs, $1.46 with judges.
- **stop-message 0/3 on the re-run (g3 had 1/3; the runs are different samples).** Judge votes were FAIL PASS FAIL, FAIL FAIL FAIL and FAIL FAIL FAIL, and the judges gave no reasoning, so the causes below are my reading of the final messages (speculative). All three end with the exact `Next: /rung (Opus: /model opus)` line and name the handoff note, so the remaining miss is likely the grader's first bullet, "without needing any file opened": each message sends the owner to `Documentation/Handoff/milestone-close-M1.md` for the detail of the ruling. The g3 run 2 miss (ending "Next: run `/rung` once you have a ruling...") did not recur. Run 0's earlier bare-ID concern (R1, R2 labels) was not re-checked.
