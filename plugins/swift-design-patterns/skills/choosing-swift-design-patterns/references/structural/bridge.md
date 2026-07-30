# Bridge

## Intent

Separate an abstraction from the implementation capability it delegates to so both dimensions can vary without producing a concrete type for every combination. The abstraction owns user-facing policy; the implementation protocol owns the platform or mechanism boundary.

## Prefer Swift-native alternatives when

Use a generic parameter when the implementation is fixed at composition time and static dispatch is useful. Store a small protocol-conforming value when runtime substitution is needed. For a single operation, an injected closure often expresses the entire implementation boundary. These are idiomatic ways to realize Bridge’s separation; a hierarchy on both sides is rarely necessary in Swift.

## Choose this pattern when

Choose Bridge when two axes genuinely change independently and their cross-product is causing duplication. A notification product might vary by presentation policy—urgent, digest, transactional—and by delivery channel—email, push, or console. Keeping channel mechanics behind one capability lets new notification abstractions reuse them, while new channels do not duplicate presentation workflows.

## Avoid it when

Avoid Bridge when there is one stable dimension, a direct generic type is already sufficient, or the supposed axes always change together. Do not manufacture an “abstraction hierarchy” around a few flags. If code only converts an incompatible existing API, use Adapter. If the variation is one replaceable calculation within an otherwise stable object, Strategy is usually the clearer description.

## Design pressures

Signals include names such as `UrgentEmailNotification`, `UrgentPushNotification`, `DigestEmailNotification`, and `DigestPushNotification`, with each type repeating most logic. Also look for platform imports mixed with domain formatting or tests that cannot exercise message policy without invoking delivery infrastructure. Bridge is justified when each axis has its own reasons to change.

## Swift implementation

Give the implementation protocol the narrow operation the abstraction needs. A generic abstraction preserves concrete channel information and avoids existential overhead; use `any DeliveryChannel` only when channels must be stored heterogeneously or selected at runtime. Keep message construction in the abstraction and transport details in the implementor. Composition should occur near the application boundary.

## Concurrency and ownership

Delivery channels commonly perform asynchronous I/O. In production, make the protocol operation `async throws` and require `Sendable` where instances cross task boundaries. A generic wrapper inherits the safety of its stored channel; it does not add isolation. Actor-isolate mutable channel state such as connection pools, while leaving immutable notification policy as a value.

## Compare

Strategy swaps one algorithm used by a context; Bridge separates two broader, independently extensible dimensions and usually gives the abstraction meaningful policy of its own. Adapter makes an existing incompatible interface fit after the fact. Abstract Factory may construct compatible families but does not itself define ongoing delegation. A generic parameter or protocol composition is often Bridge’s Swift form, not an alternative intent.

## Example

```swift
protocol DeliveryChannel {
    func deliver(subject: String, body: String) -> String
}

struct EmailChannel: DeliveryChannel {
    let address: String

    func deliver(subject: String, body: String) -> String {
        "Email to \(address): \(subject) — \(body)"
    }
}

struct ConsoleChannel: DeliveryChannel {
    func deliver(subject: String, body: String) -> String {
        "[\(subject)] \(body)"
    }
}

struct Notification<Channel: DeliveryChannel> {
    let channel: Channel
    let applicationName: String

    func send(message: String) -> String {
        channel.deliver(
            subject: applicationName,
            body: message
        )
    }
}

struct UrgentNotification<Channel: DeliveryChannel> {
    let channel: Channel

    func send(message: String) -> String {
        channel.deliver(
            subject: "Action required",
            body: message.uppercased()
        )
    }
}

let email = EmailChannel(address: "ops@example.com")
let urgent = UrgentNotification(channel: email)
print(urgent.send(message: "database capacity is low"))

let local = Notification(
    channel: ConsoleChannel(),
    applicationName: "Preview"
)
print(local.send(message: "render complete"))
```

Notification policy and delivery mechanism can grow independently. Generics keep each composed value concrete; an existential channel could replace the generic when runtime switching is a real requirement.

## Review checklist

- Are there two independent reasons to vary?
- Is a growing cross-product of concrete combinations visible?
- Would one generic type or injected closure be enough?
- Does the abstraction own policy rather than merely forwarding?
- Is the implementation protocol narrow and mechanism-focused?
- Are composition and runtime-versus-static selection deliberate?
- Is this distinct from interface conversion or one algorithm swap?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Bridge in Swift](https://refactoring.guru/design-patterns/bridge/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
