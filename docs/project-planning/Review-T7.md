# Review notes: the system design and design-session skills

Status: waiting on the owner's review (T7 Review the system design and design-session skills, 2026-11-01); delete this file when the review closes.

Reviewed files: `plugins/project-planning/skills/system-design/SKILL.md`, its `references/overview-template.md` (with `subsystem-template.md` and `subsystems.md`, changed to match), and `plugins/project-planning/skills/design-session/SKILL.md` (new). Spec: `docs/project-planning/Design-Blueprint_And_Milestones.md`.

The spec's rulings (what the system design agrees, the additive check, the marks, owner sketch or first pass, the tightening offer, the notes file and promote step) are not reopened. The items below are choices the skill text made where the spec was silent, or how it read the spec. Section names are the headings in each file.

Eval `g2` (spec, "Eval results"): no grader regressed, so it is not an item. Over-detail-trap still fails milestone-scope 0/3, likely because M1 is sized too wide and the roadmap skill is not yet rewritten.

## Important

Two more qualify (adopt mode's scope, review load); they open the notable tier.

**1. Accepted items keep no trace of who drafted them, and no commit does either** (system-design SKILL.md, "6. Iterate to agreement" and "Retrospective"; overview-template.md, "Notes": **Agreement**). When the owner accepts a `proposed` item unchanged, the mark is removed; an item the owner edited reads `owner`. E.g. "Sales Importer … `settled`" (accepted as drafted) beside "Import Command … `settled · owner`". The system design is committed once, at sign-off (step 7; step 4 only saves the draft), and design-session's promote commit already carries final marks, so no commit ever holds an item as `proposed` and then accepted. The share accepted unchanged cannot be recovered from the doc or from git, yet the spec judges owner preferences by it and "Retrospective" lists it as evidence built from git history.
Why: stored format in every system design, and as written the spec's only measure of owner preferences is lost.
- **Drop the mark and record nothing** (as written). Pro: clean agreed doc, no new field. Con: the share cannot be measured, so retros and `/retro-feedback` cannot tell a skill gap from a missing preference.
- **Keep an `agent` origin after acceptance** (`settled · agent`). Pro: the share is countable from the doc. Con: a third origin value on most rows, and rejected items still leave no count.
- **Drop the mark and record the counts when the system design is agreed** (recommended): proposed, accepted unchanged, edited and rejected, as fields on step 7's `step` metrics event (and on design-session's promote event); "Retrospective" reads them from the metrics log instead of git. Pro: the doc stays clean and the share is measured per milestone, as the spec asks. Con: the agent counts at sign-off, and a miscount cannot be checked afterwards.

**2. Assumptions and Focus areas are gone from every design doc** (overview-template.md, the template and "Migrating older docs"; subsystem-template.md; subsystems.md, "When a piece is a subsystem"). A guess the agent makes is now a `proposed` item; an open assumption about the world (does the API return a year of reviews?) is a Risk with its cheapest experiment. Focus areas become risks or are dropped. `A` IDs survive only in older docs, kept by migration.
Why: file format of every system design and subsystem doc, and migration of existing projects.
- **Drop both, as written** (recommended). Pro: one place for each kind of unknown, and no section that invites deep design (focus areas were where depth grew). Con: a design choice the agent assumed and a fact it assumed now look alike until reviewed.
- **Keep an Assumptions section for facts about the world only.** Pro: assumed facts stay visible apart from risks. Con: overlaps the risk register, which already holds each unknown with an experiment.

**3. The look-back returns a list and applies nothing; the checkpoint record file is gone** (system-design SKILL.md, "Look-back (checkpoint)"). Milestone planning calls it first and presents its findings with the milestone's design delta; the forward look moved into that delta. Run alone (`/system-design checkpoint`, kept for older roadmaps with a `Kind: checkpoint` rung), it applies the rulings and records each accepted refactor rung in the code-quality review report as accepted and not yet placed; the following milestone planning places it ahead of the first feature rung and reuses that look-back instead of running another. `Rung-<RungId>-Checkpoint.md` is no longer written.
Why: hands state between sessions through the review report, and milestone planning (not yet rewritten) must honour it.
- **As written** (recommended). Pro: one look-back per milestone, no extra record file, and placing rungs stays with the session that orders the milestone. Con: an accepted refactor rung waits in a review report until milestone planning reads it.
- **Run alone, invoke the roadmap re-plan to place rungs at once** (the old behaviour). Pro: the roadmap shows the rung immediately. Con: places rungs before the milestone is planned, then milestone planning reorders them.

**4. Migration keeps existing marks and runs only from the first milestone planning** (system-design SKILL.md, "Migration"; overview-template.md, "Migrating older docs"). Settled by the spec: the first milestone planning converts in a move-mostly commit, IDs unchanged. Chosen here: decisions `accepted` read `settled`, or `working` with their old revisit note; only cells with no source (a component's Agreement, a new milestone line, a `Touches` line) are `proposed`; open world assumptions go to Risks, choices to Decisions; `Map.md` is skipped with a one-line note if the `roadmap` tool cannot generate it yet; the commit holds nothing else. E.g. FileOrganizerHero's accepted D-rows read `settled` without a new review.
Unmapped, for you to rule (overview-template.md, "Migrating older docs"): an old decision with status `deferred` (or `superseded`, where a doc uses it) has no mapping, and a confirmed assumption that moves to Decisions gets no stated mark. Recommended: `deferred` becomes an Open question keeping its reason; `superseded` stays in Decisions as `superseded by D<n>` with no agreement mark; a confirmed assumption moves as `settled · owner`, since the owner confirmed it.
Why: migration of existing projects (FileOrganizerHero first).
- **Carry marks over, review only sourceless cells** (recommended). Pro: the owner re-reviews only what is new. Con: an old `accepted` that would be `working` under the new terms passes unless its revisit note says so.
- **Mark every migrated item `proposed`.** Pro: the owner re-agrees everything under the new terms. Con: a long review of decisions already ruled, against the spec's "little churn".

**5. A design session only says a re-plan is due** (design-session SKILL.md, "6. Promote"). When a promoted item changes a `settled` item or adds structure to the current milestone, the session says so and ends with `Next: /rung (Opus: /model opus)`; nothing durable records it, so a later `/rung` in a new session does not know. The routing tasks still to come can add a signal.
Why: the spec keeps next-step state in files; this one lives only in chat.
- **Say it now, add a file signal with the `/rung` routing work** (recommended). Pro: no format invented before `/rung` defines its state. Con: until then a missed message means a missed re-plan.
- **Write a re-plan marker now** (a line in the roadmap, as the escalation marker works). Pro: survives a new session. Con: a format `/rung` and milestone planning do not yet read.

## Notable

**6. Adopt mode now designs the current milestone in the same doc** (system-design SKILL.md, "Adopt mode", step 4). After the as-is description is agreed and the `shift` decisions recorded, adopt names the current milestone and runs steps 3 to 7, so one `Overview.md` holds what exists (`built` rows) and what the milestone adds (`sketched` rows). The old adopt ended at the as-is description plus `shift` decisions and handed to the roadmap. E.g. adopting FileOrganizerHero would end with M2's subsystems and seams agreed beside the as-is components.
- **Adopt through the current milestone, as written** (recommended). Pro: ends where New mode ends, with an agreed design the roadmap can size milestones against. Con: a long first session in which the as-is review and the forward design compete for the owner's attention.
- **End adopt at the as-is description and `shift` decisions; milestone planning adds the current milestone's design.** Pro: two smaller sessions, each with one question (is this true? what next?). Con: the roadmap is drafted without a current-milestone design to size M1, the likely cause of the `g2` milestone-scope failures.

**7. The owner rules on every proposed item; the 3–5 question cap is gone** (system-design SKILL.md, "5. Review with the owner" and "7. Confirm and hand off"; subsystems.md, "Subsystem mode", step 3). Review is the whole `proposed` list in tiers, and step 7's bar ("nothing the current milestone builds is still `proposed`") means every item needs a ruling; the closing question lets one reply accept the rest as recommended. E.g. a first pass with 30 proposed rows is one review of 30 items, at most 5 in the callout.
- **Rule on all, tiered, one reply accepts the rest** (recommended). Pro: nothing enters the design unseen, and the tiers keep attention on the costly few. Con: a long review message after a first pass.
- **Restore a 3–5 question cap; the rest are accepted by default.** Pro: a short review. Con: items accepted unread count as agreed, and inflate the share accepted unchanged (item 1).

**8. Subsystem docs and a piece's internals are designed at milestone planning** (subsystems.md, "Promote on demand" and "Subsystem mode"). No real alternative: the spec's one planning session per milestone settles it. **As written** (recommended).

**9. Outline and Full modes are gone** (system-design SKILL.md, "Layout and modes"). No real alternative: the spec's "Scope: the current milestone only" settles it. **As written** (recommended).

**10. "Decide after it runs" items wait under Open questions until a roadmap exists** (system-design SKILL.md, "6. Iterate to agreement"; overview-template.md, "Notes": **Open questions**). Before the roadmap, a minutia reads `Q2 (after it runs): how many days to fetch per call`; it moves to the roadmap's list once that exists.
- **Open questions, marked** (recommended). Pro: no extra file before the roadmap. Con: one move later, which someone must do.
- **Create the roadmap's list early.** Pro: one home from the start. Con: a roadmap file before any roadmap.

**11. Parked items in a design session** (design-session SKILL.md, "6. Promote", table). A parked structural item becomes an Open question naming its milestone, "Q4 (parked until M3, record changes): …"; a parked minutia goes on the "decide after it runs" list. **As written** (recommended). Pro: reuses existing sections, so milestone planning finds them. Con: Open questions now mix three kinds (open, parked, after it runs). **A Parked section in the system design.** Pro: easy to scan. Con: a new section in every doc.

**12. Design session commits twice** (design-session SKILL.md, "6. Promote"). The promote commit includes the notes file; a second commit removes it, so `git log` holds the notes. **As written** (recommended). Pro: the spec's "git keeps it" holds literally. Con: two commits per session. **Never commit the notes.** Pro: one commit. Con: the notes are lost.

**13. A design session before any system design writes a draft Overview** (design-session SKILL.md, "6. Promote" and "3. Trace consequences"). It creates `Overview.md` with `Status: draft` and only the sections promoted items fill; `system-design` continues from it. It also skips the additive check until milestones exist. **As written** (recommended). Pro: nothing promoted is lost and no milestones are invented. Con: a partial Overview that looks like a started system design. **Keep the notes until system-design runs.** Pro: no partial doc. Con: promotion is not a real edit, against the spec.

## Small

**14. Depth tags kept** (overview-template.md, "Notes": **Depth tags**). `sketched`, `designed`, `built` stay; diagrams and the roadmap read them. No real alternative after the terms review. **As written** (recommended).

**15. First pass without a preferences file** (system-design SKILL.md, "2. Start from the owner's sketch or a first pass"). Applies preferences and project rules, otherwise defaults you would defend (simplest option, native tools). **As written** (recommended). Pro: a first pass still has a rule. Con: none worth naming.

**16. `Taxonomy.md` created at sign-off if missing** (system-design SKILL.md, "7. Confirm and hand off"). **As written** (recommended). Pro: agreed names have a home from the first milestone. Con: one more file in a small project.

**17. Description shortened** (system-design SKILL.md, front matter) from about 1,600 to about 850 characters, naming the modes in one sentence. **As written** (recommended). Pro: cheaper in every session's skill list. Con: fewer trigger phrases; the eval's design-skill-used grader still passed 3/3.

**18. Tightening offer shared with the promote message** (design-session SKILL.md, "6. Promote"). One message carries the promote list, preference lines and wording offers. **As written** (recommended). Pro: one round trip. Con: a long message. **Separate message.** Pro: shorter each. Con: an extra turn.

Which options do you take for items 1 to 5? Reply only with the other items you would change; the rest go ahead as recommended.
