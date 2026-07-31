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


classify_change = load_script("classify_change")


class ChangeClassificationTests(unittest.TestCase):
    target = "plugins/example/skills/example"

    def classify(self, *paths):
        return classify_change.classify_paths(paths, self.target)

    def test_skill_md_is_behavior(self):
        result = self.classify(f"{self.target}/SKILL.md")

        self.assertEqual(result.profile, "behavior")
        self.assertEqual(result.categories, ("behavior",))
        self.assertEqual(
            result.reasons,
            (f"{self.target}/SKILL.md: skill instructions changed",),
        )

    def test_repository_root_target_classifies_skill_md(self):
        result = classify_change.classify_paths(("SKILL.md",), ".")

        self.assertEqual(result.profile, "behavior")
        self.assertEqual(result.categories, ("behavior",))

    def test_reference_and_content_support_paths_are_content(self):
        paths = (
            f"{self.target}/references/guide.md",
            f"{self.target}/references/README.md",
            f"{self.target}/examples/sample.md",
            f"{self.target}/examples/LICENSE",
            f"{self.target}/ATTRIBUTION.md",
            f"{self.target}/attribution/source.md",
            f"{self.target}/content-policy.md",
            f"{self.target}/content-policy/rules.md",
        )

        result = self.classify(*reversed(paths))

        self.assertEqual(result.profile, "content")
        self.assertEqual(result.categories, ("content",))
        self.assertEqual(result.paths, tuple(sorted(paths)))
        self.assertEqual(
            len(result.reasons),
            len(paths),
            "every classified path must have a path-specific reason",
        )
        for path, reason in zip(result.paths, result.reasons):
            self.assertTrue(reason.startswith(f"{path}: "))

    def test_importer_script_names_are_importer(self):
        for basename in ("import_catalog.py", "cache_manager.py"):
            with self.subTest(basename=basename):
                path = f"{self.target}/scripts/{basename}"

                result = self.classify(path)

                self.assertEqual(result.profile, "importer")
                self.assertEqual(result.categories, ("importer",))
                self.assertEqual(result.paths, (path,))
                self.assertIn("importer script", result.reasons[0])

    def test_production_script_with_test_prefix_is_not_tests_only(self):
        path = f"{self.target}/scripts/test_import.py"

        result = self.classify(path)

        self.assertEqual(result.profile, "importer")
        self.assertEqual(result.categories, ("importer",))

    def test_ordinary_production_script_fails_closed_to_full(self):
        path = f"{self.target}/scripts/validate.py"

        result = self.classify(path)

        self.assertEqual(result.profile, "full")
        self.assertEqual(result.categories, ("production",))
        self.assertEqual(result.paths, (path,))

    def test_unknown_distributable_path_fails_closed_to_full(self):
        path = f"{self.target}/templates/prompt.txt"

        result = self.classify(path)

        self.assertEqual(result.profile, "full")
        self.assertEqual(result.categories, ("unknown",))
        self.assertEqual(result.paths, (path,))

    def test_metadata_and_tests_are_quick(self):
        paths = (
            f"{self.target}/agents/openai.yaml",
            "plugins/example/.claude-plugin/plugin.json",
            "plugins/example/.codex-plugin/plugin.json",
            "plugins/example/.cursor-plugin/plugin.json",
            "plugins/example/gemini-extension.json",
            ".agents/plugins/marketplace.json",
            ".claude-plugin/marketplace.json",
            "nested/.agents/plugins/marketplace.json",
            "nested/.claude-plugin/marketplace.json",
            "nested/.cursor-plugin/marketplace.json",
            "plugins/example/README.md",
            "plugins/example/LICENSE",
            "tests/test_example.py",
        )

        result = self.classify(*paths)

        self.assertEqual(result.profile, "quick")
        self.assertEqual(result.categories, ("metadata", "tests"))
        self.assertEqual(result.paths, tuple(sorted(paths)))
        self.assertEqual(len(result.reasons), len(paths))

    def test_arbitrary_marketplace_basename_is_not_metadata(self):
        result = self.classify("nested/catalog/marketplace.json")

        self.assertEqual(result.profile, "full")
        self.assertEqual(result.categories, ("unknown",))

    def test_behavior_and_content_escalate_to_full(self):
        result = self.classify(
            f"{self.target}/SKILL.md",
            f"{self.target}/references/guide.md",
        )

        self.assertEqual(result.profile, "full")
        self.assertEqual(result.categories, ("behavior", "content"))

    def test_behavior_and_metadata_escalate_to_full(self):
        result = self.classify(
            f"{self.target}/SKILL.md",
            f"{self.target}/agents/openai.yaml",
        )

        self.assertEqual(result.profile, "full")
        self.assertEqual(result.categories, ("behavior", "metadata"))

    def test_content_and_metadata_escalate_to_full(self):
        result = self.classify(
            f"{self.target}/references/guide.md",
            f"{self.target}/agents/openai.yaml",
        )

        self.assertEqual(result.profile, "full")
        self.assertEqual(result.categories, ("content", "metadata"))

    def test_tests_do_not_escalate_one_production_category(self):
        result = self.classify(
            f"{self.target}/SKILL.md",
            "tests/test_example.py",
        )

        self.assertEqual(result.profile, "behavior")
        self.assertEqual(result.categories, ("behavior", "tests"))

    def test_no_paths_is_quick_with_exact_reason(self):
        result = self.classify()

        self.assertEqual(result.profile, "quick")
        self.assertEqual(result.categories, ())
        self.assertEqual(result.paths, ())
        self.assertEqual(result.reasons, ("no distributable changes",))

    def test_paths_are_sorted_unique_posix_and_target_match_is_segment_aware(self):
        behavior = f"{self.target}/SKILL.md"
        sibling = "plugins/example/skills/example-other/SKILL.md"

        result = self.classify(sibling, behavior, behavior)

        self.assertEqual(result.paths, tuple(sorted((behavior, sibling))))
        self.assertEqual(result.categories, ("behavior", "unknown"))
        self.assertEqual(result.profile, "full")

    def test_unsafe_paths_are_rejected(self):
        unsafe_paths = (
            "",
            ".",
            "/absolute/path",
            "../escape",
            "safe/../escape",
            r"ambiguous\path",
            "line\nbreak",
            "control\x01path",
            "next-line\u0085path",
            "format\u200epath",
            "surrogate\ud800path",
            "line-separator\u2028path",
            "paragraph-separator\u2029path",
        )
        for path in unsafe_paths:
            with self.subTest(path=path):
                with self.assertRaises(classify_change.ClassificationError):
                    self.classify(path)

    def test_ordinary_non_ascii_letters_are_allowed(self):
        path = f"{self.target}/references/café.md"

        result = self.classify(path)

        self.assertEqual(result.profile, "content")
        self.assertEqual(result.paths, (path,))


class GitPathCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        self.git("init", "-q")
        self.write("committed.txt", "initial")
        self.write("modified.txt", "initial")
        self.write("staged.txt", "initial")
        self.git("add", ".")
        self.commit("initial")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def git(self, *arguments):
        return subprocess.run(
            ["git", *arguments],
            cwd=self.repository,
            check=True,
            capture_output=True,
            text=True,
        )

    def commit(self, message):
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-q",
            "-m",
            message,
        )

    def write(self, relative_path, text):
        path = self.repository / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_collects_committed_modified_staged_untracked_and_deduplicates(self):
        self.write("committed.txt", "committed")
        self.git("add", "committed.txt")
        self.commit("second")
        self.write("committed.txt", "also modified")
        self.write("modified.txt", "modified")
        self.write("staged.txt", "staged")
        self.git("add", "staged.txt")
        self.write("untracked file.txt", "untracked")

        result = classify_change.collect_git_paths(self.repository, self.base)

        self.assertEqual(
            result,
            (
                "committed.txt",
                "modified.txt",
                "staged.txt",
                "untracked file.txt",
            ),
        )

    def test_collects_rename_source_and_destination_with_spaces(self):
        self.write("old name.txt", "rename")
        self.git("add", "old name.txt")
        self.commit("rename base")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("mv", "old name.txt", "new name.txt")

        result = classify_change.collect_git_paths(self.repository, base)

        self.assertEqual(result, ("new name.txt", "old name.txt"))

    def test_collects_deleted_path(self):
        self.write("deleted.txt", "delete")
        self.git("add", "deleted.txt")
        self.commit("delete base")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        (self.repository / "deleted.txt").unlink()

        result = classify_change.collect_git_paths(self.repository, base)

        self.assertEqual(result, ("deleted.txt",))

    def test_staged_skill_rename_collects_source_and_destination_and_escalates(self):
        source = "skills/example/SKILL.md"
        destination = "skills/example/README.md"
        self.write(source, "# Skill")
        self.git("add", source)
        self.commit("skill base")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("mv", source, destination)

        paths = classify_change.collect_git_paths(self.repository, base)
        classification = classify_change.classify_paths(paths, "skills/example")

        self.assertEqual(paths, (destination, source))
        self.assertEqual(classification.profile, "full")
        self.assertEqual(
            classification.categories,
            ("behavior", "metadata"),
        )

    def test_committed_rename_collects_source_and_destination(self):
        source = "skills/example/SKILL.md"
        destination = "skills/example/README.md"
        self.write(source, "# Skill")
        self.git("add", source)
        self.commit("skill base")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("mv", source, destination)
        self.commit("rename skill")

        result = classify_change.collect_git_paths(self.repository, base)

        self.assertEqual(result, (destination, source))

    def test_unstaged_tracked_move_collects_source_and_destination(self):
        source = "old tracked.txt"
        destination = "new tracked.txt"
        self.write(source, "move")
        self.git("add", source)
        self.commit("move base")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("mv", source, destination)
        self.git("reset", "-q", "HEAD", "--", source, destination)

        result = classify_change.collect_git_paths(self.repository, base)

        self.assertEqual(result, (destination, source))

    def test_git_error_is_controlled_without_absolute_repository_path(self):
        with self.assertRaises(classify_change.ClassificationError) as raised:
            classify_change.collect_git_paths(self.repository, "missing-ref")

        self.assertNotIn(str(self.repository), str(raised.exception))

    def test_base_option_injection_is_rejected_before_subprocess(self):
        for base in ("", "--src-prefix=owned"):
            with self.subTest(base=base):
                with mock.patch.object(
                    classify_change.subprocess,
                    "run",
                ) as run:
                    with self.assertRaises(classify_change.ClassificationError):
                        classify_change.collect_git_paths(self.repository, base)

                run.assert_not_called()


class ClassifierCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        subprocess.run(
            ["git", "init", "-q", str(self.repository)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.target = self.repository / "skills" / "example"
        self.target.mkdir(parents=True)
        self.config_path = self.repository / "optimizer.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "target": "skills/example",
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
                        "cases": "future/cases.json",
                        "rubric": "future/rubric.md",
                    },
                }
            ),
            encoding="utf-8",
        )
        (self.target / "SKILL.md").write_text("# Example", encoding="utf-8")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-q",
            "-m",
            "initial",
        )
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def git(self, *arguments):
        return subprocess.run(
            ["git", *arguments],
            cwd=self.repository,
            check=True,
            capture_output=True,
            text=True,
        )

    def run_cli(self, *arguments):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / "classify_change.py"),
                *arguments,
            ],
            capture_output=True,
            text=True,
        )

    def test_json_output_is_deterministic(self):
        (self.target / "SKILL.md").write_text("# Changed", encoding="utf-8")

        first = self.run_cli(str(self.config_path), "--base", self.base, "--json")
        second = self.run_cli(str(self.config_path), "--base", self.base, "--json")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(
            json.loads(first.stdout),
            {
                "categories": ["behavior"],
                "paths": ["skills/example/SKILL.md"],
                "profile": "behavior",
                "reasons": [
                    "skills/example/SKILL.md: skill instructions changed"
                ],
            },
        )
        self.assertEqual(first.stderr, "")

    def test_config_error_exits_two(self):
        missing = self.repository / "missing.json"

        result = self.run_cli(str(missing), "--json")

        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)
        self.assertNotIn(str(self.repository), result.stderr)

    def test_git_error_exits_two(self):
        result = self.run_cli(
            str(self.config_path),
            "--base",
            "missing-ref",
            "--json",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)
        self.assertNotIn(str(self.repository), result.stderr)

    def test_repository_inspection_exceptions_are_private_and_controlled(self):
        failures = (
            subprocess.CalledProcessError(
                128,
                ["git", "-C", str(self.repository), "rev-parse"],
                stderr=f"fatal: {self.repository}",
            ),
            OSError(f"failure at {self.repository}"),
        )
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with mock.patch.object(
                    classify_change.optimizer_config,
                    "load_config",
                    side_effect=failure,
                ):
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        result = classify_change.main(["ignored.json"])

                self.assertEqual(result, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertEqual(
                    stderr.getvalue(),
                    "classify_change: unable to inspect repository\n",
                )
                self.assertNotIn(str(self.repository), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
