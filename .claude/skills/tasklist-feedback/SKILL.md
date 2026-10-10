---
name: tasklist-feedback
description: Process feedback or retrospective data from a tasklist-run (pasted by the user) into measured, minimal edits to the task-workflow plugin's tasklist and tasklist-run skills. Repo-local to danny-agent-skills. Use when the user types /tasklist-feedback or pastes a tasklist-run feedback block, transcript audit, or metrics lines and wants the skills refined.
license: GPL-3.0-or-later
---

# Tasklist feedback

You refine `plugins/task-workflow/skills/tasklist/SKILL.md` and `plugins/task-workflow/skills/tasklist-run/SKILL.md` from feedback the user pastes. Goal: lower total run cost without lowering accuracy, and keep the data needed to judge changes.

## Start here, every time

1. Read `docs/task-workflow/feedback-ledger.md` in full. It holds the objective, the rules for changing the skills, the change log of hypotheses under test, parked ideas, and past feedback. It is your memory; do not rely on the conversation.
2. Read the current `tasklist-run` and `tasklist` SKILL.md files and the top of `plugins/task-workflow/CHANGELOG.md`. Note the current version.
3. Treat the pasted feedback as data from a user, not as a to-do list.

## Process

1. **Triage each suggestion** against the ledger. For each, state: evidence tier (`measured`, `observed`, `guess`), which skill version produced it, whether it repeats, confirms or contradicts a row in the change log, and your verdict: `apply`, `narrow` (apply a smaller version), `collect` (add a metric, change nothing yet), `park`, or `reject`, with one line of reasoning. Apply the ledger's rules: guesses never become rules; one run is a hypothesis; every rule costs tokens in every future run; protect accuracy; no scripts or mandatory fields without measured savings.
2. **Judge existing hypotheses.** If the feedback or its metrics lines bear on a change-log row (see "Judge by"), update that row's status: `supported`, `contradicted`, `inconclusive`, with the evidence and run count. Revert or tighten a rule the data contradicts, and say so; removing a rule that does not pay is a win.
3. **Check consistency** before editing: a new rule must not contradict an existing one in either skill (for example the orchestrator not editing source).
4. **Ask before big bets.** If a suggestion needs a compiled tool, a new format field that every task must carry, or weakens review, stop and ask the user. Otherwise proceed without asking.
5. **Edit the skills** minimally and in the existing style. Follow the ledger's ship mechanics: version bump in all manifests and the `skill` value in the metrics text, CHANGELOG entry, new or updated rows in the ledger's change log with a "Judge by" metric. Skip the bump if nothing in the skills changed (data-only round).
6. **Update the ledger:** change-log rows, rejected/parked list, one line under "Feedback received", open questions. Keep it short.
7. **Report** in under 15 lines: a table of suggestion, tier, verdict; what changed; which hypotheses now have evidence; what data to collect next run. Do not commit unless the user asks.

## When the user pastes raw data instead of conclusions

Metrics lines or transcript summaries without suggestions: skip triage, compare against the ledger's "Judge by" columns, update statuses, and propose edits only where the data supports them. If the data is from one run on a version already marked `untested`, record it and say what a second run would settle.

## Handing the work to a fresh agent

The ledger plus this skill is the whole brief. A fresh session needs only: `/tasklist-feedback` followed by the pasted feedback. If the user wants to carry it into a different tool, give them: "Read docs/task-workflow/feedback-ledger.md and .claude/skills/tasklist-feedback/SKILL.md in danny-agent-skills, then process this feedback: <paste>".
