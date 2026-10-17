import Foundation

/// One heading in a markdown file, with the line range of its section.
public struct Section {
    public let level: Int
    public let title: String
    public let line: Int          // 1-based
    public internal(set) var endLine: Int   // 1-based, inclusive, covers child sections
    public internal(set) var ownEndLine: Int // up to the next heading of any level
}

/// Heading structure of a markdown file. Headings inside code fences are ignored.
public struct Markdown {
    public let lines: [String]
    public let sections: [Section]

    public init(text: String) {
        lines = text.components(separatedBy: "\n")
        var found: [Section] = []
        var inFence = false
        for (index, line) in lines.enumerated() {
            if line.hasPrefix("```") || line.hasPrefix("~~~") { inFence.toggle(); continue }
            if inFence { continue }
            let level = line.prefix(while: { $0 == "#" }).count
            guard (1...6).contains(level), line.dropFirst(level).first == " " else { continue }
            let title = line.dropFirst(level + 1).trimmingCharacters(in: .whitespaces)
            found.append(Section(level: level, title: title, line: index + 1, endLine: lines.count, ownEndLine: lines.count))
        }
        for i in found.indices {
            if i + 1 < found.count { found[i].ownEndLine = found[i + 1].line - 1 }
            if let next = found[(i + 1)...].first(where: { $0.level <= found[i].level }) {
                found[i].endLine = next.line - 1
            }
        }
        sections = found
    }

    public func bytes(from first: Int, to last: Int) -> Int {
        guard first <= last, first >= 1 else { return 0 }
        return lines[(first - 1)..<min(last, lines.count)].reduce(0) { $0 + $1.utf8.count + 1 }
    }

    public func text(from first: Int, to last: Int) -> String {
        guard first <= last, first >= 1 else { return "" }
        return lines[(first - 1)..<min(last, lines.count)].joined(separator: "\n")
    }

    /// First section whose title is `query` or starts with it followed by a non-alphanumeric
    /// character (so `L9` finds `L9: Per-version ...` but not `L9b: ...`). Case-insensitive.
    public func section(matching query: String) -> Section? {
        let q = query.lowercased()
        return sections.first { section in
            let t = section.title.lowercased()
            guard t.hasPrefix(q) else { return false }
            guard let next = t.dropFirst(q.count).first else { return true }
            return !(next.isLetter || next.isNumber)
        }
    }

    /// Sections whose title is `query` or starts with it, e.g. `Learning log`.
    public func sectionContaining(_ line: Int) -> Section? {
        sections.last { $0.line <= line }
    }

    /// Longest lines, for size budgets.
    public func longLines(over limit: Int) -> [(line: Int, length: Int)] {
        lines.enumerated().compactMap { index, text in
            text.count > limit ? (index + 1, text.count) : nil
        }
    }

    /// `outline`: one row per heading, `line  own-bytes  subtree-bytes  heading`.
    public func outline() -> String {
        sections.map { s in
            let own = bytes(from: s.line, to: s.ownEndLine)
            let total = bytes(from: s.line, to: s.endLine)
            return "\(s.line)\t\(own)\t\(total)\t\(String(repeating: "#", count: s.level)) \(s.title)"
        }.joined(separator: "\n")
    }
}

public struct Finding: Equatable {
    public enum Severity: String { case error, warning }
    public let severity: Severity
    public let line: Int?
    public let message: String

    public init(_ severity: Severity, line: Int?, _ message: String) {
        self.severity = severity
        self.line = line
        self.message = message
    }

    public var rendered: String {
        let place = line.map { ":\($0)" } ?? ""
        return "\(severity.rawValue)\(place): \(message)"
    }
}

public func isID(_ s: String, prefixes: String = "PGT") -> Bool {
    guard let first = s.first, prefixes.contains(first), s.count > 1 else { return false }
    return s.dropFirst().allSatisfy(\.isNumber)
}
