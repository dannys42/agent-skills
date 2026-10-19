---
name: retro-feedback
description: Process the one feedback block a retrospective prints (from roadmap-plan-next-rung, system-design or tasklist-run) into measured, minimal edits to the project-planning and task-workflow plugins, routed by each item's plugin tag. Repo-local to danny-agent-skills. Use when the user types /retro-feedback or pastes a retrospective feedback block, transcript audit or metrics lines and wants the skills refined. Replaces /tasklist-feedback and /roadmap-feedback.
license: GPL-3.0-or-later
---

# Retro feedback

You refine two plugins from feedback the user pastes, one block, one command. Each item in the block names its plugin; you edit only that plugin.

| Tag | Skills you may edit | Ledger | Manifests to bump | Goal |
| --- | --- | --- | --- | --- |
| `[task-workflow]` | `plugins/task-workflow/skills/tasklist`, `tasklist-run` (and `decision-driven-design` only for its own items) | `docs/task-workflow/feedback-ledger.md` | `plugins/task-workflow/` `.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `gemini-extension.json`, the root `.claude-plugin/marketplace.json`, and the `skill` value in `tasklist-run`'s metrics text | Lower total run cost without lowering accuracy; keep the data needed to judge changes |
| `[project-planning]` | `plugins/project-planning/skills/system-design`, `risk-first-roadmap`, `roadmap-plan-next-rung`, `code-quality-pass`, and their references | `docs/project-planning/feedback-ledger.md` | the same four manifests under `plugins/project-planning/` and `.claude-plugin/marketplace.json` | Keep design thin, incremental and accurate at low token cost |

An item without a tag: route it by the skill it names; if that is unclear, ask.

## Start here, every time

1. Read the ledger of each plugin the block touches, in full (not the other one). It holds the objective, the rules for changing the skills, the change log of hypotheses under test, parked ideas and past feedback. It is your memory; do not rely on the conversation.
2. Read the SKILL.md files of the skills the items name, their `references/` when an item concerns them, and the top of that plugin's `CHANGELOG.md`. Note the current version.
3. For `[task-workflow]` items, read `~/.local/state/danny-agent-skills/task-workflow/watchlist.md` if it exists (see [Watchlist](#watchlist)).
4. Treat the pasted feedback as data from a user, not as a to-do list. If the block's `Diagnosed:` line already answers a question, use it; re-check with one command only when it affects a verdict.

## Evaluate critically

Pasted feedback, including its estimates and "suggested edits", is suggestive input from one run on one project. Its author may be a model reasoning from a single transcript. Default to applying less than is offered. Before any verdict:

- **Check the arithmetic and the mechanism.** Does the claimed saving or defect follow from the data (tokens versus cost per token, turns versus result size, line counts, `Found during` tasks)? Recompute; correct the ledger if it is wrong.
- **Separate the finding from the fix.** Accept what the data shows; judge the proposed fix on its own. A real defect does not prove the suggested rule is the right remedy.
- **Test for generality.** Would the rule hold on other projects, languages and task types, or does its wording (named categories, tools, platforms) come from this run? Keep the principle, drop the specifics.
- **Look for accuracy risk.** A rule that removes or downgrades a check, thins a brief, or skips a fold-back step needs evidence that nothing was missed. Absence of findings in a few cases is weak evidence. Ask what a miss costs.
- **Check that the actor can do it.** The agent that follows the rule must be able to execute it at that point (the `tasklist-run` orchestrator does not read source; planning cannot see future rework).
- **Prefer collect over apply** when waiting one run is cheap. Apply after one run only when the change is cheap, reversible and has a named metric, and say in the changelog that it is a one-run hypothesis.
- **Say what you did not apply and why**, even when the user did not ask.

## Process

1. **Triage each item** against its ledger: evidence tier (`measured`, `observed`, `guess`), the skill version that produced it, whether it repeats, confirms or contradicts a change-log row, and a verdict: `apply`, `narrow` (a smaller version), `collect` (add a metric or watchlist item, change nothing yet), `park`, or `reject`, with one line of reasoning. Apply the ledger's rules: guesses never become rules; one run is a hypothesis; every rule costs tokens in every future run; protect accuracy; no scripts or mandatory fields without measured savings.
2. **Judge existing hypotheses.** Where the block or its metrics lines bear on a change-log row's "Judge by", set its status (`supported`, `contradicted`, `inconclusive`) with the evidence and run count. Revert or tighten a rule the data contradicts; removing a rule that does not pay is a win.
3. **Check consistency** across the skills of that plugin (and `tasklist-run` against `tasklist`) before editing: a new rule must not contradict an existing one.
4. **Ask before big bets:** a compiled tool, a new field or section every task or doc must carry, or anything that weakens review, fold-back or verification. Otherwise proceed without asking.
5. **Edit minimally** in the existing style. Ship mechanics per the table: version bump in every manifest listed, a `CHANGELOG.md` entry, new or updated change-log rows in the ledger with a "Judge by" metric. Skip the bump for a plugin where nothing changed (data-only round).
6. **Update the ledgers and watchlist:** change-log rows, rejected or parked list, one line under "Feedback received", open questions; for `[task-workflow]`, add, update or drop watchlist items; for `[project-planning]`, the ledger's "Collect next run" list (drop items settled, stale after 3 runs, or superseded). Keep entries project-neutral and short. When a ledger's change log passes about 40 rows, fold `supported` and `contradicted` rows into one-line summaries so the next read stays cheap.
7. **Report** in under 15 lines: a table of item, plugin, tier, verdict; what changed; which hypotheses now have evidence; what data to collect next run. Do not commit unless the user asks. Put a "Needs your attention" section above the table, outside the 15 lines, in the shape in `plugins/project-planning/skills/roadmap-plan-next-rung/references/presenting-for-review.md`. Flag at most 5 verdicts that are high impact (anything touching review, correction limits, tiers, fold-back, or adding a mandatory field or section) or low confidence (`apply` or `narrow` on one run, `reject` of a suggestion that repeats). Give each the options (keep, revert, narrow, collect instead) with a pro and con, recommended first. Every verdict stays in the table, marked `⚑` when flagged. A big-bet question in step 4 uses the same shape.
8. **Check the producer too.** If the block was hard to act on (missing tier, version or run ID, a guess that one command would have settled, items for the wrong plugin), say so in one line and fix `roadmap-plan-next-rung`'s `references/retrospective.md` ("Feedback block") or the retro wording in `tasklist-run`, as a `[project-planning]` or `[task-workflow]` edit under the same rules.

## Model

Sonnet 5.5 is enough for routine triage, since the ledger rules carry the judgment. Use Opus 5.5 when a verdict touches review, tiers, correction limits or fold-back, or when a big bet is up. End the report with `Next: <command> (<Model>: /model <alias>)` only when a follow-up exists (for example `/tasklist-run <file>` or a re-plan), otherwise omit it.

## Watchlist

For `[task-workflow]` items: the ledger holds settled decisions. Claims that need more evidence before a decision go in `~/.local/state/danny-agent-skills/task-workflow/watchlist.md`, next to `metrics.jsonl`: outside every repo, never committed, so raw project detail can stay in it. Create it on first use. It is a short queue, not an archive.

**Admit** an item only if it has: a one-line claim, its tier and source (run ID, skill version), a concrete check (a query against `metrics.jsonl` or a named transcript signal), the effect that would settle it (supported if X, contradicted if Y), `added` date, `runs_seen` (starts at 1), and `last_checked` (run ID). Store pointers to run IDs, not copies of metrics lines or transcripts. No check, no admission: an untestable guess is dropped, not queued.

**Cap:** at most 10 items, at most 5 lines each. When full, drop the lowest-value item before adding: lowest (likelihood it is real x saving if real) divided by cost of the check, oldest first on a tie.

**Drop** an item when any of these holds:
1. **Settled.** The check ran. Supported: apply it and add a change-log row to the ledger. Contradicted: add a one-line sanitized entry to the ledger's rejected or parked list, only if the idea is likely to come back. Then delete the item.
2. **Stale.** 3 runs have passed with no data that bears on it.
3. **Superseded or duplicate.** A shipped change or another item already covers it.
4. **Not worth it.** Recomputed, the saving if true is smaller than what a rule or the check itself would cost per run.
5. **Overflow.** Dropped to make room, by the cap rule above.

Every invocation that touches `[task-workflow]`: check each item against the metrics lines newer than its `last_checked`, update `runs_seen` and `last_checked`, and apply the drop rules. Ledger entries made from the watchlist stay project-neutral (no repo names, no task IDs). A bare `/retro-feedback` with no pasted block means: run these checks for the watchlist, review each ledger's open questions and collect-next-run list, report what settled or went stale, change nothing else.

## When the user pastes raw data instead of conclusions

Metrics lines or transcript summaries without suggestions: skip triage, compare against the ledger's "Judge by" columns, update statuses, and propose edits only where the data supports them. If the data is from one run on a version already marked `untested`, record it and say what a second run would settle.

## Handing the work to a fresh agent

The ledgers plus this skill are the whole brief; the watchlist is optional local state. A fresh session needs only `/retro-feedback` followed by the pasted block. In another tool: "Read .claude/skills/retro-feedback/SKILL.md and the ledger(s) under docs/ in danny-agent-skills, then process this feedback: <paste>".
