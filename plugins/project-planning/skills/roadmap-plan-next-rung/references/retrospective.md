# Retrospective

Shared by `roadmap-plan-next-rung` (`retro [L3]`, and offered at the end of fold-back) and `system-design` (offered after sign-off, and `retro` any time). Its purpose is to tell the user what is worth changing, and the maintainer of these skills whether the design stayed thin, the run stayed cheap, and the quality pass paid, with evidence a clean agent can act on later.

Build it from the project's actual docs, history and metrics, not from memory. Apply nothing; the user decides what to do with it.

## Gather the evidence

- **Rung retro:** the brief, every design doc it lists as touched, the rung's tasklist and its `-Tidy` tasklist if one ran (in `<DocDir>/` or `<DocDir>/Completed/`), the rung's commits (`git log --oneline <Base>..HEAD`, and `git log -- <DocDir>/SystemDesign` for doc changes), and the metrics: run `metrics tokens` (no tasklist argument; it adds every run's token events from the transcripts, options `--log`, `--root`, `--dry-run`), then `metrics summary <rung tasklist>` (the file name is enough, also after the list moved to `Completed/`; runs are matched by the `list` name in their `start` line, then by the batch commit). Both are the `task-workflow` plugin's `metrics` tool, see the `code-quality-pass` skill's "Metrics tool check". Without the tool, add up the rung's `batch` lines from the metrics log by hand.
- **Check before you guess:** when a number is missing or odd (0 batches, 0 tokens, rounds unknown), spend one command on the cause before tagging it `guess`: `grep '"list":"<tasklist file name>"' ~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl` for the run's `start` and `end` lines (the `end` line's `note` often says why), and `metrics --version`. Report what was found under `Diagnosed:` in the feedback block; a retro that sends "cause unknown" without this check has skipped its job.
- **System-design retro:** the Overview (and any subsystem doc written this session) and its git history.
- **Sizes:** lines before and after for each touched design doc (`git show <rev>:<path> | wc -l` against `wc -l <path>`).
- **Questions:** the questions asked and how many answers changed the draft versus confirmed a default. From the same session this is `observed`; in a later session, infer it from assumption and decision rows (`confirmed` versus replaced) and mark it so.
- **Rework:** in the tasklist, items with `Found during`, `[-] INVALID`, or `SUPERSEDED`, and tasks whose `Model` was raised.

## The report

One screen, this shape, at most about 25 lines before the feedback block:

```text
Rung L20 retro · project-planning 0.6.0, task-workflow 0.12.1
Verdict: design right-sized · run 10 batches, 2 rounds (median 1) · quality tidy 3 commits, 1 proposal
<the table from `metrics summary`, pasted as is>
Worth changing:
1. ⚑ [measured] Rung diff 2357 lines vs median 484: the brief scoped two data sources → split such rungs at planning
   Why: high impact (changes how every later rung is cut) · Options: split at planning (recommended; pro: smaller reviews, con: more briefs) / keep and raise the review tier (pro: no re-plan, con: costlier rounds)
2. [observed] Reviewer entries missing from `agents` in every batch → tasklist-run logging gap
Keep: assumptions checked by one real call before tasks; 0 rework
Tooling: T5–T8 each rebuilt the same fixture by hand (~4 tool calls × 4 batches, ~6% of implementer tokens) → a project fixture script; clears the 3% bar
```

- **Verdict:** one line. Design: `right-sized`, `heavy` (sections nobody used) or `thin` (gaps tasks had to fill). Run: batches and rounds against the median. Quality: what the pass did, `deferred`, or `not run`.
- **Numbers:** the `metrics summary` table and its "Largest batches" and "Stands out" lines, pasted as is. The tool already leaves out rows that are zero for this rung and its peers.
- **Worth changing:** numbered, each tagged `measured` (counted from docs, git or the log), `observed` (seen in this session) or `guess`, each ending in `→` and the change or action. Draw from: brief size and sections used, questions that changed the draft, assumptions overturned, drift between brief and code and which side was fixed, rework and `Found during` tasks, subsystem promotions and whether they met a trigger, diagram problems, missing-sibling notices, Overview growth, tier mismatches, correction rounds and their causes, tool-count outliers, `TaskStop`s or repeat hand-backs (always listed, with the cause or "cause unknown"), tidy items reverted, proposals raised. Number the items that need the user's attention first (high impact, or resting on a `guess` or a single observation; rules in [presenting-for-review.md](presenting-for-review.md)), mark them `⚑`, and give each one indented line with why and two or three options, recommended first, each with a pro and con. At most 3, so the report stays one screen.
- **Keep:** one line, only when something worked that a later edit might break.
- **Tooling:** would a custom tool have cut this rung's cost? Look at the largest batches, the stands-out lines, a `Token efficiency` group in the tasklist, and repeated hand-run sequences or rediscovery reads in the session. For each candidate, estimate its share `s` of the rung's tokens and apply the decision rule: at least 8% realistic saving is worth building for cost; 3–8% only if it also improves reliability; under 3% is left out. Say whether it is a project tool (a script or fixture in the project) or a skill tool (a `metrics`/`tasklist` subcommand or a skill rule).

**Omission rule:** delete every line whose content would be "none", "nothing found", "as expected" or "no change". No empty headings. A rung with nothing worth changing gets one line: `Rung L20 retro: nothing stands out (<the verdict line>)`, and no feedback block.

A system-design retro uses the same shape with `Design retro` in place of the rung, no numbers table, and only the design items.

## Feedback block

A retro ends with exactly one feedback block, only when some item has a suggested edit, for the single command `/retro-feedback` (it replaces the old per-plugin commands). Items for both plugins go in it, each tagged `[project-planning]` (design, roadmap and quality-pass skills) or `[task-workflow]` (`tasklist`, `tasklist-run`, `metrics`). Never split it into two blocks, and never put a plugin's items under the other plugin's tag. Project-neutral by default: no project names, file paths, or code unless the user asks. Read skill versions from each plugin's manifest (`../../.claude-plugin/plugin.json` relative to each skill's folder); if it is absent, write "version unknown (standalone install)".

Print the block last in the retro, in a fenced `text` block, preceded by one plain line: `Paste this block into /retro-feedback in danny-agent-skills:`. Nothing follows the block except the offer to save (below). The block is self-contained: do not refer to the report above it.

```text
retro feedback
Run: <rung ID or design> retro · <date> · run IDs <ids from the metrics log, or none>
Skills: <skill> <version> (<plugin>); <other skills used, with versions>
Context: <rung retro | system-design retro | run retro>; <project kind, e.g. "macOS document app">; <new | adopted>
Evidence:
- [measured] [task-workflow] ...
- [observed] [project-planning] ...
Diagnosed: <checks already run and what they found, one line each; omit when none>
Suggested edits (plugin, skill, section, change, why; aim: thinner design and cheaper runs, same accuracy):
- [task-workflow] <skill>, <section>: <change>; <why>
- [project-planning] <skill>, <section>: <change>; <why>
```

Offer to save the retrospective to the scratchpad or a path the user names. Do not write it into the project's design docs by default; they describe the system, not the process.
