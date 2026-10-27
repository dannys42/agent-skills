# Roadmap file format and worked example

File: `<DocDir>/Roadmap-<Topic>.md`.

```markdown
# Roadmap: <Project name>

Design: <DocDir>/SystemDesign/Overview.md (or a legacy Design-<Topic>.md)
Build boundaries: <"decided in L1's brief", or "single target">
Quality: <DocDir>/Quality/Status.md (code-quality-pass; omit until the first pass)
Parked ideas: <DocDir>/ParkedIdeas-<Topic>.md (omit until the first one)
Updated: <date>

## Milestones
- M1 — <an outcome the owner can use>; needs: <capabilities> [current]
- M2 — <outcome>; needs: <capabilities> [planned]

## Ladder (one line per rung, in order)
1. L1 — <question> [status]
...

## Rungs (detailed)
### L1: ...
...

(Requirement coverage lives in the Overview's traceability table. Only a legacy design without one gets a small FR/NFR-to-rung table here.)

## Horizon (not yet detailed)
- L6 — <one-line question>

## Learning log
- L1 (done, <date>): <what we learned, measured answer>
```

Ladder line format (the `roadmap` tool and `lint` read exactly this):

`<n>. L<id> — <question> [<status>]`, optionally followed by ` detail: <path>` for a finished rung whose section moved out.

- `<status>` is one of `planned`, `in progress`, `done`, `failed`, `changed`, `obsolete`, `deferred`; a reason of a few words may follow after `:` or `;` (`[failed: fallback taken]`); the line stays under about 400 characters
- `<n>` is plain digits and only a position, nothing cites it. A new rung, wherever it sits in the order, takes the next unused ID (`L48`, not `L25a`) and its line goes in place; renumber the `<n>` of the lines after it (never `25a.` or `25.1`: such a line is not read, and the rung is skipped without a warning)
- the bracket is the last thing on the line, apart from a `detail:` pointer: `1. L1 — Can I run an app? [done] detail: Completed/Roadmap-X-Rungs.md`
- no other brackets after the status, no status outside the brackets, one line per rung
- horizon rungs are `- L6 — <question>` bullets under `## Horizon`, not on the ladder, one line each (`M2` and a `ParkedIdeas` pointer may follow the question)
- milestone lines are `- M<id> — <outcome>; needs: <capabilities> [<status>]`, with status `planned`, `current`, `done`, `deferred` or `dropped`; the `roadmap` tool does not read them

## Worked example: printable Sudoku app for macOS

Risks from the design, ranked: generator correctness and speed (high impact, high uncertainty); fidelity of drawing and printed text (medium, medium); document-based app shape (medium, low); arbitrary grid sizes (low, low once the generator is generic). Nothing is on a clock.

### Milestones

- M1 — I can print a playable 3×3 Sudoku; needs: document app, grid drawing, text, generator [current]
- M2 — I can print any grid size I choose; needs: generic generator, size picker [planned]

### Ladder

1. L1 — Can I build and run the most basic document-based macOS app? (M1, shape)
2. L2 — Can I draw the project's most basic repeated element, a fixed 3×3 grid? (M1, shape)
3. L3 — Do I have fine enough control over the drawing: fonts, size, color, style, readable? (M1, shape)
4. L4 — Can I produce the core logic: a Sudoku generator for a 3×3 grid, with no UI? (M1, shape)
5. L5 — Can I see the generator's result on the grid? (M1, shape: the first end-to-end run)
6. L6 — Can the generator produce a playable starting point (cells removed), shown on screen? (M1, breadth)
7. L7 — Does everything hold for a 4×4 grid? (M2, breadth)
8. L8 — Can the user choose arbitrary grid sizes from the UI? (M2, breadth)

(The milestone and class in brackets are for this example; in a roadmap they live in each rung's section.)

### Why this order

- L1–L5 are shape: each could change the UI approach or the generator's design, and L5 is the first end-to-end run. L4 is the biggest unknown and needs no UI, so it may go ahead of L2 if it looks frightening; the user decides.
- L6 completes M1. L7–L8 are breadth for M2: once the generator is generic they are straightforward changes, not unknowns.

### Detailed rungs (first three)

```markdown
### L1: Build and run a document-based macOS app
Question: Can I build and run the most basic app of the right shape?
Slice: A document-based SwiftUI macOS app with a blank window that opens, saves, and reopens a document.
Done when: `xcodebuild build` succeeds, the app launches, File > New opens a window, and Save then Open round-trips an empty document.
De-risks: R-skeleton, R-documents
Depends on: none
Milestone: M1
Class: shape
If no: Fall back to a single-window app and revisit documents later; record why in the design.
Status: planned

### L2: Draw a fixed 3x3 grid
Question: Can I draw on a canvas?
Slice: Replace the blank window content with a 3×3 grid drawn at a fixed size.
Done when: The grid appears with even, crisp lines at 1× and 2× scale; a screenshot or a snapshot test shows it.
De-risks: R-drawing
Depends on: L1
Milestone: M1
Class: shape
If no: Try Core Graphics via an AppKit view instead of SwiftUI Canvas.
Status: planned

### L3: Control text in the grid
Question: Do fonts work, and is the size, color, and style legible?
Slice: Fill the grid with fixed numbers 1–9 in the chosen font; export one page as PDF.
Done when: The PDF shows centered, readable digits; a printed page is checked by eye.
De-risks: R-text, R-print
Depends on: L2
Milestone: M1
Class: shape
If no: Change font or draw digits as paths; record the decision in the Overview.
Status: planned
```

### Horizon

- L4–L6 as listed in the ladder, detailed one at a time after L3 teaches us what the drawing layer can do. L7–L8 stay one line under M2 until M1 is done.

## Another shape: a CLI or service (not Apple-specific)

The same method yields a different ladder: L1 builds and runs hello-world with CI; L2 reads one real input end to end; L3 proves the one risky integration against the real service; L4 adds the core transformation with tests; L5 adds persistence; later rungs add breadth. What stays the same is the rule, not the content: each rung is runnable and answers the biggest unknown reachable from here. If the service archives data its source keeps only for a while, that ingestion is clock work: it starts right after the skeleton and its coverage is finished before features that read the data go deeper. L5's persistence is one table, the one L4 needs; later tables arrive with the rungs that need them.
