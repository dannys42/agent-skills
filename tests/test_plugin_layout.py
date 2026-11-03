import json
import re
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
    "task-workflow": {"decision-driven-design", "tasklist", "tasklist-run"},
    "project-planning": {"system-design", "risk-first-roadmap", "plan-milestone", "code-quality-pass", "rung", "design-session"},
    "storytelling": {"crafting-compelling-stories"},
}
# Claude Code mods: hooks modules, listed in the Claude marketplace only.
MODS = {"peak-hours"}
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
        self.assertEqual(set(BUNDLE_SKILLS) | MODS, found)

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

    def test_each_mod_has_a_manifest_and_hooks(self):
        for mod in MODS:
            with self.subTest(mod=mod):
                manifest = load_json(PLUGINS_ROOT / mod / ".claude-plugin/plugin.json")
                self.assertEqual(mod, manifest["name"])
                self.assertTrue((PLUGINS_ROOT / mod / "hooks/hooks.json").is_file())

    def test_every_marketplace_lists_each_bundle_once(self):
        paths = (
            REPOSITORY_ROOT / ".agents" / "plugins" / "marketplace.json",
            REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
            REPOSITORY_ROOT / ".cursor-plugin" / "marketplace.json",
        )
        for path in paths:
            names = [plugin["name"] for plugin in load_json(path)["plugins"]]
            expected = set(BUNDLE_SKILLS)
            if path.parent.name == ".claude-plugin":
                expected |= MODS
            with self.subTest(marketplace=str(path.relative_to(REPOSITORY_ROOT))):
                self.assertEqual(sorted(expected), sorted(names))

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

    def test_claude_marketplace_versions_match_the_manifests(self):
        marketplace = load_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")
        for plugin in marketplace["plugins"]:
            with self.subTest(plugin=plugin["name"]):
                manifest = load_json(PLUGINS_ROOT / plugin["name"] / ".claude-plugin/plugin.json")
                self.assertEqual(manifest["version"], plugin["version"])


# Bundles whose skills write the metrics log; every event's `skill` is `<skill name> <plugin version>`.
METRIC_BUNDLES = ("task-workflow", "project-planning")
PLAN_TOOLS = PLUGINS_ROOT / "task-workflow" / "tools" / "plantools"


class MetricStampTests(unittest.TestCase):
    """Run `scripts/bump_version.py <plugin> <version>` to keep these in step."""

    def test_every_stamp_names_the_current_plugin_version(self):
        for bundle in METRIC_BUNDLES:
            version = load_json(PLUGINS_ROOT / bundle / ".claude-plugin/plugin.json")["version"]
            names = sorted(BUNDLE_SKILLS[bundle], key=len, reverse=True)
            stamp = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, names)) + r") (\d+\.\d+\.\d+)")
            for path in (PLUGINS_ROOT / bundle / "skills").rglob("*.md"):
                for name, found in stamp.findall(path.read_text(encoding="utf-8")):
                    with self.subTest(file=str(path.relative_to(REPOSITORY_ROOT)), stamp=f"{name} {found}"):
                        self.assertEqual(version, found)

    def test_every_skill_that_logs_a_step_gives_its_stamp(self):
        for bundle in METRIC_BUNDLES:
            version = load_json(PLUGINS_ROOT / bundle / ".claude-plugin/plugin.json")["version"]
            for skill in BUNDLE_SKILLS[bundle]:
                text = (PLUGINS_ROOT / bundle / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                if "`step` event" in text or "metrics.jsonl" in text:
                    with self.subTest(skill=skill):
                        self.assertIn(f"{skill} {version}", text)

    def test_plan_tool_version_checks_match_the_tool(self):
        tool = re.search(r'planToolsVersion = "([\d.]+)"', (PLAN_TOOLS / "Sources/PlanKit/CLI.swift").read_text()).group(1)
        key = lambda v: tuple(int(n) for n in v.split("."))
        tasklist = (PLUGINS_ROOT / "task-workflow/skills/tasklist/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(f"If it fails or is not `{tool}`" in tasklist, f"tasklist's tool check must name {tool}")
        minimums = []
        for path in (PLUGINS_ROOT / "project-planning/skills").rglob("*"):
            if path.suffix in (".md", ".sh"):
                text = path.read_text(encoding="utf-8")
                minimums += [(path, v) for v in re.findall(r"older than `?([\d]+\.[\d]+\.[\d]+)", text)]
                minimums += [(path, v) for v in re.findall(r"^min=([\d.]+)$", text, re.M)]
        self.assertTrue(minimums)
        floor = max(key(v) for _, v in minimums)
        for path, v in minimums:
            with self.subTest(file=str(path.relative_to(REPOSITORY_ROOT))):
                self.assertLessEqual(key(v), key(tool))
                self.assertEqual(floor, key(v), "every project-planning check names the same minimum")


if __name__ == "__main__":
    unittest.main()
