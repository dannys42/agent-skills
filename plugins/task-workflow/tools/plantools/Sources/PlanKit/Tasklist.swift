import Foundation

public let reasonWords = ["OBSOLETE", "INVALID", "SUPERSEDED", "DEFERRED"]

public enum Mark: Equatable { case open, done, closed }

public struct Heading {
    public let id: String
    public let title: String
    public let line: Int
    public var endLine: Int
    public let reason: String?      // closed-heading reason word, if any
    public var goal: String?
    public let parent: String?      // enclosing phase for a group
}

public struct TaskItem {
    public let id: String
    public let mark: Mark
    public let user: Bool
    public let blocked: String?     // text inside BLOCKED(...)
    public let inProgress: Bool
    public let reason: String?      // reason word for `[-]`
    public let supersededBy: [String]
    public let title: String
    public let line: Int
    public var endLine: Int
    public var fields: [String: String]
    public let phase: String?
    public let group: String?

    public var needs: [String] {
        (fields["needs"] ?? "").split(separator: ",").compactMap {
            let word = $0.trimmingCharacters(in: .whitespaces).split(separator: " ").first.map(String.init) ?? ""
            return isID(word) ? word : nil
        }
    }
}

public struct Tasklist {
    public let markdown: Markdown
    public let title: String?
    public let source: String?
    public private(set) var headings: [Heading] = []
    public private(set) var tasks: [TaskItem] = []

    public var lines: [String] { markdown.lines }

    public init(text: String) {
        markdown = Markdown(text: text)
        var title: String?
        var source: String?
        var phase: String?
        var group: String?
        var current: Int?   // index into tasks
        var lastHeading: Int?

        func closeBlock(_ tasks: inout [TaskItem], _ index: Int?, before line: Int, lines: [String]) {
            guard let index else { return }
            var end = line - 1
            while end > tasks[index].line, lines[end - 1].trimmingCharacters(in: .whitespaces).isEmpty { end -= 1 }
            tasks[index].endLine = end
        }

        for (offset, line) in markdown.lines.enumerated() {
            let number = offset + 1
            if line.hasPrefix("#") {
                let level = line.prefix(while: { $0 == "#" }).count
                let text = line.dropFirst(level).trimmingCharacters(in: .whitespaces)
                if level == 1 { title = title ?? text }
                let first = text.split(separator: " ").first.map(String.init) ?? ""
                if isID(first, prefixes: "PG") {
                    closeBlock(&tasks, current, before: number, lines: markdown.lines)
                    current = nil
                    if let i = lastHeading { headings[i].endLine = number - 1 }
                    let rest = text.dropFirst(first.count).trimmingCharacters(in: .whitespaces)
                    let heading = Heading(id: first, title: rest, line: number, endLine: markdown.lines.count,
                                          reason: Tasklist.headingReason(rest), goal: nil,
                                          parent: first.hasPrefix("G") ? phase : nil)
                    headings.append(heading)
                    lastHeading = headings.count - 1
                    if first.hasPrefix("P") { phase = first; group = nil } else { group = first }
                }
                continue
            }
            if source == nil, line.hasPrefix("Source:") {
                source = line.dropFirst("Source:".count).trimmingCharacters(in: .whitespaces)
            }
            if let i = lastHeading, headings[i].goal == nil, current == nil, line.hasPrefix("Goal:") {
                headings[i].goal = line.dropFirst("Goal:".count).trimmingCharacters(in: .whitespaces)
            }
            if let task = Tasklist.parseTask(line, number: number, phase: phase, group: group) {
                closeBlock(&tasks, current, before: number, lines: markdown.lines)
                tasks.append(task)
                current = tasks.count - 1
                continue
            }
            if let i = current, let (key, value) = Tasklist.parseField(line) {
                tasks[i].fields[key] = value
            }
        }
        closeBlock(&tasks, current, before: markdown.lines.count + 1, lines: markdown.lines)
        self.title = title
        self.source = source
    }

    static func headingReason(_ rest: String) -> String? {
        let candidates = [rest.components(separatedBy: " — ").last ?? rest, rest]
        for text in candidates {
            let word = text.split(separator: " ").first.map(String.init) ?? ""
            if let hit = reasonWords.first(where: { word.hasPrefix($0) }) { return hit }
        }
        return nil
    }

    static func parseField(_ line: String) -> (String, String)? {
        let indent = line.prefix(while: { $0 == " " }).count
        guard (2...3).contains(indent) else { return nil }
        let body = line.dropFirst(indent)
        guard body.hasPrefix("- "), let colon = body.firstIndex(of: ":") else { return nil }
        let key = body[body.index(body.startIndex, offsetBy: 2)..<colon].trimmingCharacters(in: .whitespaces).lowercased()
        guard !key.isEmpty, key.count <= 12, !key.contains(" ") else { return nil }
        return (key, body[body.index(after: colon)...].trimmingCharacters(in: .whitespaces))
    }

    static func parseTask(_ line: String, number: Int, phase: String?, group: String?) -> TaskItem? {
        guard line.hasPrefix("- ["), line.count > 6 else { return nil }
        let chars = Array(line)
        guard chars[4] == "]", chars[5] == " " else { return nil }
        let mark: Mark
        switch chars[3] {
        case " ": mark = .open
        case "x", "X": mark = .done
        case "-": mark = .closed
        default: return nil
        }
        var rest = String(chars[6...])
        guard let id = rest.split(separator: " ").first.map(String.init), isID(id, prefixes: "T") else { return nil }
        rest = String(rest.dropFirst(id.count)).trimmingCharacters(in: .whitespaces)

        var user = false, inProgress = false
        var blocked: String?, reason: String?
        var supersededBy: [String] = []
        while true {
            if rest.hasPrefix("USER") && (rest.count == 4 || rest.dropFirst(4).first == " ") {
                user = true; rest = String(rest.dropFirst(4))
            } else if rest.hasPrefix("IN-PROGRESS") {
                inProgress = true; rest = String(rest.dropFirst("IN-PROGRESS".count))
            } else if rest.hasPrefix("BLOCKED("), let close = rest.firstIndex(of: ")") {
                blocked = String(rest[rest.index(rest.startIndex, offsetBy: 8)..<close])
                rest = String(rest[rest.index(after: close)...])
            } else if let word = reasonWords.first(where: { rest.hasPrefix($0) }) {
                reason = word
                rest = String(rest.dropFirst(word.count))
                if word == "SUPERSEDED", rest.hasPrefix("→") {
                    rest = String(rest.dropFirst())
                    let ids = rest.prefix(while: { $0 != " " })
                    supersededBy = ids.split(separator: ",").map(String.init)
                    rest = String(rest.dropFirst(ids.count))
                }
            } else {
                break
            }
            rest = rest.trimmingCharacters(in: .whitespaces)
        }
        if rest.hasPrefix("— ") { rest = String(rest.dropFirst(2)) }
        return TaskItem(id: id, mark: mark, user: user, blocked: blocked, inProgress: inProgress,
                        reason: reason, supersededBy: supersededBy, title: rest, line: number,
                        endLine: number, fields: [:], phase: phase, group: group)
    }

    // MARK: - Queries

    public func task(_ id: String) -> TaskItem? { tasks.first { $0.id == id } }
    public func heading(_ id: String) -> Heading? { headings.first { $0.id == id } }

    /// Highest used number per prefix, counting closed items. `next-id T` prints one more.
    public func nextID(prefix: Character) -> String {
        var highest = 0
        let ids = headings.map(\.id) + tasks.map(\.id)
        for id in ids where id.first == prefix { highest = max(highest, Int(id.dropFirst()) ?? 0) }
        return "\(prefix)\(highest + 1)"
    }

    /// The closed reason of a heading above the task, if any.
    public func closedHeading(for task: TaskItem) -> Heading? {
        [task.group, task.phase].compactMap { $0 }.compactMap(heading).first { $0.reason != nil }
    }

    public func isSatisfied(_ id: String) -> Bool {
        guard let target = task(id) else { return false }
        if target.mark == .done { return true }
        if target.mark == .closed, target.reason == "SUPERSEDED" {
            return !target.supersededBy.isEmpty && target.supersededBy.allSatisfy { task($0)?.mark == .done }
        }
        return false
    }

    public enum Eligibility: Equatable {
        case eligible
        case notOpen
        case user
        case blocked(String)
        case inProgress
        case closedHeading(String)
        case waiting([String])
    }

    public func eligibility(of task: TaskItem) -> Eligibility {
        if task.mark != .open { return .notOpen }
        if task.user { return .user }
        if let blocked = task.blocked { return .blocked(blocked) }
        if task.inProgress { return .inProgress }
        if let heading = closedHeading(for: task) { return .closedHeading(heading.id) }
        let waiting = task.needs.filter { !isSatisfied($0) }
        return waiting.isEmpty ? .eligible : .waiting(waiting)
    }

    /// First eligible task in document order, per the `tasklist` skill's rule.
    public func next() -> TaskItem? { tasks.first { eligibility(of: $0) == .eligible } }

    /// Why nothing is eligible: one line per open task.
    public func blockers() -> [String] {
        tasks.compactMap { task in
            switch eligibility(of: task) {
            case .user: return "\(task.id) waits on the user: \(task.title)"
            case .blocked(let why): return "\(task.id) BLOCKED(\(why))"
            case .inProgress: return "\(task.id) IN-PROGRESS"
            case .closedHeading(let h): return "\(task.id) is under closed heading \(h)"
            case .waiting(let ids): return "\(task.id) needs \(ids.joined(separator: ", "))"
            case .eligible, .notOpen: return nil
            }
        }
    }

    /// Heading context plus the task block, the text an implementer prompt starts from.
    public func context(for task: TaskItem) -> String {
        var parts: [String] = []
        if let source { parts.append("Source: \(source)") }
        for id in [task.phase, task.group].compactMap({ $0 }) {
            if let h = heading(id) { parts.append("\(h.id) \(h.title)" + (h.goal.map { "\nGoal: \($0)" } ?? "")) }
        }
        parts.append(block(of: task))
        return parts.joined(separator: "\n\n")
    }

    public func block(of task: TaskItem) -> String { markdown.text(from: task.line, to: task.endLine) }

    // MARK: - Lint

    /// Rules from the `tasklist` skill's "Before finishing". `base` is an earlier version of the
    /// same file; with it, deleted IDs and in-place title rewrites are reported too.
    public func lint(base: Tasklist? = nil) -> [Finding] {
        var out: [Finding] = []
        var seen: [String: Int] = [:]
        for (id, line) in headings.map({ ($0.id, $0.line) }) + tasks.map({ ($0.id, $0.line) }) {
            if let first = seen[id] { out.append(.init(.error, line: line, "duplicate ID \(id) (first at line \(first))")) }
            else { seen[id] = line }
        }
        for task in tasks {
            for need in task.needs where self.task(need) == nil {
                out.append(.init(.error, line: task.line, "\(task.id) needs \(need), which does not exist"))
            }
            for id in task.supersededBy where self.task(id) == nil {
                out.append(.init(.error, line: task.line, "\(task.id) is superseded by \(id), which does not exist"))
            }
            if task.mark == .open, !task.user, task.fields["model"] == nil {
                out.append(.init(.error, line: task.line, "\(task.id) has no Model"))
            }
            if task.mark == .closed {
                if task.reason == nil { out.append(.init(.error, line: task.line, "\(task.id) is [-] without a reason word")) }
                if task.fields["why"] == nil { out.append(.init(.error, line: task.line, "\(task.id) is [-] without Why:")) }
            }
            if task.blocked != nil, task.mark == .open, !task.blocked!.isEmpty, !isID(task.blocked!), task.fields["why"] == nil {
                out.append(.init(.error, line: task.line, "\(task.id) BLOCKED(reason) without Why:"))
            }
            if let why = task.fields["why"], !hasISODate(why) {
                out.append(.init(.warning, line: task.line, "\(task.id) Why: has no ISO date"))
            }
            if task.user, task.mark == .open, !blockHasSteps(task) {
                out.append(.init(.warning, line: task.line, "\(task.id) is USER but has no lettered steps"))
            }
            for need in task.needs {
                if let target = self.task(need), target.mark == .closed, target.reason == "OBSOLETE" || target.reason == "INVALID" {
                    out.append(.init(.warning, line: task.line, "\(task.id) needs \(need), which is \(target.reason!): re-point or close it"))
                }
            }
        }
        if let cycle = findCycle() {
            out.append(.init(.error, line: task(cycle[0])?.line, "dependency cycle: \(cycle.joined(separator: " → "))"))
        }
        if let base {
            let ids = Set(headings.map(\.id) + tasks.map(\.id))
            for old in base.headings.map(\.id) + base.tasks.map(\.id) where !ids.contains(old) {
                out.append(.init(.error, line: nil, "\(old) existed in the base file and is gone: close it, never delete it"))
            }
            for old in base.tasks {
                if let now = task(old.id), now.title != old.title {
                    out.append(.init(.warning, line: now.line, "\(old.id) title changed in place; close it and add a new task instead"))
                }
                if let now = task(old.id), old.mark != .open, now.mark == .open, old.reason != "DEFERRED" {
                    out.append(.init(.warning, line: now.line, "\(old.id) was closed in the base file and is open again"))
                }
            }
        }
        return out
    }

    func hasISODate(_ s: String) -> Bool {
        let chars = Array(s)
        guard chars.count >= 10 else { return false }
        for i in 0...(chars.count - 10) {
            let w = chars[i..<(i + 10)]
            let p = Array(w)
            if p[4] == "-", p[7] == "-", [0, 1, 2, 3, 5, 6, 8, 9].allSatisfy({ p[$0].isNumber }) { return true }
        }
        return false
    }

    func blockHasSteps(_ task: TaskItem) -> Bool {
        markdown.lines[(task.line - 1)..<task.endLine].contains {
            $0.trimmingCharacters(in: .whitespaces).hasPrefix("a. ")
        }
    }

    func findCycle() -> [String]? {
        var state: [String: Int] = [:]   // 1 visiting, 2 done
        var stack: [String] = []
        func visit(_ id: String) -> [String]? {
            state[id] = 1; stack.append(id)
            for need in task(id)?.needs ?? [] where task(need) != nil {
                if state[need] == 1, let start = stack.firstIndex(of: need) { return Array(stack[start...]) + [need] }
                if state[need] == nil, let found = visit(need) { return found }
            }
            stack.removeLast(); state[id] = 2
            return nil
        }
        for task in tasks where state[task.id] == nil {
            if let cycle = visit(task.id) { return cycle }
        }
        return nil
    }

    // MARK: - Counts

    public struct Counts: Equatable {
        public var open = 0, done = 0, closed = 0, blocked = 0, user = 0, eligible = 0
    }

    public func counts() -> Counts {
        var c = Counts()
        for task in tasks {
            switch task.mark {
            case .done: c.done += 1
            case .closed: c.closed += 1
            case .open:
                c.open += 1
                switch eligibility(of: task) {
                case .user: c.user += 1
                case .blocked: c.blocked += 1
                case .eligible: c.eligible += 1
                default: break
                }
            }
        }
        return c
    }

    // MARK: - Editing (the only write the tool makes)

    public enum EditError: Error, CustomStringConvertible {
        case unknown(String), alreadyClosed(String), userTask(String)
        public var description: String {
            switch self {
            case .unknown(let id): return "no task \(id)"
            case .alreadyClosed(let id): return "\(id) is already closed"
            case .userTask(let id): return "\(id) is USER: pass --confirmed once the user has confirmed it"
            }
        }
    }

    /// New file text with the given tasks ticked `[x]`. Only the checkbox characters change.
    public func ticking(_ ids: [String], userConfirmed: Bool = false) throws -> String {
        var lines = markdown.lines
        for id in ids {
            guard let task = task(id) else { throw EditError.unknown(id) }
            guard task.mark == .open else { throw EditError.alreadyClosed(id) }
            if task.user, !userConfirmed { throw EditError.userTask(id) }
            lines[task.line - 1] = "- [x]" + lines[task.line - 1].dropFirst(5)
        }
        return lines.joined(separator: "\n")
    }
}
