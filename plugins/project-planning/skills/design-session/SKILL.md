---
name: design-session
description: Work a design out together with the owner when they say "let's work through the design", "design session", "explore options for...", "I want to think through..." or "let's work it out together". The owner leads; the agent offers 2-3 alternative shapes with diagrams, traces consequences (including the additive check against later milestones), catches contradictions and offers a throwaway spike when only running something will settle a question. Notes go to a scratch file, not the system design. Ends with a promote step: the owner picks what enters the system design as settled or working, what is parked for a later milestone and what is dropped; the edit is committed and the notes file deleted. Use any time: before a system design exists, during milestone planning or mid-milestone. Not for drafting a whole system design (use system-design) or planning a rung (use roadmap-plan-next-rung).
license: GPL-3.0-or-later
model: opus
---

# Design Session

Think a design through with the owner before anything is recorded. The owner leads; the agent widens the options, shows what each one implies and keeps the conversation honest. Nothing reaches the system design until the promote step at the end, where the owner picks what goes in.

Use it at any point: before the system design exists, during milestone planning, or in the middle of a milestone. Terms (system design, additive check, reviewable surfaces, `settled`/`working`, `owner`/`proposed`, milestone, spike, provisional code, owner preference, two-overrides rule) are defined in the `system-design` skill's [terms.md](../system-design/references/terms.md); use them as defined there.

## Files

```
<DocDir>/SystemDesign/
  Overview.md                       the system design (system-design); changed only by the promote step
  Sessions/<date>-<Short_Topic>.md  this skill's scratch notes, deleted after the promote step
```

`<date>` is `YYYY-MM-DD`; `Short_Topic` is 2–3 words in Snake_Case, e.g. `2026-11-01-Review_Import.md`. The notes are free-form: no IDs, no statuses, no agreement marks and no question cap. They hold the owner's sketch, the shapes considered with their diagrams, consequences traced, contradictions found and how they were resolved, spike results, and where the owner is leaning. Update them whenever the conversation moves, so a session that stops early can resume from the file.

## Workflow

### 1. Read, then let the owner lead

Read the system design and any subsystem doc the topic touches, the roadmap's current milestone, `<DocDir>/Taxonomy.md`, the project rules file (`CLAUDE.md` or equivalent) and the owner preferences file `~/.local/state/danny-agent-skills/owner-preferences.md` if it exists. If a notes file for this topic exists in `Sessions/`, continue from it. Otherwise create it and state the path.

Ask the owner what they are picturing, and reflect their sketch back in a few lines and, when it has two or more parts, a diagram. Ask only what would change the shape; never ask what you could state as a default.

### 2. Offer alternative shapes

Offer 2–3 shapes, the owner's own sketch counting as one. For each: a Mermaid diagram following the `roadmap-plan-next-rung` skill's [diagrams.md](../roadmap-plan-next-rung/references/diagrams.md) (node labels are the system design's component names exactly, new pieces `sketched`, what the shape changes marked `touched`), a plain example of how it behaves on a case from the project, and a one-line pro and con. Then recommend one, or say "no recommendation" and why. Name new things by what they do (terms.md, "Names and labels"). Render-check each diagram as diagrams.md says.

### 3. Trace consequences

For the shape the owner is leaning toward, say what it changes: subsystems, seams, the data model, reviewable surfaces (field by field only there), names and the threat and privacy section. Run the additive check against each later milestone's line: if a later milestone could not be added without restructuring, say which seam would have to be decided now. With no system design or no later-milestone lines yet, skip the additive check until milestones exist; never invent milestones to check against. Name every `settled` item the shape would change; changing one is a re-plan trigger. Leave internals inside the seams undecided; minutiae go on the "decide after it runs" list.

### 4. Catch contradictions

Say so plainly when something the owner says conflicts with an earlier statement in this session, a `settled` item, an owner preference, the project rules or a name in `Taxonomy.md`. Quote both sides and ask which holds. Record the answer in the notes.

### 5. Offer a throwaway spike

When only running something will settle a question (is it fast enough, does the API return this, can the platform do that), offer the smallest run that answers it: what it does, what result points which way, and roughly how long it takes. Build it only if the owner accepts, outside the product code (a scratch directory or a throwaway branch), run it, and record the result in the notes. The code is thrown away; if the owner wants to keep it, it is promoted as provisional code in step 6.

### 6. Promote

When the owner says they are done, or the conversation has converged, list every item in the notes that could enter the system design, in the shape in [presenting-for-review.md](../roadmap-plan-next-rung/references/presenting-for-review.md), each with a recommended outcome:

- **Promote as `settled`** or **promote as `working`** with its revisit note ("revisit if …").
- **Park** for a later milestone, naming the milestone.
- **Drop.**

In the same message, propose owner-preference lines per the two-overrides rule: only where the owner overrode the same kind of shape you offered twice in this session, or stated a taste outright. One line each (the preference, one example, the date), saying whether it goes in the cross-project owner preferences file or the project rules file. A single ruling is a decision, not a preference; feedback on how this skill behaves goes to the retro, not here. For each item in the owner's wording (a name, outcome text, a seam), make the `system-design` skill's step-4 tightening offer once in the same message: list each ambiguity and show a tightened version beside the original; the owner accepts, edits or keeps it. End with one question.

Apply the owner's rulings to the system design ([overview-template.md](../system-design/references/overview-template.md)) as a normal edit:

| Promoted item | Where it goes |
| --- | --- |
| A component | a Components row (`sketched`, Build target, Agreement) and a diagram node with its depth class only, never `touched` |
| A seam | a Seams and interfaces row with its Agreement |
| A table, API or public symbol | Reviewable surfaces, field by field, with its mark |
| An entity or relationship | Data model |
| A name | Names, then `<DocDir>/Taxonomy.md`, reviewed with the rest as a set |
| A choice between shapes | a Decisions row: next free `D` ID, Kind `choice`, Agreement `settled` or `working (revisit if …)`, Why naming the rejected shape |
| An unknown the session found | a Risks row with its cheapest experiment |
| A change to a later milestone | its Scope and milestones line and Additive check cell |
| Spike code the owner keeps | a Provisional code row, and the `PROVISIONAL` marker in the code |
| A parked structural item | an Open questions line naming the milestone it waits for, e.g. "Q4 (parked until M3, record changes): …" |
| A parked minutia | the "decide after it runs" list, under the milestone that will settle it |

Agreement marks follow the template: an item the owner wrote or edited reads `owner` (e.g. `settled · owner`); an item the owner accepted unchanged carries no `proposed` mark. New IDs continue the document's sequence and are never reused. A change to an agreed item goes through the decision log, not a silent edit. When a promoted item changes a `settled` item (a seam, say) or an owner request adds structure to the current milestone, say plainly that a re-plan is due. Dropped items are not recorded; the notes file in git history keeps them. Write accepted preference lines to the file the owner chose.

If no system design exists yet, write the promoted items into a new `Overview.md` with the template's header (`Status: draft`) and only the sections they fill; `system-design` continues from it.

Commit, staging by explicit path, the system design, `Taxonomy.md`, the project rules file if it changed, and the notes file, as `Design session: <topic>`, so history keeps the notes. Then `git rm` the notes file and commit that as `Remove design session notes: <topic>`. Log a `step` event with `skill` `design-session 0.11.2` and `kind` `design-session` (other fields in `tasklist-run`'s metrics log).

End with a plain sentence saying what changed and what the next step is, then `Next: /rung`, adding `(Opus: /model opus)` when that step needs Opus: a system design still to agree, milestone planning, or a re-plan that step 6 said is due.

If the owner stops before promoting, leave the notes file in place, uncommitted, and say its path; the next design session on the topic continues from it.

## If a linked file or skill is missing

When a linked file is absent, do not stop: use the minimum here, and say once, in one or two lines, what is missing and how to install it (`claude plugin install project-planning@danny-sung-agent-skills`, or `npx skills add dannys42/agent-skills --skill <skill-name>` into the same skills directory so relative links resolve).

- No `terms.md`: `settled` is expected to hold; `working` is good enough to start and names what would make us revisit it; `owner` items are the owner's words, `proposed` the agent's. The additive check asks whether each later milestone can be added without restructuring.
- No `diagrams.md`: Mermaid `flowchart`, quote every label, labels are the component names, one class per depth (`sketched` dashed, `designed` thin, `built` bold).
- No `presenting-for-review.md`: important items first (at most 5, hard to reverse or wide reach), each with options, a plain example, a pro and con and a recommendation; end with one question.
- No `overview-template.md`: promote into the system design's existing sections, matching their tables and marks.

## Judgment calls

- **The owner leads.** Offer shapes and consequences; do not interrogate or steer toward your favourite. A question that would not change the shape is not worth asking.
- **Explore freely, promote narrowly.** Anything may be discussed in the session, but only structure enters the system design: subsystems, seams, data model, reviewable surfaces, names, decisions and risks. Internals stay out.
- **A spike beats an argument.** When the owner and agent disagree on a fact that a short run would settle, offer the run instead of debating.
