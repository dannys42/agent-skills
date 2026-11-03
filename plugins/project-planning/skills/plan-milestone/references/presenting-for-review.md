# Presenting items for the user to rule on

Shared by `system-design`, `risk-first-roadmap`, `plan-milestone` and `code-quality-pass`, and by the repo-local feedback skills. Use it whenever you hand the user a list to accept, reject or choose from: a draft's questions and assumptions, a rung order, review proposals, triage verdicts, "worth changing" items. It adds tiers, an order and options; it never removes an item or a field the calling skill shows.

## Tiers

The test: if this is wrong, what does it cost to fix three milestones from now? Group items by tier and sort each tier by that cost, highest first.

- **Important** when any of these holds:
  - hard to reverse: stored data, file formats, public interfaces, names others build on (a schema name, domain term, wire field, type or component name), migration of existing projects
  - wide reach: several skills or tools, or text every run reads
  - changes a concept rather than wording
  - changes the owner's workload or the cost: sessions, review points, the model per step
  - low confidence on something consequential: inferred rather than checked, conflicting or single-run evidence, or it hangs on what the user wants
- **Notable**: fixable later in a few files, or changes one skill's behaviour noticeably.
- **Small**: local and reversible in one edit: wording, an easily overridden default, ordering inside a list, an internal name.

Important is the callout: at most 5. If more qualify, keep the 5 that cost most, say how many more qualify, and open the notable tier with the rest. List new names together as one item, each with its candidates.

## Shape

1. **Important**, **Notable**, **Small**, in that order; leave out an empty tier. With nothing important, say `Nothing needs special attention.` in one line.
2. Every decision: a statement that opens with one plain sentence on what the thing does, or what happens today, shown on a case from the project; then two or three options, each with a plain example and a one-line pro and con; then a recommendation, or "no recommendation" and why. An open or naming question lists candidate answers the same way; "I will ask you for X" cannot be ruled on. With no real alternative, say so in one line instead of inventing one.
3. **An ID carries its name.** The first time any ID appears in a message (an item, rung, milestone, task or requirement), follow it with its short name: "L4 (folder suggestions)", "A3 (puzzle storage)", never "L4" alone. Get rung and milestone names from `roadmap name` when the tool has it, not by reading sections.
4. Important items add **Why** (which test it meets, in a few words) and, when confidence is the issue, **To settle it**: the cheapest check or the one question that decides it.
5. A list whose order is the content (a rung ladder) is shown whole in its own order first; the decisions about it follow, by tier.
6. **One closing question**: which options to take for the important items and any without a recommendation, and "reply only with the other items you would change; the rest go ahead as recommended". With a structured question tool, ask the important items through it (recommended option first, the pro and con in each option's description) and give the rest in markdown.

## Example

```markdown
**Important**

**A3 (puzzle storage): Puzzles are stored as one JSON file per puzzle.** Each saved puzzle becomes its own file in the library folder.
Why: stored data, costly to change after rung 2, and I guessed the library size.
To settle it: about how many puzzles will a user keep, tens or thousands?
- **One file per puzzle** (recommended). Pro: simple, easy to diff and sync. Con: slow to list once there are thousands.
- **SQLite store.** Pro: fast queries at any size. Con: a schema and migrations from rung 1.

**Notable**

**A1 (minimum macOS): macOS 15 minimum.** The app will not install on macOS 14.
- **macOS 15** (recommended). Pro: native SwiftUI tables. Con: drops macOS 14 users.
- **macOS 14.** Pro: more users. Con: a hand-built table view.

**Small**: **A2 (window title): The window title shows the puzzle's name.** **Puzzle name** (recommended). Pro: reads well. Con: two "Untitled" puzzles look alike. **File name.** Pro: unique. Con: reads like a path.

Which storage option should we use for A3 (puzzle storage)? Reply only with the other items you would change.
```
