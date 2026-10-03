# Changelog

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
