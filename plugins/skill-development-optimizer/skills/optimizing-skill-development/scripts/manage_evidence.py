#!/usr/bin/env python3

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_sibling(name):
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


evidence_schema = _load_sibling("evidence_schema")
evidence_store = _load_sibling("evidence_store")

EvidenceError = evidence_schema.EvidenceError
initialize_evidence = evidence_store.initialize_evidence
complete_evidence = evidence_store.complete_evidence
validate_evidence = evidence_store.validate_evidence
summarize = evidence_schema.summarize


def _safe_cli_error(error, paths):
    message = str(error)
    for path in paths:
        try:
            message = message.replace(str(Path(path).resolve()), Path(path).name)
        except (OSError, ValueError):
            pass
        message = message.replace(str(path), Path(path).name)
    return message


def _print_json(value):
    sys.stdout.write(json.dumps(value, sort_keys=True) + "\n")


def _print_diagnostics(diagnostics, as_json):
    if as_json:
        _print_json(
            {
                "schema_version": 1,
                "diagnostics": diagnostics,
                "valid": not diagnostics,
            }
        )
    elif diagnostics:
        sys.stdout.write("".join(f"{item}\n" for item in diagnostics))
    else:
        sys.stdout.write("evidence verified\n")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Initialize and verify frozen evaluation evidence."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    init_parser = commands.add_parser("init")
    init_parser.add_argument("artifact")
    init_parser.add_argument("cases")
    init_parser.add_argument("rubric")
    init_parser.add_argument("output")
    init_parser.add_argument("--cohort", required=True)
    complete_parser = commands.add_parser(
        "complete",
        description=(
            "Publish completion text in a new immutable generation. Completion "
            "runs identify cases without supplying run ids; managed draft run "
            "ids are preserved."
        ),
    )
    complete_parser.add_argument("evidence")
    complete_parser.add_argument("cases")
    complete_parser.add_argument("rubric")
    complete_parser.add_argument(
        "completion",
        help=(
            "schema-1 JSON with exact keys schema_version, cohort_id, and runs"
        ),
    )
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("evidence")
    verify_parser.add_argument("cases")
    verify_parser.add_argument("rubric")
    verify_parser.add_argument("--json", action="store_true", dest="as_json")
    summary_parser = commands.add_parser(
        "summarize",
        description=(
            "Verify authoritative current-case coverage, referenced files, "
            "and prompts before scoring complete evidence."
        ),
    )
    summary_parser.add_argument("evidence")
    summary_parser.add_argument("cases")
    summary_parser.add_argument("rubric")
    summary_parser.add_argument("--json", action="store_true", dest="as_json")
    arguments = parser.parse_args(argv)
    paths = [
        value
        for name, value in vars(arguments).items()
        if name
        in (
            "artifact",
            "cases",
            "rubric",
            "output",
            "evidence",
            "completion",
        )
    ]
    try:
        if arguments.command == "init":
            result = initialize_evidence(
                Path(arguments.artifact),
                Path(arguments.cases),
                Path(arguments.rubric),
                Path(arguments.output),
                arguments.cohort,
            )
            _print_json(result)
            return 0
        if arguments.command == "complete":
            result = complete_evidence(
                Path(arguments.evidence),
                Path(arguments.cases),
                Path(arguments.rubric),
                Path(arguments.completion),
            )
            _print_json(result)
            return 0
        evidence = evidence_schema.load_json(arguments.evidence, "evidence")
        cases = evidence_schema.validate_cases(
            evidence_schema.load_json(arguments.cases, "cases")
        )
        rubric = evidence_schema.validate_rubric(
            evidence_schema.load_json(arguments.rubric, "rubric")
        )
        diagnostics = validate_evidence(
            Path(arguments.evidence).parent,
            evidence,
            cases,
            rubric,
        )
        if diagnostics:
            _print_diagnostics(diagnostics, arguments.as_json)
            return 1
        if arguments.command == "verify":
            _print_diagnostics([], arguments.as_json)
            return 0
        result = summarize(evidence, rubric)
        if arguments.as_json:
            _print_json({"schema_version": 1, **result})
        else:
            sys.stdout.write(
                f"passed: {result['passed']}\ntotal: {result['total']}\n"
            )
        return 0
    except (EvidenceError, OSError) as error:
        print(
            f"manage_evidence: {_safe_cli_error(error, paths)}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
