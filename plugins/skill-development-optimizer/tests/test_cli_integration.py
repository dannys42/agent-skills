import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path, PureWindowsPath


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = PLUGIN_ROOT / "skill-optimizer.example.json"
BOOTSTRAP_CONFIG = (
    PLUGIN_ROOT
    / "skills"
    / "optimizing-skill-development"
    / "assets"
    / "skill-optimizer.example.json"
)
SCRIPTS_ROOT = (
    PLUGIN_ROOT / "skills" / "optimizing-skill-development" / "scripts"
)


class ExampleConfigurationTests(unittest.TestCase):
    def test_example_configuration_matches_the_documented_optimizer_contract(self):
        configuration = json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))

        self.assertEqual(
            configuration,
            {
                "schema_version": 1,
                "target": (
                    "plugins/skill-development-optimizer/skills/"
                    "optimizing-skill-development"
                ),
                "distributable": {
                    "include": [
                        "SKILL.md",
                        "agents/**/*.yaml",
                        "assets/**/*.json",
                        "references/**/*.md",
                        "scripts/**/*.py",
                    ],
                    "exclude": [
                        "**/__pycache__/**",
                        "**/*.pyc",
                    ],
                },
                "commands": {
                    "optimizer-tests": {
                        "argv": [
                            "python3",
                            "-m",
                            "unittest",
                            "discover",
                            "-s",
                            "plugins/skill-development-optimizer/tests",
                            "-v",
                        ],
                        "cwd": ".",
                        "timeout_seconds": 120,
                        "max_output_bytes": 1048576,
                        "network": False,
                        "timing_kind": "work",
                    }
                },
                "profiles": {
                    "quick": ["optimizer-tests"],
                    "content": ["optimizer-tests"],
                    "behavior": ["optimizer-tests"],
                    "importer": ["optimizer-tests"],
                    "full": ["optimizer-tests"],
                },
                "evaluations": {
                    "cases": (
                        "plugins/skill-development-optimizer/tests/"
                        "evaluation-cases.json"
                    ),
                    "rubric": (
                        "plugins/skill-development-optimizer/tests/"
                        "evaluation-rubric.json"
                    ),
                },
            },
        )

    def test_bundled_bootstrap_uses_repository_relative_example_paths(self):
        configuration = json.loads(BOOTSTRAP_CONFIG.read_text(encoding="utf-8"))

        self.assertEqual(configuration["schema_version"], 1)
        self.assertEqual(configuration["target"], "skills/example-skill")
        self.assertEqual(
            configuration["evaluations"],
            {
                "cases": "tests/evaluation-cases.json",
                "rubric": "tests/evaluation-rubric.json",
            },
        )
        self.assertIn("assets/**/*.json", configuration["distributable"]["include"])
        self.assertFalse(
            any(
                Path(value).is_absolute()
                for value in (
                    configuration["target"],
                    *configuration["evaluations"].values(),
                )
            )
        )


class IntegratedCliTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name).resolve()
        self.repository = self.root / "repository"
        self.caller = self.root / "arbitrary-caller"
        self.repository.mkdir()
        self.caller.mkdir()
        self.environment = os.environ.copy()
        self.environment.update(
            {
                "LC_ALL": "C",
                "LANG": "C",
                "GIT_AUTHOR_NAME": "Fixture Author",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_NAME": "Fixture Committer",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            }
        )
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(self.repository)],
            check=True,
            capture_output=True,
            text=True,
            env=self.environment,
        )
        self._create_complete_fixture()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_text(self, relative, content):
        path = self.repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, relative, value):
        return self.write_text(
            relative,
            json.dumps(value, indent=2, sort_keys=True) + "\n",
        )

    def git(self, *arguments):
        return subprocess.run(
            ["git", "-C", str(self.repository), *arguments],
            check=True,
            capture_output=True,
            text=True,
            env=self.environment,
        )

    def run_cli(self, script, *arguments):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_ROOT / f"{script}.py"),
                *map(str, arguments),
            ],
            cwd=self.caller,
            capture_output=True,
            text=True,
            env=self.environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertEqual(result.stderr, "")
        return result

    def parse_json(self, result):
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["schema_version"], 1)
        self.assert_sorted_json_objects(parsed)
        self.assert_no_absolute_paths(parsed)
        return parsed

    def assert_sorted_json_objects(self, value):
        if isinstance(value, dict):
            self.assertEqual(list(value), sorted(value))
            for item in value.values():
                self.assert_sorted_json_objects(item)
        elif isinstance(value, list):
            for item in value:
                self.assert_sorted_json_objects(item)

    def assert_no_absolute_paths(self, value):
        if isinstance(value, dict):
            for key, item in value.items():
                self.assert_no_absolute_paths(key)
                self.assert_no_absolute_paths(item)
        elif isinstance(value, list):
            for item in value:
                self.assert_no_absolute_paths(item)
        elif isinstance(value, str):
            path_tokens = [
                token.strip("\"'`()[]{}<>,;")
                for token in value.split()
            ]
            self.assertFalse(
                any(
                    token.startswith(("/", "\\"))
                    or PureWindowsPath(token).is_absolute()
                    for token in path_tokens
                ),
                f"absolute path leaked into JSON: {value}",
            )
            self.assertNotIn(str(self.root), value)

    def _create_complete_fixture(self):
        self.write_json(
            "fixture-plugin/.codex-plugin/plugin.json",
            {"name": "fixture-plugin"},
        )
        self.write_text(
            "fixture-plugin/skills/complete-skill/SKILL.md",
            "---\nname: complete-skill\ndescription: Complete fixture.\n---\n",
        )
        self.write_text(
            "fixture-plugin/skills/complete-skill/agents/openai.yaml",
            "interface:\n  display_name: Complete fixture\n",
        )
        self.write_text(
            "fixture-plugin/skills/complete-skill/references/guide.md",
            "# Fixture guide\n",
        )
        self.write_text(
            "fixture-plugin/skills/complete-skill/scripts/check.py",
            "print('fixture script')\n",
        )
        self.write_text(
            "fixture-plugin/tests/test_fixture.py",
            "import unittest\n\n"
            "class FixtureTest(unittest.TestCase):\n"
            "    def test_fixture(self):\n"
            "        self.assertTrue(True)\n",
        )
        self.write_json(
            "fixture-plugin/tests/evaluation-cases.json",
            [
                {
                    "id": "case-1",
                    "prompt": "Inspect the complete fixture skill.",
                }
            ],
        )
        self.write_json(
            "fixture-plugin/tests/evaluation-rubric.json",
            ["accurate", "grounded"],
        )

        configuration = json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))
        configuration["target"] = (
            "fixture-plugin/skills/complete-skill"
        )
        configuration["commands"] = {
            "fixture-check": {
                "argv": [
                    "python3",
                    "-c",
                    "print('fixture validation passed')",
                ],
                "cwd": ".",
                "timeout_seconds": 10,
                "max_output_bytes": 4096,
                "network": False,
                "timing_kind": "work",
            }
        }
        configuration["profiles"] = {
            profile: ["fixture-check"]
            for profile in ("quick", "content", "behavior", "importer", "full")
        }
        configuration["evaluations"] = {
            "cases": "fixture-plugin/tests/evaluation-cases.json",
            "rubric": "fixture-plugin/tests/evaluation-rubric.json",
        }
        self.config = self.write_json("skill-optimizer.json", configuration)
        self.git("add", ".")
        self.git("commit", "-q", "-m", "fixture baseline")
        self.write_text(
            "fixture-plugin/skills/complete-skill/references/guide.md",
            "# Updated fixture guide\n",
        )

    def test_all_clis_compose_from_an_arbitrary_working_directory(self):
        inspect_first = self.run_cli("inspect_skill", self.config, "--json")
        inspect_second = self.run_cli("inspect_skill", self.config, "--json")
        self.assertEqual(inspect_first.stdout, inspect_second.stdout)
        inspection = self.parse_json(inspect_first)
        self.assertTrue(inspection["skill"]["has_skill_md"])

        classify_first = self.run_cli("classify_change", self.config, "--json")
        classify_second = self.run_cli("classify_change", self.config, "--json")
        self.assertEqual(classify_first.stdout, classify_second.stdout)
        classification = self.parse_json(classify_first)
        self.assertIn(
            "fixture-plugin/skills/complete-skill/references/guide.md",
            classification["paths"],
        )

        artifact_path = self.repository / "artifact.json"
        hash_first = self.run_cli(
            "hash_artifact",
            self.config,
            "--json",
            "--output",
            artifact_path,
        )
        hash_second = self.run_cli("hash_artifact", self.config, "--json")
        self.assertEqual(hash_first.stdout, hash_second.stdout)
        artifact = self.parse_json(hash_first)
        self.assertEqual(
            artifact,
            json.loads(artifact_path.read_text(encoding="utf-8")),
        )

        report_path = self.repository / "validation-report.json"
        validation_result = self.run_cli(
            "run_validation",
            self.config,
            "quick",
            "--output",
            report_path,
        )
        self.assertEqual(validation_result.stdout, "")
        validation_report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(validation_report["schema_version"], 1)
        self.assert_no_absolute_paths(validation_report)

        cases = self.repository / "fixture-plugin/tests/evaluation-cases.json"
        rubric = self.repository / "fixture-plugin/tests/evaluation-rubric.json"
        evidence_path = self.repository / "evaluation/evidence.json"
        initialized = self.parse_json(
            self.run_cli(
                "manage_evidence",
                "init",
                artifact_path,
                cases,
                rubric,
                evidence_path,
                "--cohort",
                "integrated",
            )
        )
        self.assertEqual(
            initialized["artifact"]["digest"],
            artifact["digest"],
        )
        self.assertEqual(
            initialized["cohorts"][0]["artifact_digest"],
            artifact["digest"],
        )
        completion_path = self.write_json(
            "evaluation-completion.json",
            {
                "schema_version": 1,
                "cohort_id": "integrated",
                "runs": [
                    {
                        "case_id": "case-1",
                        "response": "The fixture is complete.\n",
                        "files_read": "SKILL.md\nreferences/guide.md\n",
                        "files_read_kind": "agent-reported",
                        "rubric": {"accurate": True, "grounded": True},
                    }
                ],
            },
        )
        completed = self.parse_json(
            self.run_cli(
                "manage_evidence",
                "complete",
                evidence_path,
                cases,
                rubric,
                completion_path,
            )
        )
        self.assertEqual(completed["artifact"]["digest"], artifact["digest"])
        self.assertEqual(
            completed["cohorts"][0]["artifact_digest"],
            artifact["digest"],
        )

        verified = self.parse_json(
            self.run_cli(
                "manage_evidence",
                "verify",
                evidence_path,
                cases,
                rubric,
                "--json",
            )
        )
        self.assertEqual(verified["diagnostics"], [])
        self.assertTrue(verified["valid"])

        summarized = self.parse_json(
            self.run_cli(
                "manage_evidence",
                "summarize",
                evidence_path,
                cases,
                rubric,
                "--json",
            )
        )
        self.assertEqual(summarized["passed"], summarized["total"])

        timing = self.parse_json(
            self.run_cli(
                "report_timing",
                report_path,
                "--json",
            )
        )
        self.assertEqual(timing["command_count"], 1)
        self.assertEqual(timing["status_counts"]["passed"], 1)

    def test_json_privacy_assertion_checks_keys_and_portable_absolute_paths(self):
        unsafe_values = (
            {"/private/key": "value"},
            {"key": "/private/value"},
            {"key": "C:\\private\\value"},
            {"key": "C:/private/value"},
            {"key": "\\\\server\\share\\private"},
            {"C:\\private\\key": "value"},
            {"diagnostic": "failed at /absolute/private"},
            {"diagnostic": "failed at C:\\absolute\\private"},
            {"diagnostic": "failed at \\\\server\\share\\private"},
            {"diagnostic": "failed at \\absolute\\private"},
        )
        for value in unsafe_values:
            with self.subTest(value=value):
                with self.assertRaises(AssertionError):
                    self.assert_no_absolute_paths(value)

        self.assert_no_absolute_paths(
            {
                "identifier": "sha256-length-framed-v1",
                "relative": "fixture-plugin/skills/example",
                "windows-looking-identifier": "profile:C",
            }
        )

    @unittest.skipUnless(
        os.environ.get("RUN_SKILL_OPTIMIZER_BENCHMARKS") == "1",
        "set RUN_SKILL_OPTIMIZER_BENCHMARKS=1 for local timing evidence",
    )
    def test_local_cli_medians_are_below_one_second_for_existing_plugins(self):
        self.measured_medians = {}
        repository_root = PLUGIN_ROOT.parents[1]
        plugin_targets = {
            "swift-testing": "skills/naming-swift-tests",
            "swift-design-patterns": "skills/choosing-swift-design-patterns",
        }
        self.write_json("benchmark-cases.json", [{"id": "case", "prompt": "Check."}])
        self.write_json("benchmark-rubric.json", ["correct"])

        for plugin_name, skill_relative in plugin_targets.items():
            source = repository_root / "plugins" / plugin_name
            destination = self.repository / "benchmark-plugins" / plugin_name
            shutil.copytree(
                source,
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            target = f"benchmark-plugins/{plugin_name}/{skill_relative}"
            configuration = {
                "schema_version": 1,
                "target": target,
                "distributable": {
                    "include": [
                        "SKILL.md",
                        "agents/**/*.yaml",
                        "references/**/*.md",
                        "scripts/**/*.py",
                    ],
                    "exclude": ["**/__pycache__/**", "**/*.pyc"],
                },
                "commands": {
                    "fixture-check": {
                        "argv": ["python3", "-c", "pass"],
                        "cwd": ".",
                        "timeout_seconds": 10,
                        "max_output_bytes": 4096,
                        "network": False,
                        "timing_kind": "work",
                    }
                },
                "profiles": {
                    profile: ["fixture-check"]
                    for profile in (
                        "quick",
                        "content",
                        "behavior",
                        "importer",
                        "full",
                    )
                },
                "evaluations": {
                    "cases": "benchmark-cases.json",
                    "rubric": "benchmark-rubric.json",
                },
            }
            config = self.write_json(
                f"benchmark-{plugin_name}.json",
                configuration,
            )
            medians = {}
            for script in ("inspect_skill", "classify_change", "hash_artifact"):
                durations = []
                for _ in range(10):
                    started = time.perf_counter()
                    self.run_cli(script, config, "--json")
                    durations.append(time.perf_counter() - started)
                medians[script] = statistics.median(durations)

            for script, median in medians.items():
                self.measured_medians[(plugin_name, script)] = median
                with self.subTest(plugin=plugin_name, script=script):
                    self.assertLess(median, 1.0)


if __name__ == "__main__":
    unittest.main()
