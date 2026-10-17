import Foundation
import Testing
@testable import PlanKit

private func roadmap() throws -> Roadmap {
    let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent().appendingPathComponent("Fixtures/Roadmap-Synthetic.md")
    return Roadmap(text: try String(contentsOf: url, encoding: .utf8))
}

@Suite("Roadmap")
struct RoadmapTests {
    @Test func readsLadderStatusesAndDetails() throws {
        let r = try roadmap()
        #expect(r.ladder.map(\.id) == ["L1", "L1b", "L2", "L3", "L3b", "L4"])
        #expect(r.ladder.map(\.status) == ["done", "done", "done", "in progress", "planned", "horizon"])
        #expect(r.details.map(\.id) == ["L1", "L2", "L3", "L3b"])
        #expect(r.log.map(\.rung) == ["L1", "L2", "L3", "L9"])
    }

    @Test func nextRungPrefersInProgressThenPlanned() throws {
        #expect(try roadmap().nextRung()?.id == "L3")
        let r = Roadmap(text: "## Ladder\n\n1. L1 — a [done]\n2. L2 — b [planned]\n3. L3 — c [planned]\n")
        #expect(r.nextRung()?.id == "L2")
    }

    @Test func showReturnsOnlyThatRungsPieces() throws {
        let out = try #require(try roadmap().show("L3"))
        #expect(out.contains("Prove the pipeline."))
        #expect(out.contains("three values exist"))
        #expect(!out.contains("Prove the key."))
        #expect(!out.contains("Client chart"))
        #expect(try #require(try roadmap().show("L3", includeLog: false)).contains("three values") == false)
    }

    @Test func showDoesNotConfuseL3WithL3b() throws {
        #expect(try #require(try roadmap().show("L3b")).contains("Show it."))
        #expect(try #require(try roadmap().show("L3b")).contains("Prove the pipeline.") == false)
    }

    @Test func statusCollapsesFinishedRungs() throws {
        let out = try roadmap().status()
        #expect(out.hasPrefix("next: L3 (in progress)\ndone (3): L1 L1b L2\n"))
        #expect(out.contains("L4 [horizon]"))
    }

    @Test func lintFlagsStructureProblems() throws {
        let messages = try roadmap().lint().map(\.message)
        #expect(messages.contains { $0.contains("learning-log entry names L9") })
        #expect(messages.contains { $0.contains("L1b") } == false)  // finished rungs may have no detail section
        #expect(!messages.contains { $0.contains("duplicate") })
    }

    @Test func lintFlagsDuplicatesMissingDetailAndBudgets() {
        let r = Roadmap(text: """
        ## Ladder

        1. L1 — a [in progress]
        2. L1 — b [planned]
        3. L2 — c [planned]

        ## Rungs (detailed)

        ### L7: Orphan
        text
        """)
        let messages = r.lint(budget: .init(maxBytes: 50, maxLine: 20)).map(\.message)
        #expect(messages.contains { $0.contains("duplicate ladder ID L1") })
        #expect(messages.contains { $0.contains("L1 is in progress but has no detail section") })
        #expect(messages.contains { $0.contains("L2 is planned but has no detail section") })
        #expect(messages.contains { $0.contains("rung section L7 has no ladder entry") })
        #expect(messages.contains { $0.contains("over the 50 budget") })
    }

    @Test func logEntriesNotTaggedWithARungIDAreNotRungEntries() {
        let r = Roadmap(text: "## Learning log\n\n- 2026-10-17 re-plan after L3: moved things.\n- 2026-10-18 L4 (done): ok.\n")
        #expect(r.log.map(\.rung) == ["L4"])
    }

    @Test func headingsInsideCodeFencesAreIgnored() {
        let md = Markdown(text: "# A\n```\n## not a heading\n```\n## B\ntext\n")
        #expect(md.sections.map(\.title) == ["A", "B"])
        #expect(md.section(matching: "B")?.line == 5)
    }

    @Test func outlineReportsOwnAndSubtreeBytes() {
        let md = Markdown(text: "# A\nxx\n## B\nyyyy\n## C\nz\n")
        let rows = md.outline().components(separatedBy: "\n").map { $0.components(separatedBy: "\t") }
        #expect(rows[0] == ["1", "7", "25", "# A"])   // own: "# A\nxx\n"; subtree adds B, C and the final empty line
        #expect(rows[1][3] == "## B")
    }
}

@Suite("Roadmap, format as documented in the skill")
struct DocumentedRoadmapTests {
    private func documented() throws -> Roadmap {
        let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent().appendingPathComponent("Fixtures/Roadmap-Documented.md")
        return Roadmap(text: try String(contentsOf: url, encoding: .utf8))
    }

    @Test func statusComesFromTheDetailSectionAndHorizonItemsJoinTheLadder() throws {
        let r = try documented()
        #expect(r.ladder.map(\.id) == ["L1", "L2", "L3", "L4"])
        #expect(r.ladder.map(\.status) == ["done", "in progress", "horizon", "horizon"])
        #expect(r.nextRung()?.id == "L2")
    }

    @Test func logEntriesWithTheRungFirstAreRecognised() throws {
        let r = try documented()
        #expect(r.log.map(\.rung) == ["L1"])
        #expect(r.log.first?.date == "2026-09-01")
        #expect(try #require(r.show("L1")).contains("signing change"))
    }

    @Test func lintIsCleanOnTheDocumentedFormat() throws {
        #expect(try documented().lint().isEmpty)
    }

    @Test func otherLifecycleStatusesAreRecognised() {
        let r = Roadmap(text: "## Ladder\n\n1. L1 — a [failed: fallback taken]\n2. L2 — b [obsolete]\n3. L3 — c [changed]\n")
        #expect(r.lint().isEmpty)
    }
}
