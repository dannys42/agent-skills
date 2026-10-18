import Foundation

public struct LadderRung {
    public let id: String
    public let status: String      // done, in progress, planned, horizon, or the raw word
    public let text: String        // the ladder line after the number
    public let line: Int
}

public struct LogEntry {
    public let line: Int
    public let date: String
    public let rung: String
}

/// The `risk-first-roadmap` file: a numbered ladder, `### <Rung>` detail sections, a learning log.
public struct Roadmap {
    public let markdown: Markdown
    public private(set) var ladder: [LadderRung] = []
    public private(set) var details: [(id: String, line: Int)] = []
    public private(set) var log: [LogEntry] = []

    public init(text: String) {
        markdown = Markdown(text: text)
        if let s = markdown.sections.first(where: { $0.level == 2 && $0.title.hasPrefix("Ladder") }) {
            for number in (s.line + 1)...max(s.line + 1, s.endLine) where number <= markdown.lines.count {
                if let rung = Roadmap.parseLadder(markdown.lines[number - 1], line: number) { ladder.append(rung) }
            }
        }
        if let s = markdown.sections.first(where: { $0.level == 2 && $0.title.hasPrefix("Horizon") }) {
            for number in (s.line + 1)...max(s.line + 1, s.endLine) where number <= markdown.lines.count {
                let line = markdown.lines[number - 1]
                guard line.hasPrefix("- ") else { continue }
                let text = String(line.dropFirst(2))
                let id = String(text.prefix(while: { $0 != " " }))
                if id.first == "L", id.dropFirst().first?.isNumber == true, !ladder.contains(where: { $0.id == id }) {
                    ladder.append(LadderRung(id: id, status: "horizon", text: text, line: number))
                }
            }
        }
        if let rungs = markdown.sections.first(where: { $0.level == 2 && $0.title.hasPrefix("Rungs") }) {
            for s in markdown.sections where s.level == 3 && s.line > rungs.line && s.line <= rungs.endLine {
                let id = String(s.title.prefix(while: { $0 != ":" && $0 != " " }))
                details.append((id, s.line))
            }
        }
        // Ladder lines without a bracketed status take the `Status:` line of their detail section.
        for (i, rung) in ladder.enumerated() where rung.status == "unknown" {
            if let d = details.first(where: { $0.id == rung.id }), let sec = markdown.sections.first(where: { $0.line == d.line }) {
                for number in sec.line...sec.endLine {
                    let line = markdown.lines[number - 1]
                    if line.hasPrefix("Status:") {
                        let word = line.dropFirst(7).trimmingCharacters(in: .whitespaces).lowercased()
                            .prefix(while: { $0 != ":" && $0 != ";" && $0 != "," && $0 != "(" }).trimmingCharacters(in: .whitespaces)
                        ladder[i] = LadderRung(id: rung.id, status: word, text: rung.text, line: rung.line)
                        break
                    }
                }
            }
        }
        if let s = markdown.sections.first(where: { $0.level == 2 && $0.title.hasPrefix("Learning log") }) {
            for number in (s.line + 1)...max(s.line + 1, s.endLine) where number <= markdown.lines.count {
                let line = markdown.lines[number - 1]
                guard line.hasPrefix("- ") else { continue }
                let body = String(line.dropFirst(2))
                func rungToken(_ t: Substring) -> String? {
                    let id = String(t.prefix(while: { $0 != " " && $0 != "(" && $0 != "," && $0 != ":" }))
                    return id.first == "L" && id.dropFirst().first?.isNumber == true ? id : nil
                }
                if let id = rungToken(body[...]) {
                    log.append(LogEntry(line: number, date: Roadmap.firstDate(in: body) ?? "", rung: id))
                } else if body.count > 11, body.prefix(10).dropFirst(4).first == "-", let id = rungToken(body.dropFirst(11)) {
                    log.append(LogEntry(line: number, date: String(body.prefix(10)), rung: id))
                }
            }
        }
    }

    static func firstDate(in text: String) -> String? {
        let chars = Array(text)
        guard chars.count >= 10 else { return nil }
        for i in 0...(chars.count - 10) {
            let p = Array(chars[i..<(i + 10)])
            if p[4] == "-", p[7] == "-", [0, 1, 2, 3, 5, 6, 8, 9].allSatisfy({ p[$0].isNumber }) { return String(p) }
        }
        return nil
    }

    static let knownStatuses = ["planned", "in progress", "done", "failed", "changed", "obsolete", "deferred", "horizon"]

    static func parseLadder(_ line: String, line number: Int) -> LadderRung? {
        guard let dot = line.firstIndex(of: "."), line[..<dot].allSatisfy(\.isNumber), !line[..<dot].isEmpty else { return nil }
        let text = line[line.index(after: dot)...].trimmingCharacters(in: .whitespaces)
        let id = String(text.prefix(while: { $0 != " " }))
        guard id.first == "L", id.count > 1 else { return nil }
        var status = "unknown"
        // A finished rung's pointer may follow the status: `... [done] detail: Completed/...`.
        var head = Substring(text)
        if let pointer = text.range(of: " detail:", options: .backwards), text[..<pointer.lowerBound].hasSuffix("]") {
            head = text[..<pointer.lowerBound]
        }
        if head.hasSuffix("]"), let open = head.lastIndex(of: "[") {
            let inside = head[head.index(after: open)..<head.index(before: head.endIndex)].lowercased()
            let word = inside.prefix(while: { $0 != ":" && $0 != ";" && $0 != "," }).trimmingCharacters(in: .whitespaces)
            status = word.hasPrefix("done") ? "done" : word
        }
        return LadderRung(id: id, status: status, text: text, line: number)
    }

    /// Per `roadmap-plan-next-rung`: first `in progress` rung, else the first `planned`.
    public func nextRung() -> LadderRung? {
        ladder.first { $0.status.hasPrefix("in progress") } ?? ladder.first { $0.status.hasPrefix("planned") }
    }

    /// Ladder line, detail section and learning-log entries for one rung, nothing else.
    public func show(_ id: String, includeLog: Bool = true) -> String? {
        guard let rung = ladder.first(where: { $0.id.lowercased() == id.lowercased() }) else { return nil }
        var parts = ["\(rung.text)"]
        if let detail = markdown.section(matching: rung.id), detail.level == 3 {
            parts.append(markdown.text(from: detail.line, to: detail.endLine))
        }
        if includeLog {
            for entry in log where entry.rung == rung.id {
                parts.append(markdown.lines[entry.line - 1])
            }
        }
        return parts.joined(separator: "\n\n")
    }

    /// Next rung, finished rungs collapsed to one line, every other rung on its own line.
    public func status() -> String {
        var rows: [String] = []
        if let next = nextRung() { rows.append("next: \(next.id) (\(next.status))") }
        let done = ladder.filter { $0.status == "done" }
        rows.append("done (\(done.count)): " + done.map(\.id).joined(separator: " "))
        for rung in ladder where rung.status != "done" {
            let question = rung.text.dropFirst(rung.id.count).trimmingCharacters(in: CharacterSet(charactersIn: " —-"))
            rows.append("\(rung.id) [\(rung.status)] \(question.prefix(90))")
        }
        return rows.joined(separator: "\n")
    }

    public struct Budget {
        public var maxBytes = 40_000
        public var maxLine = 1_500
        public init(maxBytes: Int = 40_000, maxLine: Int = 1_500) { self.maxBytes = maxBytes; self.maxLine = maxLine }
    }

    public func lint(budget: Budget = Budget()) -> [Finding] {
        var out: [Finding] = []
        var seen: [String: Int] = [:]
        for rung in ladder {
            if let first = seen[rung.id] { out.append(.init(.error, line: rung.line, "duplicate ladder ID \(rung.id) (first at line \(first))")) }
            else { seen[rung.id] = rung.line }
            if !Roadmap.knownStatuses.contains(where: { rung.status.hasPrefix($0) }) {
                out.append(.init(.warning, line: rung.line, "\(rung.id) has no recognised status in brackets; end the line with [planned], [in progress], [done] and so on, optionally followed by detail: <path>"))
            }
        }
        var detailSeen: [String: Int] = [:]
        for (id, line) in details {
            if let first = detailSeen[id] { out.append(.init(.error, line: line, "duplicate rung section \(id) (first at line \(first))")) }
            else { detailSeen[id] = line }
            if seen[id] == nil { out.append(.init(.error, line: line, "rung section \(id) has no ladder entry")) }
        }
        for rung in ladder where detailSeen[rung.id] == nil {
            if rung.status.hasPrefix("in progress") {
                out.append(.init(.error, line: rung.line, "\(rung.id) is in progress but has no detail section"))
            } else if rung.status.hasPrefix("planned") {
                out.append(.init(.warning, line: rung.line, "\(rung.id) is planned but has no detail section"))
            }
        }
        for entry in log where seen[entry.rung] == nil {
            out.append(.init(.warning, line: entry.line, "learning-log entry names \(entry.rung), which is not on the ladder"))
        }
        let size = markdown.lines.reduce(0) { $0 + $1.utf8.count + 1 }
        if size > budget.maxBytes { out.append(.init(.warning, line: nil, "file is \(size) bytes, over the \(budget.maxBytes) budget")) }
        for (line, length) in markdown.longLines(over: budget.maxLine) {
            out.append(.init(.warning, line: line, "line is \(length) characters, over the \(budget.maxLine) budget"))
        }
        return out
    }
}
