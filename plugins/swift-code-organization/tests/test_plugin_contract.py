import hashlib
import json
import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).parents[1]
REPOSITORY_ROOT = PLUGIN_ROOT.parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "organizing-swift-files"
PLUGIN_NAME = "swift-code-organization"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = (
    "Personal Swift file, directory, and structural-commit organization "
    "conventions"
)
PLUGIN_REPOSITORY = "https://github.com/dannys42/agent-skills"
PLUGIN_KEYWORDS = [
    "swift",
    "ios",
    "macos",
    "file-organization",
    "project-structure",
    "refactoring",
    "agent-skills",
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class PluginContractTests(unittest.TestCase):
    def test_codex_manifest_identifies_skill_plugin(self):
        manifest = load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual(
            {"name": "Danny Sung", "url": "https://github.com/dannys42"},
            manifest["author"],
        )
        self.assertEqual(PLUGIN_REPOSITORY, manifest["repository"])
        self.assertEqual(PLUGIN_KEYWORDS, manifest["keywords"])
        self.assertEqual(
            {
                "displayName": "Swift Code Organization",
                "shortDescription": "Keep Swift source trees concept-focused",
                "longDescription": (
                    "Organize Swift types into focused files and concept "
                    "directories while preserving reviewable structural and "
                    "behavioral commits."
                ),
                "developerName": "Danny Sung",
                "category": "Developer Tools",
                "capabilities": [
                    "Swift file organization",
                    "Feature directory organization",
                    "Structural refactoring sequencing",
                ],
                "defaultPrompt": [
                    "Organize or review these Swift source files and preserve "
                    "clean commit boundaries."
                ],
            },
            manifest["interface"],
        )

    def test_codex_marketplace_exposes_plugin_once(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json"
        )
        matches = [
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == PLUGIN_NAME
        ]
        self.assertEqual(
            [
                {
                    "name": PLUGIN_NAME,
                    "source": {
                        "source": "local",
                        "path": "./plugins/swift-code-organization",
                    },
                    "policy": {
                        "installation": "AVAILABLE",
                        "authentication": "ON_INSTALL",
                    },
                    "category": "Developer Tools",
                }
            ],
            matches,
        )

    def test_portable_plugin_manifests_share_canonical_identity(self):
        for relative_path in (
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            "gemini-extension.json",
        ):
            with self.subTest(path=relative_path):
                manifest = load_json(PLUGIN_ROOT / relative_path)
                self.assertEqual(PLUGIN_NAME, manifest["name"])
                self.assertEqual(PLUGIN_VERSION, manifest["version"])
                self.assertEqual(PLUGIN_DESCRIPTION, manifest["description"])

    def test_claude_manifest_uses_provider_metadata(self):
        manifest = load_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json")
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual({"name": "Danny Sung"}, manifest["author"])
        self.assertEqual(PLUGIN_KEYWORDS, manifest["keywords"])

    def test_cursor_manifest_uses_provider_metadata(self):
        manifest = load_json(PLUGIN_ROOT / ".cursor-plugin" / "plugin.json")
        self.assertEqual("Swift Code Organization", manifest["displayName"])
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual({"name": "Danny Sung"}, manifest["author"])
        self.assertEqual(PLUGIN_REPOSITORY, manifest["repository"])
        self.assertEqual(PLUGIN_KEYWORDS, manifest["keywords"])
        self.assertEqual("developer-tools", manifest["category"])
        self.assertEqual(
            ["swift", "organization", "refactoring"], manifest["tags"]
        )
        self.assertEqual("./skills/", manifest["skills"])

    def test_gemini_manifest_contains_only_canonical_identity(self):
        manifest = load_json(PLUGIN_ROOT / "gemini-extension.json")
        self.assertEqual(
            {
                "name": PLUGIN_NAME,
                "version": PLUGIN_VERSION,
                "description": PLUGIN_DESCRIPTION,
            },
            manifest,
        )

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
                    if plugin["name"] == PLUGIN_NAME
                ]
                self.assertEqual(1, len(matches))

    def test_claude_marketplace_uses_canonical_plugin_entry(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json"
        )
        entry = next(
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == PLUGIN_NAME
        )
        self.assertEqual(
            {
                "name": PLUGIN_NAME,
                "source": "./plugins/swift-code-organization",
                "version": PLUGIN_VERSION,
                "description": PLUGIN_DESCRIPTION,
                "category": "developer-tools",
                "keywords": PLUGIN_KEYWORDS,
                "tags": ["swift", "organization", "refactoring"],
            },
            entry,
        )

    def test_cursor_marketplace_uses_canonical_plugin_entry(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json"
        )
        entry = next(
            plugin
            for plugin in marketplace["plugins"]
            if plugin["name"] == PLUGIN_NAME
        )
        self.assertEqual(
            {
                "name": PLUGIN_NAME,
                "source": "plugins/swift-code-organization",
                "description": PLUGIN_DESCRIPTION,
            },
            entry,
        )

    def test_cursor_marketplace_uses_supported_entry_fields(self):
        marketplace = load_json(
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json"
        )
        supported_fields = {
            "name",
            "source",
            "description",
            "minClientVersions",
        }
        for plugin in marketplace["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertLessEqual(set(plugin), supported_fields)

    def test_plugin_documentation_names_skill_and_license(self):
        readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (PLUGIN_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        license_text = (PLUGIN_ROOT / "LICENSE").read_text(encoding="utf-8")
        reference_license = (
            REPOSITORY_ROOT / "plugins" / "swift-testing" / "LICENSE"
        ).read_text(encoding="utf-8")
        self.assertIn("`organizing-swift-files`", readme)
        self.assertEqual(reference_license, license_text)
        self.assertIn("1.0.0", changelog)

    def test_repository_readme_exposes_plugin_and_installation(self):
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("| `swift-code-organization` |", readme)
        self.assertIn("### `organizing-swift-files`", readme)
        self.assertIn("## Install `organizing-swift-files`", readme)
        self.assertIn(
            "codex plugin add swift-code-organization@danny-sung-agent-skills",
            readme,
        )
        self.assertIn("--skill organizing-swift-files", readme)

    def test_openai_metadata_is_complete(self):
        metadata = (
            SKILL_ROOT / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            """interface:
  display_name: "Organizing Swift Files"
  short_description: "Keep Swift source trees concept-focused"
  default_prompt: "Use $organizing-swift-files to organize or review Swift source files."
""",
            metadata,
        )

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

    def test_compiler_feasibility_corpus_has_unique_required_cases(self):
        cases = load_json(
            PLUGIN_ROOT / "tests" / "compiler-feasibility-cases.json"
        )
        identifiers = [case["id"] for case in cases]
        self.assertEqual(
            {
                "function-local-type",
                "cross-file-private-extension",
                "synthesized-conformance",
            },
            set(identifiers),
        )
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_compiler_feasibility_corpus_matches_canonical_cases(self):
        cases = load_json(
            PLUGIN_ROOT / "tests" / "compiler-feasibility-cases.json"
        )
        self.assertEqual(
            [
                {
                    "id": "function-local-type",
                    "prompt": (
                        "A non-generic parse(_:) function declares a "
                        "function-local struct Cursor with an index and "
                        "advance() method. Cursor is used only inside parse "
                        "and is never exposed. Apply the Swift "
                        "file-organization preference, but this must remain "
                        "a structural-only change with no behavior, API, "
                        "access-level, or ownership changes."
                    ),
                    "requirements": [
                        "recognizes that a function-local type cannot move "
                        "to another file while retaining lexical scope",
                        "does not widen or change the type's scope solely to "
                        "satisfy the file rule",
                        "keeps the declaration in place or treats scope "
                        "redesign as a separate intentional change and "
                        "verifies compilation",
                    ],
                },
                {
                    "id": "cross-file-private-extension",
                    "prompt": (
                        "Vault.swift defines a Vault class with private key "
                        "material and a fileprivate helper. A small Vault "
                        "extension in the same file accesses both. Apply the "
                        "file-organization preference by considering "
                        "Vault+Crypto.swift, but the requested change must "
                        "remain structural-only."
                    ),
                    "requirements": [
                        "recognizes that moving the extension cross-file "
                        "loses private or fileprivate access",
                        "keeps the extension in the original file unless "
                        "access redesign is separately authorized",
                        "does not widen access solely to satisfy file "
                        "organization and verifies compilation",
                    ],
                },
                {
                    "id": "synthesized-conformance",
                    "prompt": (
                        "Record.swift declares a struct Record with private "
                        "stored properties and synthesized Equatable, "
                        "Hashable, and Codable conformances. Consider moving "
                        "those conformances to Record+Conformance.swift as a "
                        "structural-only reorganization."
                    ),
                    "requirements": [
                        "recognizes same-file constraints for synthesized "
                        "conformances and stored-property access",
                        "keeps synthesis with the declaration unless "
                        "explicit conformance implementation is separately "
                        "authorized",
                        "does not hand-write conformances or widen access "
                        "solely to satisfy layout and verifies compilation",
                    ],
                },
            ],
            cases,
        )

    def test_compiler_feasibility_evidence_has_integrity(self):
        report = (
            PLUGIN_ROOT / "tests" / "forward-results-v2.md"
        ).read_text(encoding="utf-8")
        pre_fix, final = report.split("## Final 12-case cohort", 1)

        self.assertIn(
            "Pre-fix snapshot: commit "
            "`eb3342c6b16bfb452956cefcaeceffa80f47d525`, skill SHA-256 "
            "`b3b5e3c4e23574a5131ef37a56b0a1f7103694866e19ba3e9c1d6a5415edbcfc`.",
            pre_fix,
        )
        self.assertIn(
            "Unaffected snapshot: commit "
            "`e0acf75444be95aa3966edaec041f1c7a1e46445`, skill SHA-256 "
            "`c5b61e6b1ebfa44690c478eb91c3e8a6fefe50ace1faed600d65d9469dcfa13d`.",
            final,
        )
        self.assertIn(
            "Corrected snapshot: base commit "
            "`e0acf75444be95aa3966edaec041f1c7a1e46445`, skill SHA-256 "
            "`4c43e4939492f1ac52bcb41c03248dd66565bf5f06db304729ae5bbf8f935579`.",
            final,
        )

        skill = (SKILL_ROOT / "SKILL.md").read_bytes()
        self.assertIn(
            "Post-evidence wording snapshot: base commit "
            "`377f19593c1384cd4cce81abd77f7e7945227c5d`, skill SHA-256 `"
            + hashlib.sha256(skill).hexdigest()
            + "`; not evaluated by the final cohort.",
            final,
        )
        corrected_prompt = (
            "A non-generic parse(_:) function declares a function-local "
            "struct Cursor with an index and advance() method."
        )
        self.assertEqual(2, report.count(corrected_prompt))
        self.assertIn(
            "swiftc -warnings-as-errors -typecheck "
            "${TMPDIR}/swift-org-durable-fixture.swift",
            report,
        )
        self.assertIn("func parse(_ input: String) -> Int", report)
        self.assertIn("Fixture type-check exit: `0`", report)
        self.assertIn("Captured `swift --version`:", report)
        self.assertIn("Captured target triple:", report)
        self.assertIn("Compiler stdout: empty", report)
        self.assertIn("Compiler stderr: empty", report)
        self.assertIn("Warning status: none", report)
        fixture = re.search(
            r"```swift\n(.*?)```",
            report,
            re.DOTALL,
        ).group(1)
        self.assertIn(
            "Fixture SHA-256: `"
            + hashlib.sha256(fixture.encode()).hexdigest()
            + "`",
            report,
        )

        original_cases = load_json(
            PLUGIN_ROOT / "tests" / "evaluation-cases.json"
        )
        feasibility_cases = load_json(
            PLUGIN_ROOT / "tests" / "compiler-feasibility-cases.json"
        )
        requirements = {
            case["id"]: case["requirements"]
            for case in original_cases + feasibility_cases
        }

        def scored_cases(section):
            matches = list(
                re.finditer(r"^### ([a-z0-9][a-z0-9-]*)$", section, re.MULTILINE)
            )
            parsed = {}
            for index, match in enumerate(matches):
                case_id = match.group(1)
                self.assertNotIn(case_id, parsed)
                end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
                body = section[match.end():end]
                scores = re.findall(
                    r"^- (PASS|FAIL) — `([^`]+)`: ",
                    body,
                    re.MULTILINE,
                )
                self.assertEqual(requirements[case_id], [score[1] for score in scores])
                parsed[case_id] = [score[0] for score in scores]
            return parsed

        expected_pre_fix = {case["id"] for case in feasibility_cases}
        expected_final = set(requirements)
        for section, expected_ids in (
            (pre_fix, expected_pre_fix),
            (final, expected_final),
        ):
            cases = scored_cases(section)
            self.assertEqual(expected_ids, set(cases))
            pass_count = sum(scores.count("PASS") for scores in cases.values())
            fail_count = sum(scores.count("FAIL") for scores in cases.values())
            fully_passing = sum(all(score == "PASS" for score in scores) for scores in cases.values())
            requirement_count = sum(len(scores) for scores in cases.values())
            self.assertIn(
                f"**{pass_count} PASS and {fail_count} FAIL across "
                f"{requirement_count} requirements;",
                section,
            )
            self.assertIn(
                f"{fully_passing} of {len(expected_ids)} cases fully passed",
                section,
            )

    def test_skill_frontmatter_has_discoverable_trigger(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\nname: organizing-swift-files\n"))
        self.assertIn("description: Use when", skill)
        self.assertIn("creating", skill.split("---", 2)[1])
        self.assertIn("reviewing", skill.split("---", 2)[1])
        self.assertIn(
            "reviewing Swift physical organization",
            skill.split("---", 2)[1],
        )
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
        self.assertIn("EnclosingType+NestedType.swift", skill)
        self.assertIn("TypeName+Concern.swift", skill)
        self.assertIn("TypeName+ProtocolName.swift", skill)
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

    def test_skill_preserves_swift_compiler_feasibility(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        normalized_skill = " ".join(skill.split())
        for guidance in (
            "function-local",
            "lexical scope",
            "private",
            "fileprivate",
            "synthesized",
            "separate authorization",
            "Do not widen access",
            "verify compilation",
        ):
            self.assertIn(guidance, skill)
        self.assertNotIn(
            "For every move or retained exception, verify compilation",
            skill,
        )
        self.assertIn(
            "When the project is available, run relevant builds and tests "
            "and report actual results.",
            normalized_skill,
        )
        self.assertIn(
            "Otherwise state the exact verification to run without implying "
            "it ran.",
            normalized_skill,
        )
        self.assertNotIn("every conformance recommendation", skill)
        self.assertIn(
            "access widening or manual conformance implementation requires "
            "separate authorization",
            normalized_skill,
        )
        self.assertIn("When synthesis would break, state", skill)


if __name__ == "__main__":
    unittest.main()
