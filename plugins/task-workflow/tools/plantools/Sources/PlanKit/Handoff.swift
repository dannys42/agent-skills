import Foundation

/// A wait-point handoff note, `<DocDir>/Handoff/<Route>-<Target>.md` (plan-milestone's references/handoff.md):
/// a few `Key: value` header lines the tool reads, then free prose for the agent that resumes.
public struct Handoff: Equatable {
    public var route: String?
    public var model: String?
    public var waitingOn: String?
    public var date: String?
    public var rung: String?
    public var milestone: String?
    public var list: String?

    /// Routes a note may name: `roadmap next`'s labels for both roadmap formats.
    public static let routes: Set<String> = ["milestone-plan", "run", "user", "escalation", "milestone-close", "replan", "plan", "close", "design"]
    /// A note older than this is left over: its consumer never ran, or the owner abandoned the wait.
    public static let staleDays = 14

    public init(text: String) {
        // The header is the leading run of `Key: value` lines, after an optional `# Title` and blank lines.
        for line in text.components(separatedBy: "\n") {
            let trimmed = line.trimmingCharacters(in: .whitespaces)
            if trimmed.isEmpty || trimmed.hasPrefix("# ") { if route == nil && date == nil { continue } else { break } }
            guard let colon = trimmed.firstIndex(of: ":") else { break }
            let key = trimmed[..<colon].lowercased()
            let value = trimmed[trimmed.index(after: colon)...].trimmingCharacters(in: CharacterSet(charactersIn: " `"))
            switch key {
            case "route": route = value.lowercased()
            case "model": model = value.lowercased()
            case "waiting on": waitingOn = value
            case "date": date = String(value.prefix(10))
            case "rung": rung = value
            case "milestone": milestone = value
            case "list": list = value
            default: break
            }
        }
    }

    /// The route when it is one `roadmap next` knows; nil makes the note unreadable to the tool.
    public var knownRoute: String? { route.flatMap { Handoff.routes.contains($0) ? $0 : nil } }

    public var day: Date? {
        guard let date else { return nil }
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: "UTC")
        f.dateFormat = "yyyy-MM-dd"
        return f.date(from: date)
    }

    /// Why the note is left over, or nil: no route the tool knows, no `Date:`, or older than `staleDays` on `today`.
    public func leftOver(today: Date) -> String? {
        guard knownRoute != nil else { return "no Route: line naming a known route" }
        guard let day else { return "no Date: line" }
        let days = Int(today.timeIntervalSince(day) / 86_400)
        return days > Handoff.staleDays ? "\(days) days old" : nil
    }
}

/// The documentation directory, found the one way both `roadmap next` and `metrics signals` use.
public enum DocDir {
    static let candidates = ["Documentation", "docs", "Docs", "doc"]

    static func markdown(_ path: String) -> [String] {
        ((try? FileManager.default.contentsOfDirectory(atPath: path)) ?? []).filter { $0.hasSuffix(".md") }.sorted()
    }

    static func join(_ root: String, _ rel: String) -> String { root == "." ? rel : (root as NSString).appendingPathComponent(rel) }

    /// A system design: `SystemDesign/Overview.md`, or a legacy `Design-*.md`.
    public static func hasOverview(_ dir: String, in root: String = ".") -> Bool {
        FileManager.default.fileExists(atPath: join(root, dir + "/SystemDesign/Overview.md")) || markdown(join(root, dir)).contains { $0.hasPrefix("Design-") }
    }

    /// The first candidate holding a roadmap or a system design, else `.`; relative to `root`. Stops at the first hit,
    /// so `docs` and `Docs` on a case-insensitive disk are one directory, read once.
    public static func find(in root: String = ".") -> String {
        candidates.first { d in markdown(join(root, d)).contains { $0.hasPrefix("Roadmap-") } || hasOverview(d, in: root) } ?? "."
    }

    /// Handoff notes in `<dir>/Handoff/`, with paths relative to `root`.
    public static func handoffs(_ dir: String, in root: String = ".") -> [(path: String, text: String)] {
        let rel = dir == "." ? "Handoff" : dir + "/Handoff"
        return markdown(join(root, rel)).compactMap { n in
            (try? String(contentsOfFile: join(root, rel + "/" + n), encoding: .utf8)).map { (rel + "/" + n, $0) }
        }
    }
}
