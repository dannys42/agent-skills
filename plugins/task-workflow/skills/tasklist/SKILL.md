---
name: tasklist
description: Create and maintain a Tasklist.md task list in a consistent checklist format with unique IDs, dependencies, minimum-model tiers, lettered step-by-step instructions for work only the user can do, and standard markers for done, obsolete, invalid, superseded, deferred, and blocked work. Use whenever the user asks for a task list, tasklist, checklist, work breakdown, or implementation plan to be written down, or wants a task list updated, re-planned, or cleaned up, even if they do not name the format. Also use to turn decision-ledger output or a plan into executable tasks.
license: GPL-3.0-or-later
---

# Tasklist

A task list is a handoff document: another model, with no memory of the conversation, must be able to pick one item and do it. Consistent structure, stable IDs, and explicit closed states make that possible and keep the list trustworthy as the plan changes.

See [example.md](references/example.md) for a complete phased list.

## Where the file goes

Default path: `<DocDir>/Tasklist.md`.

- `DocDir` is the project's existing documentation directory, typically `Documentation/` or `docs/`. Follow project rules when they name one.
- Separate efforts that need their own list use `<DocDir>/Tasklist-<Topic>.md`, with `Topic` a short 2–3 word Snake_Case name, matching `Decision-<Topic>.md` when the list comes from a decision ledger.
- A list that expands one roadmap rung is `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`, for example `Tasklist-L3-Grid_Text_Rendering.md`. `RungId` is the roadmap ID (`L3`); the description is 2–4 Snake_Case words from the rung title. Cite the rung ID and the rung's design brief (`<DocDir>/SystemDesign/Rung-<RungId>-*.md`) in `Source`.
- When every item in a rung's list is closed, move the file unchanged to `<DocDir>/Completed/` (create the folder if needed) so `<DocDir>` holds only live lists. Do this when the list is fully closed, not before, and say where it went. This applies to rung lists only; other lists stay in place unless the user asks to archive them.
- Older projects may still have `TODO.md` or `TODO-<Topic>.md`. Read and continue those as they are; do not rename them unless asked.
- The user may override `DocDir`, `Topic`, or the whole path.
- If the file already exists, read it first and continue its IDs and layout. Never overwrite it. Items you add follow the current format in this skill (including a named model on `Model`) even when older entries do not; leave existing entries as they are. If the file's structure is fundamentally different, ask before converting.

State the path when you create the file.

## Pick the structure by size

Use the smallest structure that keeps the list navigable. Judgment beats the numbers.

| Size | Structure | When |
| --- | --- | --- |
| Short (about 8 tasks or fewer) | Tasks only | One concern, little ordering |
| Medium (about 9–30) | Groups → Tasks | Distinct themes or areas |
| Large | Phases → Groups → Tasks | Ordered milestones where one must ship or be verified before the next starts |

Do not add a level just to look organized; every level is something the reader must keep in their head.

## IDs

- Prefix by level: `P` phase, `G` group, `T` task (`P1`, `G2`, `T7`).
- Counters are **document-wide**, never per-parent. There is no `G1.T3` and `G2.T3`; there is one `T3` in the whole file. A bare ID is therefore unambiguous and can be cited alone in a commit, prompt, or dependency.
- IDs are **never reused or renumbered**, even after an item is closed or removed from view. Insert new work with the next unused number; document order and numeric order may differ. Find the next number by scanning for the highest existing ID, including closed items (`tasklist next-id <file>` does this when the [plan tools](#plan-tools-optional) are installed).
- When several tasklist files exist, qualify cross-file references with the filename.

## Layout

Phases and groups are headings. Tasks are checkbox items with indented fields.

```markdown
# Tasklist — <title>

Source: <ledger, PRD, or request this list came from>   (omit if none)

## P1 <Phase title>
Goal: <one line; what is true when this phase is done>

### G1 <Group title>

- [ ] T1 <Outcome-oriented title>
  - Model: standard
  - Needs: T2, T5
  - Context: <why, where, constraints, relevant files and decision IDs>
  - Done when: <observable check>
```

Headings carry no checkbox; a phase or group is complete when everything under it is closed. In a short list, drop the headings and keep only the tasks.

### Task fields

| Field | Required | Content |
| --- | --- | --- |
| Title | yes | Imperative outcome ("Add migration for `Word.preferredID`"), not an activity ("Work on migration") |
| `Model` | yes, except `USER` tasks | Minimum tier plus its named model, e.g. `standard (Sonnet 5.5)`; see below |
| `Context` | unless the title says it all | The facts an executor cannot guess: why, which files or symbols, constraints, and decision IDs (for example `D04`). Point at files instead of pasting code |
| `Needs` | only when dependent | Task IDs that must be closed first. Leave it out for independent tasks; most lists have several, and omitting it tells an executor the task can start now or run in parallel |
| `Run` | only for a long job (over about a minute) | The exact command that starts it, with paths and arguments, so the executor starts it once and waits once instead of discovering and polling |
| `Verify` | when the check is a command | The exact invocation(s) behind `Done when`, including the interpreter or venv path and any non-obvious tool. Saves the executor, and later the reviewer, from rediscovering CLI usage |
| `Done when` | yes for anything non-trivial | The observable check: a test, a command, a behavior |
| `Notes` / `Non-goals` | only when a trap exists | The one thing an executor would otherwise get wrong |

Write enough context that the task can be executed without reading the conversation, and stop there. If a task needs more than a short paragraph, it is probably two tasks, or it needs a linked spec (`Spec: <path>`) that the checklist item points to.

Size a task to one working session and one reviewable change with one verification. Split anything bigger. A reorganisation (code moved, split or renamed across files or modules) is its own task: one commit that changes structure and no behaviour, its `Context` listing the files it moves and the public names that must stay, and any task that changes logic there `Needs` it. A large reorganisation is several such tasks, each leaving the build and tests passing. Never fold one into a task that also changes behaviour.

## Minimum model tiers

`Model` records the cheapest tier likely to succeed first time, followed by the named model for that tier in parentheses: `Model: light (Haiku 4.5)`. A stronger model may always take the task; a weaker one should not. The tier makes the intent durable and the name makes it directly actionable.

| Tier | Choose when | Default model |
| --- | --- | --- |
| `light` | Mechanical, fully specified, local to one file or a few lines, low risk | Haiku 4.5 |
| `standard` | Multi-file change following existing patterns, some judgment, default for most work | Sonnet 5.5 |
| `heavy` | Ambiguous spec, cross-cutting design, or risky and hard-to-reverse work (migrations, concurrency, security) | Opus 5.5 |

Estimate from the task text, not the topic. A precise spec with enumerated tests is `light`, or `standard` when it spans files. Network, platform-API, or concurrency behaviour is `standard` at least (a reviewer is chosen for it separately). Rounds in practice come from what the text leaves silent, so fix the text (see below) before raising the tier.

When unsure between two tiers, choose the higher one for risky or irreversible work and the lower one otherwise. If the user pins a different model, or the project uses another tool's models, put that name in the parentheses instead; the tier stays the same. When newer models ship, update the default column here so new lists stay current. Do not rewrite names in existing lists unless asked.

Record these tier meanings here, not in the tasklist. Include a legend in the file only when the user asks for one.

## Say what the executor would otherwise guess

When writing each task, check whether `Context` or `Done when` is silent on any of these, and add a line where it matters (skip the ones that cannot apply):

- Degenerate input: empty, zero, NaN/infinite, huge, malformed.
- Performance on long input.
- Fixtures shaped like real data, not hand-made minimal ones.
- Platform or network quirks the executor must verify (content types, error codes, defaults).
- Assumed facts about real data (counts, which values exist, whether a series is complete): if the logic depends on one, check it with a read-only count on the data the code will actually read, or make a cheap probe the first dependency, rather than leaving it to the first real run.
- Behavioural choices: error vs. empty result, exit codes, usage text. Decide them now, in the task or a `Decisions:` line under the title, so an executor does not invent them.
- Commands and environment: the exact invocation for anything the task must run (`Run`, `Verify`), the venv or interpreter that has the needed packages, and tools known to be missing.

## Steps only the user can do

Some work cannot be done by an agent: creating an account or API key, enabling a capability in a web console, approving a payment, testing on a physical device, making a product decision. Mark these tasks `USER` after the ID so an executor never attempts them, never marks them done on its own, and surfaces them at the right moment. Give them lettered steps the user can follow and cite.

```markdown
- [ ] T4 USER — Create the Sign in with Apple key
  - Context: T6 needs the key to sign tokens. Takes about 5 minutes; you need Account Holder or Admin access.
  - Steps:
    a. Open https://developer.apple.com/account and choose **Certificates, IDs & Profiles → Keys**.
    b. Click **+**, name the key `Notes SIWA`, and tick **Sign in with Apple**.
    c. Under **Configure**, select the app ID `com.example.Notes`, then **Save → Continue → Register**.
    d. Click **Download** and save the `.p8` file to `~/Secrets/` (it can only be downloaded once).
    e. Note the **Key ID** shown on the page.
  - Done when: reply with the Key ID and confirm the `.p8` file is saved. Do not paste the file contents.
```

Rules for a `USER` task:

- **Steps** are a lowercase-lettered list (`a.`, `b.`, `c.`), restarting at `a` in each task. The user cites a step as `T4c`, which is unambiguous because task IDs are unique across the file.
- One action per step, in the imperative, in the order the user performs them. Name exact things: the URL, the menu path, the button label, the value to type. Skip explanation the user does not need to act; put the *why* in `Context`.
- Keep it to about eight steps or fewer. If it takes more, or mixes unrelated chores, split it into several `USER` tasks.
- `Done when` states what the user reports back or what you will check, such as a value, a confirmation, or a file path. Never ask the user to paste a secret into the tasklist or the chat; tell them where to store it, and have later tasks read it from there.
- Omit `Model`: no model runs this task. Tasks that depend on it list it in `Needs`, which holds them back until the user confirms.
- Place the task as late as its dependents allow but early enough that the user is not the bottleneck. When many `USER` tasks exist, consider grouping them so the user can do them in one sitting.

When an executor reaches a `USER` task, it shows the user the steps verbatim, asks for the `Done when` confirmation, and marks `[x]` only after the user gives it. While waiting, it continues with independent tasks.

## Status markers

| Marker | Meaning |
| --- | --- |
| `[ ]` | Open |
| `[x]` | Done and its `Done when` check passed |
| `[-]` | Closed without being done; always followed by a reason word |

Reason words for `[-]`:

| Word | Use when |
| --- | --- |
| `OBSOLETE` | Valid when written, no longer needed: requirement dropped, or done by other means |
| `INVALID` | Never valid: a premise was wrong or the task was mis-specified (file does not exist, bug does not reproduce). A planning error, so it is worth noticing |
| `SUPERSEDED→T9` | Replaced by the named item(s), which now carry the work. Use it only when another item actually takes over the work; otherwise use `OBSOLETE` |
| `DEFERRED` | Valid, but intentionally postponed. Unlike the others it may return: to revive it, change `[-]` back to `[ ]`, drop the word, and note why in `Why:` |

Qualifiers for items that stay `[ ]`:

| Word | Use when |
| --- | --- |
| `BLOCKED(T3)` / `BLOCKED(reason)` | Cannot start until the named item or condition clears |
| `IN-PROGRESS` | Claimed by an agent; use only when several agents or sessions share the list |

Write the word after the ID, then the title. (`USER` is a task type, not a status; it goes in the same position and may combine with others, such as `USER BLOCKED(T2)`.) Give every `[-]` item and every `BLOCKED(reason)` item a `Why:` line with a one-line reason and an ISO date.

```markdown
- [-] T4 OBSOLETE — Add cache layer
  - Why: profiling showed the query is already fast (2026-10-02)
- [-] T5 SUPERSEDED→T7 — Per-field flag
  - Why: flag moved to the entity (2026-10-02)
- [-] T8 DEFERRED — Export to CSV
  - Why: not needed for the first release (2026-10-02)
- [ ] T9 BLOCKED(T3) — Wire up UI
```

A reason word on a phase or group heading (`## G3 Cache — OBSOLETE`, `## P2 Export — DEFERRED`) closes every open item beneath it; anything already `[x]` stays done. Executors skip everything under a closed heading.

## Maintain the list

The list stays useful only if it matches reality, so update it as work happens.

- Check `[x]` only after the task's `Done when` has actually been verified.
- Never delete or renumber an item. Close it with `[-]` and a reason, so references in commits, reviews, and other tasks still resolve.
- When the plan changes, close the stale items and add new ones; do not rewrite an item's meaning in place, because earlier references would then point at something different.
- Add discovered work as a new task with the next ID and a context line saying where it came from ("Found during T4").
- When a `Needs` target becomes `[-] OBSOLETE` or `INVALID`, check whether the dependent task still makes sense, and re-point or close it.
- If a task fails at its stated tier, raise `Model` rather than retrying indefinitely.
- Leave fully closed phases in place. Archive only when the user asks: move them unchanged to the location the user names, or `<DocDir>/Archive/Tasks.md` by default, leaving a one-line stub (`P1 — archived, all closed`) so IDs still resolve.

## Choosing the next task

Take the first open item, in document order, that is open (`[ ]`), is not `USER`, `BLOCKED` or `IN-PROGRESS`, is not under a closed heading, and has every `Needs` target `[x]` (or `[-] SUPERSEDED` with the replacement `[x]`; a `DEFERRED` target does not count). If none qualifies, report which blockers are holding the list, including any `USER` tasks waiting on the user, rather than guessing. When an executor can make no more progress without the user, surface the pending `USER` tasks together so the user can clear them in one pass.

## Building a list from other material

When the source is a decision ledger, PRD, or plan, put its path in `Source:` and cite decision IDs in `Context`, so the task stays self-contained without repeating the whole design. Order tasks so dependencies and risk come first: interface-defining work and prototypes before dependent migrations.

## Plan tools (optional)

`tasklist`, `roadmap` and `metrics` are small command-line tools in this plugin's `tools/plantools/` (SwiftPM with Swift Argument Parser). They only apply the rules above faster; nothing here depends on them. They live outside `PATH`, in `~/.cache/danny-agent-skills/bin/` (`$XDG_CACHE_HOME` if set); below, `tasklist` means `~/.cache/danny-agent-skills/bin/tasklist`, and `roadmap` likewise. Before using one, run `~/.cache/danny-agent-skills/bin/tasklist --version`. If it fails or is not `0.5.2`, install it yourself without asking: `sh <this skill's base directory>/../../tools/plantools/build.sh`, which runs `swift build -c release` and copies the binaries there (it rebuilds only when sources changed, so it also handles a plugin update, and a deleted cache is rebuilt the same way). If `swift` is missing or the build fails, say so in one line, do not retry, and apply the rules by hand as written. Run the binary directly, never through `swift run`.

| Command | Replaces |
| --- | --- |
| `tasklist next <file> [--block\|--context]` | scanning for the next eligible task; on none, prints what blocks each open task and exits 1 |
| `tasklist context <file> <ID>` | the `Source`, enclosing `Goal` lines and task block an implementer prompt starts from |
| `tasklist show <file> <ID>` | reading one task block, or a phase or group heading with its Goal and tasks, instead of `sed -n` |
| `tasklist next-id <file> [T\|G\|P]` | scanning for the highest ID |
| `tasklist lint <file> [--base <older copy>]` | the mechanical checks in "Before finishing"; `--base` also reports deleted IDs and titles rewritten in place |
| `tasklist done <file> <ID>... [--confirmed]` | ticking `[x]` (changes only the checkbox; `--confirmed` is required for `USER` tasks) |
| `tasklist needs <file> <ID> [--add <ID>...] [--remove <ID>...]` | editing a `Needs:` line; refuses unknown IDs (a rung ID too, since it is not a task here) and cycles; adding an existing edge is a no-op. To record "waits for rung L3", use `tasklist set <file> <ID> context "Waits for L3" --append`, or a `USER` task that confirms the rung when the wait must stop the run |
| `tasklist close <file> <ID> --reason <WORD> [--by <ID>...] --why "<text>" [--date D] [--confirmed]` | closing a task, phase or group `[-]` with the reason word and a dated `Why:` (`SUPERSEDED` needs `--by`); refuses `[x]` items |
| `tasklist reopen <file> <ID> --why "<text>" [--model <tier>]` | reviving a `DEFERRED` task (`--model` when it has none) |
| `tasklist add <file> --under <ID> --title "<text>" --model <tier> [--needs ..] [--context ..] [--done-when ..] [--user --step ..] [--before <ID>]` | appending a task with the next unused ID, the tier's named model filled in; prints the ID |
| `tasklist set <file> <ID> <title\|model\|run\|verify\|done-when\|notes\|context> "<text>" [--append]` | rewording one field of an open task; prints a warning when a `title` change leaves the old wording quoted elsewhere |
| `metrics tokens` / `metrics summary <tasklist>` / `metrics signals` / `metrics predictions` | exact per-batch tokens from transcripts; a run's or rung's retrospective numbers; zero-token code-quality signals (see `tasklist-run` and `code-quality-pass`); how the tier and next-step model predictions held |

Use them instead of scripted edits to a list. Every editing command takes `--dry-run` (prints a diff, writes nothing), runs `lint` on the result and refuses when it would add an error, and touches only the lines it names. Exit codes: 0 done, 1 refused by a rule, 2 bad usage. The tool never creates, renumbers or reorders a list, and the markdown stays the source of truth. `tasklist set` may rewrite fields of open tasks; closed tasks are never rewritten; run `tasklist lint --base <older copy>` after substantial rewrites.

## Keep the file lean

The file is working state, not documentation. Leave out a "how to use this list" section, legends the user did not ask for, and any heading or section that would be empty or only a placeholder. Every line should be something an executor acts on.

## Before finishing

With the plan tools installed, run `tasklist lint <file>` first and fix every error; it covers unique IDs, existing `Needs` targets, cycles, a `Model` on every non-`USER` task, and a reason word and dated `Why:` on every `[-]` and `BLOCKED(reason)`. The judgment checks below stay yours either way.

Check the list yourself: every ID is unique and none is reused; every `Needs` target exists; there are no dependency cycles; every task has a `Model` (except `USER` tasks, which have lettered steps instead); every `[-]` has a reason word and a `Why:`; `Needs` appears only where there is a real dependency; no empty sections; no task bundles several verifications; robustness and behavioural choices are stated where they apply.

When you finish writing or re-planning a list, end with the next step, as `Next: <command> (<Model>: /model <alias>)`: `/tasklist-run <the file>` on the orchestrator model from `tasklist-run`'s "Orchestrator model" (Sonnet 5.5, or Opus 5.5 when more than half the open tasks are `heavy`). If `USER` tasks come first in dependency order, name them before the command. For a rung list the line is `Next: /rung → run <RungId>`. A list that expands a rung already gets this line from `roadmap-plan-next-rung`; give it once. Log it as a `step` event (fields in `tasklist-run`'s metrics log).
