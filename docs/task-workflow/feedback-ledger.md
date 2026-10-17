# task-workflow feedback ledger

The standing brief for refining `tasklist` and `tasklist-run` (in `plugins/task-workflow/`) from real-run feedback. The `/tasklist-feedback` skill reads this first and updates it after every round. Keep it short and factual; it is working state.

## Objective

Lower the total cost of a `tasklist-run` without lowering accuracy (correction rounds and defects that reach a commit). Cost is dominated by turns, not result size: every subagent turn re-reads its whole context. Secondary: make cost and quality measurable from the metrics log so tuning does not rest on anecdotes.

## Rules for changing the skills

1. **Evidence tiers.** Tag every incoming claim `measured` (from the log, transcripts or notifications), `observed` (seen in one run's transcript), or `guess`. Guesses never become rules; at most they become a metric to collect.
2. **One run is a hypothesis.** A change backed by one run ships only if it is cheap (a line or two), reversible, and has a named metric below. Otherwise log the data and wait for a second run.
3. **Every rule costs tokens in every future run.** Prefer deleting or tightening a rule over adding one. Reject suggestions that add code, scripts or mandatory fields unless the saving is measured. The CLI/SQLite idea is on hold; see `docs/designs/2026-10-09-task-workflow-metrics-and-cli-design.md` (decision rule: at least 8% realistic saving to build for cost).
4. **Protect accuracy.** Do not weaken the reviewer's independence, correction limits or `Done when` checks to save tokens without data showing they do not catch defects. Keep the orchestrator out of source edits.
5. **Tiers:** change a task's tier defaults only from per-task evidence (single-task batches), never from one run.
6. **Ship mechanics.** Bump the version in `.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `gemini-extension.json` and the `skill` value in the `tasklist-run` metrics text; add a `CHANGELOG.md` entry; record the change below with its metric. The metrics log records `skill`, so runs can be compared by version.

## Metrics available

Log: `~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl` (events `start`, `batch`, `end`, `tokens`). Analyzer: `misc/tasklist-metrics/analyze_transcripts.py` (`--append-tokens`, `--dry-run`). Compare by the `skill` field (0.8.0 baseline versus later). Useful derived numbers: turns per implementer (`agents[].tools`), tokens per batch, rounds per batch, `resumed`, `orch_fixes`, `cache_breaks`, `max_uncached`, reviewer share of spend (design doc baseline: reviewers about 35% of subagent spend, orchestrator about 30% of total).

## Change log (hypotheses under test)

| Version | Change | Hypothesis | Evidence | Judge by | Status |
| --- | --- | --- | --- | --- | --- |
| 0.9.0 | `Run`/`Verify` task fields; implementer prompt gets exact commands and env gotchas | Fewer discovery turns | observed (3 of 6 transcripts re-looked-up CLI usage) | implementer `tools` per task versus 0.8.0 | untested |
| 0.9.0 | Implementer rule: start long jobs once, block on a single `Monitor` | About 10 fewer turns on long jobs | observed (one run, ~10 turns on a 12-minute job) | `tools` on tasks with long jobs | untested |
| 0.9.0 | Bounded-output rules in implementer prompt | Smaller resident context, fewer cache re-reads | observed (29k, 13.7k and 32k results) | `max_uncached`, tokens per batch | untested |
| 0.9.0 | Reviewer trusts the implementer's trimmed deterministic output | Cheaper reviews | observed (reviewers re-ran ffprobe, validator, gap check) | reviewer `tools` down while defects caught per review stay flat (`kept`) | untested; accuracy risk, watch `kept` and defects found after commit |
| 0.9.0 | Orchestrator applies doc-only review fixes instead of resuming the implementer | Avoid full-context resume | guess on cost, observed on event | `orch_fixes` versus `resumed`; resume cost from `tokens` events | untested |
| 0.9.0 | Repeat completion notices need no response | Fewer wasted orchestrator turns | observed (5 notices, one agent) | orchestrator turns per batch | untested |
| 0.9.0 | Document dates from the environment date; UTC only for metrics | Correctness | observed (one wrong date) | wrong-date findings | untested |
| 0.9.0 | Commit call must include shortstat; `agents` and `orch_fixes` logged | Complete data | observed (`lines` logged as 0) | share of `batch` lines with `lines` of 0 or no `agents` | untested |
| 0.9.1 | Environment gotchas block shared with all later prompts; simulator preflight, UDID of pinned runtime | No discovery by trial and error on simulator tasks | observed (one run, 57 calls/~87k tokens to find the runtime issue) | implementer `tools` on simulator tasks; hangs at "idle" | untested |
| 0.9.1 | "Silence means hung" (3 min log silence: restart once, then `blocked`) | Hung jobs cost 2 restarts at most, not dozens of polls | observed (one run; 15-call rule never fired) | `blocked` notes citing a hang; `tools` on long-job tasks | untested |
| 0.9.1 | Lifecycle: no stray background work, `TaskStop` after accept, ignore re-sent hand-backs | No repeat hand-back loops | observed (about 12 repeats, one agent) | orchestrator turns per batch; repeat notices | untested |
| 0.9.1 | Retrospective always reports a tool-count outlier, `TaskStop` or repeat hand-backs | Cost outliers reach feedback instead of "nothing stood out" | observed (same run: retrospective skipped the prompt despite ~87k-token hang) | feedback prompts for runs with an outlier | untested |
| 0.9.1 | Simulator section: build once, absolute-threshold render checks, reviewers do not re-run scenarios | Fewer hang/compile confusions, no false pass on a light render | observed (one run) | simulator-task `tools`, reviewer `tools`, rounds | untested |
| 0.9.2 | Heavy reviewer only for security boundary, concurrency, unrecoverable data loss, unverified platform claim; network or persistence alone no longer qualifies | Same defects caught at lower reviewer cost (Sonnet is cheaper per token; token counts per review are about the same, so no token saving is claimed) | measured on cost (one run, 4 of 9 Opus reviews found nothing required), guess on "Sonnet would still catch it" | Sonnet-reviewed batches in `rev_reason` heavy-trigger areas: defects found after commit, `rev_required` per review by model, reviewer tokens per batch | untested; accuracy risk |
| 0.9.2 | Mirrored tasks tagged `mirror` in `rev_reason`; reviewer model unchanged | Shows whether mirrored tasks ever yield required findings | observed (two Opus reviews on schema tasks mirroring a passed one, none required) | `rev_required` on `mirror` batches over 2 or more runs | collect only |
| 0.9.2 | Unverified `Done when` claim becomes the reviewer's first, live-run job | Keeps the highest-value review work on target | observed (sandbox and auth findings came from live runs) | `rev_required` where the implementer flagged an unverified claim | untested |
| 0.9.2 | `rev_required` logged per batch | Cost per real finding comparable by reviewer model | collect only | needs 2 or more runs | untested |
| 0.10.1 | `tasklist`: assumed real-data facts get a read-only count or a first-dependency probe | Spec-derived rework is found before implementer batches, not at the first real-data `USER` task | observed (one run: all rework from one wrong data assumption, found at the `USER` task) | tasks added with `Found during` a `USER` real-run task; correction rounds traced to a data assumption | untested |
| 0.10.1 | Implementer confirms a scripted or multi-file edit applied before running tests | No verification against unedited files | observed (one run: edit did not apply, own check ran on old tests, reviewer caught it) | reviewer findings of "edit not applied" or stale-state checks | untested |
| 0.10.1 | A task for a user-reported mid-run defect starts by asking what the user sees or reproducing it | No batch spent on a non-bug caused by a naming mismatch | observed (one run: one standard batch on a non-bug) | tasks closed `INVALID` after a user-reported defect; mid-run tasks added for user reports | untested |

Status updates from 0.10.1 round: the 0.9.0 `lines`-of-0 row is contradicted for one run (0.9.2 run logged 0 `lines`/`files` and 0 reviewer tokens on two batches despite the "never log 0" rule), so no rule change, only compliance to watch; the 0.9.1 lifecycle/silence rows have one counterexample (a Haiku `light` implementer left a hung background job and needed `TaskStop`); the 0.9.2 Sonnet-reviewer row is inconclusive, leaning supported (about 5 Sonnet reviews, 0 required findings, one real stale-state catch, no defects reported after commit).

## Rejected or parked

- Helper script to close a batch (check off, commit, log): parked. Adds code and a duplicate of the metrics schema for an unmeasured gain; the CLI decision rule applies. Revisit if bookkeeping turns are measured above about 5% of run cost.
- Orchestrator launches long jobs itself and dispatches the agent only for the result: parked; a single blocking wait is the cheaper first step. Revisit if long-job turns persist.
- Sonnet reviewer or orchestrator spot-check for mirrored tasks (feedback 2026-10-12, reviewer model #2): parked. One run, two batches; the orchestrator does not read source, so judging a near-copy is a guess. Revisit if `mirror` batches show no required findings across 2 or more runs.
- Haiku reviewer or orchestrator-only check for `mirror` tasks (feedback 2026-10-17): still parked. Second run: 4 Sonnet-reviewed mirror-pattern batches, 0 required findings, optional-only, which meets the "2 or more runs" bar on the face of it; but it is a guess that Haiku or no review would also catch the next one, and the same run's reviewer caught a silent defect (non-mirror). Needs `mirror` tagging and `rev_required` actually logged on those batches before deciding.
- Helper that refuses to write `lines`/`files` of 0 (same feedback): rejected for now. The rule already exists (Committing); a script is code without measured savings (rule 3). Revisit if 0-line batches persist on 0.10.1.
- Extra rule for background commands left by Haiku implementers (same feedback): not added. "Finish what you start", "Silence means hung" and `TaskStop` already cover it; tracked on the watchlist instead of adding a duplicate rule.
- Dropping `concurrency` from the heavy trigger (same feedback): kept. No data either way.
- Shared simulator helper script (feedback 2026-10-12 #4): parked. One run; existing token-efficiency question 3 and the wire-the-fix rule already cover repeated plumbing. Revisit if a second run shows agents re-deriving simulator plumbing.

## Feedback received

Append one line per feedback drop: date, source run (project, tasks, skill version), what was taken, what was parked.

- 2026-10-10: video-preview pipeline run (3 tasks, 6 subagents, 0.8.0). Took #1-#7 and #9 as above (#5 narrowed to doc-only, #9 optional); parked #8 (helper script).
- 2026-10-12: iOS Simulator XCUITest run (9 batches, ~0.9.0). Took #1 (preflight, gotchas block), #2 (generalized to any long job), #3, #5, #6, #7 as a conditional Simulator section plus lifecycle rules; #8 narrowed (`lines` rule already existed in 0.9.0, so only cumulative/reviewer tokens clarified); parked #4. Follow-up: the run's own retrospective found nothing to report despite the hang, so its skip rule was widened; `/tasklist-audit` proposed, awaiting go-ahead.
- 2026-10-12 monitor data, same run: 1.3M tokens, $8.57 est., 9 implementers. T4 221k/$2.46 against a 62-133k, $0.25-0.87 spread for the rest (about $2 over the median, roughly a quarter of run cost). Rows sum to about 1.0M, so about 0.3M is reviewers/orchestrator not itemised. T9 wall-clock 7h53m on 81k tokens (paused overnight at the weekly token limit, not a hang). Light-tier T11 used 133k tokens, more than most standard tasks. No rule change.
- 2026-10-12: reviewer model selection, 15-batch Swift package plus macOS app run (0.9.0). Took #1 (narrowed: concurrency kept, wording kept generic), #2 (reduced to a `mirror` tag, no model change), #3, #5 (as `rev_required`); #4 confirms the existing correction rules, no change. Data: 9 Opus reviews ~500k tokens, 4 with no required findings (~190k); 2 Sonnet reviews each found a real defect.
- 2026-10-17: Swift app plus local server run (8 batches, 0.9.2; 0 rounds, tiers matched). Took #1 (narrowed to one line in `tasklist`), #2, #4 (narrowed) as one-run hypotheses; #3 and #5 not applied (rules already exist; compliance, not wording); mirror-reviewer downgrade stays parked. Cause of rework sits upstream: the planning brief asserted an unchecked data fact (see the project-planning ledger).

## Open questions

- Does the reviewer-trust rule change the defect catch rate? Needs 2 or more runs on 0.9.0 with comparable reviews.
- Is a mandatory `agents` field worth the orchestrator's copying, given `--append-tokens` already reports tokens from transcripts?
- Do light-tier docs tasks (T11, 133k) cost more than their tier implies? Needs a second sample before touching tiers (rule 5).
- Do Sonnet reviewers catch what Opus did on security, backup and sandbox tasks? Not tested; 0.9.2 keeps those on Opus. A later run could try Sonnet on one such task with an explicit live-run instruction.
