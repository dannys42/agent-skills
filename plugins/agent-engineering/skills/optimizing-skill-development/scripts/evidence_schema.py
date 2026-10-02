import json
import re
from pathlib import Path, PurePosixPath


ALGORITHM = "sha256-length-framed-v1"
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
EVIDENCE_KEYS = {
    "schema_version",
    "artifact",
    "headline_cohort",
    "cohorts",
}
ARTIFACT_KEYS = {"algorithm", "digest", "manifest"}
COHORT_KEYS = {"id", "status", "artifact_digest", "runs"}
RUN_KEYS = {
    "id",
    "case_id",
    "prompt",
    "response",
    "files_read",
    "files_read_kind",
    "rubric",
}
DRAFT_RUN_KEYS = {"id", "case_id", "prompt"}
MANIFEST_KEYS = {
    "schema_version",
    "algorithm",
    "digest",
    "target",
    "files",
}
MANIFEST_FILE_KEYS = {"path", "bytes"}
GENERATION_KEYS = {
    "schema_version",
    "output_key",
    "generation_id",
    "cohort_id",
    "cases",
    "rubric",
    "artifact",
    "paths",
}
GENERATION_ARTIFACT_KEYS = {"algorithm", "digest"}
GENERATION_PATHS = {
    "evidence": "evidence.json",
    "artifact": "artifact.json",
    "runs": "runs",
}
COMPLETION_KEYS = {"schema_version", "cohort_id", "runs"}
COMPLETION_RUN_KEYS = {
    "case_id",
    "response",
    "files_read",
    "files_read_kind",
    "rubric",
}


class EvidenceError(ValueError):
    pass


def _duplicate_rejecting_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def decode_json(content, label):
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EvidenceError(f"{label} is not valid UTF-8") from error
    try:
        return json.loads(
            text,
            object_pairs_hook=_duplicate_rejecting_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                EvidenceError(f"{label} contains non-finite number: {value}")
            ),
        )
    except EvidenceError:
        raise
    except json.JSONDecodeError as error:
        raise EvidenceError(f"{label} is malformed JSON") from error


def load_json(path, label):
    try:
        content = Path(path).read_bytes()
    except OSError as error:
        reason = getattr(error, "strerror", None) or "cannot read file"
        raise EvidenceError(f"{label}: {reason}") from error
    return decode_json(content, label)


def is_digest(value):
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def is_safe_id(value):
    return isinstance(value, str) and _SAFE_ID.fullmatch(value) is not None


def safe_relative(value):
    if not isinstance(value, str):
        return None
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return None
    if (
        not value
        or "\\" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        return None
    parts = value.split("/")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or any(part in ("", ".", "..") for part in parts)
        or path.as_posix() != value
    ):
        return None
    return value


def validate_cases(value):
    if not isinstance(value, list):
        raise EvidenceError("cases must be a JSON list")
    cases = []
    seen = set()
    for index, case in enumerate(value):
        if not isinstance(case, dict) or set(case) not in (
            {"id", "prompt"},
            {"id", "prompt", "expected_profile"},
        ):
            raise EvidenceError(f"case at index {index} has unexpected keys")
        case_id = case["id"]
        prompt = case["prompt"]
        if not is_safe_id(case_id):
            raise EvidenceError(f"case id at index {index} is not safe")
        if case_id in seen:
            raise EvidenceError(f"duplicate case id: {case_id}")
        if not isinstance(prompt, str) or not prompt:
            raise EvidenceError(f"case '{case_id}' prompt must be a nonempty string")
        try:
            prompt.encode("utf-8")
        except UnicodeEncodeError as error:
            raise EvidenceError(f"case '{case_id}' prompt is not valid UTF-8") from error
        if "expected_profile" in case and not is_safe_id(case["expected_profile"]):
            raise EvidenceError(
                f"case '{case_id}' expected_profile is not a safe value"
            )
        seen.add(case_id)
        normalized = {"id": case_id, "prompt": prompt}
        if "expected_profile" in case:
            normalized["expected_profile"] = case["expected_profile"]
        cases.append(normalized)
    if not cases:
        raise EvidenceError("cases must not be empty")
    return tuple(cases)


def validate_rubric(value):
    if not isinstance(value, list):
        raise EvidenceError("rubric must be a JSON list")
    seen = set()
    items = []
    for index, item in enumerate(value):
        if not is_safe_id(item):
            raise EvidenceError(f"rubric item at index {index} is not a safe key")
        if item in seen:
            raise EvidenceError(f"duplicate rubric item: {item}")
        seen.add(item)
        items.append(item)
    if not items:
        raise EvidenceError("rubric must not be empty")
    return tuple(items)


def validate_completion(value, cases, rubric_items):
    if not isinstance(value, dict) or set(value) != COMPLETION_KEYS:
        raise EvidenceError("completion has unexpected keys")
    if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise EvidenceError("completion schema_version must be 1")
    cohort_id = value.get("cohort_id")
    if not is_safe_id(cohort_id):
        raise EvidenceError("completion cohort_id is not safe")
    runs = value.get("runs")
    if not isinstance(runs, list):
        raise EvidenceError("completion runs must be a list")

    case_ids = [case["id"] for case in cases]
    declared_cases = set(case_ids)
    rubric_set = set(rubric_items)
    completions = {}
    for index, run in enumerate(runs):
        if not isinstance(run, dict) or set(run) != COMPLETION_RUN_KEYS:
            raise EvidenceError(f"completion run at index {index} has unexpected keys")
        case_id = run.get("case_id")
        if not is_safe_id(case_id):
            raise EvidenceError(f"completion run at index {index} case_id is not safe")
        if case_id not in declared_cases:
            raise EvidenceError(f"completion has unknown case id: {case_id}")
        if case_id in completions:
            raise EvidenceError(f"completion has duplicate case id: {case_id}")
        for field in ("response", "files_read"):
            text = run.get(field)
            if not isinstance(text, str) or not text:
                raise EvidenceError(
                    f"completion case '{case_id}' {field} must be nonempty text"
                )
            try:
                text.encode("utf-8")
            except UnicodeEncodeError as error:
                raise EvidenceError(
                    f"completion case '{case_id}' {field} is not valid UTF-8"
                ) from error
        if run.get("files_read_kind") not in (
            "agent-reported",
            "independently-observed",
        ):
            raise EvidenceError(
                f"completion case '{case_id}' files_read_kind is invalid"
            )
        scores = run.get("rubric")
        if not isinstance(scores, dict) or set(scores) != rubric_set:
            raise EvidenceError(
                f"completion case '{case_id}' rubric keys do not match"
            )
        if any(type(score) is not bool for score in scores.values()):
            raise EvidenceError(
                f"completion case '{case_id}' rubric scores must be boolean"
            )
        completions[case_id] = run

    missing = [case_id for case_id in case_ids if case_id not in completions]
    if missing:
        raise EvidenceError(f"completion is missing case id: {missing[0]}")
    return {
        "schema_version": 1,
        "cohort_id": cohort_id,
        "runs": tuple(completions[case_id] for case_id in case_ids),
    }


def validate_manifest(value):
    if not isinstance(value, dict) or set(value) != MANIFEST_KEYS:
        raise EvidenceError("artifact manifest has unexpected keys")
    if value["schema_version"] != 1:
        raise EvidenceError("artifact manifest schema_version must be 1")
    if value["algorithm"] != ALGORITHM:
        raise EvidenceError("artifact manifest algorithm is unsupported")
    if not is_digest(value["digest"]):
        raise EvidenceError(
            "artifact manifest digest must be 64 lowercase hexadecimal characters"
        )
    if safe_relative(value["target"]) is None:
        raise EvidenceError("artifact manifest target is not a safe POSIX-relative path")
    files = value["files"]
    if not isinstance(files, list) or not files:
        raise EvidenceError("artifact manifest files must be a nonempty list")
    seen = set()
    previous = None
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != MANIFEST_FILE_KEYS:
            raise EvidenceError("artifact manifest file has unexpected keys")
        path = entry["path"]
        if safe_relative(path) is None:
            raise EvidenceError(
                "artifact manifest file path is not a safe POSIX-relative path"
            )
        if path in seen:
            raise EvidenceError(f"artifact manifest has duplicate file path: {path}")
        if previous is not None and path < previous:
            raise EvidenceError("artifact manifest files are not sorted")
        byte_count = entry["bytes"]
        if (
            isinstance(byte_count, bool)
            or not isinstance(byte_count, int)
            or byte_count < 0
        ):
            raise EvidenceError(
                f"artifact manifest file byte count is invalid: {path}"
            )
        seen.add(path)
        previous = path
    return value


def make_generation_marker(output_key, generation_id, cohort_id, cases, rubric, manifest):
    return {
        "schema_version": 1,
        "output_key": output_key,
        "generation_id": generation_id,
        "cohort_id": cohort_id,
        "cases": list(cases),
        "rubric": list(rubric),
        "artifact": {
            "algorithm": manifest["algorithm"],
            "digest": manifest["digest"],
        },
        "paths": dict(GENERATION_PATHS),
    }


def validate_generation_marker(value, output_key, generation_id):
    if not isinstance(value, dict) or set(value) != GENERATION_KEYS:
        raise EvidenceError("generation marker has unexpected keys")
    if value.get("schema_version") != 1:
        raise EvidenceError("generation marker schema_version must be 1")
    if (
        not is_digest(value.get("output_key"))
        or value["output_key"] != output_key
    ):
        raise EvidenceError("generation marker output_key does not match namespace")
    if (
        not is_safe_id(value.get("generation_id"))
        or value["generation_id"] != generation_id
    ):
        raise EvidenceError("generation marker id does not match directory")
    cohort_id = value.get("cohort_id")
    if (
        not is_safe_id(cohort_id)
        or not generation_id.startswith(cohort_id + "-")
    ):
        raise EvidenceError("generation marker cohort id is malformed")
    cases = validate_cases(value.get("cases"))
    rubric = validate_rubric(value.get("rubric"))
    artifact = value.get("artifact")
    if (
        not isinstance(artifact, dict)
        or set(artifact) != GENERATION_ARTIFACT_KEYS
        or artifact.get("algorithm") != ALGORITHM
        or not is_digest(artifact.get("digest"))
    ):
        raise EvidenceError("generation marker artifact is malformed")
    if value.get("paths") != GENERATION_PATHS:
        raise EvidenceError("generation marker paths are malformed")
    return {
        **value,
        "cases": cases,
        "rubric": rubric,
    }


def validate_structure(evidence, rubric_items, *, allow_drafts=False):
    if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_KEYS:
        raise EvidenceError("evidence has unexpected keys")
    if evidence.get("schema_version") != 1:
        raise EvidenceError("evidence schema_version must be 1")
    artifact = evidence.get("artifact")
    if (
        not isinstance(artifact, dict)
        or set(artifact) != ARTIFACT_KEYS
        or artifact.get("algorithm") != ALGORITHM
        or not is_digest(artifact.get("digest"))
        or safe_relative(artifact.get("manifest")) is None
    ):
        raise EvidenceError("evidence artifact is malformed")
    cohorts = evidence.get("cohorts")
    if not isinstance(cohorts, list):
        raise EvidenceError("evidence cohorts must be a list")

    cohort_ids = set()
    run_ids = set()
    headline_ids = []
    headline_case_ids = set()
    rubric_set = set(rubric_items)
    for cohort in cohorts:
        if not isinstance(cohort, dict) or set(cohort) != COHORT_KEYS:
            raise EvidenceError("cohort has unexpected keys")
        cohort_id = cohort.get("id")
        if not is_safe_id(cohort_id):
            raise EvidenceError("cohort id is not safe")
        if cohort_id in cohort_ids:
            raise EvidenceError(f"duplicate cohort id: {cohort_id}")
        cohort_ids.add(cohort_id)
        status = cohort.get("status")
        if status not in ("headline", "historical"):
            raise EvidenceError(f"cohort '{cohort_id}' has invalid status")
        digest = cohort.get("artifact_digest")
        if not is_digest(digest):
            raise EvidenceError(f"cohort '{cohort_id}' artifact digest is malformed")
        if status == "headline":
            headline_ids.append(cohort_id)
            if digest != artifact["digest"]:
                raise EvidenceError(
                    f"cohort '{cohort_id}' artifact digest does not match frozen artifact"
                )
        runs = cohort.get("runs")
        if not isinstance(runs, list):
            raise EvidenceError(f"cohort '{cohort_id}' runs must be a list")
        for run in runs:
            keys = set(run) if isinstance(run, dict) else set()
            if not isinstance(run, dict) or keys not in (RUN_KEYS, DRAFT_RUN_KEYS):
                raise EvidenceError("run has unexpected keys")
            run_id = run.get("id")
            case_id = run.get("case_id")
            if not is_safe_id(run_id):
                raise EvidenceError("run id is not safe")
            if run_id in run_ids:
                raise EvidenceError(f"duplicate run id: {run_id}")
            run_ids.add(run_id)
            if not is_safe_id(case_id):
                raise EvidenceError(f"run '{run_id}' has invalid case_id")
            if status == "headline":
                if case_id in headline_case_ids:
                    raise EvidenceError(
                        f"headline cohort has duplicate case id: {case_id}"
                    )
                headline_case_ids.add(case_id)
            for field in ("prompt", "response", "files_read"):
                if field in run and safe_relative(run[field]) is None:
                    raise EvidenceError(
                        f"run '{run_id}' {field} is not a safe POSIX-relative path"
                    )
            if keys == DRAFT_RUN_KEYS:
                if not allow_drafts:
                    raise EvidenceError(f"run '{run_id}' is incomplete")
                continue
            if run.get("files_read_kind") not in (
                "agent-reported",
                "independently-observed",
            ):
                raise EvidenceError(f"run '{run_id}' has invalid files_read_kind")
            scores = run.get("rubric")
            if not isinstance(scores, dict) or not scores:
                raise EvidenceError(f"run '{run_id}' rubric is malformed")
            if any(
                not is_safe_id(key) or type(score) is not bool
                for key, score in scores.items()
            ):
                raise EvidenceError(f"run '{run_id}' rubric is malformed")
            if status == "headline" and set(scores) != rubric_set:
                raise EvidenceError(f"run '{run_id}' rubric is malformed")
    if len(headline_ids) != 1:
        raise EvidenceError("evidence must contain exactly one headline cohort")
    if evidence.get("headline_cohort") != headline_ids[0]:
        raise EvidenceError("headline_cohort does not identify the headline cohort")
    return cohorts


def summarize(evidence, rubric_items):
    """Score structure only; authoritative case coverage requires CLI verification."""
    validate_structure(evidence, rubric_items)
    headline = next(
        cohort for cohort in evidence["cohorts"] if cohort["status"] == "headline"
    )
    if not headline["runs"]:
        raise EvidenceError("headline cohort is incomplete")
    return {
        "passed": sum(
            score
            for run in headline["runs"]
            for score in run["rubric"].values()
        ),
        "total": sum(len(run["rubric"]) for run in headline["runs"]),
    }
