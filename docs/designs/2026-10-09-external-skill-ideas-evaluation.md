# task-workflow: ideas from other skills, pending data

Status: logging for the evaluation shipped in task-workflow 0.8.0. No idea below is adopted. Decide once the data floor is met (see [When to decide](#when-to-decide)).

Related: [metrics first, CLI later](2026-10-09-task-workflow-metrics-and-cli-design.md), which defines the log and the transcript analyzer this builds on.

## Why this exists

On 2026-10-09 we searched the skills.sh ecosystem (`npx skills find`) for skills similar to task-workflow, then for skills about token and cost efficiency. Nothing matches the whole plugin. Four skills have ideas worth testing against our own data. This document records what they claim, what we would change, how to test each idea with the log, and the thresholds we would use. It is meant to be read cold.

Provenance: the skill contents below come from a subagent's read of each skill's files, not from a first-hand review. Re-read the cited file before relying on a detail. Search results gave install counts only (superpowers `subagent-driven-development` 222K, ecc `cost-aware-llm-pipeline` 9.6K, `agent-pulse` 47.5K, `session-report` 3.1K); we did not check repo reputation.

## Baseline: what task-workflow does today (0.7.0)

- `tasklist` gives each task a minimum-model tier (`light`, `standard`, `heavy`) and optionally a named model.
- `tasklist-run` runs the implementer on the task's tier (highest tier in a mixed batch). It picks the reviewer by risk: Opus for `heavy` or network, concurrency, security, persistence, platform-API work, otherwise Sonnet.
- Corrections go to the same implementer with `SendMessage`; two correction rounds are allowed. A third failing review raises the task's tier once and reruns the implementer; a further failure blocks the task.
- Events go to `~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl` (`start`, `batch`, `end`). `analyze_transcripts.py --append-tokens` adds exact `tokens` events from transcripts.
- `tasklist-monitor` shows per-task tokens, cost and model live, at no token cost. It is display only; nothing acts on cost.
- `agent-engineering:audit-token-efficiency` is a manual retrospective for repeated discovery, scripts and MCP servers. It does not examine model choice.

## The ideas

Each idea has a hypothesis, what the other skill says, the log fields that test it, and a proposed adopt/reject rule. Thresholds are proposals, not agreed; the earlier CLI evaluation set its rule up front and this one should too, so confirm them before looking at the data.

### 1. Turn count beats token price (superpowers `subagent-driven-development`)

Source: its "Model Selection" section (about lines 184-220) and `implementer-prompt.md`. It says to use the least powerful model that can do each role, with three tiers (cheap for 1-2 files with a complete spec, standard for multi-file integration, most capable for design), and that the cheapest models take 2-3x the turns on multi-step work, so a mid-tier model is the floor there.

Hypothesis: `light`-tier (Haiku) implementers on multi-file tasks cost more in total than Sonnet, because they need more correction rounds and more turns.

Change if confirmed: in `tasklist`, set a Sonnet floor for tasks touching several files or needing integration; reserve `light` for single-file, fully specified work.

Test: compare `impl: haiku` batches with `impl: sonnet` batches, split by `files`. Per group look at mean `rounds`, `outcome` blocked/raised rate, and total tokens (see query A).

Proposed rule: adopt if Haiku batches with `files` >= 2 average at least 0.5 more rounds than Sonnet batches or cost at least 20% more per committed task. Reject if the difference is within noise.

Confound: batches hold several tasks and `rounds` is per batch. Compare single-task batches only (`len(tasks) == 1`), or run a few deliberately single-task runs.

### 2. Run-level budget cap (ecc `cost-aware-llm-pipeline`)

Source: a Python pattern sheet for API apps, not for agent orchestration. A `CostTracker` with `budget_limit` stops work once spend passes it. Its `select_model` chooses Haiku or Sonnet from input length (10k characters or more) or item count (30 or more). The companion `agentic-engineering` skill has a three-line routing list and says to escalate a tier only when the lower one fails with a clear reasoning gap, and to track model, tokens, retries, time and success per task.

Hypothesis: runs sometimes spend far more than the user expected, and a stop-at-budget rule would have saved real money without losing finished work.

Change if confirmed: an optional `--budget` override on `tasklist-run`. At each batch boundary the orchestrator compares an estimate to the budget and stops.

Test: this is a control, not a hypothesis, so the data question is whether it would have fired and whether the estimate is available. Compute run cost from `tokens` events (query B) and see how many runs exceeded a plausible budget and how much of the overrun came from the last third of the run. The blocker is the estimate: the orchestrator cannot see exact usage, so it would need a price table plus a running count from subagent results, or it would read the monitor's number.

Proposed rule: adopt only if at least 1 in 5 runs would have hit a budget the user would have set AND a cheap enough in-run estimate exists. Otherwise leave to the monitor.

### 3. Cache analysis (anthropics `session-report`)

Source: `analyze-sessions.mjs` in the Anthropic plugin parses transcripts including `<session>/subagents/*.jsonl`. It splits input into uncached, cache-create and cache-read; breaks usage down by project, `subagent_type`, skill and prompt; and flags cache breaks (turns with more than 100k uncached input). Its guidance thresholds (as reported): cache hit under 85%, one prompt over 2% of total, a subagent type averaging over 1M tokens per call. It reports tokens only, with no pricing and no model or task attribution.

Hypothesis: some batches lose a large share of cost to cache misses (long idle gaps expiring the cache, context rewrites), which is invisible to the per-role totals.

Change if confirmed: shorten idle gaps or batch boundaries, avoid edits that invalidate the orchestrator's prompt prefix, add a cache-hit line to the retrospective.

Test: `tokens` events carry `cr` and `cw` per role and model, plus `cache_breaks` and `max_uncached` per batch (from 0.8.0). Compute the cache-read share of input per batch (query C) and how many batches have any cache break.

Proposed rule: adopt a retrospective check if more than 25% of batches have a cache break or the median cache-read share is under 85%. Otherwise record the number and drop it.

Caveat: `cache_breaks` counts any turn with `input + cache_write` above 100k, including a subagent's first turn. Ignore a break that is a fresh subagent loading a large context; look at breaks in the orchestrator (`orch`) first. The analyzer does not yet split breaks by role.

### 4. Efficiency ranking and anomaly flags (`agent-pulse`)

Source: `SKILL.md` is a thin wrapper over a third-party PyPI CLI (`agentpulse-cli`) that reads logs from 13 agent tools and estimates cost from its own price table. Commands include `leaderboard --rank-by efficiency`, `optimize`, `budget`, `forecast`, `anomaly`, `health`. The routing logic lives in the CLI, which was not read. The skill says not to invent exact savings.

Hypothesis: some tier/model/reviewer combinations are consistently worse per committed task, and a few outlier batches account for much of the waste.

Change if confirmed: build the same two views on `metrics.jsonl` without the dependency: cost per committed task by tier and model, and a flag for batches above a multiple of their tier's median. Feed both into the retrospective.

Test: join `batch` and `tokens` on `batch_ts` (query D). Check whether batch cost has enough spread within a tier to make an outlier flag meaningful (for example, a top decile at least 3x the median).

Proposed rule: adopt the views if they surface at least one actionable difference (a model or reviewer choice that costs 20% more for the same outcome). Do not install the external CLI.

### 5. Escalation shape and explicit models (superpowers `subagent-driven-development`)

Source: the same skill. Fix rounds 1-3 resume the same implementer; rounds 4-5 use a fresh implementer on a more capable model. Always pass the model explicitly on every spawn (an omitted model inherits the session's model; `implementer-prompt.md` marks `model: REQUIRED`). Scoped re-reviews of small fix diffs use a cheaper tier. It notes a session's final-review fix wave cost more than all its tasks combined, and that fresh contexts per task and per review have a cost.

Hypothesis: after the second failed round a fresh, stronger implementer finishes sooner than resuming the stuck one on a raised tier, and re-reviewing small fixes with the heavy reviewer is wasteful.

Change if confirmed: escalate with a fresh implementer on the higher model at the point we currently raise the tier; use the standard reviewer for re-review of mechanical fixes; confirm every spawn passes `model`.

Test: with `impl_runs`, `resumed` and `raised` (0.8.0), measure how many batches reach a tier raise, and the outcome after it (`committed` vs `blocked`). Check `rev` vs `rounds` for re-reviews. Today's flow already starts a new implementer after a raise, so the open question is mostly the point of escalation and the reviewer tier on re-review.

Proposed rule: adopt earlier escalation if, among batches with `rounds >= 2`, the post-raise success rate is below 70%, or if rounds 2+ account for more than 25% of spend. Separately, check `tasklist-run` today for any spawn that omits the model; that is a bug fix, not a hypothesis.

## Log fields that support the evaluation

All fields are in `plugins/task-workflow/skills/tasklist-run/SKILL.md`. New in 0.8.0 are marked.

| Question | Fields |
| --- | --- |
| Tier vs rounds (idea 1) | `tiers`, `impl`, `rounds`, `outcome`, `files` (new), `lines` (new), `tasks` |
| Cost per committed task (ideas 2, 4) | `tokens` event: `orch`, `impl`, `rev` by model, joined on `batch_ts` |
| Cache behaviour (idea 3) | `tokens` event: `cr`, `cw`, `in`; `cache_breaks` (new), `max_uncached` (new) |
| Escalation (idea 5) | `raised`, `rounds`, `resumed` (new), `impl_runs` (new), `rev`, `rev_reason`, `outcome` |

Known limits of the data:

- `rounds` and `kept`/`dropped` are per batch, not per task. Test idea 1 on single-task batches.
- Token windows are time windows per repo path. Parallel sessions in the same repo during a run are mixed in.
- `analyze_transcripts.py` unit weights (input 1, cache read 0.1, cache write 1.25 or 2.0, output 5) and the per-model weights (opus 1, sonnet 0.6, haiku 0.2) are assumptions. Treat cost as relative, and check current pricing before quoting dollars.
- Nothing logs whether a batch was merged because of the sizing rules or the user's wishes, so batch size is a confound.
- Older runs (0.7.0 and earlier) lack the new fields. The `v` field stays 1 and all additions are optional, so filter with `select(.files != null)`.

## Queries

The log is `~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl`. Run `python3 -I misc/tasklist-metrics/analyze_transcripts.py --append-tokens` first so each batch has a `tokens` event. These `jq` sketches are untested; fix them against real lines.

```sh
LOG=~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl

# A. Rounds and outcome by implementer model and file count (single-task batches)
jq -s '[.[] | select(.event=="batch" and (.tasks|length)==1 and .files != null)]
  | group_by([.impl, (.files>=2)]) | map({impl:.[0].impl, multi_file:(.[0].files>=2),
    n:length, mean_rounds:(map(.rounds)|add/length),
    raised:(map(select(.raised))|length)})' "$LOG"

# B. Total raw tokens per run (sum every role and model)
jq -s '[.[] | select(.event=="tokens")] | group_by(.run) | map({run:.[0].run,
  batches:length, out:([.[]|(.orch,.impl,.rev)|to_entries[].value.out]|add)})' "$LOG"

# C. Cache-read share of input per batch, and batches with a cache break
jq -c 'select(.event=="tokens") | . as $t
  | ([($t.orch,$t.impl,$t.rev)|to_entries[].value] ) as $m
  | {run, batch_ts, cr:($m|map(.cr)|add), fresh:($m|map(.in+.cw)|add),
     cache_breaks, max_uncached}' "$LOG"

# D. Join batch and tokens on batch_ts, then group by tier and models
jq -s 'group_by([.run, (.batch_ts // .ts)])' "$LOG"
```

## When to decide

Data floor: about 10 runs across at least two projects and at least 30 batches, with at least 10 single-task batches (matching the floor in the CLI evaluation). Below that, differences are noise; keep running and logging.

Order of evaluation: ideas 1, 4 and 5 can be read from the log directly. Idea 3 needs the new cache fields to have been written (runs on 0.8.0 or later). Idea 2 is mainly an engineering question about getting an in-run estimate, so decide it last.

Each decision is a small edit to `tasklist` or `tasklist-run`, not a new component. Record the outcome here under a "Decisions" heading with the data it rests on, and bump the plugin version for any behaviour change.

## Not planned

- Installing `agent-pulse` or any external CLI as a dependency.
- A model router based on input length (ecc's `select_model`): our tier is set per task by the planner, and that is where the judgement lives.
- Changing escalation or tiers on the strength of these skills' claims alone, without our data.

## Known issues

- `tests/test_plugin_layout.py::test_each_bundle_contains_exactly_its_skills` fails for `task-workflow` (extra `tasklist` and `tasklist-run` skills). Pre-existing, noted in the earlier design doc; unrelated.
