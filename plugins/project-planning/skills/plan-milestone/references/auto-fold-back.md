# Automatic fold-back

The mechanical and comparison part of closing a rung (terms.md, "Automatic fold-back"). `tasklist-run` follows this once, in the same session, right after it commits the last task of a rung's list (`Tasklist-<RungId>-<ShortRungDescription>.md` or its `-Drift` list; not a `-Tidy` list or a milestone's `-Fixes` or `-Follow_ups` list). The list stays in `<DocDir>/` until step 4's commit moves it to `Completed/`, so a closed rung list still in `<DocDir>/` means the fold-back did not finish, and the next run re-enters it here. That session already holds the tasklist and the run's outcomes; read the rest by section, not whole files.

Inputs: the brief (`<DocDir>/SystemDesign/Rung-<RungId>-*.md`; none for a rung without open decisions, whose tasklist `Source:` cites the design doc instead), its `Base:` line (no brief: the tasklist's `Source:` line), the brief's `## Fold-back` list, the rung's section and the "decide after it runs" items filed under it in the roadmap, and the design-doc rows the brief cites.

## 1. Checks

Run the project's full test suite. When the suite is slow, run only the test targets the rung touched; the full suite then runs at milestone close. Slow means over the project rules' value if they set one, else over about 5 minutes on the last full run. Confirm the rung added a regression test (the one its brief's verification names, failing without the rung's change). A failing check or a missing regression test stops here: record it as the only difference in the escalation marker, skip steps 2 and 3, and in step 4 apply nothing but the commit.

## 2. Compare

Take the rung's diff, `git diff <Base>..HEAD`. Compare its reviewable surfaces (database schema, REST and wire APIs, public symbols) against the brief and the system design rows it cites; use a tool that extracts them at zero tokens when the project has one. Also check each `Done when` result from the tasklist, each "decide after it runs" item the rung was to settle, and the diff for new `PROVISIONAL(` markers.

## 3. Classify each difference

| Difference | Action |
| --- | --- |
| As agreed | Tick its `## Fold-back` item |
| Internal only (private types, algorithms, file layout) | One "As built" line in the brief; no question |
| A `working` item reworked as its revisit note foresaw | One "As built" line in the brief |
| A reviewable surface or `settled` item differs | Escalate |
| A "decide after it runs" item has no answer | Escalate |
| A `Done when` did not pass | Escalate |
| A new `PROVISIONAL` marker not in the system design's Provisional code table | Escalate |
| A re-plan trigger fired (the rung failed, answered a different question, or a `settled` seam must change) | Escalate |

Anything that fits no row escalates.

**Escalate** means: apply nothing for that difference, and write the escalation marker into the rung's section of the roadmap (`<DocDir>/Roadmap-<Topic>.md`, under `### <RungId>: ...`, after its last field), one bullet per difference:

```markdown
Escalation: <YYYY-MM-DD>
- <what differs>: agreed <what the brief or design says, with its qualified ID>; built <what the code does, file or symbol>
```

The rung stays `[in progress]`; `roadmap next` routes `escalation` while the `Escalation:` line exists, and the escalation review removes it. The clean differences are still applied in step 4.

## 4. Update the docs for the clean cases

Only what a clean difference or a passed `Done when` settles, in the docs the brief lists as touched:

- depth tags `designed → built` for the components the rung built;
- traceability rows for the requirements it proved;
- risks its passed `Done when` answers in full (never on a partial answer);
- the answer recorded on each "decide after it runs" item it settled;
- names the owner already agreed, into `Taxonomy.md`;
- the brief's `## Fold-back` items ticked and its "As built" lines.

With no escalation, also set the brief to `folded back (<date>)` and the rung `[done]` in the roadmap. Move the list to `<DocDir>/Completed/` and commit it with these changes by explicit path as `Fold back rung <RungId>`; with an escalation, the marker goes in the same commit and the message is `Fold back rung <RungId> (escalated)`, so the plain message always means a finished fold-back. Under `--no-commit` or `--confirm-commit`, follow the override.

## A `-Drift` list

The escalation review already folded the rung back and cleared the marker. Skip step 2's diff from `Base`: compare only each drift task's `Done when` result against the design row it cites, classify as in step 3, and re-apply no "As built" lines. If all are clean, set the rung `[done]` and commit as in step 4.

## What it never does

Decide which side of a drift is wrong, change a decision or a `settled` item, add or reorder rungs, call a rung `failed`, or retire a risk on a partial answer. Each of those escalates.

## 5. Report and continue

- **Clean:** one summary line to the owner (what was folded back, "As built" count), then `Next: /rung` with the model the next step needs: the next rung's run on `tasklist-run`'s orchestrator model, or, after the milestone's last rung, milestone close (`Next: /rung (Opus: /model opus)`). The next brief exists from milestone planning, so nothing is re-planned. No per-rung retro.
- **Escalated:** a few sentences saying what differs from the agreed design and why that needs an Opus review (judging which side is wrong), then `Next: /rung (Opus: /model opus)`. Write the review's handoff note first ([handoff.md](handoff.md), `Route: escalation`), naming the rung, its brief, its tasklist, its `Base` and the marker. The escalation review starts the per-rung retro.

This is the step's only `step` event: `tasklist-run` writes its `end` line without one. Log it as `tasklist-run`'s metrics log describes, with `skill` `plan-milestone 1.0.0`, `kind` `fold-back`, `target` (the RungId), `drift` (differences found beyond "as agreed"), `escalated` (true or false), `next` and `next_model`.

**Safety net:** milestone close re-reads every fold-back of the milestone together on Opus, so a drift missed here is caught there at the latest.
