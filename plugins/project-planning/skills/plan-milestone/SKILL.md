---
name: plan-milestone
description: Plan a milestone of a risk-first roadmap, review a rung whose automatic fold-back escalated, and close a milestone. Use when the user says "plan the milestone", "plan the next milestone", "design the next rungs", "what do I build next and how", "design before the tasklist", "close the milestone" or "demo the milestone", or when `/rung` routes milestone planning, an escalation review or milestone close here (even unnamed). Milestone planning runs the system design look-back, agrees the milestone's design delta (seams, threat and privacy, names), and writes every rung's brief and tasklist, each with a regression test. The escalation review judges what a fold-back could not and fixes the side that is wrong. Milestone close re-reads every fold-back together, runs the full suite, holds the owner's demo against the exit criteria, one retro and the next milestone's re-plan. Not for the whole system design (system-design), ordering milestones and rungs (risk-first-roadmap) or a rung's routine fold-back.
license: GPL-3.0-or-later
model: opus
---

# Roadmap: Plan and Close a Milestone

The system design is agreed only as deep as the current milestone needs. This skill adds the rest just before the milestone is built, and only for what it touches: milestone planning writes every rung's brief and tasklist in one session, each rung runs and folds itself back on Sonnet, and Opus returns only for an escalation and for milestone close. Nothing here plans or closes one rung per Opus session.

Terms (system design, milestone, seam, `settled`/`working`/`proposed`/`owner`, reviewable surfaces, automatic fold-back, escalation, "decide after it runs" list, owner preference) are defined in the system-design skill's [terms.md](../system-design/references/terms.md); this skill cites them. Depth follows the milestone: never design a component or open a subsystem doc its rungs do not touch.

Read [rung-brief-template.md](references/rung-brief-template.md) before drafting, [diagrams.md](references/diagrams.md) before drawing, [presenting-for-review.md](references/presenting-for-review.md) before asking the owner to rule on anything, and the system-design skill's [subsystems.md](../system-design/references/subsystems.md) for subsystem docs and cross-doc IDs.

## Invocation

`/rung` picks the step; the owner never types another command, and every `Next:` line is `/rung` plus the model switch when the step needs it, after a sentence saying what the step is and why. Routes from `roadmap next`, internal labels only: `milestone-plan` → [Milestone planning](#milestone-planning), `escalation` → [Escalation review](#escalation-review), `milestone-close` → [Milestone close](#milestone-close). Aliases of this skill, never shown: `plan [M2]`, `escalation [L3]`, `milestone-close [M2]`, `retro [M2|L3]`. Any ID shown to the owner carries its name: "L4 (folder suggestions)", never "L4".

## Files

`DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`; follow project rules when they name one).

```
<DocDir>/Roadmap-<Topic>.md                          milestone map, ladder, "decide after it runs" list (risk-first-roadmap)
<DocDir>/SystemDesign/Overview.md                    the system design (system-design)
<DocDir>/SystemDesign/<Subsystem>.md                 a subsystem's design, same shape (system-design)
<DocDir>/SystemDesign/Rung-<RungId>-<ShortRungDescription>.md   a rung's brief (this skill)
<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md            the rung's tasks (tasklist)
```

`ShortRungDescription` is 2–4 Snake_Case words from the rung title, the same in brief and tasklist. If a brief exists, read it and continue instead of overwriting. IDs (`A`, `D`, `R`, `Q`, `FR`, `NFR`) are per document, never reused or renumbered; a brief cites design-doc IDs qualified (`Overview:FR2`), its own rung-local ones bare.

State that lets a new session resume lives in files: the escalation marker the automatic fold-back writes on the rung, the milestone's `Close:` line (below), and the handoff note at each wait for the owner ([handoff.md](references/handoff.md)). Whenever a step below stops before the owner answers, it writes that note, says in a sentence or two what waits and the exact question, and ends with `Next: /rung (Opus: /model opus)`; the step that resumes reads the note and deletes it.

## Milestone planning

One Opus session, with the owner, at the start of a milestone. It plans every `planned` rung of the current milestone that has no tasklist; route `milestone-plan` means such a rung exists, and it takes precedence over `run`, `escalation` and `milestone-close`. After a mid-milestone re-plan or a rejected demo that is only the rungs added or reshaped: skip step 2, and limit step 3 to the seams, names and subsystems those rungs bring in.

### 1. Inspect

Read by section, not whole files (`roadmap show|section|outline`; the binary is `~/.cache/danny-agent-skills/bin/roadmap`; run risk-first-roadmap's "Plan tool check" first; without it, `grep -n '^#'` and read line ranges): the current milestone's line, exit criteria and rungs, the system design's sections those rungs touch, subsystem docs for pieces they work inside, and the code of the touched components. Do not ask for anything you can discover. Apply risk-first-roadmap's "Tidy an existing roadmap or Overview" triggers once and offer that pass first if one fires.

- **No system design?** Offer `system-design` first (a legacy `<DocDir>/Design-<Topic>.md` can stand in). Do not invent one inside a brief.
- **Older shape** (no Scope and milestones, no milestone fields or `Touches:`)? Run system-design's Migration first; it commits alone, and its `proposed` items join step 4's review.
- **An older `Kind: checkpoint` rung next?** Step 2 stands in for it; set it `done` with the look-back's learning-log line.
- **A rung with closed tasks but no fold-back** (in flight when the project moved to this flow)? Fold it back first with [auto-fold-back.md](references/auto-fold-back.md).
- **A one-line horizon item?** Write its question, slice, done-when, if-no and `Touches:` into the roadmap in risk-first-roadmap's rung format first.

### 2. Look back

Call system-design's Look-back (it reuses one already run for this milestone). It returns a list with recommended actions and applies nothing; keep it for step 4.

### 3. Draft the design delta

What this milestone adds to the system design, for the subsystems it touches: each seam the rungs cross (what crosses it: types, calls, events, formats; anything shared such as error codes and identifiers, reuse or reconcile; for a new entry point, what it does when input or configuration is absent; for a derived ratio, its null and zero cases and denominator), the threat and privacy pass for each new seam, data-model changes, and pieces that now meet a subsystem trigger (their docs written in system-design's subsystem mode, only as deep as this milestone needs; do not grow the parent with their internals). When a rung builds a surface the owner uses (CLI commands, API routes, screens) for the first time, list it (each command or route, its parameters, what it returns) and get the owner's confirmation before drafting the rest; a list in an agreed design doc is still a draft until confirmed. Review every new name together as one item against `<DocDir>/Taxonomy.md` (create it if absent: rules already decided, tables by area with Term | Meaning | In code | Avoid, open clashes), each with two or three candidates, the nearest existing name and any clash. A major decision (persistence, a public interface, migration) with real alternatives goes through `decision-driven-design`; a trivial one gets a `proposed` default.

Where you must guess about an external system's or framework's behaviour (including what a platform does with an event a `Done when` relies on), a property of real data (completeness, uniqueness, shape), the exact message, code or status a `Done when` expects the project's own code to return (read the route or function that produces it), or that the build and tests pass at the base (run them once now; a failure is the first task), and later tasks depend on it: check it now if a read-only look is cheap; otherwise the rung's guard rails put one real call or query first (over a sample when the rung ends in a run over many items), and each slice item resting on it is marked `conditional` with what drops if it is refuted.

### 4. Review and agree

Present, in the shape in [presenting-for-review.md](references/presenting-for-review.md), the look-back's list, the design delta, the names and any migration items together, with at most 3–5 questions whose answers would change a seam, a slice or the rung order. Structure comes first; outcome details (thresholds, output shape, polish) go on the roadmap's "decide after it runs" list, filed under the rung that settles them. If the owner does not answer in this session, write the handoff note (`Route: milestone-plan`, the questions and the draft delta's location) and stop. Iterate until the owner says it is good enough, then apply the rulings: docs fixed on the side that is wrong, each ruled item `settled` or `working` (`owner` where the owner wrote it), accepted refactor rungs placed ahead of the milestone's first feature rung, and the agreed delta written into the system design and subsystem docs. Commit the design changes as `Design for milestone <MilestoneId>: <name>`.

### 5. Write every rung's brief

Use the template. The next rung's brief is complete; the rest stay thin, citing the agreed seams and decisions by qualified ID instead of restating them. Each brief's verification names a regression test: one that fails without the rung's change. A rung with no open decisions and an obvious check gets no brief; its tasklist's `Source:` cites the design doc. Set depth tags `sketched → designed` for the components the briefs design, in each design doc they touch and only those; a parent changes only where a subsystem's Contract changes.

### 6. Write the tasklists

Use the `tasklist` skill for one `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md` per rung, `Source:` citing the rung and its brief: verification items become `Done when` checks (the regression test among them), guard rails become `Context` or `Non-goals`, decisions are cited in `Context`, and each "decide after it runs" item the rung settles goes into the `Done when` of the task that settles it, with "record the answer on the roadmap's list". Rungs stay `planned`; the run that starts a rung sets it `in progress` and writes `Base: <git rev-parse --short HEAD>` under its brief's `Status:` line (no brief: in the tasklist's `Source:` line), so fold-back can diff the rung's work. Because every tasklist lands in the one planning commit, `metrics signals --tasklist`'s fallback (the parent of the commit that added the tasklist) gives the milestone's base for every rung: right for close's milestone-wide signals, wrong for one rung.

Commit by explicit path (briefs, tasklists, design docs, `Taxonomy.md`, roadmap) as `Plan milestone <MilestoneId>: <name>`; if the owner said not to commit, say so. Run the tool's map command. End with a sentence naming the first rung with its title and that each rung now runs and folds back on its own, then `Next: /rung (<Model>: /model <alias>)` on the orchestrator model from `tasklist-run`'s "Orchestrator model". Log a `step` event with `skill` `plan-milestone 1.0.0`, `kind` `milestone-plan` (other fields in `tasklist-run`'s metrics log), plus the design delta's counts: `proposed`, `accepted` (unchanged), `edited` and `rejected`.

### Rung 1 and build boundaries

When the system design implies more than one build boundary that rung 1 must create (separate executables, a shared package, enforced layering), rung 1's brief adds a **Build targets** section (each target, its allowed imports, its build and test commands, drawn in the diagram) and its run waits for the owner to approve it. With a single app target, say so in one line.

## Escalation review

Reached when the automatic fold-back stopped on something it may not judge and left an escalation marker on the rung. Also reached, with no marker, for an `in progress` rung whose lists all moved to `Completed/`: the fold-back finished without setting it `[done]`; review its brief and fold-back commit, then finish the fold-back or set it `[done]`. Opus; not owner-facing until step 3, so `/rung` may run steps 1 and 2 as an Opus subagent started from the handoff note the fold-back wrote (`Route: escalation`).

1. **Read** the marker's differences, the brief, the rung's diff (`git diff <Base>..HEAD` for the surfaces involved), the system design and subsystem rows they touch, and the tasklist's outcomes.
2. **Judge each difference.** When the code is right and the design was a guess, fix the doc; when the code drifted for a bad reason, leave the docs and write a task in `<DocDir>/Tasklist-<RungId>-Drift.md`. An unanswered "decide after it runs" item is settled from the code or the task's output. Changing a `settled` item or a decision, retiring a risk on a partial answer, or calling the rung `failed` needs the owner: return those with a recommendation instead of applying them. Commit what was applied as `Review fold-back of rung <RungId>`.
3. **Owner items**, if any, in the shape of presenting-for-review.md; apply the rulings. Unanswered in this session: write the handoff note (`Route: escalation`, the items and what step 2 already committed) and stop.
4. **Finish the fold-back** for the escalated items as [auto-fold-back.md](references/auto-fold-back.md) step 4 does for clean ones, record each drift as a decision, clear the marker, set the brief to `folded back (<date>)` with an "As built" line per difference, set the rung `[done]` unless this review wrote a `-Drift` list, and commit by explicit path as `Fold back rung <RungId>`.
5. **Next.** Start a short retro in a background Sonnet subagent (an escalated rung is unusual; follow [retrospective.md](references/retrospective.md), absolute path, return only the report). A re-plan trigger (rung failed, answered a different question, a `settled` seam must change) runs risk-first-roadmap's Re-plan; rungs it adds have no tasklist, so `/rung` plans them first. Otherwise the next brief exists. Say what moved and why, show the retro, and end with `Next: /rung` plus the model the next step needs (a drift list or the next rung runs on the orchestrator model). Log a `step` event with `kind` `escalation`, `target`, `drift`, `next` and `next_model`.

## Milestone close

Reached when no rung of the current milestone is `planned` or `in progress` and no fix or follow-up list of it is open; a `Close:` line does not override that. Opus. The close records each finished step in a `Close:` sub-bullet under the milestone's line in the roadmap, which `roadmap next` reads; a new session resumes after the step it names. Step 8 removes the line once the ruling is in the learning log.

`Close: checks failed | checks passed | tidy run | tidy skipped | tidy deferred | re-read <sha> | awaiting demo | accepted | accepted with follow-ups (<date>)`

1. **Checks.** Run the full test suite when any fold-back ran only touched targets. A failure becomes `<DocDir>/Tasklist-<MilestoneId>-Fixes.md` with `Close: checks failed (<date>)`; commit and end with `Next: /rung (Sonnet: /model sonnet)`, and close reruns this step once the list is closed. A pass writes `Close: checks passed (<date>)`.
2. **Quality.** Run `metrics signals --base <the first rung's Base>` (see code-quality-pass's "Metrics tool check") and update `Quality/Status.md` if it exists. Offer one tidy of the milestone's files: run, skip or defer, written as `Close: tidy <answer> (<date>)`. On run, do the tidy's scout, list and rulings, commit, and end with `Next: /rung (Sonnet: /model sonnet)`; the tidy runs in its own session and close resumes at step 3.
3. **Re-read every fold-back together.** Non-interactive, so `/rung` may run it as an Opus subagent from a brief or handoff note naming the milestone, its rungs and their briefs. Read each brief's "As built" notes and fold-back commits, then the touched design docs as a whole against the code (every doc the milestone's data passed through, not only its touched components), and the "decide after it runs" items filed under this milestone or its rungs. Judge each drift the automatic fold-backs missed as step 2 of the escalation review does: apply doc fixes that change no `settled` item or decision, return the rest with a recommendation, and commit as `Re-read fold-backs of milestone <MilestoneId>` with `Close: re-read <sha> (<date>)`.
4. **Demo.** Present the re-read's owner items, apply the rulings and commit them before the demo, then walk the owner through each exit criterion: how to see it (a command, a screen, a file) and what you observed. Ask for one ruling: accept, accept with follow-ups, or reject. If the owner does not answer in this session, write `Close: awaiting demo (<date>)`, commit, write the handoff note (`Route: milestone-close`, the re-read's findings and how to see each exit criterion), and end with a sentence saying the close waits for their demo ruling, then `Next: /rung (Opus: /model opus)`.
5. **Apply the ruling** to the `Close:` line. Follow-ups each become a task in `<DocDir>/Tasklist-<MilestoneId>-Follow_ups.md`, a rung of a later milestone, or a "decide after it runs" item, as the owner picks. On reject, record which exit criteria failed in the learning log, remove the `Close:` line, keep the milestone `current`, and run risk-first-roadmap's Re-plan to add the rungs that close the gap (they have no tasklist, so `/rung` plans them, and close starts over once they are done); commit and end there with `Next: /rung (Opus: /model opus)`, which plans them.
6. **Retro.** One milestone retro in a background Sonnet subagent following [retrospective.md](references/retrospective.md) (absolute path; return only the report, apply nothing).
7. **Owner preferences.** Propose additions in one line each, by terms.md's two-overrides rule; the owner accepts or declines, and accepted ones are written where terms.md says.
8. **Re-plan the next milestone** with risk-first-roadmap's Re-plan ("At milestone close"), with the accepted quality proposals; without its `Next:` line or `step` event. Record the ruling in the learning log and remove the `Close:` line. Commit by explicit path as `Close milestone <MilestoneId>: <name>`, and run the map command.
9. **End.** Print the retro report after the re-plan summary, then the one line `retro feedback saved (<n> pending)` (the block is saved to the inbox, not printed), a sentence saying the next milestone (with its name) is planned next, then `Next: /rung (Opus: /model opus)`. Log one `step` event with `kind` `milestone-close`, `target` (the MilestoneId), `ruling`, `next` and `next_model`.

## Retrospective

`retro [M2]` writes the milestone retro, `retro [L3]` a short one for a failed, re-planned or escalated rung; both run inside the steps above. Follow [retrospective.md](references/retrospective.md): build it from the briefs, design docs, tasklists, git history and `metrics summary`, not from memory; apply nothing. Read how many `proposed` items the owner accepted unchanged from the `accepted` and `proposed` counts in the `step` events.

## If a linked file or skill is missing

This skill links to the `system-design` skill's references and hands off to `tasklist` and `decision-driven-design` (`task-workflow` plugin). When one is absent, do not stop: use the minimum below, and say once, in one or two lines, what is missing, how to install it, and how to recover.

- Install: `claude plugin install project-planning@danny-sung-agent-skills` or `claude plugin install task-workflow@danny-sung-agent-skills`; with the open installer, `npx skills add dannys42/agent-skills --skill <skill-name>` into the same skills directory, so relative links resolve.
- Recover: re-run the skipped step once it is installed. Existing docs are read and continued, never overwritten.
- No `system-design` (and no system design): offer a minimal Overview with Summary, Scope and milestones, Requirements, Components (diagram and a table with depth and `Doc`), Seams and interfaces, Decisions, Risks (ranked, cheapest experiment), Traceability. Recover by running `/system-design` on it. Without its Look-back, compare the docs with the code yourself and list each drift with the side that looks wrong. Without `subsystems.md` or `terms.md`: edit only touched docs; a parent sees a subsystem as one box and changes only with its Contract; IDs per doc, qualified across docs.
- No `diagrams.md`: Mermaid `flowchart`, quote every label, labels are component names, one class per depth (`sketched` dashed, `designed` thin, `built` bold) plus `touched`.
- No `tasklist`: write each rung's tasks as a plain checklist at `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`, each with an ID, `Needs` and `Done when`, and say the tasklist skill gives the richer format.
- No `decision-driven-design`: ask the decision questions inline, one at a time, recommended option first.
- No `presenting-for-review.md`: group items as important, notable and small, important first; give every item two or three options with a plain example and a pro and con, and a recommendation; end with one question asking for the important rulings and only the other items the owner would change.

## Judgment calls

- **Untouched means undesigned.** A component that only appears as a neighbour keeps its depth tag and gets no new detail; a subsystem no rung works inside stays one box.
- **Interfaces before internals.** At a touched seam, decide what crosses it. Internals stay with the implementer unless they decide a risk.
- **Briefs are short.** A full brief is about a page, per-component tables included (one line per component); a thin one cites the agreed seams and lists only what its tasks will cite. A brief past two pages is probably two rungs: say so and suggest splitting it in the roadmap.
- **Do not re-order the ladder while drafting.** If planning shows a rung in the wrong place or answering two unknowns, raise it in step 4; the roadmap changes through risk-first-roadmap.
