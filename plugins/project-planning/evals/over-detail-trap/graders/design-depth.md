---
type: llm
focus: {source: file, path: "Documentation/SystemDesign/Overview.md"}
weight: 3
---

The design document agrees structure, not internals, and only as far as the first milestone needs.

Pass when ALL of these hold:
- It names components, the seams between them and the data model at the level of entities and relationships.
- It contains no algorithm detail: nothing that says how a method computes its answer, such as a scoring formula, a weighting ("weighted by how distinctive each word is"), a numeric threshold the design fixes, an embedding or model choice, a calibration procedure or a sweep design. Naming a method, a measure (threshold sweep, sibling confusion, coverage) or a later milestone's work is fine, and so is deferring how it works ("decided after it runs"). A target in a risk's unknown or experiment ("say 90%+") is not algorithm detail.
- Field-level detail (columns, fields, signatures) appears only for persisted data, a wire or command-line surface the owner uses, or public library symbols, and only for what the first milestone builds.
- Methods the vision lists for later (page-text embeddings, on-device and cloud models, combined scores, calibration, other browsers, dead links, duplicates, new folders) are named, not designed: each mention is at most one line, and none says how the later method works. Mentioning the same later item in several sections (a milestone row, a decision, a risk, a name) is fine.

Fail if any later method's workings are described anywhere (including inside a first-milestone component row), if a later component is designed beyond one line, or if any algorithm is specified. Quote the line that decides a FAIL.
