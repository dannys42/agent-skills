# State

## Intent

Move state-specific behavior behind state representations so an object’s response changes with its lifecycle state. The pattern is useful when transitions and behavior have outgrown one readable exhaustive switch.

## Prefer Swift-native alternatives when

Start with an enum and exhaustive `switch`. It makes a closed state space visible, prevents forgotten cases, and often expresses a small lifecycle more clearly than several types. Associated values can carry state-specific data. A table-driven transition function returning a new enum is another compact choice when behavior is mostly validation.

## Choose this pattern when

Choose State when each state has substantial behavior, transitions differ by state, and a growing central switch changes for unrelated reasons. A connection lifecycle might have disconnected, connecting, awaiting-authentication, ready, and failed states, each interpreting events differently and carrying distinct dependencies. Separate state objects can localize those policies while the connection context presents one stable API.

## Avoid it when

Avoid the pattern for three cases with one-line branches. Do not replace compiler-checked exhaustiveness with an open class hierarchy without a real extension need. State objects should not secretly mutate the context from many directions or create transition cycles that are hard to trace. If behavior varies independently of lifecycle and callers select it, Strategy is a better fit.

## Design pressures

Look for repeated switches over the same state in several methods, invalid combinations of flags, state-specific data that is optional everywhere, and transitions that need isolated tests. Determine whether the state set is closed. Closed domains favor enums longer than traditional object-oriented examples imply; use the pattern only when behavioral cohesion repays indirection.

## Swift implementation

An enum can still implement the State pattern’s intent. Give it a transition method that consumes an event and returns a new state, keeping transition logic with lifecycle representation. If concrete state types become necessary, keep the context as transition owner and avoid bidirectional strong references. Model impossible transitions with thrown errors or explicit unchanged results.

## Concurrency and ownership

One isolation domain must own current state. An actor is appropriate for a connection shared among tasks; UI state may belong to the main actor. Never read state, suspend, and then commit a transition without considering reentrancy: another event may have changed it. State and event payloads crossing actors should be `Sendable`. Do not apply `@MainActor` merely because the type is called a state model.

## Compare

An enum switch is the preferred closed-state representation until branches become unwieldy. Strategy swaps interchangeable algorithms selected by a client or configuration; State changes behavior as the object transitions during its lifetime. Command represents events as executable values, while State determines how lifecycle events are interpreted.

## Example

```swift
enum ConnectionEvent {
    case connect
    case transportReady
    case authenticate(token: String)
    case fail(message: String)
    case disconnect
}

enum ConnectionState: Equatable {
    case disconnected
    case connecting
    case awaitingAuthentication
    case ready(userToken: String)
    case failed(message: String)

    func transition(for event: ConnectionEvent) -> ConnectionState {
        switch (self, event) {
        case (.disconnected, .connect):
            return .connecting
        case (.connecting, .transportReady):
            return .awaitingAuthentication
        case (.awaitingAuthentication, .authenticate(let token)):
            return .ready(userToken: token)
        case (_, .fail(let message)):
            return .failed(message: message)
        case (_, .disconnect):
            return .disconnected
        default:
            return self
        }
    }

    var canSendMessages: Bool {
        if case .ready = self {
            return true
        }
        return false
    }
}

struct Connection {
    private(set) var state: ConnectionState = .disconnected

    mutating func receive(_ event: ConnectionEvent) {
        state = state.transition(for: event)
    }
}

var connection = Connection()
connection.receive(.connect)
connection.receive(.transportReady)
connection.receive(.authenticate(token: "session-42"))
print(connection.state.canSendMessages)
```

Transport readiness now advances to an explicit authentication phase, and credentials presented before that phase are ignored. This closed lifecycle stays clearest as an enum: transitions are exhaustive at the representation boundary and state-specific data cannot appear in unrelated cases. Split it into concrete state types only if each case gains enough behavior and dependencies to justify that indirection.

## Review checklist

- Is the state set closed enough for an enum and switch?
- Are repeated state branches genuinely difficult to maintain?
- Are transitions explicit and testable?
- Can invalid flag combinations be removed with associated values?
- Is one owner serializing state changes?
- Could suspension make a transition stale?
- Is the variation lifecycle-driven rather than caller-selected Strategy?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: State in Swift](https://refactoring.guru/design-patterns/state/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
