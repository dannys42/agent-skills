import ArgumentParser
import Foundation
import PlanKit

@main
struct RoadmapTool: ParsableCommand {
    static let configuration = CommandConfiguration(
        commandName: "roadmap",
        abstract: "Read a roadmap, or any markdown file, by section. Plain text out; exit 1 means a problem was found.",
        version: planToolsVersion,
        subcommands: [Status.self, Show.self, Outline.self, Section.self, Lint.self]
    )

    struct Input: ParsableArguments {
        @Argument(help: "Markdown file.") var file: String
        var text: String { CLI.read(file) }
    }

    struct Status: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Next rung, finished rungs on one line, every other rung on its own line.")
        @OptionGroup var input: Input
        func run() throws { CLI.print(Roadmap(text: input.text).status()) }
    }

    struct Show: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Ladder line, detail section and learning-log entries of one rung.")
        @OptionGroup var input: Input
        @Argument var rung: String
        @Flag(name: .customLong("no-log"), help: "Leave out the learning-log entries.") var noLog = false

        func run() throws {
            guard let out = Roadmap(text: input.text).show(rung, includeLog: !noLog) else {
                CLI.fail("no rung \(rung) on the ladder", code: 1)
            }
            CLI.print(out)
        }
    }

    struct Outline: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Any markdown file: line, own bytes, subtree bytes, heading.")
        @OptionGroup var input: Input
        func run() throws { CLI.print(Markdown(text: input.text).outline()) }
    }

    struct Section: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Any markdown file: one section by heading text or leading ID.")
        @OptionGroup var input: Input
        @Argument(help: "Heading text or its leading ID, e.g. Risks or L9.") var heading: [String]

        func run() throws {
            let query = heading.joined(separator: " ")
            let md = Markdown(text: input.text)
            guard let s = md.section(matching: query) else { CLI.fail("no heading matching \(query)", code: 1) }
            CLI.print(md.text(from: s.line, to: s.endLine))
        }
    }

    struct Lint: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Unique rung IDs, ladder and detail sections agree, size budgets.")
        @OptionGroup var input: Input
        @Option(name: .customLong("max-bytes")) var maxBytes = 40_000
        @Option(name: .customLong("max-line")) var maxLine = 1_500

        func run() throws {
            let code = CLI.report(Roadmap(text: input.text).lint(budget: .init(maxBytes: maxBytes, maxLine: maxLine)))
            if code != 0 { throw ExitCode(code) }
        }
    }
}
