# Swift Code Organization Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and distribute a tested `organizing-swift-files` skill that applies Danny Sung's Swift file, directory, and structural-commit preferences.

**Architecture:** Add a standalone `swift-code-organization` plugin with one concise, self-contained skill and no runtime tooling. Verify the discipline behavior with fresh-agent baseline and forward scenarios, enforce packaging and content contracts with focused standard-library Python tests, and expose the plugin through the repository's Codex, Claude, Cursor, Gemini, and open-skill distribution surfaces.

**Tech Stack:** Agent Skills Markdown, YAML, JSON plugin manifests, Python 3 `unittest`, Git

---

## Preflight and File Map

No major repository reorganization is anticipated: the existing
`plugins/swift-code-organization/skills/organizing-swift-files/` shape fits the
new plugin. Keep all implementation work on `codex/swift-code-organization` in
`.worktrees/swift-code-organization`.

Create these files:

- `plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md` — complete organization and sequencing guidance.
- `plugins/swift-code-organization/skills/organizing-swift-files/agents/openai.yaml` — Codex skill UI metadata.
- `plugins/swift-code-organization/.codex-plugin/plugin.json` — Codex plugin manifest.
- `plugins/swift-code-organization/.claude-plugin/plugin.json` — Claude plugin manifest.
- `plugins/swift-code-organization/.cursor-plugin/plugin.json` — Cursor plugin manifest.
- `plugins/swift-code-organization/gemini-extension.json` — Gemini extension metadata.
- `plugins/swift-code-organization/README.md` — concise plugin and installation overview.
- `plugins/swift-code-organization/CHANGELOG.md` — initial release entry.
- `plugins/swift-code-organization/LICENSE` — plugin MIT license.
- `plugins/swift-code-organization/tests/evaluation-cases.json` — reusable behavioral scenarios and rubric requirements.
- `plugins/swift-code-organization/tests/baseline-results.md` — verbatim fresh-agent results without the skill.
- `plugins/swift-code-organization/tests/forward-results.md` — verbatim fresh-agent results with the skill.
- `plugins/swift-code-organization/tests/test_plugin_contract.py` — deterministic packaging, metadata, and skill-content checks.

Modify these files:

- `.agents/plugins/marketplace.json` — append the Codex marketplace entry.
- `.claude-plugin/marketplace.json` — append the Claude marketplace entry.
- `.cursor-plugin/marketplace.json` — append the Cursor marketplace entry.
- `README.md` — list, explain, and document installation of the new plugin and skill.

Do not touch the unrelated `claude-marketplace` entry in the primary workspace.

### Task 1: Capture Failing Behavioral Baselines

**Files:**
- Create: `plugins/swift-code-organization/tests/evaluation-cases.json`
- Create: `plugins/swift-code-organization/tests/baseline-results.md`

- [ ] **Step 1: Create the evaluation corpus before creating the skill**

Write `evaluation-cases.json` with this complete corpus:

```json
[
  {
    "id": "separate-primary-types",
    "prompt": "Review a Swift file named Checkout.swift containing top-level CheckoutView: View, CheckoutState: struct, CheckoutClient: class, and CheckoutStore: actor. The feature works, release is due today, the current patch already consumed several hours, and the reviewer wants a fast turnaround. Propose the file layout and explain what you would change before editing behavior.",
    "requirements": [
      "puts every struct, class, and actor in its own correspondingly named file",
      "treats the SwiftUI view as a struct",
      "does not use schedule pressure to keep primary types together"
    ]
  },
  {
    "id": "small-supporting-enum",
    "prompt": "Organize PlaybackButton.swift, which defines PlaybackButton: View and a private three-case PlaybackIcon enum used only by the view. Explain whether both declarations need separate files.",
    "requirements": [
      "keeps the small tightly coupled enum with PlaybackButton when that is clearer",
      "does not invent an absolute one-declaration-per-file rule"
    ]
  },
  {
    "id": "nested-struct",
    "prompt": "Organize TimelineView.swift. TimelineView contains a nested Marker: struct with stored properties and rendering behavior. Marker is referenced as TimelineView.Marker elsewhere. Preserve that qualified name.",
    "requirements": [
      "moves Marker to TimelineView+Marker.swift",
      "preserves TimelineView.Marker by declaring Marker in an extension of TimelineView"
    ]
  },
  {
    "id": "extension-concerns",
    "prompt": "Review LibraryViewController.swift. It has a five-line private formatting extension and a 90-line UICollectionViewDataSource extension. Propose the exact files.",
    "requirements": [
      "allows the small tightly related extension to remain with the primary type",
      "moves the substantial concern to LibraryViewController+UICollectionViewDataSource.swift"
    ]
  },
  {
    "id": "feature-directory",
    "prompt": "A Sources directory is flat and contains SearchView.swift, SearchQuery.swift, SearchClient.swift, SearchResults.swift, SettingsView.swift, and AppDelegate.swift. Recommend a hierarchy without reorganizing unrelated code.",
    "requirements": [
      "groups the four Search files in a Search directory",
      "does not create declaration-kind folders",
      "leaves unrelated files outside the Search change"
    ]
  },
  {
    "id": "reorganize-before-feature",
    "prompt": "Plan a major new sharing workflow. The existing Sharing.swift has six primary types, and the new work would add four more types and change their dependencies. The team wants reviewable commits and implementation has not started.",
    "requirements": [
      "recognizes foreseeable major reorganization",
      "reorganizes and verifies existing structure first",
      "commits structural work before behavioral implementation"
    ]
  },
  {
    "id": "reorganize-after-feature",
    "prompt": "A major export feature has just been implemented and committed. While working on it, you found directly related Export types sharing files and a separate flat Import area that could also be improved. State the next Git sequence.",
    "requirements": [
      "reorganizes related Export code in a separate commit",
      "puts broader Import cleanup in a later clean commit",
      "does not amend organization changes into the behavioral commit"
    ]
  },
  {
    "id": "no-commit-authority",
    "prompt": "Review a Swift patch for organization problems, but you are not authorized to modify files or create commits. The patch adds two structs to one file. Report what you would do.",
    "requirements": [
      "identifies the required file split",
      "reports it as follow-up work",
      "does not claim to edit or commit"
    ]
  },
  {
    "id": "generated-and-vendored-sources",
    "prompt": "A project contains generated APIModels.swift with many structs, Vendor/LegacySDK.swift, and first-party ProfileView.swift with ProfileView and ProfileState structs. Recommend organization changes.",
    "requirements": [
      "does not reorganize generated or third-party sources",
      "separates the two first-party structs",
      "explains the constrained-source exception"
    ]
  }
]
```

- [ ] **Step 2: Validate the corpus syntax**

Run:

```bash
python3 -m json.tool plugins/swift-code-organization/tests/evaluation-cases.json >/dev/null
```

Expected: exit 0 with no output.

- [ ] **Step 3: Run every scenario through fresh agents without the skill**

Use one fresh agent context per case. Give the agent only the case prompt and enough neutral context to answer; do not mention the future skill, its rules, or expected requirements. Record the complete response verbatim under the case ID in `baseline-results.md`, then score each listed requirement as pass or fail with one quoted or precisely cited reason.

Expected RED result: at least one case fails at least one requirement. If every case passes, add a harder but non-conflicting pressure variant—time pressure, sunk-cost pressure, or minimal-diff pressure—and rerun before creating the skill.

- [ ] **Step 4: Summarize baseline failure patterns**

Begin `baseline-results.md` with:

```markdown
# Baseline Swift Code Organization Results

These fresh-agent runs did not load `organizing-swift-files`. Verbatim responses
are preserved below, followed by requirement-level scoring.

## Failure patterns
```

List only failures actually observed, such as keeping multiple primary types together, applying one-file-per-declaration too broadly to tiny enums, flattening by declaration kind, or mixing structural and behavioral commits. Do not write hypothetical failures as observed evidence.

- [ ] **Step 5: Commit the RED evidence**

```bash
git add plugins/swift-code-organization/tests/evaluation-cases.json plugins/swift-code-organization/tests/baseline-results.md
git commit -m "test(swift-organization): capture baseline behavior"
```

Expected: one test-evidence commit containing no skill implementation.

### Task 2: Add a Failing Plugin Contract Test and Scaffold the Plugin

**Files:**
- Create: `plugins/swift-code-organization/tests/test_plugin_contract.py`
- Create: `plugins/swift-code-organization/.codex-plugin/plugin.json`
- Create: `plugins/swift-code-organization/skills/organizing-swift-files/agents/openai.yaml`
- Create temporarily, then replace: `plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md`
- Modify: `.agents/plugins/marketplace.json`

- [ ] **Step 1: Write the failing contract test**

Create `test_plugin_contract.py` with imports and helpers that use only the standard library:

```python
import json
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).parents[1]
REPOSITORY_ROOT = PLUGIN_ROOT.parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "organizing-swift-files"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class PluginContractTests(unittest.TestCase):
    def test_codex_manifest_identifies_skill_plugin(self):
        manifest = load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
        self.assertEqual("swift-code-organization", manifest["name"])
        self.assertEqual("1.0.0", manifest["version"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual("Developer Tools", manifest["interface"]["category"])

    def test_codex_marketplace_exposes_plugin_once(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json"
        )
        matches = [
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == "swift-code-organization"
        ]
        self.assertEqual(1, len(matches))
        self.assertEqual(
            "./plugins/swift-code-organization",
            matches[0]["source"]["path"],
        )
        self.assertEqual("AVAILABLE", matches[0]["policy"]["installation"])
        self.assertEqual("ON_INSTALL", matches[0]["policy"]["authentication"])

    def test_openai_metadata_is_complete(self):
        metadata = (
            SKILL_ROOT / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn('display_name: "Organizing Swift Files"', metadata)
        self.assertIn(
            'short_description: "Keep Swift source trees concept-focused"',
            metadata,
        )
        self.assertIn("$organizing-swift-files", metadata)

    def test_evaluation_corpus_covers_required_boundaries(self):
        cases = load_json(PLUGIN_ROOT / "tests" / "evaluation-cases.json")
        self.assertEqual(
            {
                "separate-primary-types",
                "small-supporting-enum",
                "nested-struct",
                "extension-concerns",
                "feature-directory",
                "reorganize-before-feature",
                "reorganize-after-feature",
                "no-commit-authority",
                "generated-and-vendored-sources",
            },
            {case["id"] for case in cases},
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract test to verify it fails**

Run:

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
```

Expected: errors for missing `.codex-plugin/plugin.json`, marketplace entry, or skill metadata; the evaluation-corpus test passes.

- [ ] **Step 3: Scaffold the repo-local plugin and Codex marketplace entry**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/create_basic_plugin.py" \
  swift-code-organization \
  --path plugins \
  --with-skills \
  --with-marketplace \
  --marketplace-path .agents/plugins/marketplace.json \
  --category "Developer Tools"
```

Expected: plugin root, `.codex-plugin/plugin.json`, `skills/`, and one appended Codex marketplace entry. Do not use `--force`.

- [ ] **Step 4: Initialize the skill with generated Codex metadata**

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
  organizing-swift-files \
  --path plugins/swift-code-organization/skills \
  --interface display_name="Organizing Swift Files" \
  --interface short_description="Keep Swift source trees concept-focused" \
  --interface default_prompt='Use $organizing-swift-files to organize or review Swift source files.'
```

Expected: `SKILL.md` template and `agents/openai.yaml`. Do not add resource directories.

- [ ] **Step 5: Replace the Codex manifest defaults**

Set `.codex-plugin/plugin.json` to:

```json
{
  "name": "swift-code-organization",
  "version": "1.0.0",
  "description": "Personal Swift file, directory, and structural-commit organization conventions",
  "license": "MIT",
  "skills": "./skills/",
  "author": {
    "name": "Danny Sung",
    "url": "https://github.com/dannys42"
  },
  "repository": "https://github.com/dannys42/agent-skills",
  "keywords": [
    "swift",
    "ios",
    "macos",
    "file-organization",
    "project-structure",
    "refactoring",
    "agent-skills"
  ],
  "interface": {
    "displayName": "Swift Code Organization",
    "shortDescription": "Keep Swift source trees concept-focused",
    "longDescription": "Organize Swift types into focused files and concept directories while preserving reviewable structural and behavioral commits.",
    "developerName": "Danny Sung",
    "category": "Developer Tools",
    "capabilities": [
      "Swift file organization",
      "Feature directory organization",
      "Structural refactoring sequencing"
    ],
    "defaultPrompt": [
      "Organize or review these Swift source files and preserve clean commit boundaries."
    ]
  }
}
```

- [ ] **Step 6: Run the focused contract and manifest syntax check**

Run:

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
python3 -m json.tool plugins/swift-code-organization/.codex-plugin/plugin.json >/dev/null
```

Expected: all four contract tests pass and the Codex manifest parses. Defer the
full plugin validator until Task 3 replaces the skill scaffold's intentional
template markers.

- [ ] **Step 7: Commit the scaffold and packaging contract**

```bash
git add .agents/plugins/marketplace.json plugins/swift-code-organization/.codex-plugin plugins/swift-code-organization/skills/organizing-swift-files/agents plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md plugins/swift-code-organization/tests/test_plugin_contract.py
git commit -m "feat(swift-organization): scaffold plugin"
```

Expected: one scaffold commit; no Claude, Cursor, Gemini, README, or final skill guidance yet.

### Task 3: Write the Minimal Organization Skill

**Files:**
- Modify: `plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md`
- Modify: `plugins/swift-code-organization/tests/test_plugin_contract.py`

- [ ] **Step 1: Add failing content-contract tests**

Add these methods to `PluginContractTests`:

```python
    def test_skill_frontmatter_has_discoverable_trigger(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\nname: organizing-swift-files\n"))
        self.assertIn("description: Use when", skill)
        self.assertIn("creating", skill.split("---", 2)[1])
        self.assertIn("reviewing", skill.split("---", 2)[1])
        self.assertIn("reorganizing Swift", skill.split("---", 2)[1])

    def test_skill_preserves_primary_type_and_supporting_type_rules(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for declaration in ("`struct`", "`class`", "`actor`"):
            self.assertIn(declaration, skill)
        self.assertIn("own correspondingly named Swift file", skill)
        self.assertIn("supporting `enum` or `typealias`", skill)
        self.assertIn("Never apply this exception to another", skill)

    def test_skill_covers_nested_types_extensions_and_directories(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("TypeName+Concern.swift", skill)
        self.assertIn("extension of the enclosing type", skill)
        self.assertIn("feature or domain concept", skill)
        self.assertIn("declaration kind", skill)

    def test_skill_covers_commit_sequence_and_authority(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("reorganize first", skill)
        self.assertIn("behavioral change first", skill)
        self.assertIn("separate clean commit", skill)
        self.assertIn("not authorized", skill)

    def test_skill_limits_proactive_scope(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("new or meaningfully modified", skill)
        self.assertIn("unrelated repository-wide refactor", skill)

    def test_skill_has_no_scaffold_placeholders(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for placeholder in ("TODO", "TBD", "[TODO:"):
            self.assertNotIn(placeholder, skill)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
```

Expected: the four original tests pass and the six content tests fail against the scaffold template.

- [ ] **Step 3: Replace the skill template with the minimal guidance**

Write `SKILL.md` exactly as follows, adjusting only wording required by failures observed in Task 1:

```markdown
---
name: organizing-swift-files
description: Use when creating or substantially editing Swift source files, or when reviewing or reorganizing Swift file placement, project directories, SwiftUI views, extensions, type placement, feature folders, or codebases with unclear source ownership.
---

# Organizing Swift Files

## Core rule

Give every `struct`, `class`, and `actor` its own correspondingly named Swift
file. Treat every SwiftUI view as a struct under this rule.

Allow a supporting `enum` or `typealias` to remain with the primary type only
when it is a few lines, tightly coupled, and has no useful independent role.
Never apply this exception to another `struct`, `class`, or `actor`.

For a nested primary type, preserve qualified naming by declaring it in an
extension of the enclosing type in the nested type's own file.

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
```

- [ ] **Step 4: Run focused skill and plugin validation**

Run:

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/swift-code-organization/skills/organizing-swift-files
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/swift-code-organization
wc -w plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md
```

Expected: all ten contract tests pass; both validators exit 0; `SKILL.md` remains below 500 words.

- [ ] **Step 5: Commit the GREEN skill**

```bash
git add plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md plugins/swift-code-organization/tests/test_plugin_contract.py
git commit -m "feat(swift-organization): add file organization guidance"
```

### Task 4: Forward-Test and Refine the Skill

**Files:**
- Create: `plugins/swift-code-organization/tests/forward-results.md`
- Modify if behavioral evidence requires it: `plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md`
- Modify if a transferable requirement was missing: `plugins/swift-code-organization/tests/test_plugin_contract.py`

- [ ] **Step 1: Run every corpus case through fresh agents with the skill**

Use one fresh agent context per case. Concatenate the fixed instruction below
with that case's exact `prompt` value from `evaluation-cases.json`:

```text
Use $organizing-swift-files at
plugins/swift-code-organization/skills/organizing-swift-files to answer this
request:
```

Do not disclose the rubric requirements. Preserve each complete response verbatim in `forward-results.md` and score every requirement afterward.

- [ ] **Step 2: Verify GREEN behavior**

Expected: every requirement in all nine cases passes. Pay special attention to these common loopholes:

- calling nested structs "small helpers" and leaving them in the primary file;
- creating `Views`, `Models`, or `Enums` directories instead of concept directories;
- performing unrelated repository-wide cleanup during a focused request;
- mixing structural movement into the behavioral commit;
- creating commits without authority;
- editing generated or vendored sources.

- [ ] **Step 3: Refactor only for observed failures**

For each failed requirement, add the smallest transferable clarification to `SKILL.md`, add a focused static contract assertion only when it protects a stable rule, and rerun the failing scenario in a fresh context. Do not add hypothetical policy or inflate the skill beyond 500 words.

- [ ] **Step 4: Run focused validation after the last refinement**

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/swift-code-organization/skills/organizing-swift-files
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/swift-code-organization
```

Expected: all tests and validators pass; all forward cases are fully compliant.

- [ ] **Step 5: Commit behavioral evidence and refinements**

```bash
git add plugins/swift-code-organization/tests/forward-results.md plugins/swift-code-organization/skills/organizing-swift-files/SKILL.md plugins/swift-code-organization/tests/test_plugin_contract.py
git commit -m "test(swift-organization): verify skill behavior"
```

### Task 5: Add Portable Adapters and Plugin Documentation

**Files:**
- Create: `plugins/swift-code-organization/.claude-plugin/plugin.json`
- Create: `plugins/swift-code-organization/.cursor-plugin/plugin.json`
- Create: `plugins/swift-code-organization/gemini-extension.json`
- Create: `plugins/swift-code-organization/README.md`
- Create: `plugins/swift-code-organization/CHANGELOG.md`
- Create: `plugins/swift-code-organization/LICENSE`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.cursor-plugin/marketplace.json`
- Modify: `plugins/swift-code-organization/tests/test_plugin_contract.py`

- [ ] **Step 1: Add failing portable-adapter tests**

Add these methods to `PluginContractTests`:

```python
    def test_portable_plugin_manifests_match_name_and_version(self):
        for relative_path in (
            ".claude-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            "gemini-extension.json",
        ):
            with self.subTest(path=relative_path):
                manifest = load_json(PLUGIN_ROOT / relative_path)
                self.assertEqual("swift-code-organization", manifest["name"])
                self.assertEqual("1.0.0", manifest["version"])

    def test_repository_marketplaces_expose_plugin_once(self):
        marketplace_paths = (
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json",
            REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json",
        )
        for path in marketplace_paths:
            with self.subTest(path=path):
                marketplace = load_json(path)
                matches = [
                    plugin
                    for plugin in marketplace["plugins"]
                    if plugin["name"] == "swift-code-organization"
                ]
                self.assertEqual(1, len(matches))

    def test_plugin_documentation_names_skill_and_license(self):
        readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (PLUGIN_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        license_text = (PLUGIN_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("`organizing-swift-files`", readme)
        self.assertIn("2026 Danny Sung", license_text)
        self.assertIn("1.0.0", changelog)
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
```

Expected: existing tests pass; new adapter and documentation tests fail on missing files and entries.

- [ ] **Step 3: Add manifests matching repository conventions**

Create `.claude-plugin/plugin.json` as:

```json
{
  "name": "swift-code-organization",
  "version": "1.0.0",
  "description": "Personal Swift file, directory, and structural-commit organization conventions",
  "license": "MIT",
  "author": {
    "name": "Danny Sung"
  },
  "keywords": [
    "swift",
    "ios",
    "macos",
    "file-organization",
    "project-structure",
    "refactoring",
    "agent-skills"
  ]
}
```

Create `.cursor-plugin/plugin.json` as:

```json
{
  "name": "swift-code-organization",
  "displayName": "Swift Code Organization",
  "version": "1.0.0",
  "description": "Personal Swift file, directory, and structural-commit organization conventions",
  "license": "MIT",
  "author": {
    "name": "Danny Sung"
  },
  "repository": "https://github.com/dannys42/agent-skills",
  "keywords": [
    "swift",
    "ios",
    "macos",
    "file-organization",
    "project-structure",
    "refactoring",
    "agent-skills"
  ],
  "category": "developer-tools",
  "tags": [
    "swift",
    "organization",
    "refactoring"
  ],
  "skills": "./skills/"
}
```

Create `gemini-extension.json` as:

```json
{
  "name": "swift-code-organization",
  "version": "1.0.0",
  "description": "Personal Swift file, directory, and structural-commit organization conventions"
}
```

- [ ] **Step 4: Append marketplace entries without reordering existing plugins**

Append this Claude entry:

```json
{
  "name": "swift-code-organization",
  "source": "./plugins/swift-code-organization",
  "version": "1.0.0",
  "description": "Personal Swift file, directory, and structural-commit organization conventions",
  "category": "developer-tools",
  "keywords": ["swift", "ios", "macos", "file-organization", "project-structure", "refactoring", "agent-skills"],
  "tags": ["swift", "organization", "refactoring"]
}
```

Append this Cursor entry:

```json
{
  "name": "swift-code-organization",
  "source": "plugins/swift-code-organization",
  "version": "1.0.0",
  "description": "Personal Swift file, directory, and structural-commit organization conventions",
  "keywords": ["swift", "organization", "refactoring"]
}
```

- [ ] **Step 5: Add concise plugin documentation and licensing**

Write `README.md` as:

```markdown
# swift-code-organization

A cross-agent plugin for Danny Sung's Swift source organization preferences.

## Skills

### `organizing-swift-files`

Gives every Swift struct, class, and actor a focused file, groups related files
in concept directories, and keeps structural refactoring separate from
behavioral changes in Git history.

## Install

See the repository
[installation guide](../../README.md#install-organizing-swift-files) for the
complete supported-tool matrix and direct skill installation options.
```

Write the changelog as:

```markdown
# Changelog

## 1.0.0 — 2026-08-01

- Added `organizing-swift-files` for personal Swift source organization
- Added Claude, Codex, Cursor, and Gemini distribution adapters
- Added baseline and forward behavioral evaluation evidence
```

Copy the existing repository MIT license text from `plugins/swift-testing/LICENSE` to the new plugin without modification.

- [ ] **Step 6: Run focused adapter tests and JSON validation**

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
python3 -m json.tool plugins/swift-code-organization/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/swift-code-organization/.cursor-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/swift-code-organization/gemini-extension.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .cursor-plugin/marketplace.json >/dev/null
```

Expected: all tests pass and every JSON command exits 0.

- [ ] **Step 7: Commit portable distribution metadata**

```bash
git add .claude-plugin/marketplace.json .cursor-plugin/marketplace.json plugins/swift-code-organization/.claude-plugin plugins/swift-code-organization/.cursor-plugin plugins/swift-code-organization/gemini-extension.json plugins/swift-code-organization/README.md plugins/swift-code-organization/CHANGELOG.md plugins/swift-code-organization/LICENSE plugins/swift-code-organization/tests/test_plugin_contract.py
git commit -m "feat(swift-organization): add portable distribution"
```

### Task 6: Update Repository Discovery and Installation Documentation

**Files:**
- Modify: `README.md`
- Modify: `plugins/swift-code-organization/tests/test_plugin_contract.py`

- [ ] **Step 1: Add a failing root-documentation test**

Add:

```python
    def test_repository_readme_exposes_plugin_and_installation(self):
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("| `swift-code-organization` |", readme)
        self.assertIn("### `organizing-swift-files`", readme)
        self.assertIn("## Install `organizing-swift-files`", readme)
        self.assertIn("codex plugin add swift-code-organization@danny-sung-agent-skills", readme)
        self.assertIn("--skill organizing-swift-files", readme)
```

- [ ] **Step 2: Run the focused test to verify it fails**

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
```

Expected: only `test_repository_readme_exposes_plugin_and_installation` fails.

- [ ] **Step 3: Update root discovery and installation sections**

Add this row to the Plugins table without reordering existing rows:

```markdown
| `swift-code-organization` | `organizing-swift-files` | Focused Swift files, concept directories, and clean structural commits |
```

Add this entry to the Skills section:

```markdown
### `organizing-swift-files`

Organizes Swift source so every struct, class, and actor has a focused file,
related files live in feature or domain directories, and structural refactors
remain reviewable separately from behavioral changes.
```

Add `Install organizing-swift-files` with:

- canonical source `plugins/swift-code-organization/skills/organizing-swift-files`;
- Claude command `claude plugin install swift-code-organization@danny-sung-agent-skills`;
- Codex command `codex plugin add swift-code-organization@danny-sung-agent-skills`;
- open installer command using `--skill organizing-swift-files` and the existing agent-value table.

Add `plugins/swift-code-organization/gemini-extension.json` to the marketplace-adapters list.

- [ ] **Step 4: Run the focused contract suite**

```bash
python3 -m unittest plugins/swift-code-organization/tests/test_plugin_contract.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit repository documentation**

```bash
git add README.md plugins/swift-code-organization/tests/test_plugin_contract.py
git commit -m "docs: add Swift organization skill installation"
```

### Task 7: Final Verification and Review

**Files:**
- Verify all files above
- Modify only files needed to fix discovered defects

- [ ] **Step 1: Run focused plugin validation**

```bash
python3 -m unittest discover -s plugins/swift-code-organization/tests -p 'test_*.py' -v
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/swift-code-organization/skills/organizing-swift-files
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/swift-code-organization
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .cursor-plugin/marketplace.json >/dev/null
git diff --check main...HEAD
```

Expected: all plugin tests and validators pass, all JSON parses, and Git reports no whitespace errors.

- [ ] **Step 2: Run the complete repository baseline gate once**

```bash
python3 -m unittest discover -s plugins/skill-development-optimizer/tests -p 'test_*.py'
python3 -m unittest discover -s plugins/swift-design-patterns/tests -p 'test_*.py'
```

Expected: 250 optimizer tests pass with 1 expected skip; 91 Swift-design-pattern tests pass. Run outside the sandbox if the process-tree timeout test cannot send signals.

- [ ] **Step 3: Audit spec coverage and authority boundaries**

Read the final diff against `docs/superpowers/specs/2026-08-01-swift-code-organization-skill-design.md`. Confirm every struct/class/actor rule, supporting enum/typealias exception, nested-type preservation, extension split, concept hierarchy, pre-work reorganization decision, post-work cleanup sequence, constrained-source exception, and commit-authority limit appears in both the skill and relevant evaluation coverage.

- [ ] **Step 4: Review naming and packaging consistency**

Confirm the exact identifiers `swift-code-organization` and `organizing-swift-files`, version `1.0.0`, descriptions, author, repository, marketplace paths, and generated `openai.yaml` metadata agree across every adapter. Confirm there are no TODOs, caches, temporary files, personal paths, or unrelated changes.

- [ ] **Step 5: Commit only if final verification required a fix**

If verification changed tracked files, stage only this feature's known paths
and inspect the staged diff before committing:

```bash
git add README.md .agents/plugins/marketplace.json .claude-plugin/marketplace.json .cursor-plugin/marketplace.json plugins/swift-code-organization
git diff --cached --check
git commit -m "fix(swift-organization): resolve verification findings"
```

If verification required no changes, create no empty commit.

- [ ] **Step 6: Hand off with evidence**

Report the worktree path, branch, commit list, focused and full validation commands with exit status, behavioral case pass count, the expected skipped baseline test, and the untouched unrelated `claude-marketplace` entry. Then use `finishing-a-development-branch` to offer merge, PR, or branch-preservation options.
