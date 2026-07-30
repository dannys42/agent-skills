# Proxy

## Intent

Stand in for another object behind the same interface to control access, location, lifecycle, or identity. A Proxy decides how and whether an operation reaches the real subject while allowing clients to depend on the subject’s capability rather than those access mechanics.

## Prefer Swift-native alternatives when

Use an actor-isolated cache when the only requirement is safe memoization. Put a direct permission check at a clear use-case boundary when there is one caller. An explicit wrapper with a narrowly named capability is often better than reproducing a large service protocol. Property wrappers can mediate stored-property access, but they are not a substitute for service-level authorization.

## Choose this pattern when

Choose Proxy when many clients need the same subject interface but access requires consistent authorization, lazy creation, remote transport, auditing, or lifecycle control. A permission-aware image repository can reject requests before touching storage while remaining substitutable anywhere the repository interface is expected. The proxy should have one clear access responsibility.

## Avoid it when

Avoid Proxy when the wrapper merely adds optional presentation or instrumentation—that is closer to Decorator. Do not hide network latency behind a synchronous-looking API or conceal surprising retries and caching. If all you need is a cache, an actor owning a dictionary and loader is clearer. Avoid protocols with broad forwarding surfaces that make every subject change ripple through shallow wrappers.

## Design pressures

Look for authorization checks copied into every repository caller, expensive subjects constructed even when access is denied, or remote details leaking across the domain. The strongest signal is a policy that must be applied uniformly before a subject operation. Verify that substitution is useful; sometimes a separate authorization service called explicitly is more honest.

## Swift implementation

Define the smallest subject protocol consumers require. Store the real subject and the access policy in the proxy, check policy first, then delegate without changing successful results. Name the wrapper for its responsibility, such as `PermissionCheckingImageRepository`, so access behavior is discoverable. If operations are remote, declare them `async throws` in the protocol itself rather than adapting later.

## Concurrency and ownership

A proxy does not make its subject thread-safe. Preserve the subject’s actor isolation and sendability requirements. Mutable access logs, lazy subjects, and caches need their own actor or another clear owner. Avoid a check-then-use race: authorization that can change concurrently may need to be validated by the same isolated authority that performs the operation.

## Compare

Decorator adds optional responsibilities and encourages stacking; Proxy represents or controls a subject and commonly owns an access decision. Adapter changes an incompatible interface. Facade presents a simpler workflow and need not preserve a subsystem interface. An actor-isolated cache solves shared mutable memoization directly; it is only a Proxy when it deliberately stands in for the same subject contract and governs subject access.

## Example

```swift
struct ImageRecord: Equatable {
    let identifier: String
    let bytes: [UInt8]
}

protocol ImageRepository {
    func image(identifier: String) throws -> ImageRecord
}

enum ImageAccessError: Error {
    case forbidden(String)
    case missing(String)
}

struct StoredImageRepository: ImageRepository {
    let images: [String: ImageRecord]

    func image(identifier: String) throws -> ImageRecord {
        guard let image = images[identifier] else {
            throw ImageAccessError.missing(identifier)
        }
        return image
    }
}

struct PermissionCheckingImageRepository: ImageRepository {
    let subject: any ImageRepository
    let permittedIdentifiers: Set<String>

    func image(identifier: String) throws -> ImageRecord {
        guard permittedIdentifiers.contains(identifier) else {
            throw ImageAccessError.forbidden(identifier)
        }
        return try subject.image(identifier: identifier)
    }
}

let stored = StoredImageRepository(
    images: [
        "public-cover": ImageRecord(
            identifier: "public-cover",
            bytes: [137, 80, 78, 71]
        )
    ]
)
let repository = PermissionCheckingImageRepository(
    subject: stored,
    permittedIdentifiers: ["public-cover"]
)
let image = try repository.image(identifier: "public-cover")
print(image.bytes.count)
```

The proxy checks the access rule before delegating to storage and returns the subject’s value unchanged. A production repository might make the shared interface asynchronous, but should keep authorization visible through thrown errors.

## Review checklist

- Must clients use the same interface as the controlled subject?
- Is access, location, lifecycle, or identity the wrapper’s clear responsibility?
- Would an explicit check or actor-isolated cache be simpler?
- Are latency, failure, retries, and caching semantics visible?
- Can authorization and use race with one another?
- Is the subject’s isolation preserved rather than assumed?
- Is this control of access rather than stackable behavior augmentation?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Proxy in Swift](https://refactoring.guru/design-patterns/proxy/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
