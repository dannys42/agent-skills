# Portable Swift Design Patterns Plugin — Design Specification

**Date:** 2026-07-30
**Status:** Approved
**Target plugin:** `swift-design-patterns`

## Summary

Create a new portable plugin that helps AI agents choose and apply common
design patterns in Swift. It must support both greenfield design and review of
existing code, while preferring a simpler Swift-native construct whenever that
is clearer than a formal Gang of Four pattern.

The plugin will expose one discoverable selector skill and 22 progressively
loaded pattern references. A retained import script will fetch the
Refactoring.Guru Swift catalog politely for one-time research, with a hard
minimum of five seconds between requests. Downloaded pages will not be shipped
as plugin content.

The existing `claude-marketplace/` directory or symlink target is read-only
reference material and must not be modified.

## Goals

- Make all 22 patterns in the Refactoring.Guru Swift catalog available as
  focused, actionable guidance.
- Help agents select a fitting pattern from design pressures and code
  symptoms, not superficial structural resemblance.
- Support new-code design and existing-code review.
- Prefer no change or a simpler Swift-native approach when either is clearer.
- Keep runtime token use low through progressive disclosure.
- Distribute the plugin through Codex, Claude Code, Cursor, Gemini CLI, and
  open skill installers using this repository's existing conventions.
- Attribute Refactoring.Guru correctly and comply with its Content Usage
  Policy.
- Retain a reusable, server-friendly import script for future reference.

## Non-goals

- Copy or redistribute Refactoring.Guru articles, source code, or
  illustrations.
- Generate distributable skill text automatically from downloaded HTML.
- Treat use of a named pattern as an architectural goal.
- Recommend a refactor without an observed design pressure or concrete
  benefit.
- Add a vendor-specific subagent whose behavior cannot travel with the plugin.
- Modify the reference implementation under `claude-marketplace/`.

## Pattern Scope

The plugin will cover the current catalog of 22 patterns:

### Creational

- Abstract Factory
- Builder
- Factory Method
- Prototype
- Singleton

### Structural

- Adapter
- Bridge
- Composite
- Decorator
- Facade
- Flyweight
- Proxy

### Behavioral

- Chain of Responsibility
- Command
- Iterator
- Mediator
- Memento
- Observer
- State
- Strategy
- Template Method
- Visitor

## Architecture

Create the plugin at:

```text
plugins/swift-design-patterns/
├── .claude-plugin/
├── .codex-plugin/
├── .cursor-plugin/
├── skills/
│   └── choosing-swift-design-patterns/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── references/
│       │   ├── decision-index.md
│       │   ├── creational/
│       │   │   └── <pattern>.md
│       │   ├── structural/
│       │   │   └── <pattern>.md
│       │   └── behavioral/
│       │       └── <pattern>.md
│       └── scripts/
│           └── import_refactoring_guru.py
├── README.md
└── gemini-extension.json
```

The importer will use Python 3 and its standard library so it remains portable
without adding runtime dependencies. The exact adapter contents will follow
the repository's existing portable-plugin conventions.

The repository-level Codex, Claude, and Cursor marketplace manifests will gain
an entry for the new plugin. The plugin will not depend on a custom MCP server
or network access at use time.

## Progressive Disclosure and Discoverability

Only the metadata for `choosing-swift-design-patterns` is always visible to an
agent. Its description will trigger for:

- selecting architecture for new Swift code;
- reviewing Swift code for design or structural improvements;
- direct questions about GoF or named design patterns;
- code symptoms involving creation, interface mismatch, hierarchies, behavior
  variation, state transitions, event propagation, traversal, coordination,
  undo, deferred work, or object access.

The description will describe triggering conditions rather than summarize the
workflow. It will also identify the guidance as original work informed by and
attributed to the Refactoring.Guru Swift catalog, with full attribution in the
loaded skill body and references.

Loading follows this sequence:

```text
skill metadata
    -> concise selector workflow
    -> compact symptom-to-pattern decision index
    -> one or two relevant pattern references
```

The 22 detailed references remain unloaded until selected. A direct named
pattern request may skip broad candidate generation and load that pattern's
reference immediately, while still checking whether a simpler Swift-native
solution is preferable.

## Selection Workflow

### Greenfield design

1. Identify the actual source of complexity and relevant constraints.
2. Consider no abstraction and ordinary Swift composition first.
3. Compare Swift-native tools such as value types, enums, closures, generics,
   protocols, protocol extensions, result builders, property wrappers,
   dependency injection, actors, `AsyncSequence`, and Observation.
4. Consult the decision index only when a recurring design pressure remains.
5. Load no more than the one or two most relevant pattern references.
6. Recommend one primary approach, explain its costs, and identify at most two
   lower-ranked alternatives.

### Existing-code review

1. Inspect the target type and only directly relevant collaborators.
2. Identify concrete design symptoms without assuming a refactor is necessary.
3. Prefer outcomes in this order:
   - preserve the existing design when it is already clear;
   - recommend a simpler Swift-native refactor;
   - recommend a GoF pattern when it provides a meaningful structural
     advantage.
4. Do not recommend patterns for code that was not inspected.
5. State when more context is required instead of guessing.

### Response contract

The selector should:

1. Restate the design pressure and constraints.
2. Recommend no change, a Swift-native construct, or one primary pattern.
3. Explain why the recommendation fits.
4. Name at most two alternatives and why they rank lower.
5. Flag costs such as extra types, indirection, reference semantics, actor
   isolation, or test complexity.
6. Cite the loaded internal reference and its attributed source.
7. For implementation requests, produce a project-specific design before
   changing code.

Pattern names are shared vocabulary, not goals. A pattern must solve an
observed problem and remain clearer than the code it replaces.

## Decision Index

`references/decision-index.md` will provide compact routing data:

- pattern name and common aliases;
- category;
- recognizable symptoms and design pressures;
- Swift-native alternatives to consider first;
- contraindications;
- commonly confused patterns;
- relative link to the detailed reference.

The index is advisory rather than a mechanical scoring system. For example,
duplicated interchangeable algorithms should first prompt consideration of a
closure or generic before Strategy. A small, local enum switch should remain an
enum until behavior or transition rules become distributed enough for State to
improve clarity.

## Pattern Reference Contract

Every pattern reference will contain:

1. Intent
2. Prefer Swift-native alternatives when...
3. Choose this pattern when...
4. Avoid it when...
5. Design pressures and recognizable code smells
6. Swift implementation guidance
7. Concurrency and ownership considerations where relevant
8. Comparison with commonly confused patterns
9. One original, focused Swift example
10. Review checklist
11. Attribution and a direct source link

Examples will follow modern Swift conventions:

- prefer value semantics;
- use explicit `any` existentials where appropriate;
- account for actors, isolation, and `Sendable` when concurrency matters;
- add protocol boundaries only when substitution or testability justifies
  them;
- use inheritance only when the selected design genuinely benefits from it.

## Import Workflow

The retained import script will:

1. Fetch the Swift catalog page and discover pattern URLs rather than relying
   only on a hard-coded list.
2. Process requests sequentially.
3. Enforce a configurable delay with an immutable minimum of five seconds
   between requests to `refactoring.guru`.
4. Send a descriptive user agent.
5. Honor redirects and `Retry-After`.
6. Use bounded retries with additional backoff for transient failures.
7. Never accelerate after a failure.
8. Save each successful page with its source URL, fetch timestamp, HTTP
   status, and SHA-256 checksum.
9. Resume from valid completed downloads unless an explicit refresh is
   requested.
10. Stop conservatively on unrecoverable or structurally incomplete imports.

Raw pages and import artifacts will live in a temporary or explicitly
gitignored research directory. They will not be installed with the plugin or
committed as reference content.

The importer will not turn HTML directly into skill prose. Authored references
will use the pages only as research inputs for concepts, terminology, Swift
considerations, and source identification.

## Attribution and Content Policy

Refactoring.Guru states that most site content is copyrighted and permits
limited citation with a hyperlink, provided the citation is not a substantial
part of the source article. It separately limits illustration reuse. This
plugin will not reuse illustrations.

Attribution will appear in:

- the plugin description and README;
- the selector skill;
- the import manifest;
- every pattern reference, linked to its specific Swift source page;
- shared metadata linked to the Swift catalog and Content Usage Policy where
  the metadata format permits useful links.

The distributable prose, selection guidance, comparisons, checklists, and
Swift examples will be original. Any short quotation that proves necessary
will be visibly marked, directly linked, and kept non-substantial.

Primary sources:

- [Refactoring.Guru: Design Patterns in Swift](https://refactoring.guru/design-patterns/swift)
- [Refactoring.Guru: Content Usage Policy](https://refactoring.guru/content-usage-policy)

## Failure Handling

- An incomplete catalog import must fail rather than silently omit patterns.
- A missing attribution, missing source URL, or unlinked reference must fail
  content validation.
- Invalid or ambiguous selection inputs should yield ranked alternatives or a
  request for the specific missing context.
- A failed page download must retain enough state for a safe later resume.
- Existing valid downloads must not be overwritten without explicit refresh
  intent.
- The script must expose useful error messages without printing credentials or
  unrelated environment data.

## Validation Strategy

### Skill behavior

Before authoring the selector, capture baseline agent behavior for:

- indirect design symptoms;
- direct named-pattern requests;
- misleading pattern-shaped code;
- greenfield design;
- existing-code review;
- cases where no change is best;
- cases where a Swift-native construct should beat a GoF pattern.

Repeat the scenarios with the completed skill and compare:

- whether the skill triggered;
- whether it loaded the correct references;
- whether it selected or rejected patterns appropriately;
- whether it preferred simpler Swift-native designs;
- whether it explained uncertainty and trade-offs;
- whether unrelated Swift work avoided unnecessary catalog loading.

### Reference integrity

Validate all 22 references for:

- required sections;
- decision-index linkage;
- direct pattern-specific attribution;
- source URL validity;
- original rather than copied prose;
- original Swift examples;
- absence of downloaded HTML and illustrations.

Type-check self-contained Swift examples where platform dependencies permit
it. Mark deliberately illustrative fragments and validate their syntax
separately.

### Importer

Use a local fixture server to test:

- the five-second minimum;
- sequential ordering;
- retries and backoff;
- `Retry-After`;
- redirects;
- resume behavior;
- checksums;
- interruption;
- incomplete catalogs.

During the real one-time import, record request timestamps and verify every
interval is at least five seconds.

### Packaging

Run:

- skill frontmatter and structure validation;
- plugin manifest validation;
- JSON/schema checks for portable adapters;
- repository formatting and link checks;
- a scan proving `claude-marketplace/` was not modified.

## Success Criteria

- The new portable plugin installs through every supported adapter.
- One selector skill exposes all 22 patterns through progressive references.
- Agents reliably find a relevant pattern from indirect symptoms and direct
  names.
- Agents recommend no change or a clearer Swift-native solution when
  appropriate, including during existing-code review.
- Typical use loads only the selector, decision index, and one or two pattern
  references.
- All pattern guides contain original guidance, original examples, and correct
  source attribution.
- The real import observes at least five seconds between all source-site
  requests.
- No raw downloaded content or substantial copied source material ships in the
  plugin.
- The reference `claude-marketplace/` remains unchanged.
