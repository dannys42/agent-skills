# Singleton

## Intent

Provide one process-wide instance with a controlled access point when the domain truly permits only one authority. In Swift applications, global reachability is usually the dangerous part; uniqueness alone does not justify hiding a dependency behind `shared`. Decide whether construction must be forbidden or whether the application merely needs one conventional production instance.

## Prefer Swift-native alternatives when

Create a value or service at the composition root and inject it through initializers. SwiftUI applications can place dependencies in an explicit environment, provided previews and tests can replace them. Pass a closure for a narrow capability. An actor can serialize access to one injected instance, but actor isolation does not make global access good design.

## Choose this pattern when

Choose a strict Singleton only when process-wide identity is a real invariant, construction must be controlled, and every consumer intentionally sees the same authority. A private initializer enforces that rule but removes the ability to create isolated instances. More often, a schema registry needs one production authority while tests need fresh registries; model that as an injected service with a shared production default, not as enforced uniqueness.

## Avoid it when

Avoid it as a convenience for passing dependencies, as a cache whose lifetime should be scoped, or as mutable application state. Hidden globals create order-dependent tests, make lifetimes unclear, and allow unrelated features to couple silently. Do not use Singleton to enforce uniqueness that the operating system, persistence layer, or composition root already controls.

## Design pressures

Look for duplicate registries producing conflicting interpretations of the same identifier, repeated expensive bootstrap work, or a framework callback that offers no practical injection seam. Then verify the invariant: should there truly be one per process, or one per account, document, scene, request, or test? Most apparent singleton needs reveal a narrower ownership scope.

## Swift implementation

For a strict Singleton, prefer a `final` type with a private initializer and an immutable `static let` instance. Keep its public surface small. If test isolation or multiple scopes are legitimate, keep initialization available, name the shared instance for its production role, and inject the service; be explicit that this does not enforce uniqueness. If mutation is necessary, use an actor or another explicit synchronization boundary rather than locks scattered through callers. Avoid work with surprising failure modes in static initialization; a composition root can build a fallible dependency more transparently.

## Concurrency and ownership

Swift initializes a `static let` lazily and safely, but that only protects initialization. Stored mutable state still needs isolation. An actor-backed registry serializes mutation and makes calls visibly asynchronous. Values returned across the actor boundary should be `Sendable`. The example deliberately permits fresh instances for tests, so `production` is a conventional shared authority rather than a strict Singleton.

## Compare

An injected service may have one instance without being a Singleton. A global variable provides reachability without controlled construction. A namespace enum groups stateless functions and constants, which needs no instance. Flyweight shares many immutable values by key; Singleton guarantees one object. An actor addresses data races, not dependency visibility.

## Example

```swift
actor SchemaRegistry {
    static let production = SchemaRegistry()

    struct Schema: Sendable, Equatable {
        let identifier: String
        let fieldNames: [String]
    }

    enum RegistrationError: Error {
        case conflictingIdentifier(String)
    }

    private var schemas: [String: Schema] = [:]

    init(initialSchemas: [Schema] = []) {
        schemas = Dictionary(
            uniqueKeysWithValues: initialSchemas.map { ($0.identifier, $0) }
        )
    }

    func register(_ schema: Schema) throws {
        if let current = schemas[schema.identifier], current != schema {
            throw RegistrationError.conflictingIdentifier(schema.identifier)
        }
        schemas[schema.identifier] = schema
    }

    func schema(identifier: String) -> Schema? {
        schemas[identifier]
    }
}

func loadEvent(
    registry: SchemaRegistry = .production
) async throws -> SchemaRegistry.Schema? {
    try await registry.register(
        .init(identifier: "event.v1", fieldNames: ["timestamp", "name"])
    )
    return await registry.schema(identifier: "event.v1")
}

let isolatedTestRegistry = SchemaRegistry()
let schema = try await loadEvent(registry: isolatedTestRegistry)
print(schema?.identifier ?? "missing")
```

The default expresses the application's shared production authority, while explicit injection preserves test isolation and exposes the dependency. Because callers may construct another registry, this is the Swift-native service compromise rather than enforced Singleton semantics.

## Review checklist

- Is enforced uniqueness a domain invariant, or is one production default sufficient?
- Is the intended scope really the entire process?
- Can initializer injection or an environment value remove hidden access?
- Is mutable state isolated independently of static initialization?
- Can tests construct a fresh instance without resetting global state?
- If construction is private, how will tests isolate consumers without mutating the global instance?
- Are initialization failure and lifetime behavior explicit?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Singleton in Swift](https://refactoring.guru/design-patterns/singleton/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
