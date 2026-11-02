import Foundation

/// One line of the roadmap's `## Milestones` section, with its sub-bullets, as `risk-first-roadmap`'s
/// roadmap-example.md defines it: ``- M<id> (<name>) — <outcome> `<mark>`; touches: <subsystems> [<status>]``.
public struct Milestone: Equatable {
    public let id: String
    public let name: String
    public let outcome: String
    public let mark: String          // owner or proposed; empty when the line has none
    public let touches: [String]     // empty on later milestones, which omit `; touches:`
    public let status: String        // planned, current, done, deferred, dropped, or the raw word
    public let line: Int
    public internal(set) var exit: String?
    public internal(set) var additiveCheck: String?
    /// The `Close: <step> (<date>)` sub-bullet, present only while a milestone close is in progress.
    public internal(set) var close: String?

    /// `- M1 (print a puzzle) — outcome `owner`; touches: A, B [current]`; nil for anything else.
    static func parse(_ raw: String, line number: Int) -> Milestone? {
        guard raw.hasPrefix("- M") else { return nil }
        var text = Substring(raw.dropFirst(2)).trimmingCharacters(in: .whitespaces)[...]
        let id = String(text.prefix(while: { $0 != " " && $0 != "(" }))
        guard id.count > 1, id.dropFirst().allSatisfy(\.isNumber) else { return nil }
        text = text.dropFirst(id.count).drop { $0 == " " }
        guard text.first == "(", let close = text.firstIndex(of: ")") else { return nil }
        let name = String(text[text.index(after: text.startIndex)..<close])
        text = text[text.index(after: close)...]
        var status = "unknown"
        if text.hasSuffix("]"), let open = text.lastIndex(of: "[") {
            status = text[text.index(after: open)..<text.index(before: text.endIndex)].lowercased().trimmingCharacters(in: .whitespaces)
            text = text[..<open]
        }
        var touches: [String] = []
        if let t = text.range(of: "; touches:", options: [.backwards, .caseInsensitive]) {
            touches = text[t.upperBound...].split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }.filter { !$0.isEmpty }
            text = text[..<t.lowerBound]
        }
        var body = text.trimmingCharacters(in: .whitespaces)
        var mark = ""
        if body.hasSuffix("`"), let open = body.dropLast().lastIndex(of: "`") {
            mark = String(body[body.index(after: open)..<body.index(before: body.endIndex)])
            body = String(body[..<open]).trimmingCharacters(in: .whitespaces)
        }
        let outcome = body.drop { $0 == "—" || $0 == "-" || $0 == " " }
        return Milestone(id: id, name: name, outcome: String(outcome), mark: mark, touches: touches, status: status, line: number)
    }

    /// `M1 (print a puzzle)`: how an ID is shown to the owner.
    public var named: String { name.isEmpty ? id : "\(id) (\(name))" }
}

extension Roadmap {
    static let milestoneStatuses = ["planned", "current", "done", "deferred", "dropped"]

    /// Milestone lines and their `Exit:`, `Additive check:` and `Close:` sub-bullets.
    static func parseMilestones(_ markdown: Markdown) -> [Milestone] {
        guard let s = markdown.sections.first(where: { $0.level == 2 && $0.title.hasPrefix("Milestones") }) else { return [] }
        var out: [Milestone] = []
        for number in (s.line + 1)...max(s.line + 1, s.endLine) where number <= markdown.lines.count {
            let line = markdown.lines[number - 1]
            if let m = Milestone.parse(line, line: number) { out.append(m); continue }
            let sub = line.trimmingCharacters(in: .whitespaces)
            guard line.hasPrefix(" ") || line.hasPrefix("\t"), sub.hasPrefix("- "), !out.isEmpty else { continue }
            let item = sub.dropFirst(2)
            func value(_ key: String) -> String? {
                item.hasPrefix(key + ":") ? item.dropFirst(key.count + 1).trimmingCharacters(in: .whitespaces) : nil
            }
            if let v = value("Exit") { out[out.count - 1].exit = v }
            else if let v = value("Additive check") { out[out.count - 1].additiveCheck = v }
            else if let v = value("Close") { out[out.count - 1].close = v }
        }
        return out
    }

    /// The milestone being built: the first `current` one.
    public var currentMilestone: Milestone? { milestones.first { $0.status.hasPrefix("current") } }

    /// The value of a `<key>: ...` field line in a rung's detail section, e.g. `Touches` or `Milestone`.
    public func field(_ key: String, of id: String) -> String? {
        guard let d = details.first(where: { $0.id == id }), let sec = markdown.sections.first(where: { $0.line == d.line }) else { return nil }
        for number in sec.line...sec.endLine where markdown.lines[number - 1].hasPrefix(key + ":") {
            return markdown.lines[number - 1].dropFirst(key.count + 1).trimmingCharacters(in: .whitespaces)
        }
        return nil
    }

    /// A rung's milestone: its section's `Milestone:` field, else an `(M<id>)` tag on its horizon line.
    public func milestone(of rung: LadderRung) -> String? {
        if let m = field("Milestone", of: rung.id) {
            let id = String(m.prefix(while: { $0 != " " && $0 != "(" && $0 != "," }))
            if !id.isEmpty { return id }
        }
        guard rung.status == "horizon" else { return nil }
        var rest = Substring(rung.text)
        while let open = rest.firstIndex(of: "(") {
            let inner = rest[rest.index(after: open)...].prefix(while: { $0 != ")" })
            if inner.first == "M", inner.count > 1, inner.dropFirst().allSatisfy(\.isNumber) { return String(inner) }
            rest = rest[rest.index(after: open)...]
        }
        return nil
    }

    /// `Touches:` subsystems of a rung, comma-separated.
    public func touches(of id: String) -> [String] {
        (field("Touches", of: id) ?? "").split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }.filter { !$0.isEmpty }
    }

    /// The date of the escalation marker the automatic fold-back writes in a rung's section (`Escalation: <date>`).
    public func escalation(of id: String) -> String? { field("Escalation", of: id) }

    /// A rung's short name: its section heading after the ID (`### L4: Folder suggestions`), else the ladder question.
    public func name(of rung: LadderRung) -> String {
        if let d = details.first(where: { $0.id == rung.id }), let sec = markdown.sections.first(where: { $0.line == d.line }) {
            let title = sec.title.dropFirst(rung.id.count).drop { $0 == ":" || $0 == " " }
            if !title.isEmpty { return String(title) }
        }
        var question = rung.text.dropFirst(rung.id.count).drop { $0 == " " || $0 == "—" || $0 == "-" }
        if let pointer = question.range(of: " detail:", options: .backwards) { question = question[..<pointer.lowerBound] }
        if question.hasSuffix("]"), let open = question.lastIndex(of: "[") { question = question[..<open] }
        if rung.status == "horizon", let tag = question.range(of: " (M", options: .backwards) { question = question[..<tag.lowerBound] }
        let trimmed = question.trimmingCharacters(in: .whitespaces)
        return trimmed.count > 60 ? String(trimmed.prefix(59)) + "…" : trimmed
    }

    /// `L4 (Folder suggestions)` for a rung, `M1 (print a puzzle)` for a milestone; nil for an unknown ID.
    public func named(_ id: String) -> String? {
        if let m = milestones.first(where: { $0.id.lowercased() == id.lowercased() }) { return m.named }
        guard let rung = ladder.first(where: { $0.id.lowercased() == id.lowercased() }) else { return nil }
        let name = name(of: rung)
        return name.isEmpty ? rung.id : "\(rung.id) (\(name))"
    }

    /// `Map.md`: each milestone with status and outcome, then its rungs one line each with name, status and `Touches`.
    /// A roadmap without milestones gets one list of rungs.
    public func map(source: String) -> String {
        let title = markdown.sections.first { $0.level == 1 }?.title ?? "Roadmap"
        var out = ["# Map: " + (title.hasPrefix("Roadmap: ") ? String(title.dropFirst(9)) : title), "",
                   "Generated by `roadmap map` from \(source); do not edit by hand.", ""]
        func row(_ rung: LadderRung) -> String {
            var status = rung.status
            if let date = escalation(of: rung.id) { status += ", escalated \(date)" }
            let touches = touches(of: rung.id)
            return "- \(named(rung.id) ?? rung.id) [\(status)]" + (touches.isEmpty ? "" : " — Touches: " + touches.joined(separator: ", "))
        }
        let known = Set(milestones.map(\.id))
        for m in milestones {
            out.append("## \(m.named) [\(m.status)]")
            out.append("")
            out.append(m.outcome + (m.mark.isEmpty ? "" : " `\(m.mark)`"))
            if !m.touches.isEmpty { out.append("Touches: " + m.touches.joined(separator: ", ")) }
            if let exit = m.exit { out.append("Exit: " + exit) }
            if let close = m.close { out.append("Close: " + close) }
            let rungs = ladder.filter { milestone(of: $0) == m.id }
            out.append("")
            out += rungs.isEmpty ? ["No rungs yet."] : rungs.map(row)
            out.append("")
        }
        let rest = ladder.filter { milestone(of: $0).map { !known.contains($0) } ?? true }
        if !rest.isEmpty {
            if !milestones.isEmpty { out += ["## Rungs without a milestone", ""] }
            out += rest.map(row)
            out.append("")
        }
        return out.joined(separator: "\n")
    }

    func lintMilestones() -> [Finding] {
        var out: [Finding] = []
        if let s = markdown.sections.first(where: { $0.level == 2 && $0.title.hasPrefix("Milestones") }) {
            for number in (s.line + 1)...max(s.line + 1, s.endLine) where number <= markdown.lines.count {
                let line = markdown.lines[number - 1]
                if line.hasPrefix("- M"), line.dropFirst(3).first?.isNumber == true, !milestones.contains(where: { $0.line == number }) {
                    out.append(.init(.warning, line: number, "milestone line is not in the format - M<id> (<name>) — <outcome> `<mark>`; touches: <subsystems> [<status>]"))
                }
            }
        }
        var seen: [String: Int] = [:]
        for m in milestones {
            if let first = seen[m.id] { out.append(.init(.error, line: m.line, "duplicate milestone ID \(m.id) (first at line \(first))")) }
            else { seen[m.id] = m.line }
            if !Roadmap.milestoneStatuses.contains(where: { m.status.hasPrefix($0) }) {
                out.append(.init(.warning, line: m.line, "\(m.id) has no recognised status in brackets; end the line with [planned], [current], [done], [deferred] or [dropped]"))
            }
        }
        if milestones.filter({ $0.status.hasPrefix("current") }).count > 1 {
            out.append(.init(.warning, line: nil, "more than one milestone is [current]; roadmap next uses the first"))
        }
        if !milestones.isEmpty {
            for rung in ladder {
                guard let m = milestone(of: rung) else { continue }
                if seen[m] == nil {
                    out.append(.init(.warning, line: rung.line, "\(rung.id) names milestone \(m), which is not in ## Milestones"))
                }
                if m != currentMilestone?.id, rung.status.hasPrefix("in progress") || escalation(of: rung.id) != nil {
                    let what = rung.status.hasPrefix("in progress") ? "is in progress" : "carries an Escalation marker"
                    out.append(.init(.warning, line: rung.line, "\(rung.id) \(what) but belongs to \(m), which is not the current milestone; roadmap next never routes it"))
                }
            }
        }
        return out
    }
}
