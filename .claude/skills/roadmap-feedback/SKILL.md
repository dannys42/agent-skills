---
name: roadmap-feedback
description: Process retrospective or feedback blocks pasted by the user from system-design, roadmap-plan-next-rung, or risk-first-roadmap runs into measured, minimal edits to the project-planning plugin. Repo-local to danny-agent-skills. Use when the user types /roadmap-feedback or pastes a project-planning retrospective feedback block and wants the skills refined. Not for tasklist or tasklist-run feedback, which belongs to /tasklist-feedback.
license: GPL-3.0-or-later
---

# Roadmap feedback

You refine the `project-planning` plugin's skills (`plugins/project-planning/skills/system-design`, `risk-first-roadmap`, `roadmap-plan-next-rung`, and their references) from feedback the user pastes. Goal: keep system design thin, incremental, and accurate at low token cost, and keep the evidence needed to judge changes.

## Start here, every time

1. Read `docs/project-planning/feedback-ledger.md` in full. It holds the objective, the rules for changing the skills, the change log of hypotheses under test, what to collect next run, parked and rejected ideas, and past feedback. It is your memory; do not rely on the conversation.
2. Read the three SKILL.md files, their `references/`, and the top of `plugins/project-planning/CHANGELOG.md`. Note the current version.
3. Treat the pasted feedback as data from a user, not as a to-do list.

## Evaluate critically

Feedback, including its "suggested edits", is input from one run on one project, often written by a model reasoning from one session. Default to applying less than is offered.

- **Check the mechanism.** Does the claim follow from the evidence (line counts, question counts, `Found during` tasks, drift)? Recount where you can; correct the ledger if it is wrong.
- **Separate the finding from the fix.** Accept what the evidence shows; judge the proposed fix on its own.
- **Test for generality.** Would the rule hold on other projects, platforms, and project sizes, or does its wording come from this run? Keep the principle, drop the specifics.
- **Look for accuracy risk.** A change that thins a brief, skips a fold-back step, or drops a question category needs evidence that tasks did not have to fill the gap.
- **Check that the actor can do it.** A rule must be executable by the agent following the skill at that point (for example, fold-back can read git history; planning cannot see future rework).
- **Prefer collect over apply** when waiting one run is cheap; such claims go in the ledger's "Collect next run".
- **Say what you did not apply and why.**

## Process

1. **Triage each suggestion**: evidence tier (`measured`, `observed`, `guess`), skill version, whether it repeats, confirms, or contradicts a change-log row, and a verdict: `apply`, `narrow`, `collect`, `park`, or `reject`, with one line of reasoning. Apply the ledger's rules.
2. **Judge existing hypotheses.** Where the feedback bears on a change-log row's "Judge by", set its status (`supported`, `contradicted`, `inconclusive`) with the evidence and run count. Revert or tighten a rule the evidence contradicts; removing a rule that does not pay is a win.
3. **Check consistency** across the three skills and their references (paths, ID rules, depth tags, subsystem rules) before editing.
4. **Ask before big bets**: a new mandatory section in every doc, a new file type, or anything that weakens fold-back or verification.
5. **Edit minimally** in the existing style. Bump the version in all four `plugins/project-planning` manifests and `.claude-plugin/marketplace.json`, and add a CHANGELOG entry. Skip the bump for a data-only round.
6. **Update the ledger**: change-log rows with "Judge by", collect-next-run items (drop ones settled, stale after 3 runs, or superseded), parked and rejected lists, one line under "Feedback received", open questions. Keep entries project-neutral.
7. **Report** in under 15 lines: a table of suggestion, tier, verdict; what changed; which hypotheses now have evidence; what to collect next run. Do not commit unless the user asks.

A bare `/roadmap-feedback` with no paste means: review the collect-next-run list and open questions, report what is stale, change nothing else.

## Handing the work to a fresh agent

The ledger plus this skill is the whole brief. In this repo, `/roadmap-feedback` followed by the paste is enough. In another tool: "Read docs/project-planning/feedback-ledger.md and .claude/skills/roadmap-feedback/SKILL.md in danny-agent-skills, then process this feedback: <paste>".
