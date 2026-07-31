#!/usr/bin/env python3

import argparse
import fnmatch
import hashlib
import importlib.util
import json
import os
import secrets
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath


def _load_optimizer_config():
    try:
        import optimizer_config

        return optimizer_config
    except ModuleNotFoundError as error:
        if error.name != "optimizer_config":
            raise

    module_name = "skill_optimizer_optimizer_config"
    existing_module = sys.modules.get(module_name)
    if existing_module is not None:
        return existing_module

    module_path = Path(__file__).with_name("optimizer_config.py")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load optimizer configuration")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


optimizer_config = _load_optimizer_config()
ConfigError = optimizer_config.ConfigError

ALGORITHM = "sha256-length-framed-v1"
_GLOB_MAGIC = "*?["


class ArtifactError(ValueError):
    pass


def _normalized_path(value):
    if not isinstance(value, str):
        raise ArtifactError("artifact paths must be UTF-8 strings")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ArtifactError("artifact paths must be valid UTF-8") from error
    if (
        not value
        or "\\" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise ArtifactError("artifact path is empty, ambiguous, or contains control characters")

    parts = value.split("/")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or any(part in ("", ".", "..") for part in parts)
        or path.as_posix() != value
    ):
        raise ArtifactError(f"artifact path is not a safe POSIX-relative path: {value!r}")
    return value


def digest_entries(entries):
    normalized = []
    seen = set()
    for path, content in entries:
        path = _normalized_path(path)
        if path in seen:
            raise ArtifactError(f"duplicate artifact path: {path}")
        if not isinstance(content, bytes):
            raise ArtifactError(f"artifact content must be bytes: {path}")
        seen.add(path)
        normalized.append((path, content))

    digest = hashlib.sha256()
    for path, content in sorted(normalized, key=lambda entry: entry[0]):
        path_bytes = path.encode("utf-8")
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _validate_pattern(pattern, label):
    if not isinstance(pattern, str):
        raise ArtifactError(f"{label} pattern must be a string")
    try:
        pattern.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ArtifactError(f"{label} pattern must be valid UTF-8") from error
    parts = pattern.split("/")
    if (
        not pattern
        or pattern.startswith("/")
        or "\\" in pattern
        or any(part in ("", ".", "..") for part in parts)
        or any(ord(character) < 32 or ord(character) == 127 for character in pattern)
    ):
        raise ArtifactError(f"{label} pattern must be a safe POSIX-relative glob")


def _glob_matches(path, pattern):
    path_parts = PurePosixPath(path).parts
    pattern_parts = PurePosixPath(pattern).parts
    pending = {(0, 0)}
    visited = set()
    while pending:
        path_index, pattern_index = pending.pop()
        state = (path_index, pattern_index)
        if state in visited:
            continue
        visited.add(state)
        if pattern_index == len(pattern_parts):
            if path_index == len(path_parts):
                return True
            continue
        pattern_part = pattern_parts[pattern_index]
        if pattern_part == "**":
            pending.add((path_index, pattern_index + 1))
            if path_index < len(path_parts):
                pending.add((path_index + 1, pattern_index))
        elif (
            path_index < len(path_parts)
            and fnmatch.fnmatchcase(path_parts[path_index], pattern_part)
        ):
            pending.add((path_index + 1, pattern_index + 1))
    return False


def _glob_can_match_descendant(directory, pattern):
    directory_parts = PurePosixPath(directory).parts
    pattern_parts = PurePosixPath(pattern).parts
    states = {0}
    for directory_part in directory_parts:
        next_states = set()
        pending = list(states)
        expanded = set()
        while pending:
            pattern_index = pending.pop()
            if pattern_index in expanded:
                continue
            expanded.add(pattern_index)
            if (
                pattern_index < len(pattern_parts)
                and pattern_parts[pattern_index] == "**"
            ):
                pending.append(pattern_index + 1)
                next_states.add(pattern_index)
            elif (
                pattern_index < len(pattern_parts)
                and fnmatch.fnmatchcase(
                    directory_part,
                    pattern_parts[pattern_index],
                )
            ):
                next_states.add(pattern_index + 1)
        states = next_states
        if not states:
            return False

    for pattern_index in states:
        if pattern_index < len(pattern_parts):
            return True
    return False


def _error_reason(error):
    return getattr(error, "strerror", None) or str(error)


def _directory_open_flags():
    return (
        os.O_RDONLY
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _verified_repository_descriptor(repository_root):
    try:
        before = repository_root.lstat()
        descriptor = os.open(repository_root, _directory_open_flags())
    except (OSError, TypeError) as error:
        raise ArtifactError(
            f"cannot open repository root: {_error_reason(error)}"
        ) from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISDIR(before.st_mode)
            or not stat.S_ISDIR(opened.st_mode)
            or (opened.st_dev, opened.st_ino, opened.st_mode)
            != (before.st_dev, before.st_ino, before.st_mode)
        ):
            raise ArtifactError("repository root changed before traversal")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _verified_target_descriptor(config):
    repository_root = config.repository_root
    target_root = config.target_root
    if not repository_root.is_absolute() or not target_root.is_absolute():
        raise ArtifactError("configured repository and target paths must be absolute")
    try:
        target_relative = target_root.relative_to(repository_root)
    except ValueError as error:
        raise ArtifactError("configured target escapes repository") from error
    if any(part in ("", ".", "..") for part in target_relative.parts):
        raise ArtifactError("configured target is not lexically repository-relative")

    descriptor = _verified_repository_descriptor(repository_root)
    traversed = []
    try:
        for component in target_relative.parts:
            traversed.append(component)
            label = PurePosixPath(*traversed).as_posix()
            try:
                before = os.stat(
                    component,
                    dir_fd=descriptor,
                    follow_symlinks=False,
                )
            except (OSError, TypeError) as error:
                raise ArtifactError(
                    f"cannot inspect target directory '{label}': "
                    f"{_error_reason(error)}"
                ) from error
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise ArtifactError(
                    f"target path component is not a regular directory: {label}"
                )

            child_descriptor = None
            try:
                child_descriptor = os.open(
                    component,
                    _directory_open_flags(),
                    dir_fd=descriptor,
                )
                opened = os.fstat(child_descriptor)
            except (OSError, TypeError) as error:
                if child_descriptor is not None:
                    os.close(child_descriptor)
                raise ArtifactError(
                    f"cannot open target directory '{label}': "
                    f"{_error_reason(error)}"
                ) from error
            if (
                not stat.S_ISDIR(opened.st_mode)
                or (opened.st_dev, opened.st_ino, opened.st_mode)
                != (before.st_dev, before.st_ino, before.st_mode)
            ):
                os.close(child_descriptor)
                raise ArtifactError(
                    f"target directory changed before traversal: {label}"
                )
            os.close(descriptor)
            descriptor = child_descriptor
            child_descriptor = None
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _read_regular_file_at(parent_descriptor, name, relative, before):
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(
            name,
            flags,
            dir_fd=parent_descriptor,
        )
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or (opened.st_dev, opened.st_ino, opened.st_mode)
            != (before.st_dev, before.st_ino, before.st_mode)
        ):
            raise ArtifactError(f"selected file changed before it could be read: {relative}")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
    except (OSError, TypeError) as error:
        raise ArtifactError(
            f"cannot read selected file '{relative}': {_error_reason(error)}"
        ) from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
    identity_before = (
        opened.st_dev,
        opened.st_ino,
        stat.S_IFMT(opened.st_mode),
        opened.st_size,
        opened.st_mtime_ns,
        opened.st_ctime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        stat.S_IFMT(after.st_mode),
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if not stat.S_ISREG(after.st_mode) or identity_after != identity_before:
        raise ArtifactError(f"selected file changed while being read: {relative}")
    return b"".join(chunks)


def _is_excluded(relative, excludes):
    path = PurePosixPath(relative)
    descendant = path / "__artifact_descendant__"
    return any(
        path.match(pattern) or descendant.match(pattern)
        for pattern in excludes
    )


def _walk_selected_paths(target_descriptor, includes, excludes):
    selected = {}

    def walk(directory_descriptor, relative_directory=""):
        scan_descriptor = None
        try:
            scan_descriptor = os.dup(directory_descriptor)
            with os.scandir(scan_descriptor) as scan:
                entries = sorted(scan, key=lambda entry: entry.name)
        except (OSError, TypeError) as error:
            label = relative_directory or "."
            raise ArtifactError(
                f"descriptor-relative directory scanning is unavailable for "
                f"'{label}': {_error_reason(error)}"
            ) from error
        finally:
            if scan_descriptor is not None:
                os.close(scan_descriptor)

        for entry in entries:
            relative = (
                f"{relative_directory}/{entry.name}"
                if relative_directory
                else entry.name
            )
            relative = _normalized_path(relative)
            if _is_excluded(relative, excludes):
                continue
            try:
                metadata = os.stat(
                    entry.name,
                    dir_fd=directory_descriptor,
                    follow_symlinks=False,
                )
            except (OSError, TypeError) as error:
                raise ArtifactError(
                    f"cannot inspect selected path '{relative}': {_error_reason(error)}"
                ) from error
            if stat.S_ISLNK(metadata.st_mode):
                if any(
                    _glob_matches(relative, pattern)
                    or _glob_can_match_descendant(relative, pattern)
                    for pattern in includes
                ):
                    raise ArtifactError(
                        f"selected path traverses a symbolic link: {relative}"
                    )
                continue

            matches = [
                pattern
                for pattern in includes
                if _glob_matches(relative, pattern)
            ]
            if stat.S_ISDIR(metadata.st_mode):
                if any(not any(character in pattern for character in _GLOB_MAGIC) for pattern in matches):
                    raise ArtifactError(
                        f"selected path is not a regular file: {relative}"
                    )
                child_descriptor = None
                try:
                    child_descriptor = os.open(
                        entry.name,
                        _directory_open_flags(),
                        dir_fd=directory_descriptor,
                    )
                    opened = os.fstat(child_descriptor)
                    if (
                        not stat.S_ISDIR(opened.st_mode)
                        or (opened.st_dev, opened.st_ino, opened.st_mode)
                        != (metadata.st_dev, metadata.st_ino, metadata.st_mode)
                    ):
                        raise ArtifactError(
                            f"selected directory changed before traversal: {relative}"
                        )
                    walk(child_descriptor, relative)
                except (OSError, TypeError) as error:
                    raise ArtifactError(
                        f"cannot traverse selected directory '{relative}': "
                        f"{_error_reason(error)}"
                    ) from error
                finally:
                    if child_descriptor is not None:
                        os.close(child_descriptor)
            elif matches:
                if not stat.S_ISREG(metadata.st_mode):
                    raise ArtifactError(
                        f"selected path is not a regular file: {relative}"
                    )
                selected[relative] = _read_regular_file_at(
                    directory_descriptor,
                    entry.name,
                    relative,
                    metadata,
                )

    walk(target_descriptor)
    return selected


def select_entries(config):
    for pattern in (*config.includes, *config.excludes):
        _validate_pattern(pattern, "distributable")
    target_descriptor = _verified_target_descriptor(config)
    try:
        selected = _walk_selected_paths(
            target_descriptor,
            config.includes,
            config.excludes,
        )
    finally:
        os.close(target_descriptor)

    if not selected:
        raise ArtifactError("distributable selection contains no regular files")
    return [
        (relative, selected[relative])
        for relative in sorted(selected)
    ]


def build_manifest(config):
    entries = select_entries(config)
    try:
        target = config.target_root.relative_to(config.repository_root).as_posix()
    except ValueError as error:
        raise ArtifactError("configured target escapes repository") from error
    return {
        "schema_version": 1,
        "algorithm": ALGORITHM,
        "digest": digest_entries(entries),
        "target": target,
        "files": [
            {"path": path, "bytes": len(content)}
            for path, content in entries
        ],
    }


def manifest_json(manifest):
    return json.dumps(manifest, sort_keys=True) + "\n"


def write_manifest_atomic(output_path, manifest):
    destination = Path(output_path)
    destination_name = destination.name
    if (
        not destination_name
        or destination_name in (".", "..")
        or Path(destination_name).name != destination_name
    ):
        raise ArtifactError("output path must end in a simple filename")
    parent = destination.parent
    parent_descriptor = None
    staging_descriptor = None
    file_descriptor = None
    staging_name = None
    source_name = "manifest.tmp"
    source_exists = False
    try:
        before = parent.lstat()
        parent_descriptor = os.open(parent, _directory_open_flags())
        opened = os.fstat(parent_descriptor)
        if (
            not stat.S_ISDIR(before.st_mode)
            or not stat.S_ISDIR(opened.st_mode)
            or (opened.st_dev, opened.st_ino, opened.st_mode)
            != (before.st_dev, before.st_ino, before.st_mode)
        ):
            raise ArtifactError("output parent changed before writing")
        try:
            destination_metadata = os.stat(
                destination_name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            destination_metadata = None
        if (
            destination_metadata is not None
            and stat.S_ISDIR(destination_metadata.st_mode)
        ):
            raise ArtifactError(
                f"output path is a directory: {destination_name}"
            )

        for _ in range(16):
            candidate = (
                f".{destination_name}.{secrets.token_hex(16)}.stage"
            )
            try:
                os.mkdir(
                    candidate,
                    mode=0o700,
                    dir_fd=parent_descriptor,
                )
            except FileExistsError:
                continue
            staging_name = candidate
            break
        if staging_name is None:
            raise ArtifactError("cannot allocate unique output staging directory")

        staging_before = os.stat(
            staging_name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        staging_descriptor = os.open(
            staging_name,
            _directory_open_flags(),
            dir_fd=parent_descriptor,
        )
        staging_opened = os.fstat(staging_descriptor)
        if (
            not stat.S_ISDIR(staging_before.st_mode)
            or not stat.S_ISDIR(staging_opened.st_mode)
            or (staging_opened.st_dev, staging_opened.st_ino, staging_opened.st_mode)
            != (
                staging_before.st_dev,
                staging_before.st_ino,
                staging_before.st_mode,
            )
            or stat.S_IMODE(staging_opened.st_mode) & 0o077
        ):
            raise ArtifactError("output staging directory is not private and stable")

        create_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create_flags |= getattr(os, "O_NOFOLLOW", 0)
        file_descriptor = os.open(
            source_name,
            create_flags,
            0o600,
            dir_fd=staging_descriptor,
        )
        source_exists = True
        source_opened = os.fstat(file_descriptor)
        if not stat.S_ISREG(source_opened.st_mode):
            raise ArtifactError("output temporary file is not regular")

        content = manifest_json(manifest).encode("utf-8")
        offset = 0
        while offset < len(content):
            written = os.write(file_descriptor, content[offset:])
            if written <= 0:
                raise OSError("short write while writing manifest")
            offset += written
        os.fsync(file_descriptor)

        source_metadata = os.stat(
            source_name,
            dir_fd=staging_descriptor,
            follow_symlinks=False,
        )
        source_opened = os.fstat(file_descriptor)
        if (
            not stat.S_ISREG(source_metadata.st_mode)
            or not stat.S_ISREG(source_opened.st_mode)
            or (source_metadata.st_dev, source_metadata.st_ino, source_metadata.st_mode)
            != (source_opened.st_dev, source_opened.st_ino, source_opened.st_mode)
        ):
            raise ArtifactError("output temporary file changed before replacement")

        os.replace(
            source_name,
            destination_name,
            src_dir_fd=staging_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        source_exists = False
        installed = os.stat(
            destination_name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        installed_opened = os.fstat(file_descriptor)
        if (
            not stat.S_ISREG(installed.st_mode)
            or not stat.S_ISREG(installed_opened.st_mode)
            or (installed.st_dev, installed.st_ino, installed.st_mode)
            != (
                installed_opened.st_dev,
                installed_opened.st_ino,
                installed_opened.st_mode,
            )
        ):
            raise ArtifactError("installed output does not match trusted temporary file")
        os.close(file_descriptor)
        file_descriptor = None
        os.fsync(parent_descriptor)
    except ArtifactError:
        raise
    except (OSError, TypeError) as error:
        reason = (
            "descriptor-relative output operations are unavailable"
            if isinstance(error, TypeError)
            else getattr(error, "strerror", None) or "operating system error"
        )
        raise ArtifactError(
            f"cannot write output '{destination_name}': {reason}"
        ) from error
    finally:
        cleanup_error = None
        if source_exists and staging_descriptor is not None:
            try:
                os.unlink(
                    source_name,
                    dir_fd=staging_descriptor,
                )
                source_exists = False
            except FileNotFoundError:
                source_exists = False
            except (OSError, TypeError) as error:
                cleanup_error = error
        if file_descriptor is not None:
            os.close(file_descriptor)
        if staging_descriptor is not None:
            os.close(staging_descriptor)
        if staging_name is not None and parent_descriptor is not None:
            try:
                os.rmdir(
                    staging_name,
                    dir_fd=parent_descriptor,
                )
            except FileNotFoundError:
                pass
            except (OSError, TypeError) as error:
                if cleanup_error is None:
                    cleanup_error = error
        if parent_descriptor is not None:
            os.close(parent_descriptor)
        if cleanup_error is not None:
            raise ArtifactError(
                f"cannot safely clean temporary output for '{destination_name}'"
            ) from cleanup_error


def _human_text(manifest):
    lines = [
        f"target: {manifest['target']}",
        f"algorithm: {manifest['algorithm']}",
        f"digest: {manifest['digest']}",
        "files:",
    ]
    lines.extend(
        f"  {entry['path']} ({entry['bytes']} bytes)"
        for entry in manifest["files"]
    )
    return "\n".join(lines) + "\n"


def _safe_diagnostic(error, config_argument):
    if isinstance(error, ConfigError):
        message = str(error)
        message = message.replace(str(config_argument), Path(config_argument).name)
        try:
            message = message.replace(str(Path(config_argument).resolve()), Path(config_argument).name)
        except (OSError, ValueError):
            pass
        return message
    if isinstance(error, ArtifactError):
        return str(error)
    filename = getattr(error, "filename", None)
    reason = getattr(error, "strerror", None) or str(error)
    return f"{Path(filename).name}: {reason}" if filename else reason


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Hash the frozen distributable files for an optimizer target."
    )
    parser.add_argument("config")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--output")
    arguments = parser.parse_args(argv)
    try:
        config = optimizer_config.load_config(arguments.config)
    except ConfigError as error:
        print(
            f"hash_artifact: {_safe_diagnostic(error, arguments.config)}",
            file=sys.stderr,
        )
        return 2
    except (subprocess.SubprocessError, OSError):
        print(
            "hash_artifact: configuration loading failed",
            file=sys.stderr,
        )
        return 2

    try:
        manifest = build_manifest(config)
        if arguments.output:
            write_manifest_atomic(arguments.output, manifest)
    except (OSError, ArtifactError) as error:
        print(
            f"hash_artifact: {_safe_diagnostic(error, arguments.config)}",
            file=sys.stderr,
        )
        return 2

    sys.stdout.write(manifest_json(manifest) if arguments.as_json else _human_text(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
