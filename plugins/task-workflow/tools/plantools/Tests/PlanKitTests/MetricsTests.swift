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

    @Test func takesLinesFromTheCommitAndReviewerTokensFromTokensEventsWhenTheBatchLogIsOff() {
        let log = MetricsLog.events(text: """
        {"run":"A","ts":"2026-10-01T10:00:00Z","event":"start","repo":"/p","list":"Tasklist-L1-One.md"}
        {"run":"A","ts":"2026-10-01T11:00:00Z","event":"batch","repo":"/p","tasks":["T1"],"rev":"sonnet","outcome":"committed","lines":2,"sha":"abc","agents":[{"role":"impl","tokens":40000,"tools":10},{"role":"rev","tokens":0,"tools":5}]}
        {"run":"A","ts":"2026-10-01T11:30:00Z","event":"batch","repo":"/p","tasks":["T2"],"rev":"sonnet","outcome":"committed","lines":9,"agents":[{"role":"impl","tokens":10000,"tools":4},{"role":"rev","tokens":20000,"tools":3}]}
        {"run":"A","ts":"2026-10-01T11:01:00Z","event":"tokens","repo":"/p","batch_ts":"2026-10-01T11:00:00Z","orch":{},"impl":{},"rev":{"m":{"cr":900000,"cw":100000,"in":10,"out":2000}}}
        {"run":"A","ts":"2026-10-01T11:31:00Z","event":"tokens","repo":"/p","batch_ts":"2026-10-01T11:30:00Z","orch":{},"impl":{},"rev":{"m":{"cr":500000,"cw":30000,"in":5,"out":50}}}
        """)
        let all = RunSummary.byList(log: log, repo: "/p", linesForSha: { $0 == "abc" ? 562 : nil }) { _ in nil }
        let n = all["Tasklist-L1-One.md"]!
        #expect(n.lines == 571 && n.lineMismatches == 1 && n.silentReviews == 0 && n.revTokens == 102_010 + 20_000)
        let out = RunSummary.render(target: n, all: all)
        #expect(out.contains("| Lines changed | 571 |") && !out.contains("no reviewer tokens"))
    }

    @Test func aBatchWithNoReviewerIsNotAReviewedBatchWithoutTokens() {
        let log = MetricsLog.events(text: """
        {"run":"A","ts":"2026-10-01T10:00:00Z","event":"start","repo":"/p","list":"Tasklist-L1-One.md"}
        {"run":"A","ts":"2026-10-01T11:00:00Z","event":"batch","repo":"/p","tasks":["T1"],"rev":"none","rev_reason":"orchestrator read doc-only diff","outcome":"committed","agents":[{"role":"impl","tokens":40000,"tools":10}]}
        {"run":"A","ts":"2026-10-01T12:00:00Z","event":"batch","repo":"/p","tasks":["T2"],"rev":"sonnet","outcome":"committed","agents":[{"role":"impl","tokens":10000,"tools":4}]}
        """)
        let n = RunSummary.byList(log: log, repo: "/p") { _ in nil }["Tasklist-L1-One.md"]!
        #expect(n.silentReviews == 1)
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
    {"event":"step","repo":"/r","ts":"2026-10-01T10:00:00Z","skill":"plan-milestone 0.7.0","model":"claude-opus-5-5","target":"L3","next":"/tasklist-run Tasklist-L3-X.md","next_model":"sonnet"}
    {"event":"start","repo":"/r","run":"R1","ts":"2026-10-01T10:05:00Z","list":"Tasklist-L3-X.md","model":"claude-opus-5-5"}
    {"event":"batch","repo":"/r","run":"R1","ts":"2026-10-01T10:10:00Z","tiers":["standard","heavy"],"rounds":2,"lines":100}
    {"event":"batch","repo":"/r","run":"R1","ts":"2026-10-01T10:12:00Z","tiers":["light"],"rounds":0,"lines":10,"raised":false}
    {"event":"end","repo":"/r","run":"R1","ts":"2026-10-01T10:20:00Z","stop":"complete","interventions":1,"next":"/plan-milestone fold-back L3","next_model":"opus"}
    """)

    @Test func skillNamesDropVersionsSlashesAndPlugins() {
        #expect(Predictions.skillName("plan-milestone 0.7.0") == "plan-milestone")
        #expect(Predictions.skillName("/task-workflow:tasklist-run L3") == "tasklist-run")
        #expect(Predictions.skillName(nil) == nil)
    }

    @Test func aLegacySkillStampKeepsItsAttribution() {
        #expect(Predictions.skillName("roadmap-plan-next-rung 0.7.0") == "plan-milestone")
        #expect(SkillStamp.isValid("roadmap-plan-next-rung 0.7.0"))
    }

    @Test func mixedBatchCountsUnderItsHighestTier() {
        let text = Predictions.render(log: log)
        #expect(text.contains("| heavy | 1 | 2.00 | 0 | 100.00 |"))
        #expect(text.contains("| light | 1 | 0.00 | 0 | 10.00 |"))
    }

    @Test func pairsARecommendationWithTheRunItLedTo() {
        let text = Predictions.render(log: log)
        #expect(text.contains("| plan-milestone → tasklist-run | 1 | 0 | opus ×1 |"))
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
        let log = MetricsLog.events(text: #"{"event":"step","repo":"/r","ts":"2026-10-01T11:00:00Z","began":"2026-10-01T10:00:00Z","skill":"plan-milestone 0.7.0","target":"L3"}"#)
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
            #"{"event":"step","repo":"/r","ts":"2026-10-01T09:00:00Z","skill":"plan-milestone 0.7.0","target":"L3","drift":2}"#,
            #"{"event":"step_tokens","repo":"/r","step_ts":"2026-10-01T09:00:00Z","skill":"plan-milestone 0.7.0","orch":{"opus":{"in":100}},"impl":{},"rev":{}}"#,
            #"{"event":"end","repo":"/r","run":"R","ts":"2026-10-01T10:30:00Z","discovered":1}"#,
        ] + [100, 100, 300, 300].map(tokens)).joined(separator: "\n"))
        let all = RunSummary.byList(log: log, repo: "/r") { _ in nil }
        let n = try! #require(all["Tasklist-L3-X.md"])
        #expect(n.planTokens == 100 && n.drift == 2 && n.discovered == 1 && n.runTokens == 800)
        let text = RunSummary.render(target: n, all: all)
        #expect(text.contains("Planning was 11% of this rung's tokens"))
        #expect(text.contains("rose 200%"))
    }

    @Test func rungSummaryCountsPlanningUnderALegacySkillStamp() {
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

@Suite("Session metrics")
struct SessionMetricsTests {
    @Test func stepTokensCarryTheRunAndModelOfTheirStep() throws {
        let root = tempDir() + "/projects"
        try write(turn("2026-10-01T10:30:00.000Z", "claude-opus-5-5", out: 40, id: "in"), to: root + "/-r/s1.jsonl")
        let log = MetricsLog.events(text: #"{"event":"step","run":"R9","model":"claude-opus-5-5","repo":"/r","ts":"2026-10-01T11:00:00Z","began":"2026-10-01T10:00:00Z","skill":"system-design 0.17.2","target":"design"}"#)
        let e = try #require(TranscriptTokens.newEvents(log: log, root: root).events.first)
        #expect(e.string("run") == "R9" && e.string("model") == "claude-opus-5-5" && e.string("skill") == "system-design 0.17.2")
    }

    @Test func skillStampIsNameThenVersion() {
        for good in ["tasklist-run 0.17.2", "plan-milestone 0.17.2", "rung 1.0.0"] { #expect(SkillStamp.isValid(good), "\(good)") }
        for bad in ["0.16.2", "plan-milestone 0018", "tasklist-run", "tasklist-run 0.17", "task-workflow:tasklist 0.17.2", ""] { #expect(!SkillStamp.isValid(bad), "\(bad)") }
        #expect(!SkillStamp.isValid(nil))
    }

    @Test func warnsOncePerMalformedStampAndIgnoresOtherEvents() {
        let log = MetricsLog.events(text: """
        {"event":"step","skill":"0.16.2"}
        {"event":"step","skill":"0.16.2"}
        {"event":"step","skill":"plan-milestone 0018"}
        {"event":"step","skill":"tasklist-run 0.17.2"}
        {"event":"batch","skill":"bogus"}
        {"event":"step"}
        """)
        let warnings = SkillStamp.warnings(log: log)
        #expect(warnings.count == 3)
        #expect(warnings[0].contains("\"0.16.2\" on 2") && warnings[1].contains("0018") && warnings[2].contains("(none)"))
    }

    @Test func countsEscapedFromFieldsPerRungAndShowsThemInTheSummary() {
        let text = """
        - [ ] T1 Fix crash
          - Escaped from: L3
        - [ ] T2 Fix hang
          - Escaped from: `L3`.
        - [ ] T3 Fix typo
          - Escaped from: L12
        - [ ] T4 Mentions Escaped from: L3 mid-line
        """
        let counts = Escapes.byRung(texts: [text])
        #expect(counts == ["L3": 2, "L12": 1])
        let log = MetricsLog.events(text: #"{"run":"A","ts":"2026-10-01T10:00:00Z","event":"start","repo":"/p","list":"Tasklist-L3-X.md"}"#)
        let all = RunSummary.byList(log: log, repo: "/p") { _ in nil }
        let out = RunSummary.render(target: all["Tasklist-L3-X.md"]!, all: all, escapes: counts)
        #expect(out.contains("Escaped defects from L3: 2. Escaped defects by rung: L3 2, L12 1."))
        #expect(!RunSummary.render(target: all["Tasklist-L3-X.md"]!, all: all).contains("Escaped"))
    }
}

private let milestoneRoadmap = """
# Roadmap: Demo

## Milestones
- M1 (print a puzzle) — I can print. `owner`; touches: Grid_View [done]
- M2 (any size) — I can pick a size. `proposed` [current]

## Ladder (one line per rung, in order)
1. L2 — Draw a grid? [done]
2. L3 — Control text? [done]
3. L4 — Pick a size? [planned]

## Rungs (detailed)

### L2: Draw a grid
Milestone: M1

### L3: Control text
Milestone: M1

### L4: Pick a size
Milestone: M2
"""

@Suite("Milestone metrics")
struct MilestoneMetricsTests {
    @Test func totalsEscapedDefectsPerMilestoneThroughTheRoadmap() {
        let text = "- [ ] T1 Fix\n  - Escaped from: L2\n- [ ] T2 Fix\n  - Escaped from: `L3`.\n- [ ] T3 Fix\n  - **Escaped from:** L4\n- [ ] T4 Fix\n  - Escaped from: L9\n"
        let byRung = Escapes.byRung(texts: [text])
        #expect(byRung == ["L2": 1, "L3": 1, "L4": 1, "L9": 1])
        let byMilestone = Escapes.byMilestone(byRung, roadmap: Roadmap(text: milestoneRoadmap))
        #expect(byMilestone == ["M1": 2, "M2": 1, "(no milestone)": 1])
        #expect(Escapes.renderMilestones(byMilestone) == "Escaped defects by milestone: (no milestone) 1, M1 2, M2 1.")
        let log = MetricsLog.events(text: #"{"run":"A","ts":"2026-10-01T10:00:00Z","event":"start","repo":"/p","list":"Tasklist-L2-X.md"}"#)
        let all = RunSummary.byList(log: log, repo: "/p") { _ in nil }
        let out = RunSummary.render(target: all["Tasklist-L2-X.md"]!, all: all, escapes: byRung, escapesByMilestone: byMilestone)
        #expect(out.contains("Escaped defects by milestone: "))
        #expect(!RunSummary.render(target: all["Tasklist-L2-X.md"]!, all: all).contains("by milestone"))
    }

    @Test func countsProvisionalMarkersAndFlagsOnesWhoseMilestoneIsDone() {
        var input = SignalInput()
        input.milestoneStatus = Dictionary(Roadmap(text: milestoneRoadmap).milestones.map { ($0.id, $0.status) }) { a, _ in a }
        let tag = "PROVISIONAL" + "("   // split so this file never matches the marker scan
        input.provisionalLines = [
            ("Sources/Grid.swift", "    // " + tag + "L2): replace at M1 (print a puzzle)"),
            ("Sources/Size.swift", "    // " + tag + "L4): replace at M2 (any size)"),
            ("Sources/Odd.swift", "    // " + tag + "L5): no milestone named"),
            ("Sources/Doc.swift", "    /// " + tag + "<RungId>): replace at <MilestoneId>"),
            ("Sources/Gone.swift", "    // " + tag + "L6): replace at M99 (renamed away)"),
        ]
        let signals = Signals.evaluate(input)
        #expect(signals.counts["provisional"] == 3 && signals.counts["provisional_overdue"] == 1)
        #expect(signals.triggers == ["provisional: PROVISIONAL(L2) in Grid.swift says replace at M1, which is done"])
        #expect(signals.info.contains("Provisional markers: 3, 1 past their milestone, unknown milestone M99"))
        #expect(Signals.evaluate(SignalInput()).counts["provisional"] == 0)
        input.roadmapCount = 2
        #expect(Signals.evaluate(input).info.contains("Provisional overdue check skipped: 2 roadmaps found"))
    }

    @Test func flagsAHandoffOlderThanTwoWeeksOrWithoutARouteAsLeftOver() {
        var input = SignalInput()
        input.today = ISO8601DateFormatter().date(from: "2026-11-20T12:00:00Z")!
        input.handoffs = [
            ("docs/Handoff/Tasklist-L2-Grid.md", "Route: run\nDate: 2026-11-18\n\nT4 waits on the owner."),
            ("docs/Handoff/escalation-L3.md", "# Handoff\n\nRoute: escalation\nDate: 2026-11-01\n"),
            ("docs/Handoff/notes.md", "Some prose without a header."),
        ]
        let signals = Signals.evaluate(input)
        #expect(signals.counts["handoffs"] == 3 && signals.counts["handoffs_left_over"] == 2)
        #expect(signals.triggers.isEmpty)
        #expect(signals.info.contains("Warning: left-over handoff docs/Handoff/escalation-L3.md (19 days old); resume it with /rung or delete it"))
        #expect(signals.info.contains("Warning: left-over handoff docs/Handoff/notes.md (no Route: line naming a known route); resume it with /rung or delete it"))
    }

    @Test func gatherReadsHandoffNotesOnceFromTheDocDirRoadmapNextUses() throws {
        let root = FileManager.default.temporaryDirectory.appendingPathComponent("handoff-\(UUID().uuidString)").path
        defer { try? FileManager.default.removeItem(atPath: root) }
        try FileManager.default.createDirectory(atPath: root + "/docs/Handoff", withIntermediateDirectories: true)
        try "# Roadmap\n".write(toFile: root + "/docs/Roadmap-X.md", atomically: true, encoding: .utf8)
        try "Route: run\nDate: 2026-01-01\n".write(toFile: root + "/docs/Handoff/Tasklist-L1-A.md", atomically: true, encoding: .utf8)
        try "*\n".write(toFile: root + "/docs/Handoff/.gitignore", atomically: true, encoding: .utf8)
        #expect(DocDir.find(in: root) == "docs")
        let input = SignalInput.gather(repo: root, base: nil, statusPath: nil, log: [], currentList: nil)
        #expect(input.handoffs.map(\.path) == ["docs/Handoff/Tasklist-L1-A.md"])
        #expect(Signals.evaluate(input).counts["handoffs_left_over"] == 1)
    }

    @Test func stepEventsWithKindRulingAndEscalatedAreAcceptedWithoutWarnings() {
        let log = MetricsLog.events(text: """
        {"event":"step","repo":"/r","ts":"2026-10-01T10:00:00Z","skill":"plan-milestone 0.11.2","kind":"fold-back","target":"L3","drift":0,"escalated":true,"next":"/rung","next_model":"opus"}
        {"event":"step","repo":"/r","ts":"2026-10-01T11:00:00Z","skill":"plan-milestone 0.11.2","kind":"milestone-close","target":"M1","ruling":"accept with follow-ups","next":"/rung","next_model":"opus"}
        {"event":"step","repo":"/r","ts":"2026-10-01T12:00:00Z","skill":"plan-milestone 0.11.2","kind":"milestone-plan","target":"M2","next":"/rung","next_model":"sonnet"}
        """)
        #expect(log.count == 3)
        #expect(SkillStamp.warnings(log: log).isEmpty)
        #expect(log[1].string("ruling") == "accept with follow-ups" && log[0].bool("escalated"))
        #expect(Predictions.render(log: log, repo: "/r").contains("step"))
    }
}

@Suite("Rung commands")
struct RungCommandTests {
    @Test func rungStepsMapToTheSkillTheyRun() {
        #expect(Predictions.skillName("/rung plan L3") == "plan-milestone")
        #expect(Predictions.skillName("/project-planning:rung close L3") == "plan-milestone")
        #expect(Predictions.skillName("/rung retro L3") == "plan-milestone")
        #expect(Predictions.skillName("/rung run L3") == "tasklist-run")
        #expect(Predictions.skillName("/rung replan") == "risk-first-roadmap")
        #expect(Predictions.skillName("/rung roadmap") == "risk-first-roadmap")
        #expect(Predictions.skillName("/rung design") == "system-design")
        #expect(Predictions.skillName("/rung") == nil)
        #expect(Predictions.skillName("/rung bogus") == nil)
        #expect(Predictions.skillName("/rung → close L3") == "plan-milestone")
        #expect(Predictions.skillName("/rung -> run L3") == "tasklist-run")
        #expect(Predictions.skillName("/rung → checkpoint L44") == "system-design")
    }
}

@Suite("State directory")
struct StateDirectoryTests {
    @Test(arguments: [
        ([String: String](), "/h/.local/state/danny-agent-skills"),
        (["DANNY_SKILLS_STATE_DIR": ""], "/h/.local/state/danny-agent-skills"),
        (["DANNY_SKILLS_STATE_DIR": "~/x"], "/h/x"),
    ])
    func resolvesTheStateDirectory(environment: [String: String], expected: String) {
        #expect(MetricsLog.stateDirectory(environment: environment, home: "/h") == expected)
    }
}
