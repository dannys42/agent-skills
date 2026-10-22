import Foundation
import Testing
@testable import PlanKit

private let sample = """
# Tasklist — Editing

Source: a request

## G1 First
Goal: the first thing works.

- [x] T1 Set up the project
  - Model: light (Haiku 4.5)
  - Done when: it builds

- [ ] T2 Add the parser
  - Model: standard (Sonnet 5.5)
  - Context: Reads the input format.
    Second line of the context, with `code` and a colon: kept as is.
    Third line.
  - Verify: `swift test --filter Parser`
  - Done when: the parser test passes
  - Notes: Watch the empty input.

- [ ] T3 Add the renderer
  - Model: standard (Sonnet 5.5)
  - Needs: T2
  - Done when: the renderer test passes

## G2 Second

- [ ] T4 Wire it together
  - Model: heavy (Opus 5.5)
  - Needs: T3

- [-] T5 DEFERRED — Export to CSV
  - Why: not for the first release (2026-10-03)
  - Done when: not applicable

- [ ] T6 USER — Confirm the format with the owner
  - Steps:
    a. Ask them.
  - Done when: reply yes or no

- [ ] T7 BLOCKED(no key yet) — Call the service
  - Model: standard (Sonnet 5.5)
  - Why: waiting for the key (2026-10-04)
  - Done when: the call succeeds

"""

private func list(_ text: String = sample) -> Tasklist { Tasklist(text: text) }

/// Lines that differ between two texts, as (old, new) pairs by position; both must have the same line count.
private func changes(_ old: String, _ new: String) -> [(String, String)] {
    let a = old.components(separatedBy: "\n"), b = new.components(separatedBy: "\n")
    #expect(a.count == b.count)
    return zip(a, b).filter { $0 != $1 }.map { ($0, $1) }
}

private func refusal(_ body: () throws -> Edit) -> String? {
    do { _ = try body(); return nil } catch { return "\(error)" }
}

private func usage(_ body: () throws -> Edit) -> String? {
    do { _ = try body() } catch let error as EditUsageError { return error.description } catch { return nil }
    return nil
}

@Suite("needs")
struct NeedsEditTests {
    @Test func addsAnEdgeInTheStandardPositionAndNothingElseMoves() throws {
        let edit = try list().editingNeeds("T2", add: ["T1"], remove: [])
        let lines = edit.text.components(separatedBy: "\n")
        let at = lines.firstIndex(of: "- [ ] T2 Add the parser")!
        #expect(lines[at + 1] == "  - Model: standard (Sonnet 5.5)")
        #expect(lines[at + 2] == "  - Needs: T1")
        #expect(lines[at + 3] == "  - Context: Reads the input format.")
        #expect(lines.count == sample.components(separatedBy: "\n").count + 1)
        #expect(edit.text.replacingOccurrences(of: "  - Needs: T1\n", with: "") == sample)
    }

    @Test func addingAnExistingEdgeOrRemovingAMissingOneChangesNothing() throws {
        let again = try list().editingNeeds("T3", add: ["T2"], remove: [])
        #expect(!again.changed)
        #expect(again.text == sample)
        let missing = try list().editingNeeds("T3", add: [], remove: ["T1"])
        #expect(!missing.changed)
        #expect(missing.text == sample)
    }

    @Test func addAndRemoveInOneCallAndEmptyListDropsTheLine() throws {
        let edit = try list().editingNeeds("T3", add: ["T1"], remove: ["T2"])
        #expect(changes(sample, edit.text).first?.1 == "  - Needs: T1")
        let cleared = try list().editingNeeds("T3", add: [], remove: ["T2"])
        #expect(!cleared.text.contains("  - Needs: T2\n  - Done when: the renderer"))
        #expect(cleared.text.components(separatedBy: "\n").count == sample.components(separatedBy: "\n").count - 1)
    }

    @Test func keepsAnnotationsOnEdgesItDoesNotTouch() throws {
        let text = sample.replacingOccurrences(of: "  - Needs: T2", with: "  - Needs: T2 (parser first), T1")
        let edit = try list(text).editingNeeds("T3", add: ["T1"], remove: [])
        #expect(!edit.changed)
        let removed = try list(text).editingNeeds("T3", add: [], remove: ["T1"])
        #expect(removed.text.contains("  - Needs: T2 (parser first)\n"))
    }

    @Test func refusesACycleAndNamesThePath() {
        let message = refusal { try list().editingNeeds("T2", add: ["T3"], remove: []) }
        #expect(message?.contains("dependency cycle: T2 → T3 → T2") == true)
        #expect(refusal { try list().editingNeeds("T2", add: ["T2"], remove: []) }?.contains("cycle") == true)
    }

    @Test func refusesUnknownTargetsAndClosedTasks() {
        #expect(refusal { try list().editingNeeds("T2", add: ["T99"], remove: []) }?.contains("T99 does not exist") == true)
        #expect(refusal { try list().editingNeeds("T98", add: ["T1"], remove: []) } == "no task T98")
        #expect(refusal { try list().editingNeeds("T1", add: ["T2"], remove: []) }?.contains("closed items are not rewritten") == true)
        #expect(usage { try list().editingNeeds("T2", add: ["T1"], remove: ["T1"]) } != nil)
    }
}

@Suite("close and reopen")
struct CloseEditTests {
    @Test func closesATaskWithAReasonWordAndADatedWhy() throws {
        let edit = try list().closing("T4", reason: "OBSOLETE", why: "done by other means", date: "2026-10-22")
        let lines = edit.text.components(separatedBy: "\n")
        let at = lines.firstIndex(of: "- [-] T4 OBSOLETE — Wire it together")!
        #expect(lines[at + 1] == "  - Why: done by other means (2026-10-22)")
        #expect(lines[at + 2] == "  - Model: heavy (Opus 5.5)")
        #expect(edit.text.replacingOccurrences(of: "  - Why: done by other means (2026-10-22)\n", with: "")
                    .replacingOccurrences(of: "- [-] T4 OBSOLETE — ", with: "- [ ] T4 ") == sample)
    }

    @Test func supersededNeedsByAndByNeedsSuperseded() throws {
        #expect(usage { try list().closing("T4", reason: "SUPERSEDED", why: "x", date: "2026-10-22") }?.contains("--by") == true)
        #expect(usage { try list().closing("T4", reason: "OBSOLETE", by: ["T3"], why: "x", date: "2026-10-22") } != nil)
        #expect(refusal { try list().closing("T4", reason: "SUPERSEDED", by: ["T99"], why: "x", date: "2026-10-22") }?.contains("T99 does not exist") == true)
        let edit = try list().closing("T4", reason: "SUPERSEDED", by: ["T2", "T3"], why: "split in two", date: "2026-10-22")
        #expect(edit.text.contains("- [-] T4 SUPERSEDED→T2,T3 — Wire it together"))
        #expect(Tasklist(text: edit.text).task("T4")?.supersededBy == ["T2", "T3"])
    }

    @Test func refusesDoneAndAlreadyClosedAndUnconfirmedUserTasks() throws {
        #expect(refusal { try list().closing("T1", reason: "OBSOLETE", why: "x", date: "2026-10-22") }?.contains("[x]") == true)
        #expect(refusal { try list().closing("T5", reason: "OBSOLETE", why: "x", date: "2026-10-22") }?.contains("already closed") == true)
        #expect(refusal { try list().closing("T6", reason: "OBSOLETE", why: "x", date: "2026-10-22") }?.contains("--confirmed") == true)
        let confirmed = try list().closing("T6", reason: "OBSOLETE", why: "the owner dropped it", date: "2026-10-22", userConfirmed: true)
        #expect(confirmed.text.contains("- [-] T6 USER OBSOLETE — Confirm the format with the owner"))
        #expect(usage { try list().closing("T4", reason: "OBSOLETE", why: "x", date: "22-10-2026") } != nil)
        #expect(usage { try list().closing("T4", reason: "OBSOLETE", why: "", date: "2026-10-22") } != nil)
    }

    @Test func closingABlockedTaskKeepsItsOldWhyAndLeavesOneWhyLine() throws {
        let edit = try list().closing("T7", reason: "INVALID", why: "the service does not exist", date: "2026-10-22")
        #expect(edit.text.contains("- [-] T7 INVALID — Call the service"))
        #expect(edit.text.contains("  - Why: the service does not exist (2026-10-22); was: waiting for the key (2026-10-04)\n"))
        #expect(edit.text.components(separatedBy: "  - Why:").count - 1 == 2)   // T5's and T7's
        #expect(Tasklist(text: edit.text).lint().filter { $0.message.contains("more than one") }.isEmpty)
    }

    @Test func closingAHeadingTouchesOnlyTheHeadingAndAddsAWhyAndLeavesDoneTasksDone() throws {
        let edit = try list().closing("G1", reason: "DEFERRED", why: "later", date: "2026-10-22")
        let after = Tasklist(text: edit.text)
        #expect(after.heading("G1")?.reason == "DEFERRED")
        #expect(after.task("T1")?.mark == .done)
        #expect(after.task("T2")?.mark == .open)
        let lines = edit.text.components(separatedBy: "\n")
        let at = lines.firstIndex(of: "## G1 First — DEFERRED")!
        #expect(lines[at + 1] == "Goal: the first thing works.")
        #expect(lines[at + 2] == "Why: later (2026-10-22)")
        #expect(edit.text.replacingOccurrences(of: "Why: later (2026-10-22)\n", with: "").replacingOccurrences(of: " — DEFERRED", with: "") == sample)
    }

    @Test func aHeadingWithNothingOpenOrAnOpenUserTaskIsRefused() throws {
        let finished = "## G1 Done\n\n- [x] T1 A\n  - Model: light\n"
        #expect(refusal { try list(finished).closing("G1", reason: "OBSOLETE", why: "x", date: "2026-10-22") }?.contains("nothing is open") == true)
        #expect(refusal { try list().closing("G2", reason: "OBSOLETE", why: "x", date: "2026-10-22") }?.contains("T6") == true)
        #expect(throws: Never.self) { try list().closing("G2", reason: "OBSOLETE", why: "x", date: "2026-10-22", userConfirmed: true) }
    }

    @Test func reopensOnlyDeferredTasksAndKeepsTheOldReason() throws {
        #expect(refusal { try list().reopening("T5", why: "the owner wants it", date: "2026-10-22") }?.contains("pass --model") == true)
        let edit = try list().reopening("T5", why: "the owner wants it", date: "2026-10-22", tier: "light")
        #expect(edit.text.contains("- [ ] T5 Export to CSV\n  - Why: the owner wants it (2026-10-22); was DEFERRED: not for the first release (2026-10-03)\n  - Model: light (Haiku 4.5)\n"))
        let keepsModel = try list(sample.replacingOccurrences(of: "  - Why: not for", with: "  - Model: standard (Sonnet 5.5)\n  - Why: not for")).reopening("T5", why: "back", date: "2026-10-22")
        #expect(keepsModel.text.contains("  - Model: standard (Sonnet 5.5)\n"))
        #expect(edit.text.contains("  - Why: the owner wants it (2026-10-22); was DEFERRED: not for the first release (2026-10-03)\n"))
        #expect(Tasklist(text: edit.text).task("T5")?.mark == .open)
        let closed = sample.replacingOccurrences(of: "T5 DEFERRED", with: "T5 OBSOLETE")
        #expect(refusal { try list(closed).reopening("T5", why: "x", date: "2026-10-22") }?.contains("only DEFERRED") == true)
        #expect(refusal { try list().reopening("T2", why: "x", date: "2026-10-22") }?.contains("not closed") == true)
    }
}

@Suite("add")
struct AddEditTests {
    @Test func appendsToTheGroupWithTheNextIDAndTheTiersDefaultModel() throws {
        let edit = try list().adding(NewTask(title: "Add the exporter", under: "G2", tier: "light", needs: ["T3"],
                                              context: "Found during T4.", doneWhen: "the export test passes"))
        #expect(edit.result == "T8")
        let lines = edit.text.components(separatedBy: "\n")
        let at = lines.firstIndex(of: "- [ ] T8 Add the exporter")!
        #expect(Array(lines[at...(at + 4)]) == ["- [ ] T8 Add the exporter", "  - Model: light (Haiku 4.5)", "  - Needs: T3",
                                                "  - Context: Found during T4.", "  - Done when: the export test passes"])
        #expect(lines[at - 1] == "")
        #expect(Tasklist(text: edit.text).task("T8")?.group == "G2")
        #expect(edit.text.replacingOccurrences(of: "\n\n- [ ] T8 Add the exporter\n  - Model: light (Haiku 4.5)\n  - Needs: T3\n  - Context: Found during T4.\n  - Done when: the export test passes", with: "") == sample)
    }

    @Test func aNamedModelOverridesTheDefaultAndBeforePlacesItAheadOfATask() throws {
        let edit = try list().adding(NewTask(title: "Reorder", before: "T3", tier: "heavy", modelName: "Opus 6"))
        let lines = edit.text.components(separatedBy: "\n")
        let at = lines.firstIndex(of: "- [ ] T8 Reorder")!
        #expect(lines[at + 1] == "  - Model: heavy (Opus 6)")
        #expect(lines[at + 3] == "- [ ] T3 Add the renderer")
        #expect(Tasklist(text: edit.text).task("T8")?.group == "G1")
    }

    @Test func userTasksGetLetteredStepsAndNoModel() throws {
        let edit = try list().adding(NewTask(title: "Create the key", under: "G1", doneWhen: "reply with the key ID", user: true, steps: ["Open the console.", "Click Create."]))
        let lines = edit.text.components(separatedBy: "\n")
        let at = lines.firstIndex(of: "- [ ] T8 USER — Create the key")!
        #expect(Array(lines[(at + 1)...(at + 4)]) == ["  - Steps:", "    a. Open the console.", "    b. Click Create.", "  - Done when: reply with the key ID"])
        let parsed = Tasklist(text: edit.text)
        #expect(parsed.task("T8")?.user == true)
        #expect(parsed.lint().filter { $0.severity == .error }.isEmpty)
        #expect(usage { try list().adding(NewTask(title: "x", under: "G1", user: true)) }?.contains("--step") == true)
        #expect(usage { try list().adding(NewTask(title: "x", under: "G1", tier: "light", steps: ["a"])) } != nil)
    }

    @Test func needsAGroupWhenTheListHasHeadingsAndKnownTargets() {
        #expect(refusal { try list().adding(NewTask(title: "x", tier: "light")) }?.contains("--under") == true)
        #expect(refusal { try list().adding(NewTask(title: "x", under: "G9", tier: "light")) }?.contains("no group") == true)
        #expect(refusal { try list().adding(NewTask(title: "x", under: "G1", tier: "light", needs: ["T99"])) }?.contains("T99 does not exist") == true)
        #expect(refusal { try list().adding(NewTask(title: "x", under: "G1", before: "T4", tier: "light")) }?.contains("not under G1") == true)
        #expect(usage { try list().adding(NewTask(title: "x", under: "G1", tier: "tiny")) } != nil)
        #expect(refusal { try list().adding(NewTask(title: "OBSOLETE rewrite", under: "G1", tier: "light")) }?.contains("status word") == true)
    }

    @Test func aListOfBareTasksTakesNewTasksAtTheEndAndMatchesCompactSpacing() throws {
        let bare = "- [ ] T1 A\n  - Model: light\n- [ ] T2 B\n  - Model: light\n"
        let edit = try list(bare).adding(NewTask(title: "C", tier: "standard"))
        #expect(edit.text == bare + "- [ ] T3 C\n  - Model: standard (Sonnet 5.5)\n")
        #expect(refusal { try list("# Tasklist\n").adding(NewTask(title: "C", tier: "light")) }?.contains("does not create lists") == true)
    }

    @Test func anEmptyGroupGetsItsFirstTaskUnderTheGoal() throws {
        let text = "## G1 One\nGoal: g.\n\n## G2 Two\nGoal: h.\n\n- [ ] T1 A\n  - Model: light\n"
        let edit = try list(text).adding(NewTask(title: "B", under: "G1", tier: "light"))
        #expect(edit.text == "## G1 One\nGoal: g.\n\n- [ ] T2 B\n  - Model: light (Haiku 4.5)\n\n## G2 Two\nGoal: h.\n\n- [ ] T1 A\n  - Model: light\n")
    }

    @Test func tierDefaultsMatchTheSkillsTable() throws {
        let skill = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
            .appendingPathComponent("skills/tasklist/SKILL.md")
        let text = try String(contentsOf: skill, encoding: .utf8)
        for (tier, model) in tierModels {
            #expect(text.contains("| `\(tier)` |") && text.contains("| \(model) |"), "\(tier) → \(model) is not in the tasklist skill's table")
        }
    }
}

@Suite("set")
struct SetEditTests {
    @Test func replacesOneSingleLineFieldAndNothingElse() throws {
        let edit = try list().setting("T3", field: .doneWhen, to: "the renderer test passes on empty input")
        let diff = changes(sample, edit.text)
        #expect(diff.count == 1)
        #expect(diff[0].1 == "  - Done when: the renderer test passes on empty input")
    }

    @Test func aMultiLineContextIsByteIdenticalOutsideTheEditedField() throws {
        let edit = try list().setting("T2", field: .doneWhen, to: "the parser test passes")
        #expect(edit.text.contains("    Second line of the context, with `code` and a colon: kept as is.\n    Third line.\n"))
        let other = try list().setting("T2", field: .doneWhen, to: "the parser and lexer tests pass")
        #expect(changes(sample, other.text).count == 1)
        // Replacing the context itself swaps the whole field, continuation lines included, and no other line.
        let context = try list().setting("T2", field: .context, to: "One line now.")
        let removed = sample.replacingOccurrences(of: "  - Context: Reads the input format.\n    Second line of the context, with `code` and a colon: kept as is.\n    Third line.\n", with: "  - Context: One line now.\n")
        #expect(context.text == removed)
    }

    @Test func appendAddsAContinuationLineAndIsIdempotent() throws {
        let edit = try list().setting("T2", field: .notes, to: "Also the huge input.", append: true)
        #expect(edit.text.contains("  - Notes: Watch the empty input.\n    Also the huge input.\n"))
        let again = try Tasklist(text: edit.text).setting("T2", field: .notes, to: "Also the huge input.", append: true)
        #expect(!again.changed)
        let ctx = try list().setting("T3", field: .context, to: "Found during T2.", append: true)
        #expect(ctx.text.contains("  - Context: Found during T2.\n"))   // created in the standard position
        #expect(usage { try list().setting("T2", field: .run, to: "x", append: true) } != nil)
    }

    @Test func sameValueIsANoOpAndAMissingFieldIsCreatedInPosition() throws {
        #expect(!(try list().setting("T3", field: .doneWhen, to: "the renderer test passes")).changed)
        let edit = try list().setting("T3", field: .run, to: "`swift test`")
        let lines = edit.text.components(separatedBy: "\n")
        let at = lines.firstIndex(of: "- [ ] T3 Add the renderer")!
        #expect(lines[at + 3] == "  - Run: `swift test`")
        #expect(lines[at + 4] == "  - Done when: the renderer test passes")
    }

    @Test func modelTakesATierAndFillsTheName() throws {
        let edit = try list().setting("T3", field: .model, to: "heavy")
        #expect(edit.text.contains("- [ ] T3 Add the renderer\n  - Model: heavy (Opus 5.5)\n"))
        #expect(try list().setting("T3", field: .model, to: "light (Haiku 5)").text.contains("  - Model: light (Haiku 5)\n"))
        #expect(usage { try list().setting("T3", field: .model, to: "Opus") } != nil)
        #expect(refusal { try list().setting("T6", field: .model, to: "light") }?.contains("USER") == true)
    }

    @Test func titleKeepsTheCheckboxIDAndQualifiers() throws {
        let edit = try list().setting("T7", field: .title, to: "Call the billing service")
        #expect(changes(sample, edit.text).map(\.1) == ["- [ ] T7 BLOCKED(no key yet) — Call the billing service"])
        let user = try list().setting("T6", field: .title, to: "Agree the format with the owner")
        #expect(user.text.contains("- [ ] T6 USER — Agree the format with the owner\n"))
        #expect(refusal { try list().setting("T3", field: .title, to: "USER something") }?.contains("status word") == true)
    }

    @Test func titleWarnsWhenAnotherTaskQuotesTheOldOne() throws {
        let text = sample.replacingOccurrences(of: "  - Needs: T3", with: "  - Needs: T3\n  - Context: Follows \"Add the renderer\" closely.")
        let edit = try list(text).setting("T3", field: .title, to: "Draw the output")
        #expect(edit.warnings.count == 1)
        #expect(edit.warnings[0].contains("T4 mentions the old title of T3"))
        #expect(try list().setting("T3", field: .title, to: "Draw the output").warnings.isEmpty)
    }

    @Test func refusesClosedTasksAndClaimedOnesAndHeadings() {
        for id in ["T1", "T5"] {
            let message = refusal { try list().setting(id, field: .context, to: "new") }
            #expect(message?.contains("closed items are not rewritten") == true && message?.contains("add a new task") == true)
        }
        #expect(refusal { try list().setting("T1", field: .notes, to: "x") } != nil)
        #expect(refusal { try list().setting("G1", field: .title, to: "x") }?.contains("heading") == true)
        let claimed = sample.replacingOccurrences(of: "T3 Add the renderer", with: "T3 IN-PROGRESS — Add the renderer")
        #expect(refusal { try list(claimed).setting("T3", field: .doneWhen, to: "x") }?.contains("IN-PROGRESS") == true)
        #expect(throws: Never.self) { try list(claimed).setting("T3", field: .notes, to: "x") }
        #expect(throws: Never.self) { try list(claimed).setting("T3", field: .model, to: "heavy") }
    }

    @Test func refusesATaskWithADuplicatedField() {
        let doubled = sample.replacingOccurrences(of: "  - Needs: T2\n", with: "  - Needs: T2\n  - Needs: T1\n")
        #expect(refusal { try list(doubled).setting("T3", field: .doneWhen, to: "x") } == nil)
        #expect(refusal { try list(doubled).editingNeeds("T3", add: ["T1"], remove: []) }?.contains("2 Needs: lines") == true)
        #expect(list(doubled).lint().contains { $0.severity == .warning && $0.message.contains("T3 has more than one Needs: line") })
    }
}

@Suite("edit pipeline")
struct EditPipelineTests {
    @Test func lintAfterTheEditCatchesABadEditAndWritesNothing() throws {
        let base = list()
        var lines = sample.components(separatedBy: "\n")
        lines.insert(contentsOf: ["- [ ] T2 A second T2", "  - Model: light"], at: lines.firstIndex(of: "## G2 Second")! + 1)
        #expect { try base.finish(lines, summary: "bad") } throws: { error in
            "\(error)".contains("duplicate ID T2") && "\(error)".contains("nothing written")
        }
        // An error the file already had does not block an unrelated edit.
        let broken = sample + "- [ ] T8 No model\n"
        #expect(throws: Never.self) { try list(broken).setting("T3", field: .notes, to: "fine") }
    }

    @Test func anEditThatDropsAnIDIsRefused() {
        let lines = sample.components(separatedBy: "\n").filter { !$0.contains("T4") }
        #expect { try list().finish(lines, summary: "bad") } throws: { "\($0)".contains("would drop T4") }
    }

    @Test func newWarningsAreReportedButOldOnesAreNot() throws {
        let edit = try list().closing("T3", reason: "OBSOLETE", why: "not needed", date: "2026-10-22")
        #expect(edit.warnings.contains { $0.contains("T4 needs T3, which is OBSOLETE") })
        let again = try Tasklist(text: edit.text).setting("T4", field: .notes, to: "x")
        #expect(again.warnings.isEmpty)
    }

    @Test func tickingStillChangesOnlyTheCheckbox() throws {
        let edit = try list().ticked(["T2"])
        #expect(changes(sample, edit.text).map(\.1) == ["- [x] T2 Add the parser"])
    }
}

@Suite("diff and files")
struct EditorTests {
    private func temp(_ text: String, mode: Int = 0o640) throws -> String {
        let path = NSTemporaryDirectory() + "plantools-\(UUID().uuidString).md"
        try text.write(toFile: path, atomically: true, encoding: .utf8)
        try FileManager.default.setAttributes([.posixPermissions: mode], ofItemAtPath: path)
        return path
    }

    @Test func dryRunPrintsAUnifiedDiffAndWritesNothing() throws {
        let path = try temp(sample)
        let report = try Editor.apply(file: path, dryRun: true) { try $0.setting("T3", field: .doneWhen, to: "it renders") }
        #expect(report.stdout[0].contains("--- a/\(path)"))
        #expect(report.stdout[0].contains("-  - Done when: the renderer test passes\n+  - Done when: it renders"))
        #expect(report.stdout[0].contains("@@ -"))
        #expect(report.stdout.last == "dry run: nothing written")
        #expect(try String(contentsOfFile: path, encoding: .utf8) == sample)
    }

    @Test func writePreservesPermissionsAndTheTrailingNewlineOrItsAbsence() throws {
        let path = try temp(sample, mode: 0o600)
        _ = try Editor.apply(file: path, dryRun: false) { try $0.setting("T3", field: .doneWhen, to: "it renders") }
        let attributes = try FileManager.default.attributesOfItem(atPath: path)
        #expect((attributes[.posixPermissions] as? Int) == 0o600)
        let written = try String(contentsOfFile: path, encoding: .utf8)
        #expect(written.hasSuffix("\n") && written.contains("it renders"))

        let bare = String(sample.dropLast(2))
        let other = try temp(bare)
        _ = try Editor.apply(file: other, dryRun: false) { try $0.setting("T7", field: .doneWhen, to: "ok") }
        #expect(!(try String(contentsOfFile: other, encoding: .utf8)).hasSuffix("\n"))
        #expect(try FileManager.default.contentsOfDirectory(atPath: NSTemporaryDirectory()).filter { $0.hasSuffix(".tmp") && $0.hasPrefix(".plantools-") }.isEmpty)
    }

    @Test func aNoOpLeavesTheFileAlone() throws {
        let path = try temp(sample)
        let before = try FileManager.default.attributesOfItem(atPath: path)[.modificationDate] as? Date
        let report = try Editor.apply(file: path, dryRun: false) { try $0.editingNeeds("T3", add: ["T2"], remove: []) }
        #expect(report.stdout == ["T3 needs T2: no change"])
        #expect(try FileManager.default.attributesOfItem(atPath: path)[.modificationDate] as? Date == before)
    }

    @Test func aRefusalLeavesTheFileUnchangedAndCRLFFilesAreNotTouched() throws {
        let path = try temp(sample)
        #expect(throws: Tasklist.EditError.self) { try Editor.apply(file: path, dryRun: false) { try $0.editingNeeds("T2", add: ["T3"], remove: []) } }
        #expect(try String(contentsOfFile: path, encoding: .utf8) == sample)
        let crlf = try temp(sample.replacingOccurrences(of: "\n", with: "\r\n"))
        #expect(throws: Tasklist.EditError.self) { try Editor.apply(file: crlf, dryRun: false) { try $0.setting("T3", field: .notes, to: "x") } }
        #expect(throws: EditUsageError.self) { try Editor.apply(file: "/nonexistent/Tasklist.md", dryRun: false) { try $0.ticked(["T1"]) } }
    }

    @Test func unifiedDiffGroupsNearbyChangesIntoOneHunkAndSplitsFarOnes() {
        let old = (1...30).map { "line \($0)" }.joined(separator: "\n") + "\n"
        let near = old.replacingOccurrences(of: "line 10\n", with: "ten\n").replacingOccurrences(of: "line 12\n", with: "twelve\n")
        #expect(UnifiedDiff.make(old: old, new: near, name: "f").components(separatedBy: "@@ -").count == 2)
        let far = old.replacingOccurrences(of: "line 3\n", with: "three\n").replacingOccurrences(of: "line 28\n", with: "twenty-eight\n")
        #expect(UnifiedDiff.make(old: old, new: far, name: "f").components(separatedBy: "@@ -").count == 3)
        #expect(UnifiedDiff.make(old: old, new: old, name: "f") == "")
        let added = UnifiedDiff.make(old: "a\nb\n", new: "a\nx\nb\n", name: "f")
        #expect(added == "--- a/f\n+++ b/f\n@@ -1,2 +1,3 @@\n a\n+x\n b")
    }

    @Test func isoDatesAreChecked() {
        #expect(Tasklist.isoDate("2026-10-22"))
        #expect(!Tasklist.isoDate("2026-02-30"))
        #expect(!Tasklist.isoDate("26-10-22"))
        #expect(Tasklist.isoDate(Tasklist.today()))
    }
}
