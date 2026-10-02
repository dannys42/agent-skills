# Factory Method

## Intent

Give a creator a focused seam for choosing or customizing one product while the surrounding workflow remains stable. In Swift, that seam need not use inheritance: a protocol requirement or injected creation closure usually preserves the intent with less coupling.

## Prefer Swift-native alternatives when

Call a concrete initializer directly when the caller already knows the type. Inject a closure when selection is local, there is one creation operation, and no richer factory behavior is needed. Use an enum switch at the composition root when the set of formats is closed and small. Generics are clearer when the chosen product is fixed at compile time.

## Choose this pattern when

Choose Factory Method when multiple creators share an operation but need different products, subclasses or conformers should control construction, or product selection must be independently replaceable for tests and extensions. The method should protect a stable client workflow from concrete construction details; otherwise it is just an extra forwarding layer.

## Avoid it when

Avoid it when there is one implementation with no realistic substitution, when a closure expresses the seam completely, or when selection requires a compatible group of products. Do not build a registry of metatypes merely to avoid a clear switch. Dynamic extensibility can make supported cases harder to discover and validate.

## Design pressures

Look for format-selection switches duplicated across import workflows, framework base types forced to mention application-specific decoders, or tests that must intercept construction rather than behavior. A useful factory method centralizes one varying creation decision while parsing, logging, and error handling stay unchanged.

## Swift implementation

Prefer a small protocol with a method returning `any Product` when runtime heterogeneity is required. A creator can expose one factory requirement and provide the invariant workflow in a protocol extension. If the result has associated types and callers remain generic, avoid existential erasure. Keep factory inputs explicit; hidden global configuration makes the construction seam difficult to test.

## Concurrency and ownership

Decoders should generally be short-lived values. Mark factory closures `@Sendable` when they cross task boundaries, and require produced reference objects to satisfy the intended isolation contract. A factory method does not transfer ownership automatically: document whether each call returns a fresh product, a cached value, or an actor-isolated service.

## Compare

Abstract Factory creates a family whose members must remain compatible. Builder assembles one elaborate object over stages. Factory Method varies one product-creation step. Strategy varies behavior after creation. Dependency injection through a closure is often the Swift-native form of Factory Method when the creator does not need its own polymorphic type.

## Example

```swift
import Foundation

struct Document {
    let title: String
}

protocol DocumentDecoder {
    func decode(_ data: Data) throws -> Document
}

struct JSONDocumentDecoder: DocumentDecoder {
    private struct Payload: Decodable { let title: String }

    func decode(_ data: Data) throws -> Document {
        let payload = try JSONDecoder().decode(Payload.self, from: data)
        return Document(title: payload.title)
    }
}

struct PlainTextDocumentDecoder: DocumentDecoder {
    func decode(_ data: Data) throws -> Document {
        Document(title: String(decoding: data, as: UTF8.self))
    }
}

enum DocumentFormat {
    case json
    case plainText
}

protocol DocumentImporter {
    func makeDecoder(for format: DocumentFormat) -> any DocumentDecoder
}

extension DocumentImporter {
    func importDocument(_ data: Data, format: DocumentFormat) throws -> Document {
        try makeDecoder(for: format).decode(data)
    }
}

struct DefaultDocumentImporter: DocumentImporter {
    func makeDecoder(for format: DocumentFormat) -> any DocumentDecoder {
        switch format {
        case .json: JSONDocumentDecoder()
        case .plainText: PlainTextDocumentDecoder()
        }
    }
}

let data = Data(#"{"title":"Field Notes"}"#.utf8)
let document = try DefaultDocumentImporter()
    .importDocument(data, format: .json)
print(document.title)
```

The importing workflow is stable, while `makeDecoder` is the single creation decision a specialized importer can replace.

## Review checklist

- Is exactly one product creation decision varying?
- Would a direct initializer or injected closure make the seam clearer?
- Does the creator own useful invariant work around construction?
- Is a closed switch more honest than dynamic registration?
- Are factory inputs and returned ownership semantics explicit?
- Would a product family require Abstract Factory instead?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Factory Method in Swift](https://refactoring.guru/design-patterns/factory-method/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
