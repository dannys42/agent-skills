---
name: decision-driven-design
description: Conduct an iterative design interview that resolves major product, data-model, architecture, persistence, migration, and delivery decisions before implementation. Use when a feature has meaningful ambiguity, the user wants recommendations with tradeoffs and concrete schema or interface examples, or the outcome should be an ordered set of self-contained implementation tasks. Inspect the repository first, track decisions, reconcile revisions, minimize speculative abstractions, and finish with a concise process retrospective.
license: GPL-3.0-or-later
---

# Decision-Driven Design

Move from an ambiguous idea to an implementation-ready design through evidence, explicit decisions, and dependency-aware questioning.

## Operating rules

- Inspect the workspace before asking questions. Read relevant implementation, rules, roadmap, specifications, tests, schemas, generated artifacts, and measured evidence.
- Do not ask for facts discoverable locally. Batch independent searches and factual checks.
- Separate current scope from future direction. Preserve an inexpensive future seam only when it adds no premature behavior or abstraction.
- Prefer the smallest model that satisfies accepted requirements. “Useful later” is not sufficient justification for a type, layer, projection, or repository.
- Treat performance, platform behavior, file size, and query capability as evidence questions. Inspect or measure them and label conclusions as measured, documented, inferred, or product-policy choices.
- Ask one major question at a time by default. Group at most three tightly coupled questions when they share one schema delta.
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

Give the user a short decision landscape: the unresolved areas and their dependencies. Let the user correct the landscape, but do not ask them to approve minor categories.

## Map and order decisions

Classify candidate decisions as:

- **Major** — affects schemas, interfaces, migration, user behavior, or several tasks.
- **Minor** — reversible detail; resolve autonomously using project conventions.
- **Evidence-required** — factual uncertainty that should be inspected or measured.
- **Deferred** — intentionally outside scope, with any required seam recorded.

Order questions by leverage:

```text
identity → relationships → authoritative data → query projections
→ persistence → import/export → distribution → migration → presentation
```

Resolve principles before fields. Once an accepted principle determines a downstream detail, do not reopen it without new evidence or a revision.

## Ask with a compact contract

Each major question must contain the decision and why it matters, two or three realistic options, a recommendation with its trade-off, one concise schema/interface/behavior delta, and a direct question asking which direction to use.

```markdown
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
```

Show only the affected delta; do not repeat the complete model.

## Record and reconcile

Maintain a compact ledger:

```yaml
D04:
  topic: preferred pronunciation selection
  status: accepted
  choice: preference on pronunciation
  rationale: query and persistence stay direct
  consequences:
    - no separate preference map
  revisit_when:
    - preference becomes user-specific
```

Use statuses `proposed`, `accepted`, `confirmed`, `superseded`, `deferred`, and `evidence-required`.

When the user accepts an option, record it, state the material consequence once, and continue. For an unlisted option, restate it neutrally, show its concrete delta and downstream effects, ask for confirmation, and do not advance until confirmed. When an earlier decision is revised, replace it, identify genuinely invalidated decisions, and reopen only those. After five decisions or a substantial revision, provide a short delta summary.

## Complete and plan

Stop interviewing when every major decision is accepted, confirmed, deferred, or assigned an evidence gate; no accepted decisions conflict; current scope and future direction are distinct; authoritative data and derived projections are identified; and migration and failure behavior are defined.

Generate dependency-ordered, self-contained tasks. Stabilize interface-defining and high-risk assumptions first; put prototypes and capability spikes before dependent migrations. Each task must include:

```markdown
# Task NN — Outcome-oriented title
## Outcome
## Dependencies and context
## Approved decisions
## Scope
## Ordered implementation steps
## Verification
## Non-goals
## Acceptance criteria
```

Repeat only task-relevant decisions so each task can be handed to another agent without reconstructing the interview. Preserve current behavior until replacement paths are proven. State generated-artifact and commit restrictions when relevant.

Use [interview-patterns.md](references/interview-patterns.md) for revisions, evidence gates, and failure modes. Use [output-templates.md](references/output-templates.md) for ledgers, tasks, and retrospectives.

## Retrospect

After delivering the design or plans, include a concise optional `Process improvements` section. Identify only material friction:

- Skill improvement for reusable interview, sequencing, ledger, planning, or reflection lessons.
- Project-rule candidate for a durable repository invariant.
- User-rule candidate only for a cross-project preference that recurs or was explicitly requested.

For every suggestion state the observed friction, generalized lesson, exact scope affected, and why recurrence is likely. Do not edit skill or rule files during reflection without authorization.
