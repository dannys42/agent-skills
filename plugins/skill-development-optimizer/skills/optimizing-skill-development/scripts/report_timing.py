#!/usr/bin/env python3

import argparse
import json
import math
import sys
from pathlib import Path


class TimingError(ValueError):
    pass


_REPORT_FIELDS = {
    "schema_version",
    "profile",
    "status",
    "generated_at",
    "commands",
    "duration_seconds",
}
_COMMAND_FIELDS = {
    "id",
    "status",
    "duration_seconds",
    "exit_code",
    "stdout",
    "stderr",
    "stdout_truncated",
    "stderr_truncated",
    "timing_kind",
}
_STATUSES = ("passed", "failed", "timed_out", "approval_required")
_TIMING_KINDS = ("work", "mandatory_wait")


class _DuplicateKeyError(ValueError):
    pass


def _safe_string(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value.isprintable()


def _finite_non_negative_number(value: object) -> bool:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        return False
    try:
        converted = float(value)
    except OverflowError:
        return False
    if isinstance(value, int) and int(converted) != value:
        return False
    return math.isfinite(converted)


def _sum_durations(values: list[float]) -> float:
    try:
        return math.fsum(values)
    except OverflowError as error:
        raise TimingError(
            "timing totals exceed the finite numeric range"
        ) from error


def _validate_report_metadata(report: dict[str, object], report_number: int) -> None:
    label = f"report {report_number}"
    if set(report) != _REPORT_FIELDS:
        raise TimingError(
            f"{label} must contain exactly the Task 7 report fields"
        )
    schema_version = report["schema_version"]
    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version != 1
    ):
        raise TimingError(f"{label} schema_version must be 1")
    if not _safe_string(report["profile"]):
        raise TimingError(f"{label} profile must be a non-empty safe string")
    if report["status"] not in _STATUSES:
        raise TimingError(f"{label} status must be one of: {', '.join(_STATUSES)}")
    if not _safe_string(report["generated_at"]):
        raise TimingError(
            f"{label} generated_at must be a non-empty safe single-line string"
        )
    if not _finite_non_negative_number(report["duration_seconds"]):
        raise TimingError(
            f"{label} duration_seconds must be a finite non-negative number"
        )
    if not isinstance(report["commands"], list):
        raise TimingError(f"{label} commands must be a list")


def _validated_command(
    value: object,
    report_number: int,
    command_number: int,
) -> dict[str, object]:
    label = f"report {report_number} command {command_number}"
    if not isinstance(value, dict):
        raise TimingError(f"{label} must be an object")
    if set(value) != _COMMAND_FIELDS:
        raise TimingError(
            f"{label} must contain exactly the Task 7 command fields"
        )
    if not _safe_string(value["id"]):
        raise TimingError(
            f"{label} id must be a non-empty safe single-line string"
        )
    if not _finite_non_negative_number(value["duration_seconds"]):
        raise TimingError(
            f"{label} duration_seconds must be a finite non-negative number"
        )
    if value["status"] not in _STATUSES:
        raise TimingError(
            f"{label} status must be one of: {', '.join(_STATUSES)}"
        )
    if value["timing_kind"] not in _TIMING_KINDS:
        raise TimingError(
            f"{label} timing_kind must be one of: {', '.join(_TIMING_KINDS)}"
        )
    exit_code = value["exit_code"]
    if (
        exit_code is not None
        and (
            not isinstance(exit_code, int)
            or isinstance(exit_code, bool)
        )
    ):
        raise TimingError(f"{label} exit_code must be an integer or null")
    for field in ("stdout", "stderr"):
        if not isinstance(value[field], str):
            raise TimingError(f"{label} {field} must be a string")
    for field in ("stdout_truncated", "stderr_truncated"):
        if not isinstance(value[field], bool):
            raise TimingError(f"{label} {field} must be a boolean")
    return value


def summarize_reports(
    reports: list[dict[str, object]],
) -> dict[str, object]:
    if not isinstance(reports, list):
        raise TimingError("reports must be a list")

    commands: list[dict[str, object]] = []
    for report_index, report in enumerate(reports):
        report_number = report_index + 1
        if not isinstance(report, dict):
            raise TimingError(f"report {report_number} must be an object")
        _validate_report_metadata(report, report_number)
        for command_index, command in enumerate(report["commands"]):
            commands.append(
                _validated_command(
                    command,
                    report_number,
                    command_index + 1,
                )
            )

    durations = [float(command["duration_seconds"]) for command in commands]
    work_durations = [
        float(command["duration_seconds"])
        for command in commands
        if command["timing_kind"] == "work"
    ]
    wait_durations = [
        float(command["duration_seconds"])
        for command in commands
        if command["timing_kind"] == "mandatory_wait"
    ]
    total_seconds = _sum_durations(durations)
    status_counts = {
        status: sum(command["status"] == status for command in commands)
        for status in _STATUSES
    }
    ranked_commands = sorted(
        commands,
        key=lambda command: (
            -float(command["duration_seconds"]),
            command["id"],
        ),
    )
    bottlenecks = [
        {
            "id": command["id"],
            "duration_seconds": float(command["duration_seconds"]),
            "timing_kind": command["timing_kind"],
            "status": command["status"],
            "percentage_of_total": (
                float(command["duration_seconds"]) / total_seconds * 100.0
                if total_seconds
                else 0.0
            ),
        }
        for command in ranked_commands
    ]
    return {
        "schema_version": 1,
        "report_count": len(reports),
        "command_count": len(commands),
        "total_seconds": total_seconds,
        "work_seconds": _sum_durations(work_durations),
        "mandatory_wait_seconds": _sum_durations(wait_durations),
        "status_counts": status_counts,
        "bottlenecks": bottlenecks,
    }


def render_human(summary: dict[str, object]) -> str:
    if summary["command_count"] == 0:
        return "No timing evidence."

    report_word = "report" if summary["report_count"] == 1 else "reports"
    command_word = "command" if summary["command_count"] == 1 else "commands"
    counts = summary["status_counts"]
    lines = [
        (
            f"Timing evidence: {summary['command_count']} {command_word} "
            f"across {summary['report_count']} {report_word}."
        ),
        f"Total: {summary['total_seconds']:.2f}s",
        f"Work: {summary['work_seconds']:.2f}s",
        f"Mandatory wait: {summary['mandatory_wait_seconds']:.2f}s",
        (
            "Statuses: "
            f"passed {counts['passed']}, "
            f"failed {counts['failed']}, "
            f"timed out {counts['timed_out']}, "
            f"approval required {counts['approval_required']}"
        ),
        "Bottlenecks:",
    ]
    for rank, bottleneck in enumerate(summary["bottlenecks"], start=1):
        lines.append(
            f"{rank}. {bottleneck['id']} — "
            f"{bottleneck['duration_seconds']:.2f}s "
            f"({bottleneck['percentage_of_total']:.2f}%, "
            f"{bottleneck['timing_kind']}, {bottleneck['status']})"
        )
    return "\n".join(lines)


def _reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise _DuplicateKeyError
        value[key] = item
    return value


def _reject_nonfinite_json(_value):
    raise ValueError


def _load_report(path: str, report_number: int) -> object:
    try:
        content = Path(path).read_bytes()
    except OSError as error:
        raise TimingError(f"report {report_number} could not be read") from error
    try:
        text = content.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_json,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        _DuplicateKeyError,
        ValueError,
        RecursionError,
    ) as error:
        raise TimingError(f"report {report_number} is not valid JSON") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize Task 7 validation timing reports."
    )
    parser.add_argument("reports", nargs="+", metavar="REPORT.json")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit deterministic JSON instead of human-readable output",
    )
    arguments = parser.parse_args(argv)

    try:
        reports = [
            _load_report(path, index + 1)
            for index, path in enumerate(arguments.reports)
        ]
        summary = summarize_reports(reports)
    except TimingError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if arguments.json:
        print(json.dumps(summary, sort_keys=True, allow_nan=False))
    else:
        print(render_human(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
