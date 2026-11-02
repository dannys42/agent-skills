---
name: rung
description: Work out the next step of a risk-first roadmap from the project's files and run it, so the user never has to remember which command comes next. Use whenever the user types /rung, or asks what's next, to continue the project, or for the next step of the roadmap, even if they do not name this skill. Also for "close the milestone" or "close the rung". Dispatches system-design, risk-first-roadmap, roadmap-plan-next-rung (milestone planning, escalation review, milestone close) and tasklist-run, on the model the step needs; a milestone cycles through planning, rung runs and close. Mentions design-session for working a design out together. Not for designing a rung by hand (use roadmap-plan-next-rung) or for projects without a roadmap and no wish to start one.
license: GPL-3.0-or-later
allowed-tools: Bash(sh *rung/scripts/next.sh*)
---

# Rung

One command for the rung cycle. It reads the files, says what is next, and invokes the skill that does it. It adds no work of its own.

## Invocation

- `/rung` works out the step.
- `/rung status` shows the lines under [Find the step](#find-the-step) and the output of `roadmap status <roadmap>`, and does nothing else. Do not run `roadmap next` again.
- Aliases that skip the check of what is next, never shown to the owner: `/rung plan [<milestone>]`, `/rung run [<rung>] [tasklist-run flags]`, `/rung escalation <rung>`, `/rung milestone-close`, `/rung retro [<rung>]`, `/rung replan`, `/rung design`, `/rung roadmap`, `/rung checkpoint` (the look-back: `system-design checkpoint`).

## Find the step

In Claude Code, `scripts/next.sh` ran as this skill loaded (zero turns) and printed:

```
!`sh "${CLAUDE_SKILL_DIR}/scripts/next.sh"`
```

1. Lines `step`, `milestone`, `rung`, `list`, `handoff`, `model`, `command`, `why`: use them. `command` is the dispatch target (the skill and arguments to invoke) and is never shown to the owner. If project rules name a `DocDir` other than the one found, or the output lists several `Roadmap-*.md` (ask which), re-run `~/.cache/danny-agent-skills/bin/roadmap next --dir <DocDir>` or `--roadmap <file>`.
2. `roadmap: missing or older than 0.7.0`, or the block above still shows the `!` command (another harness): install and run in one Bash call: `sh "$(ls -td ~/.claude/plugins/cache/*/task-workflow/*/tools/plantools/build.sh | head -n 1)" >/dev/null && ~/.cache/danny-agent-skills/bin/roadmap next`. If the build script is not found or fails, say so in one line and use the table below.
3. Without the tool, apply this table by hand with `grep` and `ls`, to the same routes as the dispatch table:
   - No Overview (`SystemDesign/Overview.md`, or a legacy `Design-*.md`) and no roadmap: `design`. Overview, no roadmap: `roadmap`.
   - Roadmap with a `## Milestones` section: current milestone = the first not `done`. A rung of it that is open with no `Tasklist-<rung>-*.md`: `milestone-plan`. A rung carrying an `Escalation:` marker: `escalation`. Otherwise the in-progress rung (else the first `planned`) with a live list that has open tasks (a task under a heading closed as `DEFERRED`, `OBSOLETE`, `SUPERSEDED` or `INVALID` does not count): `run` (opus if more than half the open tasks are `heavy`, else sonnet), or `user` when every open task is USER or BLOCKED. An open `Tasklist-Refactor-*`, `Tasklist-M<n>-*` list: `run` it before the next rung. No open rung but `deferred` or `horizon` rungs, or no rungs: `replan`. Nothing left: `milestone-close`. No current milestone: `replan`, or `finished` when nothing is planned either.
   - Older roadmap (no milestones): the first `in progress` rung, else the first `planned` (`plan`); none, but `deferred` or horizon items: `replan`; none: `finished`. In-progress rung with open tasks: `run`/`user`; with no tasklist: `plan`; lists closed and brief `folded back`: `replan`; otherwise `close`. With no rung in progress, an open `Tasklist-Refactor-*` list is `run`.
   - A closed list still in the doc directory (not in `Completed/`) with no open task, and the rung not done: `run` (it re-enters the fold-back). A rung whose lists all moved to `Completed/` but is not done: `escalation`.
   - A `Handoff/` note with a known `Route:` outranks all of this (see Handoff).
4. Say in one line what you found and what you will do, naming the rung or milestone with its title, e.g. `Milestone 1 (Playable grid): its rungs have no tasklists → milestone planning (Opus)`.

## Model and where it runs

State the recommended `model` before starting. Then, per step, decide between a subagent on that model inside this session and a new session on it, by cost and the step's expected context size, and say the choice in one line with the reason, e.g. `Escalation review: non-interactive, small context → Opus subagent.`

- **Starting a subagent step.** The Skill tool runs in this session, so a subagent step is started with the Agent tool on the needed model. The prompt is the handoff note, or a short brief (milestone or rung, files to read), and tells it to do only the non-interactive steps (`escalation` steps 1 and 2, `milestone-close` step 3, the re-read) and to return the owner items and what it committed. This session then presents the owner items and applies the rulings. If the remaining steps need Opus (a re-plan trigger, the demo) and this session is not on Opus, write a handoff note and end with `Next: /rung (Opus: /model opus)`.
- Non-interactive steps (`escalation` review steps 1 and 2, the `milestone-close` re-read) may be subagents on the needed model: a bounded brief, a bounded report. Prefer a subagent when the context to carry is small; prefer a session when it is large.
- Owner-facing steps (`milestone-plan`, the demo, `design`, `replan`, any design session) need a session on the right model, because the owner talks to it.
- The wrong-model stop applies only when you pick a session: if the current model is not the recommended one, ask once to switch (`/model opus`, then `/rung`) or continue. A subagent has no such stop.
- `run`: `tasklist-run` is not pinned and its orchestrator model depends on the list; if `model` is opus and the session is not on Opus, ask once as above. Any other mismatch: one line, then proceed.

## Dispatch

Use the Skill tool with the `command` target. One line per route the tool can return:

| `step` | Dispatch | Model |
| --- | --- | --- |
| `design` | `system-design`; for "let's work it out together" mention `design-session` | opus |
| `roadmap` | `risk-first-roadmap` | opus |
| `milestone-plan` | `roadmap-plan-next-rung plan <milestone>`: plans every unplanned rung of the milestone with the owner (session) | opus |
| `escalation` | `roadmap-plan-next-rung escalation <rung>`: the Opus review of a fold-back that stopped (subagent-capable for steps 1 and 2) | opus |
| `run` | `tasklist-run <list> <flags>`; a rung's run folds itself back. Also a refactor, fix or follow-up list | per `model` |
| `user` | show the pending USER tasks' steps verbatim and ask for the `Done when` confirmation per `tasklist-run`'s "USER tasks", then continue as `run` | per `model` |
| `replan` | `risk-first-roadmap`. A `why` starting `no planned rung` or `no current milestone` runs its deferred-rung and horizon steps: bring one back, detail one, or drop them | opus |
| `finished` | say every rung is done and offer to extend the ladder with `risk-first-roadmap`; do not invoke it unasked | opus |
| `milestone-close` | `roadmap-plan-next-rung milestone-close <milestone>`: checks, quality, re-read (subagent-capable), demo (session), ruling, retro, re-plan | opus |
| `plan`, `close` (older roadmaps only) | `roadmap-plan-next-rung plan`, no ID: an older roadmap has no milestones, so that session migrates the docs, folds back an in-flight rung first, then plans | opus |

`/rung retro [<rung>]` and `/rung checkpoint` stay as aliases (`roadmap-plan-next-rung retro`, `system-design checkpoint`); the tool never returns them.

**Handoff.** When the output has a `handoff:` line, read that note before dispatching: it names the route, the exact question and what to read ([handoff.md](../roadmap-plan-next-rung/references/handoff.md)). Dispatch its route as in the table (a legacy `plan` or `close` note too), give the step the note's content (it is the brief when the step runs as a subagent), then delete the note (`rm`) so the step does not look again. A step that stops for the owner again writes a new one.

**Next lines.** Every `Next:` line is `/rung`, plus the model switch when the next step needs Opus (`/model opus`). The prose before it names the rung or milestone with its title and says why. No IDs and no other command in the line.

Follow the invoked skill fully. This skill adds nothing after it, because each step ends with its own `Next:` line.

## If a linked skill is missing

This skill hands off to `system-design`, `risk-first-roadmap` and `roadmap-plan-next-rung` (`project-planning` plugin) and `tasklist-run` (`task-workflow` plugin). When one is absent, say once, in one line, which is missing and how to install it (`claude plugin install project-planning@danny-sung-agent-skills` or `claude plugin install task-workflow@danny-sung-agent-skills`), and stop at the step that needs it.
