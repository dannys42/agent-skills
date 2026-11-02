import Foundation

/// Routing for a roadmap with a `## Milestones` section, as `roadmap-plan-next-rung` defines it: milestone planning,
/// a rung's run (which folds itself back), an escalation review, and milestone close. Routes are internal labels the
/// `/rung` skill dispatches; the owner only ever types `/rung`.
extension NextStep {
    /// Seam for waiting state that outranks the roadmap (T30): a wait-point handoff note naming the step that resumes,
    /// and the re-plan signal a design session leaves when it changed a `settled` item or added current-milestone
    /// structure (route `replan`). Neither is read yet; return a step here once they are defined.
    static func waitingState(_ roadmap: Roadmap, _ input: Input) -> NextStep? { nil }

    /// A milestone-flow step; `command` is the `roadmap-plan-next-rung` alias that runs it, or `tasklist-run` for a list.
    static func route(_ step: String, _ model: String, _ command: String, milestone: Milestone?, rung: String? = nil, list: String? = nil, why: String) -> NextStep {
        NextStep(step: step, milestone: milestone?.id, rung: rung, list: list, model: model, command: command, why: why)
    }

    static func decide(milestones roadmap: Roadmap, _ input: Input) -> NextStep {
        if !input.hasOverview {
            var design = make("design", "opus", why: "the roadmap has milestones but there is no system design (SystemDesign/Overview.md)")
            design.command = "/rung design"
            return design
        }
        if let waiting = waitingState(roadmap, input) { return waiting }
        func path(_ file: File) -> String { input.docDir == "." ? file.name : input.docDir + "/" + file.name }
        func named(_ id: String) -> String { roadmap.named(id) ?? id }

        guard let m = roadmap.currentMilestone else {
            let next = roadmap.milestones.first { $0.status.hasPrefix("planned") }
            let open = roadmap.ladder.filter { $0.status.hasPrefix("planned") || $0.status.hasPrefix("in progress") }
            if next != nil || !open.isEmpty {
                let why = "no current milestone; " + (next.map { "\($0.named) is the next planned one" } ?? "open rungs: " + open.map(\.id).joined(separator: " "))
                return route("replan", "opus", "/rung replan", milestone: next, why: why)
            }
            return refactorOrNext(roadmap, input)
        }

        // The current milestone's rungs: those tagged with it, and any open ladder rung tagged with none.
        let rungs = roadmap.ladder.filter { r in
            guard r.status != "horizon" else { return false }
            if let tag = roadmap.milestone(of: r) { return tag == m.id }
            return r.status.hasPrefix("planned") || r.status.hasPrefix("in progress")
        }
        func isOpen(_ r: LadderRung) -> Bool { r.status.hasPrefix("planned") || r.status.hasPrefix("in progress") }
        func lists(_ id: String) -> [File] { input.tasklists.filter { $0.name.hasPrefix("Tasklist-\(id)-") && $0.name.hasSuffix(".md") } }

        let unplanned = rungs.filter { isOpen($0) && lists($0.id).isEmpty }
        if !unplanned.isEmpty {
            return route("milestone-plan", "opus", "/roadmap-plan-next-rung plan \(m.id)", milestone: m,
                         why: "\(m.named): \(unplanned.map { named($0.id) }.joined(separator: ", ")) \(unplanned.count == 1 ? "has" : "have") no tasklist")
        }
        if let r = rungs.first(where: { roadmap.escalation(of: $0.id) != nil }) {
            return route("escalation", "opus", "/roadmap-plan-next-rung escalation \(r.id)", milestone: m, rung: r.id,
                         why: "\(named(r.id)): the automatic fold-back escalated on \(roadmap.escalation(of: r.id) ?? "")")
        }

        let inProgress = rungs.first { $0.status.hasPrefix("in progress") }
        if let r = inProgress { return rungStep(r, m, input, roadmap) }
        // Lists placed outside the ladder run before the next rung starts: a re-plan's refactor list, a close's fix list,
        // an accepted demo's follow-ups.
        let side = openLists(input, prefix: "Tasklist-Refactor-") + openLists(input, prefix: "Tasklist-M")
            .filter { $0.0.name.dropFirst("Tasklist-M".count).first?.isNumber == true }
        if let (file, tasks) = side.sorted(by: { $0.0.modified > $1.0.modified }).first {
            return route("run", orchestrator(tasks), "/tasklist-run " + path(file), milestone: m, list: path(file),
                         why: "\(file.name) has \(tasks.count) open task(s), run before the next rung")
        }
        if let r = rungs.first(where: { $0.status.hasPrefix("planned") }) { return rungStep(r, m, input, roadmap) }
        // risk-first-roadmap's re-plan: with no rung planned, bring back a deferred rung, detail the next horizon item or
        // drop it; only with none left does the milestone go to close. A milestone with no rungs at all is re-planned too.
        let tagged = roadmap.ladder.filter { roadmap.milestone(of: $0) == m.id }
        let deferred = tagged.filter { $0.status.hasPrefix("deferred") }.map { named($0.id) }
        let horizon = tagged.filter { $0.status == "horizon" }.map { named($0.id) }
        if !deferred.isEmpty || !horizon.isEmpty {
            let parts = [("deferred", deferred), ("horizon", horizon)].filter { !$0.1.isEmpty }.map { "\($0.0): \($0.1.joined(separator: ", "))" }
            return route("replan", "opus", "/rung replan", milestone: m,
                         why: "no planned rung in \(m.named); " + parts.joined(separator: "; ") + "; bring one back, detail one, or drop them")
        }
        if rungs.isEmpty {
            return route("replan", "opus", "/rung replan", milestone: m, why: "\(m.named) has no rungs; add the rungs that reach its outcome")
        }
        let why = m.close.map { "every rung of \(m.named) is finished; the close resumes after: \($0)" }
            ?? "every rung of \(m.named) is finished and no fix or follow-up list is open"
        return route("milestone-close", "opus", "/roadmap-plan-next-rung milestone-close \(m.id)", milestone: m, why: why)
    }

    /// The step for the rung being built (`in progress`, else the first `planned` one, which the run starts): run an open
    /// list, re-enter an unfinished fold-back, or send a rung whose lists are all closed and moved to an escalation review.
    static func rungStep(_ r: LadderRung, _ m: Milestone, _ input: Input, _ roadmap: Roadmap) -> NextStep {
        let name = roadmap.named(r.id) ?? r.id
        func path(_ file: File) -> String { input.docDir == "." ? file.name : input.docDir + "/" + file.name }
        if let (file, tasks) = openLists(input, prefix: "Tasklist-\(r.id)-").first {
            let waiting = tasks.filter { $0.user && $0.blocked == nil }.map(\.id)
            let blocked = tasks.filter { $0.blocked != nil }.map(\.id)
            var run = route("run", orchestrator(tasks), "/rung run \(r.id)", milestone: m, rung: r.id, list: path(file),
                            why: "\(name): \(file.name) has \(tasks.count) open task(s)")
            guard waiting.count + blocked.count == tasks.count else { return run }
            var parts: [String] = []
            if !waiting.isEmpty { parts.append("USER tasks waiting: " + waiting.joined(separator: ", ")) }
            if !blocked.isEmpty { parts.append("blocked: " + blocked.joined(separator: ", ")) }
            run.step = "user"
            run.why = "\(name): " + parts.joined(separator: "; ")
            return run
        }
        // auto-fold-back.md: a closed rung list still in <DocDir>/ means the fold-back did not finish; the next run re-enters it.
        let unfinished = input.tasklists.filter {
            !$0.completed && $0.name.hasPrefix("Tasklist-\(r.id)-") && $0.name.hasSuffix(".md") && !$0.name.hasSuffix("-Tidy.md")
        }.max { $0.modified < $1.modified }
        if let file = unfinished {
            return route("run", "sonnet", "/rung run \(r.id)", milestone: m, rung: r.id, list: path(file),
                         why: "\(name): \(file.name) is closed but not moved to Completed/, so its fold-back did not finish; tasklist-run re-enters it")
        }
        // Every list is closed and moved, yet the fold-back did not set the rung done: Opus judges the unfinished fold-back.
        return route("escalation", "opus", "/roadmap-plan-next-rung escalation \(r.id)", milestone: m, rung: r.id,
                     why: "\(name) is \(r.status) with every list closed and moved to Completed/, but the fold-back did not set it done")
    }
}
