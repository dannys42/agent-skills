import Foundation

/// The zero-token router for the rung cycle: from what is on disk, the next step a fresh session should run.
public struct NextStep: Equatable {
    public var step: String
    public var milestone: String?
    public var rung: String?
    public var list: String?
    public var model: String
    public var command: String
    public var why: String
    /// The wait-point handoff note this step resumes from; the step that consumes it deletes it.
    public var handoff: String? = nil

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
        /// Notes in `<DocDir>/Handoff/`, git-ignored, one per wait for the owner.
        public var handoffs: [File]
        public init(docDir: String = ".", hasOverview: Bool, roadmap: Roadmap?, tasklists: [File] = [], briefs: [File] = [], handoffs: [File] = []) {
            self.docDir = docDir; self.hasOverview = hasOverview; self.roadmap = roadmap; self.tasklists = tasklists; self.briefs = briefs
            self.handoffs = handoffs
        }
    }

    /// The dispatch target for a route: the skill invocation `/rung` runs with the Skill tool. Never shown to the owner.
    static func target(_ step: String, milestone: String? = nil, rung: String? = nil, list: String? = nil) -> String {
        func with(_ skill: String, _ args: String?...) -> String { ([skill] + args.compactMap { $0 }).joined(separator: " ") }
        switch step {
        case "design": return "system-design"
        case "roadmap", "replan", "finished": return "risk-first-roadmap"
        case "milestone-plan": return with("plan-milestone", "plan", milestone ?? rung)
        // Older roadmaps have no milestones: that session migrates the docs, folds back an in-flight rung, then plans.
        case "plan", "close": return "plan-milestone plan"
        case "escalation": return with("plan-milestone", "escalation", rung)
        case "milestone-close": return with("plan-milestone", "milestone-close", milestone)
        default: return with("tasklist-run", list) // run, user
        }
    }

    static func make(_ step: String, _ model: String, milestone: String? = nil, rung: String? = nil, list: String? = nil, why: String) -> NextStep {
        NextStep(step: step, milestone: milestone, rung: rung, list: list, model: model,
                 command: target(step, milestone: milestone, rung: rung, list: list), why: why)
    }

    public static func decide(_ input: Input) -> NextStep {
        guard let roadmap = input.roadmap else {
            return input.hasOverview
                ? make("roadmap", "opus", why: "system design exists; no roadmap yet")
                : make("design", "opus", why: "no system design and no roadmap")
        }
        if !roadmap.milestones.isEmpty { return decide(milestones: roadmap, input) }
        // A `## Milestones` section whose lines all fail to parse must not read as an older roadmap: that route would
        // plan or fold back by the legacy rules and could send the owner to a re-plan that is not needed.
        let unparsed = roadmap.unparsedMilestoneLines
        if !unparsed.isEmpty {
            return make("replan", "opus", why: "\(unparsed.count) line(s) in ## Milestones do not parse (roadmap lint names them); fix their format first: - M<id> (<name>) — <outcome>; touches: <subsystems> [<status>]")
        }
        // tasklist-run and design-session write handoff notes whatever the roadmap's format, so an older roadmap reads them too.
        if let waiting = waitingState(roadmap, input) { return waiting }
        if let rung = roadmap.ladder.first(where: { $0.status.hasPrefix("in progress") }) {
            return decide(rung: rung.id, input)
        }
        return refactorOrNext(roadmap, input)
    }

    /// No rung in progress on an older roadmap: an open refactor list, else the first planned rung, else re-plan or finish.
    static func refactorOrNext(_ roadmap: Roadmap, _ input: Input) -> NextStep {
        // The re-plan puts accepted refactor tasks in their own list, run before the next rung is planned.
        if let (file, tasks) = openLists(input, prefix: "Tasklist-Refactor-").first {
            let path = input.docDir == "." ? file.name : input.docDir + "/" + file.name
            let run = make("run", orchestrator(tasks), list: path, why: "\(file.name) has \(tasks.count) open task(s), placed before the next rung; /rung plan goes past it")
            return run
        }
        if roadmap.milestones.isEmpty, let rung = roadmap.ladder.first(where: { $0.status.hasPrefix("planned") }) {
            return make("plan", "opus", rung: rung.id, why: "\(rung.id) is the first planned rung")
        }
        // Deferred and horizon rungs are not finished work: the re-plan brings one back, details one, or drops them.
        let deferred = roadmap.ladder.filter { $0.status.hasPrefix("deferred") }.map(\.id)
        let horizon = roadmap.ladder.filter { $0.status == "horizon" }.map(\.id)
        if !deferred.isEmpty || !horizon.isEmpty {
            let parts = [("deferred", deferred), ("horizon", horizon)].filter { !$0.1.isEmpty }.map { "\($0.0): \($0.1.joined(separator: " "))" }
            let replan = make("replan", "opus", why: "no planned rung; " + parts.joined(separator: "; ") + "; bring one back, detail one, or drop them")
            return replan
        }
        let done = make("finished", "opus", why: "no planned, deferred or horizon rung left; extend the ladder or stop")
        return done
    }

    static func decide(rung id: String, _ input: Input) -> NextStep {
        let lists = input.tasklists.filter { $0.name.hasPrefix("Tasklist-\(id)-") && $0.name.hasSuffix(".md") }
        let brief = input.briefs.first { $0.name.hasPrefix("Rung-\(id)-") && $0.name.hasSuffix(".md") }
        let briefStatus = brief.flatMap { b in
            b.text.split(separator: "\n", omittingEmptySubsequences: false)
                .first { $0.hasPrefix("Status:") }.map { $0.dropFirst(7).trimmingCharacters(in: .whitespaces).lowercased() }
        } ?? ""
        if let (file, tasks) = openLists(input, prefix: "Tasklist-\(id)-").first {
            let path = input.docDir == "." ? file.name : input.docDir + "/" + file.name
            let waiting = tasks.filter { $0.user && $0.blocked == nil }.map(\.id)
            let blocked = tasks.filter { $0.blocked != nil }.map(\.id)
            let run = make("run", orchestrator(tasks), rung: id, list: path, why: "\(file.name) has \(tasks.count) open task(s)")
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
            return make("plan", "opus", rung: id, why: "\(id) is in progress; \(reason)")
        }
        let last = lists.max { $0.modified < $1.modified }!
        let path = input.docDir == "." ? last.name : input.docDir + "/" + last.name
        if briefStatus.hasPrefix("folded back") {
            let replan = make("replan", "opus", rung: id, list: path, why: "\(id) folded back; roadmap still in progress")
            return replan
        }
        return make("close", "opus", rung: id, list: path, why: "\(last.name) closed; " + (brief == nil ? "no brief to fold back" : "brief not folded back"))
    }

    /// Live (not `Completed/`) lists with the prefix that have open tasks, newest first. A task under a closed heading is
    /// not open work: `tasklist-run` will not pick it, so it must not hold a rung in `run`.
    static func openLists(_ input: Input, prefix: String) -> [(File, [TaskItem])] {
        input.tasklists.filter { !$0.completed && $0.name.hasPrefix(prefix) && $0.name.hasSuffix(".md") }
            .map { file -> (File, [TaskItem]) in
                let list = Tasklist(text: file.text)
                return (file, list.tasks.filter { $0.mark == .open && list.closedHeading(for: $0) == nil })
            }
            .filter { !$0.1.isEmpty }.sorted { $0.0.modified > $1.0.modified }
    }

    /// Opus when more than half the open tasks are `heavy`, as `tasklist-run`'s "Orchestrator model" says.
    static func orchestrator(_ tasks: [TaskItem]) -> String {
        tasks.filter { $0.fields["model"]?.lowercased().hasPrefix("heavy") == true }.count * 2 > tasks.count ? "opus" : "sonnet"
    }

    public var rendered: String {
        var rows = ["step: \(step)"]
        if let milestone { rows.append("milestone: \(milestone)") }
        if let rung { rows.append("rung: \(rung)") }
        if let list { rows.append("list: \(list)") }
        if let handoff { rows.append("handoff: \(handoff)") }
        rows += ["model: \(model)", "command: \(command)", "why: \(why)"]
        return rows.joined(separator: "\n")
    }
}
