# project-planning

Start a large or semi-ambiguous project without a top-heavy spec: a thin outline of the whole system, a roadmap ordered by risk, and design depth added one rung at a time, just before that rung is built.

| Skill | What it does | Output |
| --- | --- | --- |
| `system-design` | Drafts a one-page outline of the whole system (scope, headline requirements, components with depth tags, decisions, assumptions, ranked risks, traceability) with flagged assumptions, then iterates with you to agreement. A piece that warrants it (a separate app, library, or service, or a major subsystem) gets its own doc of the same shape, which the parent treats as one component. Adopt mode documents an existing codebase as-is and records where it should head | `<DocDir>/SystemDesign/Overview.md`, plus `<DocDir>/SystemDesign/<Subsystem>.md` when a subsystem is promoted |
| `risk-first-roadmap` | Orders the work as end-to-end increments (rungs), each answering the riskiest unknown reachable from where you are | `<DocDir>/Roadmap-<Topic>.md` |
| `roadmap-plan-next-rung` | Designs just the next rung (scope, requirements and components it touches, decisions, verification, guard rails), agrees it with you, hands off to `tasklist`, and folds the finished rung back into the design | `<DocDir>/SystemDesign/Rung-<RungId>-<ShortRungDescription>.md` |
| `code-quality-pass` | `/code-quality-pass [status \| tidy \| review \| baseline \| defer]`. Tier 1 tidies the files a rung changed (small behaviour-preserving commits, run by `tasklist-run`); Tier 2 reviews the whole codebase's shape every few rungs or on a trigger and proposes refactor rungs or tasks you accept or defer. Triggers come from the zero-token `metrics signals`; never blocks a feature rung | `<DocDir>/Quality/Status.md`, `<DocDir>/Quality/Review-<date>.md`, `Tasklist-<RungId>-Tidy.md` |

The flow is: `system-design` → `risk-first-roadmap` → for each rung, `/roadmap-plan-next-rung` → `tasklist` → `tasklist-run` → `/roadmap-plan-next-rung close <RungId>` (fold-back, retrospective and re-plan, with an optional `/code-quality-pass tidy` first and `/code-quality-pass review` when one is due). `/rung` runs each step for you: plan, run, close. `tasklist` and `tasklist-run` come from the `task-workflow` plugin and write `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`.

`DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`), the same convention as the `task-workflow` plugin. Older `Design-<Topic>.md` files are still read, and `system-design` offers to migrate them into `SystemDesign/Overview.md`.

No design doc grows without bound. Each subsystem doc carries a `Parent:` header and a Contract (what the rest of the system may rely on); its parent shows it as one box and changes only when the Contract does. Subsystem docs are written on demand, when a rung needs a piece's internals, not up front. IDs are per document and cited across docs as `Puzzle_Generator:R3`.

Each skill works on its own: when a sibling skill or linked reference is missing, it uses an inline minimum and tells you what to install (`claude plugin install project-planning@danny-sung-agent-skills`, `claude plugin install task-workflow@danny-sung-agent-skills`) and how to pick up where it left off. `system-design retro` and `/roadmap-plan-next-rung retro <RungId>` produce a one-screen retrospective (the rung's design, runs and quality pass) with feedback blocks for the skills' maintainer.

Diagrams are Mermaid inside the markdown by default, with Graphviz for diagrams too dense for Mermaid's layout. Each component's depth tag (`sketched`, `designed`, `built`) is drawn in the diagram, so the Overview shows where the design is still thin.

## Apple-platform tuning

The skills are tuned for Apple-platform apps. For those projects they propose native defaults (SwiftUI with AppKit/UIKit where needed, document-based vs database persistence, `xcodebuild` verification), seed the risk register with platform risks (drawing, text, printing, documents, sandboxing, signing and notarization), and start the roadmap with a runnable skeleton of the final app shape. Other platforms still work; the Apple reference is simply not loaded.

## Install

```bash
claude plugin install project-planning@danny-sung-agent-skills
```
