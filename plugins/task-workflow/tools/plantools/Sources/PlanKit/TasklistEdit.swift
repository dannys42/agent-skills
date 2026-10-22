import Foundation

/// Bad arguments, independent of the file's content (exit 2).
public struct EditUsageError: Error, CustomStringConvertible {
    public let description: String
    public init(_ description: String) { self.description = description }
}

/// The result of one editing command: the new file text and what to tell the caller.
public struct Edit {
    public var text: String
    public var summary: String
    public var result: String?          // printed instead of the summary, e.g. the new task ID
    public var warnings: [String]
    public var changed: Bool
}

/// Default named model per tier. Keep in step with the tasklist skill's "Minimum model tiers" table
/// (a test reads the skill and fails when they differ).
public let tierModels: [(tier: String, model: String)] = [
    ("light", "Haiku 4.5"), ("standard", "Sonnet 5.5"), ("heavy", "Opus 5.5"),
]

public struct NewTask {
    public var title: String
    public var under: String?
    public var before: String?
    public var tier: String?
    public var modelName: String?
    public var needs: [String] = []
    public var context: String?
    public var doneWhen: String?
    public var user = false
    public var steps: [String] = []

    public init(title: String, under: String? = nil, before: String? = nil, tier: String? = nil, modelName: String? = nil,
                needs: [String] = [], context: String? = nil, doneWhen: String? = nil, user: Bool = false, steps: [String] = []) {
        self.title = title; self.under = under; self.before = before; self.tier = tier; self.modelName = modelName
        self.needs = needs; self.context = context; self.doneWhen = doneWhen; self.user = user; self.steps = steps
    }
}

public enum SettableField: String, CaseIterable {
    case title, model, run, verify, doneWhen = "done-when", notes, context

    var key: String { self == .doneWhen ? "done when" : rawValue }
    /// Rewriting these needs an open task nobody has claimed; `model` and `notes` stay editable while IN-PROGRESS.
    var needsUnclaimedTask: Bool { ![.model, .notes].contains(self) }
    var canAppend: Bool { self == .context || self == .notes }
}

// MARK: - Field lines

extension Tasklist {
    struct FieldSpan {
        let key: String         // lowercased, may contain spaces ("done when")
        let start: Int          // 0-based line index of the `  - Key:` line
        var end: Int            // 0-based, inclusive: last continuation line
        let indent: String
        let head: String        // through the colon, as written
        let value: String       // text after the colon on the first line
    }

    /// Where a new field goes when absent: after the last present field that precedes it in this order.
    static let fieldOrder = ["why", "model", "needs", "context", "steps", "run", "verify", "done when", "notes"]

    static func display(_ key: String) -> String {
        key == "done when" ? "Done when" : key.prefix(1).uppercased() + key.dropFirst()
    }

    /// Like `parseField`, but keys may hold spaces ("Done when") and must be words.
    static func fieldHead(_ line: String) -> (indent: String, key: String, head: String, value: String)? {
        let indent = line.prefix(while: { $0 == " " })
        guard (2...3).contains(indent.count) else { return nil }
        let body = line.dropFirst(indent.count)
        guard body.hasPrefix("- "), let colon = body.firstIndex(of: ":") else { return nil }
        let raw = body[body.index(body.startIndex, offsetBy: 2)..<colon]
        guard !raw.isEmpty, raw.count <= 24, raw.first != " ", raw.allSatisfy({ $0.isLetter || $0 == " " || $0 == "-" }) else { return nil }
        let head = String(line.prefix(indent.count + body.distance(from: body.startIndex, to: colon) + 1))
        return (String(indent), raw.lowercased(), head, body[body.index(after: colon)...].trimmingCharacters(in: .whitespaces))
    }

    func spans(of task: TaskItem) -> [FieldSpan] {
        var out: [FieldSpan] = []
        for index in task.line..<task.endLine {
            if let head = Tasklist.fieldHead(markdown.lines[index]) {
                out.append(FieldSpan(key: head.key, start: index, end: index, indent: head.indent, head: head.head, value: head.value))
            } else if !out.isEmpty {
                out[out.count - 1].end = index
            }
        }
        return out
    }

    func uniqueSpan(_ key: String, in spans: [FieldSpan], of task: TaskItem) throws -> FieldSpan? {
        let hits = spans.filter { $0.key == key }
        if hits.count > 1 { throw EditError.refused("\(task.id) has \(hits.count) \(Tasklist.display(key)): lines; fix it by hand first") }
        return hits.first
    }

    /// 0-based line index at which a new `key` field is inserted.
    func insertionIndex(for key: String, spans: [FieldSpan], task: TaskItem) -> Int {
        let order = Tasklist.fieldOrder
        guard let rank = order.firstIndex(of: key) else { return task.endLine }
        if let previous = spans.last(where: { order.firstIndex(of: $0.key).map { $0 < rank } ?? false }) { return previous.end + 1 }
        if let next = spans.first(where: { order.firstIndex(of: $0.key).map { $0 > rank } ?? false }) { return next.start }
        return task.endLine
    }

    func fieldLine(_ key: String, _ value: String, spans: [FieldSpan]) -> String {
        "\(spans.first?.indent ?? "  ")- \(Tasklist.display(key)): \(value)"
    }

    // MARK: Title line

    /// The task line split into the part before the title, the title, and any trailing space.
    func titleParts(of task: TaskItem) -> (prefix: String, title: String, suffix: String) {
        let line = markdown.lines[task.line - 1]
        guard !task.title.isEmpty, let range = line.range(of: task.title, options: .backwards) else {
            return (line.trimmingCharacters(in: .whitespaces) + " ", "", "")
        }
        return (String(line[..<range.lowerBound]), task.title, String(line[range.upperBound...]))
    }

    static func titleLine(mark: Character, id: String, qualifiers: [String], title: String) -> String {
        let head = "- [\(mark)] \(id)"
        return qualifiers.isEmpty ? "\(head) \(title)" : "\(head) \(qualifiers.joined(separator: " ")) — \(title)"
    }

    /// Qualifiers worth keeping on a line: `USER` always, BLOCKED and IN-PROGRESS only while open.
    func qualifiers(of task: TaskItem, open: Bool, reason: String?) -> [String] {
        var out: [String] = []
        if task.user { out.append("USER") }
        if open, let blocked = task.blocked { out.append("BLOCKED(\(blocked))") }
        if open, task.inProgress { out.append("IN-PROGRESS") }
        if let reason { out.append(reason) }
        return out
    }

    // MARK: Pipeline

    /// Re-parses `lines`, and refuses the edit when lint reports an error the file did not already have
    /// or an ID has gone. Warnings that are new come back on the result.
    func finish(_ lines: [String], summary: String, unchanged: String? = nil, result: String? = nil, warnings: [String] = []) throws -> Edit {
        let text = lines.joined(separator: "\n")
        if text == markdown.lines.joined(separator: "\n") {
            return Edit(text: text, summary: unchanged ?? "unchanged", result: nil, warnings: warnings, changed: false)
        }
        let after = Tasklist(text: text)
        let ids = Set(headings.map(\.id) + tasks.map(\.id)), idsAfter = Set(after.headings.map(\.id) + after.tasks.map(\.id))
        if !ids.isSubset(of: idsAfter) {
            throw EditError.refused("the edit would drop \(ids.subtracting(idsAfter).sorted().joined(separator: ", ")); nothing written")
        }
        let before = lint(), now = after.lint()
        let oldErrors = Set(before.filter { $0.severity == .error }.map(\.message))
        let newErrors = now.filter { $0.severity == .error && !oldErrors.contains($0.message) }
        if !newErrors.isEmpty { throw EditError.lint(newErrors.map(\.rendered)) }
        let oldWarnings = Set(before.filter { $0.severity == .warning }.map(\.message))
        let newWarnings = now.filter { $0.severity == .warning && !oldWarnings.contains($0.message) }.map(\.rendered)
        return Edit(text: text, summary: summary, result: result, warnings: warnings + newWarnings, changed: true)
    }

    static func singleLine(_ text: String, _ what: String) throws -> String {
        let trimmed = text.trimmingCharacters(in: .whitespaces)
        if trimmed.isEmpty { throw EditUsageError("\(what) is empty") }
        if trimmed.contains("\n") { throw EditUsageError("\(what) must be one line; use --append to add another line") }
        return trimmed
    }

    static func isoDate(_ text: String) -> Bool {
        let parts = text.split(separator: "-", omittingEmptySubsequences: false)
        guard parts.count == 3, parts[0].count == 4, parts[1].count == 2, parts[2].count == 2,
              let y = Int(parts[0]), let m = Int(parts[1]), let d = Int(parts[2]) else { return false }
        let calendar = Calendar(identifier: .gregorian)
        guard let date = calendar.date(from: DateComponents(year: y, month: m, day: d)) else { return false }
        let back = calendar.dateComponents([.year, .month, .day], from: date)
        return back.year == y && back.month == m && back.day == d
    }

    public static func today() -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: Date())
    }

    /// `<why> (<date>)`, the shape lint wants in a `Why:` line.
    static func note(_ why: String, date: String) throws -> String {
        guard isoDate(date) else { throw EditUsageError("--date must be a real date as YYYY-MM-DD, got \(date)") }
        return "\(try singleLine(why, "--why")) (\(date))"
    }

    func requireOpenTask(_ id: String, doing: String) throws -> TaskItem {
        guard let task = task(id) else {
            throw heading(id) == nil ? EditError.unknown(id) : EditError.refused("\(id) is a heading; \(doing) works on tasks")
        }
        guard task.mark == .open else {
            throw EditError.refused("\(id) is closed ([\(task.mark == .done ? "x" : "-")]); closed items are not rewritten, add a new task instead")
        }
        return task
    }

    // MARK: - needs

    /// Adds and removes `Needs` edges on one open task. Adding an edge that exists, or removing one that does not, changes nothing.
    public func editingNeeds(_ id: String, add: [String], remove: [String]) throws -> Edit {
        if let both = add.first(where: remove.contains) { throw EditUsageError("\(both) is in both --add and --remove") }
        for other in add + remove where !isID(other, prefixes: "T") { throw EditUsageError("\(other) is not a task ID") }
        let target = try requireOpenTask(id, doing: "needs")
        let missing = add.filter { task($0) == nil }
        if !missing.isEmpty { throw EditError.refused("\(missing.joined(separator: ", ")) does not exist; nothing written") }

        let spans = spans(of: target)
        let span = try uniqueSpan("needs", in: spans, of: target)
        if let span, span.end != span.start { throw EditError.refused("\(id) has a Needs: spanning several lines; edit it by hand") }
        let old = (span?.value ?? "").split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }.filter { !$0.isEmpty }
        func word(_ token: String) -> String { token.split(separator: " ").first.map(String.init) ?? token }
        var tokens = old.filter { !remove.contains(word($0)) }
        for edge in add where !tokens.contains(where: { word($0) == edge }) { tokens.append(edge) }

        var lines = markdown.lines
        if tokens == old {
            return try finish(lines, summary: "", unchanged: "\(id) needs \(old.isEmpty ? "nothing" : old.joined(separator: ", ")): no change")
        }
        if tokens.isEmpty, let span {
            lines.removeSubrange(span.start...span.end)
        } else if let span {
            lines[span.start] = "\(span.head) \(tokens.joined(separator: ", "))"
        } else {
            lines.insert(fieldLine("needs", tokens.joined(separator: ", "), spans: spans), at: insertionIndex(for: "needs", spans: spans, task: target))
        }
        let rewritten = Tasklist(text: lines.joined(separator: "\n"))
        if findCycle() == nil, let cycle = rewritten.findCycle() {
            throw EditError.refused("that would create a dependency cycle: \(cycle.joined(separator: " → ")); nothing written")
        }
        return try finish(lines, summary: tokens.isEmpty ? "\(id) needs nothing now" : "\(id) needs \(tokens.joined(separator: ", "))")
    }

    // MARK: - close, reopen

    /// `[-]` with a reason word and a dated `Why:`. On a phase or group heading it appends ` — WORD` and puts the `Why:` under the Goal.
    public func closing(_ id: String, reason: String, by: [String] = [], why: String, date: String, userConfirmed: Bool = false) throws -> Edit {
        guard reasonWords.contains(reason) else { throw EditUsageError("--reason must be one of \(reasonWords.joined(separator: ", "))") }
        if reason == "SUPERSEDED", by.isEmpty { throw EditUsageError("SUPERSEDED needs --by <ID> naming the task that takes over") }
        if reason != "SUPERSEDED", !by.isEmpty { throw EditUsageError("--by goes only with --reason SUPERSEDED") }
        let note = try Tasklist.note(why, date: date)
        let token = reason == "SUPERSEDED" ? "SUPERSEDED→" + by.joined(separator: ",") : reason
        for target in by {
            if target == id { throw EditError.refused("\(id) cannot supersede itself") }
            if task(target) == nil, heading(id) == nil || heading(target) == nil { throw EditError.refused("\(target) does not exist; nothing written") }
        }
        if let heading = heading(id) { return try closingHeading(heading, token: token, reason: reason, note: note, userConfirmed: userConfirmed) }

        guard let target = task(id) else { throw EditError.unknown(id) }
        if target.mark == .done { throw EditError.refused("\(id) is [x]: done items are not closed") }
        if target.mark == .closed { throw EditError.alreadyClosed(id) }
        if target.user, !userConfirmed { throw EditError.userTask(id) }

        var lines = markdown.lines
        let spans = spans(of: target)
        if let old = try uniqueSpan("why", in: spans, of: target) {
            if old.end != old.start { throw EditError.refused("\(id) has a Why: spanning several lines; edit it by hand") }
            lines[old.start] = "\(old.head) \(note)" + (old.value.isEmpty ? "" : "; was: \(old.value)")
        } else {
            lines.insert(fieldLine("why", note, spans: spans), at: insertionIndex(for: "why", spans: spans, task: target))
        }
        let parts = titleParts(of: target)
        lines[target.line - 1] = Tasklist.titleLine(mark: "-", id: id, qualifiers: qualifiers(of: target, open: false, reason: token), title: parts.title) + parts.suffix
        return try finish(lines, summary: "closed \(id) \(token)")
    }

    private func closingHeading(_ heading: Heading, token: String, reason: String, note: String, userConfirmed: Bool) throws -> Edit {
        if let already = heading.reason { throw EditError.refused("\(heading.id) is already closed (\(already))") }
        let under = tasks.filter { heading.id.hasPrefix("P") ? $0.phase == heading.id : $0.group == heading.id }
        let open = under.filter { $0.mark == .open }
        if open.isEmpty { throw EditError.refused("nothing is open under \(heading.id); there is nothing to close") }
        let users = open.filter(\.user).map(\.id)
        if !users.isEmpty, !userConfirmed {
            throw EditError.refused("\(heading.id) holds open USER tasks (\(users.joined(separator: ", "))): pass --confirmed once the user has agreed to drop them")
        }
        var lines = markdown.lines
        // Why goes under the Goal line, or straight under the heading when there is none.
        var after = heading.line  // 0-based index just past the heading line
        var insert = ["Why: \(note)"]
        if heading.goal != nil, let goal = (heading.line..<heading.endLine).first(where: { lines[$0].hasPrefix("Goal:") }) {
            after = goal + 1
        } else if after < lines.count, lines[after].trimmingCharacters(in: .whitespaces).isEmpty {
            insert = ["", "Why: \(note)"]
        }
        lines.insert(contentsOf: insert, at: after)
        lines[heading.line - 1] = lines[heading.line - 1].trimmingCharacters(in: .whitespaces) + " — \(token)"
        let skipped = under.filter { $0.mark == .done }.count
        return try finish(lines, summary: "closed \(heading.id) \(token): \(open.count) open task(s) now sit under it, \(skipped) done task(s) untouched")
    }

    /// DEFERRED back to open: drops the word and notes why in `Why:`. A task closed without a `Model` needs one to be open again.
    public func reopening(_ id: String, why: String, date: String, tier: String? = nil, modelName: String? = nil) throws -> Edit {
        let note = try Tasklist.note(why, date: date)
        if let tier, !tierModels.contains(where: { $0.tier == tier }) { throw EditUsageError("--model must be one of \(tierModels.map(\.tier).joined(separator: ", "))") }
        if tier == nil, modelName != nil { throw EditUsageError("--model-name goes with --model") }
        if heading(id) != nil { throw EditError.refused("\(id) is a heading: remove its ' — DEFERRED' by hand") }
        guard let target = task(id) else { throw EditError.unknown(id) }
        guard target.mark == .closed else { throw EditError.refused("\(id) is not closed") }
        guard target.reason == "DEFERRED" else {
            throw EditError.refused("\(id) is \(target.reason ?? "closed"): only DEFERRED items are reopened, add a new task instead")
        }
        var lines = markdown.lines
        let spans = spans(of: target)
        if let old = try uniqueSpan("why", in: spans, of: target) {
            if old.end != old.start { throw EditError.refused("\(id) has a Why: spanning several lines; edit it by hand") }
            lines[old.start] = "\(old.head) \(note)" + (old.value.isEmpty ? "" : "; was DEFERRED: \(old.value)")
        } else {
            lines.insert(fieldLine("why", note, spans: spans), at: insertionIndex(for: "why", spans: spans, task: target))
        }
        let parts = titleParts(of: target)
        lines[target.line - 1] = Tasklist.titleLine(mark: " ", id: id, qualifiers: qualifiers(of: target, open: true, reason: nil), title: parts.title) + parts.suffix
        if tier != nil || (!target.user && target.fields["model"] == nil) {
            guard let tier else { throw EditError.refused("\(id) has no Model, which an open task needs: pass --model <light|standard|heavy>") }
            lines = try Tasklist(text: lines.joined(separator: "\n")).settingLines(id, field: .model, to: modelName.map { "\(tier) (\($0))" } ?? tier).lines
        }
        return try finish(lines, summary: "reopened \(id)")
    }

    // MARK: - add

    /// One new open task at the end of a heading's tasks (or before `before`), with the next unused T ID.
    public func adding(_ spec: NewTask) throws -> Edit {
        let title = try Tasklist.singleLine(spec.title, "--title")
        let context = try spec.context.map { try Tasklist.singleLine($0, "--context") }
        let doneWhen = try spec.doneWhen.map { try Tasklist.singleLine($0, "--done-when") }
        let steps = try spec.steps.map { try Tasklist.singleLine($0, "--step") }
        if spec.user {
            if steps.isEmpty { throw EditUsageError("--user needs at least one --step") }
            if spec.tier != nil || spec.modelName != nil { throw EditUsageError("--user tasks have no Model") }
            if steps.count > 26 { throw EditUsageError("at most 26 steps; split the task") }
        } else {
            if !steps.isEmpty { throw EditUsageError("--step goes only with --user") }
            guard let tier = spec.tier, tierModels.contains(where: { $0.tier == tier }) else {
                throw EditUsageError("--model must be one of \(tierModels.map(\.tier).joined(separator: ", "))")
            }
        }
        let needs = spec.needs.reduce(into: [String]()) { if !$0.contains($1) { $0.append($1) } }
        for need in needs where !isID(need, prefixes: "T") { throw EditUsageError("\(need) is not a task ID") }
        let missing = needs.filter { task($0) == nil }
        if !missing.isEmpty { throw EditError.refused("\(missing.joined(separator: ", ")) does not exist; nothing written") }

        var under = spec.under
        let anchor = try spec.before.map { id -> TaskItem in
            guard let found = task(id) else { throw EditError.unknown(id) }
            return found
        }
        if let anchor {
            let home = anchor.group ?? anchor.phase
            if let under, under != home { throw EditError.refused("\(anchor.id) is not under \(under)") }
            under = home
        }
        if let under, heading(under) == nil { throw EditError.refused("no group or phase \(under)") }
        if under == nil, !headings.isEmpty { throw EditError.refused("this list has groups; say which with --under <ID>") }

        let id = nextID(prefix: "T")
        var block = ["- [ ] \(id) " + (spec.user ? "USER — " : "") + title]
        if let tier = spec.tier, !spec.user {
            let name = spec.modelName ?? tierModels.first { $0.tier == tier }!.model
            block.append("  - Model: \(tier) (\(name))")
        }
        if !needs.isEmpty { block.append("  - Needs: \(needs.joined(separator: ", "))") }
        if let context { block.append("  - Context: \(context)") }
        if spec.user {
            block.append("  - Steps:")
            for (index, step) in steps.enumerated() { block.append("    \(Character(UnicodeScalar(97 + index)!)). \(step)") }
        }
        if let doneWhen { block.append("  - Done when: \(doneWhen)") }

        var lines = markdown.lines
        let separated = separatesBlocks()
        if let anchor {
            lines.insert(contentsOf: block + (separated ? [""] : []), at: anchor.line - 1)
        } else {
            let here = tasks.filter { under == nil || (heading(under!)!.id.hasPrefix("P") ? ($0.phase == under && $0.group == nil) : $0.group == under) }
            if let last = here.last {
                lines.insert(contentsOf: (separated ? [""] : []) + block, at: last.endLine)
            } else if let under, let h = heading(under) {
                let goal = h.goal == nil ? nil : (h.line..<h.endLine).first { lines[$0].hasPrefix("Goal:") }
                lines.insert(contentsOf: [""] + block, at: (goal ?? h.line - 1) + 1)
            } else {
                throw EditError.refused("the list has no task or heading to place a new task near; this tool does not create lists")
            }
        }
        let check = Tasklist(text: lines.joined(separator: "\n"))
        guard let made = check.task(id), made.title == title, made.user == spec.user, made.mark == .open,
              made.reason == nil, made.blocked == nil, !made.inProgress else {
            throw EditError.refused("that title would be read as a status word; reword it")
        }
        return try finish(lines, summary: "added \(id)", result: id)
    }

    /// Whether the list puts a blank line between task blocks (the majority style), for matching on insert.
    func separatesBlocks() -> Bool {
        var blank = 0, compact = 0
        for (previous, next) in zip(tasks, tasks.dropFirst()) {
            let gap = next.line - previous.endLine - 1
            if gap == 0 { compact += 1 } else if gap == 1, markdown.lines[next.line - 2].isEmpty { blank += 1 }
        }
        return blank >= compact
    }

    // MARK: - set

    /// Replaces (or with `append`, extends) one field of an open task. Other lines stay byte-identical.
    public func setting(_ id: String, field: SettableField, to rawText: String, append: Bool = false) throws -> Edit {
        let (lines, warnings) = try settingLines(id, field: field, to: rawText, append: append)
        return try finish(lines, summary: "\(id) \(field.rawValue) \(append ? "extended" : "set")",
                          unchanged: "\(id) \(field.rawValue) already reads that way: no change", warnings: warnings)
    }

    func settingLines(_ id: String, field: SettableField, to rawText: String, append: Bool = false) throws -> (lines: [String], warnings: [String]) {
        let text = try Tasklist.singleLine(rawText, "the new value")
        if append, !field.canAppend { throw EditUsageError("--append works only for context and notes") }
        let target = try requireOpenTask(id, doing: "set")
        if field.needsUnclaimedTask, target.inProgress {
            throw EditError.refused("\(id) is IN-PROGRESS: another agent has claimed it, so its \(field.rawValue) is not rewritten")
        }
        var lines = markdown.lines
        var warnings: [String] = []

        switch field {
        case .title:
            let parts = titleParts(of: target)
            if parts.title.isEmpty { throw EditError.refused("\(id) has no title to replace; edit it by hand") }
            lines[target.line - 1] = parts.prefix + text + parts.suffix
            let reread = Tasklist(text: lines.joined(separator: "\n")).task(id)
            guard let reread, reread.title == text, reread.user == target.user, reread.blocked == target.blocked,
                  reread.inProgress == target.inProgress, reread.reason == nil else {
                throw EditError.refused("that title would be read as a status word; reword it")
            }
            warnings = staleTitleWarnings(old: target.title, of: target)
        default:
            if field == .model, target.user { throw EditError.refused("\(id) is USER: it has no Model") }
            var value = text
            if field == .model { value = try Tasklist.modelValue(text) }
            let spans = spans(of: target)
            if let span = try uniqueSpan(field.key, in: spans, of: target) {
                if append {
                    let last = span.end == span.start ? span.value : lines[span.end].trimmingCharacters(in: .whitespaces)
                    if last != value { lines.insert("\(span.indent)  \(value)", at: span.end + 1) }
                } else if span.start != span.end || span.value != value {
                    lines.replaceSubrange(span.start...span.end, with: ["\(span.head) \(value)"])
                }
            } else {
                lines.insert(fieldLine(field.key, value, spans: spans), at: insertionIndex(for: field.key, spans: spans, task: target))
            }
        }
        return (lines, warnings)
    }

    /// `heavy` becomes `heavy (Opus 5.5)`; `heavy (Other)` is kept.
    static func modelValue(_ text: String) throws -> String {
        let tier = text.split(separator: " ").first.map(String.init) ?? text
        guard let known = tierModels.first(where: { $0.tier == tier }) else {
            throw EditUsageError("a model starts with its tier: \(tierModels.map(\.tier).joined(separator: ", "))")
        }
        if text == tier { return "\(tier) (\(known.model))" }
        let rest = text.dropFirst(tier.count).trimmingCharacters(in: .whitespaces)
        guard rest.hasPrefix("("), rest.hasSuffix(")") else { throw EditUsageError("write the model as `\(tier)` or `\(tier) (Name)`") }
        return text
    }

    /// Other tasks that quote the old title; a reference by wording may now be stale.
    func staleTitleWarnings(old: String, of task: TaskItem) -> [String] {
        guard old.count >= 6 else { return [] }   // very short titles match everything
        return tasks.filter { $0.id != task.id }.compactMap { other in
            guard let line = (other.line...other.endLine).first(where: { markdown.lines[$0 - 1].contains(old) }) else { return nil }
            return "warning:\(line): \(other.id) mentions the old title of \(task.id) (\"\(old)\"); check that it still reads right"
        }
    }

    // MARK: - done

    /// `ticking`, run through the same checks as every other edit.
    public func ticked(_ ids: [String], userConfirmed: Bool = false) throws -> Edit {
        let text = try ticking(ids, userConfirmed: userConfirmed)
        return try finish(text.components(separatedBy: "\n"), summary: "ticked \(ids.joined(separator: " "))")
    }
}
