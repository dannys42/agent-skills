# Roadmap file format and worked example

File: `<DocDir>/Roadmap-<Topic>.md`.

```markdown
# Roadmap: <Project name>

Design: <DocDir>/SystemDesign/Overview.md (or a legacy Design-<Topic>.md)
Build boundaries: <"decided in L1's brief", or "single target">
Updated: <date>

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

## Worked example: printable Sudoku app for macOS

Risks from the design, ranked: generator correctness and speed (high impact, high uncertainty); fidelity of drawing and printed text (medium, medium); document-based app shape (medium, low); arbitrary grid sizes (low, low once the generator is generic).

### Ladder

1. L1 — Can I build and run the most basic document-based macOS app?
2. L2 — Can I draw the project's most basic repeated element, a fixed 3×3 grid?
3. L3 — Do I have fine enough control over the drawing: fonts, size, color, style, readable?
4. L4 — Can I produce the core logic: a Sudoku generator for a 3×3 grid, with no UI?
5. L5 — Can I see the generator's result on the grid?
6. L6 — Can the generator produce a playable starting point (cells removed), shown on screen?
7. L7 — Does everything hold for a 4×4 grid?
8. L8 — Can the user choose arbitrary grid sizes from the UI?

### Why this order

- L1 first: nothing else can be tested without a running app (the skeleton).
- L2–L3 before the generator: they are cheap, and a failure here (fonts unreadable, drawing awkward) would change the UI approach; they also give a canvas to show the generator's output.
- L4 is the biggest unknown but needs no UI, so it can be proven in isolation with unit tests. It sits after the drawing rungs only because the drawing rungs are fast and cheap. Putting L4 earlier is also valid; the user decides. If the generator looked frightening, pull it ahead of L2.
- L5 joins the two proven halves; it is the first moment the product does its job.
- L7–L8 come last because once the generator is generic they are straightforward changes, not unknowns.

### Detailed rungs (first three)

```markdown
### L1: Build and run a document-based macOS app
Question: Can I build and run the most basic app of the right shape?
Slice: A document-based SwiftUI macOS app with a blank window that opens, saves, and reopens a document.
Done when: `xcodebuild build` succeeds, the app launches, File > New opens a window, and Save then Open round-trips an empty document.
De-risks: R-skeleton, R-documents
Depends on: none
If no: Fall back to a single-window app and revisit documents later; record why in the design.
Status: planned

### L2: Draw a fixed 3x3 grid
Question: Can I draw on a canvas?
Slice: Replace the blank window content with a 3×3 grid drawn at a fixed size.
Done when: The grid appears with even, crisp lines at 1× and 2× scale; a screenshot or a snapshot test shows it.
De-risks: R-drawing
Depends on: L1
If no: Try Core Graphics via an AppKit view instead of SwiftUI Canvas.
Status: planned

### L3: Control text in the grid
Question: Do fonts work, and is the size, color, and style legible?
Slice: Fill the grid with fixed numbers 1–9 in the chosen font; export one page as PDF.
Done when: The PDF shows centered, readable digits; a printed page is checked by eye.
De-risks: R-text, R-print
Depends on: L2
If no: Change font or draw digits as paths; record the decision in the Overview.
Status: planned
```

### Horizon

- L4–L8 as listed in the ladder, detailed one at a time after L3 teaches us what the drawing layer can do.

## Another shape: a CLI or service (not Apple-specific)

The same method yields a different ladder: L1 builds and runs hello-world with CI; L2 reads one real input end to end; L3 proves the one risky integration against the real service; L4 adds the core transformation with tests; L5 adds persistence; later rungs add breadth. What stays the same is the rule, not the content: each rung is runnable and answers the biggest unknown reachable from here.
