# Design file template

File: `<DocDir>/Design-<Topic>.md`. Keep it short enough to read in one sitting; most sections are a few lines or a small table. Omit a section only if it truly does not apply, and say so in one line rather than deleting silently.

IDs are document-wide and never reused or renumbered: `A` assumption, `D` decision, `R` risk, `Q` open question, `FR`/`NFR` requirements.

## Template

```markdown
# Design: <Project name>

Status: draft | agreed (<date>)
Platform: <e.g. macOS 14+, SwiftUI>

## 1. Summary
One paragraph: what it is, who it is for, why it exists.
Success looks like: <2–4 observable outcomes>

## 2. Users and key flows
- Primary user: ...
- Flow 1: <user does X → system does Y → user sees Z>
- Flow 2: ...
(Flows come before entities because they show which entities matter.)

## 3. Scope
| In | Out (not this project) | Later (wanted, not now) |
| --- | --- | --- |

## 4. Focus areas
The 1–3 parts that make or break the project and get the most design depth.

## 5. Requirements
Functional (priority: must / should / could)
- FR1 (must): ...
Non-functional (only those that constrain this project, each with a measurable target where possible)
- NFR1: <quality> — <target>; matters because <reason>

## 6. Constraints and assumptions
| ID | Statement | Status (assumed / confirmed) | If wrong |
| --- | --- | --- | --- |

## 7. Key entities and data model
- Entity: purpose, key fields, owner, lifetime
- Relationships: <A has many B>
- Authoritative vs derived data; what is persisted and where (document file, database, cache, none)
- File or interchange formats the user can see (documents, exports, imports)
Keep to names, relationships, and ownership; no full schemas.

## 8. Architecture sketch
Components and their one-line responsibilities, plus how data flows between them.
Use a small text or Mermaid diagram.
Name the seams: where one component can be swapped, tested, or run without the UI.

## 9. Interfaces
- Internal: the main module boundaries and what crosses them (types, calls, events)
- External: file formats, import/export, network APIs, OS integrations (printing, sharing, shortcuts)
Direction only; leave signatures for implementation.

## 10. Technology direction
| Area | Choice | Why | Rejected alternative |
| --- | --- | --- | --- |

## 11. Verification strategy
How we will know each important thing works: unit tests for logic, UI or snapshot checks, manual checks, performance measurements. This feeds each roadmap item's "done when".

## 12. Risks and unknowns
Ranked, highest first. Score impact and uncertainty as H/M/L; the priority is what hurts most if wrong and what we know least about.
| ID | Unknown | Impact | Uncertainty | Cheapest way to answer | Depends on |
| --- | --- | --- | --- | --- | --- |

## 13. Decision log
| ID | Decision | Status (accepted / open / deferred / rejected) | Why | Revisit when |
| --- | --- | --- | --- | --- |
```

## Notes

- **Summary and success criteria** make "done" testable for the roadmap; without them rungs drift.
- **Cheapest way to answer** is the field the roadmap skill reads most closely. Write it as an experiment ("render a 9×9 grid with a serif numeral at print size and compare to a printed sheet"), not as a worry ("fonts might be hard").
- **Depends on** records what must exist before the risk can even be tested (for example, a running app skeleton). It determines roadmap order.
- A confirmed assumption stays in the table with status `confirmed`; do not delete it, so the reasoning survives.
- When agreement is reached, set `Status: agreed (<date>)`. Later changes go through the decision log, not silent edits.
