# Composite

## Intent

Represent individual objects and nested groups through one interface so recursive client operations do not branch on “leaf versus container.” Composite is valuable when an open family of nodes shares a meaningful operation across an arbitrarily deep tree.

## Prefer Swift-native alternatives when

Use an `indirect enum` for a closed tree. Associated values make all cases visible, exhaustive switches keep operations easy to find, and value semantics simplify ownership. A recursive struct may suffice when every node has the same shape. Choose protocol-based Composite only when node kinds must be extended independently, callers should treat them uniformly, or operations naturally belong to each node.

## Choose this pattern when

Choose Composite when leaves and containers participate in the same domain operation, nesting depth is unbounded, and clients should ask the root for an aggregate result. Document outlines, layout trees, and command groups can fit. The shared interface must mean something for every member; a protocol filled with leaf-only or container-only methods is not uniform.

## Avoid it when

Avoid Composite for a closed handful of cases where an enum switch is clearer. Do not expose child mutation on leaf nodes through meaningless methods. Avoid existential trees when algorithms need exhaustive knowledge of every node kind. If only traversal varies, `Sequence` may be the important abstraction rather than Composite.

## Design pressures

Look for recursive code that repeatedly checks concrete node types before calculating word counts, prices, or permissions. Another signal is duplicated aggregation logic in multiple clients. The pattern helps when each container can combine the same result produced by a child. It helps less when operations require unrelated data and extensive downcasting.

## Swift implementation

Define a small protocol around the uniform operation. Leaf values compute directly; container values reduce over children. `[any OutlineElement]` permits an open set of conformers but introduces existential storage and reference/value subtleties. Keep mutation outside the protocol unless it applies uniformly. For a closed model, prefer `indirect enum Outline { case paragraph(String); case section(String, [Outline]) }` and implement the calculation once with an exhaustive switch.

## Concurrency and ownership

An immutable value tree is easiest to reason about and can be `Sendable` when its elements are. Existential storage is not automatically sendable; add that requirement only if every conformer can honor it. Mutable reference nodes need a single owner or actor isolation, especially when aggregate results are cached. Never assume recursive structure implies safe snapshot semantics.

## Compare

Decorator also nests values behind one interface, but each layer usually wraps one component to augment behavior; Composite containers manage multiple children and aggregate them. Iterator exposes traversal without requiring uniform aggregate behavior. Visitor adds operations to a stable set of node types. An `indirect enum` is normally superior when the tree’s variants are closed and exhaustiveness matters.

## Example

```swift
protocol OutlineElement {
    var wordCount: Int { get }
    func rendered(indentation: Int) -> String
}

struct Paragraph: OutlineElement {
    let text: String

    var wordCount: Int {
        text.split(whereSeparator: \.isWhitespace).count
    }

    func rendered(indentation: Int) -> String {
        String(repeating: " ", count: indentation) + text
    }
}

struct Section: OutlineElement {
    let title: String
    let children: [any OutlineElement]

    var wordCount: Int {
        children.reduce(0) { $0 + $1.wordCount }
    }

    func rendered(indentation: Int) -> String {
        let prefix = String(repeating: " ", count: indentation)
        let nested = children
            .map { $0.rendered(indentation: indentation + 2) }
            .joined(separator: "\n")
        return "\(prefix)\(title)\n\(nested)"
    }
}

let outline = Section(
    title: "Design Notes",
    children: [
        Paragraph(text: "Prefer values first"),
        Section(
            title: "Exceptions",
            children: [Paragraph(text: "Identity can matter")]
        )
    ]
)

print(outline.wordCount)
print(outline.rendered(indentation: 0))
```

Both paragraphs and sections answer the same questions, and a section recursively combines child results. If those were the only two permanent cases, an `indirect enum` would likely be smaller and more exhaustive.

## Review checklist

- Do leaves and containers share a genuinely uniform operation?
- Is the node family open enough to justify protocols and existentials?
- Would an `indirect enum` provide a clearer closed model?
- Can container-only mutation stay out of the common interface?
- Does aggregation avoid concrete-type checks and downcasts?
- Are tree ownership, mutation, and sendability explicit?
- Is traversal, rather than recursive composition, the actual need?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Composite in Swift](https://refactoring.guru/design-patterns/composite/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
