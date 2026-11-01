---
type: llm
target: {source: file, path: "Documentation/Roadmap-Shop_Lab.md"}
weight: 3
---

Data that cannot be recovered later is collected first.

Two sources lose data every day they are not collected: storefront analytics (kept 90 days only) and product pages (the platform keeps no history, so changes must be snapshotted as they happen).

Pass when BOTH of these hold:
- Collection of storefront analytics and snapshots of product pages each start within the first three rungs after the walking skeleton (or are part of it), and the roadmap says why (the data cannot be recovered later).
- Sources with full history (orders, ads, newsletter) are not placed ahead of them unless they are needed as a prerequisite, and the roadmap says so.

Fail if either perishable source starts after a rung that only adds a source with full history, or after any experiment or presentation work.
