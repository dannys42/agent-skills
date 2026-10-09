# Changelog

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
