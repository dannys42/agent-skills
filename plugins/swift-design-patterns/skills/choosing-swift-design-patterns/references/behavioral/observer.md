# Observer

## Intent

Let interested consumers react when a subject changes without the subject naming each consumer’s concrete type. In modern Swift, the important decision is usually which native observation or stream mechanism expresses delivery, lifetime, and backpressure most clearly.

## Prefer Swift-native alternatives when

Use Observation for UI-facing state whose readers should invalidate when accessed properties change. Use one direct callback for a single owner-child event. Choose `AsyncStream` for typed values consumed over time with structured `for await` syntax. Foundation notifications remain useful for loosely coupled process-wide signals, especially existing framework events, but their stringly or global character is often unnecessary for a local feature.

## Choose this pattern when

Choose an explicit Observer abstraction when multiple heterogeneous subscribers need controlled registration, delivery, and removal semantics that native facilities do not provide. Examples include priorities, filtered subscriptions, synchronous transactional delivery, or a domain-specific subscription token. The pattern is about one-to-many change propagation; a manual array of observer objects is not automatically better than an `AsyncSequence`.

## Avoid it when

Avoid broadcasting when one direct dependency is clearer. Do not conceal important control flow behind global notifications. Unbounded async buffering can turn a slow consumer into a memory problem, while dropping values may be incorrect for audit events. A subject that retains observers strongly can leak them. Observation is not an event log: repeated equal assignments, intermediate states, and access tracking have different semantics from a stream of readings.

## Design pressures

Identify whether consumers need current state or every event, synchronous or asynchronous delivery, one or many subscribers, and replay for late subscribers. Specify ordering, buffering, error completion, and terminal behavior. A sensor reading stream may tolerate keeping only recent values, whereas financial transactions may not tolerate drops.

## Swift implementation

Prefer a typed stream over a custom callback registry when values arrive asynchronously. Make producer ownership explicit, select a buffering policy, inspect `yield` results if drops matter, and call `finish()` on shutdown. Each independent subscriber generally needs its own stream and continuation; sharing one stream among consumers distributes iteration rather than necessarily broadcasting every value.

## Concurrency and ownership

Values crossing tasks or actors should be `Sendable`. A continuation is thread-safe to yield through, but the owner must define who finishes it and release subscriber bookkeeping on termination. Consumer cancellation ends that iteration; it does not automatically stop an unrelated producer. Avoid creating unstructured tasks inside the stream solely to hide ownership. Verify default actor isolation and strict-concurrency settings before exposing a stream from an unknown module.

## Compare

Observation tracks reads of state for reactive invalidation. `AsyncStream` models asynchronously delivered values with explicit completion and buffering. Notifications broadcast through a shared center and fit broad framework signals. Callbacks are ideal for one narrow relationship. Mediator owns collaboration rules among peers; Observer only announces change and leaves reactions to subscribers.

## Example

```swift
struct SensorReading: Sendable, Equatable {
    let sensorID: String
    let celsius: Double
}

struct SensorPipe: Sendable {
    let readings: AsyncStream<SensorReading>
    private let continuation: AsyncStream<SensorReading>.Continuation

    init(bufferLimit: Int) {
        (readings, continuation) = AsyncStream.makeStream(
            of: SensorReading.self,
            bufferingPolicy: .bufferingNewest(bufferLimit)
        )
    }

    @discardableResult
    func publish(_ reading: SensorReading)
        -> AsyncStream<SensorReading>.Continuation.YieldResult {
        continuation.yield(reading)
    }

    func finish() {
        continuation.finish()
    }
}

func collectTemperatures(
    from stream: AsyncStream<SensorReading>
) async -> [Double] {
    var temperatures: [Double] = []
    for await reading in stream {
        temperatures.append(reading.celsius)
    }
    return temperatures
}

let pipe = SensorPipe(bufferLimit: 8)
_ = pipe.publish(SensorReading(sensorID: "greenhouse", celsius: 21.4))
pipe.finish()
```

The producer-owned pipe exposes typed readings, a finite newest-value buffer, and explicit completion. It represents one stream; a broadcast service would create and track a continuation per subscriber and remove it when that subscriber terminates.

## Review checklist

- Do consumers need state observation or an event stream?
- Would one typed callback express the relationship?
- Are delivery order and execution context defined?
- Is buffering bounded, and are dropped values acceptable?
- Who finishes the producer and removes cancelled subscribers?
- Are emitted values safe across isolation boundaries?
- Would a mediator be more appropriate for coordinated reactions?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Observer in Swift](https://refactoring.guru/design-patterns/observer/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
