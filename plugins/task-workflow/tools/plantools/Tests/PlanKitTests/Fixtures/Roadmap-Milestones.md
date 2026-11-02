# Roadmap: Sudoku printer

Design: docs/SystemDesign/Overview.md
Updated: 2026-11-01

## Milestones
- M1 (print a puzzle) — I can print a playable 9×9 Sudoku from the app. `owner`; touches: Document_App, Grid_View [current]
  - Exit: File > Print gives a page whose puzzle has exactly one solution.
- M2 (any size) — I can choose a grid size and print a puzzle of it. `proposed`; touches: Generator, Size_Picker [planned]
  - Additive check: yes, the generator takes the box size as a parameter.
- M3 (puzzle library) — I can keep the puzzles I made and print them again. `proposed` [planned]

## Ladder (one line per rung, in order)
1. L1 — Can I build and run the most basic document-based macOS app? [done] detail: Completed/Roadmap-Milestones-Rungs.md
2. L2 — Can I draw the most basic repeated element, a fixed 9x9 grid? [in progress]
3. L3 — Do I control the drawing finely enough? [planned]

## Rungs (detailed)

### L2: Draw a fixed 9x9 grid
Question: Can I draw on a canvas?
Milestone: M1
Touches: Grid_View
Class: shape

### L3: Control text in the grid
Question: Do fonts work?
Milestone: M1
Touches: Grid_View, Print_Export
Class: shape

## Horizon (not yet detailed)
- L6 — Can the generator remove cells so one solution remains? (M1)
- L7 — Can I pick a size? (M2)

## Learning log
- L1 (done, 2026-10-30): the document app round-trips.
