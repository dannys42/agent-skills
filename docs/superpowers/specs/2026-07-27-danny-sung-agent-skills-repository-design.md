# Danny Sung's Agent Skills Repository Design

**Date:** 2026-07-27

## Purpose

Create a standalone, portable catalog of agent skills at the intended local
repository, `~/projects/AITools/swift-testing-skill`. The planned GitHub
repository is `dannys42/agent-skills`, with the display title **Danny Sung's
Agent Skills** and marketplace identifier `danny-sung-agent-skills`.

The repository begins with Swift unit-test naming guidance but must support
additional Swift and Apple-platform skill bundles later.

## Repository Structure

Use a plugin catalog:

```text
agent-skills/
├── plugins/
│   └── swift-testing/
│       ├── skills/
│       │   └── naming-swift-tests/
│       └── marketplace adapters
├── .claude-plugin/
├── .agents/
├── .cursor-plugin/
└── README.md
```

`swift-testing` is the initial focused plugin. Future bundles may be added as
sibling plugins without forcing users to install every Apple-related skill.

## Initial Release

- Repository version: `1.0.0`
- Initial plugin: `swift-testing`
- Initial skill: `naming-swift-tests`
- License: MIT
- Canonical skill path:
  `plugins/swift-testing/skills/naming-swift-tests/SKILL.md`
- Skill length: at most 500 words

The naming skill is the tested, approved artifact developed through the prior
interview. It covers Swift Testing and XCTest files, suites, functions,
variables, fixtures, helpers, test environments, and parameterized arguments.

For one result role, use `expectedValue` and `observedValue`. When a test has
multiple result roles, qualify both sides symmetrically, such as
`expectedOutputValue`/`observedOutputValue`. Preserve cardinality within each
role: a single searched-for event is `expectedEventValue`, while the complete
recorded collection is `observedEventValues`.

## Distribution

Provide native adapters for:

- Claude
- Codex
- Cursor
- Gemini

Document direct installation for:

- Claude Code
- Codex
- Cursor
- Gemini CLI
- GitHub Copilot
- OpenCode
- Roo Code
- Zoo Code
- ZCode
- Zed

Document readiness for skills.sh, SkillsMD, and mdskills.ai indexing without
claiming that the repository has been submitted or published there.

Do not copy the reference marketplace's custom `registry.json`; it is not a
portable marketplace standard.

## Commit Boundaries

Use one commit per major task:

1. `docs: design Danny Sung's Agent Skills repository`
2. `skill(swift-testing): add Swift test naming conventions`
3. `plugin(swift-testing): add cross-agent distribution`

The distribution commit contains the initial `1.0.0` manifests, README,
changelog, MIT license, and marketplace adapters. This avoids artificial
intermediate version bumps.

## Migration and Recovery

1. Recreate the approved skill and supporting files in the intended repository.
2. Validate the new repository before modifying the reference repository.
3. Remove the untracked `claude-marketplace` reference symlink.
4. Confirm the reference repository contains no unrelated local work.
5. Restore `claude-marketplace` exactly to `origin/main`, removing only the
   commits and files created during the mistaken implementation.

Do not create a GitHub repository, add a remote, or push without separate user
authorization. Keep the local directory name `swift-testing-skill`; the user
will rename and reopen it later.

## Verification

Before completion:

- Validate the skill frontmatter and enforce the 500-word limit.
- Forward-test representative Swift Testing and XCTest naming scenarios.
- Parse all JSON and run available Claude, Codex, Cursor, and Gemini checks.
- Confirm every manifest reports version `1.0.0`.
- Verify universal discovery finds `naming-swift-tests`.
- Verify the README covers every supported host and open registry.
- Run whitespace and clean-worktree checks.
- Independently review each major implementation commit and the complete result.
