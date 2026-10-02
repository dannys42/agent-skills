---
name: decision-driven-design
description: Conduct an iterative design interview that resolves major product, data-model, architecture, persistence, migration, and delivery decisions before implementation. Use when a feature has meaningful ambiguity, the user wants recommendations with tradeoffs and concrete schema or interface examples, or the outcome should be an ordered set of self-contained implementation tasks. Not for small, well-specified, or easily reversible changes.
license: GPL-3.0-or-later
---

# Decision-Driven Design

Move from an ambiguous idea to an implementation-ready design through evidence, explicit decisions, and dependency-aware questioning.

Read [interview-patterns.md](references/interview-patterns.md) before the first question; it covers batching, revisions, evidence gates, and failure modes. Use [output-templates.md](references/output-templates.md) for the ledger file, tasks, and retrospectives.

## Operating rules

- Inspect the workspace before asking questions. Read relevant implementation, rules, roadmap, specifications, tests, schemas, generated artifacts, and measured evidence.
- Do not ask for facts discoverable locally. Batch independent searches and factual checks.
- Separate current scope from future direction. Preserve an inexpensive future seam only when it adds no premature behavior or abstraction.
- Prefer the smallest model that satisfies accepted requirements. “Useful later” is not sufficient justification for a type, layer, projection, or repository.
- Treat performance, platform behavior, file size, and query capability as evidence questions. Inspect or measure them and label conclusions as measured, documented, inferred, or product-policy choices.
- Ask one major question at a time by default. Group at most three tightly coupled questions when they share one schema delta. Batch low-risk recommendations for default acceptance as described in interview-patterns.md.
- If a structured question tool is available, use it: put the recommended option first and show each option's delta as its preview. Otherwise use the markdown contract below.
- Keep the active ledger compact. Refer to decisions by ID and summarize deltas instead of replaying history.

## Inspect and frame

Build an internal context capsule:

```text
Current system:
Constraints:
Existing behavior to preserve:
Known future direction:
Unresolved decisions:
Evidence still needed:
```

Before treating existing behavior as something to preserve, check what it actually guarantees today. For example, a value may be attached to a position or derived slot rather than the entity. A goal like “make X stick to the entity” implies it did not before, which lowers the fidelity bar rather than raising it.

Give the user a short decision landscape: the unresolved areas and their dependencies. Let the user correct the landscape, but do not ask them to approve minor categories.

## Size the interview

If the feature is small and reversible, say so, resolve its decisions autonomously with briefly stated assumptions, and go straight to planning.

Otherwise, interview only on decisions affecting user-visible behavior, public interfaces, persistence, migration, or task boundaries. Resolve the rest autonomously and state the assumptions briefly.

## Map and order decisions

Classify candidate decisions as:

- **Major** — affects schemas, interfaces, migration, user behavior, or several tasks.
- **Minor** — reversible detail; resolve autonomously using project conventions.
- **Evidence-required** — factual uncertainty that should be inspected or measured.
- **Deferred** — intentionally outside scope, with any required seam recorded.

Order questions by leverage. The default order for data-heavy features:

```text
scope and user-visible behavior → identity → relationships → authoritative data
→ query projections → persistence → import/export → distribution → migration → presentation
```

For other features, such as UI flows, APIs, concurrency, or auth, keep scope and behavior first, then order by which decisions constrain the most downstream decisions.

Resolve principles before fields. Once an accepted principle determines a downstream detail, do not reopen it without new evidence or a revision.

## Ask with a compact contract

Each major question must contain the decision and why it matters, two or three realistic options, a recommendation with its trade-off, one concise schema/interface/behavior delta, and a direct question asking which direction to use.

~~~markdown
Decision D04: Preferred pronunciation selection

Why it matters: This determines where preference is stored and queried.

Options:

1. Store `isPreferred` on each pronunciation. Recommended because...
2. Store a preferred-ID map on each word. This would...
3. Resolve preference dynamically. This would...

Schema delta of the recommendation:

```swift
PracticePronunciation(dialectID: "en-US", isPreferred: true)
```

Which direction should we use?
~~~

Show only the affected delta; do not repeat the complete model.

## Record and reconcile

Persist the ledger to a file so it survives context compaction and session breaks:

```text
<DocDir>/Decision-<Topic>.md
```

- `DocDir` is the project's existing directory for design documentation, typically `Documentation/` or `docs/`. Follow project rules when they name one.
- `Topic` is a short 2–3 word Snake_Case name for the design, such as `Preferred_Pronunciation`.
- The user may override `DocDir`, `Topic`, or the whole path.

State the path when creating the file. Update it after every accepted, revised, or deferred decision. To resume an interrupted interview, read the ledger file and continue from its first unresolved decision.

When the user accepts an option, record it, state the material consequence once, and continue. For an unlisted option, restate it neutrally, show its concrete delta and downstream effects, and ask for confirmation. Record it as `proposed` until confirmed and do not advance. When an earlier decision is revised, supersede it, identify genuinely invalidated decisions, and reopen only those. After five decisions or a substantial revision, provide a short delta summary.

## Complete and plan

Stop interviewing when every major decision is accepted, deferred, or assigned an evidence gate; no accepted decisions conflict; current scope and future direction are distinct; authoritative data and derived projections are identified where relevant; and migration and failure behavior are defined where relevant.

Generate dependency-ordered, self-contained tasks using the task template. Stabilize interface-defining and high-risk assumptions first; put prototypes and capability spikes before dependent migrations.

Repeat only task-relevant decisions so each task can be handed to another agent without reconstructing the interview. Preserve current behavior until replacement paths are proven. State generated-artifact and commit restrictions when relevant.

## Retrospect

After delivering the design or plans, include a concise `Process improvements` section only when there was material friction; otherwise omit it entirely. Candidates:

- Skill improvement for reusable interview, sequencing, ledger, planning, or reflection lessons.
- Project-rule candidate for a durable repository invariant.
- User-rule candidate only for a cross-project preference that recurs or was explicitly requested.

For every suggestion state the observed friction, generalized lesson, exact scope affected, and why recurrence is likely. Do not edit skill or rule files during reflection without authorization.
