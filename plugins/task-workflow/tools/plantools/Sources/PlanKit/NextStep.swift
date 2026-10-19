import Foundation

/// The zero-token router for the rung cycle: from what is on disk, the next step a fresh session should run.
public struct NextStep: Equatable {
    public var step: String
    public var rung: String?
    public var list: String?
    public var model: String
    public var command: String
    public var why: String

    /// A tasklist or brief as found in the doc directory; `completed` marks a file under `Completed/`.
    public struct File {
        public let name: String
        public let text: String
        public let completed: Bool
        public let modified: Date
        public init(name: String, text: String, completed: Bool = false, modified: Date = .distantPast) {
            self.name = name; self.text = text; self.completed = completed; self.modified = modified
        }
    }

    /// Everything the rules read, injected so the decision needs no filesystem.
    public struct Input {
        public var docDir: String
        public var hasOverview: Bool
        public var roadmap: Roadmap?
        public var tasklists: [File]
        public var briefs: [File]
        public init(docDir: String = ".", hasOverview: Bool, roadmap: Roadmap?, tasklists: [File] = [], briefs: [File] = []) {
            self.docDir = docDir; self.hasOverview = hasOverview; self.roadmap = roadmap; self.tasklists = tasklists; self.briefs = briefs
        }
    }

    static func make(_ step: String, _ model: String, _ args: String = "", rung: String? = nil, list: String? = nil, why: String) -> NextStep {
        NextStep(step: step, rung: rung, list: list, model: model, command: "/rung " + step + (args.isEmpty ? "" : " " + args), why: why)
    }

    public static func decide(_ input: Input) -> NextStep {
        guard let roadmap = input.roadmap else {
            return input.hasOverview
                ? make("roadmap", "opus", why: "system design exists; no roadmap yet")
                : make("design", "opus", why: "no system design and no roadmap")
        }
        if let rung = roadmap.ladder.first(where: { $0.status.hasPrefix("in progress") }) {
            return decide(rung: rung.id, input)
        }
        if let rung = roadmap.ladder.first(where: { $0.status.hasPrefix("planned") }) {
            return make("plan", "opus", rung.id, rung: rung.id, why: "\(rung.id) is the first planned rung")
        }
        var done = make("finished", "opus", why: "no planned rung left; extend the ladder or stop")
        done.command = "/risk-first-roadmap"
        return done
    }

    static func decide(rung id: String, _ input: Input) -> NextStep {
        let lists = input.tasklists.filter { $0.name.hasPrefix("Tasklist-\(id)-") && $0.name.hasSuffix(".md") }
        let brief = input.briefs.first { $0.name.hasPrefix("Rung-\(id)-") && $0.name.hasSuffix(".md") }
        let briefStatus = brief.flatMap { b in
            b.text.split(separator: "\n", omittingEmptySubsequences: false)
                .first { $0.hasPrefix("Status:") }.map { $0.dropFirst(7).trimmingCharacters(in: .whitespaces).lowercased() }
        } ?? ""
        let open = lists.filter { !$0.completed }.map { ($0, Tasklist(text: $0.text).tasks.filter { $0.mark == .open }) }
            .filter { !$0.1.isEmpty }.sorted { $0.0.modified > $1.0.modified }

        if let (file, tasks) = open.first {
            let path = input.docDir == "." ? file.name : input.docDir + "/" + file.name
            let heavyCount = tasks.filter { $0.fields["model"]?.lowercased().hasPrefix("heavy") == true }.count
            let heavy = heavyCount * 2 > tasks.count
            let waiting = tasks.filter { $0.user && $0.blocked == nil }.map(\.id)
            let blocked = tasks.filter { $0.blocked != nil }.map(\.id)
            let run = make("run", heavy ? "opus" : "sonnet", id, rung: id, list: path, why: "\(file.name) has \(tasks.count) open task(s)")
            guard waiting.count + blocked.count == tasks.count else { return run }
            var parts: [String] = []
            if !waiting.isEmpty { parts.append("USER tasks waiting: " + waiting.joined(separator: ", ")) }
            if !blocked.isEmpty { parts.append("blocked: " + blocked.joined(separator: ", ")) }
            var user = run
            user.step = "user"
            user.why = parts.joined(separator: "; ")
            return user
        }
        if lists.isEmpty {
            let reason = brief == nil ? "brief missing" : briefStatus.hasPrefix("agreed") ? "brief agreed; no tasklist yet" : "brief is a draft"
            return make("plan", "opus", id, rung: id, why: "\(id) is in progress; \(reason)")
        }
        let last = lists.max { $0.modified < $1.modified }!
        let path = input.docDir == "." ? last.name : input.docDir + "/" + last.name
        if briefStatus.hasPrefix("folded back") {
            var replan = make("replan", "opus", rung: id, list: path, why: "\(id) folded back; roadmap still in progress")
            replan.command = "/rung replan"
            return replan
        }
        return make("close", "opus", id, rung: id, list: path, why: "\(last.name) closed; " + (brief == nil ? "no brief to fold back" : "brief not folded back"))
    }

    public var rendered: String {
        var rows = ["step: \(step)"]
        if let rung { rows.append("rung: \(rung)") }
        if let list { rows.append("list: \(list)") }
        rows += ["model: \(model)", "command: \(command)", "why: \(why)"]
        return rows.joined(separator: "\n")
    }
}
