# Strategy

## Intent

Make an algorithm replaceable without changing the caller that uses it. The design separates stable orchestration from a varying calculation or policy.

## Prefer Swift-native alternatives when

Pass a closure for a small stateless formula. Use a generic function parameter when selection happens at compile time and specialization is useful. A free function or enum switch is clearer when there are only a few fixed policies. Swift makes these alternatives lightweight, so a strategy protocol should not be the default.

## Choose this pattern when

Choose Strategy when algorithms have meaningful state, dependencies, independent tests, or runtime substitution across a stable interface. Shipping pricing may depend on carrier tables, destinations, package limits, and promotional policy. Named strategy types can keep those collaborators cohesive and let a checkout service change carriers without branching on concrete types.

## Avoid it when

Avoid one protocol and several wrapper types for three one-line arithmetic expressions. Do not erase a generic strategy to `any Protocol` unless runtime heterogeneity is required. Strategies should not own the caller’s lifecycle state or decide when they replace themselves; that drifts toward State. Beware interfaces so broad that every algorithm ignores half the inputs.

## Design pressures

Look for repeated conditional selection of algorithms, formulas that change independently, configuration-driven choice, or policy dependencies that make closures bulky. Decide whether selection occurs at compile time, initialization, or per call. Keep inputs and results domain-specific so strategies are substitutable under the same documented contract.

## Swift implementation

Prefer a closure type alias for the first extraction. Promote it to a protocol when a strategy needs stored collaborators, several related operations, or a testable semantic name. Generics preserve concrete types and avoid existential dispatch but make one context hold only one strategy type. An existential permits runtime replacement at the cost of type erasure and some flexibility.

## Concurrency and ownership

Immutable value strategies are easy to share. Strategies holding mutable rates or caches need a clear owner, potentially an actor. Closures crossing isolation boundaries must be `@Sendable` and may capture only safely transferable values. Do not add `Sendable` to a strategy protocol until its actual use crosses isolation. If pricing awaits remote data, expose `async throws` honestly and define consistency across updates.

## Compare

A closure is Swift’s smallest strategy. A generic parameter is best for compile-time substitution. State also delegates behavior, but transitions choose the active state as an object evolves; clients or configuration choose a Strategy. Template Method fixes an algorithm skeleton and varies selected steps, while Strategy replaces the algorithm as a unit.

## Example

```swift
struct Parcel {
    let weightInGrams: Int
    let distanceInKilometers: Int
}

protocol ShippingPricing {
    func priceInCents(for parcel: Parcel) -> Int
}

struct GroundPricing: ShippingPricing {
    let baseInCents: Int

    func priceInCents(for parcel: Parcel) -> Int {
        baseInCents
            + parcel.weightInGrams / 100
            + parcel.distanceInKilometers / 10
    }
}

struct ExpressPricing: ShippingPricing {
    let minimumInCents: Int

    func priceInCents(for parcel: Parcel) -> Int {
        max(
            minimumInCents,
            parcel.weightInGrams / 25
                + parcel.distanceInKilometers / 3
        )
    }
}

struct ShippingQuote {
    let pricing: any ShippingPricing

    func totalInCents(for parcels: [Parcel]) -> Int {
        parcels.reduce(into: 0) { total, parcel in
            total += pricing.priceInCents(for: parcel)
        }
    }
}

let parcels = [
    Parcel(weightInGrams: 1_200, distanceInKilometers: 350),
    Parcel(weightInGrams: 600, distanceInKilometers: 350)
]
let quote = ShippingQuote(pricing: ExpressPricing(minimumInCents: 1_500))
print(quote.totalInCents(for: parcels))
```

The quote owns stable aggregation while the injected strategy owns carrier-specific pricing. If each formula remained one expression with no dependencies, injecting `(Parcel) -> Int` would communicate the same variation with fewer types.

## Review checklist

- Is there a real family of interchangeable algorithms?
- Would a closure or generic parameter be clearer?
- Do all strategies honor the same input and result contract?
- Does runtime replacement justify existential storage?
- Are dependencies cohesive within each strategy?
- Is mutable strategy state isolated appropriately?
- Is this caller-selected variation rather than lifecycle-driven State?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Strategy in Swift](https://refactoring.guru/design-patterns/strategy/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
