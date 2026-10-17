import Foundation
import Testing
@testable import PlanKit

private func fixture(_ name: String) throws -> String {
    let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent().appendingPathComponent("Fixtures/\(name)")
    return try String(contentsOf: url, encoding: .utf8)
}

private func rungList() throws -> Tasklist { Tasklist(text: try fixture("Tasklist-X9-Listing_Snapshots.md")) }

@Suite("Tasklist parsing")
struct TasklistParsingTests {
    @Test func readsTitleSourceHeadingsAndGoals() throws {
        let list = try rungList()
        #expect(list.title == "Tasklist — X9 Per-version listing snapshots")
        #expect(list.source == "Roadmap rung X9; brief SystemDesign/Rung-X9-Listing_Snapshots.md")
        #expect(list.headings.map(\.id) == ["G1", "G2", "G3", "G4"])
        #expect(list.heading("G1")?.goal == "one read-only probe answers whether snapshots are possible at all.")
        #expect(list.tasks.count == 11)
    }

    @Test func readsMarkersAndQualifiers() throws {
        let list = try rungList()
        #expect(list.task("T1")?.mark == .done)
        #expect(list.task("T2")?.user == true)
        #expect(list.task("T2")?.title == "Confirm the draft-version question with the owner")
        #expect(list.task("T5")?.reason == "SUPERSEDED")
        #expect(list.task("T5")?.supersededBy == ["T6"])
        #expect(list.task("T8")?.blocked == "waiting on the owner's date")
        #expect(list.task("T10")?.reason == "DEFERRED")
        #expect(list.task("T3")?.title == "Add the snapshot fetcher")
    }

    @Test func readsFieldsAndNeeds() throws {
        let list = try rungList()
        #expect(list.task("T3")?.needs == ["T1", "T2"])
        #expect(list.task("T4")?.fields["model"] == "light (Haiku 4.5)")
        #expect(list.task("T11")?.fields["run"] == "`swift run Portal snapshot --once`")
        #expect(list.task("T1")?.group == "G1")
    }

    @Test func blockEndsBeforeTheNextItem() throws {
        let list = try rungList()
        let block = list.block(of: list.task("T2")!)
        #expect(block.hasPrefix("- [ ] T2 USER"))
        #expect(block.contains("    b. Note whether a draft listing exists."))
        #expect(block.hasSuffix("do not paste screenshots with account data."))
    }

    @Test func parsesPhasesAndTheirGroups() {
        let list = Tasklist(text: """
        ## P1 First
        Goal: ship.
        ### G1 One
        - [ ] T1 A
          - Model: light
        ## P2 Second — DEFERRED
        ### G2 Two
        - [ ] T2 B
          - Model: light
        """)
        #expect(list.task("T1")?.phase == "P1")
        #expect(list.task("T2")?.phase == "P2")
        #expect(list.heading("G2")?.parent == "P2")
        #expect(list.heading("P2")?.reason == "DEFERRED")
        #expect(list.closedHeading(for: list.task("T2")!)?.id == "P2")
        #expect(list.closedHeading(for: list.task("T1")!) == nil)
    }

    @Test func readsLegacyListsWithoutModelNames() {
        let list = Tasklist(text: "# TODO\n\n- [ ] T1 Old item\n  - Model: standard\n- [x] T2 Done item\n")
        #expect(list.tasks.map(\.id) == ["T1", "T2"])
        #expect(list.next()?.id == "T1")
    }
}

@Suite("Choosing the next task")
struct NextTaskTests {
    @Test func skipsUserBlockedClosedHeadingAndUnmetNeeds() throws {
        let list = try rungList()
        // T2 is USER; T3 needs T2; T4 needs T3; T6 needs T3; T8 BLOCKED; T9 under a DEFERRED group;
        // T11 needs T10, a DEFERRED target, which never counts.
        #expect(list.next() == nil)
        let blockers = list.blockers().joined(separator: "\n")
        #expect(blockers.contains("T2 waits on the user"))
        #expect(blockers.contains("T3 needs T2"))
        #expect(blockers.contains("T8 BLOCKED(waiting on the owner's date)"))
        #expect(blockers.contains("T9 is under closed heading G3"))
        #expect(blockers.contains("T11 needs T4, T10"))
    }

    @Test func userConfirmationReleasesDependents() throws {
        let list = try rungList()
        let ticked = Tasklist(text: try list.ticking(["T2"], userConfirmed: true))
        #expect(ticked.next()?.id == "T3")
    }

    @Test func supersededTargetCountsOnlyWhenReplacementIsDone() {
        var text = """
        - [-] T1 SUPERSEDED→T2 — Old
          - Why: replaced (2026-10-02)
        - [ ] T2 New
          - Model: light
        - [ ] T3 Dependent
          - Model: light
          - Needs: T1
        """
        #expect(Tasklist(text: text).next()?.id == "T2")
        #expect(Tasklist(text: text).eligibility(of: Tasklist(text: text).task("T3")!) == .waiting(["T1"]))
        text = text.replacingOccurrences(of: "- [ ] T2 New", with: "- [x] T2 New")
        #expect(Tasklist(text: text).next()?.id == "T3")
    }

    @Test func deferredTargetNeverSatisfiesNeeds() {
        let list = Tasklist(text: """
        - [-] T1 DEFERRED — Later
          - Why: postponed (2026-10-02)
        - [ ] T2 Waits
          - Model: light
          - Needs: T1
        """)
        #expect(list.next() == nil)
    }

    @Test func inProgressIsNotOffered() {
        let list = Tasklist(text: "- [ ] T1 IN-PROGRESS — Claimed\n  - Model: light\n- [ ] T2 Free\n  - Model: light\n")
        #expect(list.next()?.id == "T2")
    }

    @Test func contextCarriesSourceGoalAndBlock() throws {
        let list = try rungList()
        let context = list.context(for: list.task("T3")!)
        #expect(context.hasPrefix("Source: Roadmap rung X9"))
        #expect(context.contains("Goal: each snapshot lands in Raw once and verifies."))
        #expect(context.contains("- [ ] T3 Add the snapshot fetcher"))
        #expect(!context.contains("T4 Add the snapshot route"))
    }
}

@Suite("IDs")
struct IDTests {
    @Test func nextIDCountsClosedItemsAndDocumentOrderIsIrrelevant() throws {
        let list = try rungList()
        #expect(list.nextID(prefix: "T") == "T12")
        #expect(list.nextID(prefix: "G") == "G5")
        #expect(list.nextID(prefix: "P") == "P1")
        let shuffled = Tasklist(text: "- [-] T9 OBSOLETE — x\n  - Why: gone (2026-10-02)\n- [ ] T3 y\n  - Model: light\n")
        #expect(shuffled.nextID(prefix: "T") == "T10")
    }

    @Test func deletedIDsAreReportedAgainstTheBase() throws {
        let base = try rungList()
        let trimmed = Tasklist(text: base.lines.filter { !$0.contains("T10") && !$0.contains("Hourly polling") }.joined(separator: "\n"))
        let findings = trimmed.lint(base: base)
        #expect(findings.contains { $0.severity == .error && $0.message.contains("T10 existed in the base file") })
    }

    @Test func titleRewrittenInPlaceIsFlagged() throws {
        let base = try rungList()
        let edited = Tasklist(text: try base.lines.joined(separator: "\n").replacingOccurrences(of: "Add the snapshot route", with: "Add the CSV route"))
        #expect(edited.lint(base: base).contains { $0.message.contains("T4 title changed in place") })
    }

    @Test func reopeningAClosedTaskIsFlaggedExceptDeferred() {
        let base = Tasklist(text: "- [x] T1 A\n  - Model: light\n- [-] T2 DEFERRED — B\n  - Why: later (2026-10-02)\n")
        let now = Tasklist(text: "- [ ] T1 A\n  - Model: light\n- [ ] T2 B\n  - Model: light\n")
        let warnings = now.lint(base: base).map(\.message)
        #expect(warnings.contains { $0.contains("T1 was closed in the base file") })
        #expect(!warnings.contains { $0.contains("T2 was closed") })
    }
}

@Suite("Lint")
struct LintTests {
    @Test func realisticFixturePassesWithoutErrors() throws {
        let findings = try rungList().lint()
        #expect(findings.filter { $0.severity == .error }.isEmpty)
    }

    @Test func reportsDuplicateIDsMissingNeedsAndMissingModel() {
        let list = Tasklist(text: """
        - [ ] T1 A
          - Model: light
        - [ ] T1 B
          - Model: light
          - Needs: T9
        - [ ] T2 C
        """)
        let messages = list.lint().map(\.message)
        #expect(messages.contains { $0.contains("duplicate ID T1") })
        #expect(messages.contains { $0.contains("T1 needs T9, which does not exist") })
        #expect(messages.contains { $0.contains("T2 has no Model") })
    }

    @Test func closedItemsNeedAReasonWordAndWhy() {
        let list = Tasklist(text: "- [-] T1 Plain title\n- [-] T2 OBSOLETE — x\n  - Why: gone\n")
        let messages = list.lint().map(\.message)
        #expect(messages.contains("T1 is [-] without a reason word"))
        #expect(messages.contains("T1 is [-] without Why:"))
        #expect(messages.contains("T2 Why: has no ISO date"))
    }

    @Test func blockedByReasonNeedsWhyButBlockedByTaskDoesNot() {
        let list = Tasklist(text: """
        - [ ] T1 BLOCKED(T2) — A
          - Model: light
        - [ ] T2 BLOCKED(no key yet) — B
          - Model: light
        """)
        let messages = list.lint().map(\.message)
        #expect(!messages.contains { $0.contains("T1 BLOCKED") })
        #expect(messages.contains("T2 BLOCKED(reason) without Why:"))
    }

    @Test func detectsCyclesAndNamesThePath() {
        let list = Tasklist(text: """
        - [ ] T1 A
          - Model: light
          - Needs: T3
        - [ ] T2 B
          - Model: light
          - Needs: T1
        - [ ] T3 C
          - Model: light
          - Needs: T2
        """)
        let cycle = list.lint().first { $0.message.hasPrefix("dependency cycle") }
        #expect(cycle?.message == "dependency cycle: T1 → T3 → T2 → T1")
    }

    @Test func userTasksNeedStepsButNoModel() {
        let ok = Tasklist(text: "- [ ] T1 USER — Do it\n  - Steps:\n    a. First.\n  - Done when: reply\n")
        #expect(ok.lint().isEmpty)
        let bare = Tasklist(text: "- [ ] T1 USER — Do it\n  - Done when: reply\n")
        #expect(bare.lint().contains { $0.message.contains("no lettered steps") })
    }

    @Test func warnsWhenADependencyIsObsolete() {
        let list = Tasklist(text: """
        - [-] T1 OBSOLETE — Gone
          - Why: not needed (2026-10-02)
        - [ ] T2 Dependent
          - Model: light
          - Needs: T1
        """)
        #expect(list.lint().contains { $0.severity == .warning && $0.message.contains("T2 needs T1, which is OBSOLETE") })
    }
}

@Suite("Editing")
struct EditingTests {
    @Test func tickingChangesOnlyTheCheckbox() throws {
        let list = try rungList()
        let text = try list.ticking(["T4"], userConfirmed: false)
        let before = list.lines, after = text.components(separatedBy: "\n")
        #expect(before.count == after.count)
        let changed = zip(before, after).enumerated().filter { $0.element.0 != $0.element.1 }
        #expect(changed.count == 1)
        #expect(after[changed[0].offset] == "- [x] T4 Add the snapshot route")
    }

    @Test func refusesUserTasksUnlessConfirmedAndClosedOrUnknownTasks() throws {
        let list = try rungList()
        #expect(throws: Tasklist.EditError.self) { try list.ticking(["T2"]) }
        #expect(throws: Tasklist.EditError.self) { try list.ticking(["T1"]) }
        #expect(throws: Tasklist.EditError.self) { try list.ticking(["T99"]) }
        #expect(throws: Never.self) { try list.ticking(["T2"], userConfirmed: true) }
    }

    @Test func counts() throws {
        let c = try rungList().counts()
        #expect(c == Tasklist.Counts(open: 8, done: 1, closed: 2, blocked: 1, user: 1, eligible: 0))
    }
}
