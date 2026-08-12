---
name: choosing-swift-design-patterns
description: Use when designing or reviewing Swift code that may need a GoF design pattern, when comparing named patterns, or when code shows creation, interface, hierarchy, state, event, traversal, coordination, undo, behavior-variation, or access-control pressures.
license: GPL-3.0-or-later
---

# Choosing Swift Design Patterns

## Core principle

Make clarity the goal, not pattern use. Apply this priority equally to
greenfield design and existing-code review:

1. Preserve a clear design or add no abstraction.
2. Prefer a clearer Swift-native approach: value types, enums, closures,
   generics, protocols, result builders, property wrappers, dependency
   injection, actors, `AsyncSequence`, or Observation.
3. Use a GoF pattern only when a recurring pressure justifies its extra
   structure.

## Select deliberately

1. Identify the concrete pressure and constraints before opening the index:
   what varies, who owns state, which boundary is unstable, and what must be
   tested or isolated.
2. For existing code, inspect the target type and directly relevant
   collaborators. Do not make any recommendation about existing code you have
   not inspected; request the missing context instead.
3. Apply the priority above. When no change or an obvious Swift-native approach
   resolves the pressure, stop; do not load the index or a pattern reference,
   and omit the References section.
   For a small set of stateless, single-operation behaviors, prefer an injected
   closure or generic function. Use an enum-owned switch when closed identity
   or exhaustiveness is itself the pressure; startup decoding alone does not
   require the enum to own the algorithms.
   For typed events, prefer `AsyncSequence` when consumers are asynchronous or
   Observation for current state. Choose Combine only when the project already
   uses it or its operators and delivery semantics are required.
4. For a direct named-pattern request, resolve and load that pattern's file
   under `references/` directly. Do not open the broad index unless comparison
   is needed. Challenge the requested pattern against the same priority and
   reject it when it would make the design less clear.
5. Otherwise, only after a recurring pressure remains, open the
   [decision index](references/decision-index.md). Treat its routes as prompts,
   not mechanical answers, and load only the one or two strongest candidate
   references.
6. Recommend one primary approach. Name at most two lower-ranked alternatives.
   Every non-primary approach named anywhere—including rejected patterns and
   approaches in costs or contraindications—counts. Before responding, merge or
   remove entries until no more than two remain. The approach being replaced
   consumes one slot, so if named, offer at most one other.
7. State why the primary fits, why alternatives rank lower, its costs, and its
   contraindications. Include relevant indirection, extra types, ownership,
   actor isolation, reference semantics, and test complexity.

For implementation work, produce a project-specific design before changing
code. Before responding, compare References with the files you opened. If any
file under `references/` was loaded, a References section is mandatory: list
every loaded `references/...` path exactly, then each detailed guide's
attributed external source separately. Never label an external URL as an
internal guide.

## Quick response template

```text
Pressure: [observed problem and constraints]
Recommendation: [no change / Swift-native approach / one GoF pattern]
Why: [fit and concrete benefit]
Costs and contraindications: [complexity, ownership, concurrency, testing]
Alternatives (0–2): [option — why it ranks lower]
References (only if loaded): [internal guide and attributed source]
Next context or design step: [only when needed]
```

## Attribution and use

Use this original guidance as informed by the
[Refactoring.Guru Swift design-pattern catalog](https://refactoring.guru/design-patterns/swift)
and in accordance with its
[Content Usage Policy](https://refactoring.guru/content-usage-policy).
Do not redistribute downloaded pages, source examples, or illustrations.
Follow each pattern guide's direct source link when citing its catalog entry.
