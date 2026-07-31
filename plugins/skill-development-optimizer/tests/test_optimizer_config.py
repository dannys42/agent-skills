import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import load_script


optimizer_config = load_script("optimizer_config")


class OptimizerConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        subprocess.run(
            ["git", "init", "-q", str(self.repository)],
            check=True,
            capture_output=True,
            text=True,
        )
        (self.repository / "skill").mkdir()
        (self.repository / "nested").mkdir()
        self.config_path = self.repository / "nested" / "optimizer.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def valid_configuration(self):
        return {
            "schema_version": 1,
            "target": "skill",
            "distributable": {
                "include": ["SKILL.md", "references/**"],
                "exclude": ["tests/**"],
            },
            "commands": {
                "quick-validate": {
                    "argv": ["python3", "validate.py"],
                    "cwd": "skill",
                    "timeout_seconds": 30,
                    "max_output_bytes": 4096,
                    "network": False,
                    "timing_kind": "work",
                },
                "wait-for-import": {
                    "argv": ["python3", "wait.py"],
                    "cwd": ".",
                    "timeout_seconds": 60.5,
                    "max_output_bytes": 8192,
                    "network": True,
                    "timing_kind": "mandatory_wait",
                },
            },
            "profiles": {
                "quick": ["quick-validate"],
                "content": ["quick-validate"],
                "behavior": ["quick-validate"],
                "importer": ["wait-for-import"],
                "full": ["quick-validate", "wait-for-import"],
            },
            "evaluations": {
                "cases": "future/evaluation-cases.json",
                "rubric": "future/rubric.md",
            },
        }

    def write_configuration(self, configuration=None, *, raw=None):
        if raw is None:
            raw = json.dumps(
                self.valid_configuration()
                if configuration is None
                else configuration
            )
        self.config_path.write_text(raw, encoding="utf-8")

    def load(self):
        return optimizer_config.load_config(self.config_path)

    def assert_config_error(self, pattern):
        return self.assertRaisesRegex(optimizer_config.ConfigError, pattern)

    def test_valid_config_loads_resolved_paths_and_profile_tuples(self):
        self.write_configuration()

        loaded = self.load()

        self.assertEqual(loaded.repository_root, self.repository.resolve())
        self.assertEqual(loaded.target_root, (self.repository / "skill").resolve())
        self.assertEqual(loaded.profiles["quick"], ("quick-validate",))
        self.assertEqual(loaded.includes, ("SKILL.md", "references/**"))
        self.assertEqual(
            loaded.commands["quick-validate"].argv,
            ("python3", "validate.py"),
        )
        repository_stat = self.repository.resolve().stat()
        self.assertEqual(
            loaded.repository_identity,
            (repository_stat.st_dev, repository_stat.st_ino),
        )

    def test_command_cwd_traversal_is_rejected(self):
        configuration = self.valid_configuration()
        configuration["commands"]["quick-validate"]["cwd"] = "../outside"
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"command 'quick-validate' cwd escapes repository: \.\./outside"
        ):
            self.load()

    def test_string_argv_is_rejected(self):
        configuration = self.valid_configuration()
        configuration["commands"]["quick-validate"]["argv"] = "python validate.py"
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"command 'quick-validate' argv must be a non-empty array of strings"
        ):
            self.load()

    def test_schema_version_must_be_one(self):
        configuration = self.valid_configuration()
        configuration["schema_version"] = 2
        self.write_configuration(configuration)

        with self.assert_config_error(r"schema_version must be 1"):
            self.load()

    def test_malformed_json_is_reported_as_config_error(self):
        self.write_configuration(raw="{not json")

        with self.assert_config_error(r"invalid JSON"):
            self.load()

    def test_duplicate_top_level_member_is_rejected(self):
        raw = json.dumps(self.valid_configuration()).replace(
            '"target": "skill"',
            '"target": "skill", "target": "skill"',
            1,
        )
        self.write_configuration(raw=raw)

        with self.assert_config_error(r"duplicate JSON member: target"):
            self.load()

    def test_duplicate_nested_security_field_is_rejected(self):
        raw = json.dumps(self.valid_configuration()).replace(
            '"network": false',
            '"network": false, "network": false',
            1,
        )
        self.write_configuration(raw=raw)

        with self.assert_config_error(r"duplicate JSON member: network"):
            self.load()

    def test_duplicate_command_identifier_is_rejected(self):
        configuration = self.valid_configuration()
        duplicate_command = json.dumps(
            configuration["commands"]["quick-validate"]
        )
        raw = json.dumps(configuration).replace(
            '"commands": {',
            f'"commands": {{"quick-validate": {duplicate_command}, ',
            1,
        )
        self.write_configuration(raw=raw)

        with self.assert_config_error(r"duplicate JSON member: quick-validate"):
            self.load()

    def test_invalid_utf8_is_reported_as_config_error(self):
        self.config_path.write_bytes(b"\xff")

        with self.assert_config_error(
            r"cannot read configuration '.*optimizer\.json': invalid UTF-8"
        ):
            self.load()

    def test_missing_configuration_is_reported_as_config_error(self):
        missing_path = self.repository / "missing.json"

        with self.assert_config_error(r"cannot read configuration '.*missing\.json':"):
            optimizer_config.load_config(missing_path)

    def test_directory_configuration_is_reported_as_config_error(self):
        with self.assert_config_error(r"cannot read configuration '.*nested':"):
            optimizer_config.load_config(self.config_path.parent)

    def test_absolute_target_is_rejected(self):
        configuration = self.valid_configuration()
        configuration["target"] = str(self.repository / "skill")
        self.write_configuration(configuration)

        with self.assert_config_error(r"target must be a repository-relative path"):
            self.load()

    def test_target_traversal_is_rejected(self):
        configuration = self.valid_configuration()
        configuration["target"] = "../outside"
        self.write_configuration(configuration)

        with self.assert_config_error(r"target escapes repository: \.\./outside"):
            self.load()

    def test_missing_target_is_config_error(self):
        configuration = self.valid_configuration()
        configuration["target"] = "missing"
        self.write_configuration(configuration)

        with self.assert_config_error(r"target does not exist: missing"):
            self.load()

    def test_regular_file_target_is_rejected(self):
        (self.repository / "file-target").write_text("not a skill root")
        configuration = self.valid_configuration()
        configuration["target"] = "file-target"
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"target must be a directory: file-target"
        ):
            self.load()

    def test_nul_in_configured_path_is_reported_as_config_error(self):
        configuration = self.valid_configuration()
        configuration["target"] = "invalid\u0000target"
        self.write_configuration(configuration)

        with self.assert_config_error(r"target cannot be resolved:"):
            self.load()

    def test_symlink_target_escape_is_rejected(self):
        outside = self.repository.parent / f"{self.repository.name}-outside"
        outside.mkdir()
        (self.repository / "escaping-link").symlink_to(outside, target_is_directory=True)
        self.addCleanup(outside.rmdir)
        configuration = self.valid_configuration()
        configuration["target"] = "escaping-link"
        self.write_configuration(configuration)

        with self.assert_config_error(r"target escapes repository: escaping-link"):
            self.load()

    def test_empty_distributable_patterns_are_rejected(self):
        for collection_name in ("include", "exclude"):
            with self.subTest(collection_name=collection_name):
                configuration = self.valid_configuration()
                configuration["distributable"][collection_name] = [""]
                self.write_configuration(configuration)

                with self.assert_config_error(
                    rf"distributable {collection_name} must contain non-empty strings"
                ):
                    self.load()

    def test_empty_argv_element_is_rejected(self):
        configuration = self.valid_configuration()
        configuration["commands"]["quick-validate"]["argv"] = ["python3", ""]
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"command 'quick-validate' argv must be a non-empty array of strings"
        ):
            self.load()

    def test_timeout_seconds_bounds_and_types_are_rejected(self):
        for value in (0, 3600.01, "30", True, None):
            with self.subTest(value=value):
                configuration = self.valid_configuration()
                configuration["commands"]["quick-validate"][
                    "timeout_seconds"
                ] = value
                self.write_configuration(configuration)

                with self.assert_config_error(
                    r"command 'quick-validate' timeout_seconds must be a number from 1 to 3600"
                ):
                    self.load()

    def test_max_output_bytes_bounds_and_types_are_rejected(self):
        for value in (0, 16_777_217, 1.5, "4096", True, None):
            with self.subTest(value=value):
                configuration = self.valid_configuration()
                configuration["commands"]["quick-validate"][
                    "max_output_bytes"
                ] = value
                self.write_configuration(configuration)

                with self.assert_config_error(
                    r"command 'quick-validate' max_output_bytes must be an integer from 1 to 16777216"
                ):
                    self.load()

    def test_network_must_be_boolean(self):
        configuration = self.valid_configuration()
        configuration["commands"]["quick-validate"]["network"] = 1
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"command 'quick-validate' network must be a boolean"
        ):
            self.load()

    def test_timing_kind_must_be_supported(self):
        configuration = self.valid_configuration()
        configuration["commands"]["quick-validate"]["timing_kind"] = "sleep"
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"command 'quick-validate' timing_kind must be work or mandatory_wait"
        ):
            self.load()

    def test_unknown_profile_command_is_rejected(self):
        configuration = self.valid_configuration()
        configuration["profiles"]["quick"] = ["unknown"]
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"profile 'quick' references unknown command: unknown"
        ):
            self.load()

    def test_every_required_profile_must_be_present(self):
        for profile_name in optimizer_config.PROFILE_NAMES:
            with self.subTest(profile_name=profile_name):
                configuration = self.valid_configuration()
                del configuration["profiles"][profile_name]
                self.write_configuration(configuration)

                with self.assert_config_error(
                    rf"profiles must contain exactly: .*{profile_name}"
                ):
                    self.load()

    def test_evaluation_paths_cannot_escape(self):
        for name in ("cases", "rubric"):
            with self.subTest(name=name):
                configuration = self.valid_configuration()
                configuration["evaluations"][name] = "../outside"
                self.write_configuration(configuration)

                with self.assert_config_error(
                    rf"evaluations {name} escapes repository: \.\./outside"
                ):
                    self.load()

    def test_non_git_directory_falls_back_to_config_parent(self):
        non_git_directory = tempfile.TemporaryDirectory()
        self.addCleanup(non_git_directory.cleanup)
        non_git_root = Path(non_git_directory.name)
        (non_git_root / "skill").mkdir()
        self.config_path = non_git_root / "optimizer.json"
        self.write_configuration()

        loaded = self.load()

        self.assertEqual(loaded.repository_root, non_git_root.resolve())

    def test_git_root_is_discovered_from_nested_config_parent(self):
        deeper = self.repository / "nested" / "deeper"
        deeper.mkdir()
        self.config_path = deeper / "optimizer.json"
        self.write_configuration()

        loaded = self.load()

        self.assertEqual(loaded.repository_root, self.repository.resolve())

    def test_git_discovery_uses_deterministic_locale_and_preserves_environment(self):
        result = subprocess.CompletedProcess(
            ["git"],
            0,
            stdout=f"{self.repository}\n",
            stderr="",
        )
        with mock.patch.object(
            optimizer_config.subprocess,
            "run",
            return_value=result,
        ) as run:
            optimizer_config.discover_repository_root(self.config_path.parent)

        environment = run.call_args.kwargs["env"]
        self.assertEqual(environment["LC_ALL"], "C")
        self.assertEqual(environment["LANG"], "C")
        if "PATH" in os.environ:
            self.assertEqual(environment["PATH"], os.environ["PATH"])

    def test_empty_or_relative_git_root_is_rejected(self):
        cases = (
            ("", r"Git repository root is empty"),
            ("relative/root", r"Git repository root must be absolute: relative/root"),
        )
        for stdout, error_pattern in cases:
            with self.subTest(stdout=stdout):
                result = subprocess.CompletedProcess(
                    ["git"],
                    0,
                    stdout=f"{stdout}\n",
                    stderr="",
                )
                with mock.patch.object(
                    optimizer_config.subprocess,
                    "run",
                    return_value=result,
                ):
                    with self.assert_config_error(error_pattern):
                        optimizer_config.discover_repository_root(
                            self.config_path.parent
                        )

    def test_arbitrary_git_execution_failure_is_not_silently_fallback(self):
        failure = subprocess.CalledProcessError(
            128,
            ["git"],
            stderr="fatal: unsafe repository",
        )
        with mock.patch.object(
            optimizer_config.subprocess,
            "run",
            side_effect=failure,
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                optimizer_config.discover_repository_root(self.config_path.parent)

    def test_missing_config_parent_is_reported_as_config_error(self):
        missing_parent = self.repository / "missing-parent"

        with self.assert_config_error(
            r"cannot resolve configuration parent '.*missing-parent':"
        ):
            optimizer_config.discover_repository_root(missing_parent)

    def test_missing_git_root_is_reported_as_config_error(self):
        missing_root = self.repository / "vanished-root"
        result = subprocess.CompletedProcess(
            ["git"],
            0,
            stdout=f"{missing_root}\n",
            stderr="",
        )

        with mock.patch.object(
            optimizer_config.subprocess,
            "run",
            return_value=result,
        ):
            with self.assert_config_error(
                r"cannot resolve Git repository root '.*vanished-root':"
            ):
                optimizer_config.discover_repository_root(self.config_path.parent)

    def test_missing_command_cwd_is_config_error(self):
        configuration = self.valid_configuration()
        configuration["commands"]["quick-validate"]["cwd"] = "missing"
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"command 'quick-validate' cwd does not exist: missing"
        ):
            self.load()

    def test_symlink_command_cwd_escape_is_rejected(self):
        outside = self.repository.parent / f"{self.repository.name}-outside-cwd"
        outside.mkdir()
        (self.repository / "cwd-link").symlink_to(outside, target_is_directory=True)
        self.addCleanup(outside.rmdir)
        configuration = self.valid_configuration()
        configuration["commands"]["quick-validate"]["cwd"] = "cwd-link"
        self.write_configuration(configuration)

        with self.assert_config_error(
            r"command 'quick-validate' cwd escapes repository: cwd-link"
        ):
            self.load()

    def test_unknown_and_missing_required_keys_are_rejected(self):
        configurations = []
        missing = self.valid_configuration()
        del missing["target"]
        configurations.append(missing)
        unknown = self.valid_configuration()
        unknown["unexpected"] = True
        configurations.append(unknown)

        for configuration in configurations:
            with self.subTest(configuration=configuration):
                self.write_configuration(configuration)
                with self.assert_config_error(r"keys"):
                    self.load()

    def test_wrong_container_types_are_rejected(self):
        for key in ("distributable", "commands", "profiles", "evaluations"):
            with self.subTest(key=key):
                configuration = self.valid_configuration()
                configuration[key] = []
                self.write_configuration(configuration)

                with self.assert_config_error(r"must be an object"):
                    self.load()


if __name__ == "__main__":
    unittest.main()
