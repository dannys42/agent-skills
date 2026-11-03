# Review notes: the 1.0.0 release (project-planning 1.0.0 and task-workflow 0.18.0)

Status: waiting on the owner's review (T21, final review of the 1.0.0 release, 2026-11-02); delete this file when the review closes.

Reviewed files: `plugins/project-planning/CHANGELOG.md` and `plugins/task-workflow/CHANGELOG.md` (top entries), the READMEs (`README.md`, `plugins/project-planning/README.md`, `plugins/task-workflow/README.md`), the plugin manifests and marketplace files, and the eval results in `docs/project-planning/Design-Blueprint_And_Milestones.md` ("Eval results", "1.0.0 findings"). The release commit is `Release project-planning 1.0.0 and task-workflow 0.18.0`. Review notes still open are in `docs/project-planning/Tasklist-Redesign.md` ("Review notes").

The spec's rulings are not reopened. The spec's Rollout lists the pilot on FileOrganizerHero after the new-version eval run; the first item below is whether to release before or after it.

## Eval evidence: 0.11.2 against 1.0.0

Passes out of 3 per grader, judge Sonnet. The full table is in the spec's "Eval results", with the interim columns g2 (after the system design rewrite) and g3 (after the milestone map and fold-back work). The 1.0.0 results file (`plugins/project-planning/evals/results/1.0.0.json`) is untracked, as the spec states.

| Case | Grader | 0.11.2 | 1.0.0 |
| --- | --- | --- | --- |
| over-detail-trap | design-depth | 0/3 | 1/3 |
| over-detail-trap | milestone-scope | 0/3 | 3/3 |
| over-detail-trap | summary-names-ids | 2/3 | 3/3 |
| over-detail-trap | design-skill-used, files-written | 3/3 each | 3/3 each |
| over-detail-trap | score (mean) | 0.33 | 0.80 |
| foundation-before-goal | milestone-order | 0/3 | 3/3 |
| foundation-before-goal | perishable-first | 1/3 | 3/3 |
| foundation-before-goal | summary-names-ids | 1/3 | 0/3 |
| foundation-before-goal | design-skill-used, files-written | 3/3 each | 3/3 each |
| foundation-before-goal | score (mean) | 0.37 | 0.80 |
| demo-stop-handoff (new, no 0.11.2 column) | stop-message | n/a | 0/3 |
| demo-stop-handoff | handoff-resumable | n/a | 2/3 |
| demo-stop-handoff | the other four graders | n/a | 3/3 each |
| demo-stop-handoff | score (mean) | n/a | 0.73 |

Both original cases are well above the baseline. Three results are still failing: design-depth (1/3, and judges are noisy on long files; I did not read the documents by hand), foundation-before-goal summary-names-ids (0/3, all nine votes FAIL, a real gap) and stop-message (0/3 twice; read by hand, the messages meet the grader's three bullets but all give the handoff path, which `plan-milestone/references/handoff.md` "The stop message" forbids). The run cost $10.94 with judges, about 12 minutes.

## Important

**1. Release timing: the release is already committed; the question is whether it ships to users now or after the FileOrganizerHero pilot** (Design-Blueprint_And_Milestones.md, "Rollout" steps 4 and 5). The spec ran the evals (step 4) and then piloted on FileOrganizerHero (step 5): its checkpoint before M2 becomes the first milestone planning session, which also exercises the migration of an existing project. Today the version bumps, changelogs and marketplace entries are committed locally but `main` is 50 commits ahead of `origin/main` (checked with `git ls-remote origin main`: the remote is still at d2d0d0a), so nothing is published yet; pushing `main` is the release.
Why: wide reach (every run of seven skills and the tool reads the new text), migration of existing projects, and the evidence is n=3 per grader on synthetic cases, not a real project. Three graders still fail at 1.0.0 (design-depth, foundation-before-goal summary-names-ids and demo-stop-handoff stop-message), and against g3 two results slipped (foundation-before-goal mean 0.93 to 0.80, handoff-resumable 3/3 to 2/3).
To settle it: is FileOrganizerHero the only project you have in flight, and are you willing to be on 1.0.0 while it is piloted? The migration commit and the milestone planning session have never run on a real project.
- **Release now, pilot afterwards.** Pro: the evals show clear gains, the pilot then runs on the released version and any finding becomes a 1.0.x fix. Con: a defect in migration or milestone planning, which no eval covers, reaches you (and anyone else who installs) as a released version, and a version number cannot be taken back.
- **Pilot first, release after** (recommended). Pro: the pilot covers what the evals cannot (migration of a real Overview and roadmap, the first real milestone planning session, handoff notes in use), and its findings go in before the number is public. Con: the release waits for one real milestone planning session, and the pilot runs on an unpublished build (an install from the repository, which the pilot needs anyway).
- **Release now as a pre-release** (for example, mark it in the changelog as pending the pilot). Pro: installable today and honest about its status. Con: an extra rule to track and the version scheme has no pre-release form today.

**2. Known gaps: fix the three before the release or after the pilot** (Tasklist-Redesign.md, "Review notes", the last three lines; Design-Blueprint_And_Milestones.md, "1.0.0 findings"). Three small gaps are recorded as open:
- (a) The closing summaries of `risk-first-roadmap` and `system-design` do not repeat the rule that every ID carries its name. In the 1.0.0 run, foundation-before-goal summary-names-ids went from 2/3 to 0/3, the bare IDs being milestone and rung IDs.
- (b) `plan-milestone` "Milestone close", step 4 (Demo), and `references/handoff.md`, "The stop message", disagree on what goes in chat and what goes only in the handoff note. Every demo-stop-handoff run gave the full walkthrough and the handoff path.
- (c) The stop-message grader (`evals/demo-stop-handoff/graders/stop-message.md`) omits the short-and-measurable and no-handoff-path rules, so it cannot judge the case against the skill's own text.
Why: (a) and (b) change text every run reads, and (c) decides whether a later eval can show whether (b) is fixed.
- **Fix all three before the release.** Pro: the released text has no known contradiction, and the 1.0.0 column is not carried forward with failing graders no one owns. Con: three small tasks, then the 1.0.0 column no longer describes the text (a re-run to confirm costs about $11, or you accept the fixes unmeasured) and the release moves by those tasks.
- **Fix after the pilot** (recommended). Pro: the pilot shows which gaps matter in a real session (the demo stop is exercised there for the first time), and one batch of fixes comes with the pilot's own findings and one eval re-run of about $11. Con: you pilot on text with two known inconsistencies and may meet (b) in your first real close.
- **Fix only (b) and (c) now, (a) after.** Pro: (b) is the one a real owner sees at a real demo stop, and (c) is a grader-only edit that costs no tokens at run time. Con: (a) stays a known 0/3 until later, and the pilot's first closing summary may show bare IDs.
Recommendation: pilot first, fix the gaps after, with one eval re-run on the combined fixes. Each fix is a small task (a few lines of text or one grader file); the $11 re-run costs the same whether you fix before or after, so the choice is about timing, not money.

## Notable

**3. The version numbers: project-planning 1.0.0 and task-workflow 0.18.0** (the plugin manifests, the marketplace files, `plugins/project-planning/CHANGELOG.md` and `plugins/task-workflow/CHANGELOG.md`). project-planning moves from 0.11.2 to a major version for the new planning model and a changed command set; task-workflow moves from 0.17.2 to 0.18.0 for the tool 0.7.0 and the metrics changes (its changelog says `tasklist` asks for exactly tool 0.7.0, and the first `tasklist` use rebuilds the tool).
- **1.0.0 and 0.18.0** (as committed, recommended). Pro: matches the spec's Rollout step 3, and the major version tells installers that commands changed (`/roadmap-plan-next-rung`, `close <RungId>` and `retro <RungId>` are gone). Con: a 1.0.0 label before a real-project pilot reads as proven.
- **0.12.0 and 0.18.0 until the pilot, 1.0.0 after.** Pro: the number matches the evidence level. Con: a rename and a version change at the same time across manifests, stamps and the changelog, and the spec already ruled 1.0.0.

**4. Changelog wording and the migration paragraph** (`plugins/project-planning/CHANGELOG.md`, 1.0.0, "What changed for the owner" and "Migration of existing projects"; `plugins/task-workflow/CHANGELOG.md`, 0.18.0). The project-planning entry lists the owner-visible changes as bullets (system design model, milestone map, `plan-milestone`, `design-session`, automatic fold-back, milestone close, owner preferences, handoff notes, the retro feedback inbox, lint of left-over markers, other), then one migration paragraph: nothing to do by hand, the first milestone planning session converts existing documents in one commit titled `Migrate planning docs to the system design shape`, IDs never change, and the old commands are gone, replaced by `/rung`.
- **Keep as written** (recommended). Pro: written for the owner, with the migration paragraph stating what you do (nothing) and what the first session commits. Con: long (about 20 lines), so the eleven bullets are skimmable, not read.
Migration for you is nothing by hand: `/rung` starts the first milestone planning session, which converts the existing documents in one commit and shows you the `proposed` cells; the first `tasklist` use rebuilds the tool. That conversion is the pilot's first act on FileOrganizerHero (item 1).
- **Shorten to the five changes the owner will notice** and link the rest. Pro: a 10-second read. Con: drops the retro inbox and its `DANNY_SKILLS_STATE_DIR` setting, which an owner on two machines needs.

**5. README structure** (`README.md`, `plugins/project-planning/README.md`, `plugins/task-workflow/README.md`). The release commit rewrote the skill table rows and the flow paragraph in the project-planning README (system design, milestone map, `plan-milestone`, tidy at milestone close, `/rung` at the milestone's end) and added the retro inbox to the task-workflow README; the root README gained the matching lines. One open review note concerns the README: the system-design paragraph there once said "headline requirements, detail added one rung at a time" (recorded when the system design was rewritten, to be fixed at the bump); The release commit closed it (`README.md` no longer has "rung at a time"), and it closed the note about the codex `defaultPrompt` list too (`plugins/project-planning/.codex-plugin/plugin.json` now has design-session and plan-milestone prompts).
- **Keep the structure** (recommended). Pro: the flow paragraph and the table match the skills. Con: the flow paragraph is one long sentence.
- **Add a short "Upgrading from 0.x" section** to the project-planning README. Pro: the migration note is found by anyone who reads the README and not only the changelog. Con: a second copy of the migration text to keep in step.

**6. The old name `roadmap-plan-next-rung`: alias or a note** (`plugins/project-planning/CHANGELOG.md`, 1.0.0 `plan-milestone` bullet, "formerly `roadmap-plan-next-rung`"; `Predictions.swift` `legacySkillNames`). The changelog notes the old name and says the old commands are gone. The metrics tools accept the old stamp: `legacySkillNames` maps `roadmap-plan-next-rung` to `plan-milestone`, so earlier log lines still count.
- **A note only** (as committed, recommended). Pro: nothing to maintain, the owner never typed the old name (`/rung` dispatches it), and the metrics history is kept. Con: someone typing the old command gets "unknown skill" with no pointer.
- **Keep a stub skill under the old name** that says "renamed to `plan-milestone`". Pro: a typed old command finds a pointer. Con: a skill listed in every install that does nothing, and an agent may pick it by its old triggers.

**7. The decision-fatigue concern, parked** (`docs/project-planning/feedback-ledger.md`, "Parked"). Two reviews held about 20 decisions each and you accepted most recommendations unchanged; the entry parks "how to cut the count you must read" as a feature after 1.0.0. This review has 8 items (2 important, 6 notable, none small) for that reason.
- **Stay parked** (recommended). Pro: one session of evidence, and the pilot's reviews give a second. Con: the next review is as long as the last.
- **Take it into the first 1.0.x release.** Pro: the pilot's reviews are shorter. Con: a design change to a shared reference (`presenting-for-review.md`) before any measure of what you skip.

**8. Open items still queued** (`docs/project-planning/Tasklist-Redesign.md`, "Review notes"). The section has 23 lines: the three known gaps (item 2) and twenty older ones, of which the release closed two (the README system-design paragraph and the codex `defaultPrompt` list), leaving 21 open, including: metrics `Escapes` ID parsing for hyphenated IDs and `Escaped from:` without a space, steps without `began` never costed, a duplicated stderr line in `MetricsTool.swift`, `presenting-for-review.md` wording notes, stale anchors to `risk-first-roadmap`, `plan-milestone` close blocked by an open follow-ups list, `Signals` not reusing `NextStep.stale`, and the foundation-before-goal milestone-order grader check.
- **Release with the list open and sweep it after the pilot** (recommended). Pro: each line is small, local and not on a path the pilot needs. Con: the metrics ones (the `Escapes` parsing in particular) could undercount escapes in the pilot's first milestone.
- **Sweep the metrics lines first.** Pro: the pilot's measurements are trustworthy. Con: a tool change, which bumps the tool version again.

Should the release go out now or after the FileOrganizerHero pilot (item 1: release now, pilot first, or pre-release), and should the three known gaps be fixed before the release or after the pilot (item 2: all three first, after the pilot, or only the demo stop and grader now)? Reply only with the other items you would change; the rest go ahead as recommended.
