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
    /// Reviewer tokens from the `tokens` events (exact), for batches whose logged `agents` carry none.
    public var measuredRevTokens: Int?
    /// Batches whose logged `lines` differ from the commit's own diff, and committed batches logged with no reviewer tokens.
    public var lineMismatches = 0, silentReviews = 0
    /// Orchestrator tokens of each batch's `tokens` event, in log order, to see whether a long run gets dearer per batch.
    public var orchByBatch: [Int] = []
    /// Tokens of every role in the rung's `tokens` events.
    public var runTokens: Int?
    public var discovered = 0
    /// Planning and fold-back (`roadmap-plan-next-rung` steps for this rung): tokens from `step_tokens`, and the drift fold-back found.
    public var planTokens: Int?, drift: Int?
    public var planSteps = 0
    /// Batches with two or more correction rounds, a tier raise or a block.
    public var hardBatches: [String] = []

    public var implTokens: Int { agents.filter { $0.role == "impl" }.reduce(0) { $0 + $1.tokens } }
    public var revTokens: Int {
        let logged = agents.filter { $0.role == "rev" }.reduce(0) { $0 + $1.tokens }
        return logged > 0 ? logged : measuredRevTokens ?? 0
    }
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
    /// `linesForSha` gives a commit's insertions plus deletions from git; it replaces the logged `lines`, which the
    /// orchestrator copies by hand and sometimes gets wrong.
    public static func byList(log: [LogEvent], repo: String, linesForSha: (String) -> Int? = { _ in nil }, listForSha: (String) -> String?) -> [String: RungNumbers] {
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
                let logged = e.int("lines") ?? 0
                if let sha = e.string("sha"), let actual = linesForSha(sha) {
                    if actual != logged { n.lineMismatches += 1 }
                    n.lines += actual
                } else {
                    n.lines += logged
                }
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
                if e.string("outcome") == "committed", e.string("rev") != nil,
                   !(e["agents"] as? [LogEvent] ?? []).contains(where: { $0.string("role") == "rev" && ($0.int("tokens") ?? 0) > 0 }) {
                    n.silentReviews += 1
                }
                var why: [String] = []
                if rounds >= 2 { why.append("\(rounds) correction rounds") }
                if e.bool("raised") { why.append("tier raised") }
                if e.string("outcome") == "blocked" { why.append("blocked") }
                if !why.isEmpty { n.hardBatches.append("\(tasks): " + why.joined(separator: ", ")) }
            case "end":
                n.discovered += e.int("discovered") ?? 0
            case "tokens":
                var orch = 0
                for usage in (e["orch"] as? [String: [String: Int]] ?? [:]).values { orch += usage.values.reduce(0, +) }
                n.orchTokens = (n.orchTokens ?? 0) + orch
                n.orchByBatch.append(orch)
                let rev = tokenTotal(e, "rev")
                if rev > 0 { n.measuredRevTokens = (n.measuredRevTokens ?? 0) + rev }
                n.runTokens = (n.runTokens ?? 0) + TranscriptTokens.roles.reduce(0) { $0 + tokenTotal(e, $1) }
                n.cacheBreaks = (n.cacheBreaks ?? 0) + (e.int("cache_breaks") ?? 0)
            default:
                break
            }
            out[list] = n
        }
        attachPlanning(events: events, to: &out)
        return out
    }

    /// All tokens of one role in a `tokens` or `step_tokens` event.
    static func tokenTotal(_ e: LogEvent, _ role: String) -> Int {
        (e[role] as? [String: [String: Int]] ?? [:]).values.reduce(0) { $0 + $1.values.reduce(0, +) }
    }

    /// Planning cost belongs to the rung a `roadmap-plan-next-rung` step names, though it happens outside any run.
    static func attachPlanning(events: [LogEvent], to out: inout [String: RungNumbers]) {
        var tokens: [String: Int] = [:]
        for e in events where e.string("event") == "step_tokens" {
            tokens["\(e.string("skill") ?? "")|\(e.string("step_ts") ?? "")"] = roles(of: e)
        }
        var byRung: [String: (tokens: Int?, drift: Int?, steps: Int)] = [:]
        for e in events where e.string("event") == "step" && Predictions.skillName(e.string("skill")) == "roadmap-plan-next-rung" {
            guard let target = e.string("target") else { continue }
            var p = byRung[target] ?? (nil, nil, 0)
            p.steps += 1
            if let t = tokens["\(e.string("skill") ?? "")|\(e.string("ts") ?? "")"] { p.tokens = (p.tokens ?? 0) + t }
            if let d = e.int("drift") { p.drift = (p.drift ?? 0) + d }
            byRung[target] = p
        }
        for (list, var n) in out where isRungList(list) {
            guard let rung = n.rung, let p = byRung[rung] else { continue }
            n.planTokens = p.tokens
            n.drift = p.drift
            n.planSteps = p.steps
            out[list] = n
        }
    }

    static func roles(of e: LogEvent) -> Int { TranscriptTokens.roles.reduce(0) { $0 + tokenTotal(e, $1) } }

    /// First-half against second-half orchestrator tokens per batch; nil under four batches, where it says nothing.
    static func orchestratorTrend(_ series: [Int]) -> (line: String, ratio: Double)? {
        guard series.count >= 4 else { return nil }
        let half = series.count / 2
        let first = Double(series.prefix(half).reduce(0, +)) / Double(half)
        let second = Double(series.suffix(half).reduce(0, +)) / Double(half)
        guard first > 0 else { return nil }
        return ("Orchestrator tokens per batch: \(k(Int(first))) in the first half, \(k(Int(second))) in the second.", second / first)
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
        row("Reviewer tokens", { $0.agents.isEmpty && $0.measuredRevTokens == nil ? nil : $0.revTokens }, format: k)
        row("Orchestrator tokens", { $0.orchTokens }, format: k)
        row("Median tools per agent", { $0.medianTools })
        row("Cache breaks", { $0.cacheBreaks })
        row("Discovered tasks", { $0.discovered })
        row("Planning tokens (brief, fold-back)", { $0.planTokens }, format: k)
        row("Fold-back drift items", { $0.drift })
        if let plan = target.planTokens, let run = target.runTokens, plan + run > 0 {
            out.append("\nPlanning was \(Int((Double(plan) / Double(plan + run) * 100).rounded()))% of this rung's tokens (planning \(k(plan)), run \(k(run))).")
        }
        if let trend = orchestratorTrend(target.orchByBatch) { out.append(trend.line) }

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
        if let trend = orchestratorTrend(target.orchByBatch), trend.ratio >= 1.5 {
            standOut.append("orchestrator cost per batch rose \(Int(((trend.ratio - 1) * 100).rounded()))% from the first half of the run to the second")
        }
        if target.lineMismatches > 0 {
            standOut.append("\(target.lineMismatches) batch line(s) logged `lines` that differ from the commit's diff; the table uses the diff")
        }
        if target.silentReviews > 0 {
            standOut.append("\(target.silentReviews) reviewed batch(es) logged no reviewer tokens in `agents`; reviewer tokens use the `tokens` events where present")
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
