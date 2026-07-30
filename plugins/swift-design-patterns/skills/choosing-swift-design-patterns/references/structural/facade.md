# Facade

## Intent

Provide a focused entry point for a recurring subsystem workflow. A Facade hides coordination details and presents operations named in the client’s domain while leaving lower-level components available to clients that genuinely need them.

## Prefer Swift-native alternatives when

Call a few well-named values directly when the composition is short and appears once. Extract a focused service or free function when one use case needs coordination; in Swift, that service is often the Facade without requiring a special hierarchy. Prefer explicit injected dependencies over a global utility. The goal is a useful boundary, not a type named `Manager`.

## Choose this pattern when

Choose Facade when multiple clients repeat the same sequence across several subsystem APIs, sequencing and error policy belong in one place, or callers are coupled to details they should not understand. Media import is a good fit when loading, format detection, metadata extraction, and persistence must follow one reliable workflow.

## Avoid it when

Avoid Facade when it only forwards one call or when different clients require genuinely different workflows. Do not let it become a miscellaneous “manager” with unrelated responsibilities. A Facade should not conceal dependencies through singletons, swallow meaningful errors, or prevent advanced callers from using subsystem APIs directly.

## Design pressures

Look for three or more call sites repeating steps in slightly different orders, inconsistent validation or cleanup, and features importing many low-level modules solely to perform one use case. The boundary is strongest when it reduces conceptual load and owns a cohesive policy. Continual unrelated method growth suggests several use-case services rather than one facade.

## Swift implementation

Create a small service whose initializer receives the subsystem capabilities it coordinates. Its methods should use application language such as `importMedia`, not mirror low-level methods. Concrete value dependencies are enough when substitution is unnecessary; protocols or closures can provide test seams at real I/O boundaries. Preserve useful result and error information rather than collapsing every failure to a Boolean.

## Concurrency and ownership

Coordination does not imply ownership of all subsystem state. Keep file, decoder, and store isolation contracts explicit. An asynchronous facade can sequence actor calls and use structured concurrency for truly independent work, but it should not detach tasks or hide cancellation. If it owns mutable workflow state, isolate the service or keep each invocation’s state local.

## Compare

Adapter translates one incompatible interface; Facade offers a simpler workflow over one or more compatible subsystem interfaces. Mediator governs ongoing communication among peer objects, while a Facade is a one-way entry point clients call. A generic `Manager` often accumulates unrelated operations; a good Facade is named for a cohesive capability. Coordinator can describe UI navigation or orchestration, but the same depth test applies.

## Example

```swift
struct MediaFile {
    let name: String
    let bytes: [UInt8]
}

struct ImportedMedia {
    let identifier: Int
    let format: String
    let title: String
}

struct FormatDetector {
    func detect(_ file: MediaFile) -> String {
        file.name.hasSuffix(".wav") ? "audio/wav" : "application/octet-stream"
    }
}

struct MetadataExtractor {
    func title(from file: MediaFile) -> String {
        file.name.split(separator: ".").dropLast().joined(separator: ".")
    }
}

final class MediaStore {
    private var nextIdentifier = 1

    func save(format: String, title: String) -> ImportedMedia {
        defer { nextIdentifier += 1 }
        return ImportedMedia(
            identifier: nextIdentifier,
            format: format,
            title: title
        )
    }
}

struct MediaImportService {
    let detector: FormatDetector
    let metadata: MetadataExtractor
    let store: MediaStore

    func importMedia(_ file: MediaFile) -> ImportedMedia {
        let format = detector.detect(file)
        let title = metadata.title(from: file)
        return store.save(format: format, title: title)
    }
}

let importer = MediaImportService(
    detector: FormatDetector(),
    metadata: MetadataExtractor(),
    store: MediaStore()
)
let result = importer.importMedia(
    MediaFile(name: "interview.wav", bytes: [82, 73, 70, 70])
)
print("\(result.identifier): \(result.title)")
```

Clients ask for one media-import use case. The detector, extractor, and store remain separate collaborators rather than becoming hidden methods on a broad manager.

## Review checklist

- Is a cohesive subsystem workflow repeated across clients?
- Would direct composition remain clearer at the current scale?
- Are dependencies passed explicitly?
- Does the API use client-domain language and preserve useful errors?
- Can advanced code still access lower-level capabilities when appropriate?
- Is the type focused, or is it becoming a generic manager?
- Is this an entry point rather than peer-to-peer mediation?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Facade in Swift](https://refactoring.guru/design-patterns/facade/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
