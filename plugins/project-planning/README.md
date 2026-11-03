# project-planning

Start a large or semi-ambiguous project without a top-heavy spec: a system design agreed only as deep as the current milestone needs, a milestone map ordered foundation first and by risk, and design depth added milestone by milestone.

| Skill | What it does | Output |
| --- | --- | --- |
| `system-design` | Agrees a system design with you, starting from your own vision doc or a first pass, bounded by the current milestone (subsystems, seams, data model, names, threat and privacy, decisions, ranked risks), with later milestones one line each. A piece that warrants it (a separate app, library, or service, or a major subsystem) gets its own doc of the same shape, which the parent treats as one component. Adopt mode documents an existing codebase as-is and records where it should head | `<DocDir>/SystemDesign/Overview.md`, plus `<DocDir>/SystemDesign/<Subsystem>.md` when a subsystem is promoted |
| `risk-first-roadmap` | Turns the system design into a milestone map: capability layers ordered foundation first, each with a plain-language outcome and exit criteria, and inside the current milestone a ladder of small end-to-end rungs, riskiest unknown first, so a runnable app exists at every step. Re-plans when a rung fails or answers a different question | `<DocDir>/Roadmap-<Topic>.md`, `<DocDir>/Map.md` (generated) |
| `plan-milestone` | Plans a whole milestone in one session: look-back at the system design, the milestone's design delta (seams, threat and privacy, names), and every rung's brief and tasklist, each with a regression test. Also reviews a rung whose automatic fold-back escalated, and closes a milestone (re-read, owner demo, retro, re-plan) | `<DocDir>/SystemDesign/Rung-<RungId>-<ShortRungDescription>.md`, tasklists |
| `design-session` | Works a design out with you at any point (before the system design, at milestone planning or mid-milestone): you lead, the agent offers two or three shapes with diagrams, traces consequences including the additive check, catches contradictions and offers a throwaway spike. A promote step moves what you pick into the system design as `settled` or `working`, parks or drops the rest | `<DocDir>/SystemDesign/Sessions/<date>-<Short_Topic>.md` (scratch, deleted after promotion); edits to `<DocDir>/SystemDesign/Overview.md` |
| `code-quality-pass` | `/code-quality-pass [status \| tidy \| review \| baseline \| defer]`. Tier 1 tidies the milestone's files at milestone close (small behaviour-preserving commits, run by `tasklist-run`); Tier 2 reviews the whole codebase's shape every few milestones or on a trigger and proposes refactor rungs or tasks you accept or defer. Triggers come from the zero-token `metrics signals`; never blocks a feature rung | `<DocDir>/Quality/Status.md`, `<DocDir>/Quality/Review-<date>.md`, `Tasklist-<MilestoneId>-Tidy.md` |

The flow is: `system-design` → `risk-first-roadmap` → for each milestone, `/plan-milestone` (every rung's brief and tasklist) → for each rung, `tasklist-run` (which folds the finished rung back into the design automatically and escalates what it cannot judge) → `/rung` at the milestone's end (milestone close: owner demo, retrospective and re-plan, with an optional `/code-quality-pass tidy` first and `/code-quality-pass review` when one is due). `/rung` runs each step for you. When you would rather work a design out together, `design-session` explores it with you and promotes what you agree into the system design. `tasklist` and `tasklist-run` come from the `task-workflow` plugin and write `<DocDir>/Tasklist-<RungId>-<ShortRungDescription>.md`.

`DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`), the same convention as the `task-workflow` plugin. Older `Design-<Topic>.md` files are still read, and `system-design` offers to migrate them into `SystemDesign/Overview.md`.

No design doc grows without bound. Each subsystem doc carries a `Parent:` header and a Contract (what the rest of the system may rely on); its parent shows it as one box and changes only when the Contract does. Subsystem docs are written on demand, when a rung needs a piece's internals, not up front. IDs are per document and cited across docs as `Puzzle_Generator:R3`.

Each skill works on its own: when a sibling skill or linked reference is missing, it uses an inline minimum and tells you what to install (`claude plugin install project-planning@danny-sung-agent-skills`, `claude plugin install task-workflow@danny-sung-agent-skills`) and how to pick up where it left off. `system-design retro` and milestone close (through `/rung`) produce a one-screen retrospective (the milestone's design, runs and quality pass) with feedback blocks for the skills' maintainer.

Diagrams are Mermaid inside the markdown by default, with Graphviz for diagrams too dense for Mermaid's layout. Each component's depth tag (`sketched`, `designed`, `built`) is drawn in the diagram, so the Overview shows where the design is still thin.

## Apple-platform tuning

The skills are tuned for Apple-platform apps. For those projects they propose native defaults (SwiftUI with AppKit/UIKit where needed, document-based vs database persistence, `xcodebuild` verification), seed the risk register with platform risks (drawing, text, printing, documents, sandboxing, signing and notarization), and start the roadmap with a runnable skeleton of the final app shape. Other platforms still work; the Apple reference is simply not loaded.

## Install

```bash
claude plugin install project-planning@danny-sung-agent-skills
```
