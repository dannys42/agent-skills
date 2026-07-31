import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import SCRIPTS_ROOT, load_script


inspect_skill = load_script("inspect_skill")
optimizer_config = load_script("optimizer_config")


class SkillInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        subprocess.run(
            ["git", "init", "-q", str(self.repository)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.config_path = self.repository / "skill-optimizer.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def configuration(self, target):
        return {
            "schema_version": 1,
            "target": target,
            "distributable": {"include": ["**"], "exclude": []},
            "commands": {},
            "profiles": {
                "quick": [],
                "content": [],
                "behavior": [],
                "importer": [],
                "full": [],
            },
            "evaluations": {
                "cases": "future/evaluation-cases.json",
                "rubric": "future/evaluation-rubric.json",
            },
        }

    def write_configuration(self, target):
        self.config_path.write_text(
            json.dumps(self.configuration(target)),
            encoding="utf-8",
        )

    def load_configuration(self):
        return optimizer_config.load_config(self.config_path)

    def write_file(self, relative_path, text="fixture"):
        path = self.repository / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def create_plugin(
        self,
        root=Path("."),
        *,
        skill_name="example",
        plugin_name="fixture-plugin",
    ):
        target = root / "skills" / skill_name
        self.write_file(target / "SKILL.md", "# Example")
        self.write_file(target / "agents" / "openai.yaml", "name: Example")
        for manifest in (
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            "gemini-extension.json",
        ):
            self.write_file(root / manifest, json.dumps({"name": plugin_name}))
        return target

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPTS_ROOT / "inspect_skill.py"), *arguments],
            capture_output=True,
            text=True,
        )

    def test_plugin_inventory_has_exact_structure(self):
        target = self.create_plugin()
        self.write_file(target / "references" / "first.md")
        self.write_file(target / "references" / "nested" / "second.txt")
        self.write_file(target / "scripts" / "validate.py")
        self.write_file("tests/test_example.py")
        self.write_configuration(target.as_posix())

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(
            inventory,
            {
                "target": "skills/example",
                "skill": {
                    "name": "example",
                    "has_skill_md": True,
                    "has_openai_yaml": True,
                    "references": 2,
                    "scripts": 1,
                },
                "plugin_manifests": [
                    ".claude-plugin/plugin.json",
                    ".codex-plugin/plugin.json",
                    ".cursor-plugin/plugin.json",
                    "gemini-extension.json",
                ],
                "marketplace_adapters": [],
                "tests": 1,
                "has_optimizer_config": True,
            },
        )

    def test_standalone_skill_uses_tests_adjacent_to_target(self):
        self.write_file("standalone/SKILL.md")
        self.write_file("standalone/references/guide.md")
        self.write_file("tests/test_standalone.py")
        self.write_configuration("standalone")

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(inventory["plugin_manifests"], [])
        self.assertEqual(inventory["marketplace_adapters"], [])
        self.assertEqual(inventory["tests"], 1)
        self.assertEqual(inventory["target"], "standalone")

    def test_repository_root_standalone_does_not_count_sibling_tests(self):
        container = self.repository
        self.repository = container / "root-skill-repository"
        self.repository.mkdir()
        subprocess.run(
            ["git", "init", "-q", str(self.repository)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.config_path = self.repository / "skill-optimizer.json"
        self.write_file("SKILL.md")
        sibling_test = container / "tests" / "test_sibling.py"
        sibling_test.parent.mkdir()
        sibling_test.write_text("outside repository", encoding="utf-8")
        self.write_configuration(".")

        first = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(first["target"], ".")
        self.assertEqual(first["tests"], 0)

        real_walk = inspect_skill.os.walk

        def rejecting_outside_walk(root, *, followlinks, onerror=None):
            try:
                Path(root).relative_to(self.repository.resolve())
            except ValueError:
                if onerror is None:
                    raise AssertionError("os.walk onerror callback is required")
                onerror(
                    PermissionError(
                        13,
                        "Permission denied",
                        str(Path(root) / "private"),
                    )
                )
            return real_walk(
                root,
                followlinks=followlinks,
                onerror=onerror,
            )

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(
            inspect_skill.os,
            "walk",
            side_effect=rejecting_outside_walk,
        ):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = inspect_skill.main([str(self.config_path), "--json"])

        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stdout.getvalue())["tests"], 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn(str(container.resolve()), stdout.getvalue())

    def test_regular_file_count_rejects_root_outside_repository(self):
        outside_root = self.repository.parent / "absent-outside-root"

        with mock.patch.object(inspect_skill.os, "walk") as walk:
            with self.assertRaisesRegex(
                inspect_skill.InspectionError,
                r"cannot traverse path outside repository",
            ) as raised:
                inspect_skill._count_regular_files(
                    outside_root,
                    self.repository.resolve(),
                )

        walk.assert_not_called()
        self.assertNotIn(str(outside_root), str(raised.exception))

    def test_missing_skill_md_is_reported_in_inventory(self):
        (self.repository / "standalone").mkdir()
        self.write_configuration("standalone")

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertFalse(inventory["skill"]["has_skill_md"])

    def test_resource_counts_exclude_all_symlinks(self):
        target = self.create_plugin()
        target_path = self.repository / target
        real_reference = self.write_file(
            target / "references" / "nested" / "real.md"
        )
        real_script = self.write_file(target / "scripts" / "real.py")
        (target_path / "references" / "file-link.md").symlink_to(real_reference)
        (target_path / "scripts" / "file-link.py").symlink_to(real_script)
        (target_path / "references" / "broken").symlink_to("missing")
        (target_path / "scripts" / "broken").symlink_to("missing")
        outside = self.repository / "outside-resources"
        self.write_file("outside-resources/linked.md")
        self.write_file("outside-resources/linked.py")
        (target_path / "references" / "directory-link").symlink_to(
            outside,
            target_is_directory=True,
        )
        (target_path / "scripts" / "directory-link").symlink_to(
            outside,
            target_is_directory=True,
        )
        self.write_configuration(target.as_posix())

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(inventory["skill"]["references"], 1)
        self.assertEqual(inventory["skill"]["scripts"], 1)

    def test_nearest_plugin_root_excludes_unrelated_sibling_manifests(self):
        target = self.create_plugin(Path("plugins/selected"))
        self.write_file("plugins/unrelated/.codex-plugin/plugin.json", "{}")
        self.write_configuration(target.as_posix())

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(
            inventory["plugin_manifests"],
            [
                "plugins/selected/.claude-plugin/plugin.json",
                "plugins/selected/.codex-plugin/plugin.json",
                "plugins/selected/.cursor-plugin/plugin.json",
                "plugins/selected/gemini-extension.json",
            ],
        )

    def test_marketplace_adapter_is_reported_only_when_it_references_plugin(self):
        target = self.create_plugin(
            Path("plugins/selected"),
            plugin_name="selected",
        )
        self.write_file(
            ".agents/plugins/marketplace.json",
            json.dumps(
                {
                    "plugins": [
                        {
                            "name": "selected",
                            "source": {
                                "source": "local",
                                "path": "./plugins/selected",
                            },
                        }
                    ]
                }
            ),
        )
        self.write_file(".claude-plugin/marketplace.json", "{malformed")
        self.write_file(
            ".cursor-plugin/marketplace.json",
            json.dumps(
                {
                    "plugins": [
                        {
                            "name": "unrelated",
                            "source": {
                                "path": "plugins/unrelated",
                                "description": "plugins/selected",
                            },
                        },
                        {
                            "name": "selected",
                            "source": {"path": "plugins/unrelated"},
                        },
                        {
                            "name": "selected",
                            "source": "plugins/selected/",
                        },
                    ]
                }
            ),
        )
        self.write_configuration(target.as_posix())

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(
            inventory["marketplace_adapters"],
            [".agents/plugins/marketplace.json"],
        )

    def test_marketplace_identity_comes_from_provider_manifest_name(self):
        target = self.create_plugin(
            Path("plugins/directory-name"),
            plugin_name="manifest-name",
        )
        self.write_file(
            ".agents/plugins/marketplace.json",
            json.dumps(
                {
                    "plugins": [
                        {
                            "name": "manifest-name",
                            "source": "plugins/directory-name",
                        }
                    ]
                }
            ),
        )
        self.write_configuration(target.as_posix())

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(
            inventory["marketplace_adapters"],
            [".agents/plugins/marketplace.json"],
        )

    def test_conflicting_or_unusable_manifest_names_fail_closed(self):
        cases = ("conflicting", "unusable")
        for case in cases:
            with self.subTest(case=case):
                target = self.create_plugin(
                    Path(f"plugins/{case}"),
                    plugin_name="first-name",
                )
                if case == "conflicting":
                    self.write_file(
                        f"plugins/{case}/.codex-plugin/plugin.json",
                        json.dumps({"name": "second-name"}),
                    )
                    error_pattern = r"conflicting plugin names in plugins/conflicting"
                else:
                    for manifest in (
                        ".claude-plugin/plugin.json",
                        ".codex-plugin/plugin.json",
                        ".cursor-plugin/plugin.json",
                        "gemini-extension.json",
                    ):
                        self.write_file(
                            Path("plugins") / case / manifest,
                            json.dumps({"name": "   "}),
                        )
                    self.write_file(
                        f"plugins/{case}/.codex-plugin/plugin.json",
                        json.dumps({"name": 42}),
                    )
                    self.write_file(
                        f"plugins/{case}/.cursor-plugin/plugin.json",
                        json.dumps({"metadata": {"name": "nested-name"}}),
                    )
                    self.write_file(
                        f"plugins/{case}/gemini-extension.json",
                        "{malformed",
                    )
                    error_pattern = (
                        r"cannot determine plugin name from "
                        r"manifests in plugins/unusable"
                    )
                self.write_configuration(target.as_posix())

                with self.assertRaisesRegex(
                    inspect_skill.InspectionError,
                    error_pattern,
                ):
                    inspect_skill.inspect(self.load_configuration())

    def test_whitespace_padded_manifest_name_is_unusable(self):
        target = self.create_plugin(
            Path("plugins/padded"),
            plugin_name=" plugin-name ",
        )
        self.write_configuration(target.as_posix())

        with self.assertRaisesRegex(
            inspect_skill.InspectionError,
            r"cannot determine plugin name from manifests in plugins/padded",
        ):
            inspect_skill.inspect(self.load_configuration())

    def test_repository_root_plugin_source_dot_slash_matches(self):
        target = self.create_plugin(plugin_name="root-plugin")
        self.write_file(
            ".agents/plugins/marketplace.json",
            json.dumps(
                {
                    "plugins": [
                        {"name": "root-plugin", "source": "./"}
                    ]
                }
            ),
        )
        self.write_configuration(target.as_posix())

        inventory = inspect_skill.inspect(self.load_configuration())

        self.assertEqual(
            inventory["marketplace_adapters"],
            [".agents/plugins/marketplace.json"],
        )

    def test_traversal_errors_return_two_without_partial_inventory(self):
        target = self.create_plugin()
        (self.repository / target / "references").mkdir()
        (self.repository / "tests").mkdir()
        self.write_configuration(target.as_posix())
        real_walk = inspect_skill.os.walk

        failure_cases = (
            ("skills/example/references", "Permission denied"),
            ("tests", "OSError"),
        )
        for failing_relative_path, expected_reason in failure_cases:
            with self.subTest(path=failing_relative_path):
                def failing_walk(root, *, followlinks, onerror=None):
                    relative_root = (
                        Path(root)
                        .relative_to(self.repository.resolve())
                        .as_posix()
                    )
                    if relative_root == failing_relative_path:
                        if onerror is None:
                            raise AssertionError("os.walk onerror callback is required")
                        if failing_relative_path.endswith("references"):
                            onerror(
                                PermissionError(
                                    13,
                                    "Permission denied",
                                    str(Path(root) / "private"),
                                )
                            )
                        else:
                            onerror(
                                OSError(
                                    f"failure at {self.repository.resolve()}"
                                )
                            )
                    return real_walk(
                        root,
                        followlinks=followlinks,
                        onerror=onerror,
                    )

                stdout = io.StringIO()
                stderr = io.StringIO()
                with mock.patch.object(
                    inspect_skill.os,
                    "walk",
                    side_effect=failing_walk,
                ):
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        result = inspect_skill.main(
                            [str(self.config_path), "--json"]
                        )

                self.assertEqual(result, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual(
                    stderr.getvalue(),
                    "inspect_skill: cannot traverse "
                    f"{failing_relative_path}: {expected_reason}\n",
                )
                self.assertNotIn(str(self.repository), stderr.getvalue())

    def test_json_cli_output_is_sorted_deterministic_and_relative(self):
        target = self.create_plugin()
        self.write_configuration(target.as_posix())

        first = self.run_cli(str(self.config_path), "--json")
        second = self.run_cli(str(self.config_path), "--json")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(
            first.stdout,
            json.dumps(
                inspect_skill.inspect(self.load_configuration()),
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        self.assertNotIn(str(self.repository), first.stdout)

    def test_human_rendering_is_deterministic_and_useful(self):
        target = self.create_plugin()
        self.write_file(target / "references" / "guide.md")
        self.write_file("tests/test_example.py")
        self.write_configuration(target.as_posix())
        inventory = inspect_skill.inspect(self.load_configuration())

        rendered = inspect_skill.render_human(inventory)

        self.assertEqual(rendered, inspect_skill.render_human(inventory))
        self.assertEqual(
            rendered,
            "\n".join(
                [
                    "Target: skills/example",
                    "Skill: example",
                    "SKILL.md: yes",
                    "OpenAI metadata: yes",
                    "References: 1",
                    "Scripts: 0",
                    "Plugin manifests: 4",
                    "  - .claude-plugin/plugin.json",
                    "  - .codex-plugin/plugin.json",
                    "  - .cursor-plugin/plugin.json",
                    "  - gemini-extension.json",
                    "Marketplace adapters: 0",
                    "Tests: 1",
                    "Optimizer config: yes",
                ]
            ),
        )

    def test_cli_exit_codes_distinguish_config_and_skill_errors(self):
        missing_skill = self.repository / "missing-skill"
        missing_skill.mkdir()
        self.write_configuration("missing-skill")

        absent_skill_result = self.run_cli(str(self.config_path), "--json")
        self.write_file("missing-skill/SKILL.md")
        valid_config_result = self.run_cli(str(self.config_path), "--json")
        invalid_config_result = self.run_cli(
            str(self.repository / "absent-config.json"),
            "--json",
        )

        self.assertEqual(absent_skill_result.returncode, 1)
        self.assertFalse(
            json.loads(absent_skill_result.stdout)["skill"]["has_skill_md"]
        )
        self.assertEqual(
            absent_skill_result.stderr,
            "inspect_skill: missing required file: "
            "missing-skill/SKILL.md\n",
        )
        self.assertEqual(valid_config_result.returncode, 0)
        self.assertEqual(valid_config_result.stderr, "")
        self.assertEqual(invalid_config_result.returncode, 2)
        self.assertEqual(invalid_config_result.stdout, "")
        self.assertRegex(
            invalid_config_result.stderr,
            r"^inspect_skill: cannot read configuration ",
        )


if __name__ == "__main__":
    unittest.main()
