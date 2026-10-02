#!/usr/bin/env python3

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


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

IMPORTER_TERMS = (
    "import",
    "fetch",
    "download",
    "cache",
    "crawl",
    "scrape",
    "sync",
)
PROVIDER_MANIFESTS = {
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
}
MARKETPLACE_MANIFESTS = {
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
}


class ClassificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Classification:
    profile: str
    categories: tuple[str, ...]
    paths: tuple[str, ...]
    reasons: tuple[str, ...]


def _has_unsafe_unicode(value: str) -> bool:
    return any(
        unicodedata.category(character) in {"Cc", "Cf", "Cs", "Zl", "Zp"}
        for character in value
    )


def _normalized_path(value: str, *, label: str = "changed path") -> str:
    if not isinstance(value, str):
        raise ClassificationError(f"{label} must be text")
    if (
        not value
        or value == "."
        or value.startswith("/")
        or "\\" in value
        or _has_unsafe_unicode(value)
    ):
        raise ClassificationError(f"{label} is not a safe repository-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ClassificationError(f"{label} is not a safe repository-relative path")
    normalized = path.as_posix()
    if normalized != value:
        raise ClassificationError(f"{label} is not normalized")
    return normalized


def _is_beneath(path: str, prefix: str) -> bool:
    if prefix == ".":
        return True
    return path == prefix or path.startswith(f"{prefix}/")


def _relative_to_target(path: str, target_prefix: str) -> str | None:
    if not _is_beneath(path, target_prefix):
        return None
    if target_prefix == ".":
        return path
    if path == target_prefix:
        return ""
    return path[len(target_prefix) + 1 :]


def _script_tokens(basename: str) -> tuple[str, ...]:
    """Return separator- and camel-case-delimited lexical tokens.

    Importer terms match complete tokens, so `import_catalog.py` and
    `importCatalog.py` match while an unrelated word such as `important.py`
    does not.
    """
    stem = PurePosixPath(basename).stem
    separated = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", stem)
    return tuple(re.findall(r"[a-z0-9]+", separated.lower()))


def _is_test_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return "tests" in {part.lower() for part in parts}


def _is_metadata_path(path: str, relative_target: str | None) -> bool:
    lowered = path.lower()
    basename = PurePosixPath(path).name.lower()
    if relative_target == "agents/openai.yaml":
        return True
    manifests = PROVIDER_MANIFESTS | MARKETPLACE_MANIFESTS
    if any(
        lowered == manifest or lowered.endswith(f"/{manifest}")
        for manifest in manifests
    ):
        return True
    return (
        basename == "readme"
        or basename.startswith("readme.")
        or basename == "license"
        or basename.startswith("license.")
    )


def _content_reason(relative_target: str) -> str | None:
    parts = tuple(part.lower() for part in PurePosixPath(relative_target).parts)
    basename = parts[-1] if parts else ""
    if parts and parts[0] == "references":
        return "reference content changed"
    if "examples" in parts:
        return "example content changed"
    normalized_basename = basename.replace("_", "-")
    normalized_parts = tuple(part.replace("_", "-") for part in parts)
    if "attribution" in normalized_basename or "attribution" in normalized_parts:
        return "attribution content changed"
    if "content-policy" in normalized_basename or "content-policy" in normalized_parts:
        return "content policy changed"
    return None


def _category_and_reason(path: str, target_prefix: str) -> tuple[str, str]:
    relative_target = _relative_to_target(path, target_prefix)
    if relative_target == "SKILL.md":
        return "behavior", "skill instructions changed"
    if relative_target is not None:
        content_reason = _content_reason(relative_target)
        if content_reason is not None:
            return "content", content_reason
        relative_parts = PurePosixPath(relative_target).parts
        if relative_parts and relative_parts[0].lower() == "scripts":
            if any(
                token in IMPORTER_TERMS
                for token in _script_tokens(PurePosixPath(path).name)
            ):
                return "importer", "importer script changed"
            return "production", "production script changed"
    if _is_test_path(path):
        return "tests", "test coverage changed"
    if _is_metadata_path(path, relative_target):
        return "metadata", "metadata changed"
    return "unknown", "unrecognized distributable path changed"


def classify_paths(paths: Iterable[str], target_prefix: str) -> Classification:
    normalized_target = (
        "."
        if target_prefix == "."
        else _normalized_path(target_prefix, label="target prefix")
    )
    normalized_paths = tuple(sorted({_normalized_path(path) for path in paths}))
    if not normalized_paths:
        return Classification(
            profile="quick",
            categories=(),
            paths=(),
            reasons=("no distributable changes",),
        )

    classified = [
        _category_and_reason(path, normalized_target) for path in normalized_paths
    ]
    categories = tuple(sorted({category for category, _ in classified}))
    non_test_categories = set(categories) - {"tests"}
    if not non_test_categories or non_test_categories == {"metadata"}:
        profile = "quick"
    elif len(non_test_categories) == 1:
        only_category = next(iter(non_test_categories))
        profile = (
            only_category
            if only_category in {"behavior", "content", "importer"}
            else "full"
        )
    else:
        profile = "full"
    reasons = tuple(
        f"{path}: {reason}"
        for path, (_, reason) in zip(normalized_paths, classified)
    )
    return Classification(profile, categories, normalized_paths, reasons)


def _run_git_z(repository: Path, arguments: list[str]) -> list[bytes]:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repository,
            check=True,
            capture_output=True,
            text=False,
            shell=False,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ClassificationError("Git command failed") from error
    if not result.stdout:
        return []
    if not result.stdout.endswith(b"\0"):
        raise ClassificationError("Git returned an ambiguous path list")
    return result.stdout[:-1].split(b"\0")


def _decode_git_path(value: bytes) -> str:
    try:
        decoded = value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ClassificationError("Git returned a non-UTF-8 path") from error
    return _normalized_path(decoded)


def collect_git_paths(repository: Path, base: str) -> tuple[str, ...]:
    if (
        not isinstance(base, str)
        or not base
        or base.startswith("-")
        or _has_unsafe_unicode(base)
    ):
        raise ClassificationError("base reference is invalid")
    try:
        resolved_repository = repository.resolve(strict=True)
    except (OSError, ValueError) as error:
        raise ClassificationError("repository is unavailable") from error
    if not resolved_repository.is_dir():
        raise ClassificationError("repository is unavailable")

    records: set[str] = set()
    diff_commands = (
        ["diff", "--no-renames", "--name-only", "-z", f"{base}...HEAD"],
        ["diff", "--no-renames", "--name-only", "-z"],
        ["diff", "--no-renames", "--cached", "--name-only", "-z"],
    )
    for command in diff_commands:
        records.update(
            _decode_git_path(value)
            for value in _run_git_z(resolved_repository, command)
        )

    status_values = _run_git_z(
        resolved_repository,
        ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
    )
    index = 0
    while index < len(status_values):
        record = status_values[index]
        if len(record) < 4 or record[2:3] != b" ":
            raise ClassificationError("Git returned ambiguous status data")
        status = record[:2]
        records.add(_decode_git_path(record[3:]))
        index += 1
        if b"R" in status or b"C" in status:
            if index >= len(status_values):
                raise ClassificationError("Git returned ambiguous rename data")
            original_path = _decode_git_path(status_values[index])
            if b"R" in status:
                records.add(original_path)
            index += 1
    return tuple(sorted(records))


def render_json(classification: Classification) -> str:
    return json.dumps(
        {"schema_version": 1, **asdict(classification)},
        indent=2,
        sort_keys=True,
    )


def render_human(classification: Classification) -> str:
    categories = ", ".join(classification.categories) or "none"
    lines = [
        f"Profile: {classification.profile}",
        f"Categories: {categories}",
        "Changed paths:",
    ]
    lines.extend(f"  - {path}" for path in classification.paths)
    lines.append("Reasons:")
    lines.extend(f"  - {reason}" for reason in classification.reasons)
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Classify the validation risk of changed skill paths."
    )
    parser.add_argument("config", type=Path)
    parser.add_argument("--base", default="main")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)

    try:
        config = optimizer_config.load_config(arguments.config)
        target_prefix = config.target_root.relative_to(
            config.repository_root
        ).as_posix()
        classification = classify_paths(
            collect_git_paths(config.repository_root, arguments.base),
            target_prefix,
        )
    except ConfigError:
        print("classify_change: error: invalid configuration", file=sys.stderr)
        return 2
    except (ClassificationError, ValueError):
        print("classify_change: error: Git or classification failure", file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError):
        print("classify_change: unable to inspect repository", file=sys.stderr)
        return 2

    rendered = (
        render_json(classification)
        if arguments.json
        else render_human(classification)
    )
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
