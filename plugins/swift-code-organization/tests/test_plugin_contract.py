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
