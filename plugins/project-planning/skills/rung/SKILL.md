---
name: rung
description: Work out the next step of a risk-first roadmap from the project's files and run it, so the user does not have to remember which command comes next. Routes to system-design, risk-first-roadmap, roadmap-plan-next-rung or tasklist-run. A rung takes three sessions - plan, run, close. Use whenever the user types /rung, or asks what's next, to continue the project, or for the next step of the roadmap, even if they do not name this skill. Not for designing a rung by hand (use roadmap-plan-next-rung) or for projects without a roadmap and no wish to start one.
license: GPL-3.0-or-later
allowed-tools: Bash(sh *rung/scripts/next.sh*)
---

# Rung

One command for the rung cycle. It reads the files, says what is next, and invokes the skill that does it. It adds no work of its own.

## Invocation

- `/rung` works out the step.
- `/rung status` shows the lines under [Find the step](#find-the-step) and the output of `roadmap status <roadmap>`, and does nothing else. Do not run `roadmap next` again.
- Overrides: `/rung plan [L5]`, `/rung run [L3] [tasklist-run flags]`, `/rung close [L3]`, `/rung retro [L3]`, `/rung replan`, `/rung design`, `/rung roadmap`. An override skips the check of what is next but still names the rung if omitted.

## Find the step

In Claude Code, `scripts/next.sh` ran as this skill loaded (zero turns) and printed:

```
!`sh "${CLAUDE_SKILL_DIR}/scripts/next.sh"`
```

1. Lines `step`, `rung`, `list`, `model`, `command`, `why`: use them. If project rules name a `DocDir` other than the one found, or the output lists several `Roadmap-*.md` (ask which), re-run `~/.cache/danny-agent-skills/bin/roadmap next --dir <DocDir>` or `--roadmap <file>`.
2. `roadmap: missing or not 0.5.1`, or the block above still shows the `!` command (another harness): install and run in one Bash call: `sh "$(ls -td ~/.claude/plugins/cache/*/task-workflow/*/tools/plantools/build.sh | head -n 1)" >/dev/null && ~/.cache/danny-agent-skills/bin/roadmap next`. If the build script is not found or fails, say so in one line and use the table below.
3. Without the tool, apply this table by hand with `grep` and `ls`:
   - No Overview (`SystemDesign/Overview.md`, or a legacy `Design-*.md`) and no roadmap: `design`. Overview, no roadmap: `roadmap`.
   - Current rung: the first `in progress` on the ladder, else the first `planned` (`plan`). None: `finished`.
   - In-progress rung R with a `Tasklist-R-*.md` (not in `Completed/`) that has open tasks: `run` (model opus if more than half the open tasks are `heavy`, else sonnet), or `user` when every open task is USER or BLOCKED.
   - In-progress rung R with no tasklist: `plan`. All of R's lists closed and the brief `folded back`: `replan`. Otherwise: `close`.
4. Say in one line what you found and what you will do, e.g. `L3: tasks closed, brief not folded back → close (Opus)`.

## Model

`system-design`, `risk-first-roadmap` and `roadmap-plan-next-rung` pin `model:` in their frontmatter and switch model themselves where the harness supports it. `tasklist-run` is not pinned, and its orchestrator model depends on the list. For `run`, if `model` is opus and the session is not on Opus, ask once: switch (`/model opus`, then `/rung`) or continue. Any other mismatch: one line, then proceed.

## Dispatch

Use the Skill tool.

- `design`: `system-design`.
- `roadmap`, `replan`: `risk-first-roadmap`.
- `finished`: say every rung is done and offer to extend the ladder with `risk-first-roadmap`. Do not invoke it unasked.
- `plan`: `roadmap-plan-next-rung <rung>`.
- `run`: `tasklist-run <list> <flags>`.
- `user`: show the pending USER tasks' steps verbatim and ask for the `Done when` confirmation per `tasklist-run`'s "USER tasks", then continue as `run`.
- `close`: `roadmap-plan-next-rung close <rung>`.
- `retro`: `roadmap-plan-next-rung retro <rung>`.

Follow the invoked skill fully. This skill adds nothing after it, because each step ends with its own `Next:` line.

## If a linked skill is missing

This skill hands off to `system-design`, `risk-first-roadmap` and `roadmap-plan-next-rung` (`project-planning` plugin) and `tasklist-run` (`task-workflow` plugin). When one is absent, say once, in one line, which is missing and how to install it (`claude plugin install project-planning@danny-sung-agent-skills` or `claude plugin install task-workflow@danny-sung-agent-skills`), and stop at the step that needs it.
