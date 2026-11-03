import Foundation

/// Routing for a roadmap with a `## Milestones` section, as `plan-milestone` defines it: milestone planning,
/// a rung's run (which folds itself back), an escalation review, and milestone close. Routes are internal labels the
/// `/rung` skill dispatches; the owner only ever types `/rung`.
extension NextStep {
    /// Waiting state that outranks the roadmap: the newest live handoff note (references/handoff.md), by `Date:` then file
    /// time. A design session that changed a `settled` item or added current-milestone structure leaves one with
    /// `Route: replan`. Notes with no known route are skipped here; `metrics signals` flags them.
    static func waitingState(_ roadmap: Roadmap, _ input: Input) -> NextStep? {
        let notes = input.handoffs.filter { !$0.completed && $0.name.hasSuffix(".md") }
            .map { ($0, Handoff(text: $0.text)) }.filter { $0.1.knownRoute != nil && stale($0.1, roadmap, input) == nil }
        guard let (file, note) = notes.max(by: { ($0.1.date ?? "", $0.0.modified) < ($1.1.date ?? "", $1.0.modified) }),
              let step = note.knownRoute else { return nil }
        let path = (input.docDir == "." ? "" : input.docDir + "/") + "Handoff/" + file.name
        let opus: Set<String> = ["milestone-plan", "escalation", "milestone-close", "replan", "plan", "close", "design"]
        let model = note.model.flatMap { ["opus", "sonnet", "haiku"].contains($0) ? $0 : nil } ?? (opus.contains(step) ? "opus" : "sonnet")
        let waiting = note.waitingOn.map { "waiting on " + $0 } ?? "a stop waits on the owner"
        return NextStep(step: step, milestone: note.milestone, rung: note.rung, list: note.list, model: model, command: target(step, milestone: note.milestone, rung: note.rung, list: note.list),
                        why: waiting + " (handoff " + (note.date.map { "of \($0)" } ?? "undated") + ")", handoff: path)
    }

    /// Why a note's waiting point is gone, or nil: a run or user note whose list has no open task left in the doc
    /// directory, a milestone-close note whose milestone is not `Close: awaiting demo`, an escalation note whose rung
    /// carries no `Escalation:` marker. Such a note was answered in the session that wrote it; it no longer routes.
    static func stale(_ note: Handoff, _ roadmap: Roadmap, _ input: Input) -> String? {
        switch note.knownRoute {
        case "run", "user":
            guard let list = note.list else { return nil }
            let name = (list as NSString).lastPathComponent
            return openLists(input, prefix: name).contains { $0.0.name == name } ? nil : "\(name) has no open task outside Completed/"
        case "milestone-close":
            guard let id = note.milestone else { return nil }
            let close = roadmap.milestones.first { $0.id == id }?.close ?? ""
            return close.hasPrefix("awaiting demo") ? nil : "\(id) is not awaiting a demo ruling"
        case "escalation":
            guard let id = note.rung else { return nil }
            let inProgress = roadmap.ladder.first { $0.id == id }?.status.hasPrefix("in progress") == true
            if roadmap.escalation(of: id) == nil { return "\(id) carries no escalation marker" }
            return inProgress ? nil : "\(id) is not in progress, so its escalation marker no longer routes"
        default:
            return nil
        }
    }

    /// A milestone-flow step; `command` is its dispatch target.
    static func route(_ step: String, _ model: String, milestone: Milestone?, rung: String? = nil, list: String? = nil, why: String) -> NextStep {
        make(step, model, milestone: milestone?.id, rung: rung, list: list, why: why)
    }

    static func decide(milestones roadmap: Roadmap, _ input: Input) -> NextStep {
        if !input.hasOverview {
            return make("design", "opus", why: "the roadmap has milestones but there is no system design (SystemDesign/Overview.md)")
        }
        if let waiting = waitingState(roadmap, input) { return waiting }
        func path(_ file: File) -> String { input.docDir == "." ? file.name : input.docDir + "/" + file.name }
        func named(_ id: String) -> String { roadmap.named(id) ?? id }

        guard let m = roadmap.currentMilestone else {
            let next = roadmap.milestones.first { $0.status.hasPrefix("planned") }
            let open = roadmap.ladder.filter { $0.status.hasPrefix("planned") || $0.status.hasPrefix("in progress") }
            if next != nil || !open.isEmpty {
                let why = "no current milestone; " + (next.map { "\($0.named) is the next planned one" } ?? "open rungs: " + open.map(\.id).joined(separator: " "))
                return route("replan", "opus", milestone: next, why: why)
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
            return route("milestone-plan", "opus", milestone: m,
                         why: "\(m.named): \(unplanned.map { named($0.id) }.joined(separator: ", ")) \(unplanned.count == 1 ? "has" : "have") no tasklist")
        }
        if let r = rungs.first(where: { $0.status.hasPrefix("in progress") && roadmap.escalation(of: $0.id) != nil }) {
            return route("escalation", "opus", milestone: m, rung: r.id,
                         why: "\(named(r.id)): the automatic fold-back escalated on \(roadmap.escalation(of: r.id) ?? "")")
        }

        let inProgress = rungs.first { $0.status.hasPrefix("in progress") }
        if let r = inProgress { return rungStep(r, m, input, roadmap) }
        // Lists placed outside the ladder run before the next rung starts: a re-plan's refactor list, a close's fix list,
        // an accepted demo's follow-ups.
        let side = openLists(input, prefix: "Tasklist-Refactor-") + openLists(input, prefix: "Tasklist-M")
            .filter { $0.0.name.dropFirst("Tasklist-M".count).first?.isNumber == true }
        if let (file, tasks) = side.sorted(by: { $0.0.modified > $1.0.modified }).first {
            return route("run", orchestrator(tasks), milestone: m, list: path(file),
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
            return route("replan", "opus", milestone: m,
                         why: "no planned rung in \(m.named); " + parts.joined(separator: "; ") + "; bring one back, detail one, or drop them")
        }
        if rungs.isEmpty {
            return route("replan", "opus", milestone: m, why: "\(m.named) has no rungs; add the rungs that reach its outcome")
        }
        let why = m.close.map { "every rung of \(m.named) is finished; the close resumes after: \($0)" }
            ?? "every rung of \(m.named) is finished and no fix or follow-up list is open"
        return route("milestone-close", "opus", milestone: m, why: why)
    }

    /// The step for the rung being built (`in progress`, else the first `planned` one, which the run starts): run an open
    /// list, re-enter an unfinished fold-back, or send a rung whose lists are all closed and moved to an escalation review.
    static func rungStep(_ r: LadderRung, _ m: Milestone, _ input: Input, _ roadmap: Roadmap) -> NextStep {
        let name = roadmap.named(r.id) ?? r.id
        func path(_ file: File) -> String { input.docDir == "." ? file.name : input.docDir + "/" + file.name }
        if let (file, tasks) = openLists(input, prefix: "Tasklist-\(r.id)-").first {
            let waiting = tasks.filter { $0.user && $0.blocked == nil }.map(\.id)
            let blocked = tasks.filter { $0.blocked != nil }.map(\.id)
            var run = route("run", orchestrator(tasks), milestone: m, rung: r.id, list: path(file),
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
            return route("run", "sonnet", milestone: m, rung: r.id, list: path(file),
                         why: "\(name): \(file.name) is closed but not moved to Completed/, so its fold-back did not finish; tasklist-run re-enters it")
        }
        // Every list is closed and moved, yet the fold-back did not set the rung done: Opus judges the unfinished fold-back.
        return route("escalation", "opus", milestone: m, rung: r.id,
                     why: "\(name) is \(r.status) with every list closed and moved to Completed/, but the fold-back did not set it done")
    }
}
