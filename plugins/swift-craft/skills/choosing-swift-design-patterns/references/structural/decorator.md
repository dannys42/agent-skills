# Decorator

## Intent

Add behavior around a component while preserving its interface, allowing responsibilities to be layered without multiplying subclasses. Each decorator handles one concern and delegates the core operation to the next component.

## Prefer Swift-native alternatives when

Compose closures for a single operation such as request middleware. A protocol extension is clearer when behavior should apply uniformly and needs no stored wrapped component. Use a property wrapper for local stored-property access semantics, not as a general object decorator. These tools often preserve the useful layering while avoiding a family of forwarding types.

## Choose this pattern when

Choose Decorator when several optional behaviors must be combined in different orders, each behavior surrounds the same operation, and clients should remain unaware of the concrete stack. Request logging, metrics, retry policy, and header enrichment are typical pressures. A named decorator type earns its cost when it owns configuration, state, or independently testable policy.

## Avoid it when

Avoid Decorator when one extension method or a short closure pipeline is enough. Do not create wrappers whose only purpose is forwarding every protocol member. Deep stacks can hide execution order and error behavior, so composition should remain visible at one boundary. If the wrapper controls access to a remote or expensive subject rather than adding an optional responsibility, it is probably a Proxy.

## Design pressures

Look for subclasses representing combinations such as logged-and-retried-and-authorized clients, flags that produce tangled branching around one call, or cross-cutting behavior copied into multiple senders. Decorator fits when every layer can be expressed as “before, delegate, after.” Middleware closure composition is often the most compact Swift expression of that same pressure.

## Swift implementation

Start with a function type when the interface has one operation. A middleware is a function that accepts and returns that handler, making order explicit at assembly. Use protocols and concrete decorator structs when the interface has several related operations or layers need discoverable identities. Avoid unnecessary `class` inheritance; structs containing closures work well when captures have clear lifetimes.

## Concurrency and ownership

Captured mutable state can make a closure pipeline unsafe across tasks. Mark handlers and middleware `@Sendable` when crossing concurrency domains, and place counters or mutable caches in actors. Retry and logging layers must preserve cancellation and must not accidentally repeat non-idempotent work. Wrapping a component does not upgrade its sendability.

## Compare

Proxy preserves an interface to control access, location, identity, or lifecycle; it often decides whether the subject runs at all. Decorator adds optional responsibilities and is intentionally stackable. Adapter changes the interface. Chain of Responsibility gives multiple handlers a chance to handle or pass a request, whereas Decorator middleware normally delegates through every layer. Closure composition is usually the Swift-native implementation to try first.

## Example

```swift
struct Request {
    var path: String
    var headers: [String: String] = [:]
}

struct Response {
    let status: Int
    let trace: [String]
}

typealias RequestHandler = (Request) -> Response
typealias Middleware = (@escaping RequestHandler) -> RequestHandler

func addingHeader(name: String, value: String) -> Middleware {
    { next in
        { request in
            var changed = request
            changed.headers[name] = value
            return next(changed)
        }
    }
}

func tracing(_ label: String) -> Middleware {
    { next in
        { request in
            let response = next(request)
            return Response(
                status: response.status,
                trace: [label] + response.trace
            )
        }
    }
}

func apply(
    _ middleware: [Middleware],
    to terminal: @escaping RequestHandler
) -> RequestHandler {
    middleware.reversed().reduce(terminal) { next, layer in
        layer(next)
    }
}

let transport: RequestHandler = { request in
    Response(
        status: request.headers["Authorization"] == nil ? 401 : 200,
        trace: ["transport"]
    )
}

let send = apply(
    [tracing("metrics"), addingHeader(name: "Authorization", value: "token")],
    to: transport
)
print(send(Request(path: "/events")))
```

Each closure preserves the handler interface and wraps the next operation. Named protocol decorators would be appropriate if the request client exposed a larger cohesive API.

## Review checklist

- Are optional responsibilities being combined around one interface?
- Would a closure pipeline or protocol extension be simpler?
- Is composition order visible and tested?
- Does every layer preserve errors, cancellation, and return semantics?
- Are stateful captures isolated under concurrency?
- Is the wrapper augmenting behavior rather than controlling access?
- Would a growing forwarding surface make the abstraction too shallow?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Decorator in Swift](https://refactoring.guru/design-patterns/decorator/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
