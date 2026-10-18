import Foundation

/// How well the skills' predictions held: the declared tier of each batch against the rounds it took, and each recommended
/// model for the next step against the model that step actually ran on, with what the run cost in either case.
public enum Predictions {
    static let tierOrder = ["light": 0, "standard": 1, "heavy": 2]

    /// `roadmap-plan-next-rung 0.7.0` → `roadmap-plan-next-rung`; `/task-workflow:tasklist-run L3` → `tasklist-run`.
    public static func skillName(_ text: String?) -> String? {
        guard let word = text?.split(separator: " ").first else { return nil }
        let name = word.drop { $0 == "/" }
        return String(name.split(separator: ":").last ?? name)
    }

    struct Tally { var n = 0, rounds = 0, raised = 0, lines = 0 }

    static func mean(_ sum: Int, _ n: Int) -> String { n == 0 ? "–" : String(format: "%.2f", Double(sum) / Double(n)) }

    /// A mixed batch counts under the highest tier among its tasks, as `tasklist-run` dispatches it.
    static func tierCalibration(_ log: [LogEvent]) -> [String] {
        var byTier: [String: Tally] = [:]
        var byRepoTier: [String: [String: Tally]] = [:]
        for e in log where e.string("event") == "batch" {
            guard let tier = e.strings("tiers").filter({ tierOrder[$0] != nil }).max(by: { tierOrder[$0]! < tierOrder[$1]! }) else { continue }
            for key in [("all", tier), (e.string("repo") ?? "?", tier)] {
                var t = key.0 == "all" ? byTier[tier] ?? Tally() : byRepoTier[key.0]?[tier] ?? Tally()
                t.n += 1
                t.rounds += e.int("rounds") ?? 0
                t.raised += e.bool("raised") ? 1 : 0
                t.lines += e.int("lines") ?? 0
                if key.0 == "all" { byTier[tier] = t } else { byRepoTier[key.0, default: [:]][tier] = t }
            }
        }
        guard !byTier.isEmpty else { return ["No batches logged yet."] }
        var out = ["Declared tier against what the batch needed:", "", "| Tier | Batches | Rounds/batch | Raised | Lines/batch |", "| --- | --- | --- | --- | --- |"]
        for tier in tierOrder.keys.sorted(by: { tierOrder[$0]! < tierOrder[$1]! }) {
            guard let t = byTier[tier] else { continue }
            out.append("| \(tier) | \(t.n) | \(mean(t.rounds, t.n)) | \(t.raised) | \(mean(t.lines, t.n)) |")
        }
        if byRepoTier.count > 1 {
            out += ["", "By repository (rounds per batch; n in brackets):", "", "| Repo | " + tierOrder.keys.sorted(by: { tierOrder[$0]! < tierOrder[$1]! }).joined(separator: " | ") + " |", "| --- | --- | --- | --- |"]
            for repo in byRepoTier.keys.sorted() {
                let cells = tierOrder.keys.sorted(by: { tierOrder[$0]! < tierOrder[$1]! }).map { tier -> String in
                    guard let t = byRepoTier[repo]?[tier] else { return "–" }
                    return "\(mean(t.rounds, t.n)) (\(t.n))"
                }
                out.append("| \((repo as NSString).lastPathComponent) | " + cells.joined(separator: " | ") + " |")
            }
        }
        return out
    }

    struct Pair { let from: String, next: String, recommended: String, actual: String, run: String? }

    /// Each `step` that named a next step, paired with the first later event of the skill it named in the same repo.
    static func pairs(_ log: [LogEvent]) -> [Pair] {
        var out: [Pair] = []
        for (i, s) in log.enumerated() where s.string("event") == "step" {
            guard let next = s.string("next"), next != "none", let name = skillName(next), let rec = s.string("next_model"),
                  let from = skillName(s.string("skill")) else { continue }
            let follower = log.dropFirst(i + 1).first { e in
                guard e.string("repo") == s.string("repo") else { return false }
                if e.string("event") == "start", e.string("model") != nil { return name == "tasklist-run" }
                return e.string("event") == "step" && skillName(e.string("skill")) == name
            }
            guard let follower, let actual = follower.string("model") else { continue }
            out.append(Pair(from: from, next: name, recommended: rec.lowercased(), actual: TranscriptTokens.shortModel(actual),
                            run: follower.string("event") == "start" ? follower.string("run") : nil))
        }
        return out
    }

    static func followThrough(_ log: [LogEvent]) -> [String] {
        let all = pairs(log)
        let steps = log.filter { $0.string("event") == "step" && $0.string("next") != nil && $0.string("next") != "none" }.count
        guard !all.isEmpty else {
            return steps == 0 ? ["No `step` events with a recommendation logged yet."] : ["\(steps) recommendation(s) logged; none followed by a logged step yet."]
        }
        var edges: [String: [Pair]] = [:]
        all.forEach { edges["\($0.from) → \($0.next)", default: []].append($0) }
        var out = ["Recommended model against the model the next step ran on:", "", "| Step | Pairs | Followed | Ran on instead |", "| --- | --- | --- | --- |"]
        for edge in edges.keys.sorted() {
            let ps = edges[edge]!
            let followed = ps.filter { $0.recommended == $0.actual }.count
            let others = Dictionary(grouping: ps.filter { $0.recommended != $0.actual }, by: \.actual).map { "\($0.key) ×\($0.value.count)" }.sorted()
            out.append("| \(edge) | \(ps.count) | \(followed) | \(others.isEmpty ? "–" : others.joined(separator: ", ")) |")
        }
        out += runOutcomes(log, all.filter { $0.run != nil })
        return out
    }

    /// For `tasklist-run` followers: did running on the recommended model cost more rounds or more user corrections?
    static func runOutcomes(_ log: [LogEvent], _ runs: [Pair]) -> [String] {
        guard !runs.isEmpty else { return [] }
        func stats(_ ps: [Pair]) -> (runs: Int, rounds: String, interventions: String) {
            var rounds = 0, batches = 0, interventions = 0
            for p in ps {
                for e in log where e.string("run") == p.run {
                    if e.string("event") == "batch" { batches += 1; rounds += e.int("rounds") ?? 0 }
                    if e.string("event") == "end" { interventions += e.int("interventions") ?? 0 }
                }
            }
            return (ps.count, mean(rounds, batches), mean(interventions, ps.count))
        }
        var out = ["", "Orchestrator choice for `tasklist-run`, by outcome (small samples say little; treat as a hypothesis):", "", "| Orchestrator | Runs | Rounds/batch | Corrections/run |", "| --- | --- | --- | --- |"]
        for (label, ps) in [("recommended model", runs.filter { $0.recommended == $0.actual }), ("another model", runs.filter { $0.recommended != $0.actual })] where !ps.isEmpty {
            let s = stats(ps)
            out.append("| \(label) | \(s.runs) | \(s.rounds) | \(s.interventions) |")
        }
        return out
    }

    public static func render(log all: [LogEvent], repo: String? = nil) -> String {
        let log = repo.map { r in all.filter { $0.string("repo") == r } } ?? all
        return (tierCalibration(log) + [""] + followThrough(log)).joined(separator: "\n")
    }
}
