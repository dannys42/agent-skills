import Foundation

/// Unified diff of two texts, for `--dry-run`.
public enum UnifiedDiff {
    public static func make(old: String, new: String, name: String, context: Int = 3) -> String {
        func split(_ text: String) -> [String] {
            var lines = text.components(separatedBy: "\n")
            if text.hasSuffix("\n") { lines.removeLast() }
            return lines
        }
        let a = split(old), b = split(new)
        var prefix = 0
        while prefix < a.count, prefix < b.count, a[prefix] == b[prefix] { prefix += 1 }
        var suffix = 0
        while suffix < a.count - prefix, suffix < b.count - prefix, a[a.count - 1 - suffix] == b[b.count - 1 - suffix] { suffix += 1 }
        let midA = Array(a[prefix..<(a.count - suffix)]), midB = Array(b[prefix..<(b.count - suffix)])

        // Edit script over the differing middle: (" ", "-" or "+", text).
        var ops: [(tag: Character, text: String)] = a[..<prefix].map { (" ", $0) }
        if midA.count * midB.count > 4_000_000 {
            ops += midA.map { ("-", $0) } + midB.map { ("+", $0) }
        } else {
            var table = Array(repeating: Array(repeating: 0, count: midB.count + 1), count: midA.count + 1)
            for i in stride(from: midA.count - 1, through: 0, by: -1) {
                for j in stride(from: midB.count - 1, through: 0, by: -1) {
                    table[i][j] = midA[i] == midB[j] ? table[i + 1][j + 1] + 1 : max(table[i + 1][j], table[i][j + 1])
                }
            }
            var i = 0, j = 0
            while i < midA.count || j < midB.count {
                if i < midA.count, j < midB.count, midA[i] == midB[j] { ops.append((" ", midA[i])); i += 1; j += 1 }
                else if i < midA.count, j == midB.count || table[i + 1][j] >= table[i][j + 1] { ops.append(("-", midA[i])); i += 1 }
                else { ops.append(("+", midB[j])); j += 1 }
            }
        }
        ops += a[(a.count - suffix)...].map { (" ", $0) }

        let changed = ops.indices.filter { ops[$0].tag != " " }
        guard !changed.isEmpty else { return "" }
        var out = ["--- a/\(name)", "+++ b/\(name)"]
        var index = 0
        while index < changed.count {
            var last = changed[index]
            var end = index
            while end + 1 < changed.count, changed[end + 1] - last <= 2 * context + 1 { end += 1; last = changed[end] }
            let from = max(0, changed[index] - context), to = min(ops.count - 1, last + context)
            let slice = ops[from...to]
            let oldStart = ops[..<from].filter { $0.tag != "+" }.count, newStart = ops[..<from].filter { $0.tag != "-" }.count
            let oldCount = slice.filter { $0.tag != "+" }.count, newCount = slice.filter { $0.tag != "-" }.count
            out.append("@@ -\(oldCount == 0 ? oldStart : oldStart + 1),\(oldCount) +\(newCount == 0 ? newStart : newStart + 1),\(newCount) @@")
            out += slice.map { "\($0.tag)\($0.text)" }
            index = end + 1
        }
        return out.joined(separator: "\n")
    }
}

public struct EditReport {
    public var stdout: [String]
    public var stderr: [String]
}

/// Reads a file, applies one edit, and writes it back only when every check passed.
public enum Editor {
    public static func apply(file: String, dryRun: Bool, _ make: (Tasklist) throws -> Edit) throws -> EditReport {
        let path = URL(fileURLWithPath: file).resolvingSymlinksInPath().path
        guard let original = try? String(contentsOfFile: path, encoding: .utf8) else { throw EditUsageError("cannot read \(file)") }
        if original.utf8.contains(13) { throw Tasklist.EditError.refused("\(file) has CRLF line endings; this tool edits LF files only") }
        let edit = try make(Tasklist(text: original))
        let warnings = edit.warnings
        guard edit.changed else { return EditReport(stdout: [edit.summary], stderr: warnings) }
        if dryRun {
            return EditReport(stdout: [UnifiedDiff.make(old: original, new: edit.text, name: file), "dry run: nothing written"], stderr: warnings)
        }
        // Someone else may have saved the file while the edit was being made.
        guard (try? String(contentsOfFile: path, encoding: .utf8)) == original else {
            throw Tasklist.EditError.refused("\(file) changed while it was being edited; nothing written, run the command again")
        }
        let directory = URL(fileURLWithPath: path).deletingLastPathComponent().path
        let temporary = "\(directory)/.\(URL(fileURLWithPath: path).lastPathComponent).\(ProcessInfo.processInfo.processIdentifier).tmp"
        do {
            let attributes = try FileManager.default.attributesOfItem(atPath: path)
            try Data(edit.text.utf8).write(to: URL(fileURLWithPath: temporary))
            if let permissions = attributes[.posixPermissions] { try FileManager.default.setAttributes([.posixPermissions: permissions], ofItemAtPath: temporary) }
            guard rename(temporary, path) == 0 else { throw EditUsageError("cannot replace \(file): \(String(cString: strerror(errno)))") }
        } catch {
            try? FileManager.default.removeItem(atPath: temporary)
            throw error
        }
        return EditReport(stdout: [edit.result ?? edit.summary], stderr: warnings)
    }
}
