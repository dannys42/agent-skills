import hashlib
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
        self.assertEqual("local", matches[0]["source"]["source"])
        self.assertEqual("Developer Tools", matches[0]["category"])
        self.assertEqual("AVAILABLE", matches[0]["policy"]["installation"])
        self.assertEqual("ON_INSTALL", matches[0]["policy"]["authentication"])

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

        self.assertEqual(3, pre_fix.count("#### Verbatim response"))
        self.assertEqual(3, pre_fix.count("#### Requirement scoring"))
        self.assertEqual(12, final.count("#### Verbatim response"))
        self.assertEqual(12, final.count("#### Requirement scoring"))
        self.assertIn("eb3342c6b16bfb452956cefcaeceffa80f47d525", pre_fix)
        self.assertIn(
            "b3b5e3c4e23574a5131ef37a56b0a1f7103694866e19ba3e9c1d6a5415edbcfc",
            pre_fix,
        )
        self.assertIn("e0acf75444be95aa3966edaec041f1c7a1e46445", final)
        self.assertIn(
            "c5b61e6b1ebfa44690c478eb91c3e8a6fefe50ace1faed600d65d9469dcfa13d",
            final,
        )

        skill = (SKILL_ROOT / "SKILL.md").read_bytes()
        self.assertIn(hashlib.sha256(skill).hexdigest(), final)
        corrected_prompt = (
            "A non-generic parse(_:) function declares a function-local "
            "struct Cursor with an index and advance() method."
        )
        self.assertEqual(2, report.count(corrected_prompt))
        self.assertIn("swiftc -typecheck", report)
        self.assertIn("func parse(_ input: String) -> Int", report)
        self.assertIn("Fixture type-check exit: `0`", report)

        for section, case_count in ((pre_fix, 3), (final, 12)):
            pass_count = section.count("- PASS —")
            fail_count = section.count("- FAIL —")
            requirement_count = pass_count + fail_count
            self.assertIn(
                f"**{pass_count} PASS and {fail_count} FAIL across "
                f"{requirement_count} requirements;",
                section,
            )
            fully_passing = section.count(
                "of " + str(case_count) + " cases fully passed"
            )
            self.assertEqual(1, fully_passing)

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
        self.assertIn(
            "For every move or retained exception, verify compilation",
            skill,
        )
        self.assertIn(
            "Always end every organization recommendation",
            skill,
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
