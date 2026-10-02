# Memento

## Intent

Capture an object’s restorable state without exposing or duplicating its internal mutation rules. The originator creates and consumes the snapshot; a caretaker stores it without needing to interpret private representation.

## Prefer Swift-native alternatives when

Start with an immutable value snapshot. Swift structs already copy state semantically and often make undo as simple as storing prior values. Use `Codable` when the need is serialization to a stable persistence format, not merely in-memory restoration. For small edits, a command that records its inverse can use less memory than copying a complete document.

## Choose this pattern when

Choose Memento when a stateful object must control exactly what is captured and how restoration preserves invariants. A drawing editor may snapshot canvas dimensions, ordered shapes, and selection while excluding derived caches and transient gesture state. The caretaker can implement history limits and labels without gaining setters for the editor’s internals.

## Avoid it when

Avoid wrapping a public value in a ceremonial `Memento` type when storing that value directly is clear. Do not confuse a process-local snapshot with durable persistence: schema evolution, corruption handling, and migrations are separate responsibilities. Large snapshots can exhaust memory, and reference properties may still alias mutable objects unless copied deliberately. Restoration must not bypass invariants.

## Design pressures

Look for undo checkpoints, speculative editing, rollback, or recovery where clients should not know internal fields. Decide snapshot granularity, retention policy, and whether derived data is recomputed. Clarify whether external resources can be restored at all. A snapshot of a file handle or network session is not equivalent to recreating its external state.

## Swift implementation

Use a nested or access-controlled value for the snapshot and expose only `snapshot()` and `restore(from:)`. Capture authoritative data, not caches. Validate before committing restored state if snapshots can come from outside the process. A ring buffer or bounded history can cap memory. If `Codable` is added, version the serialized representation rather than assuming today’s stored properties are permanent.

## Concurrency and ownership

Snapshot and restore should occur within the originator’s isolation boundary so they observe a coherent state. An actor can expose value snapshots that conform to `Sendable`; callers should not receive mutable references into actor state. UI editors may belong to the main actor, but that choice follows UI ownership rather than the pattern. Large snapshot encoding should avoid blocking an actor after safely copying the value.

## Compare

An ordinary value snapshot is usually the simplest Memento realization in Swift. `Codable` addresses representation across storage or transport and introduces compatibility concerns. Command stores operations and inverses; Memento stores state. Prototype creates an independent working object, while Memento restores a particular originator to a prior state.

## Example

```swift
struct Point: Equatable {
    var x: Double
    var y: Double
}

struct Stroke: Equatable {
    var points: [Point]
    var colorName: String
}

struct DrawingEditor {
    struct Snapshot {
        fileprivate let canvasSize: Point
        fileprivate let strokes: [Stroke]
        fileprivate let selectedIndex: Int?
    }

    private(set) var canvasSize: Point
    private(set) var strokes: [Stroke] = []
    private(set) var selectedIndex: Int?

    mutating func append(_ stroke: Stroke) {
        strokes.append(stroke)
        selectedIndex = strokes.indices.last
    }

    func snapshot() -> Snapshot {
        Snapshot(
            canvasSize: canvasSize,
            strokes: strokes,
            selectedIndex: selectedIndex
        )
    }

    mutating func restore(from snapshot: Snapshot) {
        canvasSize = snapshot.canvasSize
        strokes = snapshot.strokes
        selectedIndex = snapshot.selectedIndex.flatMap {
            strokes.indices.contains($0) ? $0 : nil
        }
    }
}

var editor = DrawingEditor(canvasSize: Point(x: 800, y: 600))
let beforeInk = editor.snapshot()
editor.append(
    Stroke(
        points: [Point(x: 10, y: 10), Point(x: 20, y: 24)],
        colorName: "indigo"
    )
)
editor.restore(from: beforeInk)
print(editor.strokes.count)
```

The snapshot contains authoritative drawing values while restoration rechecks selection validity. Copy-on-write collections keep creation inexpensive until one side mutates, but a long history can still retain substantial storage.

## Review checklist

- Would storing the value directly be sufficient?
- Does the originator alone create and restore snapshots?
- Are caches and transient resources excluded?
- Are referenced mutable objects actually independent?
- Is history bounded according to snapshot size?
- Does durable storage require versioning and migration?
- Is capture coherent within the owner’s isolation boundary?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Memento in Swift](https://refactoring.guru/design-patterns/memento/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
