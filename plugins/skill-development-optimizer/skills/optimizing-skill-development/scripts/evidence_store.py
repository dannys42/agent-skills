#!/usr/bin/env python3

import json
import hashlib
import os
import re
import secrets
import stat
import sys
import threading
from pathlib import Path

import evidence_schema as _schema

try:
    import fcntl
except ImportError:
    fcntl = None


EvidenceError = _schema.EvidenceError
ALGORITHM = _schema.ALGORITHM
_EVIDENCE_KEYS = _schema.EVIDENCE_KEYS
_ARTIFACT_KEYS = _schema.ARTIFACT_KEYS
_COHORT_KEYS = _schema.COHORT_KEYS
_RUN_KEYS = _schema.RUN_KEYS
_DRAFT_RUN_KEYS = _schema.DRAFT_RUN_KEYS
_decode_json = _schema.decode_json
_load_json = _schema.load_json
_is_digest = _schema.is_digest
_is_safe_id = _schema.is_safe_id
_safe_relative = _schema.safe_relative
_validate_cases = _schema.validate_cases
_validate_rubric = _schema.validate_rubric
_validate_manifest = _schema.validate_manifest
_THREAD_LOCKS = {}
_THREAD_LOCKS_GUARD = threading.Lock()
_GENERATION_NAME = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._-]*-[0-9a-f]{32}\Z"
)


def _directory_flags():
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )


def _same_file(first, second):
    return (
        first.st_dev,
        first.st_ino,
        first.st_mode,
    ) == (
        second.st_dev,
        second.st_ino,
        second.st_mode,
    )


def _require_security_capabilities():
    required = (
        hasattr(os, "O_NOFOLLOW"),
        hasattr(os, "O_DIRECTORY"),
        os.open in os.supports_dir_fd,
        os.stat in os.supports_dir_fd,
        os.rename in os.supports_dir_fd,
        fcntl is not None and hasattr(fcntl, "flock"),
    )
    if not all(required):
        raise EvidenceError("required secure filesystem capabilities are unavailable")


def _thread_lock(key):
    with _THREAD_LOCKS_GUARD:
        return _THREAD_LOCKS.setdefault(key, threading.Lock())


def _acquire_parent_evidence_lock(parent_descriptor):
    _require_security_capabilities()
    identity = os.fstat(parent_descriptor)
    process_lock = _thread_lock(("parent", identity.st_dev, identity.st_ino))
    process_lock.acquire()
    flock_acquired = False
    try:
        fcntl.flock(parent_descriptor, fcntl.LOCK_EX)
        flock_acquired = True
        opened = os.fstat(parent_descriptor)
        if not stat.S_ISDIR(opened.st_mode) or not _same_file(opened, identity):
            raise EvidenceError("evidence output parent identity changed")
        return process_lock, identity
    except (EvidenceError, OSError, NotImplementedError, TypeError) as error:
        if flock_acquired:
            try:
                fcntl.flock(parent_descriptor, fcntl.LOCK_UN)
            except (OSError, NotImplementedError, TypeError):
                pass
        process_lock.release()
        if isinstance(error, EvidenceError):
            raise
        reason = getattr(error, "strerror", None) or "operation unavailable"
        raise EvidenceError(
            f"cannot acquire secure evidence parent lock: {reason}"
        ) from error


def _release_parent_evidence_lock(process_lock, parent_descriptor):
    try:
        fcntl.flock(parent_descriptor, fcntl.LOCK_UN)
    finally:
        process_lock.release()


def _verify_evidence_lock(namespace_descriptor, descriptor, identity):
    # This fences races detected during our transaction. A same-UID process can
    # still mutate files after initialize_evidence returns; no filesystem lock
    # can turn those paths into an authorization boundary.
    try:
        opened = os.fstat(descriptor)
        entry = os.stat(
            ".lock",
            dir_fd=namespace_descriptor,
            follow_symlinks=False,
        )
    except (OSError, NotImplementedError, TypeError) as error:
        raise EvidenceError("evidence lock identity changed") from error
    if (
        not stat.S_ISREG(opened.st_mode)
        or not stat.S_ISREG(entry.st_mode)
        or opened.st_nlink != 1
        or entry.st_nlink != 1
        or not _same_file(opened, identity)
        or not _same_file(entry, identity)
    ):
        raise EvidenceError("evidence lock identity changed")


def _acquire_evidence_lock(namespace_descriptor, output_key):
    _require_security_capabilities()
    namespace_identity = os.fstat(namespace_descriptor)
    process_lock = _thread_lock(
        (namespace_identity.st_dev, namespace_identity.st_ino, output_key)
    )
    process_lock.acquire()
    descriptor = None
    flock_acquired = False
    try:
        for attempt in range(16):
            try:
                descriptor = os.open(
                    ".lock",
                    os.O_RDWR
                    | os.O_CREAT
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_CLOEXEC", 0),
                    0o600,
                    dir_fd=namespace_descriptor,
                )
                break
            except FileNotFoundError:
                if attempt == 15:
                    raise
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise EvidenceError("evidence lock is not a private regular file")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        flock_acquired = True
        opened = os.fstat(descriptor)
        _verify_evidence_lock(namespace_descriptor, descriptor, opened)
        return process_lock, descriptor, opened
    except (EvidenceError, OSError, NotImplementedError, TypeError) as error:
        if descriptor is not None:
            if flock_acquired:
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_UN)
                except (OSError, NotImplementedError, TypeError):
                    pass
            os.close(descriptor)
        process_lock.release()
        if isinstance(error, EvidenceError):
            raise
        reason = getattr(error, "strerror", None) or "operation unavailable"
        raise EvidenceError(f"cannot acquire secure evidence lock: {reason}") from error


def _release_evidence_lock(process_lock, descriptor):
    try:
        try:
            if fcntl is not None:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)
    finally:
        process_lock.release()


def _open_root(root):
    try:
        before = Path(root).lstat()
        descriptor = os.open(root, _directory_flags())
        opened = os.fstat(descriptor)
    except OSError as error:
        raise EvidenceError("evidence root is missing or not a stable directory") from error
    if (
        not stat.S_ISDIR(before.st_mode)
        or not stat.S_ISDIR(opened.st_mode)
        or not _same_file(before, opened)
    ):
        os.close(descriptor)
        raise EvidenceError("evidence root is missing or not a stable directory")
    return descriptor


def _read_anchored(root_descriptor, relative, label):
    components = relative.split("/")
    descriptor = os.dup(root_descriptor)
    traversed = []
    try:
        for component in components[:-1]:
            traversed.append(component)
            try:
                before = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
                child = os.open(component, _directory_flags(), dir_fd=descriptor)
                opened = os.fstat(child)
            except OSError as error:
                raise EvidenceError(
                    f"{label} is missing or not a regular nonsymlink file"
                ) from error
            if (
                stat.S_ISLNK(before.st_mode)
                or not stat.S_ISDIR(before.st_mode)
                or not stat.S_ISDIR(opened.st_mode)
                or not _same_file(before, opened)
            ):
                os.close(child)
                raise EvidenceError(
                    f"{label} is missing or not a regular nonsymlink file"
                )
            os.close(descriptor)
            descriptor = child

        name = components[-1]
        try:
            before = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            file_descriptor = os.open(
                name,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0),
                dir_fd=descriptor,
            )
            opened = os.fstat(file_descriptor)
        except OSError as error:
            raise EvidenceError(
                f"{label} is missing or not a regular nonsymlink file"
            ) from error
        try:
            if (
                stat.S_ISLNK(before.st_mode)
                or not stat.S_ISREG(before.st_mode)
                or not stat.S_ISREG(opened.st_mode)
            ):
                raise EvidenceError(
                    f"{label} is missing or not a regular nonsymlink file"
                )
            if not _same_file(before, opened):
                raise EvidenceError(f"{label} changed before it could be read")
            chunks = []
            while True:
                chunk = os.read(file_descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after = os.fstat(file_descriptor)
            if (
                not _same_file(opened, after)
                or opened.st_size != after.st_size
                or opened.st_mtime_ns != after.st_mtime_ns
                or opened.st_ctime_ns != after.st_ctime_ns
            ):
                raise EvidenceError(f"{label} changed while it was read")
            return b"".join(chunks)
        finally:
            os.close(file_descriptor)
    finally:
        os.close(descriptor)


def _append_file_diagnostic(
    diagnostics,
    root_descriptor,
    relative,
    run_id,
    field,
    *,
    nonempty=False,
):
    if _safe_relative(relative) is None:
        diagnostics.append(
            f"run '{run_id}' {field} is not a safe POSIX-relative path"
        )
        return None
    label = f"run '{run_id}' {field} file"
    try:
        content = _read_anchored(root_descriptor, relative, label)
    except EvidenceError as error:
        diagnostics.append(str(error))
        return None
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        diagnostics.append(f"{label} is not valid UTF-8")
        return None
    if nonempty and not content:
        diagnostics.append(f"{label} must be nonempty")
    return text


def validate_evidence(
    root,
    evidence,
    cases,
    rubric_items,
    *,
    _root_descriptor=None,
):
    diagnostics = []
    if not isinstance(evidence, dict):
        return ["evidence must be a JSON object"]
    if set(evidence) != _EVIDENCE_KEYS:
        diagnostics.append("evidence has unexpected keys")
    if evidence.get("schema_version") != 1:
        diagnostics.append("evidence schema_version must be 1")

    artifact = evidence.get("artifact")
    artifact_digest = None
    if not isinstance(artifact, dict):
        diagnostics.append("artifact must be an object")
    else:
        if set(artifact) != _ARTIFACT_KEYS:
            diagnostics.append("artifact has unexpected keys")
        if artifact.get("algorithm") != ALGORITHM:
            diagnostics.append("artifact algorithm is unsupported")
        artifact_digest = artifact.get("digest")
        if not _is_digest(artifact_digest):
            diagnostics.append(
                "artifact digest must be 64 lowercase hexadecimal characters"
            )

    case_map = {
        case.get("id"): case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    }
    rubric_set = set(rubric_items)
    cohorts = evidence.get("cohorts")
    if not isinstance(cohorts, list):
        diagnostics.append("cohorts must be a list")
        cohorts = []

    cohort_ids = set()
    run_ids = set()
    headline_cohorts = []
    headline_case_ids = []
    root_descriptor = _root_descriptor
    owns_root_descriptor = root_descriptor is None
    try:
        if owns_root_descriptor:
            try:
                root_descriptor = _open_root(Path(root))
            except EvidenceError as error:
                diagnostics.append(str(error))

        for cohort in cohorts:
            if not isinstance(cohort, dict):
                diagnostics.append("cohort must be an object")
                continue
            cohort_id = cohort.get("id")
            display_id = cohort_id if _is_safe_id(cohort_id) else "<invalid>"
            if set(cohort) != _COHORT_KEYS:
                diagnostics.append(f"cohort '{display_id}' has unexpected keys")
            if not _is_safe_id(cohort_id):
                diagnostics.append("cohort id is not safe")
            elif cohort_id in cohort_ids:
                diagnostics.append(f"duplicate cohort id: {cohort_id}")
            else:
                cohort_ids.add(cohort_id)
            status = cohort.get("status")
            if status not in ("headline", "historical"):
                diagnostics.append(f"cohort '{display_id}' has invalid status")
            elif status == "headline":
                headline_cohorts.append(cohort)
            cohort_digest = cohort.get("artifact_digest")
            if not _is_digest(cohort_digest):
                diagnostics.append(
                    f"cohort '{display_id}' artifact digest must be 64 lowercase hexadecimal characters"
                )
            if status == "headline" and _is_digest(artifact_digest) and cohort_digest != artifact_digest:
                diagnostics.append(
                    f"cohort '{display_id}' artifact digest does not match frozen artifact"
                )

            runs = cohort.get("runs")
            if not isinstance(runs, list):
                diagnostics.append(f"cohort '{display_id}' runs must be a list")
                continue
            for run in runs:
                if not isinstance(run, dict):
                    diagnostics.append(f"cohort '{display_id}' run must be an object")
                    continue
                run_id = run.get("id")
                display_run = run_id if _is_safe_id(run_id) else "<invalid>"
                is_draft = set(run) == _DRAFT_RUN_KEYS
                if not is_draft and set(run) != _RUN_KEYS:
                    diagnostics.append(f"run '{display_run}' has unexpected keys")
                if not _is_safe_id(run_id):
                    diagnostics.append("run id is not safe")
                elif run_id in run_ids:
                    diagnostics.append(f"duplicate run id: {run_id}")
                else:
                    run_ids.add(run_id)
                case_id = run.get("case_id")
                case_id_is_safe = _is_safe_id(case_id)
                if not case_id_is_safe:
                    diagnostics.append(f"run '{display_run}' has invalid case_id")
                if status == "headline" and case_id_is_safe:
                    headline_case_ids.append(case_id)

                if root_descriptor is not None and "prompt" in run:
                    prompt_text = _append_file_diagnostic(
                        diagnostics,
                        root_descriptor,
                        run.get("prompt"),
                        display_run,
                        "prompt",
                    )
                    declared_case = (
                        case_map.get(case_id)
                        if status == "headline" and case_id_is_safe
                        else None
                    )
                    if (
                        prompt_text is not None
                        and declared_case is not None
                        and prompt_text != declared_case["prompt"] + "\n"
                    ):
                        diagnostics.append(
                            f"run '{display_run}' prompt does not match declared case prompt"
                        )
                if is_draft:
                    diagnostics.append(
                        f"run '{display_run}' is incomplete: missing response, files_read, files_read_kind, rubric"
                    )
                    continue
                if "response" in run and root_descriptor is not None:
                    _append_file_diagnostic(
                        diagnostics,
                        root_descriptor,
                        run["response"],
                        display_run,
                        "response",
                        nonempty=True,
                    )
                if "files_read" in run and root_descriptor is not None:
                    _append_file_diagnostic(
                        diagnostics,
                        root_descriptor,
                        run["files_read"],
                        display_run,
                        "files_read",
                        nonempty=True,
                    )
                if run.get("files_read_kind") not in (
                    "agent-reported",
                    "independently-observed",
                ):
                    diagnostics.append(
                        f"run '{display_run}' has invalid files_read_kind"
                    )
                rubric = run.get("rubric")
                if status == "headline" and (
                    not isinstance(rubric, dict)
                    or set(rubric) != rubric_set
                ):
                    diagnostics.append(
                        f"run '{display_run}' rubric keys do not exactly match declared rubric"
                    )
                elif not isinstance(rubric, dict) or not rubric:
                    diagnostics.append(f"run '{display_run}' rubric is malformed")
                else:
                    for item, score in rubric.items():
                        if not _is_safe_id(item) or type(score) is not bool:
                            if status == "headline" and item in rubric_set:
                                diagnostics.append(
                                    f"run '{display_run}' rubric item '{item}' is not boolean"
                                )
                            else:
                                diagnostics.append(
                                    f"run '{display_run}' rubric is malformed"
                                )
    except BaseException:
        if owns_root_descriptor and root_descriptor is not None:
            os.close(root_descriptor)
        raise

    if len(headline_cohorts) != 1:
        diagnostics.append("evidence must contain exactly one headline cohort")
    headline_id = evidence.get("headline_cohort")
    if not _is_safe_id(headline_id):
        diagnostics.append("headline_cohort is not a safe id")
    elif len(headline_cohorts) == 1 and headline_cohorts[0].get("id") != headline_id:
        diagnostics.append("headline_cohort does not identify the headline cohort")

    declared_case_ids = [case["id"] for case in cases if isinstance(case, dict) and "id" in case]
    for case_id in headline_case_ids:
        if case_id not in case_map:
            diagnostics.append(f"headline cohort has unknown case id: {case_id}")
    for case_id in declared_case_ids:
        count = headline_case_ids.count(case_id)
        if count == 0:
            diagnostics.append(f"headline cohort is missing case id: {case_id}")
        elif count > 1:
            diagnostics.append(f"headline cohort has duplicate case id: {case_id}")

    if isinstance(artifact, dict):
        manifest_path = artifact.get("manifest")
        if _safe_relative(manifest_path) is None:
            diagnostics.append(
                "artifact manifest is not a safe POSIX-relative path"
            )
        elif root_descriptor is not None:
            try:
                manifest_content = _read_anchored(
                    root_descriptor,
                    manifest_path,
                    "artifact manifest",
                )
            except EvidenceError as error:
                diagnostics.append(str(error))
            else:
                try:
                    manifest = _validate_manifest(
                        _decode_json(manifest_content, "artifact manifest")
                    )
                except EvidenceError as error:
                    diagnostics.append(str(error))
                else:
                    if manifest["algorithm"] != artifact.get("algorithm"):
                        diagnostics.append(
                            "artifact manifest algorithm does not match evidence artifact algorithm"
                        )
                    if manifest["digest"] != artifact_digest:
                        diagnostics.append(
                            "artifact manifest digest does not match evidence artifact digest"
                        )
    if owns_root_descriptor and root_descriptor is not None:
        os.close(root_descriptor)
    return diagnostics


def _cohort_generation(cohort, output_key):
    generations = set()
    for run in cohort.get("runs", ()):
        if not isinstance(run, dict):
            raise EvidenceError("existing cohort run is malformed")
        for field in ("prompt", "response", "files_read"):
            if field not in run:
                continue
            relative = _safe_relative(run[field])
            parts = relative.split("/") if relative is not None else ()
            expected_name = {
                "prompt": "prompt.md",
                "response": "response.md",
                "files_read": "files-read.txt",
            }[field]
            if (
                len(parts) != 6
                or parts[0] != ".evidence-data"
                or parts[1] != output_key
                or parts[3] != "runs"
                or parts[4] != run.get("id")
                or parts[5] != expected_name
            ):
                raise EvidenceError("existing cohort has nonlocal managed paths")
            generations.add(parts[2])
    if len(generations) != 1:
        raise EvidenceError("existing cohort must reference exactly one generation")
    return next(iter(generations))


def _validate_owned_existing(root, evidence, output_key):
    if not isinstance(evidence, dict) or set(evidence) != _EVIDENCE_KEYS:
        raise EvidenceError("existing evidence has unexpected keys")
    cohorts = evidence.get("cohorts")
    if not isinstance(cohorts, list) or not cohorts:
        raise EvidenceError("existing evidence cohorts must be a nonempty list")
    root_descriptor = _open_root(root)
    records = []
    try:
        for cohort in cohorts:
            if not isinstance(cohort, dict):
                raise EvidenceError("existing cohort is malformed")
            generation = _cohort_generation(cohort, output_key)
            prefix = f".evidence-data/{output_key}/{generation}"
            marker = _schema.validate_generation_marker(
                _decode_json(
                    _read_anchored(
                        root_descriptor,
                        f"{prefix}/generation.json",
                        "generation marker",
                    ),
                    "generation marker",
                ),
                output_key,
                generation,
            )
            if marker["cohort_id"] != cohort.get("id"):
                raise EvidenceError("generation marker cohort does not match evidence")
            synthetic = {
                "schema_version": 1,
                "artifact": {
                    "algorithm": marker["artifact"]["algorithm"],
                    "digest": marker["artifact"]["digest"],
                    "manifest": f"{prefix}/artifact.json",
                },
                "headline_cohort": cohort.get("id"),
                "cohorts": [{**cohort, "status": "headline"}],
            }
            diagnostics = validate_evidence(
                root,
                synthetic,
                marker["cases"],
                marker["rubric"],
                _root_descriptor=root_descriptor,
            )
            if diagnostics:
                raise EvidenceError(
                    "existing evidence is invalid: " + diagnostics[0]
                )
            if cohort.get("artifact_digest") != marker["artifact"]["digest"]:
                raise EvidenceError("cohort artifact does not match generation marker")
            records.append((cohort, generation, marker))
    finally:
        os.close(root_descriptor)
    headline = [
        record
        for record in records
        if record[0].get("status") == "headline"
    ]
    if len(headline) != 1:
        raise EvidenceError("existing evidence must contain exactly one headline cohort")
    headline_cohort, headline_generation, headline_marker = headline[0]
    if evidence.get("headline_cohort") != headline_cohort.get("id"):
        raise EvidenceError("headline_cohort does not identify the headline cohort")
    expected_manifest = (
        f".evidence-data/{output_key}/{headline_generation}/artifact.json"
    )
    artifact = evidence.get("artifact")
    if (
        not isinstance(artifact, dict)
        or artifact.get("manifest") != expected_manifest
        or artifact.get("algorithm") != headline_marker["artifact"]["algorithm"]
        or artifact.get("digest") != headline_marker["artifact"]["digest"]
    ):
        raise EvidenceError("existing headline artifact is not owned by its generation")
    _schema.validate_structure(
        evidence,
        headline_marker["rubric"],
        allow_drafts=False,
    )
    return cohorts


def _write_all(descriptor, content):
    offset = 0
    while offset < len(content):
        written = os.write(descriptor, content[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written


def _open_absolute_directory_chain(path):
    absolute = Path(os.path.abspath(path))
    descriptor = os.open(os.sep, _directory_flags())
    chain = []
    try:
        for component in absolute.parts[1:]:
            created = False
            try:
                before = os.stat(
                    component,
                    dir_fd=descriptor,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                try:
                    os.mkdir(component, mode=0o700, dir_fd=descriptor)
                    created = True
                except FileExistsError:
                    created = False
                before = os.stat(
                    component,
                    dir_fd=descriptor,
                    follow_symlinks=False,
                )
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise EvidenceError(
                    "output path contains a non-directory or symbolic-link component"
                )
            try:
                child = os.open(
                    component,
                    _directory_flags(),
                    dir_fd=descriptor,
                )
            except BaseException:
                if created:
                    try:
                        os.rmdir(component, dir_fd=descriptor)
                    except OSError:
                        pass
                raise
            opened = os.fstat(child)
            if not stat.S_ISDIR(opened.st_mode) or not _same_file(before, opened):
                os.close(child)
                raise EvidenceError("output directory changed during traversal")
            chain.append((descriptor, component, child, created, opened))
            descriptor = child
        if not chain:
            os.close(descriptor)
        return absolute, chain
    except BaseException:
        for parent_descriptor, component, child, created, identity in reversed(chain):
            os.close(child)
            if created:
                try:
                    _unlink_if_identity(
                        parent_descriptor,
                        component,
                        identity,
                        directory=True,
                    )
                except OSError:
                    pass
        os.close(descriptor if not chain else chain[0][0])
        raise


def _open_child_directory(parent_descriptor, name, *, create=False, mode=0o700):
    created = False
    try:
        before = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        if not create:
            raise
        try:
            os.mkdir(name, mode=mode, dir_fd=parent_descriptor)
            created = True
        except FileExistsError:
            created = False
        before = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise EvidenceError(f"directory is not a regular nonsymlink directory: {name}")
    descriptor = os.open(name, _directory_flags(), dir_fd=parent_descriptor)
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode) or not _same_file(before, opened):
        os.close(descriptor)
        raise EvidenceError(f"directory changed before it could be opened: {name}")
    return descriptor, created, opened


def _verify_directory_chain(chain):
    for parent_descriptor, component, child, _, identity in chain:
        try:
            current = os.stat(
                component,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            opened = os.fstat(child)
        except OSError as error:
            raise EvidenceError("output directory chain changed") from error
        if (
            stat.S_ISLNK(current.st_mode)
            or not stat.S_ISDIR(current.st_mode)
            or not stat.S_ISDIR(opened.st_mode)
            or not _same_file(current, identity)
            or not _same_file(opened, identity)
        ):
            raise EvidenceError("output directory chain changed")


def _verify_directory_entry(parent_descriptor, name, opened):
    try:
        current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except OSError as error:
        raise EvidenceError(f"directory changed during transaction: {name}") from error
    if (
        stat.S_ISLNK(current.st_mode)
        or not stat.S_ISDIR(current.st_mode)
        or not _same_file(current, opened)
    ):
        raise EvidenceError(f"directory changed during transaction: {name}")


def _create_file_at(parent_descriptor, name, content):
    descriptor = os.open(
        name,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
        dir_fd=parent_descriptor,
    )
    try:
        _write_all(descriptor, content)
        os.fsync(descriptor)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise EvidenceError(f"staged file is not regular: {name}")
        return opened
    finally:
        os.close(descriptor)


def _optional_regular_at(parent_descriptor, name, label):
    try:
        metadata = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise EvidenceError(f"{label} is not a regular nonsymlink file")
    return _read_anchored(parent_descriptor, name, label)


def _unlink_if_identity(parent_descriptor, name, expected, *, directory=False):
    try:
        current = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return False
    if not _same_file(current, expected):
        return False
    if directory:
        os.rmdir(name, dir_fd=parent_descriptor)
    else:
        os.unlink(name, dir_fd=parent_descriptor)
    return True


def _restore_entry(
    parent_descriptor,
    stage_descriptor,
    recovery_descriptor,
    destination,
    backup,
    installed_identity,
):
    if installed_identity is not None:
        try:
            _unlink_if_identity(
                parent_descriptor,
                destination,
                installed_identity,
            )
        except OSError:
            pass
    try:
        os.stat(destination, dir_fd=parent_descriptor, follow_symlinks=False)
        destination_exists = True
    except FileNotFoundError:
        destination_exists = False
    if not destination_exists:
        try:
            os.replace(
                backup,
                destination,
                src_dir_fd=stage_descriptor,
                dst_dir_fd=parent_descriptor,
            )
        except FileNotFoundError:
            pass
        except OSError:
            pass
        return None

    try:
        os.stat(backup, dir_fd=stage_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None
    for _ in range(16):
        recovery = f"recovery-{secrets.token_hex(16)}.json"
        try:
            os.stat(
                recovery,
                dir_fd=recovery_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            os.replace(
                backup,
                recovery,
                src_dir_fd=stage_descriptor,
                dst_dir_fd=recovery_descriptor,
            )
            os.fsync(recovery_descriptor)
            return recovery
    raise EvidenceError("cannot allocate collision-resistant recovery output")


def _cleanup_stage(
    parent_descriptor,
    stage_name,
    stage_descriptor,
    stage_identity,
    run_ids,
):
    try:
        runs_descriptor, _, _ = _open_child_directory(stage_descriptor, "runs")
    except (FileNotFoundError, EvidenceError, OSError):
        runs_descriptor = None
    if runs_descriptor is not None:
        try:
            for run_id in run_ids:
                try:
                    run_descriptor, _, _ = _open_child_directory(
                        runs_descriptor,
                        run_id,
                    )
                except (FileNotFoundError, EvidenceError, OSError):
                    continue
                try:
                    try:
                        os.unlink("prompt.md", dir_fd=run_descriptor)
                    except OSError:
                        pass
                finally:
                    os.close(run_descriptor)
                try:
                    os.rmdir(run_id, dir_fd=runs_descriptor)
                except OSError:
                    pass
        finally:
            os.close(runs_descriptor)
        try:
            os.rmdir("runs", dir_fd=stage_descriptor)
        except OSError:
            pass
    for name in (
        "artifact.json",
        "generation.json",
        "evidence.json",
        "artifact.previous",
        "evidence.previous",
    ):
        try:
            os.unlink(name, dir_fd=stage_descriptor)
        except OSError:
            pass
    os.close(stage_descriptor)
    try:
        _unlink_if_identity(
            parent_descriptor,
            stage_name,
            stage_identity,
            directory=True,
        )
    except OSError:
        pass


def _referenced_generations(evidence):
    referenced = set()
    values = []
    artifact = evidence.get("artifact")
    if isinstance(artifact, dict):
        values.append(artifact.get("manifest"))
    for cohort in evidence.get("cohorts", ()):
        if not isinstance(cohort, dict):
            continue
        for run in cohort.get("runs", ()):
            if not isinstance(run, dict):
                continue
            values.extend(run.get(field) for field in ("prompt", "response", "files_read"))
    for value in values:
        relative = _safe_relative(value)
        if relative is None:
            continue
        parts = relative.split("/")
        if len(parts) >= 4 and parts[0] == ".evidence-data":
            referenced.add(parts[2])
    return referenced


def _owned_orphan_run_ids(descriptor, output_key, generation_name):
    marker = _schema.validate_generation_marker(
        _decode_json(
            _read_anchored(
                descriptor,
                "generation.json",
                "orphan generation marker",
            ),
            "orphan generation marker",
        ),
        output_key,
        generation_name,
    )
    manifest = _validate_manifest(
        _decode_json(
            _read_anchored(
                descriptor,
                "artifact.json",
                "orphan generation artifact",
            ),
            "orphan generation artifact",
        )
    )
    if (
        manifest["algorithm"] != marker["artifact"]["algorithm"]
        or manifest["digest"] != marker["artifact"]["digest"]
    ):
        raise EvidenceError("orphan generation artifact does not match marker")
    orphan = _decode_json(
        _read_anchored(
            descriptor,
            "evidence.json",
            "orphan generation evidence",
        ),
        "orphan generation evidence",
    )
    cohorts = _schema.validate_structure(
        orphan,
        marker["rubric"],
        allow_drafts=True,
    )
    if orphan["headline_cohort"] != marker["cohort_id"]:
        raise EvidenceError("orphan generation headline does not match marker")
    headline = next(cohort for cohort in cohorts if cohort["status"] == "headline")
    if any(
        set(run) != _DRAFT_RUN_KEYS
        for run in headline["runs"]
    ) or _cohort_generation(headline, output_key) != generation_name:
        raise EvidenceError("orphan generation contains nonlocal managed runs")
    allowed = {
        "artifact.json",
        "evidence.json",
        "evidence.previous",
        "generation.json",
        "runs",
    }
    if set(os.listdir(descriptor)) - allowed:
        raise EvidenceError("orphan generation contains unknown entries")
    runs_descriptor, _, _ = _open_child_directory(descriptor, "runs")
    try:
        expected = {run["id"] for run in headline["runs"]}
        if set(os.listdir(runs_descriptor)) != expected:
            raise EvidenceError("orphan generation run entries are malformed")
        for run_id in expected:
            run_descriptor, _, _ = _open_child_directory(runs_descriptor, run_id)
            try:
                if os.listdir(run_descriptor) != ["prompt.md"]:
                    raise EvidenceError("orphan generation run contains unknown entries")
                _read_anchored(
                    run_descriptor,
                    "prompt.md",
                    "orphan generation prompt",
                )
            finally:
                os.close(run_descriptor)
    finally:
        os.close(runs_descriptor)
    return list(expected)


def _remove_unreferenced_generations(data_descriptor, evidence, output_key):
    referenced = _referenced_generations(evidence) if evidence is not None else set()
    try:
        names = os.listdir(data_descriptor)
    except (OSError, NotImplementedError, TypeError) as error:
        raise EvidenceError("cannot inspect immutable evidence generations") from error
    for name in names:
        if name in referenced or _GENERATION_NAME.fullmatch(name) is None:
            continue
        descriptor = None
        try:
            descriptor, _, identity = _open_child_directory(data_descriptor, name)
            run_ids = _owned_orphan_run_ids(
                descriptor,
                output_key,
                name,
            )
        except (EvidenceError, OSError, NotImplementedError, TypeError):
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            continue
        _cleanup_stage(
            data_descriptor,
            name,
            descriptor,
            identity,
            run_ids,
        )
    os.fsync(data_descriptor)


def _close_directory_chain(chain):
    identity_error = None
    try:
        _verify_directory_chain(chain)
    except EvidenceError as error:
        identity_error = error
    for parent_descriptor, component, child, created, identity in reversed(chain):
        os.close(child)
        if created:
            try:
                _unlink_if_identity(
                    parent_descriptor,
                    component,
                    identity,
                    directory=True,
                )
            except OSError:
                pass
    if chain:
        os.close(chain[0][0])
    if identity_error is not None:
        raise identity_error


def initialize_evidence(
    artifact_manifest,
    cases_path,
    rubric_path,
    output,
    cohort_id,
):
    manifest = _validate_manifest(_load_json(artifact_manifest, "artifact manifest"))
    cases = _validate_cases(_load_json(cases_path, "cases"))
    rubric_items = _validate_rubric(_load_json(rubric_path, "rubric"))
    if not _is_safe_id(cohort_id):
        raise EvidenceError("cohort id is not safe")
    output = Path(output)
    if not output.name or output.name in (".", ".."):
        raise EvidenceError("output must end in a simple filename")

    chain = []
    standalone_parent_descriptor = None
    stage_descriptor = None
    evidence_installed = None
    evidence_temporary_identity = None
    evidence_temporary_name = None
    data_descriptor = None
    namespace_descriptor = None
    generation_installed = False
    runs = []
    committed = False
    process_lock = None
    lock_descriptor = None
    lock_identity = None
    parent_process_lock = None
    parent_lock_identity = None
    try:
        _, chain = _open_absolute_directory_chain(output.parent)
        if chain:
            parent_descriptor = chain[-1][2]
        else:
            standalone_parent_descriptor = os.open(os.sep, _directory_flags())
            parent_descriptor = standalone_parent_descriptor
        _verify_directory_chain(chain)
        parent_process_lock, parent_lock_identity = _acquire_parent_evidence_lock(
            parent_descriptor
        )
        output_key = hashlib.sha256(output.name.encode("utf-8")).hexdigest()
        data_descriptor, data_created, data_identity = _open_child_directory(
            parent_descriptor,
            ".evidence-data",
            create=True,
        )
        if data_created:
            os.fsync(parent_descriptor)
        namespace_descriptor, namespace_created, namespace_identity = _open_child_directory(
            data_descriptor,
            output_key,
            create=True,
        )
        if namespace_created:
            os.fsync(data_descriptor)
        if stat.S_IMODE(namespace_identity.st_mode) & 0o077:
            raise EvidenceError("evidence output namespace is not private")
        process_lock, lock_descriptor, lock_identity = _acquire_evidence_lock(
            namespace_descriptor,
            output_key,
        )
        _verify_evidence_lock(namespace_descriptor, lock_descriptor, lock_identity)
        existing_content = _optional_regular_at(
            parent_descriptor,
            output.name,
            "existing evidence",
        )
        existing_cohorts = []
        existing = None
        if existing_content is not None:
            existing = _decode_json(existing_content, "existing evidence")
            raw_cohorts = existing.get("cohorts") if isinstance(existing, dict) else None
            if not isinstance(raw_cohorts, list):
                raise EvidenceError("existing evidence cohorts must be a list")
            seen_cohorts = set()
            for raw_cohort in raw_cohorts:
                raw_id = raw_cohort.get("id") if isinstance(raw_cohort, dict) else None
                if not _is_safe_id(raw_id):
                    raise EvidenceError("existing cohort id is not safe")
                if raw_id in seen_cohorts:
                    raise EvidenceError(f"duplicate cohort id: {raw_id}")
                seen_cohorts.add(raw_id)
            if cohort_id in seen_cohorts:
                raise EvidenceError(f"cohort already exists: {cohort_id}")
            existing_cohorts = _validate_owned_existing(
                Path(output).parent,
                existing,
                output_key,
            )
            existing_cohorts = [
                {**cohort, "status": "historical"}
                for cohort in existing_cohorts
            ]
        _verify_directory_entry(
            parent_descriptor,
            ".evidence-data",
            data_identity,
        )
        _verify_directory_entry(data_descriptor, output_key, namespace_identity)
        _verify_evidence_lock(namespace_descriptor, lock_descriptor, lock_identity)
        _remove_unreferenced_generations(namespace_descriptor, existing, output_key)

        generation_name = f"{cohort_id}-{secrets.token_hex(16)}"
        generation_prefix = f".evidence-data/{output_key}/{generation_name}"
        runs = []
        for case in cases:
            run_id = f"{cohort_id}-{case['id']}"
            if not _is_safe_id(run_id):
                raise EvidenceError(f"generated run id is not safe: {run_id}")
            runs.append(
                {
                    "id": run_id,
                    "case_id": case["id"],
                    "prompt": f"{generation_prefix}/runs/{run_id}/prompt.md",
                }
            )
        evidence = {
            "schema_version": 1,
            "artifact": {
                "algorithm": ALGORITHM,
                "digest": manifest["digest"],
                "manifest": f"{generation_prefix}/artifact.json",
            },
            "headline_cohort": cohort_id,
            "cohorts": existing_cohorts
            + [
                {
                    "id": cohort_id,
                    "status": "headline",
                    "artifact_digest": manifest["digest"],
                    "runs": runs,
                }
            ],
        }

        for _ in range(16):
            stage_name = f".{output.name}.{secrets.token_hex(16)}.stage"
            try:
                os.mkdir(stage_name, mode=0o700, dir_fd=namespace_descriptor)
            except FileExistsError:
                continue
            break
        else:
            raise EvidenceError("cannot allocate initialization staging directory")
        stage_descriptor, _, stage_identity = _open_child_directory(
            namespace_descriptor,
            stage_name,
        )
        if stat.S_IMODE(stage_identity.st_mode) & 0o077:
            raise EvidenceError("initialization staging directory is not private")
        stage_runs_descriptor, _, _ = _open_child_directory(
            stage_descriptor,
            "runs",
            create=True,
        )
        try:
            for case, run in zip(cases, runs):
                run_descriptor, _, _ = _open_child_directory(
                    stage_runs_descriptor,
                    run["id"],
                    create=True,
                )
                try:
                    _create_file_at(
                        run_descriptor,
                        "prompt.md",
                        (case["prompt"] + "\n").encode("utf-8"),
                    )
                    os.fsync(run_descriptor)
                finally:
                    os.close(run_descriptor)
            os.fsync(stage_runs_descriptor)
        finally:
            os.close(stage_runs_descriptor)
        _create_file_at(
            stage_descriptor,
            "artifact.json",
            (json.dumps(manifest, sort_keys=True) + "\n").encode("utf-8"),
        )
        _create_file_at(
            stage_descriptor,
            "evidence.json",
            (json.dumps(evidence, sort_keys=True) + "\n").encode("utf-8"),
        )
        marker = _schema.make_generation_marker(
            output_key,
            generation_name,
            cohort_id,
            cases,
            rubric_items,
            manifest,
        )
        _create_file_at(
            stage_descriptor,
            "generation.json",
            (json.dumps(marker, sort_keys=True) + "\n").encode("utf-8"),
        )
        if existing_content is not None:
            _create_file_at(
                stage_descriptor,
                "evidence.previous",
                existing_content,
            )
            existing_identity = os.stat(
                output.name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            os.chmod(
                "evidence.previous",
                stat.S_IMODE(existing_identity.st_mode),
                dir_fd=stage_descriptor,
                follow_symlinks=False,
            )
            prior_identity = os.stat(
                "evidence.previous",
                dir_fd=stage_descriptor,
                follow_symlinks=False,
            )
            if not stat.S_ISREG(prior_identity.st_mode):
                raise EvidenceError("prior evidence backup changed during staging")
        os.fsync(stage_descriptor)

        _verify_directory_entry(
            parent_descriptor,
            ".evidence-data",
            data_identity,
        )
        _verify_directory_entry(data_descriptor, output_key, namespace_identity)
        _verify_evidence_lock(namespace_descriptor, lock_descriptor, lock_identity)
        _verify_directory_chain(chain)
        os.replace(
            stage_name,
            generation_name,
            src_dir_fd=namespace_descriptor,
            dst_dir_fd=namespace_descriptor,
        )
        generation_installed = True
        os.fsync(namespace_descriptor)
        _verify_directory_entry(
            parent_descriptor,
            ".evidence-data",
            data_identity,
        )
        _verify_directory_entry(
            namespace_descriptor,
            generation_name,
            stage_identity,
        )

        for _ in range(16):
            candidate = f".{output.name}.{secrets.token_hex(16)}.commit"
            try:
                evidence_temporary_identity = _create_file_at(
                    namespace_descriptor,
                    candidate,
                    (json.dumps(evidence, sort_keys=True) + "\n").encode("utf-8"),
                )
            except FileExistsError:
                continue
            evidence_temporary_name = candidate
            break
        if evidence_temporary_name is None:
            raise EvidenceError("cannot allocate evidence commit file")
        os.fsync(namespace_descriptor)
        _verify_directory_chain(chain)
        _verify_directory_entry(
            parent_descriptor,
            ".evidence-data",
            data_identity,
        )
        _verify_directory_entry(data_descriptor, output_key, namespace_identity)
        _verify_evidence_lock(namespace_descriptor, lock_descriptor, lock_identity)
        os.fsync(data_descriptor)
        os.replace(
            evidence_temporary_name,
            output.name,
            src_dir_fd=namespace_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        evidence_temporary_name = None
        evidence_installed = os.stat(
            output.name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if not _same_file(evidence_installed, evidence_temporary_identity):
            evidence_installed = evidence_temporary_identity
            raise EvidenceError("installed evidence changed during transaction")
        _verify_directory_entry(
            namespace_descriptor,
            generation_name,
            stage_identity,
        )
        os.fsync(parent_descriptor)
        _verify_directory_chain(chain)
        _verify_evidence_lock(namespace_descriptor, lock_descriptor, lock_identity)
        committed = True
        return evidence
    except EvidenceError:
        raise
    except (OSError, NotImplementedError, TypeError) as error:
        reason = (
            "descriptor-relative filesystem operations are unavailable"
            if isinstance(error, TypeError)
            else getattr(error, "strerror", None) or "operating system error"
        )
        raise EvidenceError(f"cannot initialize evidence: {reason}") from error
    finally:
        primary_error = sys.exception()
        cleanup_failures = []
        recovery_names = []

        def attempt_cleanup(label, operation):
            try:
                return operation()
            except Exception:
                cleanup_failures.append(label)
                return None

        if chain or standalone_parent_descriptor is not None:
            parent_descriptor = (
                chain[-1][2] if chain else standalone_parent_descriptor
            )
            attempt_cleanup(
                "output directory verification",
                lambda: _verify_directory_chain(chain),
            )
            if (
                namespace_descriptor is not None
                and lock_descriptor is not None
                and lock_identity is not None
            ):
                attempt_cleanup(
                    "namespace lock verification",
                    lambda: _verify_evidence_lock(
                        namespace_descriptor,
                        lock_descriptor,
                        lock_identity,
                    ),
                )
            if evidence_temporary_name is not None:
                attempt_cleanup(
                    "temporary pointer removal",
                    lambda: _unlink_if_identity(
                        namespace_descriptor,
                        evidence_temporary_name,
                        evidence_temporary_identity,
                    ),
                )
            if not committed and generation_installed and stage_descriptor is not None:
                def restore_prior_pointer():
                    recovery = _restore_entry(
                        parent_descriptor,
                        stage_descriptor,
                        namespace_descriptor,
                        output.name,
                        "evidence.previous",
                        evidence_installed,
                    )
                    if recovery is not None:
                        recovery_names.append(recovery)

                attempt_cleanup("prior pointer recovery", restore_prior_pointer)
                attempt_cleanup(
                    "post-recovery directory verification",
                    lambda: _verify_directory_chain(chain),
                )
            if stage_descriptor is not None:
                attempt_cleanup(
                    "pre-stage-cleanup directory verification",
                    lambda: _verify_directory_chain(chain),
                )
                if committed:
                    attempt_cleanup(
                        "generation descriptor close",
                        lambda: os.close(stage_descriptor),
                    )
                else:
                    attempt_cleanup(
                        "staged generation cleanup",
                        lambda: _cleanup_stage(
                            namespace_descriptor,
                            generation_name if generation_installed else stage_name,
                            stage_descriptor,
                            stage_identity,
                            [run["id"] for run in runs],
                        ),
                    )
            if process_lock is not None and lock_descriptor is not None:
                attempt_cleanup(
                    "namespace lock release",
                    lambda: _release_evidence_lock(
                        process_lock,
                        lock_descriptor,
                    ),
                )
                process_lock = None
                lock_descriptor = None
            if parent_process_lock is not None:
                attempt_cleanup(
                    "parent lock release",
                    lambda: _release_parent_evidence_lock(
                        parent_process_lock,
                        parent_descriptor,
                    ),
                )
                parent_process_lock = None
            if namespace_descriptor is not None:
                attempt_cleanup(
                    "namespace descriptor close",
                    lambda: os.close(namespace_descriptor),
                )
            if data_descriptor is not None:
                attempt_cleanup(
                    "data descriptor close",
                    lambda: os.close(data_descriptor),
                )
            if chain:
                attempt_cleanup(
                    "output directory chain close",
                    lambda: _close_directory_chain(chain),
                )
            elif standalone_parent_descriptor is not None:
                attempt_cleanup(
                    "output parent descriptor close",
                    lambda: os.close(standalone_parent_descriptor),
                )

        cleanup_diagnostics = list(cleanup_failures)
        if recovery_names:
            cleanup_diagnostics.append(
                "prior evidence preserved as " + ", ".join(recovery_names)
            )
        if primary_error is not None:
            if cleanup_diagnostics and hasattr(primary_error, "add_note"):
                primary_error.add_note(
                    "evidence cleanup failed: " + "; ".join(cleanup_diagnostics)
                )
        elif cleanup_diagnostics:
            if committed:
                raise EvidenceError(
                    "evidence transaction committed but cleanup failed"
                )
            raise EvidenceError("evidence cleanup failed")
