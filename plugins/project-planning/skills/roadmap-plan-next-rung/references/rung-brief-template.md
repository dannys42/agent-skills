# Rung brief template

File: `<DocDir>/SystemDesign/Rung-<RungId>-<ShortRungDescription>.md`. About a page. Every section answers a question the task list would otherwise guess at; leave out a section that has nothing to say, with a one-line "none" rather than a placeholder.

The example is rung L3 of a printable Sudoku app for macOS. Its Overview names the components App Shell, Puzzle Document, Grid View, Puzzle Generator (a subsystem, `Doc: pending`), and PDF Exporter; L1 and L2 built the app shell and an empty grid. L3 works only at the Overview's level, so it touches one design doc.

IDs from design docs are cited qualified (`Overview:FR2`); the brief's own rung-local decisions and assumptions use bare IDs local to the brief.

## Template with example

````markdown
# Rung L3: Grid Text Rendering

Roadmap: ../Roadmap-Sudoku_Printer.md (L3)
Overview: Overview.md
Status: draft | agreed (<date>) | folded back (<date>)
Base: <short sha of HEAD when the tasks were handed off>

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
| Overview:D3 | Render the PDF by drawing Grid View's shapes into a Core Graphics PDF context, not by printing the view | accepted | default; vector output and no print dialog needed; recorded in the Overview because it fixes a component boundary |
| A1 | SF Pro is acceptable as the numeral font | assumed | rung-local; user to confirm on the printed page |

## Verification
- `xcodebuild -scheme SudokuPrinter test` passes, including a snapshot test of a filled grid at 1× and 2×.
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

- **Question and slice** are copied from the roadmap, not rewritten, so the brief and the ladder cannot disagree. If planning shows they are wrong, fix the roadmap and say so.
- **Scope for this rung** is the most valuable section for the task list: it stops an implementer from finishing the version instead of the rung.
- **Components and interfaces** list only what the rung creates or changes. Neighbours appear in the diagram only when needed to understand a touched edge. See [diagrams.md](diagrams.md) for the classes.
- **Design docs touched** lists every design doc the rung changes, so step 5 and fold-back edit those and no others. A rung may span several subsystems.
- **Decisions** may hold rung-local choices that never reach a design doc. A decision that changes a component, a boundary between components, or technology direction is recorded in the design doc that owns it, with that doc's next ID, and cited qualified here.
- **Verification** items are checks with the command or action, so they drop straight into `Done when` and `Verify` fields.
- **Fold-back** is written now, while the intent is clear, and ticked at fold-back time. It lists every design-doc change the rung should cause if it succeeds, grouped by doc.
- For rung 1 with more than one build boundary, add a **Build targets** section after Components: each target, its allowed imports, and its build and test commands.

## A rung that works inside a subsystem

L4 designs the generator's internals. Puzzle Generator is a separate build target, so it meets a subsystem trigger, and its doc is created in subsystem mode as part of this rung's step 5, with only what L4 needs. The brief's diagram draws the generator's inner components and keeps App Shell as one box; the Overview keeps one Puzzle Generator box.

```markdown
## Design docs touched
| Doc | What changes | Depth before → after |
| --- | --- | --- |
| Puzzle_Generator.md | New (subsystem mode): Contract, Grid Solver and Cell Remover designed, Difficulty Rater sketched | new |
| Overview.md | Puzzle Generator row: `Doc` link, Contract summary; subsystem index | Puzzle Generator sketched → designed |
```
