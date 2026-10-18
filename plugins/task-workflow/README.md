# task-workflow

A cross-agent plugin for planning and executing work: resolve consequential
decisions first, then break them into tasks and carry them out.

## Skills

### `decision-driven-design`

Inspects an existing system, interviews for high-leverage product and
engineering decisions, reconciles revisions, and produces dependency-ordered
implementation tasks without speculative abstractions.

### `tasklist`

Creates and maintains `<DocDir>/Tasklist.md` with unique phase/group/task IDs,
dependencies, minimum-model tiers, and standard markers (`OBSOLETE`, `INVALID`,
`SUPERSEDED`, `DEFERRED`, `BLOCKED`) so any model can pick up a task.

### `tasklist-run`

Executes the open tasks in a `tasklist`-format `Tasklist.md`, one reviewable commit
at a time: a subagent on the cheapest adequate model implements each batch, an
Opus reviewer checks it against the task's intent, corrections loop back to the
implementer, and the passing change is committed before the next batch. Supports
one-task runs, named task/group/phase scope, no-commit, confirm-before-commit,
and parallel worktrees, and queues token-efficiency fixes in the tasklist.

### Plan tools (optional)

`tools/plantools/` holds three small Swift command-line tools: `tasklist` and
`roadmap` apply the list and roadmap rules mechanically (next eligible task,
lint, next ID, tick, one-rung and one-section reads), and `metrics` reads the
run log and the repository (exact per-batch tokens from transcripts, a rung's
retrospective numbers, zero-token code-quality signals). `tools/plantools/build.sh`
runs `swift build -c release` and copies the binaries to
`~/.cache/danny-agent-skills/bin/` (outside `PATH`; safe to delete, it is rebuilt).
The skills run it themselves when the binaries are missing or stale, call the
binaries by full path, and work without them.

### `tasklist-monitor` (Claude Code mod)

Opens a pane during `/tasklist-run` showing each task's status, tokens,
estimated cost, runtime, and completion time, with phase and group subtotals.
It polls the tasklist from a local timer and never calls the model, so it adds no
token cost. Reopen it with `/tasklist-monitor`.

## Install

See the repository [installation guide](../../README.md#install-decision-driven-design)
for the complete supported-tool matrix and direct skill installation options.
