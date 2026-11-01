# Review notes: the planning terms

Reviewed file: `plugins/project-planning/skills/system-design/references/terms.md` (the shared vocabulary every project-planning skill will use without redefining). Spec: `docs/project-planning/Design-Blueprint_And_Milestones.md`.

Each term is one decision: what it means and how widely it reaches. Where the spec already ruled on a concept, that ruling is not reopened; the options below are only about how the term is worded or scoped, and each item says where the spec settled it. Section names below are the headings in `terms.md`. Item numbers are unchanged from the first draft; item 17 is new.

## Decided (owner, 2026-11-01)

- **Rename: no "blueprint".** The design doc is "the system design"; its file stays `<DocDir>/SystemDesign/Overview.md` and the skill stays `system-design`. "Blueprint delta" is now "design delta". Applied in terms.md, the spec and the tasklist (the spec's file name stays as it is). See item 1.
- **Additive check: as written** (item 8). A line in the feedback ledger's "Collect next run" watches for an addition that passes the check but forces rework later.
- **Foundation and pillars** (new item 17). The foundation grows pillar by pillar, only as deep as the next pillar needs.
- **Manual stand-ins** (new item 18). A named term beside provisional code: a manual or fake step standing in for a later pillar's capability. Provisional code is preferred; each stand-in is listed in the system design next to the Provisional code table and replaced on purpose.
- **End-of-goal rule, option 1** (item 9). The goal's own machinery waits until its foundation milestones are done, except a thin end-to-end slice (the first pillar) using stand-ins or provisional code; "thin" means no machinery a later pillar must rebuild. The spike wording stays for "is it feasible?".
- **Milestone close pauses and resumes** (item 10). It stops at the owner demo; after the owner rules, the same close resumes, possibly in a new session. Splitting the demo into its own session was rejected.
- **One command, `/rung`** (item 5; terms.md: **Next step**). Every `Next:` line is `/rung` plus the model switch when needed; the escalation session has no owner-facing name (internally the route is `escalation`); state lives in files so a new session can resume; `/rung` states the model first and stops on the wrong one.

## Important

Seven more qualify (kept spike code, milestone planning, re-plan triggers, the additive check, the end-of-goal rule and spikes, milestone close, owner preferences); they open the notable tier.

**1. The file name `Overview.md` stays; the term is "system design"** (terms.md, "The system design": **System design**; "Terms that change or retire": **Overview**). The owner ruled the term: skill text calls the design doc "the system design", never "blueprint". Decided. The file stays at `<DocDir>/SystemDesign/Overview.md` and is scoped to the current milestone instead of "about a page". On FileOrganizerHero, the first milestone planning converts the existing `Overview.md` into the system design for its next milestone, keeping the file.
Why: hard to reverse (a file path existing projects hold) and wide reach (every skill reads it).
Spec: the scope (current milestone, later milestones one line each) is settled; the file name is not stated there.
- **Keep the file name `Overview.md`, call the doc "the system design" in text** (recommended). Pro: no migration of the file, links keep working. Con: the name on disk and the name in text differ.
- **Rename the file to `SystemDesign.md`** in the first milestone planning's move-mostly commit. Pro: one name everywhere. Con: every skill, tool and old link must handle both names during migration.

**3. Agreement states and origin marks** (terms.md, "Agreement states and marks": **`settled`**, **`working`**, **`owner` and `proposed`**). Every agreed item carries a state (`settled`, or `working` with a revisit note) and an origin (`owner` or `proposed`). E.g. "one SQLite file per project (`working`; revisit if two apps need to share data)".
Why: hard to reverse (literal marks stored in every system design) and wide reach (fold-back's classification and every first pass read them).
Spec: both pairs and their meanings are settled; that a first pass marks everything `proposed` is also in the spec.
- **Two independent marks, as written** (recommended). Pro: a `proposed` item can still be proposed as `settled` or `working`. Con: two marks per item.
- **Fold origin into state** (`proposed` as a third state that becomes `settled` or `working` on acceptance). Pro: one mark per item. Con: loses who wrote an accepted item, which the owner-preference metric (accepted-unchanged share) needs.

**4. Only three surfaces get field-by-field review** (terms.md, "The system design": **Reviewable surfaces**). The owner reviews database schema, REST and wire APIs, and a library's public symbols field by field; everything else is the agent's inside the agreed seams. E.g. the owner reviews the `sales` table's columns; the agent picks the parsing algorithm.
Why: owner workload (what the owner reviews at every step) and wide reach (what fold-back escalates).
Spec: the three surfaces are settled. The spec uses both names: "Field-level review, only for" (system design section) and "Compare the reviewable surfaces" (automatic fold-back, step 2). The choice is which one terms.md makes the term.
- **"Reviewable surfaces"** (recommended). Pro: names the things, so fold-back can say "a reviewable surface differs". Con: the system design section of the spec says "field-level review", so the two read slightly differently.
- **"Field-level review"**. Pro: matches the spec's system design section. Con: names the activity, so "a field-level review differs" reads badly in the fold-back rules.

**5. Closing a rung becomes automatic, with an escalation path** (terms.md, "Cadence": **Automatic fold-back**, **Escalation**; "Terms that change or retire": **Rung close**, **Fold-back**). After `tasklist-run` commits a rung's last task, the same Sonnet session runs the checks, compares the reviewable surfaces, classifies differences and commits `Fold back rung <RungId>`; anything it may not judge stops, records an escalation marker on the rung, and the next `/rung` runs an Opus review. E.g. "L9 (daily import) renamed a settled column; the next step is an Opus review of that. Next: /rung (Opus: /model opus)." Decided.
Why: workload and cost (the model per step and the number of Opus sessions) and a concept change (three things were called "close").
Spec: the steps, the classification table and the never-does list are settled; the owner's ruling below resolves the naming.
- **One `/rung` command, escalation has no owner-facing name** (decided, owner 2026-11-01). Pro: the owner never chooses between kinds of close; the agent tracks the next step in files and `roadmap next` returns route, reason and model. Con: durable state (escalation marker, handoff note, paused milestone close) must be reliable.
- **Named close commands** such as "escalated close" and `/rung close` (rejected). Pro: each session is explicit. Con: the owner must manage several kinds of close.

**17. Foundation grows pillar by pillar** (terms.md, "Milestones": **Foundation-first order**). New. The foundation is the shared base the pillars stand on (the data store, the core model). A pillar is a group of milestones (sometimes one) that together deliver one end-to-end capability toward the goal. The first pillar is the thinnest end-to-end slice that proves the goal's most fundamental capability, at minimal depth across several subsystems, with manual stand-ins for what is not built yet. Later pillars deepen an existing pillar or add a new direction; at a pillar boundary the agent proposes the next-pillar options with their dependencies and costs, and the owner picks. The foundation is built only as deep as the next pillar needs, under the same depth limit as the system design; once a pillar is good enough, the foundation may be extended for the next pillar, as new work in a later milestone, not before. E.g. a key-value store as a service: sign-in by hand-added API key, the data store and REST `get` (sets done by hand) are one pillar of three milestones; a fuller REST API is the second.
Why: a concept change (it sets how deep each milestone's foundation work goes) and wide reach (milestone planning, the additive check and the over-detail trap all read it).
Spec: "foundation first" is settled; the depth rule is the owner's ruling of 2026-11-01, recorded in the spec's "Foundation and pillars" paragraph.
- **As ruled: pillars are groups of milestones, the first the thinnest end-to-end slice, and the foundation grows pillar by pillar** (recommended, the owner's ruling). Pro: no speculative design; each extension is planned with the pillar that needs it. Con: a later pillar may extend the foundation, which is new work in a later milestone.
- **Build the full foundation first.** Pro: no later rework of the foundation. Con: deep speculative design, the over-detail trap.

## Notable

**2. Kept spike code is marked and tabled** (terms.md, "Milestones": **Provisional code**). Kept spike code carries `PROVISIONAL(<RungId>): replace at <MilestoneId> (<milestone name>)` in the code and a row in the system design's Provisional code table; `metrics signals` counts the markers. E.g. `// PROVISIONAL(L6): replace at M4 (grade changes)`.
Why it would be important: hard to reverse (a text format a tool parses and code in every project will carry).
No real alternative: the spec settled the marker form, the table's columns and the seam rule, and terms.md matches them. **As written** (recommended).

**18. Manual stand-in is a named term** (terms.md, "Milestones": **Manual stand-in**). New. A manual or fake step that replaces a capability a later pillar will build, so the first pillar can run end to end. Provisional code is preferred when possible (code kept behind a seam beats a hand step); a stand-in is sometimes fine. Each is listed in the system design next to the Provisional code table (what it replaces, the milestone that replaces it, how it is done by hand) and replaced on purpose. E.g. key-value store: the API key is added to the database by hand until the sign-up milestone.
Spec: owner ruling of 2026-11-01.
- **New term beside provisional code** (recommended, decided). Pro: the hand steps are listed and replaced on purpose, not forgotten. Con: one more term and one more table.
- **No term; leave "manual stand-ins" as plain words in the first-pillar definition.** Pro: nothing new to define. Con: hand steps go unlisted and nothing schedules their replacement.

**6. Milestone planning replaces the checkpoint rung and per-rung planning** (terms.md, "Cadence": **Milestone planning**; "Terms that change or retire": **Checkpoint rung**, **Per-rung plan session**, **Depth tags**). One Opus session at a milestone's start looks back at the code, writes the design delta (with the threat and privacy pass), every rung's brief, names as a set and the tasklists; `designed` is now set then, `built` still at fold-back. E.g. "M2 (see it) planning wrote the briefs and tasklists for its four rungs in one session."
Why it would be important: changes sessions and cost.
No real alternative: the spec's "Cadence" table and migration settle it, and terms.md matches. **As written** (recommended).

**7. Re-planning only on a trigger** (terms.md, "Cadence": **Re-plan triggers**; "Terms that change or retire": **Re-plan after every rung**). Inside a milestone, re-plan only when a rung fails, answers a different question than it asked, an owner request lands in the current milestone, or a `settled` seam must change.
No real alternative: the spec's "Cadence" table settles the four triggers; only the name "re-plan triggers" is new, and it is plain. **As written** (recommended).

**8. The additive check stops system design depth** (terms.md, "The system design": **Additive check**). For each later milestone's line, ask whether it can be added as new entities, endpoints or symbols without restructuring; if not, decide that seam now at the smallest depth. E.g. `Change` gets a timestamp now so grading can link to metric windows later.
Decided: the owner approved it as written.
Spec: settled, nearly word for word.
- **"New entities, endpoints or symbols", as written** (decided). Pro: concrete, checkable against the reviewable surfaces. Con: may miss additions that are a new subsystem; the feedback ledger now watches for an addition that passes the check but forces rework later.
- **Add "or subsystems"** (not taken). Pro: covers a milestone that adds a whole component. Con: a new subsystem can hide a restructure the check should catch.

**9. Milestones, foundation first, and spikes before the goal** (terms.md, "Milestones": **Milestone**, **Foundation-first order**, **End-of-goal rule**, **Spike**). Milestones are capability layers with an owner-language outcome, subsystems, demo exit criteria and rungs, ordered so data and the core model come before the goal; the goal's own machinery waits until its foundation milestones are done, except a thin end-to-end slice (the first pillar) that uses manual stand-ins or provisional code ("thin" means no machinery a later pillar must rebuild). A spike, "is it feasible?", may run first and builds none of the goal's machinery. E.g. "can we detect a 10–30% effect at this traffic?" may run as a spike; the experiment loop waits, unless a first pillar runs it end to end on a hand-entered result. Owner ruled (2026-11-01). How deep the foundation goes is item 17.
Spec: all four are settled, including the name "end-of-goal rule".
- **As written** (recommended). Pro: matches the spec and the foundation-before-goal eval. Con: "end-of-goal rule" does not say what it forbids.
- **Rename to "goal-waits rule"**. Pro: says what it does. Con: departs from the spec's own name and the eval's wording.
- Also: **Spike** is defined as "a rung", while `design-session` offers a "throwaway spike" that is not one. Recommend keeping "a rung" and letting `design-session` say "throwaway run" if they must differ.

**10. One retro per milestone at milestone close** (terms.md, "Cadence": **Milestone close**; "Terms that change or retire": **Per-rung retro**). One Opus session at a milestone's end: the full suite if needed, a re-read of every fold-back together, an owner demo ruled accept, accept with follow-ups or reject, one retro, proposed owner preferences, and the re-plan of the next milestone. An unusual rung (failed, re-planned or drifted) still gets a short retro.
Decided (owner): pause and resume. The close does the re-read, then stops at the owner demo; after the owner rules, the same close resumes (retro, preferences, re-plan of the next milestone), possibly in a new session.
Spec: settled.
- **Pause at the demo and resume the same close** (decided). Pro: the owner's part is not rushed and the agent's work continues from the ruling. Con: the close can span two sessions.
- **Split the demo into its own short session** (rejected). Pro: the owner's part is separate from the agent's re-read. Con: one more session per milestone, against the spec's cadence.

**11. Owner preferences and the two-overrides rule** (terms.md, "Owner preferences": **Owner preference**, **Where**, **What is not one**, **Two-overrides rule**). A taste the agent applies to every first pass, one line each with an example and date; cross-project ones in `~/.local/state/danny-agent-skills/owner-preferences.md`, project ones in the rules file; a single ruling or skill feedback is not one; a preference enters after two overrides of the same kind or an outright statement.
Spec: settled; the name "two-overrides rule" is new.
- **Name it "two-overrides rule"** (recommended). Pro: says the threshold. Con: does not mention "or stated outright".
- **No name; keep the rule as a sentence under Owner preference**. Pro: one fewer term. Con: harder to cite from milestone close and `design-session`.

**12. Naming rules for the owner** (terms.md, "Names and labels": **An ID shown to the owner carries its name**, **Names say what the thing does**, **Names are reviewed as a set**). Every ID shown to the owner gets its short name on first use in a message; names use the owner's words with no general words, unlisted metaphors or role names; names are reviewed as a set at the system design and milestone planning. E.g. "L4 (architecture check before folder suggestions)".
Why notable: wide reach (every message), but the spec settled all three.
- **As written** (recommended). Pro: matches the spec. Con: the first-mention rule adds words to short `Next:` lines.
- **Exempt `Next:` lines when the name appeared earlier in the session**. Pro: shorter lines. Con: the owner often reads `Next:` alone after a break.

## Small

**13. `Map.md` and `Touches:`** ("Milestones"). `Map.md` is a zero-token one-page view of milestones and their rungs (name, status, `Touches`); `Touches:` names the subsystems a rung changes. No real alternative: the spec settled both. **As written** (recommended).

**14. Rung** ("Rungs and detail"). One increment inside the current milestone, ordered riskiest unknown first among that milestone's rungs, with an owner pin. **As written** (recommended). Pro: short. Con: does not name the risk kinds (shape, clock, breadth) the spec lists. **Add the three risk kinds.** Pro: one place for them. Con: `risk-first-roadmap` already defines them.

**15. Detail by distance** ("Rungs and detail"). Full brief for the current rung, short briefs for the rest of the milestone, one line plus the additive-check line for the next milestone, a name and one line beyond. Spec settled, same table. **As written** (recommended); no real alternative.

**16. "Decide after it runs" list** ("Rungs and detail"; "Terms that change or retire": **The brief's `Deferred:` line**). A project-level list of minutiae, each filed under the milestone or rung that settles it, checked at fold-back; it replaces the brief's `Deferred:` line. **"Decide after it runs"** (recommended, the spec's name). Pro: says when. Con: long to quote. **"Deferred list".** Pro: short, familiar. Con: the old per-brief meaning lingers.

Shall I close this review as approved?
