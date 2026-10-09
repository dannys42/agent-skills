# task-workflow

A cross-agent plugin for planning and executing work: resolve consequential
decisions first, then break them into tasks and carry them out.

## Skills

### `decision-driven-design`

Inspects an existing system, interviews for high-leverage product and
engineering decisions, reconciles revisions, and produces dependency-ordered
implementation tasks without speculative abstractions.

### `tasklist`

Creates and maintains `<DocDir>/TODO.md` with unique phase/group/task IDs,
dependencies, minimum-model tiers, and standard markers (`OBSOLETE`, `INVALID`,
`SUPERSEDED`, `DEFERRED`, `BLOCKED`) so any model can pick up a task.

### `tasklist-run`

Executes the open tasks in a `tasklist`-format `TODO.md`, one reviewable commit
at a time: a subagent on the cheapest adequate model implements each batch, an
Opus reviewer checks it against the task's intent, corrections loop back to the
implementer, and the passing change is committed before the next batch. Supports
one-task runs, named task/group/phase scope, no-commit, confirm-before-commit,
and parallel worktrees, and queues token-efficiency fixes in the TODO.

### `tasklist-monitor` (Claude Code mod)

Opens a pane during `/tasklist-run` showing each task's status, tokens,
estimated cost, runtime, and completion time, with phase and group subtotals.
It polls the TODO from a local timer and never calls the model, so it adds no
token cost. Reopen it with `/tasklist-monitor`.

## Install

See the repository [installation guide](../../README.md#install-decision-driven-design)
for the complete supported-tool matrix and direct skill installation options.
