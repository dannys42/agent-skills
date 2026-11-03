# Tasklist — Blueprint and milestones redesign

Source: [Design-Blueprint_And_Milestones.md](Design-Blueprint_And_Milestones.md) (owner-ruled 2026-11-01; its decisions are settled, do not reopen them). Evals: `plugins/project-planning/evals/` (baseline on 0.11.2: over-detail-trap 0.4/0.4/0.2, foundation-before-goal 1.0/0.5/0.2, the 1.0 a false pass fixed by T1). Ledgers: `docs/project-planning/feedback-ledger.md`, `docs/task-workflow/feedback-ledger.md`. Diff against the commit that adds this file.

Standing context for every task:
- Write skill text in the house style: plain sentences, no bare IDs shown to the owner, every line earns its tokens (ledger rule 3).
- Terms come from `plugins/project-planning/skills/system-design/references/terms.md` (written by T2). Cite it, do not redefine a term.
- The design doc keeps its path `<DocDir>/SystemDesign/Overview.md` and is called the system design in skill text. The path stays so existing projects, `next.sh`, the `roadmap` tool and the eval graders keep working.
- Each skill that logs a `step` event keeps its version stamp as set by `scripts/bump_version.py`. Do not bump versions before T22.
- Owner reviews: before each `USER` review task, its preparation task writes `docs/project-planning/Review-<UserTaskId>.md` in the shape of `plugins/project-planning/skills/roadmap-plan-next-rung/references/presenting-for-review.md` (as updated by T24): the decisions the reviewed content makes, important ones in a callout first, then notable, then small; every decision with options, a pro and a con each, and a recommendation (or "no recommendation" and why); a closing question. The notes name each decision in plain words with the file and section it lives in, never a bare ID.
- Eval command (one case: add `--case <name>`): `claude plugin eval plugins/project-planning --runs 3 --scaffold --trust-plugin --allow-tools Bash Write Edit --ablation none -j 3 --no-publish --threshold 0 --judge-model sonnet --max-cost-usd 15 --json plugins/project-planning/evals/results/<label>.json`. Results stay out of git.

### G1 Baseline and vocabulary

- [x] T1 Tighten the milestone-order grader and re-score the baseline
  - Model: standard (Sonnet 5.5)
  - Context: In `plugins/project-planning/evals/foundation-before-goal/graders/milestone-order.md`, add to the Fail line: "Fail if the first milestone's outcome is running or reading an experiment, even when data collection is listed as what it needs." The 0.11.2 baseline passed a run whose M1 was "I can run one product-page experiment" (owner-approved fix, 2026-11-01). Re-run that case on the current skills with label `baseline-0.11.2-fbg2`.
  - Done when: the grader line is committed, and the commit message gives the three new scores with the per-grader passes; the run that has an experiment as M1 now fails milestone-order.

- [x] T24 Order every review by importance, with options for every decision
  - Model: heavy (Opus 5.5)
  - Context: Owner request, 2026-11-01. Update `plugins/project-planning/skills/roadmap-plan-next-rung/references/presenting-for-review.md`. Today only flagged items (at most 5) get options with a pro and con; the rest show a default in the calling skill's order. Change: (1) every decision gets two or three options, each with a one-line pro and con, and a recommendation, or "no recommendation" with the reason; a decision with no real alternative says so in one line. (2) Items are grouped by tier and sorted within a tier by the cost of getting them wrong: **important** (the callout, at most 5; more qualify, say how many), **notable**, **small** last. (3) Add the guide. The test: "if this is wrong, what does it cost to fix three milestones from now?" Important when any of: hard to reverse (stored data, file formats, public interfaces, names others build on, migration of existing projects); wide reach (several skills or tools, or text every run reads); changes a concept rather than wording; changes the owner's workload or the cost (sessions, review points, model per step); low confidence on something consequential. Notable: fixable later in a few files, or changes one skill's behaviour noticeably. Small: local and reversible in one edit (wording, easily overridden defaults, ordering inside a list, internal names). (4) A list whose order is the content (a rung ladder) keeps its order; the decisions about it are listed separately by tier. Keep the one closing question, and the example updated to the new shape. Keep the file about its current length; cut repetition to pay for the additions.
  - Done when: the file states the tiers, the test and the per-decision options rule, and its example shows all three tiers.

- [x] T2 Write the shared planning terms
  - Model: heavy (Opus 5.5)
  - Context: New file `plugins/project-planning/skills/system-design/references/terms.md`, under about 120 lines, one short definition and one example each, from the spec's sections "The model", "Cadence", "Names and labels" and "Owner preferences": system design; additive check; reviewable surfaces (database schema, REST and wire APIs, public library symbols); `settled` and `working` (with its revisit note); `owner` and `proposed` marks; milestone (outcome, subsystems, exit criteria, rungs); foundation-first order; end-of-goal rule and spike; `PROVISIONAL(<RungId>): replace at <MilestoneId> (<name>)` marker and the Provisional code table; `Touches:`; detail by distance; the "decide after it runs" list; milestone planning, automatic fold-back, escalation, milestone close; re-plan triggers; the rule that an ID shown to the owner carries its name; owner preferences (where, what is not one, the two-overrides rule). Also state which existing terms change meaning or retire (checkpoint rung becomes part of milestone planning; per-rung close becomes the escalation path).
  - Done when: every term the spec introduces is defined once, no definition contradicts the spec, and the file reads without the spec open.

- [x] T25 Prepare the review notes for the terms review
  - Model: heavy (Opus 5.5)
  - Needs: T2, T24
  - Context: Standing context "Owner reviews". Write `docs/project-planning/Review-T22.md` for `terms.md`: each term is a decision (its meaning); most are important because a concept change spreads to every skill. Include what each term replaces or retires.
  - Done when: the notes are committed and every term in `terms.md` appears in them.

- [x] T22 USER — Review the planning terms
  - Needs: T25
  - Context: The only review that holds work back. Every later skill rests on these concepts, so a change here is cheap now and costly later. Wording you would change inside a skill waits for the content reviews (T7, T16), which do not hold work back. About 10 minutes.
  - Steps:
    a. Read `docs/project-planning/Review-T22.md`.
    b. Open `plugins/project-planning/skills/system-design/references/terms.md` where the notes leave you unsure.
    c. Reply "approved", or give your choice for each decision you would change.
  - Done when: the owner replies "approved", or the requested changes are applied to `terms.md` and committed (no new review needed unless the owner asks).

### G2 System design and design sessions

- [x] T3 Rewrite `system-design` for the system design model (new projects)
  - Model: heavy (Opus 5.5)
  - Needs: T22
  - Context: Spec "1. System design", "Owner preferences", the threat and privacy row of "Open items". Replace the outline-first workflow: start from an owner document when one exists, else ask once "sketch it yourself, or shall I take a first pass?"; read the owner preferences file and project rules before drafting; agree only what the current milestone needs, stopping at the additive check; field-level review only for reviewable surfaces; `settled`/`working` and `owner`/`proposed` marks; offer once to tighten owner wording before saving; a short threat and privacy section; the Provisional code table and manual stand-ins; later milestones one line each. Drop rules the system design format makes obsolete (the one-page target becomes "bounded by the current milestone"; depth tags may stay if still useful, say which). Rewrite `references/overview-template.md` to the system design shape (keep the file name). Keep the description field accurate and trigger-rich. The SKILL.md should end shorter than today's 117 lines or justify each added line.
  - Non-goals: adopt and checkpoint modes (T4); milestones in the roadmap (T7).
  - Done when: a reader can follow the skill from an owner document to an agreed system design without the spec, and every spec rule in "1. System design" maps to a line.

- [x] T4 Adapt adopt mode, checkpoint and migration in `system-design`
  - Model: heavy (Opus 5.5)
  - Needs: T3
  - Context: Spec "Rollout" (migration paragraph) and "Cadence" (checkpoint look-back now runs inside milestone planning). Adopt mode ends in a system design for the current milestone. Checkpoint mode becomes the look-back step that milestone planning calls (keep `/system-design checkpoint` as an alias that runs it). Migration: an existing Overview and roadmap are read as they are; the first milestone planning session converts them (system design sections, milestone fields, `Touches`, `Map.md`) in a move-mostly commit, IDs unchanged. Update `references/subsystems.md` and `subsystem-template.md` only where the system design changes them.
  - Done when: adopt, checkpoint and migration each have a short procedure consistent with `terms.md`, and nothing still tells the agent to deepen per rung.

- [x] T5 Write the `design-session` skill
  - Model: heavy (Opus 5.5)
  - Needs: T22
  - Context: Spec "Design sessions (new skill)". New `plugins/project-planning/skills/design-session/SKILL.md` (frontmatter like its siblings, `model: opus`, a description that triggers on "let's work through the design", "design session", "explore options for", "I want to think through"). Scratch notes in `<DocDir>/SystemDesign/Sessions/<date>-<topic>.md`; no IDs, statuses or question cap; owner leads; the agent offers 2–3 alternative shapes with Mermaid diagrams (follow `roadmap-plan-next-rung/references/diagrams.md`), traces consequences including the additive check, catches contradictions, offers a throwaway spike; ends with the promote step (to the system design as `settled` or `working`, parked, dropped), commits the system design edit, deletes the notes file, and proposes owner-preference lines per the two-overrides rule. Add it to the plugin README and the repo README skill tables.
  - Done when: the skill is listed in both READMEs, `python3 -m pytest tests` passes, and the promote step's output matches the system design format from T3.
  - Verify: `python3 -m pytest tests`

- [x] T6 Re-run the evals after G2
  - Model: standard (Sonnet 5.5)
  - Needs: T1, T3, T4, T5
  - Context: Both cases, label `g2`. Compare per grader with the baseline (T1's scores for foundation-before-goal). Read each run's design doc for over-detail-trap yourself; if a judge verdict looks wrong, say so with the line that shows it.
  - Done when: a short table of scores (baseline vs `g2`, per grader) is appended to the spec under a new "## Eval results" heading and committed; a regression on any grader is named with its cause.

- [x] T26 Prepare the review notes for the system design and design-session review
  - Model: heavy (Opus 5.5)
  - Needs: T6
  - Context: Standing context "Owner reviews". Write `docs/project-planning/Review-T7.md` covering the decisions in `system-design` (SKILL.md, `references/overview-template.md`, adopt, checkpoint and migration) and `design-session`, and the `g2` eval results as one item if any grader regressed.
  - Done when: the notes are committed.

- [x] T7 USER — Review the system design and design-session skills
  - Needs: T26
  - Context: First owner content review (spec "Rollout"). It does not hold work back: G3 and G4 continue while you review. About 20 minutes.
  - Steps:
    a. Read `docs/project-planning/Review-T7.md`.
    b. Open `plugins/project-planning/skills/system-design/SKILL.md` and `plugins/project-planning/skills/design-session/SKILL.md` where the notes leave you unsure.
    c. Reply "approved", or give your choice for each decision you would change.
  - Done when: the owner replies "approved" or lists changes. Each change becomes a fix task, inserted ahead of the first open task, that also updates any later skill already built on the changed text.

- [x] T32 Record the agreement counts in the step event, not in git
  - Model: standard (Sonnet 5.5)
  - Context: Owner ruling on the system design review (2026-11-01), item 1: accepted items still drop the `proposed` mark and gain no origin, and the counts are recorded instead. system-design step 7 ("Confirm and hand off") adds fields to its `step` metrics event: `proposed`, `accepted` (unchanged), `edited`, `rejected`; design-session "6. Promote" adds the same fields to its step event. Its "Retrospective" section reads the share accepted unchanged from the metrics log, not git history. Also update the text already built on the old claim that the share cannot be recovered: `roadmap-plan-next-rung/SKILL.md` (the `retro` paragraph) and `references/retrospective.md` (milestone retro bullet) read the counts from the log; milestone planning in `roadmap-plan-next-rung` logs the same fields when it agrees a design delta. Where step fields are listed (grep `next_model` under `plugins/`), add the four with one clause each.
  - Done when: grep -rn "accepted unchanged" plugins/project-planning shows no line saying git or the doc cannot show the share; each session that agrees proposed items names the four step fields; python3 -m pytest tests passes.

- [x] T33 Map deferred, superseded and confirmed items in migration
  - Model: standard (Sonnet 5.5)
  - Context: Owner ruling on the system design review (2026-11-01), item 4: in `plugins/project-planning/skills/system-design/references/overview-template.md` "Migrating older docs" (and the matching line in system-design SKILL.md "Migration" if it lists mappings): an old decision `deferred` becomes an Open question keeping its reason; `superseded` stays in Decisions as `superseded by D<n>` with no agreement mark; a confirmed assumption moves to Decisions as `settled · owner`. Also fix the Review note: legacy Design migration still sends "Constraints and assumptions" to the removed Assumptions section (open world assumptions go to Risks, choices to Decisions).
  - Done when: the migration text maps deferred, superseded and confirmed assumptions as above, no migration line points at an Assumptions section, and python3 -m pytest tests passes.

### G3 Milestone map, cadence and fold-back

- [x] T8 Rewrite `risk-first-roadmap` around the milestone map
  - Model: heavy (Opus 5.5)
  - Needs: T3
  - Context: Spec "2. Milestone map", "3. Rungs", re-plan triggers in "Cadence". Milestones as capability layers ordered foundation first; outcome sentence proposed in plain language and marked `proposed` until accepted; exit criteria; owner sets milestone order; end-of-goal rule with spikes and kept spike code (`PROVISIONAL` marker, Provisional code table, behind a seam; manual stand-ins listed beside the table, provisional code preferred); risk classes (shape, clock, breadth) only inside the current milestone; detail by distance; `Touches:` on every rung; the "decide after it runs" list; re-plan only on the four triggers; the roadmap's `Updated:` history goes to the log file. Remove the checkpoint-rung placement rules (look-back now runs in milestone planning). Update `references/roadmap-example.md` to match. Keep the archive and partial-read rules that still apply.
  - Done when: every rule in spec sections 2 and 3 maps to a line, and the example roadmap shows milestones, `Touches`, one detailed milestone and one-line later milestones.

- [x] T9 Rewrite `roadmap-plan-next-rung` for milestone planning and milestone close
  - Model: heavy (Opus 5.5)
  - Needs: T8
  - Context: Spec "Cadence" table, "Open items" (regression test, owner acceptance). Milestone planning (Opus): the look-back from T4, the design delta for the milestone, every rung's brief (thin, citing agreed seams), and the tasklists; each rung's tasklist requires a regression test. Milestone close (Opus): re-read every fold-back in the milestone together, full test suite, owner demo against exit criteria (accept, accept with follow-ups, reject), one milestone retro, re-plan of the next milestone. The escalation target of the automatic fold-back is an internal route reached through `/rung`; it has no owner-facing close name and no `/rung close` command (owner, 2026-11-01). The escalation and milestone-close re-read steps are written so they can run as an Opus subagent from a brief or handoff note (owner, 2026-11-01). Update `references/rung-brief-template.md` (thinner) and `references/presenting-for-review.md` (IDs carry names). Decide whether the skill should be renamed; if so propose the name in the commit message and do not rename (owner decides at T15).
  - Done when: planning, escalation and milestone close each have a procedure, and nothing schedules an Opus session per rung.

- [x] T10 Write the automatic fold-back and hook it into `tasklist-run`
  - Model: heavy (Opus 5.5)
  - Needs: T9
  - Context: Spec "Automatic fold-back" (all five steps, the classification table, "what it never does", the safety net) and the owner's test-scope rule (full suite, or the touched targets when the suite is slow, defined in the spec). Write the procedure as `plugins/project-planning/skills/roadmap-plan-next-rung/references/auto-fold-back.md`. In `plugins/task-workflow/skills/tasklist-run/SKILL.md`, when a run closes the last task of a rung list, follow that reference in the same session (if the file is missing, say so in one line and end with `Next: /rung`). Escalation ends the run with prose saying what differs and why an Opus review is next, then `Next: /rung (Opus: /model opus)`. The five-step procedure writes an escalation marker on the rung that `roadmap next` reads. A per-rung retro runs only for a failed, re-planned or escalated rung.
  - Done when: the reference covers every row of the spec's table, and `tasklist-run` calls it exactly once per rung list.
  - Notes: Found during T9: planning commits all tasklists at once, so the run that starts a rung sets it in progress and writes Base: (under the brief's Status:, or in the tasklist Source: line when no brief).

- [x] T11 Update `tasklist` for regression tests and escaped defects
  - Model: standard (Sonnet 5.5)
  - Needs: T22
  - Context: Spec "Open items". In `plugins/task-workflow/skills/tasklist/SKILL.md`: a rung list includes at least one test that fails without the rung's change (say it in the rung-list guidance, a line or two); a bug task fixing a closed rung's defect carries `Escaped from: <RungId>` (add to the field table). Update `references/example.md` only if it shows a rung list.
  - Done when: both rules are in the skill, each in under three lines.

- [x] T12 Extend the `roadmap` tool: map, names, Touches and routing
  - Model: heavy (Opus 5.5)
  - Needs: T8, T9, T10
  - Context: `plugins/task-workflow/tools/plantools` (Swift; `Sources/PlanKit/Roadmap.swift`, `NextStep.swift`, `CLI.swift`, `Sources/roadmap/RoadmapTool.swift`). Add `roadmap map <file>` (writes or prints `Map.md`: milestones with status and outcome, each rung as one line with name, status and `Touches`); `roadmap name <file> <ID>...` (prints each rung or milestone ID with its title); parse `Touches:` and milestone fields; `roadmap next` routes the new steps: `milestone-plan` (no planned rung with a brief in the current milestone), `run`, `escalation` (the rung carries the escalation marker T10's reference records), `milestone-close` (every rung of the current milestone done, or a paused close waiting for the owner's demo ruling, read from its pause state), `replan`, `finished`, `design`. Routes are internal labels, never commands the owner types. `roadmap next` returns route, a one-line reason and the model, and reads the escalation marker and the handoff notes (T30). Keep old roadmaps working (no milestones section: current behaviour). Bump the tool version per its existing practice and update the minimum version in `next.sh`, the Plan tool check and the Metrics tool check.
  - Verify: `swift test --package-path plugins/task-workflow/tools/plantools`
  - Done when: tests cover each new command and each new route, including an old-format roadmap, and pass.
  - Notes: Found during T5: route replan when a design session left the re-plan signal T30 defines. Found during T9: milestone-plan fires when a planned rung of the current milestone has no tasklist (not 'no brief'); parse the milestone's Close: sub-bullet (paused close, rejected) per roadmap-plan-next-rung; an in-progress rung whose tasklist is all closed but not folded back needs a route (fold-back), else close is blocked.

- [x] T13 Extend `metrics`: session tokens, escapes and stamps
  - Model: standard (Sonnet 5.5)
  - Context: Spec "Model choice" and "Open items". These do not depend on the milestone format, so they can run while the owner reviews. `metrics tokens` also logs planning, close and design sessions from their transcripts, keyed to the `step` event (`run` id, `skill`, `model`); `metrics summary` counts `Escaped from: <RungId>` tasks per rung (the field T11 adds to `tasklist`); reject or warn on a malformed `skill` stamp (seen in the log: a bare `0.16.2`, `roadmap-plan-next-rung 0018`). Do not bump the tool version; T12 does.
  - Verify: `swift test --package-path plugins/task-workflow/tools/plantools`
  - Done when: tests cover each addition and pass.

- [x] T23 Extend `metrics`: provisional markers and escapes per milestone
  - Model: standard (Sonnet 5.5)
  - Needs: T12, T13
  - Context: Spec "End-of-goal rule" (kept spike code) and "Open items". `metrics signals` counts `PROVISIONAL(` markers and flags one whose named milestone is already done (read milestone status through PlanKit, as T12 parses it); `metrics summary` also totals `Escaped from:` tasks per milestone.
  - Verify: `swift test --package-path plugins/task-workflow/tools/plantools`
  - Done when: tests cover both additions and pass.
  - Notes: Found during T9: step events gain kind (milestone-plan, escalation, milestone-close) and ruling; document them in tasklist-run's metrics schema and accept them in metrics.

- [x] T29 Align code-quality-pass reports with tiered reviews
  - Model: standard (Sonnet 5.5)
  - Needs: T24
  - Context: Found during T24. `plugins/project-planning/skills/code-quality-pass/references/quality-files.md` (~line 98: at most 5 flagged proposals get options) and `SKILL.md` (~lines 85, 118) still describe the old flagged-only rule. Align them with `roadmap-plan-next-rung/references/presenting-for-review.md`: tiers, options with a pro and con for every proposal, important first; the report's own length limit (10 ranked proposals, one line for the rest) wins, items past it keep a one-line default. The system-design and roadmap-plan-next-rung SKILL.md lines that restate the old rule are fixed by their rewrites (T3, T9), including their no-reference fallbacks.
  - Done when: No line in code-quality-pass restates the old flagged-only rule and its report follows the tiered shape.

- [x] T30 Write the wait-point handoff note and wire it into the skills
  - Model: heavy (Opus 5.5)
  - Needs: T10
  - Context: Owner request, 2026-11-01: any point where a run or session stops for the owner (USER review, escalation, milestone demo, a blocked task, a run ending on a question) saves what a fresh agent needs, assuming the owner replies much later. Write `plugins/project-planning/skills/roadmap-plan-next-rung/references/handoff.md` once and point `tasklist-run`, `roadmap-plan-next-rung` (escalation, milestone close pause at the demo) and `rung` at it. The note is a scratch file kept out of git (proposed `<DocDir>/Handoff/<topic>.md`, ignored by git; decide where it lives and how the ignore is set up), holding: what was done and the commits, what is pending and the exact question, decisions already made this session, files to read, the tasklist state. The handoff note is where waiting state lives, so a fresh session resumes from it via `roadmap next`. The owner-review notes (`Review-*.md`) serve as the handoff for owner reviews: give them a short status header, delete them when the review closes. The step that consumes a handoff deletes it; `metrics signals` flags a left-over one (small addition to T23's scope or a note for it). Every `Next:` line that waits on the owner is `/rung` (plus the model switch when needed); no per-kind resume command is shown, and the stop message to the owner is short and self-contained. `/rung` finds the handoff and routes the resume to the right skill. The handoff note doubles as the brief a subagent starts from when `/rung` runs a step as a subagent (owner, 2026-11-01). Include a regression eval case if feasible: a stopped run leaves a handoff that a new session can resume from.
  - Done when: handoff.md exists and each waiting point in the three skills writes or consumes a handoff exactly once; a left-over handoff is detectable.
  - Notes: Found during T5: a design session that changes a settled item or adds current-milestone structure must leave a durable signal (handoff note or marker) that roadmap next reads as replan; today design-session only tells the owner. Found during T12: roadmap next does not yet read handoff notes or that signal; plug them into the seam T12 left in NextStep.swift (Swift change, verify with swift test).

- [x] T14 Update `rung`, `next.sh` and `code-quality-pass` for the new steps
  - Model: standard (Sonnet 5.5)
  - Needs: T12, T30
  - Context: `plugins/project-planning/skills/rung/SKILL.md` and `scripts/next.sh`: `rung` is the one command: it dispatches every route (`milestone-plan` and `milestone-close` to `roadmap-plan-next-rung`, `escalation` to its Opus review, `run` to `tasklist-run`, `replan`, `finished`, `design` to `system-design`), and mentions `design-session` for "let's work it out together"; drop checkpoint and skip routing (keep `/rung checkpoint` as an alias of the look-back); the hand-made fallback table matches the tool. Every `Next:` line is `/rung` plus the model switch when the step needs Opus; the prose before it names the rung or milestone with its title and says why (no IDs in the `Next:` line itself). `/rung` states the recommended model before starting. Per step it decides between a subagent on the needed model inside the current session and a new session on that model, by cost and the step's expected context size (owner, 2026-11-01): non-interactive steps (escalation review, milestone-close re-read) may be subagents, owner-facing steps (milestone planning, demo, design sessions) need a session. It states the choice in one line with the reason; the wrong-model stop applies only when it picks a session. Explicit sub-commands may remain as aliases but are never shown. `plugins/project-planning/skills/code-quality-pass/SKILL.md`: its review trigger `checkpoint` becomes milestone planning, and the tidy offer moves from per-rung close to milestone close.
  - Done when: each route the tool can return has a dispatch line, and `python3 -m pytest tests` passes.
  - Verify: `python3 -m pytest tests`
  - Notes: Found during T12: roadmap next's command: row means three things (skill alias like /roadmap-plan-next-rung plan M1, owner-typable /rung run L2, /tasklist-run <path>); make it the dispatch target in every route (tool change in NextStep+Milestones.swift if needed) and never echo it to the owner; read the new milestone: row.

- [x] T15 Re-run the evals after G3
  - Model: standard (Sonnet 5.5)
  - Needs: T8, T9, T10, T14, T32, T33
  - Context: As T6, label `g3`. Add the column to the spec's "Eval results" table. Run it after any T7 fix tasks that are already open have closed.
  - Done when: the table is updated and committed; any regression against `g2` is named with its cause.

- [x] T27 Prepare the review notes for the milestone map and fold-back review
  - Model: heavy (Opus 5.5)
  - Needs: T15
  - Context: Standing context "Owner reviews". Write `docs/project-planning/Review-T16.md` covering the decisions in `risk-first-roadmap`, `roadmap-plan-next-rung` (with `auto-fold-back.md`), `rung`, the tool commands and routes, and any rename T9 proposed; the `g3` eval results as one item if any grader regressed.
  - Done when: the notes are committed.

- [x] T16 USER — Review the milestone map, cadence and fold-back
  - Needs: T27
  - Context: Second owner content review. It does not hold work back: G4 and the ledger review continue while you review. About 30 minutes. Also rule on any rename T9 proposed.
  - Steps:
    a. Read `docs/project-planning/Review-T16.md`.
    b. Open the skill files it names where the notes leave you unsure.
    c. Reply "approved", or give your choice for each decision you would change, including the rename.
  - Done when: the owner replies. Each change becomes a fix task, inserted ahead of the first open task, that also updates any later work already built on the changed text; a rename ruling becomes its own structure-only task.

- [x] T34 Fix the handoff-ignored grader and re-score demo-stop-handoff
  - Model: light (Haiku 4.5)
  - Needs: T15
  - Context: Found during T15. In plugins/project-planning/evals/demo-stop-handoff/graders, handoff-ignored is tool_used with max: 0 and no min, so zero matching calls reads as 'expected 1..0' and fails; set min: 0. Re-score the g3 demo-stop-handoff runs from their kept traces if possible, else re-run that case with --case; update the g3 numbers in the spec's Eval results.
  - Done when: The grader passes when no Bash call matches, the corrected demo-stop-handoff scores are in the spec's Eval results, and the commit message gives them.

### G4 Feedback inbox

- [x] T17 Retros write to the feedback inbox
  - Model: standard (Sonnet 5.5)
  - Needs: T10
  - Context: Spec "Retro feedback inbox" items 1 and 4. In `roadmap-plan-next-rung/references/retrospective.md` (and the retro paragraphs of `system-design` and `tasklist-run`): write the block to `${DANNY_SKILLS_STATE_DIR:-~/.local/state/danny-agent-skills}/feedback/inbox/<utc-timestamp>-<skill>.md` and print one line `retro feedback saved (<n> pending)`; show the block only when asked. Milestone retro at milestone close; per-rung retro only for an unusual rung. The retro reports the share of `proposed` items the owner accepted unchanged. Point the metrics log at the same state directory variable in `tasklist-run` (and the tools, if they hard-code the path: check `MetricsLog.swift`).
  - Done when: no skill still tells the owner to paste a block, and the path is the same in every skill and tool.

- [x] T18 `/retro-feedback` reads the inbox, exports and imports
  - Model: standard (Sonnet 5.5)
  - Needs: T17
  - Context: Spec "Retro feedback inbox" items 2 and 3, and the scenario-suite paragraph on regression cases. `.claude/skills/retro-feedback/SKILL.md`: with no argument, process every inbox item, then move each to `feedback/processed/` with the ledger line that handled it, and purge processed items older than 90 days; a pasted block still works; `export` writes pending items into one file and moves them to `feedback/exported/`; `import <file>` adds them to the inbox; for an item reporting an owner redirect or a refuted rule, propose a regression eval case beside the skill edit.
  - Done when: each command has a short procedure and the skill stays under about 100 lines.

- [x] T31 Decide whether tasklist-run should pause itself for a fresh session
  - Model: heavy (Opus 5.5)
  - Needs: T30
  - Context: Found during T15: after 13 batches the owner asked whether the run should pause and continue in a clean session. The orchestrator's context is re-read on every dispatch, so a long run gets slower and more expensive, and judgment drifts after a compaction. Consider a check at each batch boundary in tasklist-run's 'Check efficiency' step, using signals the orchestrator can count (batches committed, correction rounds, a compaction having happened, which model the remaining open tasks need against the session's model). Past the threshold: finish the batch, write the end/step metrics lines and a handoff note (references/handoff.md, Route: run), then stop with one Next: line naming the command and model. Decide whether to build it, the thresholds, and whether the decision belongs in tasklist-run only or also in rung's subagent-vs-session rule; record the decision in the spec. Build it if accepted.
  - Done when: the spec records the decision; if built, tasklist-run names the signals, the threshold and the stop message, and a run past the threshold stops with a handoff note and a Next: line.

- [x] T35 Restore the planning rules the milestone rewrite dropped
  - Model: standard (Sonnet 5.5)
  - Needs: T19
  - Context: Found during T19. In plugins/project-planning/skills/roadmap-plan-next-rung/SKILL.md, compared with the text at 2994be7, restore: Milestone planning step 3's guess clause (an external system's or framework's behaviour, including what a platform does with an event a Done when relies on; completeness, uniqueness and shape for a property of real data; code in message, code or status and read the route or function that produces it; run the build and tests at the base once, a failure being the first task); Briefs are short's per-component tables one line each; first-time owner surface confirmed before drafting the rest. Also check that tasklist-run's Tidy lists rules cover a Tasklist-<MilestoneId>-Tidy.md (no behaviour change, no tier raise).
  - Done when: Each restored rule is in the skill in one line, the ledger notes that said a rule was dropped now say restored, and the tidy rules name the milestone tidy list.

### G5 Ledger and release

- [x] T19 Review the ledger's untested rows against the redesign
  - Model: heavy (Opus 5.5)
  - Needs: T15
  - Context: `docs/project-planning/feedback-ledger.md` change log (about 40 `untested` rows) and its "Collect next run" list. For each: keep (still applies as written), fold (now covered by a redesign rule; name it), or retire (obsolete under the redesign; one-line reason). Move retired rows to a "Retired by 1.0.0" list, keep IDs and dates. Add rows for the redesign itself, with the spec's "Judge by" signals. Update the ledger's Objective paragraph from "thin, incremental" to the system design model. Do the same pass on the task-workflow ledger for rows the redesign touches. If T16's fix tasks later change a rule a verdict cites, they update that verdict too.
  - Done when: every untested row has a verdict, and the Objective matches the spec.

- [x] T36 Lint a left-over Escalation or Close line and stop routing on it
  - Model: standard (Sonnet 5.5)
  - Needs: T16
  - Context: Owner ruling on the milestone review (2026-11-02): keep the marker lines and add the lint check. Review-T16.md, the item on where a rung or close stands, the option 'As written, plus a lint check'. In plugins/task-workflow/tools/plantools (Milestones.swift lintMilestones and NextStep+Milestones.swift): roadmap lint flags an Escalation: on a rung that is not in progress and a Close: on a milestone that is not current; roadmap next ignores an Escalation: on a done rung; the escalation review and the skill text say the line is deleted when the review ends. Add tests for both lint rules and for the routing guard; update the ledger row if one cites this.
  - Done when: A done rung with an Escalation: line and a finished milestone with a Close: line each produce a lint warning, roadmap next no longer routes escalation for the done rung, and swift test passes with the new cases.

- [x] T37 Rename roadmap-plan-next-rung to plan-milestone
  - Model: standard (Sonnet 5.5)
  - Needs: T36
  - Context: Owner ruling on the milestone review (2026-11-02): the name is plan-milestone. Structure only, no behaviour change: git mv plugins/project-planning/skills/roadmap-plan-next-rung to plan-milestone; update the name in its frontmatter and agents/openai.yaml, every reference in the other skills, README files, plugin.json prompts, the evals (prompts and graders that name the skill), the plantools sources and tests that carry the skill name, tasklist-run and tasklist skills, the ledgers and the spec, and the trigger phrase 'plan the next rung' in its description. Leave CHANGELOG entries that describe history and Completed lists untouched; note the old name in the new CHANGELOG entry at release. Check metrics and step-event stamps that parse a skill name still parse.
  - Done when: No file outside CHANGELOGs and history notes mentions roadmap-plan-next-rung (git grep), the skill directory is renamed, python3 -m pytest tests and swift test --package-path plugins/task-workflow/tools/plantools pass, and the diff changes names only.

- [x] T20 Release notes, versions and final eval
  - Model: standard (Sonnet 5.5)
  - Needs: T6, T7, T15, T16, T18, T19, T23, T35, T36, T37
  - Context: `scripts/bump_version.py project-planning 1.0.0` and `scripts/bump_version.py task-workflow <next minor>`; `CHANGELOG.md` entries for both (what changed for the owner, migration of existing projects); plugin and repo README updates for the new model; final eval run, label `1.0.0`, added to the "Eval results" table.
  - Verify: `python3 -m pytest tests`; `swift test --package-path plugins/task-workflow/tools/plantools`
  - Done when: every fix task from the T7 and T16 reviews is closed, tests pass, versions agree in every manifest and stamp, and the eval table has the `1.0.0` column.

- [x] T28 Prepare the review notes for the final review
  - Model: standard (Sonnet 5.5)
  - Needs: T20
  - Context: Standing context "Owner reviews". Write `docs/project-planning/Review-T21.md`: release now or after the FileOrganizerHero pilot as the important decision; any decisions T20 made (versions, changelog wording, README structure) below it; the eval table's `0.11.2` vs `1.0.0` columns.
  - Done when: the notes are committed.

- [ ] T21 USER — Final review and pilot decision
  - Needs: T28
  - Context: Last owner review point (spec "Rollout" steps 4 and 5).
  - Steps:
    a. Read `docs/project-planning/Review-T21.md`.
    b. Reply with release-now or pilot-first, and any other change.
  - Done when: the owner replies with release-now or pilot-first.

### G6 Known gaps from the 1.0.0 eval

- [x] T38 Every closing summary names each milestone and rung it mentions
  - Model: standard (Sonnet 5.5)
  - Context: Spec 'Eval results' 1.0.0 findings: foundation-before-goal summary-names-ids went 2/3 to 0/3. Add the 'an ID shown to the owner carries its name' rule (terms.md) to the closing summary step of risk-first-roadmap and system-design SKILL.md, in one line each, and check roadmap-plan-next-rung and plan-milestone closing text for the same gap. Also fix the review notes on stale anchors to the retired per-rung flow in risk-first-roadmap, roadmap-plan-next-rung and code-quality-pass that touch the same lines.
  - Done when: Each closing summary step states the rule; python3 -m pytest tests passes.

## Review notes

- presenting-for-review.md: Small example item is run-together bold text; two bullets would scan better (T24)
- presenting-for-review.md: old guard "do not flag an item only because it is new or long" dropped; could return as half a sentence (T24)
- presenting-for-review.md: say that a caller's length limit wins and items past it keep a one-line default (T24; handled for code-quality-pass by its new task)
- plantools Escapes.byRung: ID taken by split(" ").last, wrong for `Escaped from:`L3` without a space; use the regex capture (T13)
- plantools Escapes: ID pattern [A-Za-z0-9]+ truncates hyphenated or dotted IDs; recheck against the rung ID format (T13)
- plantools metrics: steps without `began` are never costed; consider a note or fallback window (T13)
- plantools MetricsTool.swift: duplicated stderr write line; small helper (T13)
- code-quality-pass quality-files.md: Small template line shows no inline options; the tiers bullet covers it (T29)
- foundation-before-goal eval: a run with a data-collection first milestone still failed milestone-order 3 of 3; check at T6 whether the grader is too strict (T1)
- roadmap-plan-next-rung SKILL.md: fallback minimal Overview lists Scope, Headline requirements, Assumptions; fold-back updates "assumptions" (T3; for T9)
- system-design adopt mode: marks inferred requirements `assumed` and hands off with /risk-first-roadmap, not /rung (T3; for T4)
- README.md: system-design paragraph still says headline requirements, detail added one rung at a time (T3; for T20)
- system-design SKILL.md: Migration's "no other mode starts it" sits beside New mode's legacy Design-*.md offer; say it is separate (T4)
- rung SKILL.md passes a rung ID to `system-design checkpoint`; code-quality-pass L79, roadmap-plan-next-rung L48, risk-first-roadmap Checkpoints still describe the retired flow (T4; for T8, T9, T14)
- design-session SKILL.md: a parked minutia with no roadmap yet has no home; system-design uses Open questions marked `after it runs` (T5)
- .codex-plugin/plugin.json: defaultPrompt list could gain a design-session prompt at the version bump (T5; for T20)
- Stale anchors to risk-first-roadmap: roadmap-plan-next-rung SKILL.md:100 "Re-plan after each rung", :101 old `/rung → plan`; plantools RoadmapArchive.swift:4 "Keep the roadmap small"; README.md:8 old ladder (T8; for T9, T12, T20)
- risk-first-roadmap: the `Additive check:` sub-bullet on the next milestone may trip the over-detail "later milestone is one line" grader; watch at T15 (T8)
- roadmap-plan-next-rung close: an open Follow_ups list blocks resuming an accepted close (steps 6–8); exempt it once Close: reads accepted with follow-ups, or run 6–8 before creating it (T9)
- plantools Signals: a handoff note roadmap next already skips as stale gets no warning until 14 days old; reuse NextStep.stale in signals (T30)

- [x] T39 Make the demo stop message and handoff note agree
  - Model: standard (Sonnet 5.5)
  - Context: plan-milestone Milestone close step 4 (Demo) and references/handoff.md 'The stop message' disagree on what goes in chat versus only in the handoff note; every demo-stop-handoff run gave the full walkthrough and the handoff path (stop-message 0/3 twice). Make step 4 follow handoff.md (short, measurable, no handoff path in chat), and update evals/demo-stop-handoff/graders/stop-message.md pass bullets to include the short-and-measurable and no-handoff-path rules.
  - Done when: Skill text and grader state the same rules; python3 -m pytest tests passes.

- [x] T40 Diagnose design-depth failures from the documents
  - Model: heavy (Opus 5.5)
  - Context: design-depth is 1/3 at 1.0.0. Re-run over-detail-trap once (label 1.0.0-dd), read each Overview.md the run wrote by hand, and decide per failure whether the doc is truly over-detailed (then fix the system-design skill text or template that allowed it) or the judge is wrong (then tighten the grader). Standing eval command applies.
  - Done when: Each failing doc has a stated cause, the skill or grader change is committed, and the finding is appended to the spec under 1.0.0 findings.

- [ ] T41 Re-run all evals after the gap fixes
  - Model: standard (Sonnet 5.5)
  - Needs: T38, T39, T40
  - Context: Label 1.0.1-gaps, all three cases, standing eval command. Add the column to the spec's Eval results table and name any grader below its 1.0.0 score with its cause. Then update docs/project-planning/Review-T21.md eval table.
  - Done when: Table column and Review-T21.md updated and committed.
