import ArgumentParser
import Foundation
import PlanKit

@main
struct TasklistTool: ParsableCommand {
    static let configuration = CommandConfiguration(
        commandName: "tasklist",
        abstract: "Apply the tasklist skill's rules mechanically. Plain text out; exit 1 means a problem was found.",
        version: planToolsVersion,
        subcommands: [Next.self, Show.self, Context.self, NextID.self, Lint.self, Done.self, Status.self]
    )

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

        func run() throws {
            do {
                let text = try Tasklist(text: CLI.read(file)).ticking(ids, userConfirmed: confirmed)
                try text.write(toFile: file, atomically: true, encoding: .utf8)
                CLI.print("ticked \(ids.joined(separator: " "))")
            } catch let error as Tasklist.EditError { CLI.fail("\(error)", code: 1) }
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
