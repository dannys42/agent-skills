import Foundation

/// `<DocDir>/Quality/Status.md`: the code-quality pass's current state, a few `Key: value` lines.
public struct QualityStatus {
    public var every = 5
    public var lastReviewSha: String?
    public var sinceReview = 0
    public var deferred: String?
    /// File-name families the last review judged to be conventions, not duplication (`Runner`, `Routes`).
    public var acceptedShapes: Set<String> = []
    public let lineCount: Int

    public static let lineBudget = 25

    public init(text: String) {
        let lines = text.components(separatedBy: "\n")
        lineCount = lines.count - (text.hasSuffix("\n") ? 1 : 0)
        for line in lines {
            guard let colon = line.firstIndex(of: ":") else { continue }
            let key = line[..<colon].trimmingCharacters(in: CharacterSet(charactersIn: " -*")).lowercased()
            let value = line[line.index(after: colon)...].trimmingCharacters(in: .whitespaces)
            let none = value.isEmpty || value.lowercased().hasPrefix("none") || value.lowercased() == "no"
            switch key {
            case "every":
                every = Int(value.prefix { $0.isNumber }) ?? every
            case "last review":
                lastReviewSha = none ? nil : value.components(separatedBy: "·").map { $0.trimmingCharacters(in: .whitespaces) }
                    .first { $0.count >= 7 && $0.count <= 40 && $0.allSatisfy(\.isHexDigit) }
            case "since review":
                if none { sinceReview = 0 }
                else if let open = value.lastIndex(of: "("), let n = Int(value[value.index(after: open)...].prefix { $0.isNumber }) { sinceReview = n }
                else { sinceReview = value.split(separator: ",").filter { !$0.trimmingCharacters(in: .whitespaces).isEmpty }.count }
            case "deferred":
                deferred = none ? nil : value
            case "accepted shapes":
                acceptedShapes = none ? [] : Set(value.split(separator: ",").map { $0.trimmingCharacters(in: CharacterSet(charactersIn: " *`")) })
            default:
                continue
            }
        }
    }
}

/// What `metrics signals` reads. `reviewFiles` and `reviewTypeNames` are nil when no review has been recorded.
public struct SignalInput {
    public var swiftFiles: [(path: String, text: String)] = []
    public var reviewFiles: [String]?
    public var reviewTypeNames: Set<String>?
    public var status: QualityStatus?
    public var statusPath: String?
    public var rungLines: Int?
    public var priorRungLines: [Int] = []
    public var newSubsystemDocs: [String] = []
    public var churn: [(path: String, commits: Int)] = []

    public init() {}
}

/// Zero-token quality signals: triggers that call for a review, plus a few counts to watch.
/// Every threshold here is a starting guess; the `quality` events record the raw counts so they can be tuned.
public struct Signals {
    public var triggers: [String] = []
    public var info: [String] = []
    public var counts: [String: Int] = [:]

    static let largeFile = 400
    static let shapeTrigger = 4          // the fourth file of one shape
    static let noBaselineLines = 3_000
    static let ignoredSuffixes: Set<String> = ["View", "Views", "App", "Test", "Tests", "Mock", "Mocks", "Preview", "Previews", "Extension", "Extensions"]
    static let mirrorPairs = [("Row", "Input"), ("Row", "Record"), ("Record", "Input"), ("DTO", "Model"), ("Entity", "Model"), ("Row", "Model")]

    static func count(_ pattern: String, in text: String) -> Int {
        (try? NSRegularExpression(pattern: pattern))?.numberOfMatches(in: text, range: NSRange(text.startIndex..., in: text)) ?? 0
    }

    public static func typeNames(in text: String) -> Set<String> {
        guard let re = try? NSRegularExpression(pattern: #"\b(?:struct|class|enum|actor|protocol)\s+([A-Z][A-Za-z0-9_]*)"#) else { return [] }
        return Set(re.matches(in: text, range: NSRange(text.startIndex..., in: text)).compactMap {
            Range($0.range(at: 1), in: text).map { String(text[$0]) }
        })
    }

    static func isTest(_ path: String) -> Bool {
        let name = (path as NSString).lastPathComponent
        return path.contains("Tests/") || name.hasSuffix("Tests.swift") || name.hasSuffix("Test.swift")
    }

    /// Last CamelCase word of a file's base name: `ListingChangeDeriver.swift` → `Deriver`.
    public static func shape(of path: String) -> String? {
        let base = Array(((path as NSString).lastPathComponent as NSString).deletingPathExtension)
        guard !base.contains("+"), base.count > 1 else { return nil }
        for i in stride(from: base.count - 1, to: 0, by: -1) where base[i].isUppercase && (base[i - 1].isLowercase || base[i - 1].isNumber) {
            let word = String(base[i...])
            return ignoredSuffixes.contains(word) ? nil : word
        }
        return nil
    }

    static func shapeGroups(_ paths: [String]) -> [String: [String]] {
        var groups: [String: Set<String>] = [:]
        for p in paths where !isTest(p) {
            if let s = shape(of: p) { groups[s, default: []].insert(((p as NSString).lastPathComponent as NSString).deletingPathExtension) }
        }
        return groups.mapValues { $0.sorted() }
    }

    static func mirrors(_ names: Set<String>) -> [(String, String)] {
        var out: [(String, String)] = []
        for (a, b) in mirrorPairs {
            for name in names.sorted() where name.hasSuffix(a) && name.count > a.count {
                let twin = String(name.dropLast(a.count)) + b
                if names.contains(twin) { out.append((name, twin)) }
            }
        }
        return out
    }

    public static func evaluate(_ input: SignalInput) -> Signals {
        var s = Signals()
        let sources = input.swiftFiles.filter { !isTest($0.path) }
        let lineCounts = input.swiftFiles.map { ($0.path, $0.text.reduce(0) { $1 == "\n" ? $0 + 1 : $0 }) }
        let totalLines = lineCounts.reduce(0) { $0 + $1.1 }
        let large = lineCounts.filter { $0.1 > largeFile && !isTest($0.0) }.sorted { $0.1 > $1.1 }
        let allText = sources.map(\.text).joined(separator: "\n")
        let names = typeNames(in: allText)
        let accepted = input.status?.acceptedShapes ?? []
        let groups = shapeGroups(input.swiftFiles.map(\.path)).filter { $0.value.count >= 3 && !accepted.contains($0.key) }
        let pairs = mirrors(names)

        s.counts = [
            "swift_files": input.swiftFiles.count, "swift_lines": totalLines, "large_files": large.count,
            "catch_all": count(#"catch\s*(?:let\s+\w+\s*)?\{|catch\s+_\s*\{"#, in: allText),
            "try_optional": count(#"try\?"#, in: allText),
            "tuple_returns": count(#"->\s*\([^()]*,[^()]*\)"#, in: allText),
            "shape_groups": groups.count, "mirrors": pairs.count,
        ]

        // Triggers
        if let status = input.status, status.sinceReview >= status.every {
            s.triggers.append("interval: \(status.sinceReview) rungs since the last review (every \(status.every))")
        }
        if input.status == nil, totalLines >= noBaselineLines {
            s.triggers.append("no-baseline: no Quality/Status.md and \(totalLines) lines of Swift")
        }
        if let lines = input.rungLines {
            let threshold = input.priorRungLines.count >= 3 ? max(400, 2 * (RunSummary.median(input.priorRungLines) ?? 0)) : 1_500
            if lines > threshold { s.triggers.append("rung-size: \(lines) lines changed (threshold \(threshold))") }
        }
        if let before = input.reviewFiles {
            let old = shapeGroups(before)
            for (shape, members) in groups.sorted(by: { $0.key < $1.key }) where members.count >= shapeTrigger && (old[shape]?.count ?? 0) < members.count {
                s.triggers.append("shape: *\(shape) now has \(members.count) files (\(members.joined(separator: ", ")))")
            }
        }
        if let before = input.reviewTypeNames {
            for (a, b) in pairs where !before.contains(a) || !before.contains(b) {
                s.triggers.append("mirror: new mirrored types \(a) / \(b)")
            }
        }
        for doc in input.newSubsystemDocs { s.triggers.append("subsystem: new design doc \(doc)") }

        // Info
        if !input.swiftFiles.isEmpty {
            var line = "\(input.swiftFiles.count) Swift files, \(totalLines) lines"
            if !large.isEmpty {
                line += "; \(large.count) over \(largeFile) lines: " + large.prefix(5).map { "\(($0.0 as NSString).lastPathComponent) \($0.1)" }.joined(separator: ", ")
            }
            s.info.append(line)
        }
        if !groups.isEmpty {
            s.info.append("Shape groups: " + groups.sorted { $0.value.count > $1.value.count }.prefix(5)
                .map { "*\($0.key) ×\($0.value.count) (\($0.value.prefix(4).joined(separator: ", ")))" }.joined(separator: "; "))
        }
        if !pairs.isEmpty { s.info.append("Mirrored types: " + pairs.prefix(5).map { "\($0.0) / \($0.1)" }.joined(separator: "; ")) }
        let risky = [("catch-alls", "catch_all"), ("try?", "try_optional"), ("tuple returns", "tuple_returns")]
            .filter { (s.counts[$0.1] ?? 0) > 0 }.map { "\($0.0) \(s.counts[$0.1]!)" }
        if !risky.isEmpty { s.info.append(risky.joined(separator: ", ")) }
        let hot = input.churn.filter { $0.commits >= 5 }.prefix(5)
        if !hot.isEmpty { s.info.append("Most changed: " + hot.map { "\(($0.path as NSString).lastPathComponent) \($0.commits) commits" }.joined(separator: ", ")) }
        if let status = input.status, status.lineCount > QualityStatus.lineBudget {
            s.info.append("Warning: \(input.statusPath ?? "Status.md") is \(status.lineCount) lines (budget \(QualityStatus.lineBudget)); it holds current state only")
        }
        if let deferred = input.status?.deferred { s.info.append("Deferred: \(deferred)") }
        return s
    }

    public func render(header: String) -> String {
        var out = ["Quality signals · \(header)"]
        out.append(triggers.isEmpty ? "Triggers: none" : "Triggers:")
        out += triggers.map { "- \($0)" }
        out += info.map { "- \($0)" }
        return out.joined(separator: "\n")
    }

    /// Compact object for the `signals` field of a `quality` event.
    public var json: LogEvent {
        var out: LogEvent = counts
        out["triggers"] = triggers.map { String($0.prefix { $0 != ":" }) }
        return out
    }
}

/// Runs git in a repository; nil on any failure.
public enum Git {
    public static func run(_ args: [String], in dir: String) -> String? {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["git"] + args
        process.currentDirectoryURL = URL(fileURLWithPath: dir)
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = FileHandle.nullDevice
        do { try process.run() } catch { return nil }
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        process.waitUntilExit()
        return process.terminationStatus == 0 ? String(decoding: data, as: UTF8.self) : nil
    }

    static func lines(_ args: [String], in dir: String) -> [String] {
        (run(args, in: dir) ?? "").split(separator: "\n").map(String.init)
    }

    /// The parent of the commit that added `tasklist` (following renames into `Completed/`).
    public static func baseOf(tasklist: String, in repo: String) -> String? {
        guard let added = lines(["log", "--follow", "--diff-filter=A", "--format=%H", "--", tasklist], in: repo).last else { return nil }
        return run(["rev-parse", "--short", added + "^"], in: repo)?.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// Insertions plus deletions in one commit; nil when git cannot resolve it.
    public static func commitLines(_ sha: String, in repo: String) -> Int? {
        guard let out = run(["show", "--shortstat", "--format=", sha], in: repo) else { return nil }
        let numbers = out.split(whereSeparator: { !$0.isNumber }).compactMap { Int($0) }
        // shortstat: "N files changed, X insertions(+), Y deletions(-)"
        return numbers.count >= 2 ? numbers.dropFirst().reduce(0, +) : nil
    }

    /// Insertions plus deletions between `base` and HEAD.
    public static func changedLines(since base: String, in repo: String) -> Int? {
        guard let stat = run(["diff", "--shortstat", base, "HEAD"], in: repo) else { return nil }
        return stat.components(separatedBy: ",").reduce(0) { total, part in
            let words = part.split(separator: " ")
            guard let n = words.first.flatMap({ Int($0) }), part.contains("insertion") || part.contains("deletion") else { return total }
            return total + n
        }
    }

    /// The first `Tasklist-*.md` a commit touched, by file name.
    public static func tasklist(touchedBy sha: String, in repo: String) -> String? {
        lines(["show", "--name-only", "--format=", sha], in: repo)
            .map { ($0 as NSString).lastPathComponent }
            .first { $0.hasPrefix("Tasklist-") && $0.hasSuffix(".md") }
    }
}

extension SignalInput {
    /// Gathers everything from git and the files on disk. `base` scopes the rung-size and subsystem checks.
    public static func gather(repo: String, base: String?, statusPath: String?, log: [LogEvent], currentList: String?) -> SignalInput {
        var input = SignalInput()
        let swiftPaths = Git.lines(["ls-files", "--", "*.swift"], in: repo)
        input.swiftFiles = swiftPaths.compactMap { path in
            (try? String(contentsOfFile: (repo as NSString).appendingPathComponent(path), encoding: .utf8)).map { (path, $0) }
        }
        let candidates = statusPath.map { [$0] } ?? ["Documentation", "docs", "Docs"].map { "\($0)/Quality/Status.md" }
        for path in candidates {
            let full = path.hasPrefix("/") ? path : (repo as NSString).appendingPathComponent(path)
            if let text = try? String(contentsOfFile: full, encoding: .utf8) {
                input.status = QualityStatus(text: text)
                input.statusPath = path
                break
            }
        }
        if let sha = input.status?.lastReviewSha, Git.run(["cat-file", "-e", sha + "^{commit}"], in: repo) != nil {
            input.reviewFiles = Git.lines(["ls-tree", "-r", "--name-only", sha], in: repo).filter { $0.hasSuffix(".swift") }
            let grep = Git.run(["grep", "-h", "-E", "(struct|class|enum|actor|protocol)[[:space:]]+[A-Z]", sha, "--", "*.swift"], in: repo) ?? ""
            input.reviewTypeNames = Signals.typeNames(in: grep)
            var counts: [String: Int] = [:]
            Git.lines(["log", "--format=", "--name-only", "\(sha)..HEAD", "--", "*.swift"], in: repo).forEach { counts[$0, default: 0] += 1 }
            input.churn = counts.map { ($0.key, $0.value) }.sorted { $0.commits > $1.commits }
        } else {
            var counts: [String: Int] = [:]
            Git.lines(["log", "-n", "200", "--format=", "--name-only", "--", "*.swift"], in: repo).forEach { counts[$0, default: 0] += 1 }
            input.churn = counts.map { ($0.key, $0.value) }.sorted { $0.commits > $1.commits }
        }
        if let base {
            input.rungLines = Git.changedLines(since: base, in: repo)
            let peers = RunSummary.byList(log: log, repo: repo) { Git.tasklist(touchedBy: $0, in: repo) }
                .values.filter { RunSummary.isRungList($0.list) && $0.list != currentList }
                .sorted { $0.lastTS < $1.lastTS }.suffix(5)
            input.priorRungLines = peers.map(\.lines)
        }
        if let since = base ?? input.status?.lastReviewSha {
            input.newSubsystemDocs = Git.lines(["diff", "--name-only", "--diff-filter=A", since, "HEAD"], in: repo).filter {
                let name = ($0 as NSString).lastPathComponent
                return $0.contains("SystemDesign/") && name.hasSuffix(".md") && !name.hasPrefix("Rung-") && name != "Overview.md"
            }
        }
        return input
    }
}
