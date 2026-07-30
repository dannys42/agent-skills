# Command

## Intent

Represent an operation as a value with enough information to execute it later and, when required, reverse it. This separates the object requesting work from the operation’s receiver and enables queues, history, replay, undo, and redo.

## Prefer Swift-native alternatives when

Use a closure when a caller needs one deferred action and does not inspect, persist, undo, or replay it. Register an undo closure with Foundation’s `UndoManager` when platform-integrated undo grouping and responder-chain behavior already match the product. A direct method call remains clearest when timing and receiver are immediate.

## Choose this pattern when

Choose Command when operations need stable identity or data beyond invocation. Reversible text editing is a strong fit because each edit can record its location, inserted content, and expected removed content, then move between undo and redo stacks. A named command also permits logging, coalescing, and deterministic replay.

## Avoid it when

Avoid a type per trivial button tap. Do not claim undoability unless the command captures all state needed for a correct inverse. Reject a replay whose recorded location or expected content no longer matches the receiver; applying it to stale state can silently edit the wrong text. Commands that retain entire object graphs can make history unexpectedly expensive. Persistence is unsafe when commands embed process-only references or closures.

## Design pressures

Look for actions that outlive their initiating call, require audit records, or move through undo and redo history. Decide whether commands are repeatable and whether failures enter history. Establish whether undo restores an exact prior state or performs a compensating action; remote side effects often support only the latter.

## Swift implementation

Value-type commands work well when they capture immutable edit data. Give execution an explicit receiver parameter so commands do not retain the editor unnecessarily. Validate recorded coordinates and expected receiver content before mutation. For reversible operations, return the inverse generated from the actual pre-edit state, and update history only after execution succeeds. An enum with associated values provides an exhaustive command set for a closed domain.

## Concurrency and ownership

The history owner should be singular. UI editing history commonly belongs to a main-actor model because it mutates UI-observed state, while a non-UI document service may use its own actor. Do not mark every command `Sendable` by assumption: receiver references and captured closures may not cross isolation safely. Preserve command order, and define cancellation before placing asynchronous commands in a queue.

## Compare

A closure is compact but usually opaque and has no inherent inverse. `UndoManager` supplies mature platform history behavior and may be the best receiver for simple app edits. Memento stores state snapshots rather than intent. Strategy supplies interchangeable algorithms for an immediate operation. Command records “perform this action,” often with timing and history semantics.

## Example

```swift
struct TextDocument {
    private(set) var text: String

    mutating func replace(
        range: Range<String.Index>,
        with replacement: String
    ) -> String {
        let removed = String(text[range])
        text.replaceSubrange(range, with: replacement)
        return removed
    }
}

enum TextEditError: Error {
    case invalidRange(offset: Int, removedCount: Int)
    case staleContent(expected: String, actual: String)
}

struct TextEdit {
    let offset: Int
    let removed: String
    let inserted: String

    func apply(to document: inout TextDocument) throws -> TextEdit {
        guard
            offset >= 0,
            let start = document.text.index(
                document.text.startIndex,
                offsetBy: offset,
                limitedBy: document.text.endIndex
            ),
            let end = document.text.index(
                start,
                offsetBy: removed.count,
                limitedBy: document.text.endIndex
            )
        else {
            throw TextEditError.invalidRange(
                offset: offset,
                removedCount: removed.count
            )
        }

        let currentContent = String(document.text[start..<end])
        guard currentContent == removed else {
            throw TextEditError.staleContent(
                expected: removed,
                actual: currentContent
            )
        }

        let actualRemoved = document.replace(
            range: start..<end,
            with: inserted
        )
        return TextEdit(
            offset: offset,
            removed: inserted,
            inserted: actualRemoved
        )
    }
}

struct EditHistory {
    private(set) var document: TextDocument
    private var undoStack: [TextEdit] = []
    private var redoStack: [TextEdit] = []

    init(document: TextDocument) {
        self.document = document
    }

    mutating func perform(_ edit: TextEdit) throws {
        let inverse = try edit.apply(to: &document)
        undoStack.append(inverse)
        redoStack.removeAll()
    }

    mutating func undo() throws {
        guard let inverse = undoStack.popLast() else { return }
        do {
            let redo = try inverse.apply(to: &document)
            redoStack.append(redo)
        } catch {
            undoStack.append(inverse)
            throw error
        }
    }

    mutating func redo() throws {
        guard let edit = redoStack.popLast() else { return }
        do {
            let inverse = try edit.apply(to: &document)
            undoStack.append(inverse)
        } catch {
            redoStack.append(edit)
            throw error
        }
    }
}

var history = EditHistory(document: TextDocument(text: "Swift code"))
try history.perform(
    TextEdit(offset: 6, removed: "code", inserted: "patterns")
)
try history.undo()
try history.redo()
print(history.document.text)
```

Each edit verifies that its character offset is in bounds and that the recorded old text still matches before mutation. It then produces an inverse from the content it actually replaced. Failed undo or redo restores the popped command to its original stack. Production editors should use one documented coordinate system consistently; integer character offsets are deliberately simple here, not a recommendation for large text storage.

## Review checklist

- Must actions be queued, replayed, logged, undone, or redone?
- Would a closure or `UndoManager` meet the need with less machinery?
- Does every reversible command capture a correct inverse?
- Does execution reject stale content and invalid coordinates before mutation?
- Who owns command ordering and history?
- Do failed perform, undo, and redo operations preserve history coherently?
- Can retained receivers or snapshots make history expensive?
- Are cross-actor commands genuinely `Sendable`?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Command in Swift](https://refactoring.guru/design-patterns/command/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
