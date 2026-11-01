import ArgumentParser
import Foundation
import PlanKit

@main
struct RoadmapTool: ParsableCommand {
    static let configuration = CommandConfiguration(
        commandName: "roadmap",
        abstract: "Read a roadmap, or any markdown file, by section, or print the next step of the rung cycle. Plain text out; exit 1 means a problem was found.",
        version: planToolsVersion,
        subcommands: [Status.self, Show.self, Outline.self, Section.self, Lint.self, Next.self, Archive.self]
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

    struct Archive: ParsableCommand {
        static let configuration = CommandConfiguration(
            abstract: "Move finished rungs' sections verbatim to Completed/<Roadmap>-Rungs.md and add the detail: pointer to their ladder lines.",
            discussion: "Exit 1 when a rung is not done, failed, changed or obsolete, is not on the ladder, or the result would add a lint error; 2 on bad usage. A rung already archived is skipped.")
        @Argument(help: "Roadmap file.") var file: String
        @Argument(help: "Rung IDs, e.g. L3 L4.") var rungs: [String] = []
        @Flag(help: "Print a unified diff of both files and write nothing.") var dryRun = false

        func run() throws {
            if rungs.isEmpty { CLI.fail("name at least one rung", code: 2) }
            let text = CLI.read(file)
            let relative = RoadmapArchive.completedPath(forRoadmap: file)
            let target = URL(fileURLWithPath: file).deletingLastPathComponent().appendingPathComponent(relative).path
            let existing = try? String(contentsOfFile: target, encoding: .utf8)
            do {
                let result = try RoadmapArchive.make(roadmap: text, ids: rungs, completedPath: relative, completed: existing)
                result.skipped.forEach { CLI.print("skipped: \($0)") }
                guard !result.moved.isEmpty else { CLI.print("nothing to move"); return }
                if dryRun {
                    CLI.print(UnifiedDiff.make(old: text, new: result.roadmap, name: file))
                    CLI.print(UnifiedDiff.make(old: existing ?? "", new: result.completed, name: target))
                    CLI.print("dry run: nothing written")
                    return
                }
                try Editor.replace(file: target, original: existing, with: result.completed)
                try Editor.replace(file: file, original: text, with: result.roadmap)
                CLI.print("archived \(result.moved.joined(separator: " ")) to \(relative); check with git diff --color-moved")
            } catch let error as Tasklist.EditError { CLI.fail("\(error)", code: 1)
            } catch let error as EditUsageError { CLI.fail("\(error)", code: 2) }
        }
    }

    struct Next: ParsableCommand {
        static let configuration = CommandConfiguration(abstract: "Next step of the rung cycle from the project's docs, run from the project root.")
        @Option(help: "Documentation directory; default: the first of Documentation, docs, Docs, doc, . holding a roadmap or design.") var dir: String?
        @Option(help: "Roadmap file; default: the one Roadmap-*.md in the documentation directory.") var roadmap: String?

        func run() throws {
            let fm = FileManager.default
            func names(_ path: String) -> [String] { ((try? fm.contentsOfDirectory(atPath: path)) ?? []).filter { $0.hasSuffix(".md") }.sorted() }
            func isRoadmap(_ n: String) -> Bool { n.hasPrefix("Roadmap-") && !n.hasSuffix("-Log.md") }
            func hasOverview(_ d: String) -> Bool {
                fm.fileExists(atPath: d + "/SystemDesign/Overview.md") || names(d).contains { $0.hasPrefix("Design-") }
            }
            let docDir = dir ?? ["Documentation", "docs", "Docs", "doc"].first { d in
                names(d).contains { $0.hasPrefix("Roadmap-") } || hasOverview(d)
            } ?? "."
            var file = roadmap
            if file == nil {
                let found = names(docDir).filter(isRoadmap).map { docDir == "." ? $0 : docDir + "/" + $0 }
                if found.count > 1 {
                    CLI.print(found.joined(separator: "\n") + "\nmore than one roadmap; pass --roadmap <file> to pick one")
                    throw ExitCode(1)
                }
                file = found.first
            }
            func files(_ sub: String, prefix: String, completed: Bool) -> [NextStep.File] {
                let d = docDir + sub
                return names(d).filter { $0.hasPrefix(prefix) }.map { n in
                    let modified = (try? fm.attributesOfItem(atPath: d + "/" + n)[.modificationDate] as? Date) ?? nil
                    return NextStep.File(name: n, text: CLI.read(d + "/" + n), completed: completed, modified: modified ?? .distantPast)
                }
            }
            let step = NextStep.decide(.init(
                docDir: docDir, hasOverview: hasOverview(docDir), roadmap: file.map { Roadmap(text: CLI.read($0)) },
                tasklists: files("", prefix: "Tasklist-", completed: false) + files("/Completed", prefix: "Tasklist-", completed: true),
                briefs: files("/SystemDesign", prefix: "Rung-", completed: false)))
            CLI.print(step.rendered)
        }
    }
}
