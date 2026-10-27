---
name: code-quality-pass
description: Periodic code-quality passes for a project built rung by rung. Tier 1 `tidy` makes small, behaviour-preserving cleanups to the files one rung changed (naming, idiomatic Swift, file organization, duplication with sibling code, leftover review notes, stale test or doc names), one small commit each. Tier 2 `review` is a read-only whole-codebase architecture review (module boundaries and seams, duplication across rungs, design docs versus what was built, idiom and naming consistency) whose ranked proposals the roadmap re-plan turns into refactor rungs or tasks. `status` reports zero-token signals and triggers; `baseline` starts the cycle on an existing project. Use when the user types /code-quality-pass, asks for a tidy, cleanup, refactor pass, code-quality pass or architecture review of a project, or accepts the offer at fold-back or re-plan. Not for bug hunting in a diff (use a code review) or for designing new features.
license: GPL-3.0-or-later
---

# Code Quality Pass

Rungs ship features; nothing in the rung cycle steps back to ask whether the code is still shaped well. This skill adds that step in two tiers, so it stays cheap and never blocks feature work:

- **Tier 1, `tidy`**: after a rung, small behaviour-preserving fixes to the files that rung changed. Executed.
- **Tier 2, `review`**: every few rungs or when a trigger fires, a read-only look at the whole codebase. Proposes; the user decides.

Signals and triggers come from the `metrics` tool, which reads git and the files and costs no tokens. Read [quality-files.md](references/quality-files.md) before writing `Status.md`, a review report, or a scout prompt.

## Judge by long-term quality

In both tiers, rank and decide by what keeps the codebase healthy over many future rungs, not by how little work the change takes now. Cost sets the order and the size of the pieces (small commits, a split `L` proposal); it is never a reason to drop, demote or soften a finding.

- Prefer the durable fix (remove the duplication, move the seam, enforce the boundary) over a local patch that leaves the cause in place.
- Do not leave out an item because it is large or touches many call sites: make it a proposal, and split it if it is too big for one rung.
- A cheap cleanup that entrenches a weak shape ranks below a larger one that removes it. Say so in the ranking.
- Rank by benefit over the project's expected life and by how fast the problem compounds; `Size` is information for scheduling, not a score.

## Invocation

`/code-quality-pass [status | tidy [<RungId>] | review | baseline | defer [reason]]`. With no mode, run `status`.

| Mode | Does |
| --- | --- |
| `status` | `metrics signals`, printed as is, plus one line naming the mode a trigger calls for. Nothing else. |
| `tidy [L20]` | Tier 1 on that rung (default: the rung most recently folded back or with a closed tasklist). |
| `review` | Tier 2. On a project with no recorded review it is a baseline over the whole codebase. |
| `baseline` | For a project with no `Quality/Status.md`: `status`; if a trigger other than `no-baseline` fires, or the user asks, run `review`; otherwise write `Status.md` with `Last review: <HEAD> · checked, no trigger`. |
| `defer` | Write `Deferred: <date>, <reason>` in `Status.md` (creating it from the template with `Last review: none` if absent, which also ends the `no-baseline` nudge), log it, and stop. |

## Files

```
<DocDir>/Quality/Status.md                 current state only, at most 25 lines (template in quality-files.md)
<DocDir>/Quality/Review-<date>.md          the live Tier 2 report, at most one
<DocDir>/Quality/Proposals-<RungId>.md     a tidy scout's proposals and defects, verbatim, at most one per rung (shape in quality-files.md)
<DocDir>/Completed/Quality/Review-<date>.md  earlier reports, moved verbatim when the next review is written (a Proposals file moves there once the re-plan has placed or dropped every entry)
<DocDir>/Tasklist-<RungId>-Tidy.md         a Tier 1 pass, run by tasklist-run
```

`Status.md` never grows with history: every field is overwritten, `Since review:` resets at each review and is written as a range with a count (`L18–L31 (14)`) past twice the interval, and proposals live only in the review report or a `Proposals-<RungId>.md`. History is in the metrics log.

## Metrics tool check

Before the first `metrics` call in a session, run `~/.cache/danny-agent-skills/bin/metrics --version`. If it fails or is not `0.5.1`, install it without asking with the `task-workflow` plugin's build script, as in `risk-first-roadmap`'s "Plan tool check". Without it, say so in one line; `status` and the triggers are then unavailable, and `tidy` and `review` read `git diff --stat` and `grep` counts by hand.

`metrics signals [--base <sha> | --tasklist <path>] [--status <path>] [--json]` exits 1 when a trigger fires; that is a result, not an error. Pass `--status` when `DocDir` is not `Documentation`, `docs` or `Docs`.

## Never block feature work

- Every offer of a pass is one line with three answers: run, skip, defer. Skip and defer cost nothing further.
- No rung's `Depends` names a quality item, and `tasklist-run` never reads `Status.md`.
- An accepted refactor rung is ordered by the re-plan like any other; it goes ahead of a feature rung only when the user puts it there.
- At fold-back or re-plan, offer at most once. When `Since review:` reaches twice the interval, the offer says so; it is still only an offer.
- A defect found by either tier (a behaviour bug, such as an error path that can lose data) is not a quality item: report it at once and record it (Tier 1: the Proposals file; Tier 2: the report), and ask yes or no to a bug task with a reproducing test first. Only a yes writes the task, through the re-plan or in the active tasklist; `tasklist-run`, the tidy tasks and the fold-back never write one unasked.

## Tier 1: tidy

1. **Preconditions.** The rung's tasks are closed and the test command passes on HEAD. If not, say so and stop.
2. **Gather** (you, cheaply): the base commit (the brief's `Base:` line, else `metrics signals --tasklist <rung tasklist>` resolves it), `git diff --stat <base> HEAD` on source and test files, the `## Review notes` section of the rung's tasklist, and the project conventions file's conventions section if one exists.
3. **Scout** one subagent, `standard` (Sonnet). Use `heavy` (Opus) only when the diff touches concurrency, a persistence schema, or a type shared across modules. Give it the file list, the review notes, the base, and the scout brief in [quality-files.md](references/quality-files.md). It reads the rung's diff, sibling files found by grepping the touched type names, and applies `organizing-swift-files` and `naming-swift-tests` (swift-craft) where installed. It returns at most 6 tidy items, then proposals and defects, never edits.
4. **Classify each item.** Judge by long-term quality, not effort: an item that is too big for a tidy becomes a proposal, never a dropped finding. Tidy: naming clarity, idiomatic Swift, file organization, duplication with sibling code that one small extraction removes, a leftover review note, a stale test or doc name, a compiler warning in a rung file, a finding of the project's existing linter. Everything else is a **proposal**: a behaviour change, a public interface change beyond renames, a change spreading beyond the rung's files and their call sites, or more than about 80 changed lines for one item.
5. **Characterization first.** If an item changes code that no test exercises, its first task adds a characterization test, in its own commit, before the change.
6. **Write `Tasklist-<RungId>-Tidy.md`** in `tasklist` format: `Source:` the rung and base; at most 6 tasks and about 300 changed lines in all; each `Done when` includes the full test command passing; one `Non-goals` line: no behaviour change, and no fix for a defect. A pure rename or move is `light`, anything else `standard`.
7. **Record** before offering, so a skip loses nothing: if the scout returned proposals or defects, write them verbatim to `Quality/Proposals-<RungId>.md` (shape in quality-files.md, each entry `Decision: pending`), and set `Status.md`'s `Backlog:` to link to it. Never write a count that links to nothing. Log a `quality` event (below).
   Then **offer** the tasks: one line per task, then run, skip or defer. On run, hand the file to `tasklist-run` (orchestrate on Sonnet 5.5; the tidy list has no `heavy` tasks). When the pass is done, say the next step is the fold-back it interrupted: `/rung → close <RungId>` on Opus. Its tidy rules (no tier raise; a task that fails review twice is reverted and closed as a proposal) keep the pass small.
8. **Rule on proposals and defects**, only when the scout returned some, as one batched question in the same message as the tidy offer, shown apart from the tidy tasks, in the shape in `roadmap-plan-next-rung`'s [presenting-for-review.md](../roadmap-plan-next-rung/references/presenting-for-review.md). Each proposal: accept (the re-plan places it as a `refactor-rung` or `task`), defer or reject. Each defect: "bug task with a reproducing test first, yes or no". The answer to the whole question may be skip or defer; unanswered entries stay `pending` and cost nothing further (they are not asked again at this fold-back). Record the answers in the Proposals file and log `quality_outcome`.

## Tier 2: review

Read-only. The output is a report the user rules on; nothing is edited except `Status.md` and the report.

Run from a checkpoint (`system-design` checkpoint mode, trigger `checkpoint`): do steps 1 to 4 and return the report. The checkpoint presents it with its own proposals; once the owner has ruled, record the answers in the report and do steps 6 and 7.

1. **Signals**: `metrics signals --json`, kept for the event, and the plain output for the scouts.
2. **Scope.** No recorded review: the whole codebase. Otherwise: modules changed since `Last review` (`git diff --stat <sha> HEAD`), modules named by pending triggers, and proposals the last report or a Proposals file deferred.
3. **Scouts**: at most 6 `standard` (Sonnet) subagents in parallel, one per module, target or top-level source directory in scope (group small ones). Each writes one seam card of at most 40 lines (format in quality-files.md) and reads with bounded output: `grep -n`, ranged reads, no whole large files.
4. **Synthesis**: one `heavy` (Opus) subagent. It reads the cards, the signals, the Overview's Components table and Decisions (`roadmap section`), each subsystem doc's Contract for modules in scope, `Status.md` and the deferred items of the last report. It uses the `codebase-design` vocabulary (deep modules, seams, interfaces) and `choosing-swift-design-patterns` where a pattern fits, and opens source only to confirm a proposal (a few ranged reads). A claim that needs a cross-module or live-data check (can module A import B, does X write a row) is not verifiable from the cards: mark it `unverified` with the one check that settles it unless a card or the build manifest shows it. Each flagged proposal carries its options as `presenting-for-review.md` shapes them. It ranks by long-term benefit and compounding cost, not by effort. It returns the report in the shape in quality-files.md: defects first, then the proposals that need the user's attention, then at most 10 ranked proposals, then one line each for the rest.
5. **Present** the defects, then the attention section and the ranked list, in the shape in `roadmap-plan-next-rung`'s [presenting-for-review.md](../roadmap-plan-next-rung/references/presenting-for-review.md). For each proposal the user answers accept, defer or reject (for a flagged one, which option); batch the question. Record the answers in the report.
6. **Apply the accepted kinds**:
   - `refactor-rung` or `task`: hand to the roadmap re-plan (`risk-first-roadmap`), which places them.
   - `conventions`: one line in the project conventions file (`CLAUDE.md` or `AGENTS.md`, whichever the project uses; ask if neither), so implementers stop reproducing the inconsistency. One line per rule.
   - `fitness-test`: a task to make the boundary permanent. Prefer a boundary the compiler enforces (a SwiftPM target whose dependencies forbid the import); otherwise a small test that fails on the forbidden import or pattern.
   - `accept-shape`: add the family to `Accepted shapes:` so the `shape` trigger stops reporting a deliberate convention.
7. **Update** `Status.md` (`Last review` with HEAD, `Since review: none`, `Triggers pending: none`, backlog counts, link; `Backlog:` links every live report and Proposals file), move the previous report to `Completed/Quality/`, and log `quality` and `quality_outcome` events.

## Model choice

| Step | Model | Up | Down |
| --- | --- | --- | --- |
| Tier 1 scout | Sonnet | Opus: concurrency, persistence schema, cross-module types | never; naming and duplication need judgment |
| Tier 1 tasks | their `Model` line; reviewer by `tasklist-run`'s rules | | Haiku for pure renames and moves |
| Tier 2 scouts | Sonnet | | |
| Tier 2 synthesis | Opus, over cards only | | Sonnet when the scope is one or two modules |

A model the user names wins.

## Metrics events

Append to the `tasklist-run` metrics log (`~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl`), in the same Bash call as the step it records, with `v` 1, `run` (a new UTC ID per pass), `ts`, `skill` (`code-quality-pass 0.8.7`), `repo`:

- `quality`: `kind` (`tidy`, `review`, `baseline`, `deferred`), `rung` (the rung it follows), `trigger` (`fold-back`, `manual`, `checkpoint`, or the trigger names), `models`, `commits` and `lines` (a review or baseline; a tidy omits them, as it logs before its tasks run, and its own `tasklist-run` run carries the numbers), `proposals`, `defects`, and `signals` (the `metrics signals --json` object), and `model` (the model ID you ran on). A tidy that hands off to `tasklist-run` also writes a `step` event as `tasklist-run`'s metrics log defines it (`next_model` `sonnet`).
- `quality_outcome` (once the user has ruled a review's proposals, or a tidy's proposals and defects): `kind` (`review` or `tidy`), `accepted`, `deferred`, `rejected` (entries still `pending` count as deferred), and `kinds` (accepted counts by kind; `bug` for an accepted defect).

Payoff is judged later from `metrics summary` on the rungs before and after a pass (rounds, lines, implementer tools), against the pass's own cost. Treat it as a hypothesis until several passes exist.

## If something is missing

- No `tasklist-run`: run each tidy task as one implementer and one reviewer subagent yourself, commit each, and say that `task-workflow` gives the full loop (`claude plugin install task-workflow@danny-sung-agent-skills`).
- No roadmap: everything works; accepted `refactor-rung` proposals become a `Tasklist-Refactor-<Short_Name>.md` instead.
- No `codebase-design` or swift-craft skills: the scouts and synthesis use the criteria above as written.
- No `presenting-for-review.md`: the report's "Needs your attention" section already carries the flagged proposals; present it before the ranked list as written.
