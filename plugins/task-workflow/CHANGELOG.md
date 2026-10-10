# Changelog

## 0.9.0

From a transcript audit of one run (3 tasks, 6 subagents): cost followed turn count, not result size, since every turn re-reads the agent's whole context.

- `tasklist` gains optional `Run` (exact command for a long job) and `Verify` (exact check invocations, interpreter or venv) task fields
- `tasklist-run` implementer prompts now paste `Run`/`Verify` and known environment gotchas, and carry standing rules: bounded output (`grep -n`, `offset`/`limit`, logs plus tail), one background start and a single blocking `Monitor` for long jobs, and finishing own background work before handing back
- Reviewers trust the implementer's trimmed output for deterministic checks and re-run only what they doubt or the implementer could not
- Doc-only or few-line fixes are applied by the orchestrator or reviewer instead of resuming the implementer
- A repeat completion notice for a closed agent needs no response
- Dates in documents come from the environment date or local `date +%F`; UTC is for run IDs and metrics only
- The commit call must include `git diff --cached --shortstat` so `lines` and `files` are never logged as 0
- Documentation-only review fixes may be applied by the orchestrator instead of resuming the implementer (the one exception to not editing; counted in `orch_fixes`)
- `batch` lines carry per-subagent `agents` (`tokens`, `tools`) when the task notifications report them
- Each change here is a hypothesis; `docs/task-workflow/feedback-ledger.md` records what to measure for each

## 0.8.0

- `batch` metrics lines gain `files` and `lines` (size of the commit), `resumed` (corrections sent to a live implementer) and `impl_runs` (every implementer model when a tier raise started another), so tier, round and escalation questions can be answered from the log
- `rounds` is documented as per batch; per-task comparisons need single-task batches
- `analyze_transcripts.py --append-tokens` adds `cache_breaks` and `max_uncached` to each `tokens` event
- No new cost per run: the new fields come from a `git diff --cached --shortstat` in the commit call and from the transcripts

## 0.7.0

- `tasklist-run` now writes a structured metrics log instead of the prose run log: one JSON line per event (`start`, `batch`, `end`) appended to `~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl`, outside every repo, shared across projects and runs
- Each `batch` line records tiers, implementer and reviewer models, the reviewer's reason, correction rounds, findings kept and dropped, tier raises, outcome and commit; the retrospective is built from the run's own lines
- The orchestrator does not log tokens; `misc/tasklist-metrics/analyze_transcripts.py --append-tokens` adds exact per-batch `tokens` events to the same file afterwards, from the session transcripts, at no per-run cost
- `<DocDir>/.tasklist-runlog.md` is no longer written

## 0.6.3

- Added a monitor test that a spawn whose prompt paraphrases the task (`Task T1: ...`) still starts the run

## 0.6.2

- Fixed the `tasklist-monitor` pane staying empty when the orchestrator's spawn prompts paraphrased the tasks
  - A spawn now starts the run when a task ID appears in its description or at the start of its prompt, as long as the TODO has that ID
  - A typed `/task-workflow:tasklist-run` also starts the run through `command.run`
- `tasklist-run` now has the orchestrator begin every implementer and reviewer prompt with the task ID(s)
- The empty pane says what it is waiting for and which TODO it found
- The header notes tasks already done when the run started, which have no token or cost data
- The pane gains a model column before tokens: `Opus 5.5` when wide (110+ columns), `Opu5.5` when tight (70+), omitted when narrow; the `time` column is now `duration`
- Hooks log to the debug log (`claude --debug`) only; the monitor makes no model calls and adds no token cost

## 0.6.1

- Added run limits to `tasklist-run`: stop after more than 3 tasks added in one run, two consecutive blocked tasks, or a repeated identical failure across correction rounds; agents report `blocked` after about 15 tool calls without progress
- Replaced the 0.6.0 pre-run build check with a rule to stop and ask when a failure is environmental, so the common case pays nothing

## 0.6.0

- `tasklist-run` now picks the reviewer by risk in the task (network, concurrency, security, persistence, platform behaviour, or a `Done when` that cannot verify intent) instead of by the implementer's tier; Sonnet is the default reviewer otherwise
- Reviewers get the implementer's concerns and check output, verify platform behaviour with a scratch script, and tag findings `required`/`optional` and `speculative`
- The orchestrator drops speculative findings, sends the rest in one message, and may skip the re-review of a mechanical fix after re-running build/test itself
- Added a preflight: build/test must pass on the clean tree before the first batch
- Added a run log (`<DocDir>/.tasklist-runlog.md`, never committed) and an end-of-run retrospective with a feedback prompt to paste back for tuning the skills; nothing is applied automatically
- The final report lists decisions the orchestrator made that the TODO did not
- `tasklist` gained tier-estimation guidance and a short checklist of things to state in a task (degenerate input, long-input performance, realistic fixtures, platform quirks, behavioural choices)

## 0.5.1

- Fixed the `tasklist-monitor` pane staying on "No /tasklist-run yet." during a run
  - A subagent spawn whose prompt contains task blocks now starts (or reactivates) the run, so it no longer depends on the `skill.prompt` hook having fired
  - The run no longer ends when the orchestrator's turn ends while spawned agents are still working; it ends on the first orchestrator turn that finishes with none left
- After updating, run `/reload-plugins` (or restart the session) to pick up the mod change

## 0.5.0

- Added a Claude Code mod, `tasklist-monitor`, that opens a pane while `/tasklist-run` works (reopen with `/tasklist-monitor`)
  - Shows each task's status, tokens, estimated cost, runtime, and completion time, with subtotals per group and phase
  - The layout follows the list: phase > group > task, group > task, or tasks alone
  - Reads the TODO on a local timer, so the pane costs no model tokens
  - Cost is an estimate from published per-model rates and the token counts each subagent reports

## 0.4.0

- Added `tasklist-run` for executing a `TODO.md` task by task (invoke with `/tasklist-run`)
  - Each batch is implemented by a subagent on the task's named model, reviewed by a separate reviewer subagent, corrected through the same implementer, and committed on its own
  - Batches are sized for relevant, reviewable commits; oversized work is split with preparatory tasks first
  - Overrides: one task, a named task/group/phase, no auto-commit, confirm before commit, parallel worktrees
  - Queues token-efficiency fixes in the active TODO and tells the user before running them

## 0.3.0 — 2026-10-02

- Added `tasklist` for writing and maintaining a `TODO.md` checklist (invoke with `/tasklist`)
  - Phase, group, and task IDs (`P1`, `G2`, `T7`) are unique across the whole file and never reused or renumbered
  - Each task records its minimum model as a tier plus a named model, such as `standard (Sonnet 5.5)`
  - Standard markers: `[x]` done, `[-]` closed with `OBSOLETE`, `INVALID`, `SUPERSEDED→ID`, or `DEFERRED`, and `BLOCKED` and `IN-PROGRESS` for open items
  - `USER` tasks mark work only the user can do, with lettered steps (`a.`, `b.`, `c.`) the user can cite as `T4c`
  - Default path is `<DocDir>/TODO.md`; fully closed phases stay in place unless the user asks to archive them to `<DocDir>/Archive/Tasks.md`
- `decision-driven-design` can now emit its tasks in the `tasklist` format, in a file the user names
