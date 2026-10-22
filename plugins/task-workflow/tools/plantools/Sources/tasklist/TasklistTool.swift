import ArgumentParser
import Foundation
import PlanKit

@main
struct TasklistTool: ParsableCommand {
    static let configuration = CommandConfiguration(
        commandName: "tasklist",
        abstract: "Apply the tasklist skill's rules mechanically. Plain text out; exit 1 means a problem was found.",
        version: planToolsVersion,
        subcommands: [Next.self, Show.self, Context.self, NextID.self, Lint.self, Done.self, Needs.self, Close.self, Reopen.self,
                      Add.self, SetField.self, Status.self]
    )

    /// ArgumentParser reports bad usage as 64; this tool's contract is 2.
    static func main() {
        do {
            var command = try parseAsRoot()
            try command.run()
        } catch {
            if exitCode(for: error) == .validationFailure { CLI.fail(fullMessage(for: error), code: 2) }
            exit(withError: error)
        }
    }

    /// Runs one editing command: exit 0 done or nothing to do, 1 refused by a rule, 2 bad usage.
    static func edit(_ file: String, dryRun: Bool, _ make: (Tasklist) throws -> Edit) throws {
        do {
            let report = try Editor.apply(file: file, dryRun: dryRun, make)
            report.stderr.forEach { FileHandle.standardError.write(Data(($0 + "\n").utf8)) }
            report.stdout.forEach { CLI.print($0) }
        } catch let error as Tasklist.EditError { CLI.fail("\(error)", code: 1)
        } catch let error as EditUsageError { CLI.fail("\(error)", code: 2) }
    }

    struct Source: ParsableArguments {
        @Argument(help: "Tasklist file.") var file: String
        var list: Tasklist { Tasklist(text: CLI.read(file)) }
    }

    struct Next: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "First eligible task; on none, the blockers and exit 1.")
        @OptionGroup var source: Source
        @Flag(help: "Print the whole task block.") var block = false
        @Flag(help: "Print Source, enclosing Goals and the task block.") var context = false

        func run() throws {
            let list = source.list
            guard let task = list.next() else {
                CLI.print("none eligible")
                list.blockers().forEach { CLI.print($0) }
                throw ExitCode(1)
            }
            if context { CLI.print(list.context(for: task)) }
            else if block { CLI.print(list.block(of: task)) }
            else { CLI.print("\(task.id) \(task.title)") }
        }
    }

    struct Show: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "One task block, or a phase/group heading with its Goal and tasks.")
        @OptionGroup var source: Source
        @Argument var id: String

        func run() throws {
            let list = source.list
            if let h = list.heading(id) {
                CLI.print("\(h.id) \(h.title)" + (h.goal.map { "\nGoal: \($0)" } ?? ""))
                for t in list.tasks where t.group == id || (h.id.hasPrefix("P") && t.phase == id) { CLI.print("- \(t.id) \(t.title)") }
            } else if let task = list.task(id) {
                CLI.print(list.block(of: task))
            } else {
                CLI.fail("no task \(id)", code: 1)
            }
        }
    }

    struct Context: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Source, enclosing Goal lines and the task block: the start of an implementer prompt.")
        @OptionGroup var source: Source
        @Argument var id: String

        func run() throws {
            let list = source.list
            guard let task = list.task(id) else { CLI.fail("no task \(id)", code: 1) }
            CLI.print(list.context(for: task))
        }
    }

    struct NextID: ParsableCommand {
        static let configuration = CommandConfiguration(commandName: "next-id", abstract: "Next unused ID, counting closed items.")
        @OptionGroup var source: Source
        @Argument(help: "P, G or T.") var prefix: String = "T"

        func run() throws { CLI.print(source.list.nextID(prefix: prefix.first ?? "T")) }
    }

    struct Lint: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "The mechanical checks of \"Before finishing\"; exit 1 on any error.")
        @OptionGroup var source: Source
        @Option(help: "An older copy of the file: also report deleted IDs and titles rewritten in place.") var base: String?

        func run() throws {
            let code = CLI.report(source.list.lint(base: base.map { Tasklist(text: CLI.read($0)) }))
            if code != 0 { throw ExitCode(code) }
        }
    }

    struct Done: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Tick tasks [x]; changes only the checkbox.")
        @Argument(help: "Tasklist file.") var file: String
        @Argument(help: "Task IDs.") var ids: [String]
        @Flag(help: "Required for USER tasks, once the user has confirmed them.") var confirmed = false
        @Flag(help: "Print a unified diff and write nothing.") var dryRun = false

        func run() throws { try TasklistTool.edit(file, dryRun: dryRun) { try $0.ticked(ids, userConfirmed: confirmed) } }
    }

    struct Needs: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Add or remove Needs edges on one open task; refuses unknown IDs and cycles.")
        @Argument(help: "Tasklist file.") var file: String
        @Argument(help: "Task ID.") var id: String
        @Option(name: .customLong("add"), parsing: .upToNextOption, help: "Task IDs to add to Needs.") var add: [String] = []
        @Option(name: .customLong("remove"), parsing: .upToNextOption, help: "Task IDs to drop from Needs.") var remove: [String] = []
        @Flag(help: "Print a unified diff and write nothing.") var dryRun = false

        func validate() throws { if add.isEmpty && remove.isEmpty { throw ValidationError("give --add or --remove") } }
        func run() throws { try TasklistTool.edit(file, dryRun: dryRun) { try $0.editingNeeds(id, add: add, remove: remove) } }
    }

    struct Close: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Close a task, phase or group without doing it: [-], reason word, dated Why:.")
        @Argument(help: "Tasklist file.") var file: String
        @Argument(help: "Task, phase or group ID.") var id: String
        @Option(help: "OBSOLETE, INVALID, SUPERSEDED or DEFERRED.") var reason: String
        @Option(name: .customLong("by"), parsing: .upToNextOption, help: "With SUPERSEDED: the task(s) that take over.") var by: [String] = []
        @Option(help: "One line: why it is closed.") var why: String
        @Option(help: "YYYY-MM-DD; default today.") var date: String = Tasklist.today()
        @Flag(help: "Required for USER tasks, once the user has agreed.") var confirmed = false
        @Flag(help: "Print a unified diff and write nothing.") var dryRun = false

        func run() throws {
            try TasklistTool.edit(file, dryRun: dryRun) {
                try $0.closing(id, reason: reason.uppercased(), by: by, why: why, date: date, userConfirmed: confirmed)
            }
        }
    }

    struct Reopen: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Reopen a DEFERRED task: [ ], word dropped, Why: updated. Other closed items are not reopened.")
        @Argument(help: "Tasklist file.") var file: String
        @Argument(help: "Task ID.") var id: String
        @Option(help: "One line: why it is back.") var why: String
        @Option(help: "YYYY-MM-DD; default today.") var date: String = Tasklist.today()
        @Option(help: "light, standard or heavy: required when the task has no Model, otherwise replaces it.") var model: String?
        @Option(help: "Named model instead of the tier's default.") var modelName: String?
        @Flag(help: "Print a unified diff and write nothing.") var dryRun = false

        func run() throws {
            try TasklistTool.edit(file, dryRun: dryRun) { try $0.reopening(id, why: why, date: date, tier: model, modelName: modelName) }
        }
    }

    struct Add: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Add one open task with the next unused T ID at the end of a group or phase (or before a task); prints the ID.")
        @Argument(help: "Tasklist file.") var file: String
        @Option(name: .customLong("under"), help: "Group or phase ID; needed when the list has headings.") var under: String?
        @Option(help: "Place it just before this task instead.") var before: String?
        @Option(help: "Task title.") var title: String
        @Option(help: "light, standard or heavy; the named model is filled in.") var model: String?
        @Option(help: "Named model instead of the tier's default.") var modelName: String?
        @Option(name: .customLong("needs"), parsing: .upToNextOption, help: "Task IDs it needs.") var needs: [String] = []
        @Option(help: "One line of Context.") var context: String?
        @Option(help: "One line of Done when.") var doneWhen: String?
        @Flag(help: "A task only the user can do: no Model, lettered steps.") var user = false
        @Option(name: [.customLong("step"), .customLong("steps")], help: "A USER step; repeat for a, b, c.") var steps: [String] = []
        @Flag(help: "Print a unified diff and write nothing.") var dryRun = false

        func run() throws {
            let spec = NewTask(title: title, under: under, before: before, tier: model, modelName: modelName, needs: needs,
                               context: context, doneWhen: doneWhen, user: user, steps: steps)
            try TasklistTool.edit(file, dryRun: dryRun) { try $0.adding(spec) }
        }
    }

    struct SetField: ParsableCommand {
        static let configuration = CommandConfiguration(
            commandName: "set",
            abstract: "Replace one field of an open task: title, model, run, verify, done-when, notes or context. Closed tasks are never rewritten."
        )
        @Argument(help: "Tasklist file.") var file: String
        @Argument(help: "Task ID.") var id: String
        @Argument(help: "title, model, run, verify, done-when, notes or context.") var field: String
        @Argument(help: "New one-line value (a model takes a tier).") var text: String
        @Flag(help: "Add a line to context or notes instead of replacing it.") var append = false
        @Flag(help: "Print a unified diff and write nothing.") var dryRun = false

        func validate() throws {
            if field == "needs" { throw ValidationError("use `tasklist needs <file> <ID> --add/--remove` for Needs") }
            if SettableField(rawValue: field) == nil {
                throw ValidationError("field must be one of \(SettableField.allCases.map(\.rawValue).joined(separator: ", "))")
            }
        }
        func run() throws {
            let which = SettableField(rawValue: field)!
            try TasklistTool.edit(file, dryRun: dryRun) { try $0.setting(id, field: which, to: text, append: append) }
        }
    }

    struct Status: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Counts of open, done, closed, blocked, USER and eligible tasks.")
        @OptionGroup var source: Source

        func run() throws {
            let c = source.list.counts()
            CLI.print("open \(c.open) (eligible \(c.eligible), blocked \(c.blocked), USER \(c.user)), done \(c.done), closed \(c.closed)")
        }
    }
}
