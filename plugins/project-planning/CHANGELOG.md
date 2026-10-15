# Changelog

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
