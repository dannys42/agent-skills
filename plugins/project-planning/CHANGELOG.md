# Changelog

## 0.2.0

- `risk-first-roadmap`: add an architecture/build-target step inside rung 1 (only when the design has more than one build boundary), gated on owner approval
- `risk-first-roadmap`: add a requirement traceability check to the ladder checks, plus a drift checkpoint after the first end-to-end data rung
- `risk-first-roadmap`: rename rungs from `R1...` to `L1...` so they no longer collide with the design's `R` risk IDs

## 0.1.0

- Initial release with two skills:
  - `system-design`: draft a high-level design with flagged assumptions, iterate with the user to agreement, and produce a ranked risk register at `<DocDir>/Design-<Topic>.md`
  - `risk-first-roadmap`: order work as end-to-end increments that each answer the riskiest reachable unknown, written to `<DocDir>/Roadmap-<Topic>.md`
- Apple-platform reference material for both skills
