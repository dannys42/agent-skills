# Rung brief template

File: `<DocDir>/SystemDesign/Rung-<RungId>-<ShortRungDescription>.md`, written at milestone planning for every rung of the milestone. The next rung's brief is complete, about a page; the others are thin (see [A thin brief](#a-thin-brief)). Every section answers a question the task list would otherwise guess at; a section with nothing to say is left out or reads "none". Cite the system design's agreed seams and decisions by qualified ID; never restate them.

The example is rung L3 of a printable Sudoku app for macOS. Its system design names the components App Shell, Puzzle Document, Grid View, Puzzle Generator (a subsystem, `Doc: pending`), and PDF Exporter; L1 and L2 built the app shell and an empty grid. L3 works only at the system design's top level, so it touches one design doc.

IDs from design docs are cited qualified (`Overview:FR2`); the brief's own rung-local decisions and assumptions use bare IDs local to the brief.

## Template with example

````markdown
# Rung L3: Grid Text Rendering

Roadmap: ../Roadmap-Sudoku_Printer.md (L3)
System design: Overview.md
Status: draft | agreed (<date>) | folded back (<date>)
Base: <short sha of HEAD when the run starts the rung; written by the run>

## Question and slice
Question: Do fonts work, and is the size, color, and style legible at screen and print scale?
Slice: Fill the grid with fixed digits 1–9 in the chosen font; export one page as PDF.
Done when (roadmap): The PDF shows centered, readable digits; a printed page is checked by eye.

## Scope for this rung
- In this rung: digits drawn centered in Grid View cells; one font, two weights (given vs. entered); File > Export as PDF for a single US Letter page.
- In this version, not this rung: A4 and page-size choice (later rung); the boundary is that the exporter takes page size as a parameter but the UI offers none.
- Out: pencil marks and color themes (not this version).

## Requirements touched
- Overview:FR2 (must, print a puzzle): proves single-page vector output; page-size choice not yet.
- Overview:NFR1 (digits legible at 9 mm cells when printed): measured here by a printed check.

## Design docs touched
| Doc | What changes | Depth before → after |
| --- | --- | --- |
| Overview.md | PDF Exporter interface; new `GridSnapshot` edge; decision Overview:D3 | PDF Exporter sketched → designed |

## Components and interfaces
```mermaid
flowchart LR
  classDef sketched stroke-dasharray: 5 5
  classDef designed stroke-width:1px
  classDef built stroke-width:3px
  classDef touched fill:#fff3b0,stroke:#b58900
  AppShell["App Shell"]
  GridView["Grid View"]
  PDFExporter["PDF Exporter"]
  AppShell -->|Export command| PDFExporter
  PDFExporter -->|renders| GridView
  class AppShell,GridView built
  class PDFExporter designed
  class GridView,PDFExporter touched
```

| Component | Change in this rung | Depth before → after |
| --- | --- | --- |
| Grid View | Draws a `CellText` (digit, weight) per cell, centered on the cell's optical center | built (stays built) |
| PDF Exporter | New. `export(grid: GridSnapshot, page: PageSize) -> Data`, vector only, no rasterising | sketched → designed |

Interface crossing the boundary: `GridSnapshot` (cell values and weights, no view state), so the exporter never reaches into SwiftUI state.

## Decisions
| ID | Decision | Status | How resolved |
| --- | --- | --- | --- |
| Overview:D3 | Render the PDF by drawing Grid View's shapes into a Core Graphics PDF context, not by printing the view | settled | default; vector output and no print dialog needed; recorded in the Overview because it fixes a component boundary |
| A1 | SF Pro is acceptable as the numeral font | proposed | rung-local; user to confirm on the printed page |

## Verification
- `xcodebuild -scheme SudokuPrinter test` passes, including a snapshot test of a filled grid at 1× and 2×.
- Regression test: `GridTextTests.testDigitsDrawn` fails on the base (no digits drawn) and passes after.
- Export writes a one-page PDF; `pdfinfo` reports one page, Letter size.
- USER: print the page; every digit is readable at arm's length and centered by eye.

## Guard rails for the task list
- Do not add a page-size picker or A4 support; the exporter takes `PageSize` but only `.letter` is wired.
- Do not touch Puzzle Generator or Puzzle Document; digits are hard-coded for this rung.

## Fold-back
- [ ] Overview: PDF Exporter `designed → built` if the export test and printed check pass; add the `GridSnapshot` edge to the diagram.
- [ ] Overview: confirm Overview:D3 matches what was built; if A1 held, record the font as an Overview decision.
- [ ] Overview risk register: retire Overview:R2 (text fidelity) if the printed check passes; otherwise record what failed.
- [ ] Overview traceability (the doc that owns FR2): FR2 partially proven by L3 (single page).
````

## Notes

- **Question and slice** are copied from the roadmap, not rewritten. If planning shows they are wrong, fix the roadmap and say so.
- **Scope for this rung** stops an implementer from finishing the milestone instead of the rung.
- **Components and interfaces** list only what the rung creates or changes; neighbours appear only to explain a touched edge. Classes are in [diagrams.md](diagrams.md).
- **Design docs touched** lists every doc the rung changes, so planning and fold-back edit those and no others.
- **Decisions** hold rung-local choices. One that changes a component, a seam or technology direction is recorded in the design doc that owns it and cited qualified here.
- **Verification** items carry the command or action, so they drop straight into `Done when`. One is always a regression test that fails without the rung's change.
- **Outcome details** (thresholds, exact output, polish) go on the roadmap's "decide after it runs" list under this rung, not in the brief.
- **Fold-back** is written now, while the intent is clear, and ticked by the automatic fold-back: every design-doc change the rung should cause if it succeeds, grouped by doc.
- For rung 1 with more than one build boundary, add a **Build targets** section after Components.

## A thin brief

Every rung after the next one. Seams, names and decisions were agreed at milestone planning, so the brief points at them:

```markdown
# Rung L4: Puzzle Generation

Roadmap: ../Roadmap-Sudoku_Printer.md (L4) · System design: Overview.md · Status: agreed (<date>)
Question and slice: as in the roadmap.
Scope: generate one valid puzzle per difficulty; no difficulty rating UI (L6).
Uses: Overview:D5 (Puzzle Generator as a Swift package), seam `generate(difficulty:) -> Puzzle` (Puzzle_Generator:Contract).
Verification: `swift test --package-path PuzzleGenerator`; regression test `GeneratorTests.testUniqueSolution` fails on the base.
Guard rails: do not touch Grid View or PDF Exporter.
Fold-back: Puzzle_Generator: Grid Solver and Cell Remover `designed → built`; retire Overview:R3 if uniqueness holds.
```

## A rung that works inside a subsystem

L4 designs the generator's internals. Puzzle Generator is a separate build target, so it meets a subsystem trigger, and its doc is created in subsystem mode at milestone planning, with only what L4 needs. The brief's diagram draws the generator's inner components and keeps App Shell as one box; the system design keeps one Puzzle Generator box.

```markdown
## Design docs touched
| Doc | What changes | Depth before → after |
| --- | --- | --- |
| Puzzle_Generator.md | New (subsystem mode): Contract, Grid Solver and Cell Remover designed, Difficulty Rater sketched | new |
| Overview.md | Puzzle Generator row: `Doc` link, Contract summary; subsystem index | Puzzle Generator sketched → designed |
```
