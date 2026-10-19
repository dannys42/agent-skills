import Foundation
import Testing
@testable import PlanKit

private let ladder = "## Ladder\n\n1. L1 — a [done]\n2. L3 — b [in progress]\n3. L4 — c [planned]\n"

private func list(_ name: String, _ tasks: String, completed: Bool = false, age: Double = 0) -> NextStep.File {
    NextStep.File(name: name, text: "# Tasklist\n\n## G1 Gate\n\n" + tasks, completed: completed, modified: Date(timeIntervalSince1970: age))
}

private func brief(_ id: String, status: String) -> NextStep.File {
    NextStep.File(name: "Rung-\(id)-Grid.md", text: "# Rung \(id)\n\nStatus: \(status)\n")
}

private func decide(_ roadmapText: String? = ladder, overview: Bool = true, lists: [NextStep.File] = [], briefs: [NextStep.File] = [], dir: String = "docs") -> NextStep {
    NextStep.decide(.init(docDir: dir, hasOverview: overview, roadmap: roadmapText.map { Roadmap(text: $0) }, tasklists: lists, briefs: briefs))
}

private let openStd = "- [ ] T1 Do it\n  - Model: standard (Sonnet 5.5)\n"
private let openHeavy = "- [ ] T2 Hard\n  - Model: heavy (Opus 5.5)\n"
private let done = "- [x] T1 Did it\n  - Model: standard (Sonnet 5.5)\n"

@Suite("NextStep")
struct NextStepTests {
    @Test func noDesignNoRoadmapIsDesign() {
        let s = decide(nil, overview: false)
        #expect(s.step == "design" && s.model == "opus" && s.command == "/rung design")
        #expect(s.rendered == "step: design\nmodel: opus\ncommand: /rung design\nwhy: no system design and no roadmap")
    }

    @Test func overviewWithoutRoadmapIsRoadmap() {
        let s = decide(nil)
        #expect(s.step == "roadmap" && s.command == "/rung roadmap" && s.model == "opus")
    }

    @Test func firstPlannedRungWhenNoneInProgress() {
        let s = decide("## Ladder\n\n1. L1 — a [done]\n2. L2 — b [planned]\n3. L3 — c [planned]\n")
        #expect(s.step == "plan" && s.rung == "L2" && s.command == "/rung plan L2" && s.model == "opus")
    }

    @Test func nothingLeftIsFinished() {
        let s = decide("## Ladder\n\n1. L1 — a [done]\n2. L2 — b [deferred]\n")
        #expect(s.step == "finished" && s.command == "/risk-first-roadmap" && s.rung == nil)
        #expect(s.why == "no planned rung left; extend the ladder or stop")
    }

    @Test func openTasksRunOnSonnetFromTheOpenList() {
        let s = decide(lists: [list("Tasklist-L3-Grid_Text.md", openStd)])
        #expect(s.step == "run" && s.rung == "L3" && s.model == "sonnet" && s.command == "/rung run L3")
        #expect(s.list == "docs/Tasklist-L3-Grid_Text.md")
    }

    @Test func aFewHeavyTasksStillRunOnSonnet() {
        let s = decide(lists: [list("Tasklist-L3-Grid.md", openStd + openStd + openHeavy)])
        #expect(s.step == "run" && s.model == "sonnet")
    }

    @Test func mostlyHeavyTasksMeanOpus() {
        let s = decide(lists: [list("Tasklist-L3-Grid.md", openStd + openHeavy + openHeavy)])
        #expect(s.step == "run" && s.model == "opus")
    }

    @Test func newestOpenListWins() {
        let s = decide(lists: [list("Tasklist-L3-Old.md", openStd, age: 1), list("Tasklist-L3-Tidy.md", openStd, age: 9)])
        #expect(s.list == "docs/Tasklist-L3-Tidy.md")
    }

    @Test func userOnlyAndBlockedIsUserStep() {
        let tasks = "- [ ] T5 USER — Confirm\n- [ ] T9 USER — Sign\n- [ ] T7 BLOCKED(T5) — Wait\n  - Model: standard (Sonnet 5.5)\n"
        let s = decide(lists: [list("Tasklist-L3-Grid.md", tasks)])
        #expect(s.step == "user" && s.command == "/rung run L3" && s.list == "docs/Tasklist-L3-Grid.md")
        #expect(s.why == "USER tasks waiting: T5, T9; blocked: T7")
    }

    @Test func userTaskBesideRunnableTaskStillRuns() {
        let s = decide(lists: [list("Tasklist-L3-Grid.md", "- [ ] T5 USER — Confirm\n" + openStd)])
        #expect(s.step == "run")
    }

    @Test func rungIDMatchIsExact() {
        let s = decide(lists: [list("Tasklist-L31-Other.md", openStd)], briefs: [brief("L31", status: "agreed (2026-10-01)")])
        #expect(s.step == "plan" && s.why.contains("brief missing"))
    }

    @Test func noTasklistPlansAndSaysWhy() {
        #expect(decide().why.contains("brief missing"))
        #expect(decide(briefs: [brief("L3", status: "draft")]).why.contains("draft"))
        let s = decide(briefs: [brief("L3", status: "agreed (2026-10-01)")])
        #expect(s.step == "plan" && s.command == "/rung plan L3" && s.model == "opus" && s.why.contains("agreed"))
    }

    @Test func closedListWithoutFoldBackIsClose() {
        let s = decide(lists: [list("Tasklist-L3-Grid_Text.md", done)], briefs: [brief("L3", status: "agreed (2026-10-01)")])
        #expect(s.step == "close" && s.command == "/rung close L3" && s.model == "opus" && s.list == "docs/Tasklist-L3-Grid_Text.md")
        #expect(s.why == "Tasklist-L3-Grid_Text.md closed; brief not folded back")
        #expect(decide(lists: [list("Tasklist-L3-Grid.md", done)]).step == "close")
    }

    @Test func completedListsCountAsClosedAndTidyCounts() {
        let s = decide(lists: [list("Tasklist-L3-Grid.md", openStd, completed: true), list("Tasklist-L3-Tidy.md", done)],
                       briefs: [brief("L3", status: "agreed (2026-10-01)")])
        #expect(s.step == "close")
        #expect(decide(lists: [list("Tasklist-L3-Grid.md", done, completed: true)]).step == "close")
        #expect(decide(lists: [list("Tasklist-L3-Tidy.md", openStd)]).step == "run")
    }

    @Test func foldedBackIsReplan() {
        let s = decide(lists: [list("Tasklist-L3-Grid.md", done, completed: true)], briefs: [brief("L3", status: "folded back (2026-10-02)")])
        #expect(s.step == "replan" && s.command == "/rung replan" && s.model == "opus")
        #expect(s.why == "L3 folded back; roadmap still in progress")
    }

    @Test func rootDocDirOmitsThePrefix() {
        #expect(decide(lists: [list("Tasklist-L3-Grid.md", openStd)], dir: ".").list == "Tasklist-L3-Grid.md")
    }
}
