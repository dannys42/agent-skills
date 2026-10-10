# project-planning

Start a large or semi-ambiguous project in two steps, each its own skill.

| Skill | What it does | Output |
| --- | --- | --- |
| `system-design` | Drafts a high-level design (goals, scope, requirements, entities, architecture, interfaces, technology, verification, risks) with flagged assumptions, then iterates with you to agreement | `<DocDir>/Design-<Topic>.md` |
| `risk-first-roadmap` | Orders the work as end-to-end increments, each answering the riskiest unknown reachable from where you are | `<DocDir>/Roadmap-<Topic>.md` |

`DocDir` is the project's documentation directory (typically `Documentation/` or `docs/`), the same convention as the `task-workflow` plugin. Run the roadmap skill again after any increment to re-plan; hand the next increment to `tasklist` and `tasklist-run` from `task-workflow` to build it.

## Apple-platform tuning

Both skills are tuned for Apple-platform apps. For those projects they propose native defaults (SwiftUI with AppKit/UIKit where needed, document-based vs database persistence, `xcodebuild` verification), seed the risk register with platform risks (drawing, text, printing, documents, sandboxing, signing and notarization), and start the roadmap with a runnable skeleton of the final app shape. Other platforms still work; the Apple reference is simply not loaded.

## Install

```bash
claude plugin install project-planning@danny-sung-agent-skills
```
