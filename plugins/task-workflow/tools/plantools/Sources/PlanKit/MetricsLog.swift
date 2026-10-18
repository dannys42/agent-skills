import Foundation

/// One line of the `tasklist-run` metrics log, kept as a plain JSON object.
public typealias LogEvent = [String: Any]

/// The shared metrics log: `~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl`.
public enum MetricsLog {
    public static var defaultPath: String {
        FileManager.default.homeDirectoryForCurrentUser.path + "/.local/state/danny-agent-skills/task-workflow/metrics.jsonl"
    }

    /// Unparseable lines are skipped, like the Python analyzer did.
    public static func events(text: String) -> [LogEvent] { events(data: Data(text.utf8)) }

    public static func events(data: Data) -> [LogEvent] {
        data.split(separator: UInt8(ascii: "\n")).compactMap { line in
            (try? JSONSerialization.jsonObject(with: line)) as? LogEvent
        }
    }

    public static func encode(_ event: LogEvent) -> String {
        guard let data = try? JSONSerialization.data(withJSONObject: event, options: [.sortedKeys, .withoutEscapingSlashes]) else { return "{}" }
        return String(decoding: data, as: UTF8.self)
    }

    private static let withFraction: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f
    }()
    private static let withoutFraction = ISO8601DateFormatter()

    public static func date(_ text: String?) -> Date? {
        guard let text else { return nil }
        return withFraction.date(from: text) ?? withoutFraction.date(from: text)
    }
}

extension Dictionary where Key == String, Value == Any {
    func string(_ key: String) -> String? { self[key] as? String }
    func int(_ key: String) -> Int? { (self[key] as? NSNumber)?.intValue }
    func bool(_ key: String) -> Bool { (self[key] as? NSNumber)?.boolValue ?? false }
    func strings(_ key: String) -> [String] { self[key] as? [String] ?? [] }
}

/// Exact token counts per batch from Claude Code session transcripts, appended as `tokens` events.
/// Port of the former `analyze_transcripts.py --append-tokens` (identical events on the real log), with one difference: a batch
/// whose window has no transcript turns at all (no transcripts for the repo, or they were cleaned up)
/// is skipped instead of logged as zeros.
public enum TranscriptTokens {
    static let cacheBreakUncached = 100_000
    static let roles = ["orch", "impl", "rev"]

    struct Usage {
        var input = 0, cacheRead = 0, cacheWrite = 0, output = 0
        var json: [String: Int] { ["in": input, "cr": cacheRead, "cw": cacheWrite, "out": output] }
        static func + (a: Usage, b: Usage) -> Usage {
            Usage(input: a.input + b.input, cacheRead: a.cacheRead + b.cacheRead, cacheWrite: a.cacheWrite + b.cacheWrite, output: a.output + b.output)
        }
    }

    struct Turn { let date: Date; let model: String; let usage: Usage }

    static func shortModel(_ model: String?) -> String {
        let m = (model ?? "").lowercased()
        return ["opus", "sonnet", "haiku", "fable"].first { m.contains($0) } ?? (model ?? "?")
    }

    /// Claude Code's project folder name: every character that is not an ASCII letter or digit becomes `-`.
    static func projectDir(root: String, repo: String) -> String {
        let name = String(String.UnicodeScalarView(repo.unicodeScalars.map { $0.isASCII && CharacterSet.alphanumerics.contains($0) ? $0 : "-" }))
        return (root as NSString).appendingPathComponent(name)
    }

    /// Parsed transcripts, so each file is read once per call however many batch windows it spans.
    final class Cache {
        var turns: [String: [Turn]] = [:]
        func turns(path: String) -> [Turn] {
            if let hit = turns[path] { return hit }
            let parsed = TranscriptTokens.turns(path: path)
            turns[path] = parsed
            return parsed
        }
    }

    static let assistantMarker = Data(#""type":"assistant""#.utf8)

    /// One turn per API request; a request logged in several records counts once (the last record wins).
    static func turns(path: String) -> [Turn] {
        guard let data = FileManager.default.contents(atPath: path) else { return [] }
        var byRequest: [String: Turn] = [:]
        var order: [String] = []
        let lines = data.split(separator: UInt8(ascii: "\n")).filter { $0.range(of: assistantMarker) != nil }
        let records = lines.compactMap { (try? JSONSerialization.jsonObject(with: $0)) as? LogEvent }
        for record in records where record.string("type") == "assistant" {
            guard let date = MetricsLog.date(record.string("timestamp")),
                  let message = record["message"] as? LogEvent, let u = message["usage"] as? LogEvent else { continue }
            let usage = Usage(input: u.int("input_tokens") ?? 0, cacheRead: u.int("cache_read_input_tokens") ?? 0,
                              cacheWrite: u.int("cache_creation_input_tokens") ?? 0, output: u.int("output_tokens") ?? 0)
            let key = record.string("requestId") ?? record.string("uuid") ?? ""
            if byRequest[key] == nil { order.append(key) }
            byRequest[key] = Turn(date: date, model: message.string("model") ?? "", usage: usage)
        }
        return order.compactMap { byRequest[$0] }
    }

    static func files(in dir: String, prefix: String = "", suffix: String) -> [String] {
        let names = (try? FileManager.default.contentsOfDirectory(atPath: dir)) ?? []
        return names.filter { $0.hasPrefix(prefix) && $0.hasSuffix(suffix) }.sorted().map { (dir as NSString).appendingPathComponent($0) }
    }

    /// Raw tokens by role and model for transcripts of `repo` with turns in (lo, hi]; nil when there are none.
    static func window(root: String, repo: String, lo: Date, hi: Date, cache: Cache = Cache()) -> LogEvent? {
        var usage: [String: [String: Usage]] = ["orch": [:], "impl": [:], "rev": [:]]
        var orchTurns = 0, implAgents = 0, revAgents = 0
        var uncached: [Int] = []
        func add(_ role: String, _ turn: Turn) {
            let model = shortModel(turn.model)
            usage[role, default: [:]][model] = (usage[role]?[model] ?? Usage()) + turn.usage
            uncached.append(turn.usage.input + turn.usage.cacheWrite)
        }
        for path in files(in: projectDir(root: root, repo: repo), suffix: ".jsonl") {
            let modified = (try? FileManager.default.attributesOfItem(atPath: path)[.modificationDate] as? Date) ?? .distantFuture
            if modified < lo { continue }
            for turn in cache.turns(path: path) where lo < turn.date && turn.date <= hi {
                add("orch", turn)
                orchTurns += 1
            }
            let session = String(path.dropLast(6))
            for agent in files(in: session + "/subagents", prefix: "agent-", suffix: ".jsonl") {
                let agentTurns = cache.turns(path: agent)
                guard let first = agentTurns.map(\.date).min(), lo < first, first <= hi else { continue }
                let meta = (try? Data(contentsOf: URL(fileURLWithPath: String(agent.dropLast(6)) + ".meta.json")))
                    .flatMap { try? JSONSerialization.jsonObject(with: $0) as? LogEvent }
                let role = (meta?.string("description") ?? "").lowercased().contains("review") ? "rev" : "impl"
                if role == "rev" { revAgents += 1 } else { implAgents += 1 }
                agentTurns.forEach { add(role, $0) }
            }
        }
        guard !uncached.isEmpty else { return nil }
        var out: LogEvent = [:]
        for role in roles { out[role] = usage[role]!.mapValues(\.json) }
        out["orch_turns"] = orchTurns
        out["impl_agents"] = implAgents
        out["rev_agents"] = revAgents
        out["cache_breaks"] = uncached.filter { $0 > cacheBreakUncached }.count
        out["max_uncached"] = uncached.max() ?? 0
        return out
    }

    /// New `tokens` events for batches that have none yet, in log order, and the count of batches skipped
    /// because no transcript turn fell in their window.
    public static func newEvents(log: [LogEvent], root: String) -> (events: [LogEvent], skipped: Int) {
        let done = Set(log.filter { $0.string("event") == "tokens" }.map { "\($0.string("run") ?? "")|\($0.string("batch_ts") ?? "")" })
        var previous: [String: Date] = [:]
        var out: [LogEvent] = []
        var skipped = 0
        let cache = Cache()
        for event in log {
            let run = event.string("run") ?? ""
            guard let ts = event.string("ts"), let date = MetricsLog.date(ts) else { continue }
            switch event.string("event") {
            case "start":
                previous[run] = date
            case "batch":
                let lo = previous[run] ?? date.addingTimeInterval(-2 * 3600)
                previous[run] = date
                if done.contains("\(run)|\(ts)") { continue }
                guard let repo = event.string("repo"), var tokens = window(root: root, repo: repo, lo: lo, hi: date, cache: cache) else {
                    skipped += 1
                    continue
                }
                tokens["v"] = 1
                tokens["run"] = run
                tokens["ts"] = ts
                tokens["event"] = "tokens"
                tokens["batch_ts"] = ts
                tokens["repo"] = repo
                tokens["tasks"] = event["tasks"] ?? NSNull()
                out.append(tokens)
            default:
                continue
            }
        }
        return (out, skipped)
    }
}
