# task-workflow: metrics first, CLI later

Status: metrics logging shipped in task-workflow 0.7.0. The SQLite/Swift CLI is on hold pending data.

## The idea under evaluation

Replace the markdown-and-`sed` TODO bookkeeping in `tasklist-run` with a compiled CLI (Swift) backed by SQLite. Goals: lower tokens per run, stable task IDs across lists and runs, richer per-run metadata for long-term tuning. The DB is never checked in; solo developer only for now.

Sketch if built: markdown stays the authoring format (the LLM writes `TODO.md` once); `import` ingests it; state and metrics live in the DB; the CLI patches checkboxes so the file remains a readable view and the monitor keeps working. DB at `$(git rev-parse --git-common-dir)/task-workflow.db` (per repo, shared by worktrees, WAL). Display ID stays `T4`; an internal UID (list slug + ULID) is never shown to the model. Commands: `import`, `next`, `show`, `close`, `block`, `add`, `report`, `status --json`. Tables: tasks, runs, attempts, findings, events.

## Analysis

Compiled vs interpreted does not change tokens. Savings come from the interface: `next`/`show` replace loading the TODO and copying task text into prompts; one `close` call replaces 3-4 bookkeeping turns; `report` makes the retrospective a query.

Break-even: `runs = B / (s * R)`, with B the build cost in runs' worth of spend, s the share of run cost removed, R the cost of a run. With B of 1.5-3 runs, s of 7% breaks even at 21-43 runs, s of 4% at 38-75 runs.

Decision rule (agreed up front, N_max about 30 runs, B about 2 runs): realistic saving of at least 8% builds for cost; 3-8% builds only for monitor, IDs or reliability; under 3% skips.

## Measured (2026-10-09, 21 real runs, 3 projects)

Script: `misc/tasklist-metrics/analyze_transcripts.py` (reads `~/.claude/projects` transcripts and subagent files; read-only).

- Orchestrator is about 30% of spend; subagents about 70% (reviewers 35% of that, implementers 65%).
- Bookkeeping-only turns: 166 of 1,059 orchestrator turns.
- Upper bound a CLI could save: 6.5% of total spend (bookkeeping turns 5.2%, TODO resident in context 0.4%, delegation prompts 0.9%). Realistic, at about 60% of that: about 4%.
- Bookkeeping reliability: 1 failed call in 246; 18 repeated edits to one file.
- Caveats: model price weights (opus 1, sonnet 0.6, haiku 0.2) and the 60% factor are guesses; sessions are measured from the first `tasklist-run` mention to their end, so mixed sessions inflate the orchestrator side.

Conclusion: cost alone does not justify the CLI (about 40-75 runs to break even), and reliability is not a problem. The larger lever is calibration: reviewers are about a quarter of all spend, and correction rounds cost 30-50% of a batch each. Tuning reviewer choice and tiers needs per-task history, which does not need a CLI.

## What shipped

`tasklist-run` 0.7.0 writes one JSON line per event (`start`, `batch`, `end`) to `~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl`, shared across projects, never in a repo. It replaces the prose `.tasklist-runlog.md`, so per-run cost is unchanged. Fields are listed in `plugins/task-workflow/skills/tasklist-run/SKILL.md`. The orchestrator cannot see exact token usage, so it logs none. `analyze_transcripts.py --append-tokens` appends one `tokens` event per `batch` line to the same file (raw in/cache-read/cache-write/out counts by role and model, for the window since the previous batch or `start`), matching transcripts by `repo` path. It is idempotent; `--dry-run` previews. Run it after a run; parallel sessions in the same repo would be mixed in.

## Next steps

1. Run `tasklist-run` on about 10 real runs across at least two projects.
2. Run `--append-tokens`, then extend the report to read the `tokens` events: cost per task by tier, reviewer model vs rounds and findings kept, share of runs where the tier was raised.
3. Decide on calibration edits (reviewer rule, tier defaults in `tasklist`) from that data.
4. Revisit the CLI only if wanted for the monitor, stable IDs or SQL reports. If so, the JSONL is import-ready for the schema above. Open risks: distributing a compiled binary (the plugin also targets Gemini, Cursor, Codex), and the skill should fail loudly if the binary is missing instead of keeping a markdown fallback.

## Known issues

- `tests/test_plugin_layout.py::test_each_bundle_contains_exactly_its_skills` fails for `task-workflow` (extra `tasklist` and `tasklist-run` skills not in its expected set). Pre-existing; unrelated to this work.
