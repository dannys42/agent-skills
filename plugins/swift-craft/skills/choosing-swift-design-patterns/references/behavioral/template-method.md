# Template Method

## Intent

Define a stable algorithm sequence while allowing selected steps to vary. Traditional inheritance is one implementation, but Swift usually expresses the same intent more clearly through protocol requirements, default implementations, and composed functions.

## Prefer Swift-native alternatives when

Use a plain function that accepts step closures when there are one or two variations. Compose independent parser, validator, and writer values when steps should vary separately. A protocol extension can supply the invariant algorithm while conformers implement required steps, avoiding a base class and override rules.

## Choose this pattern when

Choose Template Method when every variant must follow the same ordered pipeline and only specific hooks differ. A data importer might always read, decode, validate, normalize, and store records while CSV and line-based importers vary decoding. Keeping orchestration once prevents a conformer from accidentally storing before validation.

## Avoid it when

Avoid inheritance solely to share a ten-line procedure. Fragile base classes make it unclear which methods are safe to override and can couple subclasses to hidden state. Do not use a fixed skeleton when products need arbitrary reordering; composition is more flexible. If the entire algorithm varies as one interchangeable unit, Strategy is the closer model.

## Design pressures

Look for several implementations that duplicate control flow but differ at named steps. Separate invariant ordering from genuinely variable behavior. Decide which hooks are required, optional, or forbidden to override. Error and cancellation behavior belong to the template contract, not to ad hoc conformer choices.

## Swift implementation

Put the template operation in a protocol extension and make variable steps protocol requirements. Keep intermediate values explicit and favor associated types when stages carry domain-specific data. If callers need heterogeneous importers, a type-erased wrapper may be justified; otherwise retain generic types. Composition can replace the protocol entirely when each stage should be independently configurable.

## Concurrency and ownership

An asynchronous template should use structured calls to its steps and propagate cancellation and errors. Do not launch unstructured tasks for stages whose order is the central invariant. Mutable importer dependencies need an isolation owner. Associated values crossing actors should be `Sendable` when required by the host’s concurrency boundary; confirm language mode and default isolation before prescribing annotations.

## Compare

Protocol extensions are the Swift-native vehicle for many Template Methods. Composition exposes stages as dependencies and allows more reordering. Strategy replaces an algorithm as a whole. Builder incrementally assembles a result, while Template Method governs a fixed processing sequence. Factory Method varies object creation at one step.

## Example

```swift
import Foundation

struct ImportRecord: Equatable {
    let identifier: Int
    let name: String
}

enum ImportError: Error {
    case malformedLine(String)
    case emptyName(Int)
}

protocol DataImporter {
    func decode(_ input: String) throws -> [ImportRecord]
    func store(_ records: [ImportRecord]) throws
}

extension DataImporter {
    func run(input: String) throws {
        let decoded = try decode(input)
        let normalized = decoded.map {
            ImportRecord(
                identifier: $0.identifier,
                name: $0.name.trimmingCharacters(in: .whitespaces)
            )
        }
        for record in normalized where record.name.isEmpty {
            throw ImportError.emptyName(record.identifier)
        }
        try store(normalized)
    }
}

struct LineImporter: DataImporter {
    let save: ([ImportRecord]) throws -> Void

    func decode(_ input: String) throws -> [ImportRecord] {
        try input.split(separator: "\n").map { line in
            let fields = line.split(separator: ",", maxSplits: 1)
            guard
                fields.count == 2,
                let identifier = Int(fields[0])
            else {
                throw ImportError.malformedLine(String(line))
            }
            return ImportRecord(
                identifier: identifier,
                name: String(fields[1])
            )
        }
    }

    func store(_ records: [ImportRecord]) throws {
        try save(records)
    }
}

var stored: [ImportRecord] = []
let importer = LineImporter { stored = $0 }
try importer.run(input: "1, Ada\n2, Grace")
print(stored.count)
```

The extension fixes normalization and validation order while decoding and storage remain explicit requirements. If those stages also need arbitrary replacement and reordering, separate composed stage values would be clearer than expanding the protocol.

## Review checklist

- Is the algorithm order genuinely invariant?
- Would a function with closures or composed stages be simpler?
- Are variable steps explicit protocol requirements?
- Can conformers bypass required validation or cleanup?
- Are error and cancellation semantics consistent?
- Is inheritance being introduced where a protocol extension suffices?
- Does Strategy better describe whole-algorithm replacement?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Template Method in Swift](https://refactoring.guru/design-patterns/template-method/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
