# Changelog

## 0.10.2

A brief promised that package tests pass; the base commit would not build, and an unplanned port task cost about 16% of the rung's subagent tokens. The first-real-call clause covered external systems, framework behaviour, real data and produced messages, not the project's own build state.

- `roadmap-plan-next-rung` step 2: the unverified-assumption clause also covers "the build and tests the brief cites pass at the base": run them once at planning, and a failure is the rung's first task (about 20 words in the existing sentence)
- Not changed: asking the owner what they want to see for a rung whose done-when is a human reading output (collected); a one-line outcome for finding rows in the brief (collected)
- One-run hypothesis, wording only

## 0.10.1

A rung whose last step was a tool run over a user's whole data set saw its real-data failure only there: a single-item call had passed earlier, and the fix took three runs. The first-real-call clause already existed; it did not say how much data the first call covers.

- `roadmap-plan-next-rung` step 2: when the rung ends in a run over many items, the first real call is a run over a sample of them, not a single item (a clause of about 20 words inside the existing first-real-call sentence)
- Not changed: code-move tasks listing files in the brief's Components step. The tasklist is where a move task names its files (`task-workflow` 0.16.4 puts that, and a reorganisation-only commit, in `tasklist`), and the brief stays thin
- One-run hypothesis, wording only

## 0.10.0

Owner-directed (design: `docs/project-planning/Design-Shape_Value_Names.md`, part D). Nothing looked forward at whether the built architecture holds for the next goal; refactor rungs kept being found after the fact, and the design spread over several docs.

- `risk-first-roadmap`: checkpoint rungs (`Kind: checkpoint`), placed after the first end-to-end run of the shape and as the first rung of each milestone after M1; a ladder smell for a missing one; the `Next:` line offers a checkpoint with a skip; the one-time milestone pass places them too
- `system-design`: `checkpoint` mode. It looks back (a `code-quality-pass review` since the last checkpoint, or one run now, plus docs against code, plus folding scattered design docs into the Overview) and forward (whether the shape holds for the milestone's components, kept at `sketched`), presents one list, applies the rulings, and runs the re-plan. Record in `SystemDesign/Rung-<RungId>-Checkpoint.md`
- `rung`: a `plan` step on a checkpoint rung becomes `checkpoint`, offered as the default with run or skip; `/rung checkpoint` and `/rung skip` overrides; a skip sets `[obsolete: skipped by owner]` and is logged
- `roadmap-plan-next-rung`: a checkpoint rung goes to `system-design`; close's `Next:` uses the checkpoint form when the next rung is one
- `code-quality-pass`: a review run from a checkpoint stops after synthesis and finishes after the owner's rulings; `checkpoint` is a trigger value
- Not changed: the `roadmap` tool (an interrupted checkpoint reads as `plan`, which `/rung` converts); `code-quality-pass` triggers keep their own review offer between checkpoints

## 0.9.0

Owner-directed, not from a retro (design: `docs/project-planning/Design-Shape_Value_Names.md`). On one adopted project the experiment workflow went deep while ingestion of data that cannot be backfilled was unfinished, a "not feasible at this traffic" answer did not slow the experiment branch, new requests landed in the Horizon as design paragraphs, and new names reached the code before the owner saw them.

- `risk-first-roadmap`: each unknown has a class: `shape` (would change components, boundaries, data flow or persistence), `clock` (delay loses something for good) or `breadth`. Order is skeleton, shape until one end-to-end run, clock items started early and finished, then breadth. "Shape first, then grow" with the database counter-example (first table yes, whole schema no)
- `risk-first-roadmap`: milestones, outcomes the owner can use, in a `## Milestones` section, ordered by value; rungs carry `Milestone:` and `Class:`; only the current milestone's rungs are detailed
- `risk-first-roadmap`: new requests mid-roadmap are mapped to a milestone, their prerequisites classed, one Horizon line added, and any detail parked verbatim in `ParkedIdeas-<Topic>.md`; a Horizon item past one line is a tidy trigger
- `risk-first-roadmap` re-plan: a "no" on a milestone's premise defers its open rungs and asks the owner to keep, reshape or drop it; a finished milestone hands over to the next; an existing roadmap without milestones gets a one-time offer to add them
- Three new ladder smells: a clock item behind breadth, a rung for a later milestone while the current one is open, a whole layer designed up front
- `roadmap-plan-next-rung` and `presenting-for-review.md`: new database schema names, domain terms, wire fields and type names are flagged with candidates, the nearest existing name and any clash
- `roadmap-example.md`: milestones and classes in the format and the worked example; the "Why this order" prose is shorter
- Not yet: checkpoint rungs (0.10.0, a `checkpoint` mode in `system-design`); a glossary file as a plugin standard (waiting on `Taxonomy.md` in use)
- No `roadmap` tool change: the tool does not read `## Milestones` or the new rung lines

## 0.8.9

A rung inserted as `25a.` was never parsed by the `roadmap` tool (plain-digit prefix only): lint blamed the wrong rung, `roadmap next` and `status` picked the wrong one without a warning, and the fix was renumbering 21 lines. A roadmap ended at 47 KB with no tidy trigger left to apply. A flagged review card said only "ask you for X", and the owner had to ask for it to be expanded.

- `risk-first-roadmap` ladder format: the number is plain digits and only a position. A new rung takes the next unused ID and its line goes in place; renumber the position numbers after it, never `25a.` or `25.1`. A reason after the status is a few words, and the line stays under about 400 characters
- `risk-first-roadmap` tidy: a further trigger for a roadmap still over about 40 KB: dated re-plan bullets under `## Why this order` move verbatim to the Log file
- `presenting-for-review.md`: each option carries a plain example from the project; an open or naming question lists candidate answers; a card that only says "I will ask you" is not allowed
- `code-quality-pass` review synthesis: a claim needing a cross-module or live-data check is marked `unverified` with the check that settles it; flagged proposals carry options in the shared shape
- Not changed: the tool itself (needs a `[task-workflow]` item: accept or warn on a ladder line that starts with digits and letters), a `Taxonomy.md` glossary for names reviews, a no-Workflow-while-waiting line in close, giving scouts the manifest and live counts (see the ledger)
- One-run hypotheses, wording only
## 0.8.8

A brief's "Done when" promised a specific server message on a bad input; the route returned only a generic body, found at the real-run task.

- `roadmap-plan-next-rung`: the unverified-assumption clause also covers the exact message, code or status a `Done when` expects the project's own code to return, read from the route or function that produces it (a few words on the existing sentence; the read is cheap, so the check happens before agreement)
- One-run hypothesis, wording only

## 0.8.7

A rung's tidy logged its `quality` event at scout time with `commits 0, lines 0`, so the rung's `metrics summary` showed a pass that looked empty while the tidy's own run held 8 batches and 213 lines.

- `code-quality-pass`: a tidy's `quality` event omits `commits` and `lines` (it is written before the tasks run; the summary prints only the fields present, and the tidy's `tasklist-run` run has the real numbers). A review or baseline still logs them. The skill's version string in the event now follows the plugin
- Not changed: a brief step to list new public wire names for owner confirmation, and a brief line naming the repeated shape of sibling queries (both collected, see the ledger); the null, zero and denominator clause of 0.8.6 already covers the "unit of a common-days rule" ask by its denominator wording
- One-run hypothesis, wording only

## 0.8.6

A rung's brief agreed a response contract with derived ratios without listing their null and zero cases or denominator scope; 4 of 9 review notes were owner rulings on exactly those, and the task that built the ratios was the rung's largest batch (1 correction round).

- `roadmap-plan-next-rung`: the Components step also names, for each derived ratio or aggregate a boundary returns, its null and zero cases and what its denominator covers, as a proposed default flagged as an assumption (one clause on the existing sentence; no new section, no extra question)
- Not changed: the real-data check for an assumed link between data sets. The 0.3.4 data-property rule already covers it; the run was on 0.8.3 and no brief on 0.8.4 or later has been seen, so it is collected (see the ledger)
- One-run hypothesis, wording only

## 0.8.5

A rung's slice, scope and verification rested on an assumption that the rung's first task refuted: one of three slice items was deferred and three brief sections needed an "As built" correction. Fold-back also found a decision row that restated an existing decision and left it `proposed`. Interleaved rungs share a base commit, so the retro's commit range over-counted.

- `roadmap-plan-next-rung`: when an unchecked assumption gets a first-call task instead of an early check, each slice item that rests on it is marked `conditional` with what drops if it is refuted (a clause on the existing sentence)
- `roadmap-plan-next-rung`: a decision a design doc already holds is cited by its qualified ID, not restated as a new brief row
- `roadmap-plan-next-rung` retrospective: when another rung ran in between, the rung's commits come from its tasklist's history, not `<Base>..HEAD`
- One-run hypotheses, wording only

## 0.8.4

A rung brief assumed a framework would open a tapped document on one platform because it did on another; it showed only at the owner's hand check and cost one unplanned heavy task.

- `roadmap-plan-next-rung`: the first-real-call line for unverified assumptions also names a framework's behaviour, including what a platform does with an event a `Done when` relies on (a few words; no new section)
- One-run hypothesis

## 0.8.3

A tidy's proposals and defects were reduced to a count that linked to nothing, never ruled on, and never reached the re-plan.

- `code-quality-pass`: tidy step 7 writes the scout's proposals and defects verbatim to `Quality/Proposals-<RungId>.md` before the offer, and `Status.md`'s `Backlog:` links to it (never a bare count); step 8 asks one batched question beside the tidy offer: accept, defer or reject each proposal, "bug task with a reproducing test first, yes or no" for each defect. Only a yes writes a bug task. `quality_outcome` also covers a tidy (`kind`)
- `risk-first-roadmap`, `roadmap-plan-next-rung`: the re-plan at close places accepted entries from `Proposals-<RungId>.md` as it does a review's

## 0.8.2

- `rung`, `risk-first-roadmap`, `code-quality-pass`: the plan tools version they check for is 0.5.0 (task-workflow 0.16.0)

## 0.8.1

- `rung`, `roadmap-plan-next-rung`: a run is recommended on Opus only when more than half the open tasks are `heavy` (task-workflow 0.15.0); otherwise Sonnet with an Opus advisor for the judgment calls

## 0.8.0

Users had to remember five long commands across clean sessions, and skipping the re-plan left the finished rung `in progress`, so a bare `/roadmap-plan-next-rung` picked it again.

- New `rung` skill: `/rung` reads the project's files (with plan tools 0.4.0's `roadmap next`) and runs the next step; `/rung status` prints where the project stands. The cycle is three sessions: plan, run, close
- `rung` finds the step at zero turns: `scripts/next.sh` runs `roadmap next` as the skill loads (Claude Code `!` injection, pre-approved by `allowed-tools`) and always exits 0, because a failed injected command aborts the skill. When the tool is missing it installs and runs it in one Bash call, instead of reading another skill for the install command
- `roadmap-plan-next-rung`: `close` (alias `fold-back`) merges fold-back, the retrospective in a background Sonnet subagent and the re-plan into one Opus session
- `Next:` lines in `system-design`, `risk-first-roadmap`, `roadmap-plan-next-rung` and `code-quality-pass` point at `/rung`
- `system-design`, `risk-first-roadmap` and `roadmap-plan-next-rung` pin `model: opus`
## 0.7.1

- `retrospective.md`: a retro ends with exactly one feedback block for the new `/retro-feedback` command (replaces `/roadmap-feedback` and `/tasklist-feedback`), items tagged `[project-planning]` or `[task-workflow]`, preceded by a plain "Paste this block" line; the block gains `Run:` (run IDs) and `Diagnosed:` lines; new "Check before you guess" step (one command on the cause of a missing or odd number before tagging it `guess`); the `metrics tokens` / `metrics summary` instructions now say that `metrics tokens` takes no tasklist argument and that `summary` matches by list name, also after the list moved to `Completed/`
- `roadmap-plan-next-rung` and `system-design`: retro wording follows the single block

## 0.7.0

- `system-design`, `risk-first-roadmap`, `roadmap-plan-next-rung` and `code-quality-pass` end with a next step and a recommended model: `/risk-first-roadmap` (Opus) after a design, `/roadmap-plan-next-rung <rung>` (Opus) after a roadmap or re-plan, `/tasklist-run <file>` (orchestrator model from `tasklist-run`) after a rung brief, `/risk-first-roadmap` (Opus) after fold-back, and fold-back after a tidy. Each writes a `step` event to the metrics log (model used, next command, recommended model); `code-quality-pass` events carry `model`

## 0.6.1

- `code-quality-pass`: new "Judge by long-term quality" rule for both tiers. Cost sets order and piece size, never whether a finding is kept; a too-big tidy item becomes a proposal, and the scout and synthesis rank by long-term benefit and compounding cost, not effort

## 0.6.0

When the skills hand the user a list to rule on, the items that most deserve a look now come first, with options. Nothing that was shown before is dropped.

- New shared reference `roadmap-plan-next-rung/references/presenting-for-review.md`. It defines a "Needs your attention" section of at most 5 items that are high impact or low confidence. Each gets why it is flagged, what would settle it, and two or three options with a pro and con, recommended first. The full list follows unchanged, flagged items marked `⚑`, then one closing question
- `system-design`: the 3–5 questions and any high-impact or low-confidence assumption or decision are presented that way, and so is the adopt-mode review
- `roadmap-plan-next-rung`: the brief's questions and assumptions use the same shape; an unchecked claim about an external system or real data counts as low confidence
- `risk-first-roadmap`: the ladder review calls out ordering choices that deserve a second look, with alternative orderings
- `code-quality-pass`: the review report gains a "Needs your attention" section between defects and the ranked table; the user picks an option for a flagged proposal
- `retrospective.md`: up to 3 "Worth changing" items are flagged `⚑` with one line of options
- Each skill has a fallback for when the shared file is missing

## 0.5.0

Periodic code-quality passes in the rung cycle, which had none: one project built 17 rungs with no whole-codebase review.

- New `code-quality-pass` skill (`/code-quality-pass [status | tidy | review | baseline | defer]`). Tier 1 `tidy`: behaviour-preserving cleanups of the files one rung changed, at most 6 small commits and about 300 lines, written as `Tasklist-<RungId>-Tidy.md` and run by `tasklist-run`; anything larger becomes a proposal, a characterization test comes first for untested code. Tier 2 `review`: read-only, Sonnet scouts write 40-line seam cards per module and one Opus synthesis ranks at most 10 proposals (`refactor-rung`, `task`, `conventions`, `fitness-test`, `accept-shape`) plus defects; the user rules on each. State lives in `<DocDir>/Quality/Status.md` (current state only, 25-line budget); one live report, older ones moved to `Completed/Quality/`. Logged as `quality` and `quality_outcome` events in the task-workflow metrics log. Never blocks a feature rung
- `roadmap-plan-next-rung`: hand-off records `Base: <sha>` in the brief; fold-back starts with a quality step (`metrics signals`, one-line tidy offer, `Since review:` and `Triggers pending:` updated) and notes a third or fourth copy of one shape; `retro` is one report for the rung's design, runs and quality pass
- `retrospective.md`: standard one-screen format (verdict line, `metrics summary` table, numbered evidence-tagged "Worth changing", optional "Keep" and "Tooling"), lines that would say "none" are left out, and up to two feedback blocks (project-planning and task-workflow). The tooling line asks whether a custom tool would have cut the rung's cost, with the 8% / 3% decision rule
- `risk-first-roadmap`: re-plan places accepted quality proposals (`Kind: refactor` rungs, tasks) and offers a review when the interval or a trigger is due; the roadmap header gains an optional `Quality:` line; expected plan-tool version `0.2.0`

## 0.4.1

- `risk-first-roadmap`: new "Plan tool check" (`roadmap --version`, install from the `task-workflow` plugin's `build.sh` when missing or not `0.1.1`, no `grep`/`awk`/`sed` fallback while an install is untried); the finished-rung `detail:` pointer is shown after the bracketed status, matching what the `roadmap` tool parses
- `risk-first-roadmap`: "Tidy an existing roadmap or Overview" replaces the bare "offer to move the older ones": once per session, when a trigger fires (over about 40 KB, finished rungs and log over half, malformed ladder status, duplicate IDs, over-long lines or cells, bloated Overview cells), offer one move-only tidy pass with the bytes saved and wait for a yes; a malformed status line is repaired, never an ID, heading or other status
- `roadmap-example.md`: the ladder line format is stated explicitly (status in the last bracket, optional `detail:` pointer after it, horizon items as bullets)
- `roadmap-plan-next-rung`: applies the tidy triggers while reading and offers the pass before the brief; runs the same check instead of using the tool "only if it is there"

## 0.4.0

The roadmap and Overview were the largest reads in a planning session (66.6 KB and 27.5 KB in one project; 61% of the roadmap was finished rungs and the learning log, whose entries ran to 6 KB against the existing "one or two lines" rule).

- `risk-first-roadmap`: "Keep the roadmap small": learning-log entries at most about 600 characters with the detail in the design doc; a finished rung's section moves verbatim to `Completed/Roadmap-<Topic>-Rungs.md` at re-plan and its ladder line stays; an old log moves verbatim to `Roadmap-<Topic>-Log.md`; short cells and stable headings; read by section. Existing roadmaps are never rewritten unasked
- `roadmap-plan-next-rung`: read the roadmap rung and the Overview sections the rung touches, not whole files; fold-back keeps decision, risk and traceability cells to one line
- `system-design`: the Overview template caps table cells at about 400 characters
- Optional `roadmap` tool (`~/.cache/danny-agent-skills/bin/roadmap`, built by the `task-workflow` plugin) does the partial reads; without it, `grep -n '^#'` and ranged Reads

## 0.3.4

- `roadmap-plan-next-rung`: the unverified-assumption rule also covers a property of real data (completeness, uniqueness, shape): check it now when a read-only look is cheap, else put one real call or query first

## 0.3.3

- `roadmap-plan-next-rung`: an assumption about an external system's behaviour that later tasks depend on gets one real call as the first task (or a stated reason not to)
- `roadmap-plan-next-rung`: "The brief is short" says per-component tables count toward the page, one line per component

## 0.3.2

- `roadmap-plan-next-rung`: the brief's Components step also names what a touched boundary shares with other components (error codes, identifiers, formats; reuse or reconcile) and, for a new endpoint or entry point, its behaviour when input or configuration is absent

## 0.3.1

- `roadmap-plan-next-rung`: the trivially-small-rung test no longer requires a single component; decisions already recorded in a design or detail doc count as settled, and the tasklist's `Source:` cites that doc
- `roadmap-plan-next-rung`: fold-back works without a brief (compare against the cited doc and the tasklist; no brief status to set)

## 0.3.0

Incremental system design: a thin whole-system outline first, deepened only for what each roadmap rung needs, and split into bounded docs per subsystem instead of one ever-growing design.

- New skill `roadmap-plan-next-rung`: writes a rung design brief (`<DocDir>/SystemDesign/Rung-<RungId>-<ShortRungDescription>.md`) with scope for the rung, requirements touched, the design docs it touches, components with a highlighted Mermaid diagram, decisions, verification, guard rails, and a fold-back list; agrees it with the user, updates only the touched design docs, and hands off to `tasklist`. A `fold-back` mode updates those docs to match what a finished rung built
- `system-design`: default output is now a one-page `<DocDir>/SystemDesign/Overview.md` (outline depth) with component depth tags (`sketched`, `designed`, `built`) and requirement-to-rung traceability; `full` depth on request. New adopt mode documents an existing codebase as-is and records changes of direction as `shift` decisions. Legacy `Design-<Topic>.md` files are read and can be migrated
- `system-design`: subsystems. A piece that is a separate build target, has its own lifecycle or owner, has its own requirements and risks, or has more than about five inner parts gets its own `<DocDir>/SystemDesign/<Subsystem>.md` in the same shape, with a `Parent:` header and a Contract. Parents show it as one component and change only when the Contract does. Subsystem docs are written on demand (when a rung needs the internals, or the user asks), via the new subsystem mode
- IDs are per document and cited across docs qualified by doc name (`Puzzle_Generator:R3`)
- `system-design` references: `design-template.md` replaced by `overview-template.md`, `subsystem-template.md`, and `subsystems.md`; shared diagram rules in `roadmap-plan-next-rung/references/diagrams.md` (Mermaid default, one level per diagram, Graphviz fallback)
- Traceability across docs: each design doc owns the traceability of its own requirements; the Overview maps allocated ones `via <Subsystem>` (`(doc pending)` as coarse coverage until the subsystem doc refines them), and the roadmap's coverage check walks every existing design doc
- Retrospective: `roadmap-plan-next-rung retro [L3]` (offered after fold-back) and `system-design retro` (offered after sign-off) summarise how the design went from the docs, tasklists, and git, and produce a project-neutral feedback block for the repo-local `/roadmap-feedback` skill
- Graceful degradation: each skill keeps working when a sibling skill or linked reference is missing, using an inline minimum, and tells the user what is missing, how to install it, and how to recover
- Mermaid blocks render-checked with `mmdc`; `diagrams.md` says how to check when it is available
- `risk-first-roadmap`: reads `SystemDesign/Overview.md` (legacy `Design-<Topic>.md` as fallback) and subsystem risk registers; the rung-1 architecture document is replaced by a build-targets section in rung 1's brief, still gated on owner approval; traceability lives in the Overview; every accepted `shift` needs a rung; hand-off goes through `/roadmap-plan-next-rung`, and re-planning starts with fold-back of the affected design docs

## 0.2.0

- `risk-first-roadmap`: add an architecture/build-target step inside rung 1 (only when the design has more than one build boundary), gated on owner approval
- `risk-first-roadmap`: add a requirement traceability check to the ladder checks, plus a drift checkpoint after the first end-to-end data rung
- `risk-first-roadmap`: rename rungs from `R1...` to `L1...` so they no longer collide with the design's `R` risk IDs

## 0.1.0

- Initial release with two skills:
  - `system-design`: draft a high-level design with flagged assumptions, iterate with the user to agreement, and produce a ranked risk register at `<DocDir>/Design-<Topic>.md`
  - `risk-first-roadmap`: order work as end-to-end increments that each answer the riskiest reachable unknown, written to `<DocDir>/Roadmap-<Topic>.md`
- Apple-platform reference material for both skills
