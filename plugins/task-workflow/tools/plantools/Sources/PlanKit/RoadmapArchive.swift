import Foundation

/// `roadmap archive`: moves finished rungs' `###` sections verbatim to the Completed file
/// and points their ladder lines at it, as `risk-first-roadmap`'s "Keep the roadmap small" says.
public struct RoadmapArchive {
    public static let finishedStatuses = ["done", "failed", "changed", "obsolete"]

    public var roadmap: String
    public var completed: String
    public var moved: [String]
    public var skipped: [String]    // already archived: "L1 (already archived)"

    /// `completedPath` is the Completed file as the ladder line names it, relative to the roadmap.
    /// `completed` is that file's current text, or nil when it does not exist yet.
    public static func make(roadmap text: String, ids: [String], completedPath: String, completed: String?) throws -> RoadmapArchive {
        if text.utf8.contains(13) { throw Tasklist.EditError.refused("the roadmap has CRLF line endings; this tool edits LF files only") }
        let before = Roadmap(text: text)
        var lines = before.markdown.lines
        var ranges: [(id: String, first: Int, last: Int)] = []
        var moved: [String] = [], skipped: [String] = []

        var seen = Set<String>()
        for raw in ids {
            guard let rung = before.ladder.first(where: { $0.id.lowercased() == raw.lowercased() }), rung.status != "horizon" else {
                throw Tasklist.EditError.refused("no rung \(raw) on the ladder")
            }
            guard seen.insert(rung.id).inserted else { continue }
            guard finishedStatuses.contains(where: { rung.status.hasPrefix($0) }) else {
                throw Tasklist.EditError.refused("\(rung.id) is \(rung.status); only done, failed or obsolete rungs are archived")
            }
            let sections = before.details.filter { $0.id == rung.id }
            if sections.count > 1 { throw Tasklist.EditError.refused("\(rung.id) has \(sections.count) detail sections; fix the duplicate first") }
            let line = lines[rung.line - 1]
            let pointed = line.range(of: " detail:", options: .backwards) != nil
            guard let detail = sections.first, let section = before.markdown.sections.first(where: { $0.line == detail.line }) else {
                if pointed { skipped.append("\(rung.id) (already archived)"); continue }
                throw Tasklist.EditError.refused("\(rung.id) has no detail section and no detail: pointer")
            }
            if pointed { throw Tasklist.EditError.refused("\(rung.id) already has a detail: pointer and still has a section; check which copy is current") }
            lines[rung.line - 1] = line + " detail: " + completedPath
            ranges.append((rung.id, section.line, section.endLine))
            moved.append(rung.id)
        }

        var archive = completed ?? "# Finished rungs\n\nMoved verbatim from the roadmap by `roadmap archive`; the ladder line keeps each ID.\n"
        for range in ranges.sorted(by: { $0.first < $1.first }) {
            var block = Array(lines[(range.first - 1)...(range.last - 1)])
            while block.last?.trimmingCharacters(in: .whitespaces).isEmpty == true { block.removeLast() }
            while archive.hasSuffix("\n\n") { archive.removeLast() }
            archive += (archive.hasSuffix("\n") || archive.isEmpty ? "" : "\n") + "\n" + block.joined(separator: "\n") + "\n"
        }
        for range in ranges.sorted(by: { $0.first > $1.first }) {
            lines.removeSubrange((range.first - 1)...(range.last - 1))
        }
        let after = lines.joined(separator: "\n")

        func errors(_ t: String) -> Set<String> {
            Set(Roadmap(text: t).lint().filter { $0.severity == .error }.map(\.message))
        }
        let added = errors(after).subtracting(errors(text))
        if !added.isEmpty { throw Tasklist.EditError.lint(added.sorted()) }
        return RoadmapArchive(roadmap: after, completed: archive, moved: moved, skipped: skipped)
    }

    /// `Completed/Roadmap-<Topic>-Rungs.md` beside the roadmap.
    public static func completedPath(forRoadmap file: String) -> String {
        let name = URL(fileURLWithPath: file).deletingPathExtension().lastPathComponent
        return "Completed/\(name)-Rungs.md"
    }
}
