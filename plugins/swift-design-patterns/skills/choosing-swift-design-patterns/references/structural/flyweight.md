# Flyweight

## Intent

Reduce the memory cost of many similar objects by separating shareable intrinsic state from per-use extrinsic state. Flyweight shares one immutable representation across many logical items, while each item supplies its own position, identity, or other contextual data.

## Prefer Swift-native alternatives when

Start with structs and standard-library copy-on-write collections. Copies derived from the same `String`, `Array`, or `Dictionary` value can share backing storage until mutation. Independently decoded or constructed values are not guaranteed to share merely because they compare equal. Use a straightforward cache when the goal is avoiding repeated computation or I/O. Consider measured canonicalization or interning only when independently produced equal values retain substantial duplicate storage.

## Choose this pattern when

Choose Flyweight when the application holds a very large number of objects, much of each object’s data is identical, that shared portion can be immutable, and callers can provide the remaining context. Text layout can share glyph styles while each placed glyph retains only its character, position, and style key. The memory model should be measurable before and after the change.

## Avoid it when

Avoid Flyweight for small populations, cheap values, frequently mutated shared state, or objects whose identity carries domain meaning. Do not trade a modest allocation reduction for global lookup contention and obscure ownership. If the repository only remembers previously loaded results, that is ordinary caching unless the domain representation is deliberately split into intrinsic and extrinsic state.

## Design pressures

Look for profiles showing thousands of repeated fonts, colors, brushes, or immutable metadata bundles retained inside otherwise tiny objects. Verify equality: “usually similar” is not enough for sharing. The key must capture every intrinsic property, and extrinsic properties must not leak into the shared object. Incorrect partitioning causes surprising cross-item changes.

## Swift implementation

Represent the key and flyweight as immutable `Hashable` structs where possible. A catalog maps keys to canonical values, while lightweight client values store the key or returned style alongside contextual state. Copies of a catalog-provided value may retain common copy-on-write backing storage; equal values built through separate decoding or construction paths may not. Value semantics mean clients need not test identity, but measured canonicalization can still avoid duplicated heavy storage. Keep the catalog scoped to a document or rendering session instead of defaulting to a process global.

## Concurrency and ownership

Immutable flyweights can be shared safely when their fields are `Sendable`. The mutable catalog still needs ownership: construct it before concurrent use, protect it with an actor, or keep one cache per isolated renderer. Actor isolation can serialize lookup, so measure contention as well as memory. Never allow clients to mutate a shared reference flyweight.

## Compare

An ordinary cache stores results so future requests are faster and may evict them without changing the domain model. Flyweight restructures many live logical objects so they share intrinsic state and receive extrinsic state from context. Singleton guarantees one instance of a service, not one value per key. Prototype copies configured objects—the opposite direction from sharing immutable state.

## Example

```swift
struct GlyphStyleKey: Hashable {
    let family: String
    let pointSize: Int
    let colorName: String
}

struct GlyphStyle {
    let key: GlyphStyleKey
    let fontMetrics: [Int]
}

struct PlacedGlyph {
    let character: Character
    let x: Int
    let y: Int
    let style: GlyphStyle

    func description() -> String {
        "\(character) at (\(x), \(y)) in \(style.key.family)"
    }
}

struct GlyphStyleCatalog {
    private var styles: [GlyphStyleKey: GlyphStyle] = [:]

    mutating func style(for key: GlyphStyleKey) -> GlyphStyle {
        if let existing = styles[key] {
            return existing
        }

        let created = GlyphStyle(
            key: key,
            fontMetrics: Array(repeating: key.pointSize, count: 128)
        )
        styles[key] = created
        return created
    }
}

var catalog = GlyphStyleCatalog()
let bodyKey = GlyphStyleKey(
    family: "System",
    pointSize: 14,
    colorName: "ink"
)
let sharedStyle = catalog.style(for: bodyKey)
let glyphs = [
    PlacedGlyph(character: "S", x: 10, y: 20, style: sharedStyle),
    PlacedGlyph(character: "w", x: 19, y: 20, style: sharedStyle)
]
print(glyphs.map { $0.description() })
```

The heavy metrics belong to the intrinsic style; character and position remain extrinsic to each placed glyph. In real code, profiling should confirm that this explicit catalog beats ordinary value storage.

## Review checklist

- Has profiling identified substantial duplicated retained state?
- Is intrinsic state fully immutable and correctly keyed?
- Can per-use context remain outside the shared value?
- Do the values share copy provenance, or are equal values independently constructed?
- Would copy-on-write values already provide enough measured sharing?
- Is this structural sharing rather than a performance cache alone?
- Is catalog scope and eviction behavior explicit?
- Are concurrent lookup and mutation safely owned?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Flyweight in Swift](https://refactoring.guru/design-patterns/flyweight/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
