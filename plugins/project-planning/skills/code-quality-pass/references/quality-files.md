# Quality files, scout briefs and report shape

## Status.md

`<DocDir>/Quality/Status.md`. Current state only; every line is overwritten, never appended to. The `metrics` tool reads the `Key:` lines, so keep the keys exactly. At most 25 lines; `metrics signals` warns past that.

```markdown
# Code quality status

Every: 5 rungs
Last review: L20 · 48a0287 · 2026-10-18 · [report](Review-2026-10-18.md)
Since review: L21, L22
Triggers pending: none
Deferred: no
Accepted shapes: Runner, Routes, Response, State, Model
Backlog: 3 accepted not yet scheduled, 2 deferred · [report](Review-2026-10-18.md) · [L21](Proposals-L21.md)
```

- `Last review:` is `none`, or `<rung> · <short sha> · <date> · [report](...)`. A baseline that found nothing is `<rung or "pre-roadmap"> · <sha> · <date> · checked, no trigger`.
- `Since review:` lists rungs folded back since then; milestone close appends every rung of the milestone. Past twice `Every`, write a range and a count: `L18–L31 (14)`.
- `Triggers pending:` the trigger names milestone close's `metrics signals` saw, comma-separated; cleared at the next review.
- `Deferred:` `no`, or `<date>, <reason>`: the latest deferral only.
- `Accepted shapes:` file-name families (the last CamelCase word of the file name) a review judged to be deliberate conventions.
- `Backlog:` counts and a link to each live report or Proposals file; never the proposals themselves, and never a count without its link.

## Tier 1 scout brief

Paste this, with the gathered facts, into the scout's prompt:

> You are scouting a behaviour-preserving tidy of the files one rung changed. Base `<sha>`; changed files: `<list>`; review notes: `<lines>`; test command: `<cmd>`; conventions: `<lines or "none">`. Read the diff (`git diff <base> HEAD -- <file>`), and sibling files only by grepping the touched type and function names. Do not edit anything. Report, in this order and nothing else:
> 1. Tidy items, at most 6, ranked by value: `<files> — <what> — <why> — <about N lines> — light|standard — tested: yes|no`. Allowed: naming clarity, idiomatic Swift, file organization, duplication with a sibling that one small extraction removes, a review note, a stale test or doc name, a compiler warning, a finding of the project's existing linter.
> 2. Proposals, one line each: anything that changes behaviour or a public interface beyond a rename, spreads past these files and their call sites, or needs more than about 80 lines.
> 3. Defects: any behaviour bug you saw, with file and line. Do not fix it.
> Rank by long-term value to the codebase, not by how quick the fix is; report a worthwhile item that is too big as a proposal rather than leaving it out.
> Bounded output: `grep -n`, ranged reads, no whole large files. Stop after about 15 tool calls.

## Proposals file

`<DocDir>/Quality/Proposals-<MilestoneId>.md`, written at tidy step 7 from the scout's own lines, unedited, and completed with the user's rulings. Omit it when the scout returned neither proposals nor defects. The re-plan reads it like a review report.

```markdown
# Tidy proposals <MilestoneId> · base <sha> · <date>

## Defects
- TD1 <scout's line, with file:line> — Bug task with a reproducing test first: pending

## Proposals
- TP1 <scout's line> — Kind: refactor-rung|task — Decision: pending
```

`Decision`: `pending`, `accepted (<date>)`, `deferred`, `rejected: <reason>`. The re-plan marks each accepted entry with the rung or task that took it.

## Tier 2 seam card

Each scout returns one card of at most 40 lines for its module:

```markdown
### <Module or directory>
Role: <one line>
Public surface: <main types and entry points, one line each, at most 8>
Depends on: <modules it imports or calls>; used by: <if known>
Repeated shapes: <families of near-identical types or files, with names>
Inconsistencies: <naming, idiom, error handling, return types; each with file:line>
Design-doc mismatch: <where the Overview or subsystem Contract row says otherwise, or "none">
Risky error handling: <catch-alls or try? that can drop data, with file:line>
Candidate defects: <file:line, one line each, or "none">
```

## Tier 2 report

`<DocDir>/Quality/Review-<date>.md`, written by the synthesis agent and completed with the user's rulings.

```markdown
# Code quality review <date>

Scope: <baseline, whole codebase | since L20 (48a0287): modules ...> · Signals: <triggers fired>

## Defects (fix as bug tasks)
- QD1 <title> — <file:line> — <why it can lose or corrupt data, or misbehave> — Decision: pending

## Proposals (tiered)
**Important**

**QR1: Collapse SalesDeriver, ListingChangeDeriver, AnalyticsDeriver behind one `Deriver` protocol.** <one plain sentence on what the code does today>
Why: <test met, a few words> · To settle it: <cheapest check, only when confidence is the issue>
- **<option>** (recommended). Pro: ... Con: ...
- **<option>**. Pro: ... Con: ...

**Notable**
...

**Small**: ...

| ID | Proposal | Kind | Size | Tier | Evidence | Benefit | Risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QR1 | Collapse the three derivers behind one `Deriver` protocol | refactor-rung | M | Important | 3 files, same shape (cards: Ingest) | one place to add a source | touches scheduler hooks | pending |

## Also seen
- <one line each, no ranking>
```

- `Kind`: `refactor-rung`, `task`, `conventions`, `fitness-test`, `accept-shape`.
- `Size`: S (under about 100 lines), M (a rung's worth), L (several rungs; split before scheduling).
- Tiers, the at-most-5 cap on Important, options with a pro and con for every proposal, and the example shape follow `roadmap-plan-next-rung`'s `presenting-for-review.md`; the table is the ranked index and the tier blocks carry the decisions. An `L` size, a public interface, persistence, or a change across several modules usually makes a proposal Important; so does evidence from one card or a benefit that rests on future rungs.
- Ranking is by benefit over the project's life and how fast the problem compounds, not by effort; `Size` informs scheduling only. A large proposal is split, not demoted or dropped.
- At most 10 ranked proposals, each with options and in the table; the rest go to "Also seen" as one line with a default and no options. A proposal deferred last time is re-ranked here, not copied.
- `Decision`: `pending`, `accepted (<date>)`, `deferred`, `rejected: <reason>`.
- Leave out any section with nothing in it.
