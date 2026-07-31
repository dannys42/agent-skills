import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROFILE_NAMES = ("quick", "content", "behavior", "importer", "full")
TIMING_KINDS = {"work", "mandatory_wait"}


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Command:
    identifier: str
    argv: tuple[str, ...]
    cwd: Path
    timeout_seconds: float
    max_output_bytes: int
    network: bool
    timing_kind: str


@dataclass(frozen=True)
class Evaluations:
    cases: Path
    rubric: Path


@dataclass(frozen=True)
class OptimizerConfig:
    path: Path
    repository_root: Path
    target_root: Path
    includes: tuple[str, ...]
    excludes: tuple[str, ...]
    commands: dict[str, Command]
    profiles: dict[str, tuple[str, ...]]
    evaluations: Evaluations


def _reject_duplicate_members(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    members: dict[str, Any] = {}
    for name, value in pairs:
        if name in members:
            raise ConfigError(f"duplicate JSON member: {name}")
        members[name] = value
    return members


def _object(
    value: Any,
    label: str,
    required_keys: set[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be an object")
    if required_keys is not None and set(value) != required_keys:
        expected = ", ".join(sorted(required_keys))
        raise ConfigError(f"{label} keys must be exactly: {expected}")
    return value


def _contained_path(
    repository_root: Path,
    value: Any,
    label: str,
    *,
    strict: bool,
) -> Path:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{label} must be a non-empty repository-relative path")

    try:
        relative_path = Path(value)
    except (OSError, ValueError) as error:
        raise ConfigError(f"{label} cannot be resolved: {value}: {error}") from error
    if relative_path.is_absolute():
        raise ConfigError(f"{label} must be a repository-relative path")
    if ".." in relative_path.parts:
        raise ConfigError(f"{label} escapes repository: {value}")

    try:
        resolved = (repository_root / relative_path).resolve(strict=strict)
    except FileNotFoundError:
        raise ConfigError(f"{label} does not exist: {value}") from None
    except (OSError, ValueError) as error:
        raise ConfigError(f"{label} cannot be resolved: {value}: {error}") from error

    try:
        resolved.relative_to(repository_root)
    except ValueError:
        raise ConfigError(f"{label} escapes repository: {value}") from None
    return resolved


def discover_repository_root(config_parent: Path) -> Path:
    try:
        resolved_parent = config_parent.resolve(strict=True)
    except (OSError, ValueError) as error:
        reason = getattr(error, "strerror", None) or str(error)
        raise ConfigError(
            f"cannot resolve configuration parent '{config_parent}': {reason}"
        ) from error
    environment = os.environ.copy()
    environment.update({"LC_ALL": "C", "LANG": "C"})
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(resolved_parent),
                "rev-parse",
                "--show-toplevel",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
    except subprocess.CalledProcessError as error:
        if "not a git repository" in (error.stderr or "").lower():
            return resolved_parent
        raise
    root_value = result.stdout.strip()
    if not root_value:
        raise ConfigError("Git repository root is empty")
    repository_root = Path(root_value)
    if not repository_root.is_absolute():
        raise ConfigError(f"Git repository root must be absolute: {root_value}")
    try:
        return repository_root.resolve(strict=True)
    except (OSError, ValueError) as error:
        reason = getattr(error, "strerror", None) or str(error)
        raise ConfigError(
            f"cannot resolve Git repository root '{repository_root}': {reason}"
        ) from error


def _string_array(value: Any, label: str, *, allow_empty: bool) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or any(not isinstance(item, str) or not item for item in value)
    ):
        qualifier = "an array" if allow_empty else "a non-empty array"
        raise ConfigError(f"{label} must be {qualifier} of strings")
    return tuple(value)


def load_config(path: Path | str) -> OptimizerConfig:
    requested_path = Path(path)
    try:
        config_path = requested_path.resolve()
        config_text = config_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ConfigError(
            f"cannot read configuration '{requested_path}': invalid UTF-8"
        ) from error
    except (OSError, ValueError) as error:
        reason = getattr(error, "strerror", None) or str(error)
        raise ConfigError(
            f"cannot read configuration '{requested_path}': {reason}"
        ) from error

    try:
        raw_config = json.loads(
            config_text,
            object_pairs_hook=_reject_duplicate_members,
        )
    except json.JSONDecodeError as error:
        raise ConfigError(f"invalid JSON in {config_path}: {error.msg}") from None

    config = _object(
        raw_config,
        "configuration",
        {
            "schema_version",
            "target",
            "distributable",
            "commands",
            "profiles",
            "evaluations",
        },
    )
    if (
        not isinstance(config["schema_version"], int)
        or isinstance(config["schema_version"], bool)
        or config["schema_version"] != 1
    ):
        raise ConfigError("schema_version must be 1")

    repository_root = discover_repository_root(config_path.parent)
    target_root = _contained_path(
        repository_root,
        config["target"],
        "target",
        strict=True,
    )
    if not target_root.is_dir():
        raise ConfigError(f"target must be a directory: {config['target']}")

    distributable = _object(
        config["distributable"],
        "distributable",
        {"include", "exclude"},
    )
    for collection_name in ("include", "exclude"):
        collection = distributable[collection_name]
        if (
            not isinstance(collection, list)
            or any(
                not isinstance(pattern, str) or not pattern
                for pattern in collection
            )
        ):
            raise ConfigError(
                f"distributable {collection_name} must contain non-empty strings"
            )
    includes = tuple(distributable["include"])
    excludes = tuple(distributable["exclude"])

    command_values = _object(config["commands"], "commands")
    commands: dict[str, Command] = {}
    for identifier, raw_command in command_values.items():
        if not isinstance(identifier, str) or not identifier:
            raise ConfigError("command identifiers must be non-empty strings")
        label = f"command '{identifier}'"
        command = _object(
            raw_command,
            label,
            {
                "argv",
                "cwd",
                "timeout_seconds",
                "max_output_bytes",
                "network",
                "timing_kind",
            },
        )
        argv = _string_array(
            command["argv"],
            f"{label} argv",
            allow_empty=False,
        )

        timeout_seconds = command["timeout_seconds"]
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not 1 <= timeout_seconds <= 3600
        ):
            raise ConfigError(
                f"{label} timeout_seconds must be a number from 1 to 3600"
            )

        max_output_bytes = command["max_output_bytes"]
        if (
            isinstance(max_output_bytes, bool)
            or not isinstance(max_output_bytes, int)
            or not 1 <= max_output_bytes <= 16_777_216
        ):
            raise ConfigError(
                f"{label} max_output_bytes must be an integer from 1 to 16777216"
            )

        network = command["network"]
        if not isinstance(network, bool):
            raise ConfigError(f"{label} network must be a boolean")

        timing_kind = command["timing_kind"]
        if not isinstance(timing_kind, str) or timing_kind not in TIMING_KINDS:
            raise ConfigError(
                f"{label} timing_kind must be work or mandatory_wait"
            )

        cwd = _contained_path(
            repository_root,
            command["cwd"],
            f"{label} cwd",
            strict=True,
        )
        if not cwd.is_dir():
            raise ConfigError(f"{label} cwd must be a directory: {command['cwd']}")

        commands[identifier] = Command(
            identifier=identifier,
            argv=argv,
            cwd=cwd,
            timeout_seconds=float(timeout_seconds),
            max_output_bytes=max_output_bytes,
            network=network,
            timing_kind=timing_kind,
        )

    profile_values = _object(config["profiles"], "profiles")
    if set(profile_values) != set(PROFILE_NAMES):
        expected = ", ".join(PROFILE_NAMES)
        raise ConfigError(f"profiles must contain exactly: {expected}")
    profiles: dict[str, tuple[str, ...]] = {}
    for profile_name in PROFILE_NAMES:
        command_ids = _string_array(
            profile_values[profile_name],
            f"profile '{profile_name}'",
            allow_empty=True,
        )
        for command_id in command_ids:
            if command_id not in commands:
                raise ConfigError(
                    f"profile '{profile_name}' references unknown command: {command_id}"
                )
        profiles[profile_name] = command_ids

    evaluation_values = _object(
        config["evaluations"],
        "evaluations",
        {"cases", "rubric"},
    )
    evaluations = Evaluations(
        cases=_contained_path(
            repository_root,
            evaluation_values["cases"],
            "evaluations cases",
            strict=False,
        ),
        rubric=_contained_path(
            repository_root,
            evaluation_values["rubric"],
            "evaluations rubric",
            strict=False,
        ),
    )

    return OptimizerConfig(
        path=config_path,
        repository_root=repository_root,
        target_root=target_root,
        includes=includes,
        excludes=excludes,
        commands=commands,
        profiles=profiles,
        evaluations=evaluations,
    )
