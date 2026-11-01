---
type: llm
focus: {source: file, path: "Documentation/SystemDesign/Overview.md"}
weight: 3
---

The design document agrees structure, not internals, and only as far as the first milestone needs.

Pass when ALL of these hold:
- It names components, the seams between them and the data model at the level of entities and relationships.
- It contains no algorithm detail: no scoring formulas, weights, thresholds, embedding or model choices, calibration procedures or sweep designs. Naming a matching method as something a later milestone adds is fine.
- Field-level detail (columns, fields, signatures) appears only for persisted data, a wire or command-line surface the owner uses, or public library symbols, and only for what the first milestone builds.
- Methods the vision lists for later (page-text embeddings, on-device and cloud models, combined scores, calibration, other browsers, dead links, duplicates, new folders) appear at most as one line each, as later scope.

Fail if any component outside the first milestone is designed beyond one line, or if any algorithm is specified.
