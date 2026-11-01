# Review notes: the planning terms

Reviewed file: `plugins/project-planning/skills/system-design/references/terms.md` (the shared vocabulary every project-planning skill will use without redefining). Spec: `docs/project-planning/Design-Blueprint_And_Milestones.md`.

Each term is one decision: what it means and how widely it reaches. Where the spec already ruled on a concept, that ruling is not reopened; the options below are only about how the term is worded or scoped, and each item says where the spec settled it. Section names below are the headings in `terms.md`.

## Important

Six more qualify (milestone planning, re-plan triggers, the additive check, the end-of-goal rule and spikes, milestone close, owner preferences); they open the notable tier.

**1. The blueprint keeps the Overview's file** (terms.md, "The blueprint": **Blueprint**; "Terms that change or retire": **Overview**). Skill text calls the design doc the blueprint, but the file stays at `<DocDir>/SystemDesign/Overview.md` and is scoped to the current milestone instead of "about a page". On FileOrganizerHero, the first milestone planning converts the existing `Overview.md` into the blueprint for its next milestone, keeping the file.
Why: hard to reverse (a file path existing projects hold) and wide reach (every skill reads it).
Spec: the scope (current milestone, later milestones one line each) is settled; the file name is not stated there.
- **Keep `Overview.md`, call it the blueprint in text** (recommended). Pro: no migration of the file, links keep working. Con: the name on disk and the name in text differ.
- **Rename the file to `Blueprint.md`** in the first milestone planning's move-mostly commit. Pro: one name everywhere. Con: every skill, tool and old link must handle both names during migration.

**2. Kept spike code is marked and tabled** (terms.md, "Milestones": **Provisional code**). Kept spike code carries `PROVISIONAL(<RungId>): replace at <MilestoneId> (<milestone name>)` in the code and a row in the blueprint's Provisional code table; `metrics signals` counts the markers. E.g. `// PROVISIONAL(L6): replace at M4 (grade changes)`.
Why: hard to reverse (a text format a tool parses and code in every project will carry).
No real alternative: the spec settled the marker form, the table's columns and the seam rule, and terms.md matches them. **As written** (recommended).

**3. Agreement states and origin marks** (terms.md, "Agreement states and marks": **`settled`**, **`working`**, **`owner` and `proposed`**). Every agreed item carries a state (`settled`, or `working` with a revisit note) and an origin (`owner` or `proposed`). E.g. "one SQLite file per project (`working`; revisit if two apps need to share data)".
Why: hard to reverse (literal marks stored in every blueprint) and wide reach (fold-back's classification and every first pass read them).
Spec: both pairs and their meanings are settled; that a first pass marks everything `proposed` is also in the spec.
- **Two independent marks, as written** (recommended). Pro: a `proposed` item can still be proposed as `settled` or `working`. Con: two marks per item.
- **Fold origin into state** (`proposed` as a third state that becomes `settled` or `working` on acceptance). Pro: one mark per item. Con: loses who wrote an accepted item, which the owner-preference metric (accepted-unchanged share) needs.

**4. Only three surfaces get field-by-field review** (terms.md, "The blueprint": **Reviewable surfaces**). The owner reviews database schema, REST and wire APIs, and a library's public symbols field by field; everything else is the agent's inside the agreed seams. E.g. the owner reviews the `sales` table's columns; the agent picks the parsing algorithm.
Why: owner workload (what the owner reviews at every step) and wide reach (what fold-back escalates).
Spec: the three surfaces are settled. The spec uses both names: "Field-level review, only for" (blueprint section) and "Compare the reviewable surfaces" (automatic fold-back, step 2). The choice is which one terms.md makes the term.
- **"Reviewable surfaces"** (recommended). Pro: names the things, so fold-back can say "a reviewable surface differs". Con: the blueprint section of the spec says "field-level review", so the two read slightly differently.
- **"Field-level review"**. Pro: matches the spec's blueprint section. Con: names the activity, so "a field-level review differs" reads badly in the fold-back rules.

**5. Closing a rung becomes automatic, with an escalation path** (terms.md, "Cadence": **Automatic fold-back**, **Escalation**; "Terms that change or retire": **Rung close**, **Fold-back**). After `tasklist-run` commits a rung's last task, the same Sonnet session runs the checks, compares the reviewable surfaces, classifies differences and commits `Fold back rung <RungId>`; anything it may not judge stops and routes `/rung` to "a close session on Opus". E.g. "L9 (daily import) renamed the `units` column → escalated to close (Opus)."
Why: workload and cost (the model per step and the number of Opus sessions) and a concept change (three things are now called "close").
Spec: the steps, the classification table and the never-does list are settled. The open point is what to call the escalation session.
- **As written, "a close session on Opus"**. Pro: no new term; `/rung close` keeps its command. Con: "close" now means the escalation session, milestone close and the retired per-rung close.
- **Name it "escalated close"** in Escalation and Rung close (recommended). Pro: the three closes are distinct in skill text and `Next:` lines. Con: one more term to define.

## Notable

**6. Milestone planning replaces the checkpoint rung and per-rung planning** (terms.md, "Cadence": **Milestone planning**; "Terms that change or retire": **Checkpoint rung**, **Per-rung plan session**, **Depth tags**). One Opus session at a milestone's start looks back at the code, writes the blueprint delta (with the threat and privacy pass), every rung's brief, names as a set and the tasklists; `designed` is now set then, `built` still at fold-back. E.g. "M2 (see it) planning wrote the briefs and tasklists for its four rungs in one session."
Why it would be important: changes sessions and cost.
No real alternative: the spec's "Cadence" table and migration settle it, and terms.md matches. **As written** (recommended).

**7. Re-planning only on a trigger** (terms.md, "Cadence": **Re-plan triggers**; "Terms that change or retire": **Re-plan after every rung**). Inside a milestone, re-plan only when a rung fails, answers a different question than it asked, an owner request lands in the current milestone, or a `settled` seam must change.
No real alternative: the spec's "Cadence" table settles the four triggers; only the name "re-plan triggers" is new, and it is plain. **As written** (recommended).

**8. The additive check stops blueprint depth** (terms.md, "The blueprint": **Additive check**). For each later milestone's line, ask whether it can be added as new entities, endpoints or symbols without restructuring; if not, decide that seam now at the smallest depth. E.g. `Change` gets a timestamp now so grading can link to metric windows later.
Spec: settled, nearly word for word.
- **"New entities, endpoints or symbols", as written** (recommended). Pro: concrete, checkable against the reviewable surfaces. Con: may miss additions that are a new subsystem.
- **Add "or subsystems"**. Pro: covers a milestone that adds a whole component. Con: a new subsystem can hide a restructure the check should catch.

**9. Milestones, foundation first, and spikes before the goal** (terms.md, "Milestones": **Milestone**, **Foundation-first order**, **End-of-goal rule**, **Spike**). Milestones are capability layers with an owner-language outcome, subsystems, demo exit criteria and rungs, ordered so data and the core model come before the goal; until then the goal's own work runs only as a spike that builds none of its machinery. E.g. "can we detect a 10–30% effect at this traffic?" may run; the experiment loop may not.
Spec: all four are settled, including the name "end-of-goal rule".
- **As written** (recommended). Pro: matches the spec and the foundation-before-goal eval. Con: "end-of-goal rule" does not say what it forbids.
- **Rename to "goal-waits rule"**. Pro: says what it does. Con: departs from the spec's own name and the eval's wording.
- Also: **Spike** is defined as "a rung", while `design-session` offers a "throwaway spike" that is not one. Recommend keeping "a rung" and letting `design-session` say "throwaway run" if they must differ.

**10. One retro per milestone at milestone close** (terms.md, "Cadence": **Milestone close**; "Terms that change or retire": **Per-rung retro**). One Opus session at a milestone's end: the full suite if needed, a re-read of every fold-back together, an owner demo ruled accept, accept with follow-ups or reject, one retro, proposed owner preferences, and the re-plan of the next milestone. An unusual rung (failed, re-planned or drifted) still gets a short retro.
Spec: settled.
- **As written** (recommended). Pro: matches the spec. Con: one session carries a lot.
- **Split the demo into its own short session**. Pro: the owner's part is separate from the agent's re-read. Con: one more session per milestone, against the spec's cadence.

**11. Owner preferences and the two-overrides rule** (terms.md, "Owner preferences": **Owner preference**, **Where**, **What is not one**, **Two-overrides rule**). A taste the agent applies to every first pass, one line each with an example and date; cross-project ones in `~/.local/state/danny-agent-skills/owner-preferences.md`, project ones in the rules file; a single ruling or skill feedback is not one; a preference enters after two overrides of the same kind or an outright statement.
Spec: settled; the name "two-overrides rule" is new.
- **Name it "two-overrides rule"** (recommended). Pro: says the threshold. Con: does not mention "or stated outright".
- **No name; keep the rule as a sentence under Owner preference**. Pro: one fewer term. Con: harder to cite from milestone close and `design-session`.

**12. Naming rules for the owner** (terms.md, "Names and labels": **An ID shown to the owner carries its name**, **Names say what the thing does**, **Names are reviewed as a set**). Every ID shown to the owner gets its short name on first use in a message; names use the owner's words with no general words, unlisted metaphors or role names; names are reviewed as a set at the blueprint and milestone planning. E.g. "L4 (architecture check before folder suggestions)".
Why notable: wide reach (every message), but the spec settled all three.
- **As written** (recommended). Pro: matches the spec. Con: the first-mention rule adds words to short `Next:` lines.
- **Exempt `Next:` lines when the name appeared earlier in the session**. Pro: shorter lines. Con: the owner often reads `Next:` alone after a break.

## Small

**13. `Map.md` and `Touches:`** ("Milestones"). `Map.md` is a zero-token one-page view of milestones and their rungs (name, status, `Touches`); `Touches:` names the subsystems a rung changes. No real alternative: the spec settled both. **As written** (recommended).

**14. Rung** ("Rungs and detail"). One increment inside the current milestone, ordered riskiest unknown first among that milestone's rungs, with an owner pin. **As written** (recommended). Pro: short. Con: does not name the risk kinds (shape, clock, breadth) the spec lists. **Add the three risk kinds.** Pro: one place for them. Con: `risk-first-roadmap` already defines them.

**15. Detail by distance** ("Rungs and detail"). Full brief for the current rung, short briefs for the rest of the milestone, one line plus the additive-check line for the next milestone, a name and one line beyond. Spec settled, same table. **As written** (recommended); no real alternative.

**16. "Decide after it runs" list** ("Rungs and detail"; "Terms that change or retire": **The brief's `Deferred:` line**). A project-level list of minutiae, each filed under the milestone or rung that settles it, checked at fold-back; it replaces the brief's `Deferred:` line. **"Decide after it runs"** (recommended, the spec's name). Pro: says when. Con: long to quote. **"Deferred list".** Pro: short, familiar. Con: the old per-brief meaning lingers.

Shall the escalation session be called "escalated close" (item 5), with every other item going ahead as recommended unless you name it?
