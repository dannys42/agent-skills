import Foundation

/// The `skill` stamp of a logged `step` event: `<skill-name> <plugin version>`, as `scripts/bump_version.py` writes it
/// (`tasklist-run 0.17.2`). A bare version or a retro number (`roadmap-plan-next-rung 0018`) is malformed.
public enum SkillStamp {
    public static func isValid(_ stamp: String?) -> Bool {
        guard let stamp else { return false }
        return stamp.range(of: #"^[a-z][a-z0-9]*(-[a-z0-9]+)* [0-9]+\.[0-9]+\.[0-9]+$"#, options: .regularExpression) != nil
    }

    /// One warning per distinct malformed stamp on a `step` event, with how many events carry it; a missing stamp counts as `(none)`.
    public static func warnings(log: [LogEvent]) -> [String] {
        var counts: [String: Int] = [:]
        var order: [String] = []
        for e in log where e.string("event") == "step" && !isValid(e.string("skill")) {
            let stamp = e.string("skill") ?? "(none)"
            if counts[stamp] == nil { order.append(stamp) }
            counts[stamp, default: 0] += 1
        }
        return order.map { "warning: malformed `skill` stamp \"\($0)\" on \(counts[$0]!) step event(s); expected \"<skill-name> <x.y.z>\"" }
    }
}

/// Escaped defects: bug tasks that cite `Escaped from: <RungId>`, counted per rung.
public enum Escapes {
    /// Counts the `Escaped from:` field lines in tasklist texts. The rung ID is the first word after the colon, minus backticks and trailing punctuation.
    public static func byRung(texts: [String]) -> [String: Int] {
        var out: [String: Int] = [:]
        for text in texts {
            for line in text.split(separator: "\n", omittingEmptySubsequences: true) {
                guard let match = line.range(of: #"^\s*(?:[-*]\s+)?(?:\*\*)?Escaped from:(?:\*\*)?\s*`?([A-Za-z0-9]+)"#, options: .regularExpression) else { continue }
                let id = line[match].split(separator: " ").last.map { $0.trimmingCharacters(in: CharacterSet(charactersIn: "`*:")) } ?? ""
                if !id.isEmpty, id != "Escaped" { out[id, default: 0] += 1 }
            }
        }
        return out
    }

    /// The tasklists tracked in `repo`, read from disk.
    public static func byRung(repo: String) -> [String: Int] {
        let paths = Git.lines(["ls-files", "--", "*Tasklist*.md"], in: repo)
        return byRung(texts: paths.compactMap { try? String(contentsOfFile: (repo as NSString).appendingPathComponent($0), encoding: .utf8) })
    }

    public static func render(_ counts: [String: Int], rung: String?) -> String? {
        guard !counts.isEmpty else { return nil }
        let all = counts.sorted { $0.key.localizedStandardCompare($1.key) == .orderedAscending }.map { "\($0.key) \($0.value)" }.joined(separator: ", ")
        var line = "Escaped defects by rung: \(all)."
        if let rung { line = "Escaped defects from \(rung): \(counts[rung] ?? 0). " + line }
        return line
    }
}
