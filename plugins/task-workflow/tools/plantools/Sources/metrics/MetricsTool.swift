import ArgumentParser
import Foundation
import PlanKit

@main
struct MetricsTool: ParsableCommand {
    static let configuration = CommandConfiguration(
        commandName: "metrics",
        abstract: "Read the tasklist-run metrics log and the repository so the model does not count by hand. Plain text out.",
        version: planToolsVersion,
        subcommands: [Tokens.self, Summary.self, Signals.self, Predictions.self]
    )

    struct LogOption: ParsableArguments {
        @Option(help: "Metrics log (default ~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl).") var log: String?
        var path: String { log ?? MetricsLog.defaultPath }
        var events: [LogEvent] { (try? String(contentsOfFile: path, encoding: .utf8)).map(MetricsLog.events) ?? [] }
    }

    static func repoRoot() -> String {
        guard let root = Git.run(["rev-parse", "--show-toplevel"], in: FileManager.default.currentDirectoryPath) else {
            CLI.fail("not inside a git repository")
        }
        return root.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    struct Tokens: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Append a `tokens` event per batch from Claude Code transcripts; idempotent. Does nothing without transcripts.")
        @OptionGroup var log: LogOption
        @Option(help: "Transcript root.") var root = FileManager.default.homeDirectoryForCurrentUser.path + "/.claude/projects"
        @Flag(help: "Print the events instead of appending them.") var dryRun = false

        func run() throws {
            let (events, skipped) = TranscriptTokens.newEvents(log: log.events, root: root)
            let lines = events.map(MetricsLog.encode)
            if dryRun {
                lines.forEach(CLI.print)
            } else if !lines.isEmpty {
                guard let handle = FileHandle(forWritingAtPath: log.path) else { CLI.fail("cannot open \(log.path)") }
                handle.seekToEndOfFile()
                handle.write(Data((lines.joined(separator: "\n") + "\n").utf8))
                handle.closeFile()
            }
            FileHandle.standardError.write(Data("\(dryRun ? "would append" : "appended") \(lines.count) tokens event(s); \(skipped) batch(es) without transcripts skipped\n".utf8))
        }
    }

    struct Summary: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "The retrospective's numbers for one tasklist (all its runs) against the median of earlier rungs.")
        @OptionGroup var log: LogOption
        @Argument(help: "Tasklist file (path or name), or a run ID.") var target: String
        @Option(help: "How many earlier rung lists to compare with.") var compare = 5

        func run() throws {
            let repo = MetricsTool.repoRoot()
            let events = log.events
            let all = RunSummary.byList(log: events, repo: repo, linesForSha: { Git.commitLines($0, in: repo) }) { Git.tasklist(touchedBy: $0, in: repo) }
            let name = (target as NSString).lastPathComponent
            var numbers = all[name]
            if numbers == nil, events.contains(where: { $0["run"] as? String == target }) {
                numbers = RunSummary.byList(log: events.filter { $0["run"] as? String == target }, repo: repo, linesForSha: { Git.commitLines($0, in: repo) }) { _ in "run \(target)" }["run \(target)"]
            }
            guard let numbers else { CLI.fail("no runs logged for \(target) in \(repo)", code: 1) }
            let quality = events.filter { ($0["repo"] as? String) == repo && (($0["event"] as? String) ?? "").hasPrefix("quality") }
            CLI.print(RunSummary.render(target: numbers, all: all, quality: quality, compare: compare))
        }
    }

    struct Predictions: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "How well the tier and model predictions held: declared tier against rounds, recommended model against the model used.")
        @OptionGroup var log: LogOption
        @Flag(help: "Only the current repository's events (default: every repository in the log, to see what is general).") var thisRepo = false

        func run() throws {
            CLI.print(PlanKit.Predictions.render(log: log.events, repo: thisRepo ? MetricsTool.repoRoot() : nil))
        }
    }

    struct Signals: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Zero-token quality signals and review triggers; exit 1 when a trigger fires.")
        @OptionGroup var log: LogOption
        @Option(help: "The rung's base commit (the brief's `Base:` line).") var base: String?
        @Option(help: "The rung's tasklist; its base is the parent of the commit that added it.") var tasklist: String?
        @Option(help: "Quality status file (default <DocDir>/Quality/Status.md under Documentation, docs or Docs).") var status: String?
        @Flag(help: "Print one compact JSON object for a `quality` event's `signals` field.") var json = false

        func run() throws {
            let repo = MetricsTool.repoRoot()
            let resolvedBase = base ?? tasklist.flatMap { Git.baseOf(tasklist: $0, in: repo) }
            if tasklist != nil, resolvedBase == nil { CLI.fail("cannot find the commit that added \(tasklist!)") }
            let input = SignalInput.gather(repo: repo, base: resolvedBase, statusPath: status, log: log.events,
                                           currentList: tasklist.map { ($0 as NSString).lastPathComponent })
            let signals = PlanKit.Signals.evaluate(input)
            if json {
                CLI.print(MetricsLog.encode(signals.json))
            } else {
                let head = Git.run(["rev-parse", "--short", "HEAD"], in: repo)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "?"
                var header = "HEAD \(head)"
                if let resolvedBase { header += " · rung base \(resolvedBase)" }
                header += " · last review \(input.status?.lastReviewSha ?? "none")"
                CLI.print(signals.render(header: header))
            }
            if !signals.triggers.isEmpty { throw ExitCode(1) }
        }
    }
}
