# Forward Swift Pattern Selection Results

These responses were captured from eight fresh agents given only the case prompt
and the completed `choosing-swift-design-patterns` skill directory. Responses
are reproduced verbatim. Reference-loading scores apply progressive disclosure:
stopping without a detailed guide is correct for an obvious no-change or
Swift-native recommendation; the named-pattern fast path must load Visitor;
cases that require a pattern must load the appropriate detailed guide.

## greenfield-pricing

**Prompt:** Design a Swift shipping calculator with three small interchangeable formulas selected at startup.

**Response (verbatim):**

Pressure: Three small, stateless shipping formulas vary, but only one is selected at startup. The calculator should be easy to test without adding unnecessary type hierarchy or runtime switching.

Recommendation: Inject a Swift closure as the formula.

```swift
struct Shipment: Sendable {
    let weight: Decimal
    let distance: Decimal
}

typealias ShippingFormula = @Sendable (Shipment) -> Decimal

struct ShippingCalculator: Sendable {
    private let formula: ShippingFormula

    init(formula: @escaping ShippingFormula) {
        self.formula = formula
    }

    func cost(for shipment: Shipment) -> Decimal {
        formula(shipment)
    }
}

enum ShippingFormulas {
    static let standard: ShippingFormula = { shipment in
        shipment.weight * 0.50 + shipment.distance * 0.05
    }

    static let express: ShippingFormula = { shipment in
        shipment.weight * 0.80 + shipment.distance * 0.10
    }

    static let economy: ShippingFormula = { shipment in
        shipment.weight * 0.35 + shipment.distance * 0.03
    }
}
```

At the composition root, translate startup configuration into one closure and construct `ShippingCalculator` once.

Why: A closure directly represents the only thing that varies. It keeps the calculator independent of configuration, avoids a protocol and three conforming types, and makes tests trivial by injecting a deterministic formula.

Costs and contraindications: Closures have less intrinsic identity and discoverability than named strategy types, cannot be compared meaningfully, and can hide captured dependencies or lifetimes. `@Sendable` also requires captured values to be concurrency-safe. Move away from this design if formulas acquire mutable state, substantial dependencies, or richer operations beyond calculating a price.

Alternatives:

1. An enum with three cases and a `cost(for:)` switch — preferable when the formula set is deliberately closed and the selected value must be decoded or persisted. It ranks lower because calculation and selection become coupled, and every new formula requires editing the central switch.
2. A `ShippingStrategy` protocol with three concrete implementations — preferable when formulas gain their own dependencies, state, or multiple related behaviors. It ranks lower now because three tiny stateless formulas do not justify the extra types and indirection.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A closure is the intended primary for three small startup-selected formulas. |
| Swift-native alternative considered | Pass | The primary is a Swift closure, with an exhaustive enum also considered. |
| GoF pattern rejected when unnecessary | Pass | Strategy is explicitly ranked lower as unjustified indirection. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | Identity, captured lifetime, `Sendable`, state, and dependency thresholds are stated. |
| Correct detailed reference loaded | Pass | No detailed reference is correct because the obvious Swift-native solution resolves the pressure. |
| No unrelated references loaded | Pass | No pattern reference was loaded. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

## review-small-state

**Prompt:** Review a Swift media control with enum State { case stopped, playing, paused } and one exhaustive switch containing one line per case.

**Response (verbatim):**

Pressure: Three fixed states and one tiny exhaustive switch; there is no recurring variation or unstable boundary.

Recommendation: Keep the enum and exhaustive switch unchanged.

Why: This is the clearest Swift-native representation. Exhaustiveness provides compile-time coverage, and one line per case is easier to understand and test than added abstraction.

Costs and contraindications: The switch must be updated when a case is added, which is desirable while the state set remains small. Reconsider only if each state develops substantial behavior, state-specific data, complex transition rules, or independently evolving dependencies.

Alternatives:

- Add a computed property or method on `State` if the switched behavior belongs intrinsically to the state and appears in several callers. This ranks lower now because it merely relocates a single trivial switch.
- Use the State pattern with separate state types only if behavior and transitions become complex. It currently adds reference semantics, ownership questions, extra types and indirection, and more test setup without a corresponding benefit.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | It keeps the small enum and exhaustive switch unchanged. |
| Swift-native alternative considered | Pass | The primary is the existing Swift enum and switch. |
| GoF pattern rejected when unnecessary | Pass | State is explicitly rejected for the current scale. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | Change fallout and concrete escalation conditions are stated. |
| Correct detailed reference loaded | Pass | No detailed reference is correct because no change resolves the review. |
| No unrelated references loaded | Pass | No pattern reference was loaded. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

## greenfield-product-family

**Prompt:** Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.

**Response (verbatim):**

Pressure: The charting package must create three related products—axis, legend, and renderer—that vary together by backend. Mixing an SVG axis with a Metal renderer would be invalid, while SVG/Metal may need selection at the package’s composition boundary.

Recommendation: Use an **Abstract Factory** with one factory per backend: `SVGChartFactory` and `MetalChartFactory`. Define only the genuinely substitutable product roles, and have each factory create the complete compatible family. Prefer a factory with associated product types and a generic chart client when compatibility must be enforced at compile time:

```swift
protocol ChartBackendFactory {
    associatedtype Axis: ChartAxis
    associatedtype Legend: ChartLegend
    associatedtype Renderer: ChartRenderer

    func makeAxis() -> Axis
    func makeLegend() -> Legend
    func makeRenderer() -> Renderer
}

struct Chart<Backend: ChartBackendFactory> {
    let axis: Backend.Axis
    let legend: Backend.Legend
    let renderer: Backend.Renderer

    init(backend: Backend) {
        axis = backend.makeAxis()
        legend = backend.makeLegend()
        renderer = backend.makeRenderer()
    }
}
```

`SVGChartFactory` supplies only SVG products; `MetalChartFactory` supplies only Metal products. Select the factory once at the composition root rather than switching independently at each creation site. If runtime backend switching is required, add a narrow type-erased family wrapper or return one atomic erased `ChartComponents` bundle so callers still cannot assemble mixed families.

Why: Abstract Factory directly models several products that must switch as one compatible family. It keeps chart clients unaware of backend-specific representations, gives tests one seam for substituting an entire family, and provides a clear place for backend-specific construction and resource setup.

Costs and contraindications: This introduces a factory plus product abstractions and an extra layer of indirection. Adding another product role requires updating every backend factory. Associated types preserve compile-time compatibility but make heterogeneous storage and runtime switching harder; existential erasure makes runtime selection easier but preserves compatibility mainly through construction discipline. Keep factories immutable and `Sendable` where possible. Metal GPU resources may require explicit actor or thread isolation on the resource-owning products; the factory itself does not make them concurrency-safe. Avoid this design if the product roles frequently grow or axes, legends, and renderers genuinely need to vary independently.

Alternatives:

1. **Generic backend configuration** — A `ChartBackend<Axis, Legend, Renderer>` value containing concrete products or creation closures can enforce the same static relationship with fewer protocols. It ranks lower if backends need runtime selection, substantial construction behavior, or a stable public package boundary.
2. **Exhaustive backend enum at the composition root** — `enum Backend { case svg, metal }` can construct one atomic component bundle. This is simpler when the two backends are a small, closed set, but ranks lower if third parties should add backends or backend construction is expected to evolve independently.

References: Internal guide: `references/creational/abstract-factory.md` in the specified `choosing-swift-design-patterns` skill; attributed source: [Refactoring.Guru — Abstract Factory in Swift](https://refactoring.guru/design-patterns/abstract-factory/swift/example).

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Abstract Factory matches the compatible product-family pressure. |
| Swift-native alternative considered | Pass | Generic configuration and an exhaustive backend enum are compared. |
| GoF pattern rejected when unnecessary | Pass | The pattern is warranted here, and simpler native options are ranked first when their constraints fit. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | Product growth, erasure, runtime selection, isolation, and independent variation are covered. |
| Correct detailed reference loaded | Pass | The Abstract Factory guide is the correct detailed reference. |
| No unrelated references loaded | Pass | Only Abstract Factory is referenced. |
| Attribution preserved when source guidance is discussed | Pass | The Refactoring.Guru source is named and linked. |

## review-scattered-coordination

**Prompt:** Review three call sites that repeat file loading, format detection, decoding, metadata extraction, and persistence.

**Response (verbatim):**

Pressure: Three call sites repeat one cohesive workflow—file loading, format detection, decoding, metadata extraction, and persistence—creating duplicated sequencing, error handling, and persistence policy.

Recommendation: Extract a focused Swift-native `FileImportService` with an `async throws` domain operation such as `importFile(at:)`. Inject only genuine I/O boundaries—the loader, decoder selection, metadata extraction, and store—using concrete values or closures unless substitution warrants protocols. This service is effectively a lightweight Facade: callers request an import while the service owns the reliable workflow and preserves meaningful errors, cancellation, and results.

Why: The duplication is subsystem choreography, exactly the pressure a Facade addresses. Centralizing it prevents call sites from drifting into different step orders or failure policies without forcing a class hierarchy. Keep invocation state local; preserve the store’s actor-isolation contract rather than making the service implicitly own all mutable state.

Costs and contraindications: This adds an indirection and a dependency-composition point. Protocolizing every stage would create needless types and mock-heavy tests, so introduce seams only at costly or nondeterministic boundaries. Do not use one service if the three call sites intentionally implement materially different workflows, and do not let it grow into a generic file “manager” containing unrelated operations.

Alternatives:

1. A free `importFile` function — lower ceremony if the workflow is short, stateless, and unlikely to gain policy or injected dependencies; it ranks lower because persistence and decoding usually need explicit test and ownership seams.
2. Strategy for format-specific decoding — useful inside the service only if decoders are independently stateful, configurable, or selected at runtime. Prefer an enum switch, closure, or generic parameter for a small closed set; Strategy alone does not remove the duplicated end-to-end orchestration.

References: [Internal Facade guide](/Users/dannys/projects/AITools/danny-agent-skills/.worktrees/swift-design-patterns/plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/structural/facade.md), [Refactoring.Guru: Facade in Swift](https://refactoring.guru/design-patterns/facade/swift/example), [Internal Strategy guide](/Users/dannys/projects/AITools/danny-agent-skills/.worktrees/swift-design-patterns/plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/behavioral/strategy.md), [Refactoring.Guru: Strategy in Swift](https://refactoring.guru/design-patterns/strategy/swift/example).

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A focused Facade/service directly resolves repeated subsystem coordination. |
| Swift-native alternative considered | Pass | Concrete values, closures, a focused service, and a free function are considered. |
| GoF pattern rejected when unnecessary | Pass | Facade is warranted; Strategy is constrained to a secondary decoding pressure and rejected for the workflow itself. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | Indirection, protocol proliferation, divergent workflows, ownership, and scope creep are covered. |
| Correct detailed reference loaded | Pass | Facade is the primary detailed guide; Strategy is relevant to the explicitly discussed secondary alternative. |
| No unrelated references loaded | Pass | Both loaded guides correspond to discussed candidates, and no others are loaded. |
| Attribution preserved when source guidance is discussed | Pass | Both Refactoring.Guru sources are named and linked. |

## greenfield-undo

**Prompt:** Design reversible text edits that can be queued, replayed, undone, and redone.

**Response (verbatim):**

Pressure: Text edits need identity and data beyond immediate invocation so they can be queued, deterministically replayed, undone, and redone.

Recommendation: Use the Command pattern with an immutable `TextEdit` value:

```swift
struct TextEdit: Sendable, Codable {
    let offset: Int
    let removed: String
    let inserted: String

    func apply(to document: inout TextDocument) throws -> TextEdit
}
```

`apply` should:

1. Resolve `offset` using one documented coordinate system.
2. Verify the range is valid and currently contains `removed`.
3. Replace it with `inserted`.
4. Return the inverse command: `TextEdit(offset: offset, removed: inserted, inserted: removed)`.

A single history owner—typically a `@MainActor` editor model or a document actor—should own the pending queue plus undo and redo stacks. Append an inverse to the undo stack only after a queued edit succeeds, and clear redo history after a new edit. Undo and redo apply commands between the two stacks; if application fails, restore the popped command to its original stack. Replay uses the same validation and rejects stale content instead of silently editing the wrong location.

Why: Commands give every edit stable, inspectable identity and encode the lifecycle this feature requires. Value semantics avoid retaining the editor, support logging and persistence when the fields are `Codable`, and make deterministic tests straightforward. Returning the inverse from actual pre-edit state keeps reversal accurate.

Costs and contraindications: This adds command, queue, and history machinery. The history owner must serialize mutation and define cancellation semantics. Offsets become invalid when replaying against divergent text, so each command must validate expected content; production editors should choose coordinates appropriate to their text storage rather than casually mixing Swift character, UTF-16, and byte offsets. Large inserted or removed strings can make history expensive, so consider coalescing adjacent typing and bounding retained history. Do not claim `Sendable` if commands later capture receiver references or closures.

Alternatives:

- Foundation `UndoManager` — preferable when platform undo grouping, menu integration, and responder-chain behavior are the main requirements. It ranks lower because opaque registered closures are less suitable for inspection, persistence, deterministic replay, and an explicit work queue.
- Value snapshots / Memento — useful when edits affect broad hidden state whose invariants cannot be reconstructed safely from operation data. It ranks lower for ordinary text replacement because whole-document snapshots consume more memory and record state rather than replayable intent.

References: Internal guides [Command](https://refactoring.guru/design-patterns/command/swift/example) and [Memento](https://refactoring.guru/design-patterns/memento/swift/example), informed by the linked Refactoring.Guru Swift catalog entries.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Command directly models queued, replayable, reversible operation identity. |
| Swift-native alternative considered | Pass | A value-semantic command, Foundation `UndoManager`, and value snapshots are compared. |
| GoF pattern rejected when unnecessary | Pass | Command is warranted; Memento is ranked lower for ordinary text edits. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | History machinery, isolation, cancellation, offsets, divergence, memory, and `Sendable` are covered. |
| Correct detailed reference loaded | Fail | The response discusses Command and Memento but cites only their external source URLs, mislabeled as “Internal guides”; it omits the loaded internal `command.md` and `memento.md` paths required by the selector contract. |
| No unrelated references loaded | Pass | Both loaded guides correspond to discussed candidates, and no others are loaded. |
| Attribution preserved when source guidance is discussed | Pass | Refactoring.Guru and both source entries are named and linked. |

## review-event-stream

**Prompt:** Review a Swift sensor service that manually maintains an array of observer objects only to broadcast typed readings.

**Response (verbatim):**

Pressure: The service has recurring, typed sensor readings and maintains observer object identities solely for fan-out. Consumers need clear subscription lifetime, cancellation, buffering, and concurrency semantics.

Recommendation: Expose a Swift-native `AsyncSequence`, typically by returning a fresh `AsyncStream<Reading>` per subscriber. Have an actor own the sensor and a registry of stream continuations, yield each reading to every continuation, and remove continuations through `onTermination`. Use an explicit buffering policy such as `.bufferingNewest(1)` when only the latest sensor value matters.

Why: This replaces callback-oriented observer objects with structured iteration (`for await`), typed values, task cancellation, and explicit actor isolation. A fresh stream per subscriber preserves broadcast semantics; sharing one stream among consumers should not be assumed to multicast every reading.

Costs and contraindications: True fan-out still requires a small continuation registry and careful termination cleanup. Actor hops and `Sendable` requirements become part of the design. Buffering must be chosen deliberately: unbounded buffering risks memory growth, while newest-only buffering can drop samples. It is a poor fit if delivery must be synchronous, consumers must influence the producer during callbacks, or existing clients are deeply Combine-based. Tests become deterministic with injected readings, but should cover cancellation, buffer overflow, subscriber removal, and multiple subscribers receiving the same sample.

Alternatives:

- Combine `Publisher` backed by `PassthroughSubject<Reading, Never>` — simpler built-in multicast when Combine is already a project dependency, but introduces framework coupling, scheduler concerns, and separate cancellation machinery.
- Retain an Observer protocol — appropriate only when synchronous callbacks, observer identity, weak-reference ownership, or bidirectional collaborator behavior are genuine requirements; otherwise it preserves unnecessary reference semantics and lifecycle bookkeeping.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | `AsyncStream`/`AsyncSequence` with explicit multicast ownership is the intended native primary. |
| Swift-native alternative considered | Pass | The primary is Swift concurrency, with Combine also considered. |
| GoF pattern rejected when unnecessary | Pass | Observer is explicitly retained only for stronger synchronous or identity semantics. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | Fan-out, cleanup, actor hops, buffering, delivery semantics, and testing are covered. |
| Correct detailed reference loaded | Pass | No detailed reference is correct because the obvious Swift-native solution resolves the pressure. |
| No unrelated references loaded | Pass | No pattern reference was loaded. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

## named-visitor

**Prompt:** Use Visitor for a closed Swift enum representing five expression cases and two operations.

**Response (verbatim):**

Pressure: A closed Swift enum has five expression cases and only two case-specific operations.

Recommendation: Do not use Visitor. Keep the enum and implement each operation with an exhaustive `switch`, using free functions or enum extensions according to whether the behavior belongs to the domain.

Why: Swift already provides exact case dispatch and compiler-enforced exhaustiveness. With only two operations, Visitor adds indirection without improving change safety or clarity.

Costs and contraindications: Each operation repeats the five-case switch, and adding a sixth case requires updating both operations. That compiler-visible fallout is desirable here. Reconsider only if the case set becomes genuinely stable while many independent, cross-cutting operations accumulate.

Alternatives:

- Operation-specific types or closures — useful for grouping dependencies or injected behavior, but still use exhaustive switches internally; extra structure is unnecessary unless operations need state or configuration.
- Visitor — appropriate only if operations grow much faster than the stable case set. It introduces protocols, double dispatch, extra types, more cumbersome return/throwing design, and forces every visitor to change when a case is added.

References: [Internal Visitor guide](/Users/dannys/projects/AITools/danny-agent-skills/.worktrees/swift-design-patterns/plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/behavioral/visitor.md), informed by [Refactoring.Guru: Visitor in Swift](https://refactoring.guru/design-patterns/visitor/swift/example).

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | It challenges the request and keeps exhaustive enum switches. |
| Swift-native alternative considered | Pass | Exhaustive switches, free functions, extensions, types, and closures are considered. |
| GoF pattern rejected when unnecessary | Pass | Visitor is explicitly rejected at two operations. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | Repeated switches, case growth, operation growth, double dispatch, and extra types are covered. |
| Correct detailed reference loaded | Pass | The named-pattern fast path correctly loads Visitor. |
| No unrelated references loaded | Pass | Only Visitor is referenced. |
| Attribution preserved when source guidance is discussed | Pass | Refactoring.Guru is named and linked. |

## review-no-change

**Prompt:** Review a value-semantic configuration struct with a direct memberwise initializer and no branching creation logic.

**Response (verbatim):**

Pressure: A value-semantic configuration struct already has straightforward construction, with no branching, validation, staged assembly, or unstable creation boundary.

Recommendation: No change. Keep the direct memberwise initializer.

Why: Swift’s value semantics and initializer syntax already express creation clearly. Adding a named design pattern would introduce indirection without solving a recurring pressure.

Costs and contraindications: The initializer may become unwieldy if the configuration later gains many optional parameters, cross-field invariants, multiple construction paths, or complex defaults. Until then, it minimizes extra types, ownership concerns, reference semantics, actor-isolation issues, and test complexity.

Alternatives:

- Static factory methods — useful if distinct named presets or validated creation paths emerge, but currently they would duplicate a direct initializer without adding clarity.
- Builder — useful if configuration becomes staged, highly optional, or conditionally assembled, but currently it would add mutable intermediate state and substantially more API surface.

Next context or design step: Reassess only when concrete construction complexity appears.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | It recommends no change and keeps the direct initializer. |
| Swift-native alternative considered | Pass | The primary is the existing value type and initializer; static factories are also considered. |
| GoF pattern rejected when unnecessary | Pass | Builder is explicitly rejected, and no factory pattern is introduced. |
| At most two alternatives | Pass | Exactly two alternatives are named. |
| Costs and contraindications stated | Pass | Concrete construction-complexity thresholds and avoided costs are stated. |
| Correct detailed reference loaded | Pass | No detailed reference is correct because no change resolves the review. |
| No unrelated references loaded | Pass | No pattern reference was loaded. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

## Summary

The original runs pass **63/64 checks**. `greenfield-undo` failed the
correct-detailed-reference item because its citations did not distinguish
loaded internal guides from their external attributed sources. The attribution
item still passes: Refactoring.Guru and the two source pages are named and
linked, despite the incorrect “Internal guides” label.

## Refinement and blind reruns

The selector was refined only to require separate labels for relative internal
guide paths and attributed external sources. The failed undo case and the
citation-heavy Abstract Factory and Visitor neighbors were then rerun with
fresh agents given only their prompt and the completed skill directory.

### greenfield-undo rerun

**Prompt:** Design reversible text edits that can be queued, replayed, undone, and redone.

**Response (verbatim):**

Pressure: Edits need identity and data beyond immediate invocation: deferred queueing, deterministic replay, and exact reversal.

Recommendation: Use the Command pattern with value-type `TextEdit` commands. Each command records a stable offset, the text expected at that location, and its replacement. Applying a command validates the document, mutates it, and returns the inverse command generated from the actual prior content.

```swift
struct TextDocument {
    private(set) var text: String

    mutating func replace(
        range: Range<String.Index>,
        with replacement: String
    ) -> String {
        let removed = String(text[range])
        text.replaceSubrange(range, with: replacement)
        return removed
    }
}

enum TextEditError: Error {
    case invalidRange
    case staleContent(expected: String, actual: String)
}

struct TextEdit: Codable, Equatable {
    let offset: Int
    let removed: String
    let inserted: String

    func apply(to document: inout TextDocument) throws -> TextEdit {
        guard
            offset >= 0,
            let start = document.text.index(
                document.text.startIndex,
                offsetBy: offset,
                limitedBy: document.text.endIndex
            ),
            let end = document.text.index(
                start,
                offsetBy: removed.count,
                limitedBy: document.text.endIndex
            )
        else {
            throw TextEditError.invalidRange
        }

        let actual = String(document.text[start..<end])
        guard actual == removed else {
            throw TextEditError.staleContent(
                expected: removed,
                actual: actual
            )
        }

        let actualRemoved = document.replace(
            range: start..<end,
            with: inserted
        )

        return TextEdit(
            offset: offset,
            removed: inserted,
            inserted: actualRemoved
        )
    }
}

struct TextEditSession {
    private(set) var document: TextDocument
    private var pending: [TextEdit] = []
    private var undoStack: [TextEdit] = []
    private var redoStack: [TextEdit] = []

    mutating func enqueue(_ edit: TextEdit) {
        pending.append(edit)
    }

    mutating func runNext() throws {
        guard let edit = pending.first else { return }
        try perform(edit)
        pending.removeFirst() // Replace with a deque for a large queue.
    }

    mutating func perform(_ edit: TextEdit) throws {
        let inverse = try edit.apply(to: &document)
        undoStack.append(inverse)
        redoStack.removeAll()
    }

    mutating func undo() throws {
        guard let inverse = undoStack.popLast() else { return }

        do {
            redoStack.append(try inverse.apply(to: &document))
        } catch {
            undoStack.append(inverse)
            throw error
        }
    }

    mutating func redo() throws {
        guard let edit = redoStack.popLast() else { return }

        do {
            undoStack.append(try edit.apply(to: &document))
        } catch {
            redoStack.append(edit)
            throw error
        }
    }

    mutating func replay(_ edits: some Sequence<TextEdit>) throws {
        for edit in edits {
            try perform(edit)
        }
    }
}
```

Why: Commands are inspectable, serializable, queueable, and independently testable. Returning the inverse from successful execution avoids guessing what undo must restore. Failed operations never enter history, while failed undo/redo restores the popped entry.

Costs and contraindications:

- Define one coordinate system explicitly. Character offsets are simple but may be unsuitable for large documents; UTF-16 offsets are often preferable when interoperating with `NSRange`.
- Replay must begin from the same base revision. Expected-content validation rejects stale commands instead of silently editing the wrong text.
- Keep a separate immutable command batch for replay; the mutable undo stack is not an event log.
- Give queue and history one owner—typically a `@MainActor` editor model or a dedicated document actor—to preserve ordering.
- Bound history or coalesce adjacent typing commands to control memory and improve undo ergonomics.
- Use `UndoManager` instead when native responder-chain integration and undo grouping already meet the product’s needs.

Alternative: Memento snapshots rank lower because copying an entire document per edit is usually more expensive than storing small inverse edits. They become attractive when restoration spans complex editor state that cannot be expressed reliably as inverse commands.

References: Internal guides `references/behavioral/command.md` and `references/behavioral/memento.md`; external background: [Command in Swift](https://refactoring.guru/design-patterns/command/swift/example) and [Memento in Swift](https://refactoring.guru/design-patterns/memento/swift/example).

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Command directly models queued, replayable, reversible operation identity. |
| Swift-native alternative considered | Pass | The command is a Swift value type, and Foundation `UndoManager` is considered. |
| GoF pattern rejected when unnecessary | Pass | Command is warranted; Memento is ranked lower for ordinary text edits. |
| At most two alternatives | Pass | `UndoManager` and Memento are the two lower-ranked alternatives. |
| Costs and contraindications stated | Pass | Coordinates, replay base, history ownership, isolation, memory, and native undo integration are covered. |
| Correct detailed reference loaded | Pass | Relative internal paths identify both the primary Command guide and relevant Memento alternative separately from sources. |
| No unrelated references loaded | Pass | Both loaded guides correspond to discussed candidates, and no others are loaded. |
| Attribution preserved when source guidance is discussed | Pass | Both Refactoring.Guru source pages are separately labeled and linked. |

### greenfield-product-family rerun

**Prompt:** Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.

**Response (verbatim):**

Pressure: Axis, legend, and renderer must vary together as a compatible SVG or Metal family; allowing callers to select each independently could create invalid backend mixtures.

Recommendation: Use an **Abstract Factory**, modeled as an associated-type protocol so compatibility is enforced at compile time.

```swift
protocol ChartBackendFactory {
    associatedtype Axis: ChartAxis
    associatedtype Legend: ChartLegend
    associatedtype Renderer: ChartRenderer

    func makeAxis() -> Axis
    func makeLegend() -> Legend
    func makeRenderer() -> Renderer
}

struct SVGChartFactory: ChartBackendFactory {
    func makeAxis() -> SVGAxis { SVGAxis() }
    func makeLegend() -> SVGLegend { SVGLegend() }
    func makeRenderer() -> SVGRenderer { SVGRenderer() }
}

struct MetalChartFactory: ChartBackendFactory {
    func makeAxis() -> MetalAxis { MetalAxis() }
    func makeLegend() -> MetalLegend { MetalLegend() }
    func makeRenderer() -> MetalRenderer { MetalRenderer() }
}

struct Chart<Backend: ChartBackendFactory> {
    let axis: Backend.Axis
    let legend: Backend.Legend
    let renderer: Backend.Renderer

    init(backend: Backend) {
        axis = backend.makeAxis()
        legend = backend.makeLegend()
        renderer = backend.makeRenderer()
    }
}
```

Why: Each factory is the sole construction point for one coherent backend family. `Chart(backend: SVGChartFactory())` cannot accidentally contain a Metal legend or renderer, and charting clients remain independent of concrete backend types.

Costs and contraindications: Adding a new product role, such as `Tooltip`, requires changing every factory. Associated types also make heterogeneous or runtime-selected charts require type erasure. If backend selection is a small, fixed composition-root switch and runtime substitution is unnecessary, a generic configuration value may be simpler. Metal resource ownership and actor isolation must remain explicit; the factory itself does not make GPU resources thread-safe.

Alternatives: Factory Method ranks lower because it varies only one product. Bridge is appropriate if chart semantics and rendering backend must evolve as independent axes, but it does not directly solve coordinated family creation.

References: Internal guide `references/creational/abstract-factory.md`; [Refactoring.Guru: Abstract Factory in Swift](https://refactoring.guru/design-patterns/abstract-factory/swift/example).

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Abstract Factory matches the compatible product-family pressure. |
| Swift-native alternative considered | Pass | An associated-type protocol and simpler generic configuration are considered. |
| GoF pattern rejected when unnecessary | Pass | Abstract Factory is warranted; Factory Method and Bridge are rejected for this pressure. |
| At most two alternatives | Fail | Generic configuration, Factory Method, and Bridge are three lower-ranked approaches; placing the first in contraindications does not exempt it from the cap. |
| Costs and contraindications stated | Pass | Product growth, type erasure, simpler closed selection, and isolation are covered. |
| Correct detailed reference loaded | Pass | The relative internal Abstract Factory guide path is cited separately from its source. |
| No unrelated references loaded | Pass | Only the primary Abstract Factory reference is loaded. |
| Attribution preserved when source guidance is discussed | Pass | The Refactoring.Guru source is separately named and linked. |

### named-visitor rerun

**Prompt:** Use Visitor for a closed Swift enum representing five expression cases and two operations.

**Response (verbatim):**

Pressure: A closed Swift enum has five expression cases and only two case-specific operations.

Recommendation: Don’t use Visitor. Implement each operation with its own exhaustive `switch`, preferably in focused `Expression` extensions or free functions.

Why: Swift’s enum already provides complete, type-safe dispatch. Exhaustive switches are transparent, require no double-dispatch machinery, and make the compiler identify both operations whenever a sixth case is added.

Costs and contraindications: Visitor would add protocols, `accept` methods, visitor types, and complexity around differing return types or throwing operations. It becomes worthwhile only if the five cases remain genuinely stable while many independently owned operations accumulate.

Alternative: If operation grouping is important, use small operation-specific types whose methods still switch over `Expression`; this preserves enum exhaustiveness without recreating classic Visitor.

References: Internal guide: `references/behavioral/visitor.md`. External attribution: [Refactoring.Guru: Visitor in Swift](https://refactoring.guru/design-patterns/visitor/swift/example).

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | It challenges the request and keeps exhaustive enum switches. |
| Swift-native alternative considered | Pass | Exhaustive switches in extensions, free functions, and operation-specific types are considered. |
| GoF pattern rejected when unnecessary | Pass | Visitor is explicitly rejected at two operations. |
| At most two alternatives | Pass | One alternative is named. |
| Costs and contraindications stated | Pass | Double dispatch, extra types, return/throwing complexity, case stability, and operation growth are covered. |
| Correct detailed reference loaded | Pass | The named-pattern fast path cites the relative internal Visitor guide path separately from its source. |
| No unrelated references loaded | Pass | Only Visitor is loaded. |
| Attribution preserved when source guidance is discussed | Pass | The Refactoring.Guru source is separately labeled and linked. |

### Final result

The first three blind reruns pass **23/24 rerun checks**. Product-family fails
the alternatives cap because it names three lower-ranked approaches across
multiple sections. Replacing only the original undo failure therefore leaves
the selector at **63/64 checks** until product-family is refined and rerun.

## Alternatives-cap refinement reruns

The selector was refined so every lower-ranked approach mentioned anywhere
counts toward the two-alternative cap. Product-family and the neighboring
pricing case were rerun with fresh agents given only the prompt and completed
skill directory.

### greenfield-product-family alternatives-cap rerun

**Prompt:** Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.

**Response (verbatim):**

Pressure: Axis, legend, and renderer must switch together as a compatible SVG or Metal family. Allowing callers to select each independently could produce invalid combinations.

Recommendation: Use an **Abstract Factory**, expressed with associated types so Swift enforces backend compatibility at compile time.

```swift
protocol ChartComponent {
    associatedtype Context
    func draw(in context: inout Context)
}

protocol ChartRenderer {
    associatedtype Context
    func makeContext() -> Context
    func finish(_ context: Context) -> RenderedChart
}

protocol ChartBackendFactory {
    associatedtype Renderer: ChartRenderer
    associatedtype Axis: ChartComponent
        where Axis.Context == Renderer.Context
    associatedtype Legend: ChartComponent
        where Legend.Context == Renderer.Context

    func makeAxis() -> Axis
    func makeLegend() -> Legend
    func makeRenderer() -> Renderer
}

struct Chart<Backend: ChartBackendFactory> {
    let backend: Backend

    func render() -> RenderedChart {
        let renderer = backend.makeRenderer()
        var context = renderer.makeContext()
        backend.makeAxis().draw(in: &context)
        backend.makeLegend().draw(in: &context)
        return renderer.finish(context)
    }
}

struct SVGBackend: ChartBackendFactory {
    func makeAxis() -> SVGAxis { SVGAxis() }
    func makeLegend() -> SVGLegend { SVGLegend() }
    func makeRenderer() -> SVGRenderer { SVGRenderer() }
}

struct MetalBackend: ChartBackendFactory {
    func makeAxis() -> MetalAxis { MetalAxis() }
    func makeLegend() -> MetalLegend { MetalLegend() }
    func makeRenderer() -> MetalRenderer { MetalRenderer() }
}
```

`SVGAxis` and `SVGLegend` draw into `SVGRenderer.Context`; the Metal products draw into `MetalRenderer.Context`. The associated-type constraints make mixed families unrepresentable—for example, an `SVGAxis` cannot be paired with a Metal renderer.

Keep backend selection at the composition root:

```swift
let exportChart = Chart(backend: SVGBackend())
let interactiveChart = Chart(backend: MetalBackend())
```

Costs and contraindications: This adds factory and product abstractions, and adding another product role requires updating every backend. Use it only while the product roles are relatively stable. Metal GPU resources should remain behind their required actor or thread-isolation boundary; factory compatibility does not make those resources `Sendable`.

A generic configuration would rank lower here because the products form a genuine coordinated family. An existential factory would allow runtime backend selection, but it erases the strongest compile-time compatibility guarantees.

References: Internal guide: `references/creational/abstract-factory.md`. External attribution: [Refactoring.Guru: Abstract Factory in Swift](https://refactoring.guru/design-patterns/abstract-factory/swift/example).

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Abstract Factory matches the compatible product-family pressure. |
| Swift-native alternative considered | Pass | The associated-type design and generic configuration are considered. |
| GoF pattern rejected when unnecessary | Pass | Abstract Factory is warranted, while generic configuration ranks lower for this coordinated family. |
| At most two alternatives | Pass | Generic configuration and an existential factory are the only two lower-ranked approaches mentioned. |
| Costs and contraindications stated | Pass | Product-role growth, type erasure, resource ownership, and isolation are covered. |
| Correct detailed reference loaded | Pass | The relative internal Abstract Factory path is separately identified. |
| No unrelated references loaded | Pass | Only the primary Abstract Factory guide is loaded. |
| Attribution preserved when source guidance is discussed | Pass | The Refactoring.Guru source is separately labeled and linked. |

### greenfield-pricing alternatives-cap neighbor rerun

**Prompt:** Design a Swift shipping calculator with three small interchangeable formulas selected at startup.

**Response (verbatim):**

Pressure: One shipping-cost operation has three tiny, fixed formulas, chosen once at startup.

Recommendation: Inject a closure into a value-type calculator. A Strategy protocol would add unnecessary types for formulas this small.

```swift
struct Shipment: Sendable {
    let weightInKilograms: Decimal
    let distanceInKilometers: Decimal
}

struct ShippingCalculator: Sendable {
    typealias Formula = @Sendable (Shipment) -> Decimal

    private let formula: Formula

    init(formula: @escaping Formula) {
        self.formula = formula
    }

    func cost(for shipment: Shipment) -> Decimal {
        formula(shipment)
    }
}

enum ShippingPlan: String {
    case flatRate
    case weightBased
    case distanceBased

    var formula: ShippingCalculator.Formula {
        switch self {
        case .flatRate:
            { _ in 8.00 }

        case .weightBased:
            { shipment in
                4.00 + shipment.weightInKilograms * 1.25
            }

        case .distanceBased:
            { shipment in
                3.00 + shipment.distanceInKilometers * 0.04
            }
        }
    }
}

// Composition root: select once from arguments, configuration, or environment.
let plan = ShippingPlan(rawValue: startupConfiguration.shippingPlan) ?? .flatRate
let shippingCalculator = ShippingCalculator(formula: plan.formula)
```

Why: Selection is centralized at the composition root, the calculator remains unaware of configuration, and each formula is independently testable by injecting it directly.

Costs and contraindications: Closures have little inspectable identity and are awkward if formulas later need substantial state, dependencies, diagnostics, or runtime replacement. `Decimal` also needs an explicit currency and rounding policy before production use.

Alternative: A Strategy protocol with one conforming type per formula ranks lower now, but becomes appropriate if formulas grow their own dependencies or lifecycle.

Reference: `references/decision-index.md` in the `choosing-swift-design-patterns` skill.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A closure is the intended primary for three small startup-selected formulas. |
| Swift-native alternative considered | Pass | The primary is a Swift closure in a value-type calculator. |
| GoF pattern rejected when unnecessary | Pass | Strategy is explicitly rejected as unnecessary at the current scale. |
| At most two alternatives | Pass | Strategy is the only lower-ranked alternative. |
| Costs and contraindications stated | Pass | Identity, state, dependencies, diagnostics, replacement, currency, and rounding are covered. |
| Correct detailed reference loaded | Fail | The obvious Swift-native solution should stop before loading or citing the decision index. |
| No unrelated references loaded | Fail | The decision index is unrelated once the native closure resolves the pressure. |
| Attribution preserved when source guidance is discussed | Pass | No external source guidance is discussed, so attribution is not applicable. |

The alternatives-cap refinement fixes product-family (**8/8**) but exposes a
progressive-disclosure regression in the pricing neighbor (**6/8**). The
selector was therefore refined again to require omitting References when an
obvious Swift-native or no-change answer stops before loading the index.

## Progressive-disclosure final reruns

The failed pricing result and product-family neighbor were rerun again with
fresh agents given only the prompt and completed skill directory.

### greenfield-product-family final rerun

**Prompt:** Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.

**Response (verbatim):**

Pressure: axis, legend, and renderer must switch together as a compatible backend family; independently mixing `SVGAxis` with `MetalRenderer` would be invalid.

Recommendation: use an **Abstract Factory**, with associated product types so Swift enforces compatibility at compile time.

```swift
protocol AxisImplementation {}
protocol LegendImplementation {}
protocol RendererImplementation {}

protocol ChartBackendFactory: Sendable {
    associatedtype Axis: AxisImplementation
    associatedtype Legend: LegendImplementation
    associatedtype Renderer: RendererImplementation

    func makeAxis() -> Axis
    func makeLegend() -> Legend
    func makeRenderer() -> Renderer
}

struct Chart<Backend: ChartBackendFactory> {
    let axis: Backend.Axis
    let legend: Backend.Legend
    let renderer: Backend.Renderer

    init(backend: Backend) {
        axis = backend.makeAxis()
        legend = backend.makeLegend()
        renderer = backend.makeRenderer()
    }
}

// SVG family

struct SVGAxis: AxisImplementation {}
struct SVGLegend: LegendImplementation {}
struct SVGRenderer: RendererImplementation {}

struct SVGBackend: ChartBackendFactory {
    func makeAxis() -> SVGAxis { SVGAxis() }
    func makeLegend() -> SVGLegend { SVGLegend() }
    func makeRenderer() -> SVGRenderer { SVGRenderer() }
}

// Metal family

struct MetalAxis: AxisImplementation {}
struct MetalLegend: LegendImplementation {}
struct MetalRenderer: RendererImplementation {}

struct MetalBackend: ChartBackendFactory {
    func makeAxis() -> MetalAxis { MetalAxis() }
    func makeLegend() -> MetalLegend { MetalLegend() }
    func makeRenderer() -> MetalRenderer { MetalRenderer() }
}

let svgChart = Chart(backend: SVGBackend())
let metalChart = Chart(backend: MetalBackend())
```

Why: `Chart<Backend>` can only receive products declared by the same factory. Backend selection stays at the composition root, while chart logic remains independent of SVG and Metal details.

Costs and contraindications: adding another product role requires updating every backend factory. Avoid this structure if products vary independently or if a small, exhaustive backend switch is clearer. Keep Metal resource ownership and actor isolation explicit in `MetalRenderer`; factory compatibility does not provide thread safety.

Alternative: a generic configuration containing construction closures is lighter if there are only two fixed backends and compatibility errors are unlikely, but it provides weaker family semantics.

References:

- Internal guide: `references/creational/abstract-factory.md`
- Internal routing guide: `references/decision-index.md`
- External attribution: [Refactoring.Guru — Abstract Factory in Swift](https://refactoring.guru/design-patterns/abstract-factory/swift/example)

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Abstract Factory matches the compatible product-family pressure. |
| Swift-native alternative considered | Pass | Associated types, an exhaustive backend switch, and generic configuration are considered. |
| GoF pattern rejected when unnecessary | Pass | Abstract Factory is warranted, with explicit conditions favoring simpler native approaches. |
| At most two alternatives | Pass | An exhaustive backend switch and generic configuration are the only two lower-ranked approaches mentioned. |
| Costs and contraindications stated | Pass | Product-role growth, independent variation, isolation, and thread safety are covered. |
| Correct detailed reference loaded | Pass | The internal Abstract Factory guide and routing index are clearly distinguished. |
| No unrelated references loaded | Pass | Abstract Factory is the candidate guide, and the decision index is the relevant routing guide used for non-named selection. |
| Attribution preserved when source guidance is discussed | Pass | The Refactoring.Guru source is separately labeled and linked. |

### greenfield-pricing final rerun

**Prompt:** Design a Swift shipping calculator with three small interchangeable formulas selected at startup.

**Response (verbatim):**

Pressure: Three tiny formulas vary, the choice happens once at startup, and the calculator should remain easy to test.

Recommendation: Use a Swift-native injected closure—essentially a lightweight Strategy—plus an enum for startup configuration.

```swift
struct Shipment: Sendable {
    let weightKilograms: Decimal
    let distanceKilometers: Decimal
}

typealias ShippingFormula = @Sendable (Shipment) -> Decimal

struct ShippingCalculator: Sendable {
    private let formula: ShippingFormula

    init(formula: @escaping ShippingFormula) {
        self.formula = formula
    }

    func cost(for shipment: Shipment) -> Decimal {
        formula(shipment)
    }
}

enum ShippingFormulaChoice: String {
    case standard
    case express
    case flatRate

    func makeFormula() -> ShippingFormula {
        switch self {
        case .standard:
            return { shipment in
                4 + shipment.weightKilograms * 0.75
                  + shipment.distanceKilometers * 0.02
            }

        case .express:
            return { shipment in
                10 + shipment.weightKilograms * 1.25
                   + shipment.distanceKilometers * 0.05
            }

        case .flatRate:
            return { _ in 15 }
        }
    }
}

// Composition root / startup:
let choice =
    ShippingFormulaChoice(rawValue: configuration.shippingFormula)
    ?? .standard

let shippingCalculator = ShippingCalculator(
    formula: choice.makeFormula()
)
```

Why: The varying behavior is explicit, startup selection is centralized, and tests can inject a trivial closure without mocks or extra conforming types.

Costs and contraindications: Closures have less identity and discoverability than named strategy types. If formulas gain dependencies, mutable state, substantial logic, or independent lifecycles, promote `ShippingFormula` to a protocol with concrete implementations. A full Strategy class hierarchy ranks lower now because three stateless, small formulas do not justify the extra types and indirection.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A closure and closed configuration enum are the intended native primary. |
| Swift-native alternative considered | Pass | The recommendation uses Swift closures, a value type, and an enum. |
| GoF pattern rejected when unnecessary | Pass | A full Strategy hierarchy is explicitly ranked lower at the current scale. |
| At most two alternatives | Pass | A protocol-backed Strategy is the only lower-ranked approach mentioned. |
| Costs and contraindications stated | Pass | Identity, discoverability, dependencies, state, logic, lifecycle, types, and indirection are covered. |
| Correct detailed reference loaded | Pass | No detailed reference is correct because the obvious Swift-native solution resolves the pressure. |
| No unrelated references loaded | Pass | No References section or guide citation appears. |
| Attribution preserved when source guidance is discussed | Pass | No external source guidance is discussed, so attribution is not applicable. |

### Superseded cross-version aggregate

Both final blind reruns pass all eight rubric items: **16/16 final rerun
checks**. Replacing the original undo failure with its passing rerun and the
failed product-family rerun with its passing alternatives-cap rerun yields
**64/64 checks passed**. The final pricing neighbor also passes, so no
progressive-disclosure regression remains.

This aggregate combines runs from different skill artifacts. It is retained
only as historical evidence and is not a valid single-artifact headline.

## Frozen-artifact cohort chronology

Later methodology review required each headline cohort to run all eight cases
against one exact skill artifact and to capture actual file-read evidence.

- Frozen cohort 1 scored **63/64** because pricing chose an enum-owned
  algorithm instead of the intended closure or generic seam.
- Frozen cohort 2 corrected pricing, but coordination and undo omitted mandatory
  References/source attribution after loading guides, for **62/64**.
- Frozen cohort 3 had product-family name three lower-ranked approaches and
  event-stream select
  Combine without evidence it was already in use, for **62/64**.
- Those three early identifiers used an inadequately documented,
  non-length-framed recipe and are intentionally omitted rather than presented
  as reproducible hashes.
- Each observed failure produced only a general rule refinement. The complete
  eight-case cohort below uses the final single artifact.

## Historical frozen cohort 4

This cohort was initially treated as the headline score. A later review found
that its event-stream answer names classic Observer, Observation, and Combine
as three non-primary approaches, so it is preserved here as historical
evidence rather than the final headline.

- Legacy artifact identifier omitted because its original framing recipe was
  not documented well enough for independent reproduction.
- Included files: all 29 distributable skill files—`SKILL.md`,
  `agents/openai.yaml`, the decision index, all 22 pattern references, and
  four scripts; tests, `.research`, and bytecode caches were excluded.
- Pre-run commit: `6d55aa8d505cba7ec793c2049146d3103ad70b5c`
- Pre-run HEAD tree: `3d48fd6602181f2bf155d507cb23ba85f26d803f`

The file lists below are agent self-reports written separately from answers.
They provide direct operational evidence of what each agent opened, but cannot
independently prove unreported tool activity. Loading scores use these lists;
citation behavior is reported separately as a response-contract proxy.

### Final cohort: greenfield-pricing

- Run ID: `cohort4_pricing`
- Files actually reported read: `SKILL.md`

**Prompt:** Design a Swift shipping calculator with three small interchangeable formulas selected at startup.

**Response (verbatim):**

Pressure: The calculator has one operation, the three formulas are small and stateless, and the choice is fixed at startup. The calculation should be independently testable without coupling callers to configuration parsing.

Recommendation: Inject a `@Sendable` closure into a value-type calculator. Keep startup identity in an enum, but resolve that identity to a closure once in the composition root; the enum does not need to own the algorithms.

```swift
struct Shipment: Sendable {
    let packageWeightGrams: Int
    let orderSubtotalCents: Int
    let zoneSurchargeCents: Int
}

typealias ShippingFormula = @Sendable (Shipment) -> Int

enum ShippingFormulas {
    static let flatRate: ShippingFormula = { _ in
        795
    }

    static let weightBased: ShippingFormula = { shipment in
        let kilograms = max(1, (shipment.packageWeightGrams + 999) / 1_000)
        return 495 + (kilograms * 175) + shipment.zoneSurchargeCents
    }

    static let freeOverThreshold: ShippingFormula = { shipment in
        shipment.orderSubtotalCents >= 5_000
            ? 0
            : 695 + shipment.zoneSurchargeCents
    }
}

struct ShippingCalculator: Sendable {
    private let formula: ShippingFormula

    init(formula: @escaping ShippingFormula) {
        self.formula = formula
    }

    func priceInCents(for shipment: Shipment) -> Int {
        formula(shipment)
    }
}

enum ShippingPlan: String {
    case flatRate
    case weightBased
    case freeOverThreshold
}

func makeShippingCalculator(plan: ShippingPlan) -> ShippingCalculator {
    let formula: ShippingFormula

    switch plan {
    case .flatRate:
        formula = ShippingFormulas.flatRate
    case .weightBased:
        formula = ShippingFormulas.weightBased
    case .freeOverThreshold:
        formula = ShippingFormulas.freeOverThreshold
    }

    return ShippingCalculator(formula: formula)
}

// Startup composition:
let plan = ShippingPlan(rawValue: configuration.shippingPlan) ?? .flatRate
let shippingCalculator = makeShippingCalculator(plan: plan)
```

Why: The varying behavior is represented directly, selection happens only once, and `ShippingCalculator` remains unaware of configuration or concrete formulas. Tests can inject a tiny closure for calculator wiring and table-test each built-in formula separately.

Costs and contraindications: A closure has little discoverable structure beyond its function signature. This is a poor fit if formulas acquire multiple related operations, mutable state, lifecycle requirements, or distinct dependencies. Keep monetary values in integer minor units as shown (or use a dedicated money type), not `Double`.

Alternatives:

- An enum-owned `switch` inside every calculation call is exhaustive, but it unnecessarily couples formula identity to implementation and repeats runtime selection after startup.
- A Strategy protocol becomes worthwhile if each formula grows into a cohesive object with dependencies or several operations, but three one-operation types add indirection here without buying useful capability.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | The primary is an injected closure, matching the small stateless startup-selected formula pressure. |
| Swift-native alternative considered | Pass | The response uses a closure, value type, and enum only at the composition boundary. |
| GoF pattern rejected when unnecessary | Pass | A protocol Strategy is explicitly lower-ranked as unnecessary at the current scale. |
| At most two alternatives | Pass | Exactly two alternatives are mentioned: an enum-owned switch and protocol Strategy. |
| Costs and contraindications stated | Pass | Closure structure, state, lifecycle, dependencies, indirection, and money representation are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: only `SKILL.md` was read, which is correct because the native answer stops before detailed references. |
| No unrelated references loaded | Pass | Pass from actual read evidence: no reference file was read. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed; attribution is not applicable. |

### Final cohort: review-small-state

- Run ID: `cohort4_small`
- Files actually reported read: `SKILL.md`

**Prompt:** Review a Swift media control with enum State { case stopped, playing, paused } and one exhaustive switch containing one line per case.

**Response (verbatim):**

Pressure: The control has a closed set of three states and one trivial, exhaustive operation. There is no recurring variation, duplicated state-dependent behavior, or transition complexity to isolate.

Recommendation: No change. Keep the `State` enum and exhaustive switch.

Why: This is the clearest Swift-native representation. The enum makes invalid states unrepresentable, and the compiler verifies that the switch handles every case. Introducing the State pattern or separate state types would add indirection without solving an observed problem.

Costs and contraindications: The switch is appropriate while behavior remains small and centralized. Reconsider only if substantial state-specific behavior spreads across multiple switches, transitions acquire complex rules, or individual states need independent dependencies or testing.

Alternatives: None currently justified.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | The primary is no change: retain the small enum and exhaustive switch. |
| Swift-native alternative considered | Pass | The existing enum and switch are the Swift-native design. |
| GoF pattern rejected when unnecessary | Pass | State is rejected as needless indirection. |
| At most two alternatives | Pass | No lower-ranked alternative is recommended. |
| Costs and contraindications stated | Pass | Growth, duplicated behavior, transitions, dependencies, ownership, and indirection are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: only `SKILL.md` was read, which is correct for a no-change stop. |
| No unrelated references loaded | Pass | Pass from actual read evidence: no reference file was read. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed; attribution is not applicable. |

### Final cohort: greenfield-product-family

- Run ID: `cohort4_product`
- Files actually reported read: `SKILL.md`, `references/decision-index.md`, `references/creational/abstract-factory.md`

**Prompt:** Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.

**Response (verbatim):**

Pressure: Axis, legend, and renderer implementations must change together by backend. Letting callers choose each product independently permits invalid combinations such as an SVG axis with a Metal renderer.

Recommendation: Use an Abstract Factory, expressed as a Swift protocol with associated product types. Make the chart generic over the factory so compatibility is enforced by the type system rather than only by convention.

```swift
public protocol ChartAxis {
    associatedtype Target
    func draw(_ model: AxisModel, into target: inout Target)
}

public protocol ChartLegend {
    associatedtype Target
    func draw(_ model: LegendModel, into target: inout Target)
}

public protocol ChartRenderer {
    associatedtype Target
    func draw(_ series: [Series], into target: inout Target)
}

public protocol ChartBackend {
    associatedtype Target
    associatedtype Output
    associatedtype Axis: ChartAxis where Axis.Target == Target
    associatedtype Legend: ChartLegend where Legend.Target == Target
    associatedtype Renderer: ChartRenderer where Renderer.Target == Target

    func makeTarget(size: ChartSize) -> Target
    func makeAxis() -> Axis
    func makeLegend() -> Legend
    func makeRenderer() -> Renderer
    func finish(_ target: Target) -> Output
}

public struct Chart<Backend: ChartBackend> {
    private let backend: Backend
    private let axis: Backend.Axis
    private let legend: Backend.Legend
    private let renderer: Backend.Renderer

    public init(backend: Backend) {
        self.backend = backend
        self.axis = backend.makeAxis()
        self.legend = backend.makeLegend()
        self.renderer = backend.makeRenderer()
    }

    public func render(
        series: [Series],
        axisModel: AxisModel,
        legendModel: LegendModel,
        size: ChartSize
    ) -> Backend.Output {
        var target = backend.makeTarget(size: size)
        renderer.draw(series, into: &target)
        axis.draw(axisModel, into: &target)
        legend.draw(legendModel, into: &target)
        return backend.finish(target)
    }
}
```

Provide two complete families:

```swift
public struct SVGBackend: ChartBackend {
    public typealias Target = SVGDocument
    public typealias Output = String
    public typealias Axis = SVGAxis
    public typealias Legend = SVGLegend
    public typealias Renderer = SVGSeriesRenderer

    // makeTarget, makeAxis, makeLegend, makeRenderer, and finish
}

public struct MetalBackend: ChartBackend {
    public typealias Target = MetalRenderTarget
    public typealias Output = MetalTexture
    public typealias Axis = MetalAxis
    public typealias Legend = MetalLegend
    public typealias Renderer = MetalSeriesRenderer

    // makeTarget, makeAxis, makeLegend, makeRenderer, and finish
}
```

`Chart<SVGBackend>` can only receive products whose target is `SVGDocument`; `Chart<MetalBackend>` can only receive products whose target is `MetalRenderTarget`. Keep backend selection at the package composition root. If runtime selection is required, switch there and type-erase only the final rendered result or expose an enum wrapper around the two specialized charts; do not erase the product relationships inside `Chart`.

Why: The package has multiple stable product roles that must vary as one family. The factory gives clients one coherent backend choice, while associated types prevent accidental cross-family assembly at compile time. It also provides a complete-family seam for tests.

Costs and contraindications: Adding another product role requires updating every backend. Associated types make heterogeneous storage and runtime backend switching less direct. Keep factories immutable and `Sendable` where possible, but isolate Metal command buffers, encoders, and textures on the actor or executor required by their resource contract; the factory itself does not make GPU resources thread-safe. Avoid this design if only one product varies or if axis, legend, and renderer must vary independently.

Alternatives:

- A generic configuration value containing styles and drawing closures is smaller when the product roles are lightweight and backend selection is fixed at composition time, but it provides weaker named boundaries as each implementation grows.
- An enum switch at the composition root is simpler when SVG and Metal are a permanently closed, small set and callers never need to substitute whole families.

References:

- `references/decision-index.md`
- `references/creational/abstract-factory.md`
- Refactoring.Guru, “Abstract Factory in Swift”: https://refactoring.guru/design-patterns/abstract-factory/swift/example

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Abstract Factory is primary for axis, legend, and renderer implementations that must vary as one family. |
| Swift-native alternative considered | Pass | Associated types, a generic client, a configuration value, and a closed enum boundary are considered. |
| GoF pattern rejected when unnecessary | Pass | Abstract Factory is warranted; the response states conditions where simpler native composition is clearer. |
| At most two alternatives | Pass | Exactly two lower-ranked alternatives are named: generic configuration and an enum switch. |
| Costs and contraindications stated | Pass | Product-role growth, heterogeneous storage, actor isolation, independent variation, and thread safety are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: `references/decision-index.md` and `references/creational/abstract-factory.md` were read. |
| No unrelated references loaded | Pass | Pass from actual read evidence: the routing index and Abstract Factory guide are the only reference files read. |
| Attribution preserved when source guidance is discussed | Pass | The output separately cites both relative internal paths and the attributed Refactoring.Guru source. |

### Final cohort: review-scattered-coordination

- Run ID: `cohort4_coord`
- Files actually reported read: `SKILL.md`, `references/decision-index.md`, `references/structural/facade.md`

**Prompt:** Review three call sites that repeat file loading, format detection, decoding, metadata extraction, and persistence.

**Response (verbatim):**

Pressure: Three call sites repeat one cohesive import workflow—file loading, format detection, decoding, metadata extraction, and persistence. That scatters sequencing, validation, cancellation, and error policy across clients and makes them depend on subsystem details. No source for the call sites or collaborators was provided, so this is a provisional design review rather than a code-specific recommendation.

Recommendation: Introduce a focused Swift service as a Facade, named for the use case—for example, `DocumentImportService` with an `importFile(at:) async throws -> ImportedDocument` operation. Inject the loader, detector, decoders, metadata extractor, and store at initialization. Keep per-import intermediate state local, preserve typed errors and cancellation, and leave the lower-level components available to callers that genuinely need them.

Why: The repeated choreography is the abstraction. One domain-level entry point gives step ordering and failure policy a single owner, removes low-level coordination from all three call sites, and creates a direct test seam for the complete workflow. In Swift this does not require a class hierarchy or a type literally named `Facade`; a small struct or actor-backed service with explicit dependencies is enough.

Costs and contraindications: This adds an indirection layer and integration tests for the workflow. Protocols for every collaborator would create needless type and mock overhead, so introduce them only at I/O boundaries that actually need substitution; concrete value dependencies or injected closures may suffice elsewhere. Do not use this boundary if the call sites only look similar but require materially different ordering, persistence rules, or results. Do not turn it into a generic `Manager`, hide dependencies in singletons, swallow useful decoding or storage errors, detach work, or obscure actor-isolation requirements.

Alternatives:

- A free `importFile` function with injected closures—lower ceremony and preferable if this is a single, stateless use case with only a few dependencies, but it becomes awkward once dependency grouping, workflow policy, or multiple operations need a stable home.
- Template Method—lower-ranked because the stated pressure is duplicated coordination, not subclasses or variants that must preserve one invariant algorithm while overriding selected steps.

References:

- Internal guide: `references/structural/facade.md`
- Decision index: `references/decision-index.md`
- External source attributed by the guide: [Refactoring.Guru: Facade in Swift](https://refactoring.guru/design-patterns/facade/swift/example)

Next context or design step: Inspect the three call sites and the loader, detector, decoder selection, metadata, and persistence APIs before changing code. Confirm which steps and error policies are truly identical, what is actor-isolated, and whether decoding varies by closed format identity or by independently testable stateful strategies.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A focused Facade/service is primary, provisional on inspecting the actual review target. |
| Swift-native alternative considered | Pass | A small Swift service, concrete values or closures, and a free function are considered. |
| GoF pattern rejected when unnecessary | Pass | Facade is warranted by repeated choreography; Template Method is rejected for the stated pressure. |
| At most two alternatives | Pass | Exactly two alternatives are named: a free function and Template Method. |
| Costs and contraindications stated | Pass | Indirection, protocol overhead, divergent workflows, errors, tasks, isolation, and scope creep are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: `references/decision-index.md` and `references/structural/facade.md` were read. |
| No unrelated references loaded | Pass | Pass from actual read evidence: the routing index and Facade guide are the only reference files read. |
| Attribution preserved when source guidance is discussed | Pass | The output separately cites both relative internal paths and the attributed Refactoring.Guru source. |

### Final cohort: greenfield-undo

- Run ID: `cohort4_undo`
- Files actually reported read: `SKILL.md`, `references/decision-index.md`, `references/behavioral/command.md`, `references/behavioral/memento.md`

**Prompt:** Design reversible text edits that can be queued, replayed, undone, and redone.

**Response (verbatim):**

Pressure: Text edits must outlive the call that creates them: they need stable data for queueing and deterministic replay, plus enough information to reverse only successfully applied changes. History must remain coherent when an edit is stale or invalid, and one owner must serialize document mutation.

Recommendation: Use value-type Command objects. Model a closed edit vocabulary as a `TextEdit` value containing a coordinate, the text expected at that coordinate, and its replacement. Applying a command validates the receiver and returns the inverse command derived from the actual pre-edit state. A single history owner manages the pending queue, undo stack, redo stack, and replay log.

```swift
struct TextDocument: Equatable {
    private var storage: [Character]

    init(_ text: String) {
        storage = Array(text)
    }

    var text: String { String(storage) }

    mutating func apply(_ edit: TextEdit) throws -> TextEdit {
        guard edit.offset >= 0 else {
            throw EditError.invalidOffset(edit.offset)
        }

        let expected = Array(edit.removed)
        let replacement = Array(edit.inserted)
        let end = edit.offset + expected.count

        guard edit.offset <= storage.count, end <= storage.count else {
            throw EditError.invalidRange(
                offset: edit.offset,
                length: expected.count
            )
        }

        let range = edit.offset..<end
        let actual = Array(storage[range])
        guard actual == expected else {
            throw EditError.staleContent(
                expected: String(expected),
                actual: String(actual)
            )
        }

        storage.replaceSubrange(range, with: replacement)

        return TextEdit(
            offset: edit.offset,
            removed: edit.inserted,
            inserted: String(actual)
        )
    }
}

struct TextEdit: Equatable, Codable, Sendable {
    let offset: Int
    let removed: String
    let inserted: String
}

enum EditError: Error {
    case invalidOffset(Int)
    case invalidRange(offset: Int, length: Int)
    case staleContent(expected: String, actual: String)
}

struct TextEditSession {
    private(set) var document: TextDocument
    private(set) var replayLog: [TextEdit] = []

    private var pending: [TextEdit] = []
    private var undoStack: [TextEdit] = []
    private var redoStack: [TextEdit] = []

    mutating func enqueue(_ edit: TextEdit) {
        pending.append(edit)
    }

    mutating func perform(_ edit: TextEdit) throws {
        let inverse = try document.apply(edit)
        undoStack.append(inverse)
        redoStack.removeAll()
        replayLog.append(edit)
    }

    // All queued edits commit, or the document and queue remain unchanged.
    mutating func drainQueue() throws {
        var staged = self
        let edits = staged.pending
        staged.pending.removeAll()

        for edit in edits {
            try staged.perform(edit)
        }

        self = staged
    }

    // Replays atomically against the receiver's current state.
    mutating func replay(_ edits: [TextEdit]) throws {
        var staged = self

        for edit in edits {
            try staged.perform(edit)
        }

        self = staged
    }

    mutating func undo() throws {
        guard let inverse = undoStack.popLast() else { return }

        do {
            let redo = try document.apply(inverse)
            redoStack.append(redo)
        } catch {
            undoStack.append(inverse)
            throw error
        }
    }

    mutating func redo() throws {
        guard let edit = redoStack.popLast() else { return }

        do {
            let inverse = try document.apply(edit)
            undoStack.append(inverse)
        } catch {
            redoStack.append(edit)
            throw error
        }
    }
}
```

Why: A command is inspectable and serializable, unlike an opaque closure. The expected removed text acts as a precondition, so replay cannot silently modify the wrong content. Generating the inverse only after validation means failed edits never enter undo history. Undo and redo restore a popped command to its original stack if application fails. Staging a value-semantic session gives queue draining and batch replay all-or-nothing behavior through Swift copy-on-write.

Define the coordinate system as part of the command format. The example uses extended-grapheme-cluster offsets by storing the document as `[Character]`; a production editor would normally use a rope or piece table and a documented UTF-8/UTF-16 or stable-position scheme. Persisted replay also needs a format version and a known base-document identity or revision.

Costs and contraindications: Command adds explicit edit, history, validation, and ownership machinery. History consumes memory proportional to inserted and removed text, so bound it or coalesce adjacent typing commands. `Codable` makes the data encodable but does not by itself solve schema migration or durable storage. Keep mutation and history under one isolation domain—typically a `@MainActor` editor model for UI state or a dedicated actor for a document service. Do not use this design when edits are immediate, never inspected, and platform `UndoManager` already supplies all required grouping and responder-chain behavior.

Alternatives:

- `UndoManager` — lower-ranked when commands must also be queued, inspected, durably logged, or deterministically replayed; otherwise it may be the simpler choice for platform-integrated editing.
- Memento (or an ordinary value snapshot) — lower-ranked for localized text changes because whole-document checkpoints can retain substantially more memory. Prefer it when restoration must capture several coupled invariants that cannot be expressed safely as edit inverses.

References:

- `references/decision-index.md`
- `references/behavioral/command.md`
- `references/behavioral/memento.md`
- [Refactoring.Guru: Command in Swift](https://refactoring.guru/design-patterns/command/swift/example)
- [Refactoring.Guru: Memento in Swift](https://refactoring.guru/design-patterns/memento/swift/example)

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Command is primary for queueable, replayable, reversible edit identity. |
| Swift-native alternative considered | Pass | The implementation uses immutable Swift values and compares platform `UndoManager` and snapshots. |
| GoF pattern rejected when unnecessary | Pass | Command is warranted; `UndoManager` and Memento are limited to their clearer conditions. |
| At most two alternatives | Pass | Exactly two alternatives are named: `UndoManager` and Memento. |
| Costs and contraindications stated | Pass | Coordinates, validation, history memory, persistence, isolation, collaboration, and platform undo are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: the decision index, Command guide, and relevant Memento alternative guide were read. |
| No unrelated references loaded | Pass | Pass from actual read evidence: every read reference directly corresponds to routing, primary, or named alternative. |
| Attribution preserved when source guidance is discussed | Pass | The output cites all three relative paths and separately attributes both Refactoring.Guru sources. |

### Final cohort: review-event-stream

- Run ID: `cohort4_event`
- Files actually reported read: `SKILL.md`

**Prompt:** Review a Swift sensor service that manually maintains an array of observer objects only to broadcast typed readings.

**Response (verbatim):**

Pressure: The service owns a manual observer collection solely to fan out strongly typed sensor readings. That adds subscription bookkeeping, lifetime handling, mutation-during-broadcast hazards, and concurrency questions without buying meaningful domain abstraction.

Recommendation: Replace the observer array with a typed `AsyncSequence`—typically an `AsyncStream<Reading>` exposed by the service—when consumers process readings asynchronously. Give each subscriber its own stream/continuation, remove it on termination, and keep registration, broadcasting, and teardown inside one isolation domain, preferably the service actor.

Why: `AsyncSequence` expresses the actual contract directly: a typed stream of values over time. Consumers use `for await`, task cancellation supplies a natural unsubscribe mechanism, and actor isolation makes subscriber ownership and broadcast mutation explicit. Tests can consume a bounded prefix of readings without mock observer objects.

Costs and contraindications: The service must define buffering and dropped-reading policy, finish streams on shutdown, and clean up continuations when consumers cancel. A single shared `AsyncStream` is not automatically a broadcast channel; separate subscriber streams are required when every consumer must receive every reading. Avoid this approach when delivery must be synchronous, when callbacks must run inline before the producer continues, or when the project’s deployment/concurrency constraints prevent async consumption.

Alternatives: Observation — better when clients need the latest sensor state rather than every reading, but it does not naturally model lossless event history. Combine — reasonable when the project already depends on its operators or requires its scheduling/backpressure semantics, but otherwise adds a framework and a second concurrency model.

Next context or design step: Before changing the code, inspect the service and its consumers to confirm delivery ordering, buffering, cancellation, isolation, and whether each subscriber must receive every reading.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A typed `AsyncSequence`/`AsyncStream` is primary for asynchronous typed readings. |
| Swift-native alternative considered | Pass | AsyncSequence and Observation are preferred; Combine is conditional on an existing need. |
| GoF pattern rejected when unnecessary | Pass | A custom Observer is rejected in favor of native event/state tools. |
| At most two alternatives | Fail | Classic Observer is explicitly rejected, while Observation and Combine are also named; all three count under the global cap. |
| Costs and contraindications stated | Pass | Buffering, termination, multicast semantics, synchronous delivery, deployment, and isolation are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: only `SKILL.md` was read because the native event-stream answer stops before references. |
| No unrelated references loaded | Pass | Pass from actual read evidence: no reference file was read. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed; attribution is not applicable. |

### Final cohort: named-visitor

- Run ID: `cohort4_visitor`
- Files actually reported read: `SKILL.md`, `references/behavioral/visitor.md`

**Prompt:** Use Visitor for a closed Swift enum representing five expression cases and two operations.

**Response (verbatim):**

Pressure: The expression model has five closed cases and only two type-specific operations. The case set and operation set are both small, and Swift already provides exhaustive dispatch over the enum.

Recommendation: Do not use Visitor here. Keep the closed model as an `indirect enum`, and implement each operation with an exhaustive switch:

```swift
indirect enum Expression: Sendable {
    case number(Double)
    case variable(String)
    case add(Expression, Expression)
    case subtract(Expression, Expression)
    case multiply(Expression, Expression)
}

enum EvaluationError: Error {
    case unknownVariable(String)
}

func evaluate(
    _ expression: Expression,
    variables: [String: Double]
) throws -> Double {
    switch expression {
    case .number(let value):
        return value
    case .variable(let name):
        guard let value = variables[name] else {
            throw EvaluationError.unknownVariable(name)
        }
        return value
    case .add(let lhs, let rhs):
        return try evaluate(lhs, variables: variables)
            + evaluate(rhs, variables: variables)
    case .subtract(let lhs, let rhs):
        return try evaluate(lhs, variables: variables)
            - evaluate(rhs, variables: variables)
    case .multiply(let lhs, let rhs):
        return try evaluate(lhs, variables: variables)
            * evaluate(rhs, variables: variables)
    }
}

func format(_ expression: Expression) -> String {
    switch expression {
    case .number(let value):
        return String(value)
    case .variable(let name):
        return name
    case .add(let lhs, let rhs):
        return "(\(format(lhs)) + \(format(rhs)))"
    case .subtract(let lhs, let rhs):
        return "(\(format(lhs)) - \(format(rhs)))"
    case .multiply(let lhs, let rhs):
        return "(\(format(lhs)) * \(format(rhs)))"
    }
}
```

Why: Each switch exposes the full operation in one place, and the compiler identifies both operations when a sixth case is added. Visitor would recreate dispatch through protocols and `accept` methods without providing useful flexibility at this scale.

Costs and contraindications: Adding a case requires updating every operation, but that is desirable for a closed enum. Reconsider only if the five cases become genuinely stable while many independently owned operations are added. Keep mutable operation state local to one traversal; immutable `Sendable` expression values can safely cross concurrency boundaries when their associated values are also sendable.

Alternatives: Visitor — lower ranked because double dispatch, extra protocols, and return/error plumbing add ceremony for only two operations.

References:

- `references/behavioral/visitor.md`
- Attributed external source: [Refactoring.Guru: Visitor in Swift](https://refactoring.guru/design-patterns/visitor/swift/example)

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Visitor is challenged and rejected in favor of exhaustive enum switches. |
| Swift-native alternative considered | Pass | The primary uses an indirect enum, free functions, exhaustive switches, and Sendable values. |
| GoF pattern rejected when unnecessary | Pass | Visitor is explicitly rejected as unnecessary for two operations. |
| At most two alternatives | Pass | Visitor is the only lower-ranked alternative. |
| Costs and contraindications stated | Pass | Case growth, operation growth, double dispatch, errors, traversal state, and concurrency are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: `references/behavioral/visitor.md` was read through the named-pattern fast path. |
| No unrelated references loaded | Pass | Pass from actual read evidence: Visitor is the only reference file read. |
| Attribution preserved when source guidance is discussed | Pass | The output cites the relative Visitor path and separately attributes its Refactoring.Guru source. |

### Final cohort: review-no-change

- Run ID: `cohort4_nochange`
- Files actually reported read: `SKILL.md`

**Prompt:** Review a value-semantic configuration struct with a direct memberwise initializer and no branching creation logic.

**Response (verbatim):**

Pressure: No recurring creation pressure is present. The configuration is already value-semantic, construction is direct, and there is no branching logic or unstable creation boundary to isolate.

Recommendation: No change. Keep the struct and its direct memberwise initializer.

Why: The current design expresses the data and its construction plainly. Adding a creation pattern would introduce indirection without solving a concrete problem.

Costs and contraindications: The memberwise initializer couples call sites to the stored-property shape, which is appropriate while that shape is intentionally part of the configuration’s interface. Reconsider only if construction develops meaningful invariants, multiple branching creation paths, or a need to hide an unstable representation.

Alternatives: None.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | The primary is no change: retain the value struct and memberwise initializer. |
| Swift-native alternative considered | Pass | The existing value semantics and direct initializer are the Swift-native design. |
| GoF pattern rejected when unnecessary | Pass | Builder and factory abstractions are rejected as unjustified. |
| At most two alternatives | Pass | No alternative is recommended. |
| Costs and contraindications stated | Pass | Representation coupling, invariants, branching creation, and unstable representation are covered. |
| Correct detailed reference loaded | Pass | Pass from actual read evidence: only `SKILL.md` was read, which is correct for a no-change stop. |
| No unrelated references loaded | Pass | Pass from actual read evidence: no reference file was read. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed; attribution is not applicable. |

### Final cohort result

This frozen cohort passes **63/64 checks**. Actual read-list evidence shows
that all four native/no-change cases stopped after `SKILL.md`; Abstract
Factory and Facade loaded only the decision index plus their primary guide;
Command loaded the index plus Command and its discussed Memento alternative;
and the named Visitor fast path loaded only Visitor. No unrelated pattern guide
was reported read.

As a separate citation proxy, every final answer that loaded references used
portable relative internal paths and separately attributed the relevant
Refactoring.Guru source. Native/no-change answers omitted References as
required.

The event-stream alternative-count failure triggered one compact general
refinement and a complete fresh cohort below.


## Reproducible artifact-hash recipe

Run the following from the repository root. It includes every path for which
`Path.is_file()` is true under the skill root, including `SKILL.md`,
`agents/openai.yaml`, all references, and all scripts. It excludes files with
a `__pycache__` path component and files ending in `.pyc` or `.pyo`.
Tests and `.research` are outside the skill root and therefore excluded.

Files are sorted by their POSIX relative-path strings. For every file, SHA-256
receives: the UTF-8 path byte length as an unsigned 8-byte big-endian integer,
the path bytes, the content byte length in the same format, then the exact file
bytes. Length prefixes make the framing unambiguous.

```python
from pathlib import Path
from hashlib import sha256
from struct import pack

root = Path(
    "plugins/swift-design-patterns/skills/"
    "choosing-swift-design-patterns"
)
files = sorted(
    path for path in root.rglob("*")
    if path.is_file()
    and "__pycache__" not in path.parts
    and path.suffix not in {".pyc", ".pyo"}
)

digest = sha256()
for path in files:
    relative = path.relative_to(root).as_posix().encode("utf-8")
    content = path.read_bytes()
    digest.update(pack(">Q", len(relative)))
    digest.update(relative)
    digest.update(pack(">Q", len(content)))
    digest.update(content)

print(digest.hexdigest())
print(len(files))
```

The command prints
`076c2c4402d7df48bfc41ff1453c0bd532f7718d2aed61786840070196d13d6a`
and `29`. An independent Ruby implementation using `[length].pack("Q>")`
for the same frames produced the identical digest and file count.

A later pre-final cohort used the same reproducible recipe but was stopped after
six cases when event-stream still named the replaced Observer approach plus
Observation and Combine. That failure prompted the compact rule that the
replaced approach consumes an alternatives slot.

## Reproducible Final Cohort

This is the sole headline score. All eight fresh agents used the exact artifact
hashed above. Each received only its prompt, the skill directory, and the
operational request to write its answer and actual read list separately.

- Artifact SHA-256:
  `076c2c4402d7df48bfc41ff1453c0bd532f7718d2aed61786840070196d13d6a`
- Included distributable files: 29
- Pre-run commit: `83819f97a23c885fc93279e35de4be4691bf8cb2`
- Pre-run HEAD tree: `3a09bc3d7f00a8a90436a1ea60fb46e6a4b1f285`

Read lists are agent self-reports written separately from answers. They are
operational evidence, not independent proof against unreported tool activity.
Loading scores use these lists; portable citation behavior is a separate proxy.

### Reproducible final: greenfield-pricing

- Run ID: `cohort6_pricing`
- Files actually reported read: `SKILL.md`

**Prompt:** Design a Swift shipping calculator with three small interchangeable formulas selected at startup.

**Response (verbatim):**

Pressure: Three small, stateless, single-operation shipping formulas vary, but the choice is made once at startup. Each formula should be independently testable without adding unnecessary object structure.

Recommendation: Inject a Swift closure into a small `ShippingCalculator`. Keep startup configuration responsible only for selecting the closure.

```swift
import Foundation

struct Shipment {
    let weightInKilograms: Decimal
    let distanceInKilometers: Decimal
}

typealias ShippingFormula = (Shipment) -> Decimal

enum ShippingPlan: String {
    case flatRate
    case byWeight
    case byDistance
}

enum ShippingFormulas {
    static let flatRate: ShippingFormula = { _ in
        8
    }

    static let byWeight: ShippingFormula = { shipment in
        3 + shipment.weightInKilograms * 1.25
    }

    static let byDistance: ShippingFormula = { shipment in
        4 + shipment.distanceInKilometers * 0.05
    }
}

struct ShippingCalculator {
    private let formula: ShippingFormula

    init(formula: @escaping ShippingFormula) {
        self.formula = formula
    }

    func price(for shipment: Shipment) -> Decimal {
        formula(shipment)
    }
}

func makeShippingCalculator(plan: ShippingPlan) -> ShippingCalculator {
    let formula: ShippingFormula

    switch plan {
    case .flatRate:
        formula = ShippingFormulas.flatRate
    case .byWeight:
        formula = ShippingFormulas.byWeight
    case .byDistance:
        formula = ShippingFormulas.byDistance
    }

    return ShippingCalculator(formula: formula)
}

let startupPlan = ShippingPlan(rawValue: ProcessInfo.processInfo.environment["SHIPPING_PLAN"] ?? "")
    ?? .flatRate
let calculator = makeShippingCalculator(plan: startupPlan)
```

Why: A closure directly models one replaceable calculation. `ShippingPlan` gives startup decoding a closed, exhaustive identity, while the formulas remain ordinary values rather than being embedded in the enum. Tests can inject a stub such as `{ _ in 42 }` or exercise each production closure directly.

Costs and contraindications: The escaping closure adds one small level of indirection and captures must be considered if formulas later depend on mutable state. If pricing grows into behavior with multiple related operations, lifecycle, or substantial dependencies, this single-function boundary will become too narrow. If the calculator crosses concurrency domains, make the formula `@Sendable` and ensure captured dependencies are safe to share.

Alternatives:

- Strategy protocol — useful once each pricing policy needs several related operations or stored dependencies, but three tiny formulas do not justify three conforming types.
- Enum-owned switch — exhaustive and compact, but couples formula implementations to startup identity and makes isolated injection less direct.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | An injected closure is primary for the three small stateless startup-selected formulas. |
| Swift-native alternative considered | Pass | Closures, a value calculator, and an enum confined to startup identity are used. |
| GoF pattern rejected when unnecessary | Pass | Protocol Strategy is explicitly lower-ranked at the current scale. |
| At most two alternatives | Pass | Exactly two non-primary approaches are named: protocol Strategy and an enum-owned switch. |
| Costs and contraindications stated | Pass | Closure indirection, captures, state, lifecycle, dependencies, and Sendable are covered. |
| Correct detailed reference loaded | Pass | Actual read list: only `SKILL.md`; stopping before detailed references is correct. |
| No unrelated references loaded | Pass | Actual read list contains no reference file. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

### Reproducible final: review-small-state

- Run ID: `cohort6_small`
- Files actually reported read: `SKILL.md`

**Prompt:** Review a Swift media control with enum State { case stopped, playing, paused } and one exhaustive switch containing one line per case.

**Response (verbatim):**

Pressure: The media control has a closed set of three states and only one trivial, exhaustive dispatch point.

Recommendation: No change. Keep the `State` enum and its exhaustive `switch`.

Why: This is the clearest Swift-native representation. The enum expresses the closed state space, while the compiler verifies that every state is handled. One line per case provides no recurring complexity or variation that would justify additional abstraction.

Costs and contraindications: Reconsider only if state-specific behavior, transitions, dependencies, or testing needs grow enough that switches become large or duplicated. At the current size, extra types and indirection would make ownership and control flow harder to follow.

Alternatives: State pattern — ranks lower because it would replace three simple cases with reference-oriented objects and dispatch machinery without solving an observed problem.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | No change is primary; the enum and tiny exhaustive switch remain. |
| Swift-native alternative considered | Pass | The existing enum/switch is the Swift-native design. |
| GoF pattern rejected when unnecessary | Pass | State is rejected as needless reference-oriented dispatch. |
| At most two alternatives | Pass | State is the only non-primary approach named. |
| Costs and contraindications stated | Pass | Growth, duplication, transitions, dependencies, tests, ownership, and control flow are covered. |
| Correct detailed reference loaded | Pass | Actual read list: only `SKILL.md`; no-change correctly stops before references. |
| No unrelated references loaded | Pass | Actual read list contains no reference file. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

### Reproducible final: greenfield-product-family

- Run ID: `cohort6_product`
- Files actually reported read: `SKILL.md`, `references/decision-index.md`, `references/creational/abstract-factory.md`

**Prompt:** Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.

**Response (verbatim):**

Pressure: Axis, legend, and renderer vary together by backend. Allowing callers to choose those three products independently could create invalid SVG/Metal combinations, while Metal resource ownership must remain explicit.

Recommendation: Use an Abstract Factory with associated product types, and make the chart generic over that family. The associated-type constraints make family compatibility a compile-time invariant:

```swift
public protocol ChartAxis: Sendable {}
public protocol ChartLegend: Sendable {}

public enum ChartArtifact: Sendable {
    case svg(String)
    case metalFrame(MetalFrame)
}

public protocol ChartRenderer: Sendable {
    associatedtype Axis: ChartAxis
    associatedtype Legend: ChartLegend

    func render(
        values: [Double],
        axis: Axis,
        legend: Legend
    ) async throws -> ChartArtifact
}

public protocol ChartProductFamily: Sendable {
    associatedtype Axis: ChartAxis
    associatedtype Legend: ChartLegend
    associatedtype Renderer: ChartRenderer
        where Renderer.Axis == Axis, Renderer.Legend == Legend

    func makeAxis() -> Axis
    func makeLegend() -> Legend
    func makeRenderer() throws -> Renderer
}

public struct Chart<Family: ChartProductFamily>: Sendable {
    private let axis: Family.Axis
    private let legend: Family.Legend
    private let renderer: Family.Renderer

    public init(family: Family) throws {
        axis = family.makeAxis()
        legend = family.makeLegend()
        renderer = try family.makeRenderer()
    }

    public func render(_ values: [Double]) async throws -> ChartArtifact {
        try await renderer.render(values: values, axis: axis, legend: legend)
    }
}
```

Provide `SVGChartFamily` whose associated types are `SVGAxis`, `SVGLegend`, and `SVGRenderer`, and `MetalChartFamily` whose associated types are `MetalAxis`, `MetalLegend`, and `MetalRenderer`. Keep their concrete initializers internal where practical; public clients receive a complete `Chart<Family>` rather than assembling products. Select the family once in the package’s composition root. If runtime backend selection is required, erase or wrap the completed chart, not the three products separately, so compatibility has already been established.

Why: The package has a stable set of product roles and a backend axis that changes all of them together. One family object centralizes construction, and the `where` constraints prevent an SVG axis or legend from satisfying a Metal renderer’s associated types. Tests can inject a complete test family without exposing backend-specific construction throughout the charting code.

Costs and contraindications: Each backend adds a family and three concrete product types, and adding a new product role requires updating every family. Generics can increase signatures and code specialization; whole-chart erasure adds one boundary when runtime selection is needed. Metal GPU objects may be actor- or queue-confined, so isolate `MetalRenderer` (for example as an actor) and retain the `async` rendering boundary rather than assuming factory-created objects are automatically thread-safe. Do not use this structure if only one product varies, the roles change frequently, or incompatible combinations are actually valid.

Alternatives: An injected configuration value containing styles and rendering closures is shorter when there are only two permanently fixed backends and the products do not need distinct identities, dependencies, or isolation. It ranks lower here because it weakens the explicit family relationship and makes Metal resource ownership less visible.

References:

- `references/decision-index.md`
- `references/creational/abstract-factory.md`
- External source: [Refactoring.Guru: Abstract Factory in Swift](https://refactoring.guru/design-patterns/abstract-factory/swift/example)

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Abstract Factory is primary for three products that must vary as one compatible backend family. |
| Swift-native alternative considered | Pass | Associated types, generics, and a configuration value are considered. |
| GoF pattern rejected when unnecessary | Pass | Abstract Factory is warranted; direct composition conditions are stated without adding another named alternative. |
| At most two alternatives | Pass | Only one non-primary approach is named: an injected configuration value. |
| Costs and contraindications stated | Pass | Product-role growth, generics, erasure, Metal isolation, independent variation, and lifecycle are covered. |
| Correct detailed reference loaded | Pass | Actual read list contains the decision index and Abstract Factory guide. |
| No unrelated references loaded | Pass | The routing index and primary guide are the only reference files reported read. |
| Attribution preserved when source guidance is discussed | Pass | Both relative internal paths and the attributed Refactoring.Guru source are cited. |

### Reproducible final: review-scattered-coordination

- Run ID: `cohort6_coord`
- Files actually reported read: `SKILL.md`, `references/decision-index.md`, `references/structural/facade.md`

**Prompt:** Review three call sites that repeat file loading, format detection, decoding, metadata extraction, and persistence.

**Response (verbatim):**

Pressure: Three call sites repeat one cohesive workflow—file loading, format detection, decoding, metadata extraction, and persistence. That duplication couples each caller to subsystem details and invites drift in step ordering, validation, error handling, cancellation, and persistence policy. The call-site source was not provided, so this review cannot verify their exact dependency, ownership, or concurrency constraints.

Recommendation: Introduce a focused Facade, named in the application’s language (for example, `FileImportService`), with one operation such as `importFile(at:) async throws -> ImportedFile`. Inject the loader, detector, decoders, metadata extractor, and repository/store through its initializer. Let the service own workflow sequencing and error policy while keeping per-import mutable state local. Preserve meaningful typed errors and cancellation, and leave the lower-level collaborators directly available to advanced callers that genuinely need them.

Why: This is recurring subsystem choreography at three clients, not merely a shared one-line helper. A single entry point removes knowledge of the five-step pipeline from callers, gives ordering and failure behavior one authoritative home, and creates a practical test seam for the complete import use case. The individual components remain narrow and independently testable; the Facade composes them rather than absorbing all their logic.

Costs and contraindications: The service adds an indirection layer and a composition point, and tests may need fakes at real I/O boundaries. Avoid broad protocols for every dependency unless substitution is useful. Do not turn the service into a generic manager, hide dependencies behind global state, collapse errors to a Boolean, detach work in a way that loses cancellation, or force all clients through it if their workflows genuinely require different ordering or policies. If the implementation only forwards to one existing operation, the boundary is not earning its cost.

Alternatives:

- A free function with injected closures — smaller and suitable if the workflow is stateless, has a single operation, and needs no durable dependency-owning boundary; it ranks lower if the I/O collaborators and end-to-end policy need reusable configuration and focused integration tests.
- Keep direct coordination at each call site — lowest initial abstraction cost, but it preserves the observed duplication and policy-drift risk, so it no longer fits once the same five-step use case appears three times.

References:

- Internal guide: `references/decision-index.md`
- Internal guide: `references/structural/facade.md`
- Attributed external source: [Refactoring.Guru: Facade in Swift](https://refactoring.guru/design-patterns/facade/swift/example)

Next context or design step: Inspect the three call sites and the five collaborators before fixing the exact API, dependency types, actor isolation, and error model.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A focused Facade/service is primary, provisional on inspecting the actual review target. |
| Swift-native alternative considered | Pass | A focused Swift service, concrete dependencies, closures, and a free function are considered. |
| GoF pattern rejected when unnecessary | Pass | Facade is warranted by repeated choreography; keeping direct coordination is lower-ranked. |
| At most two alternatives | Pass | Exactly two non-primary approaches are named: a free function and direct coordination. |
| Costs and contraindications stated | Pass | Indirection, protocol overhead, workflow divergence, errors, cancellation, globals, and isolation are covered. |
| Correct detailed reference loaded | Pass | Actual read list contains the decision index and Facade guide. |
| No unrelated references loaded | Pass | The routing index and primary Facade guide are the only reference files reported read. |
| Attribution preserved when source guidance is discussed | Pass | Both relative internal paths and the attributed Refactoring.Guru source are cited. |

### Reproducible final: greenfield-undo

- Run ID: `cohort6_undo`
- Files actually reported read: `SKILL.md`, `references/decision-index.md`, `references/behavioral/command.md`

**Prompt:** Design reversible text edits that can be queued, replayed, undone, and redone.

**Response (verbatim):**

Pressure: Text edits must outlive the initiating call, execute in order, replay deterministically, and move safely through undo and redo history.

Recommendation: Use the Command pattern, represented by a value-type `TextEdit`. Model every insertion, deletion, and replacement as one replacement command containing a grapheme-cluster offset, the content expected at that location, and the replacement content. Applying a command validates the document before mutation and returns the exact inverse produced from the content actually removed.

```swift
struct TextDocument {
    private(set) var text: String

    mutating func replace(
        range: Range<String.Index>,
        with replacement: String
    ) -> String {
        let removed = String(text[range])
        text.replaceSubrange(range, with: replacement)
        return removed
    }
}

enum TextEditError: Error {
    case invalidRange
    case staleContent(expected: String, actual: String)
}

struct TextEdit: Codable, Equatable {
    /// Offset and lengths are measured in extended grapheme clusters.
    let offset: Int
    let removed: String
    let inserted: String

    func apply(to document: inout TextDocument) throws -> TextEdit {
        guard
            offset >= 0,
            let start = document.text.index(
                document.text.startIndex,
                offsetBy: offset,
                limitedBy: document.text.endIndex
            ),
            let end = document.text.index(
                start,
                offsetBy: removed.count,
                limitedBy: document.text.endIndex
            )
        else {
            throw TextEditError.invalidRange
        }

        let actual = String(document.text[start..<end])
        guard actual == removed else {
            throw TextEditError.staleContent(
                expected: removed,
                actual: actual
            )
        }

        let actualRemoved = document.replace(
            range: start..<end,
            with: inserted
        )
        return TextEdit(
            offset: offset,
            removed: inserted,
            inserted: actualRemoved
        )
    }
}

struct EditSession {
    private struct Entry {
        let forward: TextEdit
        var inverse: TextEdit
    }

    private(set) var document: TextDocument
    private var queue: [TextEdit] = []
    private var timeline: [Entry] = []
    private var cursor = 0

    mutating func enqueue(_ edit: TextEdit) {
        queue.append(edit)
    }

    /// Stops at the first invalid or stale command. A failing command stays queued.
    mutating func executeNext() throws {
        guard let edit = queue.first else { return }
        try perform(edit)
        queue.removeFirst()
    }

    mutating func perform(_ edit: TextEdit) throws {
        let inverse = try edit.apply(to: &document)

        // A new branch after undo invalidates the old redo suffix.
        timeline.removeSubrange(cursor..<timeline.endIndex)
        timeline.append(Entry(forward: edit, inverse: inverse))
        cursor += 1
    }

    mutating func undo() throws {
        guard cursor > 0 else { return }
        let inverse = timeline[cursor - 1].inverse
        _ = try inverse.apply(to: &document)
        cursor -= 1
    }

    mutating func redo() throws {
        guard cursor < timeline.count else { return }
        let forward = timeline[cursor].forward
        let refreshedInverse = try forward.apply(to: &document)
        timeline[cursor].inverse = refreshedInverse
        cursor += 1
    }

    /// Replays the currently applied prefix against the same known base revision.
    func replay(on base: TextDocument) throws -> TextDocument {
        var result = base
        for entry in timeline.prefix(cursor) {
            _ = try entry.forward.apply(to: &result)
        }
        return result
    }
}
```

Why: The command has inspectable identity and data, so it can be queued, encoded, logged, and replayed. One timeline plus a cursor makes undo/redo branching explicit: undo moves the cursor backward, redo reapplies the forward command, and a newly performed edit discards only the abandoned redo suffix. State changes and history changes are transactional—history advances only after `apply` succeeds. The expected-content guard prevents a stale offset from editing unrelated text.

Costs and contraindications: The session must be the single owner of document mutation and command ordering; a UI-backed version should normally be main-actor isolated. Integer traversal of `String` is not suitable for a large editor, so production code should use a rope or text-buffer coordinate system while preserving the same validation contract. Replay requires the same base document revision (or a verified base hash), and persisted commands need a versioned coordinate convention. History consumes memory proportional to retained inserted and removed text, so define coalescing and retention limits. This design is excessive when edits are immediate and neither history nor replay is required.

Alternative: Foundation `UndoManager` ranks lower here. It is attractive when responder-chain integration, grouping, and native menu behavior are the main requirements, but explicit command values are clearer for durable queueing, validation, inspection, and deterministic replay.

References:

- `references/decision-index.md`
- `references/behavioral/command.md`
- Attributed external source: [Refactoring.Guru: Command in Swift](https://refactoring.guru/design-patterns/command/swift/example)

Next design step: Specify the production text buffer’s coordinate system, base-revision identity, command serialization version, edit-coalescing rules, and whether queued execution must be actor-isolated.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Command is primary for queued, replayable, reversible edit identity. |
| Swift-native alternative considered | Pass | Immutable Swift values and Foundation `UndoManager` are considered. |
| GoF pattern rejected when unnecessary | Pass | Command is warranted; `UndoManager` is limited to its clearer platform-integration case. |
| At most two alternatives | Pass | `UndoManager` is the only non-primary approach named. |
| Costs and contraindications stated | Pass | Coordinates, validation, history, replay bases, persistence, memory, isolation, and scale are covered. |
| Correct detailed reference loaded | Pass | Actual read list contains the decision index and Command guide. |
| No unrelated references loaded | Pass | The routing index and primary Command guide are the only reference files reported read. |
| Attribution preserved when source guidance is discussed | Pass | Both relative internal paths and the attributed Refactoring.Guru source are cited. |

### Reproducible final: review-event-stream

- Run ID: `cohort6_event`
- Files actually reported read: `SKILL.md`

**Prompt:** Review a Swift sensor service that manually maintains an array of observer objects only to broadcast typed readings.

**Response (verbatim):**

Pressure: The service owns observer registration, removal, lifetime, and broadcast logic even though its only job is to deliver typed sensor readings.

Recommendation: Replace the manual observer array with a typed `AsyncSequence`, typically an `AsyncStream<SensorReading>` exposed by the service. Each consumer can iterate independently in its own task, and cancellation provides a natural subscription lifetime.

Why: This is a typed event stream with asynchronous consumers, so Swift’s structured-concurrency model expresses the actual pressure directly. It removes the observer protocol and broadcast loop, keeps readings strongly typed, and makes consumption and cancellation explicit.

Costs and contraindications: The service must define buffering and multi-subscriber behavior, retain and finish continuations correctly, and decide actor isolation for producer state. Consumer tasks must be cancelled deliberately. Do not make this change if the reading represents only current observable state rather than a stream of events.

Alternatives: Observation — preferable only when clients need the latest sensor state and do not need every reading.

Next context or design step: Before changing existing code, inspect the sensor service and its consumers to confirm delivery ordering, buffering, subscriber count, cancellation, and actor-isolation requirements.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | A typed `AsyncSequence`/`AsyncStream` is primary for asynchronous typed readings. |
| Swift-native alternative considered | Pass | AsyncSequence is primary and Observation is considered for current state. |
| GoF pattern rejected when unnecessary | Pass | The existing manual Observer approach is replaced by the native stream. |
| At most two alternatives | Pass | Exactly two non-primary approaches are named: the replaced Observer approach and Observation. |
| Costs and contraindications stated | Pass | Buffering, fan-out, continuations, cancellation, state semantics, and isolation are covered. |
| Correct detailed reference loaded | Pass | Actual read list: only `SKILL.md`; the native solution correctly stops before references. |
| No unrelated references loaded | Pass | Actual read list contains no reference file. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

### Reproducible final: named-visitor

- Run ID: `cohort6_visitor`
- Files actually reported read: `SKILL.md`, `references/behavioral/visitor.md`

**Prompt:** Use Visitor for a closed Swift enum representing five expression cases and two operations.

**Response (verbatim):**

Pressure: Model five expression variants and two type-specific operations while preserving exhaustive handling of every case.

Recommendation: Do not use Visitor here. Keep the closed family as an `indirect enum` and implement each operation with an exhaustive switch:

```swift
indirect enum Expression {
    case number(Double)
    case variable(String)
    case add(Expression, Expression)
    case subtract(Expression, Expression)
    case multiply(Expression, Expression)
}

enum EvaluationError: Error {
    case unknownVariable(String)
}

extension Expression {
    func evaluate(using variables: [String: Double]) throws -> Double {
        switch self {
        case .number(let value):
            return value
        case .variable(let name):
            guard let value = variables[name] else {
                throw EvaluationError.unknownVariable(name)
            }
            return value
        case .add(let left, let right):
            return try left.evaluate(using: variables)
                + right.evaluate(using: variables)
        case .subtract(let left, let right):
            return try left.evaluate(using: variables)
                - right.evaluate(using: variables)
        case .multiply(let left, let right):
            return try left.evaluate(using: variables)
                * right.evaluate(using: variables)
        }
    }

    var formatted: String {
        switch self {
        case .number(let value):
            return value.formatted()
        case .variable(let name):
            return name
        case .add(let left, let right):
            return "(\(left.formatted) + \(right.formatted))"
        case .subtract(let left, let right):
            return "(\(left.formatted) - \(right.formatted))"
        case .multiply(let left, let right):
            return "(\(left.formatted) * \(right.formatted))"
        }
    }
}
```

Why: Swift already provides exact, compiler-checked dispatch over a closed enum. With only two operations, exhaustive switches expose the behavior directly and ensure that adding a sixth case produces a compile-time error at every operation that must be updated. Visitor would recreate information the enum switch already has.

Costs and contraindications: Each operation repeats the case list, and operation-specific dependencies live in enum extensions unless moved into free functions. This design becomes less attractive if the five cases are genuinely frozen while many independently developed tooling operations accumulate. Stateful operations should keep traversal state local to one call or owner.

Alternatives: Visitor — consider it only if the expression family remains stable and the number of cross-cutting operations grows substantially; it adds visitor interfaces, double-dispatch plumbing, and a requirement to update every visitor when a case is added.

References:

- `references/behavioral/visitor.md`
- Refactoring.Guru, [Visitor in Swift](https://refactoring.guru/design-patterns/visitor/swift/example)

Next context or design step: Confirm whether operations are expected to grow much faster than expression cases. If not, keep the exhaustive-switch design.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | Visitor is challenged and rejected in favor of exhaustive enum switches. |
| Swift-native alternative considered | Pass | An indirect enum, exhaustive switches, extensions, and free functions are considered. |
| GoF pattern rejected when unnecessary | Pass | Visitor is explicitly rejected as unnecessary for two operations. |
| At most two alternatives | Pass | Visitor is the only non-primary approach named. |
| Costs and contraindications stated | Pass | Case growth, operation growth, dependencies, traversal state, errors, and concurrency are covered. |
| Correct detailed reference loaded | Pass | Actual read list contains only the direct Visitor guide, matching the named-pattern fast path. |
| No unrelated references loaded | Pass | No unrelated routing or pattern guide is reported read. |
| Attribution preserved when source guidance is discussed | Pass | The relative Visitor path and attributed Refactoring.Guru source are cited. |

### Reproducible final: review-no-change

- Run ID: `cohort6_nochange`
- Files actually reported read: `SKILL.md`

**Prompt:** Review a value-semantic configuration struct with a direct memberwise initializer and no branching creation logic.

**Response (verbatim):**

Pressure: None. The configuration has value semantics, direct construction, and no varying or branching creation behavior.
Recommendation: No change. Keep the struct and its memberwise initializer.
Why: The existing Swift-native design is already explicit, compact, and easy to test. A creation pattern would add indirection without solving a recurring problem.
Costs and contraindications: No added abstraction cost. Reconsider only if construction later gains multiple validated paths, hidden dependencies, or recurring conditional assembly that the initializer cannot express clearly.
Alternatives (0–2): None.

| Rubric item | Result | Rationale |
|---|---|---|
| Correct primary recommendation | Pass | No change is primary; the value struct and memberwise initializer remain. |
| Swift-native alternative considered | Pass | The existing value semantics and initializer are the Swift-native design. |
| GoF pattern rejected when unnecessary | Pass | Creation patterns are rejected as unjustified. |
| At most two alternatives | Pass | No non-primary approach is recommended. |
| Costs and contraindications stated | Pass | Representation coupling, invariants, branching paths, and unstable representation are covered. |
| Correct detailed reference loaded | Pass | Actual read list: only `SKILL.md`; no-change correctly stops before references. |
| No unrelated references loaded | Pass | Actual read list contains no reference file. |
| Attribution preserved when source guidance is discussed | Pass | No source guidance is discussed, so attribution is not applicable. |

### Reproducible final result

The single-artifact final cohort passes **64/64 checks**. Actual read lists show
that the four native/no-change cases opened only `SKILL.md`; Abstract Factory,
Facade, and Command opened only the routing index plus their primary guide; and
the named Visitor fast path opened only Visitor. No unrelated reference was
reported read.

As a separate response proxy, every answer that loaded a guide cited portable
relative paths and the attributed Refactoring.Guru source. Native/no-change
answers omitted References. The final artifact hash was reproduced independently
with the documented Python and Ruby implementations.
