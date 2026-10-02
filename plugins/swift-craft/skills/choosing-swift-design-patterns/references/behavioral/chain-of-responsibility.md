# Chain of Responsibility

## Intent

Pass a request through ordered handlers so each handler can accept it, reject it, transform it, or deliberately hand it onward. The pattern is valuable when routing and short-circuit behavior belong to the handlers themselves, not merely to a loop owned by the caller.

## Prefer Swift-native alternatives when

Start with an array of validation functions such as `(Purchase) -> ValidationError?`. A loop using `first(where:)`, `compactMap`, or an early return is easier to inspect when every rule has the same shape and the only outcomes are “continue” or “fail.” A throwing function that calls a few named checks in order is clearer still when the pipeline is fixed.

## Choose this pattern when

Choose Chain of Responsibility when handlers make meaningfully different routing decisions, assemble dynamically, or need to delegate without a central dispatcher knowing every concrete type. A purchase pipeline may include a fraud handler that rejects, a credit handler that approves, and a manual-review handler that consumes only uncertain requests. The benefit appears when adding or reordering those policies should not rewrite the coordinator.

## Avoid it when

Avoid the pattern for a short homogeneous list of predicates. Do not hide required validation behind a chain whose order is accidental. A request falling off the end must have an explicit meaning; silent success is usually dangerous. If every handler always calls the next one, the chain is ceremony around an ordinary loop. Avoid mutable `next` links when an immutable ordered collection communicates the topology better.

## Design pressures

Look for request categories whose handling varies independently, conditional delegation, runtime composition, and a need to stop after one handler owns the result. Clarify whether all rules must run, the first failure wins, or exactly one handler should consume the request. Those are different contracts. The pattern earns its cost when the delegation decision is local policy rather than generic iteration.

## Swift implementation

Use a small result enum to make “handled,” “rejected,” and “pass onward” exhaustive. A protocol supports stateful handlers and dependency injection; an enum or closure can model smaller chains. Keep traversal in one reusable pipeline so a malformed handler cannot invoke its successor twice. Prefer immutable handler arrays over reference-linked nodes unless handlers truly need to select different successors.

## Concurrency and ownership

The chain itself does not serialize mutable handlers. Value handlers are simplest. If handlers share changing limits, caches, or fraud state across tasks, place that state behind an actor and make the processing API asynchronous. Requests crossing isolation boundaries should be `Sendable`. Preserve ordering explicitly, and do not run handlers concurrently when first-handler-wins semantics depend on sequence.

## Compare

A validator loop applies uniform operations and owns continuation centrally. Chain of Responsibility lets each handler decide whether processing continues. Strategy chooses one algorithm for a task; a chain may consult several candidates in order. Command packages an action for later execution, while a handler responds immediately to a request. Middleware is often a functional form of a chain, especially when each layer can wrap downstream work.

## Example

```swift
struct Purchase {
    let amountInCents: Int
    let availableCreditInCents: Int
    let riskScore: Int
}

enum PurchaseDecision: Equatable {
    case approved
    case rejected(String)
    case next
}

protocol PurchaseHandler {
    func decide(_ purchase: Purchase) -> PurchaseDecision
}

struct FraudHandler: PurchaseHandler {
    func decide(_ purchase: Purchase) -> PurchaseDecision {
        purchase.riskScore >= 90
            ? .rejected("High fraud risk")
            : .next
    }
}

struct CreditHandler: PurchaseHandler {
    func decide(_ purchase: Purchase) -> PurchaseDecision {
        guard purchase.amountInCents <= purchase.availableCreditInCents else {
            return .next
        }
        return .approved
    }
}

struct ManualReviewHandler: PurchaseHandler {
    func decide(_ purchase: Purchase) -> PurchaseDecision {
        .rejected("Manual review required")
    }
}

struct PurchasePipeline {
    let handlers: [any PurchaseHandler]

    func decide(_ purchase: Purchase) -> PurchaseDecision {
        for handler in handlers {
            let decision = handler.decide(purchase)
            if decision != .next {
                return decision
            }
        }
        return .rejected("No handler accepted the purchase")
    }
}

let pipeline = PurchasePipeline(
    handlers: [FraudHandler(), CreditHandler(), ManualReviewHandler()]
)
let decision = pipeline.decide(
    Purchase(amountInCents: 2_500, availableCreditInCents: 4_000, riskScore: 12)
)
print(decision)
```

Here the fraud policy can stop the request, the credit policy can consume it, and the final handler gives exhaustion an explicit result. If each item only returned an error or `nil`, an array of validation closures would be the cleaner design.

## Review checklist

- Do handlers make distinct continue, consume, or reject decisions?
- Is the order intentional, visible, and tested?
- What happens when no handler accepts the request?
- Would a loop of uniform validation functions be clearer?
- Can handlers or shared dependencies race across tasks?
- Does adding a handler avoid changing the dispatcher?
- Are required checks impossible to bypass by reordering?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Chain of Responsibility in Swift](https://refactoring.guru/design-patterns/chain-of-responsibility/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
