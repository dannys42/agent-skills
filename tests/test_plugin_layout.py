import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[1]
PLUGINS_ROOT = REPOSITORY_ROOT / "plugins"
BUNDLE_SKILLS = {
    "swift-craft": {
        "naming-swift-tests",
        "choosing-swift-design-patterns",
        "organizing-swift-files",
    },
    "agent-engineering": {
        "optimizing-skill-development",
        "audit-token-efficiency",
    },
    "task-workflow": {"decision-driven-design"},
    "storytelling": {"crafting-compelling-stories"},
}
PORTABLE_MANIFESTS = (
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class PluginLayoutTests(unittest.TestCase):
    def test_plugins_directory_contains_exactly_the_bundles(self):
        found = {path.name for path in PLUGINS_ROOT.iterdir() if path.is_dir()}
        self.assertEqual(set(BUNDLE_SKILLS), found)

    def test_each_bundle_contains_exactly_its_skills(self):
        for bundle, skills in BUNDLE_SKILLS.items():
            with self.subTest(bundle=bundle):
                found = {
                    path.name
                    for path in (PLUGINS_ROOT / bundle / "skills").iterdir()
                    if path.is_dir()
                }
                self.assertEqual(skills, found)
                for skill in skills:
                    self.assertTrue(
                        (PLUGINS_ROOT / bundle / "skills" / skill / "SKILL.md").is_file()
                    )

    def test_portable_manifests_share_identity(self):
        for bundle in BUNDLE_SKILLS:
            codex = load_json(PLUGINS_ROOT / bundle / ".codex-plugin/plugin.json")
            for relative in PORTABLE_MANIFESTS:
                with self.subTest(bundle=bundle, manifest=relative):
                    manifest = load_json(PLUGINS_ROOT / bundle / relative)
                    for key in ("name", "version", "description"):
                        self.assertEqual(codex[key], manifest[key])
                    self.assertEqual(bundle, manifest["name"])

    def test_every_marketplace_lists_each_bundle_once(self):
        paths = (
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json",
            REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json",
        )
        for path in paths:
            names = [plugin["name"] for plugin in load_json(path)["plugins"]]
            with self.subTest(marketplace=str(path.relative_to(REPOSITORY_ROOT))):
                self.assertEqual(sorted(BUNDLE_SKILLS), sorted(names))

    def test_marketplace_sources_point_at_existing_bundles(self):
        for path, key in (
            (REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json", "source"),
            (REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json", "source"),
        ):
            for plugin in load_json(path)["plugins"]:
                with self.subTest(path=path.parent.name, plugin=plugin["name"]):
                    source = plugin[key].removeprefix("./")
                    self.assertEqual(f"plugins/{plugin['name']}", source)
        for plugin in load_json(
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json"
        )["plugins"]:
            with self.subTest(path="codex", plugin=plugin["name"]):
                self.assertEqual(
                    f"./plugins/{plugin['name']}", plugin["source"]["path"]
                )

    def test_cursor_marketplace_uses_supported_entry_fields(self):
        marketplace = load_json(REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json")
        supported = {"name", "source", "description", "minClientVersions"}
        for plugin in marketplace["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                self.assertLessEqual(set(plugin), supported)


if __name__ == "__main__":
    unittest.main()
