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

## Rejected or parked

- Helper script to close a batch (check off, commit, log): parked. Adds code and a duplicate of the metrics schema for an unmeasured gain; the CLI decision rule applies. Revisit if bookkeeping turns are measured above about 5% of run cost.
- Orchestrator launches long jobs itself and dispatches the agent only for the result: parked; a single blocking wait is the cheaper first step. Revisit if long-job turns persist.

## Feedback received

Append one line per feedback drop: date, source run (project, tasks, skill version), what was taken, what was parked.

- 2026-10-10: video-preview pipeline run (3 tasks, 6 subagents, 0.8.0). Took #1-#7 and #9 as above (#5 narrowed to doc-only, #9 optional); parked #8 (helper script).

## Open questions

- Does the reviewer-trust rule change the defect catch rate? Needs 2 or more runs on 0.9.0 with comparable reviews.
- Is a mandatory `agents` field worth the orchestrator's copying, given `--append-tokens` already reports tokens from transcripts?
