# Subsystems

Shared by `system-design` and `roadmap-plan-next-rung`. A design doc that grows forever stops being read and stops being updated, and then it stops being true. So no design doc grows without bound: when a piece of the system needs its own design, it gets its own doc, and every other doc treats it as a single component.

## Layout

```
<DocDir>/SystemDesign/
  Overview.md                  top-level design (Parent: none)
  Puzzle_Generator.md          a subsystem (Parent: Overview.md)
  Grid_Solver.md               a nested subsystem, only if warranted (Parent: Puzzle_Generator.md)
  Rung-L4-Puzzle_Generator.md  rung briefs
```

Files stay flat; the `Parent:` header gives the tree, and the Overview keeps a small subsystem index of every subsystem doc at any depth. A subsystem doc is named after its component, in Snake_Case (`Puzzle Generator` → `Puzzle_Generator.md`).

Every design doc has the same shape ([overview-template.md](overview-template.md) for the Overview, [subsystem-template.md](subsystem-template.md) for a subsystem): summary and success criteria, scope, headline requirements, focus areas, its own component diagram with depth tags, decisions, assumptions, ranked risks, open questions, and traceability. A subsystem doc adds a `Parent:` header and a **Contract**.

## When a piece is a subsystem

Make it one when any of these holds:

- it is a separate build target: an app, a library or package, an extension, a service, a CLI;
- it has its own lifecycle, release cadence, or owner;
- it has its own requirements and risks that would clutter the parent;
- its internals have more than about five moving components, or a focus area of their own.

Otherwise it stays a row in its parent, and its detail stays in the rung brief that builds it.

## Promote on demand

Every component starts as a row in its parent. A row that already meets a trigger is marked `Doc: pending`, meaning it will get its own doc when it needs one; others say `Doc: none`. Write the subsystem doc when a rung needs to design that piece's internals and it meets a trigger, or when the user asks. Do not write subsystem docs up front: an unread design of something nobody is building yet is the top-heavy spec this layout exists to avoid.

## Parent and child

- **The parent sees only the Contract.** In the parent's diagram the subsystem is one box; in its component table it is one row with a one-line responsibility, a `Doc` link, and the Contract summary. Never copy a subsystem's internals into the parent.
- **The Contract** is what the rest of the system may rely on: responsibilities, what crosses the boundary (public interface, events, file formats), and the parent requirements allocated to it, by qualified ID (`Overview:FR1`).
- **Edit where the change lives.** A change inside a subsystem edits only that subsystem's doc. The parent changes only when the Contract does: the interface, the allocated requirements, or a risk that crosses the boundary.
- **Each doc owns the traceability of its own requirements.** The parent maps an allocated requirement to a rung `via <Subsystem>`, or `via <Subsystem> (doc pending)` as coarse coverage until the subsystem doc exists; the subsystem's table maps its refined requirements, each naming the parent requirement it refines.
- **Depth tags are per doc** and describe that doc's own components. The parent tags a subsystem box `sketched` until its doc exists, `designed` once that doc is agreed, and `built` when a fold-back verified it.

## IDs

IDs (`A`, `D`, `R`, `Q`, `FR`, `NFR`) are per document: unique within the doc, never reused or renumbered. Within a doc, cite them bare (`R3`). Across docs, qualify them with the doc name: `Puzzle_Generator:R3`, `Overview:D2`. Roadmaps, rung briefs, and tasklists cite design IDs the same way.

## Subsystem mode

`/system-design <Subsystem>`, or automatically when a rung promotes a piece. It runs the normal outline workflow scoped to one subsystem:

1. **Inspect** the parent doc, the subsystem's row and Contract there, the code for that piece, and any rung briefs that touched it.
2. **Draft in one pass.** Start from the Contract, since it is what the parent already relies on; then scope, requirements (allocated ones by parent ID, refined ones as this doc's own, refining every one the parent covers as `(doc pending)`), components, decisions, assumptions, and risks. Flag every guess as an assumption. When a rung triggered this, design only what that rung needs, but keep the standard shape so later rungs know where to add.
3. **Ask 3–5 questions** that would change the Contract, the inner components, or the top risks.
4. **Iterate** until the user says it is good enough; set `Status: agreed (<date>)`.
5. **Update the parent** only for the box, its `Doc` link and depth tag, the Contract summary if it changed, and the subsystem index.

In adopt mode, list each separate build target and major module in the as-is Overview as a component with `Doc: pending`, and offer to adopt the one the user cares about first.
