# Roadmap file format and worked example

File: `<DocDir>/Roadmap-<Topic>.md`.

```markdown
# Roadmap: <Project name>

Design: <path to Design-<Topic>.md>
Updated: <date>

## Ladder (one line per rung, in order)
1. R1 — <question> [status]
...

## Rungs (detailed)
### R1: ...
...

## Horizon (not yet detailed)
- R6 — <one-line question>

## Learning log
- R1 (done, <date>): <what we learned, measured answer>
```

## Worked example: printable Sudoku app for macOS

Risks from the design, ranked: generator correctness and speed (high impact, high uncertainty); fidelity of drawing and printed text (medium, medium); document-based app shape (medium, low); arbitrary grid sizes (low, low once the generator is generic).

### Ladder

1. R1 — Can I build and run the most basic document-based macOS app?
2. R2 — Can I draw the project's most basic repeated element, a fixed 3×3 grid?
3. R3 — Do I have fine enough control over the drawing: fonts, size, color, style, readable?
4. R4 — Can I produce the core logic: a Sudoku generator for a 3×3 grid, with no UI?
5. R5 — Can I see the generator's result on the grid?
6. R6 — Can the generator produce a playable starting point (cells removed), shown on screen?
7. R7 — Does everything hold for a 4×4 grid?
8. R8 — Can the user choose arbitrary grid sizes from the UI?

### Why this order

- R1 first: nothing else can be tested without a running app (the skeleton).
- R2–R3 before the generator: they are cheap, and a failure here (fonts unreadable, drawing awkward) would change the UI approach; they also give a canvas to show the generator's output.
- R4 is the biggest unknown but needs no UI, so it can be proven in isolation with unit tests. It sits after the drawing rungs only because the drawing rungs are fast and cheap. Putting R4 earlier is also valid; the user decides. If the generator looked frightening, pull it ahead of R2.
- R5 joins the two proven halves; it is the first moment the product does its job.
- R7–R8 come last because once the generator is generic they are straightforward changes, not unknowns.

### Detailed rungs (first three)

```markdown
### R1: Build and run a document-based macOS app
Question: Can I build and run the most basic app of the right shape?
Slice: A document-based SwiftUI macOS app with a blank window that opens, saves, and reopens a document.
Done when: `xcodebuild build` succeeds, the app launches, File > New opens a window, and Save then Open round-trips an empty document.
De-risks: R-skeleton, R-documents
Depends on: none
If no: Fall back to a single-window app and revisit documents later; record why in the design.
Status: planned

### R2: Draw a fixed 3x3 grid
Question: Can I draw on a canvas?
Slice: Replace the blank window content with a 3×3 grid drawn at a fixed size.
Done when: The grid appears with even, crisp lines at 1× and 2× scale; a screenshot or a snapshot test shows it.
De-risks: R-drawing
Depends on: R1
If no: Try Core Graphics via an AppKit view instead of SwiftUI Canvas.
Status: planned

### R3: Control text in the grid
Question: Do fonts work, and is the size, color, and style legible?
Slice: Fill the grid with fixed numbers 1–9 in the chosen font; export one page as PDF.
Done when: The PDF shows centered, readable digits; a printed page is checked by eye.
De-risks: R-text, R-print
Depends on: R2
If no: Change font or draw digits as paths; update the design's technology section.
Status: planned
```

### Horizon

- R4–R8 as listed in the ladder, detailed one at a time after R3 teaches us what the drawing layer can do.

## Another shape: a CLI or service (not Apple-specific)

The same method yields a different ladder: R1 builds and runs hello-world with CI; R2 reads one real input end to end; R3 proves the one risky integration against the real service; R4 adds the core transformation with tests; R5 adds persistence; later rungs add breadth. What stays the same is the rule, not the content: each rung is runnable and answers the biggest unknown reachable from here.
