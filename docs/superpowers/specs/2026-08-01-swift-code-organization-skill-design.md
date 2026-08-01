# Swift Code Organization Skill Design

**Date:** 2026-08-01

## Goal

Create a portable personal-style skill that keeps Swift source trees easy to
navigate by giving important types focused files, grouping related files by
domain concept, and separating structural reorganization from behavioral
changes in Git history.

## Plugin Architecture

Create a new `swift-code-organization` plugin containing one discoverable
`organizing-swift-files` skill. Keep this separate from
`swift-design-patterns`: the new skill governs physical source organization,
not the selection of behavioral or architectural patterns.

Match the repository's existing portable plugin and marketplace adapter shapes
for Codex, Claude Code, Cursor, Gemini CLI, and compatible skill-directory
hosts. The skill requires no scripts, assets, or large references; its complete
guidance belongs in a concise `SKILL.md` with generated `agents/openai.yaml`
metadata.

## Trigger Scope

Trigger when creating, substantially editing, reviewing, or reorganizing Swift
source files or a Swift project directory. This includes SwiftUI views because
they are Swift structs. Do not trigger for unrelated project work or for a
request that only reads Swift code without evaluating its organization.

The skill applies these conventions to new and meaningfully modified code. It
may recommend or perform proactive reorganization according to the sequencing
rules below, but it must not silently broaden a small task into an unrelated
repository-wide refactor.

## File Rules

- Give every `struct`, `class`, and `actor` its own correspondingly named Swift
  file.
- Treat nested `struct`, `class`, and `actor` declarations as real types that
  follow the same separate-file rule. Preserve their nesting when it carries
  useful namespacing or access semantics by declaring them in an extension of
  the enclosing type in the nested type's file.
- Allow a small supporting declaration to share the primary type's file only
  when it is a few lines long, tightly coupled to that type, and has no useful
  independent role. Typical exceptions are a supporting `enum` or `typealias`.
- Do not use the supporting-type exception for another `struct`, `class`, or
  `actor`.
- Name the file after its primary type.
- Keep a small, tightly related extension with its primary type.
- Put a substantial extension or an extension representing a distinct concern
  in a sibling file named `TypeName+Concern.swift`.

## Directory Rules

Organize Swift source hierarchically by feature or domain concept rather than
placing all source files in a flat directory. When multiple files implement or
support the same concept, create a directory for that concept and keep those
files together.

Prefer the shallowest hierarchy that makes conceptual ownership clear. Do not
create a directory merely to wrap one ordinary file, and do not organize
primarily by incidental declaration kind such as `Structs`, `Classes`, or
`Enums`.

## Change Sequencing

Before substantial new work, inspect the affected area and decide whether a
major reorganization is already foreseeable.

If reorganization would materially change file locations, directory
boundaries, or the structure of the upcoming implementation:

1. Perform the structural reorganization first.
2. Verify behavior is unchanged.
3. Commit the reorganization as a clean structural commit.
4. Begin and commit the requested behavioral work separately.

If major reorganization is not necessary up front:

1. Finish and commit the requested behavioral change.
2. Proactively reorganize directly related code in a separate clean commit.
3. Put broader organization adjustments in subsequent clean commits.

Do not mix structural movement with behavioral changes unless separating them
would make the change unsafe or impractical. When Git commits are not
authorized or are outside the active workflow, identify the organization work
as a follow-up instead of mixing it into the requested change.

## Agent Decision Guidance

Use judgment rather than line-count automation. "A few lines," "substantial,"
and "major reorganization" are contextual thresholds:

- a supporting declaration remains local only when extracting it would make
  the concept harder to understand;
- an extension deserves its own file when it represents a named concern or
  makes the primary file harder to scan;
- reorganization is major when it affects enough files or boundaries that
  mixing it with new behavior would obscure review or Git history.

When existing repository constraints conflict with the preference—such as
generated code, third-party sources, package layout contracts, or Xcode project
membership—preserve correctness and explain the exception.

## Validation

Follow `writing-skills` test-first validation for this discipline-enforcing
skill. Capture baseline responses from fresh agents without the skill, then
repeat the same scenarios with it present. Cover at least:

- several top-level structs placed in one file;
- a SwiftUI view plus a small supporting enum;
- a nested supporting struct that should be extracted;
- small and substantial extensions;
- several files belonging to one feature in a flat directory;
- anticipated major reorganization before new work;
- related cleanup discovered after behavioral work;
- a workflow where commits are not authorized;
- generated or third-party Swift sources that should not be reorganized.

Success means the agent consistently separates every struct, class, and actor,
uses supporting exceptions narrowly, groups files by concept, and preserves
clean structural-versus-behavioral sequencing without exceeding its authority.

Run repository metadata, manifest, skill-frontmatter, marketplace consistency,
and focused behavioral checks before claiming completion.
