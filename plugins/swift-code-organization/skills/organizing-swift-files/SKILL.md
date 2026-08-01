---
name: organizing-swift-files
description: Use when creating or substantially editing Swift source files, or when reviewing Swift physical organization or reorganizing Swift file, directory, nested-type, SwiftUI type, or extension placement.
---

# Organizing Swift Files

## Core rule

Give every `struct`, `class`, and `actor` its own correspondingly named Swift file.
Treat every SwiftUI view as a struct under this rule.

Allow a supporting `enum` or `typealias` to remain with the primary type only
when it is a few lines, tightly coupled, and has no useful independent role.
Never apply this exception to another `struct`, `class`, or `actor`.

For a nested `struct`, `class`, or `actor`, name its file
`EnclosingType+NestedType.swift`. Preserve qualified naming by declaring the
nested type in an extension of the enclosing type.

## Extensions

- Keep a small, tightly related extension with the primary type.
- Move a substantial or distinct concern to `TypeName+Concern.swift`.

## Directories

Organize hierarchically by feature or domain concept. When several files serve
one concept, put them in that concept's directory. Prefer the shallowest clear
hierarchy; do not create folders by declaration kind or wrap one ordinary file
in a directory without a conceptual reason.

## Sequence structural work

Before substantial new work, inspect the affected area:

- If foreseeable major reorganization would change file locations, directory
  boundaries, or implementation structure, reorganize first, verify behavior
  is unchanged, and commit the structure before implementing behavior.
- Otherwise finish and commit the behavioral change first, then reorganize
  directly related code in a separate clean commit. Put broader cleanup in
  later clean commits.

Do not mix structural movement and behavioral edits unless separation would be
unsafe or impractical. If edits or commits are not authorized, report the
organization work as a follow-up instead of performing it.

## Constraints

Apply these rules to new or meaningfully modified first-party code. Do not
silently broaden a small task into an unrelated repository-wide refactor.
Preserve generated code, third-party sources, package layout contracts, and
Xcode project correctness. Explain any necessary exception. Use judgment for
"few lines," "substantial," and "major": optimize conceptual clarity and
reviewable history, not arbitrary line counts.
