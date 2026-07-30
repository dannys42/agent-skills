# Prototype

## Intent

Create an independent object by copying an existing, configured instance when reconstructing it from parameters is impractical. In Swift, ordinary assignment already provides value copying, so Prototype is mainly relevant to reference graphs that need explicit deep-copy identity rules.

## Prefer Swift-native alternatives when

Use a struct when its state has value semantics; assignment and copy-on-write collections already provide efficient independent values. Use `copy`-style methods only to express deliberate modifications, such as `configuration.withTimeout(...)`. Recreate cheap reference objects from stored configuration rather than inventing cloning machinery. `Codable` round trips are not a general cloning tool.

## Choose this pattern when

Choose Prototype when an object is expensive or awkward to configure, callers need variants of a prepared object, concrete types should remain hidden, and the copied object must have distinct identity. It is most justified for linked graphs where a deep copy must preserve internal sharing or cycles while severing links to the original graph.

## Avoid it when

Avoid it for value types, immutable shared objects, or shallow reference structures with obvious initializers. Do not promise a deep clone without specifying treatment of delegates, caches, file handles, actors, and external resources. Copying a graph can be more error-prone than reconstructing it from an authoritative model.

## Design pressures

Warning signs include ad hoc `clone` methods that accidentally share child nodes, recursive copying that duplicates a shared descendant twice, or subclasses that forget to copy new fields. A valid pressure exists when identity topology matters: two edges pointing to one original node should point to one copied node, not two unrelated copies.

## Swift implementation

For reference graphs, define a narrow copying operation and pass a memo table keyed by `ObjectIdentifier`. Register the new object before descending so cycles terminate and shared links stay shared. Keep external dependencies injected rather than copied. If subclasses participate, make the copying contract explicit and test every concrete type; a `final` graph node is simpler.

## Concurrency and ownership

Deep copying mutable reference state should happen under exclusive ownership or inside the actor that owns the graph. Copying while another task mutates edges can produce an incoherent snapshot. The resulting graph is not `Sendable` merely because it is distinct. Prefer immutable `Sendable` value snapshots for cross-task transfer, then rebuild actor-owned references at the destination.

## Compare

Builder constructs a new object from staged inputs. Memento captures state for restoration without necessarily creating a usable peer object. Prototype derives a new object from an existing exemplar. A struct copy is the Swift-native default and should not be wrapped in a formal Prototype API unless callers need additional semantics.

## Example

```swift
final class WorkflowStep {
    let name: String
    var next: [WorkflowStep]

    init(name: String, next: [WorkflowStep] = []) {
        self.name = name
        self.next = next
    }

    func deepCopy(
        memo: inout [ObjectIdentifier: WorkflowStep]
    ) -> WorkflowStep {
        let identity = ObjectIdentifier(self)
        if let existing = memo[identity] {
            return existing
        }

        let copy = WorkflowStep(name: name)
        memo[identity] = copy
        copy.next = next.map { $0.deepCopy(memo: &memo) }
        return copy
    }

    func deepCopy() -> WorkflowStep {
        var memo: [ObjectIdentifier: WorkflowStep] = [:]
        return deepCopy(memo: &memo)
    }
}

let publish = WorkflowStep(name: "Publish")
let review = WorkflowStep(name: "Review", next: [publish])
let revise = WorkflowStep(name: "Revise", next: [review])
review.next.append(revise)

let copiedReview = review.deepCopy()
let copiedPublish = copiedReview.next[0]
let copiedCycleTarget = copiedReview.next[1].next[0]

precondition(copiedReview !== review)
precondition(copiedCycleTarget === copiedReview)
precondition(copiedPublish !== publish)
```

The memo table both breaks the cycle and preserves the copied graph's identity relationships.

## Review checklist

- Would a struct or copy-on-write collection solve the need automatically?
- Is distinct identity actually required?
- Are deep versus shared fields specified?
- Does copying preserve cycles and shared descendants?
- Are external resources excluded or reconstructed deliberately?
- Is the graph stable under one owner while the snapshot is made?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Prototype in Swift](https://refactoring.guru/design-patterns/prototype/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
