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
        self.assertIn(
            "State in every conformance recommendation",
            skill,
        )


if __name__ == "__main__":
    unittest.main()
