import contextlib
import concurrent.futures
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import SCRIPTS_ROOT, load_script


manage_evidence = load_script("manage_evidence")

DIGEST = "a" * 64
RUBRIC = ("correct_profile", "mandatory_checks_present")
CASES = (
    {"id": "case-1", "prompt": "Choose the smallest adequate profile."},
)


def artifact_manifest():
    return {
        "schema_version": 1,
        "algorithm": "sha256-length-framed-v1",
        "digest": DIGEST,
        "target": "skills/example",
        "files": [{"path": "SKILL.md", "bytes": 12}],
    }


def valid_evidence():
    return {
        "schema_version": 1,
        "artifact": {
            "algorithm": "sha256-length-framed-v1",
            "digest": DIGEST,
            "manifest": "artifact.json",
        },
        "headline_cohort": "final",
        "cohorts": [
            {
                "id": "final",
                "status": "headline",
                "artifact_digest": DIGEST,
                "runs": [
                    {
                        "id": "final-case-1",
                        "case_id": "case-1",
                        "prompt": "runs/final-case-1/prompt.md",
                        "response": "runs/final-case-1/response.md",
                        "files_read": "runs/final-case-1/files-read.txt",
                        "files_read_kind": "agent-reported",
                        "rubric": {
                            "correct_profile": True,
                            "mandatory_checks_present": True,
                        },
                    }
                ],
            }
        ],
    }


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.write_json("artifact.json", artifact_manifest())
        self.write_text(
            "runs/final-case-1/prompt.md",
            CASES[0]["prompt"] + "\n",
        )
        self.write_text("runs/final-case-1/response.md", "Use quick.\n")
        self.write_text("runs/final-case-1/files-read.txt", "SKILL.md\n")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_text(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, relative, value):
        return self.write_text(relative, json.dumps(value, sort_keys=True) + "\n")

    def errors(self, evidence=None, cases=CASES, rubric=RUBRIC):
        return manage_evidence.validate_evidence(
            self.root,
            valid_evidence() if evidence is None else evidence,
            cases,
            rubric,
        )

    def test_accepts_complete_frozen_headline(self):
        self.assertEqual(self.errors(), [])

    def test_rejects_mixed_artifact_hashes_in_headline_cohort(self):
        evidence = valid_evidence()
        evidence["cohorts"][0]["artifact_digest"] = "b" * 64
        self.assertEqual(
            self.errors(evidence),
            ["cohort 'final' artifact digest does not match frozen artifact"],
        )

    def test_rejects_multiple_headline_cohorts(self):
        evidence = valid_evidence()
        other = {
            **evidence["cohorts"][0],
            "id": "other",
            "runs": [],
            "status": "headline",
        }
        evidence["cohorts"].append(other)
        self.assertIn(
            "evidence must contain exactly one headline cohort",
            self.errors(evidence),
        )

    def test_computes_score_from_declared_rubric(self):
        summary = manage_evidence.summarize(valid_evidence(), RUBRIC)
        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["total"], 2)

    def test_summary_rejects_draft_and_malformed_historical_cohorts(self):
        draft = valid_evidence()
        draft["cohorts"][0]["runs"][0] = {
            "id": "final-case-1",
            "case_id": "case-1",
            "prompt": "runs/final-case-1/prompt.md",
        }
        with self.assertRaisesRegex(manage_evidence.EvidenceError, "incomplete"):
            manage_evidence.summarize(draft, RUBRIC)

        empty = valid_evidence()
        empty["cohorts"][0]["runs"] = []
        with self.assertRaisesRegex(manage_evidence.EvidenceError, "incomplete"):
            manage_evidence.summarize(empty, RUBRIC)

        malformed = valid_evidence()
        malformed["cohorts"].append(
            {
                "id": "prior",
                "status": "historical",
                "artifact_digest": "b" * 64,
                "runs": [
                    {
                        **malformed["cohorts"][0]["runs"][0],
                        "id": "final-case-1",
                    }
                ],
            }
        )
        with self.assertRaisesRegex(manage_evidence.EvidenceError, "duplicate run id"):
            manage_evidence.summarize(malformed, RUBRIC)

    def test_summary_rejects_multiple_or_mixed_headline_cohorts(self):
        evidence = valid_evidence()
        evidence["cohorts"].append(
            {
                **evidence["cohorts"][0],
                "id": "other",
                "artifact_digest": "b" * 64,
                "runs": [],
            }
        )

        with self.assertRaisesRegex(
            manage_evidence.EvidenceError,
            "headline|artifact",
        ):
            manage_evidence.summarize(evidence, RUBRIC)

    def test_summary_rejects_duplicate_headline_case_ids(self):
        evidence = valid_evidence()
        evidence["cohorts"][0]["runs"].append(
            {
                **evidence["cohorts"][0]["runs"][0],
                "id": "second-run",
            }
        )
        with self.assertRaisesRegex(
            manage_evidence.EvidenceError,
            "duplicate case id: case-1",
        ):
            manage_evidence.summarize(evidence, RUBRIC)

    def test_summary_accepts_retired_historical_rubric_keys(self):
        evidence = valid_evidence()
        evidence["cohorts"].append(
            {
                "id": "prior",
                "status": "historical",
                "artifact_digest": "b" * 64,
                "runs": [
                    {
                        **evidence["cohorts"][0]["runs"][0],
                        "id": "prior-case",
                        "rubric": {"retired_check": False},
                    }
                ],
            }
        )
        self.assertEqual(
            manage_evidence.summarize(evidence, RUBRIC),
            {"passed": 2, "total": 2},
        )

    def test_duplicate_json_key_diagnostic_escapes_control_characters(self):
        with self.assertRaises(manage_evidence.EvidenceError) as caught:
            manage_evidence.evidence_schema.decode_json(
                b'{"line\\nbreak": 1, "line\\nbreak": 2}',
                "evidence",
            )
        self.assertIn(r"'line\nbreak'", str(caught.exception))
        self.assertNotIn("line\nbreak", str(caught.exception))

    def test_rejects_duplicate_cohort_and_global_run_ids(self):
        evidence = valid_evidence()
        historical = {
            **evidence["cohorts"][0],
            "id": "final",
            "status": "historical",
        }
        evidence["cohorts"].append(historical)
        errors = self.errors(evidence)
        self.assertIn("duplicate cohort id: final", errors)
        self.assertIn("duplicate run id: final-case-1", errors)

    def test_rejects_unknown_missing_and_duplicate_headline_cases(self):
        evidence = valid_evidence()
        run = evidence["cohorts"][0]["runs"][0]
        evidence["cohorts"][0]["runs"] = [
            run,
            {**run, "id": "other-run", "case_id": "unknown"},
            {**run, "id": "duplicate-run"},
        ]
        errors = self.errors(
            evidence,
            (
                CASES[0],
                {"id": "case-2", "prompt": "Second exact prompt."},
            ),
        )
        self.assertIn("headline cohort has unknown case id: unknown", errors)
        self.assertIn("headline cohort has duplicate case id: case-1", errors)
        self.assertIn("headline cohort is missing case id: case-2", errors)

    def test_malformed_case_ids_are_diagnostic_not_exceptions(self):
        for case_id in (["bad"], {"bad": True}, 7):
            with self.subTest(case_id=case_id):
                evidence = valid_evidence()
                evidence["cohorts"][0]["runs"][0]["case_id"] = case_id
                errors = self.errors(evidence)
                self.assertIn(
                    "run 'final-case-1' has invalid case_id",
                    errors,
                )

    def test_rejects_bad_schema_keys_digest_status_ids_and_read_kind(self):
        mutations = (
            ("evidence", lambda e: e.update(extra=True), "evidence has unexpected keys"),
            ("digest", lambda e: e["artifact"].update(digest="A" * 64), "artifact digest must be 64 lowercase hexadecimal characters"),
            ("headline", lambda e: e.update(headline_cohort="other"), "headline_cohort does not identify the headline cohort"),
            ("cohort id", lambda e: e["cohorts"][0].update(id="../bad"), "cohort id is not safe"),
            ("run id", lambda e: e["cohorts"][0]["runs"][0].update(id="bad/id"), "run id is not safe"),
            ("status", lambda e: e["cohorts"][0].update(status="draft"), "cohort 'final' has invalid status"),
            ("kind", lambda e: e["cohorts"][0]["runs"][0].update(files_read_kind="claimed"), "run 'final-case-1' has invalid files_read_kind"),
        )
        for label, mutate, diagnostic in mutations:
            with self.subTest(label=label):
                evidence = valid_evidence()
                mutate(evidence)
                self.assertIn(diagnostic, self.errors(evidence))

    def test_rejects_unsafe_missing_symlink_and_empty_run_files(self):
        evidence = valid_evidence()
        for field, value in (
            ("prompt", "../prompt.md"),
            ("response", "/response.md"),
            ("files_read", "runs\\read.txt"),
        ):
            with self.subTest(field=field):
                changed = valid_evidence()
                changed["cohorts"][0]["runs"][0][field] = value
                self.assertTrue(any("safe POSIX-relative" in error for error in self.errors(changed)))

        (self.root / "runs/final-case-1/response.md").unlink()
        self.assertIn(
            "run 'final-case-1' response file is missing or not a regular nonsymlink file",
            self.errors(evidence),
        )
        outside = self.root / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        (self.root / "runs/final-case-1/response.md").symlink_to(outside)
        self.assertIn(
            "run 'final-case-1' response file is missing or not a regular nonsymlink file",
            self.errors(evidence),
        )

    def test_rejects_symlink_path_component_without_reading_outside(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "response.md").write_text("secret", encoding="utf-8")
        (self.root / "linked").symlink_to(outside, target_is_directory=True)
        evidence = valid_evidence()
        evidence["cohorts"][0]["runs"][0]["response"] = "linked/response.md"
        with mock.patch.object(
            Path,
            "read_bytes",
            side_effect=AssertionError("path reopen attempted"),
        ) as read_bytes:
            errors = self.errors(evidence)
        self.assertTrue(any("response file is missing" in error for error in errors))
        read_bytes.assert_not_called()

    def test_rejects_file_swapped_between_inspection_and_open(self):
        real_open = manage_evidence.evidence_store.os.open
        response = self.root / "runs/final-case-1/response.md"
        replacement = self.root / "replacement.md"
        replacement.write_text("replacement", encoding="utf-8")
        swapped = {"done": False}

        def swap_on_open(path, flags, *args, **kwargs):
            if path == "response.md" and not swapped["done"]:
                swapped["done"] = True
                os.replace(replacement, response)
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(manage_evidence.evidence_store.os, "open", swap_on_open):
            errors = self.errors()
        self.assertTrue(any("response file changed before it could be read" in error for error in errors))

    def test_rejects_empty_response_files_read_and_prompt_mismatch(self):
        for relative, diagnostic in (
            ("runs/final-case-1/response.md", "response file must be nonempty"),
            ("runs/final-case-1/files-read.txt", "files_read file must be nonempty"),
        ):
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                path.write_text("", encoding="utf-8")
                self.assertTrue(any(diagnostic in error for error in self.errors()))
                path.write_text(original, encoding="utf-8")
        self.write_text("runs/final-case-1/prompt.md", "wrong\n")
        self.assertIn(
            "run 'final-case-1' prompt does not match declared case prompt",
            self.errors(),
        )

    def test_rejects_invalid_utf8_run_markdown(self):
        (self.root / "runs/final-case-1/response.md").write_bytes(b"\xff")
        self.assertIn(
            "run 'final-case-1' response file is not valid UTF-8",
            self.errors(),
        )

    def test_rejects_unknown_missing_and_nonboolean_rubric_values(self):
        for rubric, diagnostic in (
            ({"correct_profile": True}, "rubric keys do not exactly match declared rubric"),
            ({**valid_evidence()["cohorts"][0]["runs"][0]["rubric"], "extra": True}, "rubric keys do not exactly match declared rubric"),
            ({"correct_profile": 1, "mandatory_checks_present": True}, "rubric item 'correct_profile' is not boolean"),
        ):
            with self.subTest(diagnostic=diagnostic):
                evidence = valid_evidence()
                evidence["cohorts"][0]["runs"][0]["rubric"] = rubric
                self.assertTrue(any(diagnostic in error for error in self.errors(evidence)))

    def test_rejects_stored_or_reported_score_totals(self):
        for location in ("evidence", "cohort", "run"):
            with self.subTest(location=location):
                evidence = valid_evidence()
                target = {
                    "evidence": evidence,
                    "cohort": evidence["cohorts"][0],
                    "run": evidence["cohorts"][0]["runs"][0],
                }[location]
                target["passed"] = 99
                target["total"] = 2
                errors = self.errors(evidence)
                self.assertTrue(any("unexpected keys" in error for error in errors))

    def test_rejects_missing_and_mismatched_artifact_manifest(self):
        (self.root / "artifact.json").unlink()
        self.assertIn("artifact manifest is missing or not a regular nonsymlink file", self.errors())
        self.write_json("artifact.json", {**artifact_manifest(), "digest": "b" * 64})
        self.assertIn("artifact manifest digest does not match evidence artifact digest", self.errors())

    def test_rejects_malformed_artifact_manifest_contract(self):
        manifest = artifact_manifest()
        manifest["files"].append({"path": "../escape", "bytes": 1})
        self.write_json("artifact.json", manifest)
        self.assertTrue(any("artifact manifest" in error for error in self.errors()))

    def test_preserves_coherent_historical_cohort(self):
        evidence = valid_evidence()
        historical = {
            "id": "prior",
            "status": "historical",
            "artifact_digest": "b" * 64,
            "runs": [],
        }
        evidence["cohorts"].append(historical)
        self.assertEqual(self.errors(evidence), [])

    def test_historical_run_may_use_retired_case_and_recorded_prompt(self):
        evidence = valid_evidence()
        historical_run = {
            **evidence["cohorts"][0]["runs"][0],
            "id": "prior-retired",
            "case_id": "retired-case",
            "prompt": "runs/prior-retired/prompt.md",
            "response": "runs/prior-retired/response.md",
            "files_read": "runs/prior-retired/files-read.txt",
        }
        evidence["cohorts"].append(
            {
                "id": "prior",
                "status": "historical",
                "artifact_digest": "b" * 64,
                "runs": [historical_run],
            }
        )
        self.write_text("runs/prior-retired/prompt.md", "retired prompt\n")
        self.write_text("runs/prior-retired/response.md", "old response\n")
        self.write_text("runs/prior-retired/files-read.txt", "old.md\n")

        self.assertEqual(self.errors(evidence), [])

    def test_historical_prompt_need_not_match_updated_current_prompt(self):
        evidence = valid_evidence()
        historical_run = {
            **evidence["cohorts"][0]["runs"][0],
            "id": "prior-case-1",
            "prompt": "runs/prior-case-1/prompt.md",
            "response": "runs/prior-case-1/response.md",
            "files_read": "runs/prior-case-1/files-read.txt",
        }
        evidence["cohorts"].append(
            {
                "id": "prior",
                "status": "historical",
                "artifact_digest": "b" * 64,
                "runs": [historical_run],
            }
        )
        current_cases = (
            {"id": "case-1", "prompt": "Updated current prompt."},
        )
        self.write_text("runs/final-case-1/prompt.md", "Updated current prompt.\n")
        self.write_text("runs/prior-case-1/prompt.md", "original prompt\n")
        self.write_text("runs/prior-case-1/response.md", "old response\n")
        self.write_text("runs/prior-case-1/files-read.txt", "old.md\n")

        self.assertEqual(self.errors(evidence, cases=current_cases), [])


class InitializationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name).resolve()
        self.artifact = self.root / "source-artifact.json"
        self.cases = self.root / "cases.json"
        self.rubric = self.root / "rubric.json"
        self.output = self.root / "cohort" / "evidence.json"
        self.artifact.write_text(json.dumps(artifact_manifest()), encoding="utf-8")
        self.cases.write_text(json.dumps(list(CASES)), encoding="utf-8")
        self.rubric.write_text(json.dumps(list(RUBRIC)), encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_prior_cohort(self):
        self.output.parent.mkdir(exist_ok=True)
        old_digest = "b" * 64
        output_key = hashlib.sha256(self.output.name.encode("utf-8")).hexdigest()
        generation_id = "old-" + ("1" * 32)
        generation = f".evidence-data/{output_key}/{generation_id}"
        old_manifest = {**artifact_manifest(), "digest": old_digest}
        old_evidence = valid_evidence()
        old_evidence["artifact"]["digest"] = old_digest
        old_evidence["artifact"]["manifest"] = f"{generation}/artifact.json"
        old_evidence["headline_cohort"] = "old"
        old_evidence["cohorts"][0]["id"] = "old"
        old_evidence["cohorts"][0]["artifact_digest"] = old_digest
        old_evidence["cohorts"][0]["runs"][0]["id"] = "old-case-1"
        old_evidence["cohorts"][0]["runs"][0]["prompt"] = f"{generation}/runs/old-case-1/prompt.md"
        old_evidence["cohorts"][0]["runs"][0]["response"] = f"{generation}/runs/old-case-1/response.md"
        old_evidence["cohorts"][0]["runs"][0]["files_read"] = f"{generation}/runs/old-case-1/files-read.txt"
        old_evidence_bytes = (json.dumps(old_evidence, sort_keys=True) + "\n").encode()
        old_manifest_bytes = (json.dumps(old_manifest, sort_keys=True) + "\n").encode()
        self.output.write_bytes(old_evidence_bytes)
        manifest_path = self.output.parent / generation / "artifact.json"
        manifest_path.parent.mkdir(parents=True)
        self.output_namespace().chmod(0o700)
        manifest_path.write_bytes(old_manifest_bytes)
        marker = {
            "schema_version": 1,
            "output_key": output_key,
            "generation_id": generation_id,
            "cohort_id": "old",
            "cases": list(CASES),
            "rubric": list(RUBRIC),
            "artifact": {
                "algorithm": "sha256-length-framed-v1",
                "digest": old_digest,
            },
            "paths": {
                "evidence": "evidence.json",
                "artifact": "artifact.json",
                "runs": "runs",
            },
        }
        (manifest_path.parent / "generation.json").write_text(
            json.dumps(marker, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        old_run = self.output.parent / generation / "runs/old-case-1"
        old_run.mkdir(parents=True)
        (old_run / "prompt.md").write_text(CASES[0]["prompt"] + "\n", encoding="utf-8")
        (old_run / "response.md").write_text("old response\n", encoding="utf-8")
        (old_run / "files-read.txt").write_text("old.md\n", encoding="utf-8")
        return old_evidence_bytes, old_manifest_bytes, old_run

    def complete_generated_evidence(self, evidence, rubric_scores):
        run = evidence["cohorts"][-1]["runs"][0]
        generation = self.output.parent / Path(run["prompt"]).parents[2]
        response = generation / "runs" / run["id"] / "response.md"
        files_read = generation / "runs" / run["id"] / "files-read.txt"
        response.write_text("complete response\n", encoding="utf-8")
        files_read.write_text("SKILL.md\n", encoding="utf-8")
        run.update(
            {
                "response": response.relative_to(self.output.parent).as_posix(),
                "files_read": files_read.relative_to(self.output.parent).as_posix(),
                "files_read_kind": "agent-reported",
                "rubric": rubric_scores,
            }
        )
        self.output.write_text(
            json.dumps(evidence, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return generation

    def output_namespace(self, output=None):
        output = self.output if output is None else output
        key = hashlib.sha256(output.name.encode("utf-8")).hexdigest()
        return output.parent / ".evidence-data" / key

    def test_different_outputs_use_isolated_namespaces_sequentially(self):
        first = self.root / "shared" / "first.json"
        second = self.root / "shared" / "second.json"

        first_evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, first, "first"
        )
        second_evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, second, "second"
        )

        self.assertTrue(first.exists())
        self.assertTrue(second.exists())
        self.assertNotEqual(
            first_evidence["artifact"]["manifest"].split("/")[1],
            second_evidence["artifact"]["manifest"].split("/")[1],
        )
        self.assertEqual(len(list(self.output_namespace(first).glob("first-*"))), 1)
        self.assertEqual(len(list(self.output_namespace(second).glob("second-*"))), 1)
        self.assertEqual(stat.S_IMODE(self.output_namespace(first).stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.output_namespace(second).stat().st_mode), 0o700)
        self.assertEqual(
            manage_evidence.validate_evidence(
                first.parent, first_evidence, CASES, RUBRIC
            ),
            [
                "run 'first-case-1' is incomplete: missing response, files_read, files_read_kind, rubric"
            ],
        )
        self.assertEqual(
            manage_evidence.validate_evidence(
                second.parent, second_evidence, CASES, RUBRIC
            ),
            [
                "run 'second-case-1' is incomplete: missing response, files_read, files_read_kind, rubric"
            ],
        )

    def test_different_outputs_use_isolated_namespaces_concurrently(self):
        first = self.root / "shared" / "first.json"
        second = self.root / "shared" / "second.json"

        def initialize(arguments):
            output, cohort = arguments
            return manage_evidence.initialize_evidence(
                self.artifact, self.cases, self.rubric, output, cohort
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(initialize, ((first, "first"), (second, "second")))
            )

        self.assertEqual({item["headline_cohort"] for item in results}, {"first", "second"})
        self.assertEqual(len(list(self.output_namespace(first).glob("first-*"))), 1)
        self.assertEqual(len(list(self.output_namespace(second).glob("second-*"))), 1)
        self.assertTrue(first.exists())
        self.assertTrue(second.exists())
        for output, evidence in zip((first, second), results):
            self.assertEqual(len(manage_evidence.validate_evidence(output.parent, evidence, CASES, RUBRIC)), 1)

    def test_plausible_unowned_generation_is_never_deleted(self):
        namespace = self.output_namespace()
        planted = namespace / ("planted-" + ("a" * 32))
        planted.mkdir(parents=True)
        namespace.chmod(0o700)
        marker = planted / "keep.txt"
        marker.write_text("not owned\n", encoding="utf-8")

        manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "final"
        )

        self.assertEqual(marker.read_text(encoding="utf-8"), "not owned\n")

    def test_rollover_uses_stored_case_and_rubric_declarations(self):
        old = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "old"
        )
        old_generation = self.complete_generated_evidence(
            old,
            {
                "correct_profile": True,
                "mandatory_checks_present": False,
            },
        )
        self.cases.write_text(
            json.dumps([{"id": "case-2", "prompt": "A newly evolved prompt."}]),
            encoding="utf-8",
        )
        self.rubric.write_text(json.dumps(["new_check"]), encoding="utf-8")

        rolled = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "new"
        )

        self.assertEqual(
            [(cohort["id"], cohort["status"]) for cohort in rolled["cohorts"]],
            [("old", "historical"), ("new", "headline")],
        )
        self.assertEqual(
            rolled["cohorts"][0]["runs"][0]["rubric"],
            {
                "correct_profile": True,
                "mandatory_checks_present": False,
            },
        )
        self.assertTrue(old_generation.is_dir())
        self.assertEqual(
            (self.output.parent / rolled["cohorts"][1]["runs"][0]["prompt"]).read_text(
                encoding="utf-8"
            ),
            "A newly evolved prompt.\n",
        )
        self.assertEqual(
            manage_evidence.validate_evidence(
                self.output.parent,
                rolled,
                ({"id": "case-2", "prompt": "A newly evolved prompt."},),
                ("new_check",),
            ),
            [
                "run 'new-case-2' is incomplete: missing response, files_read, files_read_kind, rubric"
            ],
        )

    def test_rollover_rejects_corrupt_owned_marker_and_manifest(self):
        for corrupt in ("generation.json", "artifact.json"):
            with self.subTest(corrupt=corrupt):
                if self.output.parent.exists():
                    self.temporary_directory.cleanup()
                    self.setUp()
                old = manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "old"
                )
                generation = self.complete_generated_evidence(
                    old,
                    {
                        "correct_profile": True,
                        "mandatory_checks_present": True,
                    },
                )
                (generation / corrupt).write_text("{}\n", encoding="utf-8")
                with self.assertRaises(manage_evidence.EvidenceError):
                    manage_evidence.initialize_evidence(
                        self.artifact,
                        self.cases,
                        self.rubric,
                        self.output,
                        "new",
                    )

    def run_crashing_initializer(self, crash_point, cohort="crash"):
        program = r"""
import os
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import manage_evidence
real_replace = manage_evidence.evidence_store.os.replace
real_fsync = manage_evidence.evidence_store.os.fsync
point = sys.argv[7]
cohort = sys.argv[6]
def crashing_replace(source, destination, *args, **kwargs):
    result = real_replace(source, destination, *args, **kwargs)
    generation_commit = (
        isinstance(destination, str)
        and destination.startswith(cohort + "-")
        and kwargs.get("dst_dir_fd") is not None
    )
    evidence_commit = (
        isinstance(source, str)
        and source.startswith(".evidence.json.")
        and destination == "evidence.json"
    )
    if (point == "generation" and generation_commit) or (
        point == "evidence" and evidence_commit
    ):
        os._exit(91)
    return result
manage_evidence.evidence_store.os.replace = crashing_replace
def crashing_fsync(descriptor):
    result = real_fsync(descriptor)
    if point == "parent-fsync" and Path(sys.argv[5]).exists():
        parent = Path(sys.argv[5]).parent.stat()
        opened = os.fstat(descriptor)
        if (parent.st_dev, parent.st_ino) == (opened.st_dev, opened.st_ino):
            os._exit(92)
    return result
manage_evidence.evidence_store.os.fsync = crashing_fsync
manage_evidence.initialize_evidence(
    Path(sys.argv[2]),
    Path(sys.argv[3]),
    Path(sys.argv[4]),
    Path(sys.argv[5]),
    cohort,
)
"""
        return subprocess.run(
            [
                sys.executable,
                "-c",
                program,
                str(SCRIPTS_ROOT),
                str(self.artifact),
                str(self.cases),
                str(self.rubric),
                str(self.output),
                cohort,
                crash_point,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_crash_before_evidence_commit_leaves_old_state_and_orphan_is_recovered(self):
        result = self.run_crashing_initializer("generation")
        self.assertEqual(result.returncode, 91)
        self.assertFalse(self.output.exists())
        namespace = self.output_namespace()
        orphan_names = [
            path.name for path in namespace.iterdir() if path.name != ".lock"
        ]
        self.assertEqual(len(orphan_names), 1)

        evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "recovered"
        )

        referenced = evidence["artifact"]["manifest"].split("/")[2]
        remaining = [
            path.name for path in namespace.iterdir() if path.name != ".lock"
        ]
        self.assertEqual(remaining, [referenced])
        self.assertNotIn(orphan_names[0], remaining)
        self.assertFalse(
            any(".stage" in path.name or ".commit" in path.name for path in self.output.parent.glob(".*"))
        )

    def test_crash_after_evidence_commit_leaves_complete_new_state(self):
        result = self.run_crashing_initializer("evidence")
        self.assertEqual(result.returncode, 91)
        evidence = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(evidence["headline_cohort"], "crash")
        self.assertEqual(
            manage_evidence.validate_evidence(
                self.output.parent,
                evidence,
                CASES,
                RUBRIC,
            ),
            [
                "run 'crash-case-1' is incomplete: missing response, files_read, files_read_kind, rubric"
            ],
        )
        self.assertFalse(
            any(".stage" in path.name or ".commit" in path.name for path in self.output.parent.glob(".*"))
        )

    def test_crash_after_pointer_parent_fsync_leaves_complete_new_state(self):
        result = self.run_crashing_initializer("parent-fsync")
        self.assertEqual(result.returncode, 92)
        evidence = json.loads(self.output.read_text(encoding="utf-8"))
        generation = evidence["artifact"]["manifest"].split("/")[2]
        self.assertTrue((self.output_namespace() / generation / "generation.json").is_file())

    def test_threaded_same_cohort_initialization_serializes_to_one_generation(self):
        def initialize():
            try:
                manage_evidence.initialize_evidence(
                    self.artifact,
                    self.cases,
                    self.rubric,
                    self.output,
                    "same",
                )
                return "ok"
            except manage_evidence.EvidenceError as error:
                return str(error)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: initialize(), range(2)))

        self.assertEqual(results.count("ok"), 1)
        self.assertEqual(results.count("cohort already exists: same"), 1)
        self.assertEqual(
            len(list((self.output.parent / ".evidence-data").iterdir())),
            1,
        )

    def test_process_same_cohort_initialization_serializes_to_one_generation(self):
        self.output.parent.mkdir()
        command = [
            sys.executable,
            str(SCRIPTS_ROOT / "manage_evidence.py"),
            "init",
            str(self.artifact),
            str(self.cases),
            str(self.rubric),
            str(self.output),
            "--cohort",
            "same-process",
        ]
        first = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        second = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        first_output = first.communicate()
        second_output = second.communicate()

        self.assertEqual(sorted((first.returncode, second.returncode)), [0, 2])
        self.assertIn(
            "cohort already exists: same-process",
            first_output[1] + second_output[1],
        )
        self.assertEqual(
            len(list((self.output.parent / ".evidence-data").iterdir())),
            1,
        )

    def test_missing_secure_capability_fails_closed(self):
        with mock.patch.object(manage_evidence.evidence_store, "fcntl", None):
            with self.assertRaisesRegex(
                manage_evidence.EvidenceError,
                "secure filesystem capabilities",
            ):
                manage_evidence.initialize_evidence(
                    self.artifact,
                    self.cases,
                    self.rubric,
                    self.output,
                    "final",
                )

    def test_not_implemented_orphan_scan_is_a_controlled_error(self):
        real_listdir = manage_evidence.evidence_store.os.listdir

        def unavailable(path):
            if isinstance(path, int):
                raise NotImplementedError("descriptor listing unavailable")
            return real_listdir(path)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "listdir",
            unavailable,
        ):
            with self.assertRaisesRegex(
                manage_evidence.EvidenceError,
                "inspect immutable evidence generations",
            ):
                manage_evidence.initialize_evidence(
                    self.artifact,
                    self.cases,
                    self.rubric,
                    self.output,
                    "final",
                )

    def test_lock_substitution_during_generation_or_pointer_rename_rolls_back_owned_state(self):
        for boundary in ("generation", "pointer"):
            with self.subTest(boundary=boundary):
                if self.output.parent.exists():
                    self.temporary_directory.cleanup()
                    self.setUp()
                real_replace = manage_evidence.evidence_store.os.replace
                substituted = {"done": False}

                def substitute_before_replace(source, destination, *args, **kwargs):
                    is_generation = (
                        isinstance(destination, str)
                        and destination.startswith("final-")
                    )
                    is_pointer = (
                        isinstance(source, str)
                        and source.startswith(".evidence.json.")
                        and destination == "evidence.json"
                    )
                    if (
                        not substituted["done"]
                        and (
                            (boundary == "generation" and is_generation)
                            or (boundary == "pointer" and is_pointer)
                        )
                    ):
                        substituted["done"] = True
                        namespace = self.output_namespace()
                        lock = namespace / ".lock"
                        lock.rename(namespace / ".lock.original")
                        lock.write_text("replacement lock\n", encoding="utf-8")
                        lock.chmod(0o600)
                    return real_replace(source, destination, *args, **kwargs)

                with mock.patch.object(
                    manage_evidence.evidence_store.os,
                    "replace",
                    substitute_before_replace,
                ):
                    with self.assertRaisesRegex(
                        manage_evidence.EvidenceError,
                        "evidence lock identity changed",
                    ):
                        manage_evidence.initialize_evidence(
                            self.artifact,
                            self.cases,
                            self.rubric,
                            self.output,
                            "final",
                        )

                namespace = self.output_namespace()
                self.assertTrue(substituted["done"])
                self.assertFalse(self.output.exists())
                self.assertEqual(
                    (namespace / ".lock").read_text(encoding="utf-8"),
                    "replacement lock\n",
                )
                self.assertEqual(
                    [
                        path.name
                        for path in namespace.iterdir()
                        if not path.name.startswith(".lock")
                    ],
                    [],
                )

    def test_first_use_fsyncs_container_directories_before_pointer_replace(self):
        events = []
        real_fsync = manage_evidence.evidence_store.os.fsync
        real_replace = manage_evidence.evidence_store.os.replace

        def record_fsync(descriptor):
            opened = os.fstat(descriptor)
            if self.output.parent.exists():
                parent = self.output.parent.stat()
                if (opened.st_dev, opened.st_ino) == (parent.st_dev, parent.st_ino):
                    events.append("parent")
            data = self.output.parent / ".evidence-data"
            if data.exists():
                metadata = data.stat()
                if (opened.st_dev, opened.st_ino) == (
                    metadata.st_dev,
                    metadata.st_ino,
                ):
                    events.append("data")
            return real_fsync(descriptor)

        def record_replace(source, destination, *args, **kwargs):
            if destination == "evidence.json":
                events.append("pointer")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "fsync",
            record_fsync,
        ), mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            record_replace,
        ):
            manage_evidence.initialize_evidence(
                self.artifact, self.cases, self.rubric, self.output, "final"
            )

        self.assertLess(events.index("parent"), events.index("data"))
        self.assertLess(events.index("data"), events.index("pointer"))

    def test_first_use_container_fsync_failure_leaves_no_pointer(self):
        real_fsync = manage_evidence.evidence_store.os.fsync
        failed = {"done": False}

        def fail_parent_fsync(descriptor):
            opened = os.fstat(descriptor)
            parent = self.output.parent.stat()
            if (
                not failed["done"]
                and (opened.st_dev, opened.st_ino) == (parent.st_dev, parent.st_ino)
                and (self.output.parent / ".evidence-data").exists()
            ):
                failed["done"] = True
                raise OSError("injected parent fsync failure")
            return real_fsync(descriptor)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "fsync",
            fail_parent_fsync,
        ):
            with self.assertRaises(manage_evidence.EvidenceError):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )

        self.assertTrue(failed["done"])
        self.assertFalse(self.output.exists())

    def test_lock_acquisition_verification_failure_releases_fd_and_mutex(self):
        namespace = self.output_namespace()
        namespace.mkdir(parents=True)
        namespace.chmod(0o700)
        descriptor = os.open(namespace, manage_evidence.evidence_store._directory_flags())
        descriptors_before = len(os.listdir("/dev/fd"))
        try:
            with mock.patch.object(
                manage_evidence.evidence_store,
                "_verify_evidence_lock",
                side_effect=manage_evidence.EvidenceError("injected identity failure"),
            ):
                with self.assertRaises(manage_evidence.EvidenceError):
                    manage_evidence.evidence_store._acquire_evidence_lock(
                        descriptor,
                        "a" * 64,
                    )
            self.assertEqual(len(os.listdir("/dev/fd")), descriptors_before)
            process_lock, lock_descriptor, _ = (
                manage_evidence.evidence_store._acquire_evidence_lock(
                    descriptor,
                    "a" * 64,
                )
            )
            manage_evidence.evidence_store._release_evidence_lock(
                process_lock,
                lock_descriptor,
            )
        finally:
            os.close(descriptor)

    def test_lock_nlink_and_nonregular_failures_do_not_drift_resources(self):
        for kind in ("nlink", "directory"):
            with self.subTest(kind=kind):
                namespace = self.root / f"namespace-{kind}"
                namespace.mkdir(mode=0o700)
                lock = namespace / ".lock"
                if kind == "nlink":
                    lock.write_text("", encoding="utf-8")
                    os.link(lock, namespace / ".lock-link")
                else:
                    lock.mkdir()
                descriptor = os.open(
                    namespace,
                    manage_evidence.evidence_store._directory_flags(),
                )
                descriptors_before = len(os.listdir("/dev/fd"))
                try:
                    with self.assertRaises(manage_evidence.EvidenceError):
                        manage_evidence.evidence_store._acquire_evidence_lock(
                            descriptor,
                            "b" * 64,
                        )
                    self.assertEqual(len(os.listdir("/dev/fd")), descriptors_before)
                    if kind == "nlink":
                        (namespace / ".lock-link").unlink()
                    else:
                        lock.rmdir()
                    process_lock, lock_descriptor, _ = (
                        manage_evidence.evidence_store._acquire_evidence_lock(
                            descriptor,
                            "b" * 64,
                        )
                    )
                    manage_evidence.evidence_store._release_evidence_lock(
                        process_lock,
                        lock_descriptor,
                    )
                finally:
                    os.close(descriptor)

    def test_parent_lock_serializes_replacement_until_stale_pointer_rollback_finishes(self):
        self.output.parent.mkdir()
        ready = self.root / "pointer-ready"
        proceed = self.root / "pointer-proceed"
        replacement_started = self.root / "replacement-started"
        holder_program = r"""
import os
import sys
import time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import manage_evidence
real_replace = manage_evidence.evidence_store.os.replace
def paused_replace(source, destination, *args, **kwargs):
    if (
        isinstance(source, str)
        and source.startswith(".evidence.json.")
        and destination == "evidence.json"
    ):
        Path(sys.argv[7]).write_text("ready", encoding="utf-8")
        while not Path(sys.argv[8]).exists():
            time.sleep(0.01)
    return real_replace(source, destination, *args, **kwargs)
manage_evidence.evidence_store.os.replace = paused_replace
manage_evidence.initialize_evidence(
    Path(sys.argv[2]),
    Path(sys.argv[3]),
    Path(sys.argv[4]),
    Path(sys.argv[5]),
    sys.argv[6],
)
"""
        holder = subprocess.Popen(
            [
                sys.executable,
                "-c",
                holder_program,
                str(SCRIPTS_ROOT),
                str(self.artifact),
                str(self.cases),
                str(self.rubric),
                str(self.output),
                "stale",
                str(ready),
                str(proceed),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(ready.exists())
        namespace = self.output_namespace()
        lock = namespace / ".lock"
        lock.rename(namespace / ".lock.stale")
        lock.write_text("replacement\n", encoding="utf-8")
        lock.chmod(0o600)

        replacement_program = r"""
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import manage_evidence
Path(sys.argv[7]).write_text("started", encoding="utf-8")
raise SystemExit(manage_evidence.main([
    "init",
    sys.argv[2],
    sys.argv[3],
    sys.argv[4],
    sys.argv[5],
    "--cohort",
    sys.argv[6],
]))
"""
        replacement = subprocess.Popen(
            [
                sys.executable,
                "-c",
                replacement_program,
                str(SCRIPTS_ROOT),
                str(self.artifact),
                str(self.cases),
                str(self.rubric),
                str(self.output),
                "replacement",
                str(replacement_started),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 5
        while not replacement_started.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(replacement_started.exists())
        time.sleep(0.1)
        self.assertIsNone(replacement.poll())
        self.assertFalse(self.output.exists())

        proceed.write_text("go", encoding="utf-8")
        holder_output = holder.communicate(timeout=5)
        replacement_output = replacement.communicate(timeout=5)

        self.assertNotEqual(holder.returncode, 0)
        self.assertIn("evidence lock identity changed", holder_output[1])
        self.assertEqual(replacement.returncode, 0, replacement_output[1])
        evidence = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(evidence["headline_cohort"], "replacement")
        self.assertEqual(len(list(namespace.glob("replacement-*"))), 1)
        self.assertEqual(len(list(namespace.glob("stale-*"))), 0)

    def test_retry_after_namespace_fsync_failure_fsyncs_data_before_pointer(self):
        real_fsync = manage_evidence.evidence_store.os.fsync
        failed = {"done": False}

        def fail_first_data_fsync(descriptor):
            opened = os.fstat(descriptor)
            data = self.output.parent / ".evidence-data"
            if data.exists():
                metadata = data.stat()
                if (
                    not failed["done"]
                    and (opened.st_dev, opened.st_ino)
                    == (metadata.st_dev, metadata.st_ino)
                ):
                    failed["done"] = True
                    raise OSError("injected namespace durability failure")
            return real_fsync(descriptor)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "fsync",
            fail_first_data_fsync,
        ):
            with self.assertRaises(manage_evidence.EvidenceError):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "first"
                )
        self.assertTrue(failed["done"])
        self.assertFalse(self.output.exists())

        events = []
        real_replace = manage_evidence.evidence_store.os.replace

        def record_fsync(descriptor):
            opened = os.fstat(descriptor)
            data = self.output.parent / ".evidence-data"
            metadata = data.stat()
            if (opened.st_dev, opened.st_ino) == (
                metadata.st_dev,
                metadata.st_ino,
            ):
                events.append("data")
            return real_fsync(descriptor)

        def record_replace(source, destination, *args, **kwargs):
            if destination == "evidence.json":
                events.append("pointer")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "fsync",
            record_fsync,
        ), mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            record_replace,
        ):
            evidence = manage_evidence.initialize_evidence(
                self.artifact, self.cases, self.rubric, self.output, "retry"
            )

        self.assertLess(events.index("data"), events.index("pointer"))
        self.assertEqual(evidence["headline_cohort"], "retry")

    def test_parent_flock_failure_is_controlled_and_releases_resources(self):
        self.output.parent.mkdir()
        descriptors_before = len(os.listdir("/dev/fd"))
        with mock.patch.object(
            manage_evidence.evidence_store.fcntl,
            "flock",
            side_effect=OSError("parent flock unavailable"),
        ):
            with self.assertRaisesRegex(
                manage_evidence.EvidenceError,
                "cannot acquire secure evidence parent lock",
            ):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "failed"
                )
        self.assertEqual(len(os.listdir("/dev/fd")), descriptors_before)
        evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "retry"
        )
        self.assertEqual(evidence["headline_cohort"], "retry")

    def test_multiple_unlock_failures_after_commit_release_all_resources(self):
        self.output.parent.mkdir()
        descriptors_before = len(os.listdir("/dev/fd"))
        locked_before = {
            key
            for key, lock in manage_evidence.evidence_store._THREAD_LOCKS.items()
            if lock.locked()
        }
        real_flock = manage_evidence.evidence_store.fcntl.flock
        unlock_attempts = []

        def fail_unlock(descriptor, operation):
            if operation == manage_evidence.evidence_store.fcntl.LOCK_UN:
                unlock_attempts.append(os.fstat(descriptor).st_ino)
                raise OSError("injected unlock failure")
            return real_flock(descriptor, operation)

        with mock.patch.object(
            manage_evidence.evidence_store.fcntl,
            "flock",
            fail_unlock,
        ):
            with self.assertRaisesRegex(
                manage_evidence.EvidenceError,
                "committed but cleanup failed",
            ) as caught:
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )

        self.assertEqual(len(unlock_attempts), 2)
        self.assertTrue(self.output.exists())
        self.assertNotIn(str(self.root), str(caught.exception))
        self.assertEqual(len(os.listdir("/dev/fd")), descriptors_before)
        self.assertEqual(
            {
                key
                for key, lock in manage_evidence.evidence_store._THREAD_LOCKS.items()
                if lock.locked()
            },
            locked_before,
        )
        other = self.output.with_name("other.json")
        evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, other, "other"
        )
        self.assertEqual(evidence["headline_cohort"], "other")

    def test_multiple_unlock_failures_preserve_primary_transaction_error_and_release_all_resources(self):
        for iteration in range(3):
            with self.subTest(iteration=iteration):
                if self.output.parent.exists():
                    self.temporary_directory.cleanup()
                    self.setUp()
                self.output.parent.mkdir()
                descriptors_before = len(os.listdir("/dev/fd"))
                locked_before = {
                    key
                    for key, lock in manage_evidence.evidence_store._THREAD_LOCKS.items()
                    if lock.locked()
                }
                real_flock = manage_evidence.evidence_store.fcntl.flock
                real_replace = manage_evidence.evidence_store.os.replace
                unlock_attempts = []

                def fail_unlock(descriptor, operation):
                    if operation == manage_evidence.evidence_store.fcntl.LOCK_UN:
                        unlock_attempts.append(os.fstat(descriptor).st_ino)
                        raise OSError("injected unlock failure")
                    return real_flock(descriptor, operation)

                def fail_pointer(source, destination, *args, **kwargs):
                    if destination == "evidence.json":
                        raise OSError("primary pointer failure")
                    return real_replace(source, destination, *args, **kwargs)

                with mock.patch.object(
                    manage_evidence.evidence_store.fcntl,
                    "flock",
                    fail_unlock,
                ), mock.patch.object(
                    manage_evidence.evidence_store.os,
                    "replace",
                    fail_pointer,
                ):
                    with self.assertRaisesRegex(
                        manage_evidence.EvidenceError,
                        "cannot initialize evidence: operating system error",
                    ) as caught:
                        manage_evidence.initialize_evidence(
                            self.artifact,
                            self.cases,
                            self.rubric,
                            self.output,
                            "failed",
                        )

                self.assertEqual(len(unlock_attempts), 2)
                notes = getattr(caught.exception, "__notes__", ())
                self.assertTrue(any("cleanup failed" in note for note in notes))
                self.assertEqual(
                    str(caught.exception.__cause__),
                    "primary pointer failure",
                )
                self.assertNotIn(str(self.root), str(caught.exception))
                self.assertEqual(len(os.listdir("/dev/fd")), descriptors_before)
                self.assertEqual(
                    {
                        key
                        for key, lock in manage_evidence.evidence_store._THREAD_LOCKS.items()
                        if lock.locked()
                    },
                    locked_before,
                )
                evidence = manage_evidence.initialize_evidence(
                    self.artifact,
                    self.cases,
                    self.rubric,
                    self.output.with_name("retry.json"),
                    f"retry-{iteration}",
                )
                self.assertEqual(evidence["headline_cohort"], f"retry-{iteration}")

    def test_init_creates_exact_prompt_and_explicit_draft_without_pass_placeholders(self):
        evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "final"
        )
        run = evidence["cohorts"][0]["runs"][0]
        self.assertEqual(
            (self.output.parent / run["prompt"]).read_text(encoding="utf-8"),
            CASES[0]["prompt"] + "\n",
        )
        self.assertEqual(set(run), {"id", "case_id", "prompt"})
        self.assertEqual(evidence["cohorts"][0]["status"], "headline")
        self.assertEqual(
            manage_evidence.validate_evidence(
                self.output.parent, evidence, CASES, RUBRIC
            ),
            [
                "run 'final-case-1' is incomplete: missing response, files_read, files_read_kind, rubric"
            ],
        )
        self.assertFalse((self.output.parent / "runs/final-case-1/response.md").exists())
        with self.assertRaisesRegex(manage_evidence.EvidenceError, "incomplete"):
            manage_evidence.summarize(evidence, RUBRIC)

    def test_init_accepts_expected_profile_metadata_without_using_it_as_a_score(self):
        self.cases.write_text(
            json.dumps(
                [
                    {
                        "id": "case-1",
                        "prompt": "Choose the smallest adequate profile.",
                        "expected_profile": "quick",
                    }
                ]
            ),
            encoding="utf-8",
        )

        evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "final"
        )

        run = evidence["cohorts"][0]["runs"][0]
        self.assertNotIn("expected_profile", run)
        self.assertNotIn("rubric", run)
        generation = self.output.parent / Path(run["prompt"]).parents[2]
        marker = json.loads(
            (generation / "generation.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marker["cases"][0]["expected_profile"], "quick")

    def test_init_preserves_existing_historical_cohorts(self):
        self.write_prior_cohort()
        evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "final"
        )
        self.assertEqual([cohort["id"] for cohort in evidence["cohorts"]], ["old", "final"])
        self.assertEqual(evidence["cohorts"][0]["status"], "historical")

    def test_init_rejects_malformed_existing_cohort_structure(self):
        self.output.parent.mkdir()
        existing = valid_evidence()
        existing["cohorts"].append({**existing["cohorts"][0]})
        original = json.dumps(existing)
        self.output.write_text(original, encoding="utf-8")

        with self.assertRaisesRegex(
            manage_evidence.EvidenceError,
            "duplicate cohort id",
        ):
            manage_evidence.initialize_evidence(
                self.artifact, self.cases, self.rubric, self.output, "new"
            )

        self.assertEqual(self.output.read_text(encoding="utf-8"), original)

    def test_init_rejects_duplicate_json_keys_invalid_inputs_before_mutating(self):
        self.cases.write_text('[{"id":"case-1","id":"case-2","prompt":"x"}]', encoding="utf-8")
        with self.assertRaises(manage_evidence.EvidenceError):
            manage_evidence.initialize_evidence(
                self.artifact, self.cases, self.rubric, self.output, "final"
            )
        self.assertFalse(self.output.parent.exists())

    def test_init_failure_leaves_prior_output_and_no_staging_residue(self):
        self.output.parent.mkdir()
        self.output.write_text("prior\n", encoding="utf-8")
        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            side_effect=OSError("injected"),
        ):
            with self.assertRaises(manage_evidence.EvidenceError):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )
        self.assertEqual(self.output.read_text(encoding="utf-8"), "prior\n")
        self.assertEqual(
            sorted(path.name for path in self.output.parent.iterdir()),
            [".evidence-data", "evidence.json"],
        )

    def test_init_failure_leaves_no_new_cohort_root(self):
        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            side_effect=OSError("injected"),
        ):
            with self.assertRaises(manage_evidence.EvidenceError):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )

        self.assertFalse(self.output.exists())
        self.assertFalse(
            any(".stage" in path.name for path in self.output.parent.glob(".*"))
        )

    def test_init_rejects_symlink_output_parent_without_writing_outside(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.output.parent.symlink_to(outside, target_is_directory=True)

        with self.assertRaises(manage_evidence.EvidenceError):
            manage_evidence.initialize_evidence(
                self.artifact, self.cases, self.rubric, self.output, "final"
            )

        self.assertEqual(list(outside.iterdir()), [])

    def test_init_ignores_legacy_symlink_runs_directory_without_writing_outside(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.output.parent.mkdir()
        (self.output.parent / "runs").symlink_to(outside, target_is_directory=True)

        evidence = manage_evidence.initialize_evidence(
            self.artifact, self.cases, self.rubric, self.output, "final"
        )

        self.assertEqual(list(outside.iterdir()), [])
        self.assertTrue((self.output.parent / evidence["cohorts"][0]["runs"][0]["prompt"]).is_file())

    def test_init_rejects_symlink_ancestor_without_creating_outside_parent(self):
        outside = self.root / "outside"
        outside.mkdir()
        linked = self.root / "linked"
        linked.symlink_to(outside, target_is_directory=True)
        output = linked / "cohort" / "evidence.json"

        with self.assertRaises(manage_evidence.EvidenceError):
            manage_evidence.initialize_evidence(
                self.artifact, self.cases, self.rubric, output, "final"
            )

        self.assertEqual(list(outside.iterdir()), [])

    def test_init_runs_swap_cannot_redirect_install_outside(self):
        outside = self.root / "outside"
        outside.mkdir()
        real_replace = manage_evidence.evidence_store.os.replace
        swapped = {"done": False}

        detached_data = self.root / "detached-data"

        def swap_runs_before_install(source, destination, *args, **kwargs):
            if (
                not swapped["done"]
                and destination.startswith("final-")
                and kwargs.get("dst_dir_fd") is not None
            ):
                swapped["done"] = True
                data = self.output.parent / ".evidence-data"
                data.rename(detached_data)
                data.symlink_to(outside, target_is_directory=True)
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            swap_runs_before_install,
        ):
            with self.assertRaises(manage_evidence.EvidenceError):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )

        self.assertTrue(swapped["done"])
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse(self.output.exists())
        self.assertFalse(
            any(".stage" in path.name for path in self.output.parent.glob(".*"))
        )

    def test_init_parent_rename_before_install_fails_and_rolls_back_detached_writes(self):
        detached = self.root / "detached-cohort"
        replacement_marker = self.output.parent / "unrelated.txt"
        real_replace = manage_evidence.evidence_store.os.replace
        renamed = {"done": False}

        def rename_parent_before_install(source, destination, *args, **kwargs):
            if (
                not renamed["done"]
                and destination.startswith("final-")
                and kwargs.get("dst_dir_fd") is not None
            ):
                renamed["done"] = True
                self.output.parent.rename(detached)
                self.output.parent.mkdir()
                replacement_marker.write_text("preserve", encoding="utf-8")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            rename_parent_before_install,
        ):
            with self.assertRaisesRegex(
                manage_evidence.EvidenceError,
                "directory chain changed",
            ):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )

        self.assertTrue(renamed["done"])
        self.assertFalse(self.output.exists())
        self.assertEqual(replacement_marker.read_text(encoding="utf-8"), "preserve")
        self.assertFalse((detached / "evidence.json").exists())

    def test_init_rollback_does_not_delete_swapped_unrelated_run_directory(self):
        real_replace = manage_evidence.evidence_store.os.replace
        swapped = {"done": False}

        generation = {"path": None}

        def swap_destination_then_fail(source, destination, *args, **kwargs):
            if (
                not swapped["done"]
                and destination == "evidence.json"
                and kwargs.get("dst_dir_fd") is not None
            ):
                swapped["done"] = True
                installed = next(self.output_namespace().glob("final-*"))
                generation["path"] = installed
                backup = installed.with_name(installed.name + ".owned")
                installed.rename(backup)
                installed.mkdir()
                (installed / "unrelated.txt").write_text(
                    "preserve",
                    encoding="utf-8",
                )
                raise OSError("injected after destination swap")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            swap_destination_then_fail,
        ):
            with self.assertRaises(manage_evidence.EvidenceError):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )

        self.assertTrue(swapped["done"])
        self.assertEqual(
            (generation["path"] / "unrelated.txt").read_text(encoding="utf-8"),
            "preserve",
        )
        self.assertFalse(self.output.exists())
        self.assertFalse(
            any(".stage" in path.name for path in self.output.parent.glob(".*"))
        )

    def test_late_init_failure_restores_prior_evidence_artifact_and_runs(self):
        old_evidence_bytes, old_manifest_bytes, old_run = self.write_prior_cohort()
        real_replace = manage_evidence.evidence_store.os.replace

        def fail_evidence_install(source, destination, *args, **kwargs):
            if (
                source.startswith(".evidence.json.")
                and destination == "evidence.json"
                and kwargs.get("src_dir_fd") is not None
            ):
                raise OSError("late injected failure")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            fail_evidence_install,
        ):
            with self.assertRaises(manage_evidence.EvidenceError):
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )

        self.assertEqual(self.output.read_bytes(), old_evidence_bytes)
        self.assertIn(old_manifest_bytes, [path.read_bytes() for path in self.output.parent.glob(".evidence-data/*/*/artifact.json")])
        self.assertEqual(
            (old_run / "response.md").read_text(encoding="utf-8"),
            "old response\n",
        )
        self.assertFalse((self.output.parent / "runs/final-case-1").exists())
        self.assertFalse(
            any(".stage" in path.name for path in self.output.parent.glob(".*"))
        )

    def test_evidence_identity_race_preserves_unrelated_replacement_and_prior_recovery(self):
        old_evidence_bytes, _, _ = self.write_prior_cohort()
        prior_mode = stat.S_IMODE(self.output.stat().st_mode)
        descriptors_before = len(os.listdir("/dev/fd"))
        real_replace = manage_evidence.evidence_store.os.replace
        replaced = {"done": False}

        def replace_installed_evidence_inode(source, destination, *args, **kwargs):
            result = real_replace(source, destination, *args, **kwargs)
            if (
                not replaced["done"]
                and source.startswith(".evidence.json.")
                and destination == "evidence.json"
                and kwargs.get("dst_dir_fd") is not None
            ):
                replaced["done"] = True
                os.unlink(destination, dir_fd=kwargs["dst_dir_fd"])
                descriptor = os.open(
                    destination,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=kwargs["dst_dir_fd"],
                )
                try:
                    os.write(descriptor, b"unrelated replacement\n")
                finally:
                    os.close(descriptor)
            return result

        with mock.patch.object(
            manage_evidence.evidence_store.os,
            "replace",
            replace_installed_evidence_inode,
        ):
            with self.assertRaisesRegex(
                manage_evidence.EvidenceError,
                "installed evidence changed during transaction",
            ) as caught:
                manage_evidence.initialize_evidence(
                    self.artifact, self.cases, self.rubric, self.output, "final"
                )
        self.assertTrue(
            any(
                re.search(r"recovery-[0-9a-f]+\.json", note)
                for note in getattr(caught.exception, "__notes__", ())
            )
        )

        recoveries = list(
            self.output_namespace().glob("recovery-*.json")
        )
        self.assertTrue(replaced["done"])
        self.assertEqual(self.output.read_bytes(), b"unrelated replacement\n")
        self.assertEqual(len(recoveries), 1)
        self.assertEqual(recoveries[0].read_bytes(), old_evidence_bytes)
        self.assertEqual(stat.S_IMODE(recoveries[0].stat().st_mode), prior_mode)
        self.assertFalse(
            any(".stage" in path.name for path in self.output.parent.glob(".*"))
        )
        self.assertEqual(len(os.listdir("/dev/fd")), descriptors_before)

    def test_input_contract_rejects_duplicate_case_ids_bad_prompts_and_rubric(self):
        invalid_cases = (
            [{"id": "case-1", "prompt": "x"}, {"id": "case-1", "prompt": "y"}],
            [{"id": "../bad", "prompt": "x"}],
            [{"id": "case-1", "prompt": ""}],
        )
        for value in invalid_cases:
            with self.subTest(value=value):
                self.cases.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(manage_evidence.EvidenceError):
                    manage_evidence.initialize_evidence(
                        self.artifact, self.cases, self.rubric, self.output, "final"
                    )
        self.cases.write_text(json.dumps(list(CASES)), encoding="utf-8")
        for value in (["one", "one"], ["bad/key"], [""], {"one": True}):
            with self.subTest(rubric=value):
                self.rubric.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(manage_evidence.EvidenceError):
                    manage_evidence.initialize_evidence(
                        self.artifact, self.cases, self.rubric, self.output, "final"
                    )


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.evidence = self.root / "evidence.json"
        (self.root / "artifact.json").write_text(json.dumps(artifact_manifest()), encoding="utf-8")
        run_root = self.root / "runs/final-case-1"
        run_root.mkdir(parents=True)
        (run_root / "prompt.md").write_text(CASES[0]["prompt"] + "\n", encoding="utf-8")
        (run_root / "response.md").write_text("response\n", encoding="utf-8")
        (run_root / "files-read.txt").write_text("SKILL.md\n", encoding="utf-8")
        self.evidence.write_text(json.dumps(valid_evidence()), encoding="utf-8")
        self.cases = self.root / "cases.json"
        self.rubric = self.root / "rubric.json"
        self.cases.write_text(json.dumps(list(CASES)), encoding="utf-8")
        self.rubric.write_text(json.dumps(list(RUBRIC)), encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPTS_ROOT / "manage_evidence.py"), *map(str, arguments)],
            cwd=self.root,
            capture_output=True,
            text=True,
        )

    def test_verify_json_human_success_and_diagnostic_exit(self):
        human = self.run_cli("verify", self.evidence, self.cases, self.rubric)
        machine = self.run_cli("verify", self.evidence, self.cases, self.rubric, "--json")
        self.assertEqual((human.returncode, human.stdout), (0, "evidence verified\n"))
        self.assertEqual(json.loads(machine.stdout), {"diagnostics": [], "valid": True})

        evidence = valid_evidence()
        evidence["cohorts"][0]["artifact_digest"] = "b" * 64
        self.evidence.write_text(json.dumps(evidence), encoding="utf-8")
        failed = self.run_cli("verify", self.evidence, self.cases, self.rubric)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(
            failed.stdout,
            "cohort 'final' artifact digest does not match frozen artifact\n",
        )

    def test_summarize_json_and_human(self):
        human = self.run_cli(
            "summarize",
            self.evidence,
            self.cases,
            self.rubric,
        )
        machine = self.run_cli(
            "summarize",
            self.evidence,
            self.cases,
            self.rubric,
            "--json",
        )
        self.assertEqual((human.returncode, human.stdout), (0, "passed: 2\ntotal: 2\n"))
        self.assertEqual(json.loads(machine.stdout), {"passed": 2, "total": 2})

    def test_summarize_incomplete_or_missing_file_returns_diagnostic_exit_one(self):
        draft = valid_evidence()
        draft["cohorts"][0]["runs"][0] = {
            "id": "final-case-1",
            "case_id": "case-1",
            "prompt": "runs/final-case-1/prompt.md",
        }
        self.evidence.write_text(json.dumps(draft), encoding="utf-8")
        incomplete = self.run_cli(
            "summarize",
            self.evidence,
            self.cases,
            self.rubric,
        )
        self.assertEqual(incomplete.returncode, 1)
        self.assertIn("is incomplete", incomplete.stdout)

        self.evidence.write_text(json.dumps(valid_evidence()), encoding="utf-8")
        (self.root / "runs/final-case-1/response.md").unlink()
        missing = self.run_cli(
            "summarize",
            self.evidence,
            self.cases,
            self.rubric,
        )
        self.assertEqual(missing.returncode, 1)
        self.assertIn("response file is missing", missing.stdout)

    def test_summarize_and_verify_share_authoritative_missing_case_diagnostic(self):
        self.cases.write_text(
            json.dumps(
                [
                    CASES[0],
                    {"id": "case-2", "prompt": "Second declared prompt."},
                ]
            ),
            encoding="utf-8",
        )

        verified = self.run_cli(
            "verify",
            self.evidence,
            self.cases,
            self.rubric,
        )
        summarized = self.run_cli(
            "summarize",
            self.evidence,
            self.cases,
            self.rubric,
        )

        expected = "headline cohort is missing case id: case-2\n"
        self.assertEqual((verified.returncode, verified.stdout), (1, expected))
        self.assertEqual(
            (summarized.returncode, summarized.stdout),
            (1, expected),
        )

    def test_malformed_input_returns_two_without_absolute_path(self):
        self.evidence.write_text('{"schema_version":1,"schema_version":2}', encoding="utf-8")
        result = self.run_cli("verify", self.evidence, self.cases, self.rubric)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(str(self.root), result.stderr)
        self.assertIn("manage_evidence:", result.stderr)

    def test_verification_diagnostics_do_not_echo_unsafe_private_ids(self):
        evidence = valid_evidence()
        evidence["cohorts"][0]["runs"][0]["id"] = str(self.root)
        evidence["cohorts"][0]["runs"][0]["response"] = "missing.md"
        self.evidence.write_text(json.dumps(evidence), encoding="utf-8")

        result = self.run_cli("verify", self.evidence, self.cases, self.rubric)

        self.assertEqual(result.returncode, 1)
        self.assertNotIn(str(self.root), result.stdout)

    def test_verification_diagnostics_do_not_echo_unsafe_case_ids(self):
        for case_id in (str(self.root), "bad\nprivate"):
            with self.subTest(case_id=case_id):
                evidence = valid_evidence()
                evidence["cohorts"][0]["runs"][0]["case_id"] = case_id
                self.evidence.write_text(json.dumps(evidence), encoding="utf-8")

                result = self.run_cli(
                    "verify",
                    self.evidence,
                    self.cases,
                    self.rubric,
                )

                self.assertEqual(result.returncode, 1)
                self.assertNotIn(case_id, result.stdout)
                self.assertIn("invalid case_id", result.stdout)

    def test_verify_malformed_case_id_types_exit_one_without_traceback(self):
        for case_id in (["bad"], {"bad": True}, 7):
            with self.subTest(case_id=case_id):
                evidence = valid_evidence()
                evidence["cohorts"][0]["runs"][0]["case_id"] = case_id
                self.evidence.write_text(json.dumps(evidence), encoding="utf-8")

                result = self.run_cli(
                    "verify",
                    self.evidence,
                    self.cases,
                    self.rubric,
                )

                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")
                self.assertIn("invalid case_id", result.stdout)
                self.assertNotIn("Traceback", result.stdout)

    def test_main_returns_status_without_raising(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = manage_evidence.main(
                [
                    "summarize",
                    str(self.evidence),
                    str(self.cases),
                    str(self.rubric),
                    "--json",
                ]
            )
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(stdout.getvalue()), {"passed": 2, "total": 2})


if __name__ == "__main__":
    unittest.main()
