---
name: audit-token-efficiency
description: Reviews the task just completed for token-efficiency opportunities — repeated searches or transforms a script could replace, hand-run work an MCP server could absorb, and missing project knowledge that caused rediscovery — then records durable findings in the project's Documentation folder. Invoke manually with /audit-token-efficiency after finishing a task; it does not auto-trigger.
disable-model-invocation: true
license: GPL-3.0-or-later
---

# Audit Token Efficiency

Turn hindsight into cheaper future tasks. Look at what the just-completed task
actually cost in tool calls, searches, and back-and-forth, and write down the
few interventions — scripts, tools, MCP servers, or documentation — that would
have made it cheaper, scoped to what this project will actually need again.

## Scope

Inspect only the conversation since the user's most recent task request — not
the whole project history, and not prior retrospection runs. A cheap, focused
pass beats a thorough one; if a pattern is real, it will show up again on a
future run and earn its place then.

## What to look for

Read back through the tool calls, edits, and searches from the completed task
and ask, for each recurring or expensive step: what would have made this free
or automatic?

- **Repeated discovery** (the same grep, the same "where is X defined," the
  same directory listing run more than once) → the answer belongs in
  `Structure.md`, not a script.
- **Repeated deterministic transforms** (reformatting, extracting, or
  computing the same shape of thing by hand each time) → a script.
- **Repeated hand-run integration work** (polling the same API, driving the
  same external tool through raw shell/HTTP calls) → an MCP server
  recommendation. Check whether one already exists — installed MCP config, or
  a well-known public server — before proposing a custom one.
- **Wrong assumptions or wasted exploration caused by unstated direction**
  (the task went sideways because a goal or constraint wasn't written down
  anywhere) → `Overview.md`.

Discard anything unlikely to recur in this project. Check
`Documentation/Overview.md` (if present) for stated direction and scope before
proposing anything — a recommendation that doesn't serve this project's actual
objectives doesn't belong in the backlog.

If nothing from the completed task clears this bar, say so and leave
`Documentation/` untouched — a spurious edit costs more than the finding is
worth.

## Documentation/ layout

Create `Documentation/` at the project root on first use; update it in place
on later runs rather than rewriting it.

```
Documentation/
├── Overview.md              — objectives and direction (why)
├── Structure.md             — build targets, their directories, and scope
├── TODO-TokenEfficiency.md  — the actionable backlog this skill produces
├── Archive/                 — situational: old snapshots, not Obsolete/Completed
├── Obsolete/                — situational: superseded direction/structure, kept for history
└── Completed/               — situational: finished backlog items, moved out to stay short
```

Only create a subdirectory when there's actually something to put in it.

Treat `Documentation/` as the source of truth for direction and organization,
never for implementation — don't summarize what the code currently does; that
goes stale, and the code is already the source of truth for it.

### First run in a project

If `Documentation/` doesn't exist yet, create `Overview.md` and `Structure.md`
from [references/documentation-templates.md](references/documentation-templates.md),
filled from what's actually discoverable — a README, CLAUDE.md, package
manifests, an existing plugin or marketplace listing — rather than
interviewing the user. Mark anything inferred rather than stated, so it's
clear what still wants a human's confirmation. Create `TODO-TokenEfficiency.md`
empty; it only gets content from actual findings. Spend a handful of tool
calls on this, not a deep audit — thin and clearly-marked-as-inferred beats
thorough and expensive.

### Overview.md

Durable objectives and direction. Read this before filtering recommendations.
Write to it only when the completed task revealed an actual direction change
or gap — and even then, add rather than silently overwrite: append a dated
note the user can fold in, don't rewrite their prose.

### Structure.md

One entry per target (package, plugin, module, app — whatever this project's
actual unit is):

```markdown
## <target name>
- Directory: `path/to/target`
- Purpose: one or two sentences of scope, not an implementation summary.
```

Add an entry when this task's exploration had to rediscover a target's
purpose that wasn't written down. Don't add an entry for something you
already found documented — that's a sign it's working.

### TODO-TokenEfficiency.md

The concrete backlog: not "direction," actual tasks a future invocation (of
any model) can pick up and execute. Use a checklist so completion is visible
at a glance:

```markdown
- [ ] Write `scripts/list-untagged-releases.sh` to replace manually diffing `git tag` output against the changelog each release — recommended model: Haiku 4.5
- [ ] Recommend an MCP server for GitHub PR review data instead of ad hoc `gh api` calls — recommended model: Sonnet 5
```

When one recommendation is large enough to need its own design work (a new
program, a custom MCP server, a nontrivial script) and other backlog items
depend on it existing first, group the whole cluster into phases instead of
flat items. Each phase is its own heading with its own checklist — not a
sub-step nested under one task:

```markdown
## Phase 1
- [ ] task 1
- [ ] task 2

## Phase 2 — Build a local search index for this repo's skills
- [ ] pick an index format, prove it answers one real query
- [ ] build the indexer script
- [ ] wire it into a skill

## Phase 3
- [ ] task that depends on the Phase 2 index existing
- [ ] task that depends on the Phase 2 index existing
```

Use as many or as few phases as the actual dependency chain needs — including
none at all when nothing in the backlog depends on something larger being
built first. Phases express "this can't start until that's built," not "this
task deserves more sub-bullets."

Rules for this file:

- Append; don't remove or rewrite existing unchecked items.
- Before adding an item, check the file (including
  `Completed/TODO-TokenEfficiency.md` if it exists) for something equivalent
  already recorded — don't duplicate. Skim existing titles rather than
  re-reading full context for each one; this check should stay cheap.
- Never check off an item yourself. `[x]` means a human or a later task
  confirmed it's actually done.
- Recommend the smallest model that can execute the task correctly: a
  fast/cheap tier (e.g. Haiku 4.5) for fully-specified, deterministic steps; a
  mid tier (e.g. Sonnet 5) for ordinary feature or script work; reserve a
  frontier tier (e.g. Opus 5.5) for genuinely ambiguous design work.
  Substitute the equivalent tier when this backlog is executed under a
  different tool.
- When most of the file's items are checked off, move the completed ones into
  `Completed/TODO-TokenEfficiency.md` (creating it if needed) so the active
  file stays short. Leave unchecked items in place.

## Choosing a script's language

When a backlog item recommends a script, name its language too, so a future
run doesn't have to re-derive this project's conventions:

1. Check first whether the project already has one: an existing `scripts/`
   directory (or equivalent) sets the precedent, and `CLAUDE.md` or
   `Overview.md` may already state a preference. Follow what's already there
   over any default below.
2. If nothing exists yet, default to a shell script (`.sh`) for anything
   small and deterministic — roughly under 100 lines. Escalate to Python or a
   Swift CLI once the task needs real structure: state beyond a few
   variables, error handling beyond exit codes, or logic that would be
   painful to get right in bash.
3. For a Swift CLI, reach for
   [swift-argument-parser](https://github.com/apple/swift-argument-parser)
   for argument handling,
   [Rainbow](https://github.com/onevcat/Rainbow) for terminal color output,
   and [swift-subprocess](https://github.com/swiftlang/swift-subprocess) for
   shelling out — only the ones the task actually needs, not all three by
   default.
4. Once a project's preference becomes clear — from what you found, or from
   what its maintainer says when the item gets picked up — record it in
   `Overview.md` so it doesn't have to be rediscovered next time. That's the
   same rediscovery cost this skill exists to eliminate.

## Report back

After updating `Documentation/`, tell the user what changed in a few lines —
which files were touched and how many backlog items were added — not a
restated copy of the files. The documentation is the artifact; the chat reply
is a pointer to it.
