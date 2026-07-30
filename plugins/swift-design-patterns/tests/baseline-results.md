# Baseline Swift Pattern Selection Results

The responses below were captured before `choosing-swift-design-patterns`
existed. Each case records the unedited response followed by observed failure
classes chosen from: pattern overuse, missed Swift-native alternative,
incorrect pattern, weak contraindication, missing trade-off, or acceptable.

## greenfield-pricing

**Prompt:** Design a Swift shipping calculator with three small interchangeable formulas selected at startup.

**Response:**

Recommendation: use a small Strategy seam, selected once at the composition root and injected into `ShippingCalculator`.

```swift
struct Shipment {
    let weight: Decimal
    let distance: Decimal
}

struct ShippingQuote {
    let amount: Decimal
    let currency: Currency
}

protocol ShippingFormula: Sendable {
    func quote(for shipment: Shipment) throws -> ShippingQuote
}

struct FlatRateFormula: ShippingFormula { /* … */ }
struct WeightBasedFormula: ShippingFormula { /* … */ }
struct DistanceBasedFormula: ShippingFormula { /* … */ }

struct ShippingCalculator {
    private let formula: any ShippingFormula

    init(formula: any ShippingFormula) {
        self.formula = formula
    }

    func quote(for shipment: Shipment) throws -> ShippingQuote {
        try formula.quote(for: shipment)
    }
}
```

At startup, decode a configuration enum, construct the corresponding formula, and inject it. Keep selection logic out of `ShippingCalculator`; it should never switch on formula type. Validate negative or unsupported inputs consistently, and use `Decimal` or a dedicated `Money` type rather than `Double`.

Why this is the best fit: three adapters make the seam real, each formula is independently testable, startup selection is immutable, and adding a fourth formula does not modify callers. The cost is a protocol plus several small types, which is modest but can feel ceremonial when formulas are only one line.

Alternatives:

1. Inject a `@Sendable (Shipment) throws -> ShippingQuote` closure. This has the smallest interface and excellent testability. Trade-off: named formula types, shared dependencies, and diagnostics become less discoverable as formulas grow.

2. Store a `ShippingPlan` enum and switch inside `quote`. This is the simplest closed-world design and makes exhaustive handling explicit. Trade-off: every new formula requires editing the central switch, so extension and formula-specific dependencies become progressively awkward.

**Observed failure classes:** pattern overuse

## review-small-state

**Prompt:** Review a Swift media control with enum State { case stopped, playing, paused } and one exhaustive switch containing one line per case.

**Response:**

Recommendation: keep the enum and exhaustive `switch` as-is. With three mutually exclusive states and one line per case, it is the clearest and smallest design; the compiler enforces handling when a new state is added. Trade-off: the mapping remains at the call site, which only becomes an issue if it is duplicated.

Alternatives:

1. Move the switch into a computed property or method on `State` if multiple callers need the same mapping. This centralizes behavior, but can couple the domain state to UI-specific details.

2. Introduce a reducer/state-machine abstraction only if transitions, side effects, or invalid transitions become substantial. It improves testability at scale, but is unnecessary ceremony for the current control.

**Observed failure classes:** acceptable

## greenfield-product-family

**Prompt:** Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.

**Response:**

Recommendation: use a type-safe Abstract Factory.

Define a `ChartBackend` module whose associated product types are `Axis`, `Legend`, and `Renderer`. Implement `SVGBackend` and `MetalBackend` adapters, select one family at chart composition, and preserve that backend type through construction. This prevents mixing an SVG axis with a Metal renderer at compile time.

Trade-offs:

- Strong compatibility guarantees and localized backend knowledge.
- Adding a backend is straightforward.
- Adding a new product category requires updating every backend family.
- Runtime backend selection may require type erasure at the outermost seam.

Alternatives:

1. Backend-neutral scene graph with only SVG and Metal renderer adapters. This creates a deeper, smaller interface and is easiest to test, but works only if axis and legend behavior can remain genuinely backend-neutral.

2. Central backend enum with switches that construct concrete products. This is simpler for two permanently fixed backends, but compatibility relies more on convention, switches spread as the package grows, and extension by third parties is difficult.

Avoid independently injected axis, legend, and renderer interfaces: they allow invalid mixed-backend families unless another compatibility mechanism is added.

**Observed failure classes:** acceptable

## review-scattered-coordination

**Prompt:** Review three call sites that repeat file loading, format detection, decoding, metadata extraction, and persistence.

**Response:**

Recommendation: introduce a focused `MediaImportService` Facade with one operation that owns loading, format detection, decoding, metadata extraction, and persistence. Three duplicated orchestration sequences indicate the workflow—not any individual step—is the missing abstraction. Keep the underlying loaders, decoders, and repository independently testable.

Alternatives:

- Extract a shared function if the workflow is fixed and dependencies are simple. This has less indirection, but becomes awkward once dependencies, error policy, or format-specific behavior vary.
- Use a pipeline/Template Method only if callers need to replace or reorder stages. It offers flexibility, but adds unnecessary abstractions for one stable workflow.

Trade-offs: the Facade adds a type and can become a vague “manager” if allowed to absorb unrelated responsibilities. Give it a narrow import-specific API, inject its collaborators, and preserve stage-specific errors where callers need them.

**Observed failure classes:** acceptable

## greenfield-undo

**Prompt:** Design reversible text edits that can be queued, replayed, undone, and redone.

**Response:**

Recommend an immutable, validated patch log behind one `TextTimeline` module.

Each `TextTransaction` records:

- Document ID and base revision/hash
- Non-overlapping replacements: `{ range, expectedOldText, newText }`
- Optional grouping metadata for typing bursts or composite actions

The module atomically validates expected text, applies replacements from highest offset downward, and stores both the normalized forward patch and its computed inverse. Undo applies the inverse; redo reapplies the original. New edits clear redo. Queued edits form a revision chain against the projected queue-tail state, and replay applies forward patches from the identified baseline.

This is deterministic, serializable, atomic, and stores only changed text. Its main constraint is intentional: stale edits are rejected unless explicit rebasing exists.

Alternatives:

1. Full before/after snapshots: simplest correctness, but memory-heavy and poor for inspection or merging.
2. OT/CRDT or stable-character IDs: handles concurrent external edits, but adds substantial metadata, complexity, and harder undo semantics. Best reserved for true multi-writer editing.

**Observed failure classes:** incorrect pattern

## review-event-stream

**Prompt:** Review a Swift sensor service that manually maintains an array of observer objects only to broadcast typed readings.

**Response:**

Recommendation: replace the observer array with a Combine interface:

```swift
var readings: AnyPublisher<Reading, Never>
```

Back it with a private `PassthroughSubject<Reading, Never>`—or `CurrentValueSubject` only if new subscribers must immediately receive the latest reading. This preserves typed multicast delivery while removing registration, weak-reference cleanup, and mutation-during-broadcast logic from the module’s interface. Keep sensor callbacks and subject sends on one documented actor or serial executor.

Alternatives:

- `func readings() -> AsyncStream<Reading>`: preferable when consumers are already async/await. Return a fresh stream per subscriber; a single shared `AsyncStream` is not broadcast and may divide readings among consumers. Cancellation and buffering are explicit, but true multicast still requires a continuation registry or broadcast utility.
- A single weak delegate: smallest interface when exactly one consumer is legitimate. It avoids framework coupling but cannot support independent consumers without recreating the observer mechanism.

Trade-off: Combine is the cleanest built-in typed multicast abstraction, but introduces Combine and subscription-lifetime management. `AsyncStream` integrates better with structured concurrency but is not natively multicast. A delegate is simplest only if the one-consumer invariant is real.

**Observed failure classes:** acceptable

## named-visitor

**Prompt:** Use Visitor for a closed Swift enum representing five expression cases and two operations.

**Response:**

Recommendation: use a generic Visitor when expression cases are stable and operations are expected to grow.

```swift
protocol ExpressionVisitor {
    associatedtype Result

    func visitLiteral(_ value: Double) -> Result
    func visitAdd(_ lhs: Expression, _ rhs: Expression) -> Result
    func visitSubtract(_ lhs: Expression, _ rhs: Expression) -> Result
    func visitMultiply(_ lhs: Expression, _ rhs: Expression) -> Result
    func visitNegate(_ expression: Expression) -> Result
}

indirect enum Expression {
    case literal(Double)
    case add(Expression, Expression)
    case subtract(Expression, Expression)
    case multiply(Expression, Expression)
    case negate(Expression)

    func accept<V: ExpressionVisitor>(_ visitor: V) -> V.Result {
        switch self {
        case .literal(let value):
            visitor.visitLiteral(value)
        case .add(let lhs, let rhs):
            visitor.visitAdd(lhs, rhs)
        case .subtract(let lhs, let rhs):
            visitor.visitSubtract(lhs, rhs)
        case .multiply(let lhs, let rhs):
            visitor.visitMultiply(lhs, rhs)
        case .negate(let expression):
            visitor.visitNegate(expression)
        }
    }
}
```

Implement the two operations as separate adapters, such as `EvaluateVisitor` and `FormatVisitor`. The generic `Result` keeps the interface type-safe without erasure. Adding an operation is local; adding an expression case requires updating the protocol, `accept`, and every visitor. This is the right trade when the five cases are genuinely closed.

Alternatives:

- Enum switches in each operation: simplest and most idiomatic for only two operations. Exhaustive and low ceremony, but traversal knowledge becomes duplicated as operations grow.
- A generic `fold`/algebra: centralizes traversal behind a smaller, deeper interface and is excellent for pure recursive operations. It is less familiar, closure-heavy with five cases, and can become awkward for operations needing node context or custom traversal.

**Observed failure classes:** pattern overuse

## review-no-change

**Prompt:** Review a value-semantic configuration struct with a direct memberwise initializer and no branching creation logic.

**Response:**

Recommendation: keep the value-semantic struct and direct memberwise initializer unchanged. With no invariants, branching, or hidden creation behavior, an added seam would be shallow and increase the interface without providing leverage.

Alternatives:

1. Add named static factory methods only if recurring presets or domain-significant configurations emerge. This improves call-site intent but duplicates or obscures straightforward initialization.
2. Introduce a builder only if construction becomes staged, highly optional, or validation-heavy. It can improve ergonomics then, but currently adds state, boilerplate, and a larger test surface for no behavioral gain.

**Observed failure classes:** acceptable
