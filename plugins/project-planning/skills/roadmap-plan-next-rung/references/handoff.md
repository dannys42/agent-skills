# Handoff note

Where waiting state lives (terms.md, "Next step"). Any step that stops for the owner (a `USER` task, a blocked task, a run ending on a question, an escalation, the milestone demo, unanswered review questions, a design session that makes a re-plan due) writes one, assuming the owner replies days later in a new session that remembers nothing. `roadmap next` reads it ahead of the roadmap and routes the resume; when `/rung` runs the step as a subagent, the note is that subagent's brief.

## Where

One note per waiting point; writing the same waiting point again overwrites it. A tasklist run names its note after the list alone, whatever the route: `<DocDir>/Handoff/Tasklist-L3-Import_Orders.md`. Every other note is `<DocDir>/Handoff/<Route>-<Target>.md`: `escalation-L3.md`, `milestone-close-M2.md`, `replan-<YYYY-MM-DD>.md`.

The notes are scratch, never committed. The first write creates `<DocDir>/Handoff/.gitignore` holding `*`: the directory ignores itself and everything in it, in every clone and worktree that has it, without touching the project's own `.gitignore`. Stage by explicit path as always.

## Header

The tool reads only these lines, at the top (after an optional `# Title`):

```markdown
Route: run | user | escalation | milestone-close | milestone-plan | replan | plan | close
Model: opus | sonnet
Waiting on: <the exact question or action, one line, IDs with their names>
Date: <YYYY-MM-DD>
Rung: <RungId>            (when the route has one)
Milestone: <MilestoneId>  (when the route has one)
List: <DocDir>/Tasklist-<...>.md   (for run and user)
```

`Route` is the step that resumes, as `roadmap next` names it; `Model` the model it needs.

## Body

Short sections, only what a cold reader needs:

- **Done:** what this session did, with the commit SHAs and subjects.
- **Pending:** what waits, and the exact question as the owner saw it, with the options and the recommendation.
- **Decided:** rulings already made this session that are not yet in a committed file.
- **Read first:** the files and sections the resume needs (brief, list, design rows, marker).
- **Tasklist:** for a run, which tasks are done, open, `USER` or `BLOCKED`, and why.

## Consume

The step that resumes reads the note before anything else and deletes it (`rm`; it was never committed) as soon as it has taken the note in: `/rung` when `roadmap next` prints `handoff:`, otherwise the skill started by hand on the same work (`tasklist-run` deletes every note whose `List:` is its list, risk-first-roadmap's re-plan a `replan` note). If the owner answers before the session that wrote the note ends, that session deletes it and carries on. If the resumed step stops for the owner again, it writes a fresh note.

`roadmap next` also skips a note whose waiting point is gone: a `run` or `user` note whose list has no open task outside `Completed/`, a `milestone-close` note whose milestone is not `Close: awaiting demo`, an `escalation` note whose rung has no `Escalation:` marker. `metrics signals` warns about a left-over note: older than 14 days, or without a `Route:` the tool knows.

## Owner reviews

A review note (`Review-<UserTaskId>.md`, the shape of [presenting-for-review.md](presenting-for-review.md)) is that review's handoff: it is committed, because the owner reads it, and starts with one status line, `Status: waiting on the owner's review (<UserTaskId> <name>, <date>); delete this file when the review closes.` The step that applies the owner's rulings deletes it in the same commit.

## The stop message

Short and self-contained: what was done, what waits and the exact question, then `Next: /rung` with the model switch when the resume needs Opus. No per-kind resume command and no handoff path; `/rung` finds it.
