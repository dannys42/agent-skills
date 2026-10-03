---
name: tasklist-run
description: Execute the open tasks in a tasklist-format TODO.md one reviewable commit at a time. Each batch of tasks goes to a subagent on the cheapest adequate model, a reviewer subagent checks the result, corrections loop back to the implementer, and the passing change is committed before the next batch starts. Use whenever the user says /tasklist-run, or asks to run, work through, execute, or knock out the TODO, the task list, a phase, a group, or specific task IDs, even if they do not name this skill. Supports user overrides such as one task only, a named task/group/phase, no auto-commit, confirm before commit, and parallel worktrees.
license: GPL-3.0-or-later
---

# Tasklist Run

Work through a `tasklist`-format TODO one commit at a time. You are the orchestrator: you pick work, dispatch subagents, mark the list, and commit. You do not read or edit source yourself. Your context is the scarce resource for a long run, so everything below keeps heavy reading inside subagents and passes only small, structured messages between them.

The list format, IDs, tiers, markers, and the "Choosing the next task" rule come from the `tasklist` skill. Follow them as written instead of restating them here.

## Invocation

`/tasklist-run [T7 | G3 | P2 | path/to/TODO.md] [overrides]`

- Default file: `<DocDir>/TODO.md`. If several `TODO-*.md` files exist and none was named, ask once.
- A named task, group, or phase is the whole scope: run exactly that, then stop.
- With no scope, run until nothing qualifies.
- Overrides arrive as flags or plain language and win over every default below:

| Override | Effect |
| --- | --- |
| `--one` / "just the next task" | Run one batch, then stop |
| `--no-commit` | Implement and review, leave changes uncommitted, then stop |
| `--confirm-commit` | Pause before each commit; continue running after the user confirms |
| `--parallel` | See [Parallel mode](#parallel-mode) |
| model or reviewer pinned by the user | Use it instead of the tier default |

Stopping after one batch applies whenever the user scoped the run (named an ID, `--one`) or withheld auto-commit, because running further would exceed what they asked for.

## Before the first batch

1. Read the TODO once. From then on, work from the `Source`/`Goal` line plus the task blocks you need; do not re-read the whole file each loop.
2. Run `git status --short` and remember it. Anything dirty that is not yours stays out of every commit. Stage by explicit path, never `git add -A` or `git commit -a`.
3. Find the project's test/build command and commit style (recent `git log`) once, so subagents and commits do not rediscover them.

## The loop

For each batch:

1. **Pick** the next task by the `tasklist` rule. Tasks marked `USER` are never dispatched; see [USER tasks](#user-tasks).
2. **Size the batch** (below). Decide whether to run, merge, or split.
3. **Implement** in one subagent (below).
4. **Review** in one subagent (below). Loop corrections up to the limit.
5. **Close and commit:** mark the tasks `[x]` in the TODO, then commit the code and the TODO change together.
6. **Check efficiency** at the boundary (see [Token efficiency](#token-efficiency)), then go to step 1 unless the scope or an override says stop.

Run subagents one at a time. A serial run means each agent starts from the last committed state, which removes merge conflicts and lets a later task build on an earlier one.

### Sizing the batch

The commit is the unit. A good commit holds one coherent, reviewable change, so choose the batch by what belongs together, not by how the TODO is grouped.

- Default to one task per commit.
- Merge tasks only when they are siblings in a group, share files or one idea, are each `light` or `standard`, and would be strange to land separately (a rename and its call sites; a function and its only test). A task whose `Needs` points at another task in the same batch is fine only when the batch commits in that order.
- Never merge across a phase boundary. A phase exists because it must ship or be verified before the next starts.
- Do not let size rules distort relevance. A one-line commit is right when the change stands alone; a multi-page commit is right when splitting would leave the tree broken or the history unreadable.
- Estimate size from the tasks' `Context` file lists before dispatching. If the change looks too large to review in one sitting (rough guide: many files or several hundred changed lines), look for preparatory work that shrinks the real change, such as a utility to extract first or a refactor pass with no behavior change. Add those as new tasks with the next IDs and a `Found during <ID>` context line, `Needs` wired so they run first, then proceed. If no useful split exists, run it as one commit and say so in the report.
- When the TODO is a `USER`-free list of very small tasks in one area, batching them is how you avoid a hundred trivial commits. When one task is large, splitting it is how you avoid an unreviewable one.

### Implementer subagent

Pick the model from the task's `Model` line: the named model in parentheses, or the tier's default from the `tasklist` skill when no name is present. A mixed batch uses the highest tier among its tasks. If the user pinned a model, use that.

Prompt the implementer with only:
- the task block(s) verbatim, plus the group or phase `Goal`, plus any `Spec:` path they cite
- the test/build command and commit-style notes you found
- the instruction to make the change, run the task's `Done when` check, and **not** edit the TODO or commit

Ask for a short structured reply: status (`done`, `blocked`, or `invalid`), files changed (exact paths), the trimmed output of the `Done when` check, and concerns or discovered work. A reply that long keeps your context small across many batches.

Keep the agent's ID. Corrections go back to the same agent with `SendMessage` so it keeps its context instead of rereading the code.

### Reviewer subagent

The reviewer checks that the change does what the task *intended*, not only that it passes. It is a fresh agent with no memory of the implementer's reasoning, which is the point: it catches wrong assumptions the implementer cannot see.

- Model: `heavy` (Opus 5.5) by default. When the whole batch is `light`, use a `standard` reviewer, because a heavy reviewer on a mechanical change costs more than the risk it removes. A user-pinned reviewer wins.
- Give it the task block(s) and the list of changed files, and tell it to run `git diff --stat` and `git diff` on those paths itself (plus read any untracked files the implementer created). Fetching the diff in the reviewer keeps it out of your context. Do not pass the implementer's transcript. Tell it to read surrounding code only as needed.
- Ask it to judge: (1) does the diff satisfy each task's `Done when` and intent, including stated non-goals; (2) correctness and obvious regressions; (3) does it contain only relevant changes (stray edits, unrelated cleanup); (4) fit with the surrounding code's conventions. Ask for a verdict, `pass` or `fix`, with a short numbered list of required corrections and no style nitpicks beyond that.

### Corrections

On `fix`, send the numbered list to the implementer via `SendMessage`, then re-review the updated diff. Allow two correction rounds. If the third review still says `fix`, raise the task's `Model` one tier (per `tasklist`: raise the tier instead of retrying indefinitely), update that line in the TODO, and run the implementer once more on the higher model with the reviewer's findings. If that still fails, mark the task `BLOCKED(review: <reason>)` with a `Why:` line and today's date, leave the code uncommitted (or stash it and say where), and continue with independent work.

## Handling outcomes

- **`Done when` cannot be run** (no simulator, needs a secret, needs hardware): do not mark `[x]`. Mark `BLOCKED(<reason>)` with `Why:` and move on.
- **Task is `invalid` or already obsolete:** close it with `[-]`, the reason word, and a `Why:`. Then check the tasks that `Need` it, and re-point or close them per `tasklist`. If a replacement task you add keeps the original intent, carry on and run it. If it narrows or changes the intent (dropping a requirement, say), that is the user's call: record the question in the report and stop.
- **Discovered work:** add a new task with the next unused ID and `Found during <ID>`. Do not enlarge the current batch.
- **Heavy, irreversible, or risky work** (migrations, deleting data, security): pause and show the user the plan before dispatching, even in an unattended run.
- **Stop** when no task qualifies, a merge conflict appears, repeated blocks stack up, or the requested scope is complete. End with a short report: what was committed (one line per commit), what is blocked and why, what `USER` tasks are waiting.

### USER tasks

Never dispatch them and never check them off yourself. Keep running independent tasks. When nothing else qualifies, or a batch's `Needs` is waiting on one, show all pending `USER` tasks together with their steps verbatim, and ask for the `Done when` confirmation. Mark `[x]` only after the user gives it.

## Committing

- Stage the paths the implementer reported plus the TODO file, nothing else. Compare against the starting `git status` so unrelated dirty files stay out.
- The commit message must stand on its own. The TODO is working state that is regularly cleared out, so task IDs in a message would dangle. Write what changed and why, in the project's style. Leave out `T7`-style IDs, any mention of the TODO or task list, and any mention of files that are not in the commit (such as unrelated untracked files). The TODO edit that checks the task off rides along in the commit but is never described in the message. A commit that changes only the TODO (re-planning a task) may say what the plan changed, but still without task IDs.
- Follow the repo's conventions for attribution lines.
- With `--confirm-commit`, show the commit message and `git diff --stat`, wait, and then continue the run if the user confirms. With `--no-commit`, stop after review passes.

## Token efficiency

A long run multiplies small wastes, so check at each batch boundary with three questions, answered from what you already saw (do not investigate):

1. Did several agents read or search the same files or answer the same question? (Project knowledge is missing.)
2. Did any batch take more than two correction rounds, or fail a check for a reason a script or doc could have prevented? (A guardrail is missing.)
3. Did agents repeat the same deterministic transform or shell sequence by hand? (A script is missing.)

Three or more agents repeating one discovery, more than two correction rounds, or the same hand-run sequence twice are enough to act. When one fires:

- Add the fix as tasks in the active TODO, in a `G<n> Token efficiency` group, following the style the `audit-token-efficiency` skill uses (document-wide IDs, `Model`, `Context` starting `Found during <ID>`, `Done when`). The audit skill is manual-only, so do this check yourself; if the waste looks deeper than three questions can judge, suggest the user run `/audit-token-efficiency` with this TODO as the target file.
- Tell the user what you added and why, in a line or two. Never add silently.
- **Small and useful now:** at most three tasks, none heavy or risky, and enough batches remain (roughly three or more) that the savings plausibly exceed the cost of the fix, which is itself a batch with an implementer and a reviewer. Say you are running them, then run them through the normal loop before the next batch.
- **Wire the fix into what remains.** Agents do not discover new files on their own. After a fix that adds project knowledge (a README, a doc, a script), add a one-line pointer to the `Context` of each open task it applies to, or name it in the implementer prompt, so the saving actually reaches them. Specify fixes that remove the expensive part of the work, not just the boilerplate around it.
- **Not useful for the remaining batches:** leave them queued and mention them in the final report.
- **Large, or heavy/risky:** do not run them. If later batches would benefit, pause and ask the user to confirm; otherwise leave them queued.

## Parallel mode

Only when the user asks. Parallel runs give each implementer its own git worktree, so changes cannot collide until merge.

- Choose tasks that are independent: no `Needs` between them and no overlap in the files their `Context` names. When overlap is likely, hold the later task back and run it after the earlier one merges.
- Only you edit the TODO and commit. Collect results, review each in its own reviewer, then merge and commit serially in dependency order. Resolve nothing silently: a conflict stops the merge and goes to the user.
- Mark a running task `IN-PROGRESS` while it is dispatched, and clear that marker when it closes or fails. This is the only mode that uses the marker.
- Remove worktrees after merging.
