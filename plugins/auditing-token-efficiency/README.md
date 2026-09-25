# auditing-token-efficiency

Portable guidance for turning a completed task's friction into cheaper future
tasks. The plugin contains one skill, `auditing-token-efficiency`, invoked
manually with `/auditing-token-efficiency` after finishing a task — it does
not auto-trigger, so it costs nothing until you ask for it.

## What it does

Reads back through the tool calls, searches, and edits from the task just
completed and looks for recurring or expensive work: repeated discovery a
script or a documented structure could avoid, hand-run integration work an MCP
server could absorb, or wasted exploration caused by direction that was never
written down. Recommendations are filtered against the project's own stated
scope — nothing gets proposed that this project won't actually need again.

Findings land in a `Documentation/` folder at the project root:

- **`Overview.md`** — durable objectives and direction.
- **`Structure.md`** — a map of the project's targets, their directories, and
  their scope.
- **`TODO-TokenEfficiency.md`** — the actionable backlog: a checklist of
  scripts, tools, MCP recommendations, and doc updates, each tagged with a
  recommended model, broken into phases when a task is large enough to need
  its own design work.

`Documentation/` is a source of truth for direction and organization, never
for implementation — it never summarizes what the code currently does, since
that would go stale immediately. `Archive/`, `Obsolete/`, and `Completed/`
subdirectories are created only when there's something that actually belongs
in them.

## Install

### Claude Code

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install auditing-token-efficiency@danny-sung-agent-skills
```

### Codex

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add auditing-token-efficiency@danny-sung-agent-skills
```

### Other agents

```bash
npx skills add dannys42/agent-skills \
  --skill auditing-token-efficiency \
  --global \
  --agent <agent>
```
