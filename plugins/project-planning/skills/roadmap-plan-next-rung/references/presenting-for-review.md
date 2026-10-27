# Presenting items for the user to rule on

Shared by `system-design`, `risk-first-roadmap`, `roadmap-plan-next-rung` and `code-quality-pass`, and by the repo-local feedback skills. Use it whenever you hand the user a list to accept, reject or choose from: a draft's questions and assumptions, a rung order, review proposals, triage verdicts, "worth changing" items.

It adds an order and a callout. It never removes an item or a field the calling skill shows: every item still appears, in the calling skill's own format.

## What to flag

An item needs the user's attention when it is any of:

- **High impact**: expensive to undo (persistence, a public interface, a build boundary, migration), changes what the user sees, or shapes several later rungs or tasks.
- **A new name** of a kind that is costly to rename or that the owner will say: a database schema name, domain term, wire field or type name. List such names together as one item, each with its candidates.
- **Low confidence**: you inferred it rather than checked it, the evidence conflicts or is a single run, or it depends on what the user wants rather than on facts.

Flag at most 5. If more qualify, flag the 5 with the highest impact (then the least confidence) and say how many more qualify; those stay in the full list, marked `⚑`. Do not flag an item only because it is new or long (a new name of the kinds above is the exception).

## Shape

1. **Needs your attention**, first. For each flagged item:
   - its ID and a one-line statement
   - **Why**: `high impact`, `low confidence`, or both, and the reason in a few words
   - **To settle it** (only when confidence is the issue): the cheapest check or the one question whose answer decides it
   - **Options**: two or three, the recommended one first and marked, each with a plain example from the project and a one-line pro and con. A naming or other open question lists its candidate answers the same way; a card that only says "I will ask you for X" cannot be ruled on. When there is no real alternative, say so in one line instead of inventing one.
2. **Everything else**, in the calling skill's usual format and order. Each item shows its default or recommended action, and a flagged item stays in place as a one-line pointer (`⚑ see above`), so IDs and rankings stay intact.
3. **One closing question**: which options to take for the flagged items, and "reply only with the other items you would change; the rest go ahead as shown".

If nothing qualifies, say `Nothing needs special attention.` in one line and give the list as usual.

With a structured question tool, ask the flagged items through it (recommended option first, the pro and con in each option's description) and give the rest in markdown.

## Example

```markdown
**Needs your attention**

⚑ **A3: Puzzles are stored as one JSON file per puzzle** (high impact, low confidence)
Why: the storage format is costly to change after rung 2, and I guessed the library size.
To settle it: about how many puzzles will a user keep, tens or thousands?
- **One file per puzzle** (recommended). Pro: simple, easy to diff and sync. Con: slow to list once there are thousands.
- **SQLite store.** Pro: fast queries at any size. Con: a schema and migrations from rung 1.

**Everything else** (goes ahead unless you object)
- A1 macOS 15 minimum: assumed, native SwiftUI tables
- A2 Single window: assumed
- A3 ⚑ see above

Which storage option should we use? Reply only with the other items you would change.
```
