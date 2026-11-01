---
type: llm
weight: 2
---

The closing summary is readable without opening the documents.

Pass when every identifier the summary mentions (rung IDs such as L1, milestone IDs such as M1, and decision, risk, requirement or question IDs such as D3, R2, FR1, Q4) is accompanied, at its first mention, by a short plain name or description of what it is. A summary that uses no identifiers passes.

Fail if any identifier appears bare at its first mention, for example "L1 next" or "R2 is retired" with no name.
