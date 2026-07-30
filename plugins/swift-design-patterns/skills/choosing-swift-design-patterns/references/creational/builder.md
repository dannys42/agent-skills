# Builder

## Intent

Assemble one result through named, ordered operations while keeping validation and final construction in one place. A Builder earns its keep when creation is a process with intermediate state, not merely a long spelling of an initializer.

## Prefer Swift-native alternatives when

Start with an initializer whose optional parameters have defaults. Use a configuration value when callers benefit from storing or modifying settings before construction. A result builder is appropriate for declarative nested content, but it should not hide fallible validation or imply that arbitrary statement order is meaningful. Memberwise initialization remains the clearest choice for small value types.

## Choose this pattern when

Choose Builder when callers assemble many optional pieces, several fields are conditionally required, invalid intermediate states should not escape, or the same assembly recipe produces variants. It can also separate a mutable drafting phase from an immutable result. The final `build()` operation should provide a real boundary by validating, normalizing, or resolving dependencies.

## Avoid it when

Avoid Builder when every field is required at once, the result has only a few independent options, or fluent calls merely assign properties. Do not conceal errors through force unwraps or delayed crashes. If operation order is required, consider encoding phases in types; documentation alone is weak protection.

## Design pressures

Signals include sprawling call sites that repeatedly normalize headers, reject body/method conflicts, and construct URLs; telescoping initializers with ambiguous arguments; or partially configured reference objects passed between layers. The pressure is not raw parameter count. It is repeated construction policy and a need to prevent invalid results.

## Swift implementation

Keep the result immutable. The builder may be a value so chained methods return modified copies, avoiding aliasing surprises. Name operations for domain intent rather than `setX`. Make `build()` throwing when validity depends on accumulated data. If the builder captures closures, document their lifetime and sendability. Do not duplicate the result's entire public API on the builder unless each operation improves readability.

## Concurrency and ownership

A local value builder naturally has single-owner semantics and can cross tasks when all stored fields are `Sendable`. Avoid sharing a mutable class builder across tasks. Build first, then pass the immutable result. If construction requires actor-isolated data, perform that lookup in an isolated service and give the builder resolved values rather than smuggling actor access into synchronous methods.

## Compare

Factory Method selects which concrete result to create. Abstract Factory creates several compatible products. Builder constructs one result incrementally. A result builder is a Swift language feature for transforming declarative closures; it is not automatically the GoF pattern. A configuration struct is simpler when no staged validation or assembly behavior exists.

## Example

```swift
import Foundation

struct HTTPRequest {
    let url: URL
    let method: String
    let headers: [String: String]
    let body: Data?
}

enum RequestBuildError: Error {
    case missingServer
    case invalidServer(String)
    case bodyNotAllowedForGet
}

struct HTTPRequestBuilder {
    private var serverAddress: String?
    private var path = ""
    private var method = "GET"
    private var headers: [String: String] = [:]
    private var body: Data?

    func server(_ address: String) -> Self {
        var copy = self
        copy.serverAddress = address
        return copy
    }

    func route(_ path: String) -> Self {
        var copy = self
        copy.path = path
        return copy
    }

    func postJSON(_ data: Data) -> Self {
        var copy = self
        copy.method = "POST"
        copy.body = data
        copy.headers["Content-Type"] = "application/json"
        return copy
    }

    func authorization(bearer token: String) -> Self {
        var copy = self
        copy.headers["Authorization"] = "Bearer \(token)"
        return copy
    }

    func build() throws -> HTTPRequest {
        guard let serverAddress else { throw RequestBuildError.missingServer }
        guard
            let baseURL = URL(string: serverAddress),
            baseURL.scheme == "https",
            baseURL.host != nil
        else {
            throw RequestBuildError.invalidServer(serverAddress)
        }
        guard method != "GET" || body == nil else {
            throw RequestBuildError.bodyNotAllowedForGet
        }
        return HTTPRequest(
            url: baseURL.appendingPathComponent(path),
            method: method,
            headers: headers,
            body: body
        )
    }
}

let request = try HTTPRequestBuilder()
    .server("https://api.example.com")
    .route("events")
    .postJSON(Data("{}".utf8))
    .authorization(bearer: "token")
    .build()
print(request.url)
```

Each intermediate value stays local, while `build()` is the single gate to an immutable request.

## Review checklist

- Does construction contain policy beyond assigning stored properties?
- Can an initializer, configuration value, or result builder express it more directly?
- Does `build()` reject or normalize meaningful states?
- Are intermediate mutable values prevented from escaping?
- Are fluent operation names domain-specific and order assumptions explicit?
- Is the finished result safe to share under its concurrency contract?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Builder in Swift](https://refactoring.guru/design-patterns/builder/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
