# Mediator

## Intent

Centralize interaction rules among peers so they do not depend directly on one another. A mediator owns coordination, not each participant’s intrinsic validation or presentation behavior.

## Prefer Swift-native alternatives when

Use a coordinator closure when one child reports one event to its owner. In SwiftUI or Observation-based code, a small shared observable model can be clearer when participants simply read and edit the same state. Direct bindings are appropriate when there is one obvious source of truth and no cross-field policy. Keep pure validation in standalone functions rather than hiding it inside a mediator.

## Choose this pattern when

Choose Mediator when several peers trigger nontrivial reactions in one another and direct references would create a dependency web. Checkout fields may coordinate shipping country, postal-code rules, tax region, delivery options, and submit eligibility. A mediator can translate field events into an ordered update without requiring each field to know the rest.

## Avoid it when

Avoid a “god mediator” that accumulates business logic, networking, storage, and presentation. If participants merely share state, an observable value is simpler. If a type provides a simplified entry point into a subsystem for outside clients, it is a Facade, not a Mediator. Do not route every local method call through a mediator; reserve it for meaningful peer coordination.

## Design pressures

Look for bidirectional peer references, repeated reaction logic, update cycles, and tests that require constructing every collaborator. Identify the event vocabulary and make update ordering deterministic. The mediator should reduce participant knowledge while keeping coordination rules discoverable. If the rules form a domain process, consider naming the mediator after that process rather than using the generic suffix `Manager`.

## Swift implementation

Represent participant events with an enum and centralize resulting state transitions in one method. Keep the state value authoritative so fields render from results rather than retaining parallel flags. For open-ended component sets, a protocol may help, but a closed event enum is often more readable. Avoid callbacks from the mediator into participants when returning a new coordinated state suffices.

## Concurrency and ownership

One owner should serialize coordinated mutations. A UI checkout model may correctly be main-actor isolated because views observe it; a server-side workflow may instead be a dedicated actor. Do not add `@MainActor` without knowing the host module’s UI boundary and default isolation. Participant events crossing actors need `Sendable` payloads, and asynchronous validation needs stale-result protection so an older response cannot overwrite newer input.

## Compare

Facade simplifies how external clients invoke a subsystem; Mediator governs ongoing interactions among peers. Observer broadcasts changes without defining how recipients coordinate. A shared observable model is preferable when common state alone removes coupling. Coordinator closures work for narrow parent-child communication. Mediator is justified when several interaction rules need one explicit home.

## Example

```swift
enum CheckoutEvent {
    case countryChanged(String)
    case postalCodeChanged(String)
}

struct CheckoutState: Equatable {
    var country = "US"
    var postalCode = ""
    var deliveryOptions: [String] = []
    var canSubmit = false
}

struct CheckoutMediator {
    private(set) var state = CheckoutState()

    mutating func receive(_ event: CheckoutEvent) {
        switch event {
        case .countryChanged(let country):
            state.country = country
            state.deliveryOptions = country == "US"
                ? ["Ground", "Express"]
                : ["International"]
        case .postalCodeChanged(let postalCode):
            state.postalCode = postalCode
        }

        state.canSubmit = isPostalCodeValid(
            state.postalCode,
            for: state.country
        )
    }

    private func isPostalCodeValid(
        _ postalCode: String,
        for country: String
    ) -> Bool {
        if country == "US" {
            return postalCode.count == 5 && postalCode.allSatisfy(\.isNumber)
        }
        return postalCode.count >= 3
    }
}

var checkout = CheckoutMediator()
checkout.receive(.countryChanged("US"))
checkout.receive(.postalCodeChanged("94107"))
print(checkout.state.deliveryOptions, checkout.state.canSubmit)
```

Fields need only emit typed events and render the resulting state. If all fields could bind to `CheckoutState` without cross-field reactions, retaining the mediator would add an unnecessary forwarding layer.

## Review checklist

- Are multiple peers coupled through interaction rules?
- Would one shared observable state remove the coupling more simply?
- Are event ordering and update cycles controlled?
- Does the mediator coordinate rather than absorb every responsibility?
- Is this peer interaction rather than an external subsystem facade?
- Is there one authoritative state owner?
- Can asynchronous reactions overwrite newer state?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Mediator in Swift](https://refactoring.guru/design-patterns/mediator/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
