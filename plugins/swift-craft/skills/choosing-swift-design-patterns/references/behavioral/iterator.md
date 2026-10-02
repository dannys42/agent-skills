# Iterator

## Intent

Traverse elements without exposing the collection’s storage representation. In Swift, this intent is usually expressed directly through `Sequence`, `IteratorProtocol`, or `AsyncSequence`, so a separately named GoF layer is rarely necessary.

## Prefer Swift-native alternatives when

Make synchronous, repeatable traversal conform to `Sequence`; return an `AnySequence` when the concrete sequence should stay private. Use a lazy sequence for derived traversal that does not require allocation. Choose `AsyncSequence` when values arrive over time or obtaining the next value suspends. Standard `for` and `for await` syntax gives callers a familiar interface with algorithms such as `map`, `filter`, and `reduce`.

## Choose this pattern when

The Iterator pattern’s pressure remains useful when a custom data structure needs a traversal policy independent of storage. A tree can offer depth-first and breadth-first sequences without exposing child arrays. Custom iterator state also fits one-pass parsing or cursor-backed access. Prefer implementing Swift’s protocols rather than inventing `hasNext` and `nextElement` APIs.

## Avoid it when

Avoid a custom iterator for an array already exposed safely. Do not promise a multi-pass `Sequence` when each iterator shares one destructive cursor. Do not use `AsyncSequence` merely to run synchronous work on another executor; suspension should reflect real asynchronous production or backpressure needs. Be explicit about whether mutation during traversal is forbidden, snapshot-based, or observed.

## Design pressures

Look for private storage, multiple traversal orders, lazy access, one-pass sources, or values produced over time. Decide whether iteration is finite, repeatable, throwing, cancellable, and stable under mutation. These semantic choices matter more than the pattern name. For trees, clarify depth-first pre-order versus post-order and whether cycles are possible.

## Swift implementation

Provide a lightweight `Sequence` whose `makeIterator()` creates independent traversal state. The iterator should own its stack or cursor and return `nil` permanently after exhaustion. Keep the collection’s nodes immutable during iteration, or define snapshot behavior. For asynchronous sources, implement `AsyncSequence` only if `AsyncStream` or an existing framework sequence does not already express the lifecycle.

## Concurrency and ownership

A synchronous iterator is not automatically safe to move between tasks. Its mutable cursor belongs to one consumer unless the type documents stronger guarantees. Values crossing actor boundaries should be `Sendable`. For `AsyncStream`, choose a buffering policy, finish the continuation on producer shutdown, and specify how cancellation removes subscribers. Because module default isolation and strict-concurrency settings vary, verify those settings before promising cross-actor conformance.

## Compare

`Sequence` and `IteratorProtocol` are Swift’s native realization of Iterator. `AsyncSequence` adds suspension, cancellation, and potentially errors; it is not simply a concurrent `Sequence`. Composite models a part-whole tree, while Iterator controls how that tree is visited. Visitor puts operations over elements; iteration only supplies elements in an order.

## Example

```swift
struct TreeNode<Element> {
    let value: Element
    let children: [TreeNode<Element>]
}

struct DepthFirstSequence<Element>: Sequence {
    let root: TreeNode<Element>

    func makeIterator() -> Iterator {
        Iterator(pending: [root])
    }

    struct Iterator: IteratorProtocol {
        fileprivate var pending: [TreeNode<Element>]

        mutating func next() -> Element? {
            guard let node = pending.popLast() else {
                return nil
            }
            pending.append(contentsOf: node.children.reversed())
            return node.value
        }
    }
}

let tree = TreeNode(
    value: "root",
    children: [
        TreeNode(
            value: "documents",
            children: [
                TreeNode(value: "notes.txt", children: []),
                TreeNode(value: "draft.md", children: [])
            ]
        ),
        TreeNode(value: "images", children: [])
    ]
)

let names = Array(DepthFirstSequence(root: tree))
print(names.joined(separator: ", "))
```

Each call to `makeIterator()` gets an independent stack, and reversing children before pushing preserves their declared left-to-right order. This is a Swift-native implementation of the pattern; adding a second object hierarchy named “iterator” would not improve it.

## Review checklist

- Can the collection use `Sequence` or `AsyncSequence` directly?
- Is traversal order documented and tested?
- Are iterators independent, one-pass, or destructive?
- What happens if storage mutates during traversal?
- Does an asynchronous sequence finish and honor cancellation?
- Is its buffering policy intentional?
- Are iterator state and emitted values safe at isolation boundaries?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Iterator in Swift](https://refactoring.guru/design-patterns/iterator/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
