# Changelog

## 0.13.2

From a rung retro whose `metrics summary` showed 2 lines changed and 0 reviewer tokens for a 562-line rung with three reviews. Both numbers came from fields the orchestrator copies by hand.

- Plan tools 0.3.1: `metrics summary` takes lines changed from each batch's commit (`git show --shortstat`) instead of the logged `lines`, and reviewer tokens from the `tokens` events when the batch's `agents` carry none; it adds a "Stands out" line when either logged value was off. 59 tests (1 new)
- `tasklist-run`: the `## Review notes` section is added if absent, so left-over optional findings are not dropped when the list has no such section

## 0.13.1

From a rung retro whose run logged no `batch` lines: the orchestrator skipped them because the `metrics` and `tasklist` tools were not installed, though the log is written with plain shell.

- `tasklist-run`: writing the metrics log needs no installed tool, and `start`, `batch`, `end` and `step` lines are never skipped; before the `end` line the run counts its `batch` lines against its commits, prints one warning line if short, and backfills them from `git log`
- Retros now end with one feedback block for `/retro-feedback` (see project-planning 0.7.1)

## 0.13.0

- Every step now ends with a next step: a `Next: <command> (<Model>: /model <alias>)` line. `tasklist-run` names `/roadmap-plan-next-rung fold-back <RungId>` on Opus when a rung list is closed, or the blocker and `/tasklist-run <file>` when tasks remain; `tasklist` and `decision-driven-design` end with `/tasklist-run <file>`
- `tasklist-run`: new "Orchestrator model" rule (Sonnet 5.5, Opus 5.5 when open tasks include `heavy` ones) that the other skills quote
- Metrics log: new `step` event (`skill`, `model`, `target`, `next`, `next_model`, `basis`) written at the end of every step that names a next one, so the recommended model can be compared with the one actually used; `start` gains `model` and `heavy`; `end` gains `interventions` and `reraised`
- Plan tools 0.3.0: `metrics predictions` (declared tier against rounds, pooled and per repo; recommended model against the model the next step ran on, with the rounds and corrections of runs that followed it or not); `metrics tokens` also costs planning steps (`step_tokens`, from `began`); `metrics summary` adds planning tokens and share, fold-back drift, discovered tasks, and a first-half against second-half orchestrator cost per batch (flagged when it rises 50%). 58 tests (7 new)
- `step` events gain `began` and `drift`; `end` gains `discovered`
- `tasklist-monitor`: when a run finishes, the pane shows the same next step (computed from the list's file name and open tasks, no model call); 3 new tests

## 0.12.2

- `tasklist-run`: the reviewer judges by long-term quality (prefers the durable fix over a workaround) and the correction triage never drops a finding because fixing it is more work

## 0.12.1

- `decision-driven-design`: each option in a major question carries a pro and con, and a low-confidence recommendation says what would settle it; the decision landscape names the high-impact or uncertain areas first; a batch of default-accepted decisions puts up to 3 items that need a look in a "Needs your attention" section with options, and every item stays in the list
- `tasklist-run`: the retrospective's "Worth changing" puts up to 3 high-impact or guess-based items first, marked `⚑`, with one line of options

## 0.12.0

- Plan tools 0.2.0: new `metrics` binary. `metrics tokens` is a Swift port of `analyze_transcripts.py --append-tokens` (same events; a batch with no transcript turns is skipped instead of logged as zeros); `metrics summary <tasklist | run>` prints a rung's numbers against the median of the last 5 rung lists, its largest batches and what stands out, resolving old runs to their tasklist through the batch commit; `metrics signals` prints zero-token code-quality signals and review triggers (interval, no baseline, rung diff size, a fourth file of one shape, new mirrored types, new subsystem doc) and exits 1 when one fires. 51 tests (10 new)
- `tasklist-run`: optional review findings that are not applied go to a `## Review notes` section of the tasklist (`opt_left` in the metrics log) for the code-quality pass; implementers report new compiler warnings and findings of the project's existing linter (never one the project lacks), and reviewers treat them as required; `Tasklist-<RungId>-Tidy.md` lists never raise a tier and turn a task that fails review twice into a proposal; `start` logs `list`; the retrospective uses `metrics summary` and the shared short format, and for a rung list defers to the rung retro after fold-back
- `tasklist`: expected tool version `0.2.0`; the `metrics` commands are listed

## 0.11.1

From a bug report: a roadmap session never installed the `roadmap` tool because only `tasklist` carried the install step, and a documented ladder line was not parsed.

- `roadmap` / `tasklist` tools 0.1.1: `roadmap` reads the status of a ladder line that ends `[done] detail: Completed/...` (it showed `[unknown]` and linted a warning); `[done; detail: ...]` still works. New parser test; 41 tests pass
- `tasklist`: the expected tool version is `0.1.1`, so installed 0.1.0 binaries are rebuilt
- `tasklist-run`: names the check-and-install step before using `tasklist`; the metrics `skill` value is `0.11.1`

## 0.11.0

Cheaper planning reads and mechanical rule checks. Measured on one real project (a roadmap of 66.6 KB and a tasklist of 16.5 KB); the tool is optional and every rule still works by hand.

- New `tools/plantools/` (SwiftPM with Swift Argument Parser, 40 tests): `tasklist` (`next`, `context`, `show`, `next-id`, `lint`, `done`, `status`) and `roadmap` (`status`, `show`, `outline`, `section`, `lint`). `build.sh` builds with `swift build -c release` only when sources changed; run the installed binaries directly, not through `swift run` (8 ms against 1.4 s per call)
- `tasklist`: "Plan tools (optional)" section; the skill builds the tools itself (`build.sh`) and installs copies in `~/.cache/danny-agent-skills/bin/`, outside `PATH` when they are missing or stale, and falls back to the manual rules if `swift` or the build fails; `next-id` and `lint` named where the skill scans or checks by hand
- `tasklist-run`: uses `tasklist lint`, `next`, `context`, `done` and `next-id` when installed; unchanged otherwise

## 0.10.1

From one 8-batch run on 0.9.2 (Swift app plus local server; 0 rounds, tiers matched). All rework came from a brief that asserted a data fact true for one table but not for the series the code reads, found only at the first real-data `USER` task. Three one-run hypotheses, each a line; see the ledger.

- `tasklist`: an assumed fact about real data is checked with a read-only count on the data the code reads, or gets a probe task as its first dependency
- `tasklist-run`: implementers confirm a scripted or multi-file edit applied (grep old text, `git diff --stat`) before running tests
- `tasklist-run`: a task for a user-reported mid-run defect starts by asking what the user sees or reproducing it; a non-reproducing one closes `INVALID`
- The `skill` value in the metrics text was still `0.9.2` after the 0.10.0 rename; it now matches the plugin version

## 0.10.0

Task lists are renamed so they pair with the `project-planning` roadmap rungs and their design briefs.

- `tasklist`: the default file is `<DocDir>/Tasklist.md` (was `TODO.md`); separate efforts use `Tasklist-<Topic>.md`
- `tasklist`: a list that expands one roadmap rung is `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md` and cites the rung ID and its design brief (`SystemDesign/Rung-<RungId>-*.md`) in `Source`; when every item is closed it moves unchanged to `<DocDir>/Completed/`
- Existing `TODO.md` / `TODO-<Topic>.md` files are read and continued as they are, not renamed
- `tasklist-run`: defaults to `Tasklist.md`, offers the newest rung list first when several exist, and still reads legacy `TODO*.md`
- `tasklist-monitor` hook finds both `Tasklist*.md` and legacy `TODO*.md`

## 0.9.2

From one 15-batch run on 0.9.0 (Swift package plus macOS app): nine Opus reviews at 40-66k tokens each; four found nothing required, two of those on schema tasks mirroring a pattern already passed. Opus findings that mattered were security, backup and sandbox behaviour, found by running the thing; Sonnet reviews also caught two real defects.

- Heavy reviewer is now for security boundaries, concurrency, unrecoverable data-loss risk, or an unverified platform claim; network or persistence alone no longer qualifies, and plain schema, DTO, route, CLI and UI work goes to Sonnet. This is a one-run hypothesis with an accuracy risk; see the ledger
- Tasks that repeat an already reviewed pattern are tagged `mirror` in `rev_reason`; the reviewer model is unchanged until a second run shows whether they find anything
- An unverified `Done when` claim or platform concern becomes the reviewer's first, live-run job
- `batch` lines gain `rev_required` (required findings per review) to compare cost per real finding across reviewer models

## 0.9.1

From one iOS Simulator run (9 batches): a name-selected simulator hung (57 calls, ~87k tokens to find the cause), the 15-call stall rule never fired on a silent job, and a stray `xcodebuild` caused about 12 repeat hand-backs.

- Environment gotchas are one block, extended with what agents discover and pasted into every later implementer and reviewer prompt
- Simulator tasks (`xcodebuild`, `simctl`, UI tests) get one preflight and a short "Simulator work" section: select by UDID on a pinned runtime, `build-for-testing` once, absolute-threshold render checks with one reboot retry, no reviewer re-runs
- General: a long job whose log is silent for about 3 minutes is hung (kill, restart once, then `blocked`); implementers confirm no background work or booted simulators remain; the orchestrator `TaskStop`s accepted implementers and ignores re-sent hand-backs
- The retrospective no longer skips the feedback prompt when one agent's `tools` is an outlier, or a `TaskStop` or repeat hand-backs happened
- `agents` logging: use the resumed implementer's last (cumulative) notification and always include the reviewer

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
