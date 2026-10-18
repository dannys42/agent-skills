import Foundation

/// One rung's numbers, summed over every `tasklist-run` run of its tasklist.
public struct RungNumbers {
    public struct Agent { public let tasks: String; public let role: String; public let tokens: Int; public let tools: Int }

    public let list: String
    public var runs: Set<String> = []
    public var lastTS = ""
    public var batches = 0, blocked = 0, raised = 0, lines = 0, files = 0, rounds = 0
    public var kept = 0, dropped = 0, required = 0, optLeft = 0
    public var agents: [Agent] = []
    public var orchTokens: Int?, cacheBreaks: Int?
    /// Batches with two or more correction rounds, a tier raise or a block.
    public var hardBatches: [String] = []

    public var implTokens: Int { agents.filter { $0.role == "impl" }.reduce(0) { $0 + $1.tokens } }
    public var revTokens: Int { agents.filter { $0.role == "rev" }.reduce(0) { $0 + $1.tokens } }
    public var medianTools: Int? { RunSummary.median(agents.map(\.tools)) }

    /// `Tasklist-L20-Foo.md` → `L20`; nil for lists that are not rung lists.
    public var rung: String? { RunSummary.rung(of: list) }
}

/// The retrospective's numbers table, so the model never adds up log lines by hand.
public enum RunSummary {
    public static func rung(of list: String) -> String? {
        guard list.hasPrefix("Tasklist-") else { return nil }
        let id = list.dropFirst("Tasklist-".count).prefix { $0 != "-" && $0 != "." }
        return id.isEmpty ? nil : String(id)
    }

    static func isRungList(_ list: String) -> Bool { rung(of: list) != nil && !list.contains("-Tidy") }

    public static func median(_ values: [Int]) -> Int? {
        guard !values.isEmpty else { return nil }
        let s = values.sorted()
        return s.count % 2 == 1 ? s[s.count / 2] : (s[s.count / 2 - 1] + s[s.count / 2]) / 2
    }

    /// Groups a repo's runs by tasklist file name. A run logged before `start` carried `list` is resolved
    /// through `listForSha` from its first committed batch; runs that resolve to nothing are left out.
    public static func byList(log: [LogEvent], repo: String, listForSha: (String) -> String?) -> [String: RungNumbers] {
        let events = log.filter { $0.string("repo") == repo }
        var listOfRun: [String: String] = [:]
        for e in events where e.string("event") == "start" {
            if let run = e.string("run"), let list = e.string("list") { listOfRun[run] = (list as NSString).lastPathComponent }
        }
        for e in events where e.string("event") == "batch" {
            guard let run = e.string("run"), listOfRun[run] == nil, let sha = e.string("sha"), let list = listForSha(sha) else { continue }
            listOfRun[run] = list
        }
        var out: [String: RungNumbers] = [:]
        for e in events {
            guard let run = e.string("run"), let list = listOfRun[run] else { continue }
            var n = out[list] ?? RungNumbers(list: list)
            n.runs.insert(run)
            n.lastTS = max(n.lastTS, e.string("ts") ?? "")
            let tasks = e.strings("tasks").joined(separator: ",")
            switch e.string("event") {
            case "batch":
                n.batches += 1
                if e.string("outcome") == "blocked" { n.blocked += 1 }
                if e.bool("raised") { n.raised += 1 }
                n.lines += e.int("lines") ?? 0
                n.files += e.int("files") ?? 0
                let rounds = e.int("rounds") ?? 0
                n.rounds += rounds
                n.kept += e.int("kept") ?? 0
                n.dropped += e.int("dropped") ?? 0
                n.required += e.int("rev_required") ?? 0
                n.optLeft += e.int("opt_left") ?? 0
                for a in e["agents"] as? [LogEvent] ?? [] {
                    n.agents.append(.init(tasks: tasks, role: a.string("role") ?? "?", tokens: a.int("tokens") ?? 0, tools: a.int("tools") ?? 0))
                }
                var why: [String] = []
                if rounds >= 2 { why.append("\(rounds) correction rounds") }
                if e.bool("raised") { why.append("tier raised") }
                if e.string("outcome") == "blocked" { why.append("blocked") }
                if !why.isEmpty { n.hardBatches.append("\(tasks): " + why.joined(separator: ", ")) }
            case "tokens":
                var orch = 0
                for usage in (e["orch"] as? [String: [String: Int]] ?? [:]).values { orch += usage.values.reduce(0, +) }
                n.orchTokens = (n.orchTokens ?? 0) + orch
                n.cacheBreaks = (n.cacheBreaks ?? 0) + (e.int("cache_breaks") ?? 0)
            default:
                break
            }
            out[list] = n
        }
        return out
    }

    static func k(_ n: Int) -> String { n >= 1000 ? "\(Int((Double(n) / 1000).rounded()))k" : "\(n)" }

    /// Numbers table for `target` against the median of the last `compare` rung lists before it, the largest
    /// batches by subagent tokens, and what stands out. Rows that are zero for this rung and its peers are left out.
    public static func render(target: RungNumbers, all: [String: RungNumbers], quality: [LogEvent] = [], compare: Int = 5) -> String {
        let peers = all.values
            .filter { $0.list != target.list && isRungList($0.list) && $0.lastTS <= target.lastTS }
            .sorted { $0.lastTS < $1.lastTS }
            .suffix(compare)
        var out = ["Rung numbers: \(target.list) (\(target.runs.count) run\(target.runs.count == 1 ? "" : "s"))"]
        out.append(peers.isEmpty ? "No earlier rung lists in the log to compare with." :
                   "Compared with: " + peers.map { $0.rung ?? $0.list }.joined(separator: ", "))
        out += ["", "| Metric | This rung | Median, earlier rungs |", "| --- | --- | --- |"]
        func row(_ name: String, always: Bool = false, _ value: (RungNumbers) -> Int?, format: (Int) -> String = { "\($0)" }) {
            let mine = value(target)
            let theirs = median(peers.compactMap(value))
            guard always || (mine ?? 0) != 0 || (theirs ?? 0) != 0, mine != nil || theirs != nil else { return }
            out.append("| \(name) | \(mine.map(format) ?? "–") | \(theirs.map(format) ?? "–") |")
        }
        row("Batches", always: true) { $0.batches }
        row("Lines changed", always: true) { $0.lines }
        row("Correction rounds", always: true) { $0.rounds }
        row("Tier raises") { $0.raised }
        row("Blocked") { $0.blocked }
        row("Findings kept") { $0.kept }
        row("Required findings") { $0.required }
        row("Optional findings left") { $0.optLeft }
        row("Implementer tokens", always: true, { $0.agents.isEmpty ? nil : $0.implTokens }, format: k)
        row("Reviewer tokens", { $0.agents.isEmpty ? nil : $0.revTokens }, format: k)
        row("Orchestrator tokens", { $0.orchTokens }, format: k)
        row("Median tools per agent", { $0.medianTools })
        row("Cache breaks", { $0.cacheBreaks })

        var batches: [String: [RungNumbers.Agent]] = [:]
        target.agents.forEach { batches[$0.tasks, default: []].append($0) }
        let largest = batches.sorted { $0.value.reduce(0) { $0 + $1.tokens } > $1.value.reduce(0) { $0 + $1.tokens } }.prefix(3)
        if !largest.isEmpty {
            out += ["", "Largest batches (subagent tokens):"]
            for (tasks, agents) in largest {
                let parts = agents.map { "\($0.role) \(k($0.tokens)), \($0.tools) tools" }.joined(separator: "; ")
                out.append("- \(tasks): \(k(agents.reduce(0) { $0 + $1.tokens })) (\(parts))")
            }
        }

        var standOut = target.hardBatches
        let toolsMedian = target.medianTools ?? 0
        for a in target.agents where a.tools > 30 || (toolsMedian > 0 && a.tools >= 2 * toolsMedian && a.tools > 10) {
            standOut.append("\(a.tasks): \(a.role) used \(a.tools) tools (rung median \(toolsMedian))")
        }
        if !standOut.isEmpty { out += ["", "Stands out:"] + standOut.map { "- \($0)" } }

        let mine = quality.filter { $0.string("rung") == target.rung && ($0.string("event") ?? "").hasPrefix("quality") }
        if !mine.isEmpty {
            out += ["", "Quality passes:"]
            for q in mine {
                let fields = ["kind", "trigger", "commits", "lines", "proposals", "accepted", "deferred", "rejected"]
                    .compactMap { key in q[key].map { "\(key) \($0)" } }
                out.append("- \(q.string("event") ?? ""): " + fields.joined(separator: ", "))
            }
        }
        return out.joined(separator: "\n")
    }
}
