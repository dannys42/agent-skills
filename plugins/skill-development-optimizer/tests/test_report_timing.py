import contextlib
import copy
import io
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import load_script


report_timing = load_script("report_timing")


def command(
    identifier,
    duration,
    timing_kind="work",
    status="passed",
):
    return {
        "id": identifier,
        "status": status,
        "duration_seconds": duration,
        "exit_code": 0 if status == "passed" else None,
        "stdout": "",
        "stderr": "",
        "stdout_truncated": False,
        "stderr_truncated": False,
        "timing_kind": timing_kind,
    }


def report(*commands, profile="quick", status="passed"):
    return {
        "schema_version": 1,
        "profile": profile,
        "status": status,
        "generated_at": "2026-07-31T12:00:00Z",
        "commands": list(commands),
        "duration_seconds": math.fsum(
            item["duration_seconds"] for item in commands
        ),
    }


class TimingReportTests(unittest.TestCase):
    def test_ranks_bottlenecks_and_separates_mandatory_wait(self):
        reports = [
            report(
                command("forward-evaluation", 30.0),
                command("polite-download", 20.0, "mandatory_wait"),
                command("quick-validation", 2.0),
            )
        ]

        summary = report_timing.summarize_reports(reports)

        self.assertEqual(summary["schema_version"], 1)
        self.assertEqual(summary["report_count"], 1)
        self.assertEqual(summary["command_count"], 3)
        self.assertEqual(summary["total_seconds"], 52.0)
        self.assertEqual(summary["work_seconds"], 32.0)
        self.assertEqual(summary["mandatory_wait_seconds"], 20.0)
        self.assertEqual(
            summary["status_counts"],
            {
                "passed": 3,
                "failed": 0,
                "timed_out": 0,
                "approval_required": 0,
            },
        )
        self.assertEqual(
            [item["id"] for item in summary["bottlenecks"]],
            ["forward-evaluation", "polite-download", "quick-validation"],
        )
        self.assertEqual(
            summary["bottlenecks"][0],
            {
                "id": "forward-evaluation",
                "duration_seconds": 30.0,
                "timing_kind": "work",
                "status": "passed",
                "percentage_of_total": 30.0 / 52.0 * 100.0,
            },
        )

    def test_aggregates_multiple_reports_and_counts_blocking_statuses(self):
        reports = [
            report(
                command("compile", 1.5, status="failed"),
                status="failed",
            ),
            report(
                command("compile", 2.5, status="timed_out"),
                command("approval", 0, "mandatory_wait", "approval_required"),
                status="timed_out",
            ),
        ]

        summary = report_timing.summarize_reports(reports)

        self.assertEqual(summary["report_count"], 2)
        self.assertEqual(summary["command_count"], 3)
        self.assertEqual(summary["total_seconds"], 4.0)
        self.assertEqual(
            summary["status_counts"],
            {
                "passed": 0,
                "failed": 1,
                "timed_out": 1,
                "approval_required": 1,
            },
        )

    def test_ties_sort_by_identifier_then_retain_report_and_command_order(self):
        reports = [
            report(
                command("same", 5.0, status="failed"),
                command("z-last", 5.0),
            ),
            report(command("same", 5.0, status="timed_out")),
        ]

        bottlenecks = report_timing.summarize_reports(reports)["bottlenecks"]

        self.assertEqual(
            [(item["id"], item["status"]) for item in bottlenecks],
            [
                ("same", "failed"),
                ("same", "timed_out"),
                ("z-last", "passed"),
            ],
        )

    def test_empty_input_has_zero_summary_without_mutating_input(self):
        reports = [report()]
        original = copy.deepcopy(reports)

        summary = report_timing.summarize_reports(reports)

        self.assertEqual(reports, original)
        self.assertEqual(
            summary,
            {
                "schema_version": 1,
                "report_count": 1,
                "command_count": 0,
                "total_seconds": 0.0,
                "work_seconds": 0.0,
                "mandatory_wait_seconds": 0.0,
                "status_counts": {
                    "passed": 0,
                    "failed": 0,
                    "timed_out": 0,
                    "approval_required": 0,
                },
                "bottlenecks": [],
            },
        )
        self.assertEqual(report_timing.render_human(summary), "No timing evidence.")

    def test_rejects_invalid_duration_values(self):
        for duration in (
            -1,
            float("nan"),
            float("inf"),
            True,
            "1",
            10**1000,
        ):
            with self.subTest(duration=duration):
                invalid_report = report(command("placeholder", 0))
                invalid_report["commands"][0]["duration_seconds"] = duration
                with self.assertRaisesRegex(
                    report_timing.TimingError,
                    r"report 1 command 1 duration_seconds must be a finite "
                    r"non-negative number",
                ):
                    report_timing.summarize_reports([invalid_report])

    def test_rejects_aggregate_duration_overflow(self):
        overflowing = report(command("first", 1e308))
        overflowing["commands"].append(command("second", 1e308))
        overflowing["duration_seconds"] = 1e308

        with self.assertRaisesRegex(
            report_timing.TimingError,
            "^timing totals exceed the finite numeric range$",
        ):
            report_timing.summarize_reports([overflowing])

    def test_rejects_integer_duration_not_exactly_representable_as_float(self):
        invalid_report = report(command("rounded", 0))
        invalid_report["commands"][0]["duration_seconds"] = 9_007_199_254_740_993

        with self.assertRaisesRegex(
            report_timing.TimingError,
            r"report 1 command 1 duration_seconds must be a finite "
            r"non-negative number",
        ):
            report_timing.summarize_reports([invalid_report])

    def test_exact_integer_float_boundary_preserves_adjacent_ranking(self):
        reports = [
            report(
                command("higher", 2**53),
                command("lower", 2**53 - 1),
            )
        ]

        bottlenecks = report_timing.summarize_reports(reports)["bottlenecks"]

        self.assertEqual(
            [item["id"] for item in bottlenecks],
            ["higher", "lower"],
        )
        self.assertEqual(
            [item["duration_seconds"] for item in bottlenecks],
            [float(2**53), float(2**53 - 1)],
        )
        self.assertNotEqual(
            bottlenecks[0]["duration_seconds"],
            bottlenecks[1]["duration_seconds"],
        )

    def test_rejects_malformed_report_and_command_shapes(self):
        malformed = [
            (None, "report 1 must be an object"),
            ([], "report 1 must be an object"),
            (
                {**report(), "unexpected": 1},
                "report 1 must contain exactly the Task 7 report fields",
            ),
            (
                {**report(), "commands": {}},
                "report 1 commands must be a list",
            ),
            (
                {**report(), "commands": [None]},
                "report 1 command 1 must be an object",
            ),
            (
                report({**command("one", 1), "extra": 1}),
                "report 1 command 1 must contain exactly the Task 7 command fields",
            ),
        ]
        for value, message in malformed:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    report_timing.TimingError,
                    f"^{message}$",
                ):
                    report_timing.summarize_reports([value])

    def test_rejects_invalid_identifiers_statuses_and_timing_kinds(self):
        cases = [
            ("id", "", "must be a non-empty safe single-line string"),
            ("id", "secret\n/path", "must be a non-empty safe single-line string"),
            ("id", "\x1b[31mred", "must be a non-empty safe single-line string"),
            ("status", "unknown", "status must be one of"),
            ("timing_kind", "sleep", "timing_kind must be one of"),
        ]
        for field, value, message in cases:
            invalid = command("one", 1)
            invalid[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(
                    report_timing.TimingError,
                    message,
                ):
                    report_timing.summarize_reports([report(invalid)])

    def test_rejects_malformed_task_7_command_result_fields(self):
        cases = [
            ("exit_code", True, "exit_code must be an integer or null"),
            ("exit_code", "0", "exit_code must be an integer or null"),
            ("stdout", {}, "stdout must be a string"),
            ("stderr", [], "stderr must be a string"),
            ("stdout_truncated", 0, "stdout_truncated must be a boolean"),
            ("stderr_truncated", None, "stderr_truncated must be a boolean"),
        ]
        for field, value, message in cases:
            invalid = command("one", 1)
            invalid[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(
                    report_timing.TimingError,
                    message,
                ):
                    report_timing.summarize_reports([report(invalid)])

    def test_validates_task_7_report_metadata(self):
        cases = [
            ("schema_version", 2),
            ("schema_version", True),
            ("profile", ""),
            ("status", "unknown"),
            ("generated_at", "unsafe\nvalue"),
            ("duration_seconds", float("inf")),
        ]
        for field, value in cases:
            invalid = report()
            invalid[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaises(report_timing.TimingError):
                    report_timing.summarize_reports([invalid])

    def test_human_output_rounds_display_and_reports_work_wait_and_bottlenecks(self):
        summary = report_timing.summarize_reports(
            [
                report(
                    command("work", 1.23456),
                    command("wait", 0.33333, "mandatory_wait"),
                )
            ]
        )

        rendered = report_timing.render_human(summary)

        self.assertIn("Total: 1.57s", rendered)
        self.assertIn("Work: 1.23s", rendered)
        self.assertIn("Mandatory wait: 0.33s", rendered)
        self.assertIn("1. work — 1.23s", rendered)
        self.assertNotIn("optimized", rendered.lower())


class TimingCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def invoke(self, *arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = report_timing.main(list(arguments))
        return code, stdout.getvalue(), stderr.getvalue()

    def write_bytes(self, name, content):
        path = self.root / name
        path.write_bytes(content)
        return path

    def test_json_output_preserves_precision_and_is_deterministic(self):
        first = self.write_bytes(
            "first.json",
            json.dumps(report(command("a", 0.1))).encode(),
        )
        second = self.write_bytes(
            "second.json",
            json.dumps(report(command("b", 0.2))).encode(),
        )

        code, stdout, stderr = self.invoke(str(first), str(second), "--json")

        expected = report_timing.summarize_reports(
            [report(command("a", 0.1)), report(command("b", 0.2))]
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, json.dumps(expected, sort_keys=True) + "\n")
        self.assertEqual(json.loads(stdout)["total_seconds"], math.fsum([0.1, 0.2]))

    def test_cli_rejects_duplicate_keys_nonfinite_json_and_invalid_utf8(self):
        cases = [
            b'{"commands":[],"commands":[]}',
            b'{"duration_seconds":NaN}',
            b"\xff",
        ]
        for index, content in enumerate(cases):
            with self.subTest(content=content):
                path = self.write_bytes(f"private-{index}.json", content)
                code, stdout, stderr = self.invoke(str(path))
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("report 1", stderr)
                self.assertNotIn(str(path), stderr)
                self.assertNotIn("Traceback", stderr)

    def test_cli_file_errors_do_not_leak_paths_or_tracebacks(self):
        secret_path = self.root / "private" / "missing.json"

        code, stdout, stderr = self.invoke(str(secret_path))

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error: report 1 could not be read\n")
        self.assertNotIn(str(secret_path), stderr)
        self.assertNotIn("Traceback", stderr)

    def test_cli_controls_json_recursion_as_path_free_malformed_input(self):
        path = self.write_bytes("private-deep.json", b"{}")

        with mock.patch.object(
            report_timing.json,
            "loads",
            side_effect=RecursionError,
        ):
            code, stdout, stderr = self.invoke(str(path))

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error: report 1 is not valid JSON\n")
        self.assertNotIn(str(path), stderr)
        self.assertNotIn("Traceback", stderr)

    def test_cli_controls_unrepresentable_and_aggregate_durations(self):
        huge = report(command("huge", 0))
        huge["commands"][0]["duration_seconds"] = 10**1000
        overflowing = report(command("first", 1e308))
        overflowing["commands"].append(command("second", 1e308))
        overflowing["duration_seconds"] = 1e308

        for index, value in enumerate((huge, overflowing)):
            with self.subTest(index=index):
                path = self.write_bytes(
                    f"private-overflow-{index}.json",
                    json.dumps(value).encode(),
                )
                code, stdout, stderr = self.invoke(str(path), "--json")
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("error:", stderr)
                self.assertNotIn(str(path), stderr)
                self.assertNotIn("Traceback", stderr)


if __name__ == "__main__":
    unittest.main()
