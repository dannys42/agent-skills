# Roadmap file format and worked example

File: `<DocDir>/Roadmap-<Topic>.md`.

```markdown
# Roadmap: <Project name>

Design: <DocDir>/SystemDesign/Overview.md (or a legacy Design-<Topic>.md)
Build boundaries: <"decided in L1's brief", or "single target">
Quality: <DocDir>/Quality/Status.md (code-quality-pass; omit until the first pass)
Parked ideas: <DocDir>/ParkedIdeas-<Topic>.md (omit until the first one)
Log: <DocDir>/Roadmap-<Topic>-Log.md (omit until the first move)
Updated: <date>

## Milestones
- M1 (<name>) — <outcome in the owner's words> `<owner|proposed>`; touches: <subsystems> [current]
  - Exit: <what the owner checks at the demo>
- M2 (<name>) — <outcome> `<owner|proposed>`; touches: <subsystems> [planned]
  - Additive check: <verdict from the system design>
- M3 (<name>) — <one line> `<owner|proposed>` [planned]

## Ladder (one line per rung, in order)
1. L1 — <question> [status]
...

## Rungs (detailed)
### L1: ...
...

(Requirement coverage lives in the system design's traceability table. Only a legacy design without one gets a small FR/NFR-to-rung table here.)

## Horizon (not yet detailed)
- L6 — <one-line question> (M1)

## Decide after it runs
- <question> — settle at <RungId or MilestoneId> (<name>)

## Learning log
- L1 (done, <date>): <what we learned, measured answer>
```

Ladder line format (the `roadmap` tool and `lint` read exactly this):

`<n>. L<id> — <question> [<status>]`, optionally followed by ` detail: <path>` for a finished rung whose section moved out.

- `<status>` is one of `planned`, `in progress`, `done`, `failed`, `changed`, `obsolete`, `deferred`; a reason of a few words may follow after `:` or `;` (`[failed: fallback taken]`); the line stays under about 400 characters
- `<n>` is plain digits and only a position, nothing cites it. A new rung, wherever it sits in the order, takes the next unused ID (`L48`, not `L25a`) and its line goes in place; renumber the `<n>` of the lines after it (never `25a.` or `25.1`: such a line is not read, and the rung is skipped without a warning)
- the bracket is the last thing on the line, apart from a `detail:` pointer: `1. L1 — Can I run an app? [done] detail: Completed/Roadmap-X-Rungs.md`
- no other brackets after the status, no status outside the brackets, one line per rung
- horizon rungs are `- L6 — <question>` bullets under `## Horizon`, not on the ladder, one line each (the milestone and a `ParkedIdeas` pointer may follow the question)
- milestone lines are exactly ``- M<id> (<name>) — <outcome> `<mark>`; touches: <subsystems> [<status>]``, in the owner's order top to bottom. `<mark>` is always present: `owner` once the owner wrote or accepted the outcome, else `proposed`. `; touches: <subsystems>` (comma-separated subsystem names) is required on the current and next milestone and omitted on later ones, which end `` `<mark>` [<status>]``. `<status>` is `planned`, `current`, `done`, `deferred` or `dropped`, last on the line. The current milestone adds an `Exit:` sub-bullet, the next one an `Additive check:` sub-bullet; later ones stay one line. During milestone close the current milestone also carries a `Close: <step> (<date>)` sub-bullet recording the close's progress (`roadmap-plan-next-rung` defines the values); close removes it once the ruling is in the learning log, and on a rejected demo. The `roadmap` tool does not read them yet

## Worked example: printable Sudoku app for macOS

The system design's milestones: M1 prints one classic puzzle (the first pillar: app, grid, digits and generator at minimal depth), M2 adds grid sizes, M3 keeps a library. Risks for M1, ranked: generator correctness and speed (high impact, high uncertainty); fidelity of drawn and printed text (medium, medium); document-based app shape (medium, low). Nothing is on a clock.

### Milestones

- M1 (print a puzzle) — I can print a playable 9×9 Sudoku from the app. `owner`; touches: Document_App, Grid_View, Generator, Print_Export [current]
  - Exit: File > Print gives a page whose puzzle has exactly one solution, readable at arm's length.
- M2 (any size) — I can choose a grid size and print a puzzle of it. `proposed`; touches: Generator, Size_Picker [planned]
  - Additive check: yes, the generator takes the box size as a parameter from L4 (fixed 3×3 boxes) on.
- M3 (puzzle library) — I can keep the puzzles I made and print them again. `proposed` [planned]

### Ladder

1. L1 — Can I build and run the most basic document-based macOS app? [planned]
2. L2 — Can I draw the most basic repeated element, a fixed 9×9 grid? [planned]
3. L3 — Do I control the drawing finely enough: fonts, size, color, style, readable? [planned]
4. L4 — Can I generate a full 9×9 solution with 3×3 boxes, with no UI? [planned]
5. L5 — Can I see the generator's result on the grid? [planned]
6. L6 — Can the generator remove cells so one solution remains, and print it? [planned]

Every rung serves M1. M2 and M3 have no rungs; each gets them at its own milestone planning.

### Why this order

- M1 is the thinnest end-to-end slice: one fixed size, one generator, no difficulty levels, no saving. Sizes and the library are later lines, and M2's additive check holds because L4 takes the box size as a parameter.
- L1–L5 are shape, each able to change the UI approach or the generator's design; L5 is the first end-to-end run. L4 is the biggest unknown and needs no UI, so it may go ahead of L2; the owner decides.

### Detailed rungs (L1 to L3 shown; L4 to L6 are written the same way)

```markdown
### L1: Build and run a document-based macOS app
Question: Can I build and run the most basic app of the right shape?
Slice: A document-based SwiftUI macOS app with a blank window that opens, saves, and reopens a document.
Done when: `xcodebuild build` succeeds, the app launches, File > New opens a window, and Save then Open round-trips an empty document.
De-risks: R-skeleton, R-documents
Depends on: none
Milestone: M1
Touches: Document_App
Class: shape
If no: Fall back to a single-window app and revisit documents later; record why in the system design.

### L2: Draw a fixed 9x9 grid
Question: Can I draw on a canvas?
Slice: Replace the blank window content with a 9×9 grid drawn at a fixed size, box lines heavier.
Done when: The grid appears with even, crisp lines at 1× and 2× scale; a screenshot or a snapshot test shows it.
De-risks: R-drawing
Depends on: L1
Milestone: M1
Touches: Grid_View
Class: shape
If no: Try Core Graphics via an AppKit view instead of SwiftUI Canvas.

### L3: Control text in the grid
Question: Do fonts work, and is the size, color, and style legible?
Slice: Fill the grid with fixed digits 1–9 in the chosen font; export one page as PDF.
Done when: The PDF shows centered, readable digits; a printed page is checked by eye.
De-risks: R-text, R-print
Depends on: L2
Milestone: M1
Touches: Grid_View, Print_Export
Class: shape
If no: Change font or draw digits as paths; record the decision in the system design.
```

### Decide after it runs

- Digit font weight on paper — settle at L3 (text in the grid) after a printed page.
- How many givens to leave — settle at L6 (playable puzzle) after printing a few.

## Another shape: a CLI or service (not Apple-specific)

The same method yields a different map. A service that archives data its source keeps only for a while: M1 (data in one place) collects it, M2 (see it) reads it, and the analysis the project is for comes after. Inside M1: L1 builds and runs hello-world with CI; L2 reads one real input end to end into one table; L3 proves the risky integration against the real service; L4 keeps the collection current. Ingestion is clock work, so it sits in the first milestone; an early "is there enough data to analyse?" question is a read-only spike over collected data, not the start of the analysis. What stays the same is the rule, not the content.
