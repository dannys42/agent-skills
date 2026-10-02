# Changelog

## 0.3.0 — 2026-10-02

- Added `tasklist` for writing and maintaining a `TODO.md` checklist (invoke with `/tasklist`)
  - Phase, group, and task IDs (`P1`, `G2`, `T7`) are unique across the whole file and never reused or renumbered
  - Each task records its minimum model as a tier plus a named model, such as `standard (Sonnet 5.5)`
  - Standard markers: `[x]` done, `[-]` closed with `OBSOLETE`, `INVALID`, `SUPERSEDED→ID`, or `DEFERRED`, and `BLOCKED` and `IN-PROGRESS` for open items
  - `USER` tasks mark work only the user can do, with lettered steps (`a.`, `b.`, `c.`) the user can cite as `T4c`
  - Default path is `<DocDir>/TODO.md`; fully closed phases stay in place unless the user asks to archive them to `<DocDir>/Archive/Tasks.md`
- `decision-driven-design` can now emit its tasks in the `tasklist` format, in a file the user names
