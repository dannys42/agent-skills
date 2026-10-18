import Foundation
import Testing
@testable import PlanKit

private func turn(_ ts: String, _ model: String, out: Int, id: String, cacheWrite: Int = 5) -> String {
    #"{"type":"assistant","timestamp":"\#(ts)","requestId":"\#(id)","message":{"model":"\#(model)","usage":{"input_tokens":1,"cache_read_input_tokens":10,"cache_creation_input_tokens":\#(cacheWrite),"output_tokens":\#(out)}}}"#
}

private func write(_ text: String, to path: String) throws {
    try FileManager.default.createDirectory(atPath: (path as NSString).deletingLastPathComponent, withIntermediateDirectories: true)
    try text.write(toFile: path, atomically: true, encoding: .utf8)
}

private func tempDir() -> String {
    let dir = NSTemporaryDirectory() + "plantools-" + UUID().uuidString
    try? FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
    return dir
}

@Suite("Transcript tokens")
struct TranscriptTokensTests {
    /// Same fixture as the Python test this replaced.
    @Test func countsWindowTokensByRoleAndSkipsLoggedBatches() throws {
        let root = tempDir() + "/projects"
        let session = root + "/-work-my-repo/s1"
        try write([turn("2026-10-01T10:00:30.500Z", "claude-opus-5-5", out: 100, id: "o1"),
                   turn("2026-10-01T10:02:00.000Z", "claude-opus-5-5", out: 10, id: "o0", cacheWrite: 150_000),
                   turn("2026-10-01T10:20:00.000Z", "claude-opus-5-5", out: 200, id: "o2")].joined(separator: "\n"), to: session + ".jsonl")
        try write(turn("2026-10-01T10:01:00.000Z", "claude-sonnet-5-5", out: 50, id: "a1"), to: session + "/subagents/agent-a1.jsonl")
        try write(#"{"description":"Implement T1"}"#, to: session + "/subagents/agent-a1.meta.json")
        try write(turn("2026-10-01T10:05:00.000Z", "claude-opus-5-5", out: 70, id: "a2"), to: session + "/subagents/agent-a2.jsonl")
        try write(#"{"description":"Review T1 diff"}"#, to: session + "/subagents/agent-a2.meta.json")
        let log = MetricsLog.events(text: """
        {"run":"R","ts":"2026-10-01T10:00:00Z","event":"start","repo":"/work/my.repo"}
        {"run":"R","ts":"2026-10-01T10:10:00Z","event":"batch","repo":"/work/my.repo","tasks":["T1"]}
        """)

        let (events, skipped) = TranscriptTokens.newEvents(log: log, root: root)
        let t = try #require(events.first)
        #expect(events.count == 1 && skipped == 0)
        #expect((t["orch"] as? [String: [String: Int]])?["opus"]?["out"] == 110)
        #expect((t["impl"] as? [String: [String: Int]])?["sonnet"]?["out"] == 50)
        #expect((t["rev"] as? [String: [String: Int]])?["opus"]?["out"] == 70)
        #expect(t.int("cache_breaks") == 1 && t.int("max_uncached") == 150_001)
        #expect(t.int("impl_agents") == 1 && t.int("rev_agents") == 1)

        #expect(TranscriptTokens.newEvents(log: log + events, root: root).events.isEmpty)
    }

    @Test func skipsBatchesWithoutTranscripts() {
        let log = MetricsLog.events(text: #"{"run":"R","ts":"2026-10-01T10:10:00Z","event":"batch","repo":"/nowhere"}"#)
        let (events, skipped) = TranscriptTokens.newEvents(log: log, root: tempDir())
        #expect(events.isEmpty && skipped == 1)
    }

    @Test func projectDirMatchesClaudeCodeNaming() {
        #expect(TranscriptTokens.projectDir(root: "/r", repo: "/Users/me/my.repo_x") == "/r/-Users-me-my-repo-x")
    }
}

@Suite("Run summary")
struct RunSummaryTests {
    static let log = MetricsLog.events(text: """
    {"run":"A","ts":"2026-10-01T10:00:00Z","event":"start","repo":"/p","list":"Tasklist-L1-One.md"}
    {"run":"A","ts":"2026-10-01T11:00:00Z","event":"batch","repo":"/p","tasks":["T1"],"rounds":0,"lines":100,"kept":0,"agents":[{"role":"impl","tokens":40000,"tools":10},{"role":"rev","tokens":20000,"tools":5}]}
    {"run":"B","ts":"2026-10-02T10:00:00Z","event":"start","repo":"/p"}
    {"run":"B","ts":"2026-10-02T11:00:00Z","event":"batch","repo":"/p","tasks":["T1"],"rounds":1,"lines":300,"kept":2,"sha":"bbb","agents":[{"role":"impl","tokens":60000,"tools":12}]}
    {"run":"C","ts":"2026-10-03T10:00:00Z","event":"start","repo":"/p","list":"Documentation/Tasklist-L3-Three.md"}
    {"run":"C","ts":"2026-10-03T11:00:00Z","event":"batch","repo":"/p","tasks":["T1"],"rounds":2,"raised":true,"lines":500,"kept":3,"agents":[{"role":"impl","tokens":90000,"tools":45},{"role":"rev","tokens":30000,"tools":8}]}
    {"run":"C","ts":"2026-10-03T12:00:00Z","event":"batch","repo":"/p","tasks":["T2","T3"],"rounds":0,"lines":50,"kept":0,"agents":[{"role":"impl","tokens":20000,"tools":6}]}
    {"run":"C","ts":"2026-10-03T13:00:00Z","event":"quality","repo":"/p","rung":"L3","kind":"tidy","trigger":"fold-back","commits":2,"lines":40,"proposals":1}
    {"run":"X","ts":"2026-10-03T13:00:00Z","event":"start","repo":"/other","list":"Tasklist-L3-Three.md"}
    """)

    @Test func groupsRunsByListAndResolvesOldRunsThroughTheirCommit() {
        let all = RunSummary.byList(log: Self.log, repo: "/p") { $0 == "bbb" ? "Tasklist-L2-Two.md" : nil }
        #expect(Set(all.keys) == ["Tasklist-L1-One.md", "Tasklist-L2-Two.md", "Tasklist-L3-Three.md"])
        let l3 = all["Tasklist-L3-Three.md"]!
        #expect(l3.batches == 2 && l3.lines == 550 && l3.rounds == 2 && l3.raised == 1)
        #expect(l3.implTokens == 110_000 && l3.revTokens == 30_000)
        #expect(l3.rung == "L3")
    }

    @Test func rendersComparisonOutliersAndQualityAndLeavesOutZeroRows() {
        let all = RunSummary.byList(log: Self.log, repo: "/p") { $0 == "bbb" ? "Tasklist-L2-Two.md" : nil }
        let quality = Self.log.filter { $0.string("event") == "quality" }
        let out = RunSummary.render(target: all["Tasklist-L3-Three.md"]!, all: all, quality: quality)
        #expect(out.contains("Compared with: L1, L2"))
        #expect(out.contains("| Lines changed | 550 | 200 |"))
        #expect(out.contains("T1: 2 correction rounds, tier raised"))
        #expect(out.contains("T1: impl used 45 tools"))
        #expect(out.contains("kind tidy"))
        #expect(!out.contains("Blocked"))
        #expect(!out.contains("Cache breaks"))
    }
}

@Suite("Quality signals")
struct SignalsTests {
    @Test func parsesStatusFields() {
        let s = QualityStatus(text: """
        # Code quality status

        Every: 4 rungs
        Last review: L12 · 1a2b3c4 · 2026-09-30 · [report](Review-2026-09-30.md)
        Since review: L13, L14, L15
        Deferred: 2026-10-18, finishing L20 first

        """)
        #expect(s.every == 4 && s.lastReviewSha == "1a2b3c4" && s.sinceReview == 3)
        #expect(s.deferred == "2026-10-18, finishing L20 first")
        #expect(s.lineCount == 6)
        #expect(QualityStatus(text: "Since review: L18–L31 (14)\nLast review: none").sinceReview == 14)
        #expect(QualityStatus(text: "Since review: L18–L31 (14)\nLast review: none").lastReviewSha == nil)
    }

    @Test func shapeIsTheLastCamelCaseWord() {
        #expect(Signals.shape(of: "Sources/Ingest/ListingChangeDeriver.swift") == "Deriver")
        #expect(Signals.shape(of: "App/SalesView.swift") == nil)
        #expect(Signals.shape(of: "Store+Queries.swift") == nil)
        #expect(Signals.shape(of: "AppStoreAPI.swift") == "API")
    }

    @Test func firesTriggersOnlyAgainstARecordedReview() {
        var input = SignalInput()
        input.swiftFiles = ["SalesDeriver", "ListingChangeDeriver", "AnalyticsDeriver", "RatingsDeriver"].map { ("Sources/\($0).swift", "struct \($0) {}\n") }
            + [("Sources/Facts.swift", "struct AnalyticsFactRow {}\nstruct AnalyticsFactInput {}\nfunc f() -> (Int, String) { (1, \"\") }\n do { } catch { }\n")]
        let baseline = Signals.evaluate(input)
        #expect(baseline.triggers.isEmpty)
        #expect(baseline.info.contains { $0.contains("*Deriver ×4") })
        #expect(baseline.info.contains { $0.contains("AnalyticsFactInput / AnalyticsFactRow") || $0.contains("AnalyticsFactRow / AnalyticsFactInput") })
        #expect(baseline.counts["catch_all"] == 1 && baseline.counts["tuple_returns"] == 1)

        input.status = QualityStatus(text: "Every: 5\nLast review: L10 · abcdef0 · 2026-09-01\nSince review: L11, L12, L13, L14, L15")
        input.reviewFiles = ["Sources/SalesDeriver.swift", "Sources/ListingChangeDeriver.swift", "Sources/AnalyticsDeriver.swift"]
        input.reviewTypeNames = ["AnalyticsFactRow"]
        input.rungLines = 2_000
        input.priorRungLines = [300, 400, 500]
        input.newSubsystemDocs = ["Documentation/SystemDesign/Ingest.md"]
        let names = Signals.evaluate(input).triggers.map { String($0.prefix { $0 != ":" }) }
        #expect(names == ["interval", "rung-size", "shape", "mirror", "subsystem"])

        input.status!.acceptedShapes = ["Deriver"]
        #expect(!Signals.evaluate(input).triggers.contains { $0.hasPrefix("shape") })
        #expect(QualityStatus(text: "Accepted shapes: *Runner, Routes").acceptedShapes == ["Runner", "Routes"])
    }

    @Test func noBaselineFiresOnlyForASizeableCodebase() {
        var input = SignalInput()
        input.swiftFiles = [("A.swift", String(repeating: "let x = 1\n", count: 3_100))]
        #expect(Signals.evaluate(input).triggers.first?.hasPrefix("no-baseline") == true)
        input.swiftFiles = [("A.swift", "let x = 1\n")]
        #expect(Signals.evaluate(input).triggers.isEmpty)
    }
}

@Suite("Git helpers")
struct GitTests {
    @Test func baseIsTheParentOfTheCommitThatAddedTheTasklistEvenAfterAMove() throws {
        let repo = tempDir()
        func git(_ args: String...) { _ = Git.run(["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"] + args, in: repo) }
        git("init", "-q")
        try write("a\n", to: repo + "/a.txt"); git("add", "."); git("commit", "-qm", "one")
        let first = Git.run(["rev-parse", "--short", "HEAD"], in: repo)!.trimmingCharacters(in: .whitespacesAndNewlines)
        try write("- [ ] T1\n", to: repo + "/docs/Tasklist-L1-One.md"); git("add", "."); git("commit", "-qm", "two")
        try write("a\nb\nc\n", to: repo + "/a.txt"); git("commit", "-qam", "three")
        git("mv", "docs/Tasklist-L1-One.md", "docs/Completed-Tasklist-L1-One.md"); git("commit", "-qm", "four")
        #expect(Git.baseOf(tasklist: "docs/Completed-Tasklist-L1-One.md", in: repo) == first)
        #expect(Git.changedLines(since: first, in: repo) == 3)
        #expect(Git.tasklist(touchedBy: "HEAD~2", in: repo) == "Tasklist-L1-One.md")
    }
}

@Suite("Predictions")
struct PredictionsTests {
    private let log = MetricsLog.events(text: """
    {"event":"step","repo":"/r","ts":"2026-10-01T10:00:00Z","skill":"roadmap-plan-next-rung 0.7.0","model":"claude-opus-5-5","target":"L3","next":"/tasklist-run Tasklist-L3-X.md","next_model":"sonnet"}
    {"event":"start","repo":"/r","run":"R1","ts":"2026-10-01T10:05:00Z","list":"Tasklist-L3-X.md","model":"claude-opus-5-5"}
    {"event":"batch","repo":"/r","run":"R1","ts":"2026-10-01T10:10:00Z","tiers":["standard","heavy"],"rounds":2,"lines":100}
    {"event":"batch","repo":"/r","run":"R1","ts":"2026-10-01T10:12:00Z","tiers":["light"],"rounds":0,"lines":10,"raised":false}
    {"event":"end","repo":"/r","run":"R1","ts":"2026-10-01T10:20:00Z","stop":"complete","interventions":1,"next":"/roadmap-plan-next-rung fold-back L3","next_model":"opus"}
    """)

    @Test func skillNamesDropVersionsSlashesAndPlugins() {
        #expect(Predictions.skillName("roadmap-plan-next-rung 0.7.0") == "roadmap-plan-next-rung")
        #expect(Predictions.skillName("/task-workflow:tasklist-run L3") == "tasklist-run")
        #expect(Predictions.skillName(nil) == nil)
    }

    @Test func mixedBatchCountsUnderItsHighestTier() {
        let text = Predictions.render(log: log)
        #expect(text.contains("| heavy | 1 | 2.00 | 0 | 100.00 |"))
        #expect(text.contains("| light | 1 | 0.00 | 0 | 10.00 |"))
    }

    @Test func pairsARecommendationWithTheRunItLedTo() {
        let text = Predictions.render(log: log)
        #expect(text.contains("| roadmap-plan-next-rung → tasklist-run | 1 | 0 | opus ×1 |"))
        #expect(text.contains("| another model | 1 | 1.00 | 1.00 |"))
    }

    @Test func saysSoWhenNothingWasRecommended() {
        #expect(Predictions.render(log: []).contains("No `step` events with a recommendation logged yet."))
    }

    @Test func repoFilterLeavesOtherReposOut() {
        #expect(Predictions.render(log: log, repo: "/other").contains("No batches logged yet."))
    }
}

@Suite("Planning cost and orchestrator trend")
struct PlanningCostTests {
    @Test func stepTokensAreMeasuredFromBeganAndOnlyOnce() throws {
        let root = tempDir() + "/projects"
        try write([turn("2026-10-01T09:00:00.000Z", "claude-opus-5-5", out: 1, id: "before"),
                   turn("2026-10-01T10:30:00.000Z", "claude-opus-5-5", out: 40, id: "in")].joined(separator: "\n"), to: root + "/-r/s1.jsonl")
        let log = MetricsLog.events(text: #"{"event":"step","repo":"/r","ts":"2026-10-01T11:00:00Z","began":"2026-10-01T10:00:00Z","skill":"roadmap-plan-next-rung 0.7.0","target":"L3"}"#)
        let (events, _) = TranscriptTokens.newEvents(log: log, root: root)
        let e = try #require(events.first)
        #expect(e.string("event") == "step_tokens" && e.string("step_ts") == "2026-10-01T11:00:00Z")
        #expect((e["orch"] as? [String: [String: Int]])?["opus"]?["out"] == 40)
        #expect(TranscriptTokens.newEvents(log: log + events, root: root).events.isEmpty)
    }

    @Test func rungSummaryShowsPlanningShareDriftAndTrend() {
        func tokens(_ n: Int) -> String { #"{"event":"tokens","repo":"/r","run":"R","orch":{"opus":{"in":\#(n),"out":0}},"impl":{},"rev":{}}"# }
        let log = MetricsLog.events(text: ([
            #"{"event":"start","repo":"/r","run":"R","ts":"2026-10-01T10:00:00Z","list":"Tasklist-L3-X.md"}"#,
            #"{"event":"step","repo":"/r","ts":"2026-10-01T09:00:00Z","skill":"roadmap-plan-next-rung 0.7.0","target":"L3","drift":2}"#,
            #"{"event":"step_tokens","repo":"/r","step_ts":"2026-10-01T09:00:00Z","skill":"roadmap-plan-next-rung 0.7.0","orch":{"opus":{"in":100}},"impl":{},"rev":{}}"#,
            #"{"event":"end","repo":"/r","run":"R","ts":"2026-10-01T10:30:00Z","discovered":1}"#,
        ] + [100, 100, 300, 300].map(tokens)).joined(separator: "\n"))
        let all = RunSummary.byList(log: log, repo: "/r") { _ in nil }
        let n = try! #require(all["Tasklist-L3-X.md"])
        #expect(n.planTokens == 100 && n.drift == 2 && n.discovered == 1 && n.runTokens == 800)
        let text = RunSummary.render(target: n, all: all)
        #expect(text.contains("Planning was 11% of this rung's tokens"))
        #expect(text.contains("rose 200%"))
    }
}
