#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


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
        raise RuntimeError(f"cannot load optimizer configuration: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


optimizer_config = _load_optimizer_config()
ConfigError = optimizer_config.ConfigError
OptimizerConfig = optimizer_config.OptimizerConfig

PLUGIN_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
)
MARKETPLACE_ADAPTERS = (
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
)


class InspectionError(RuntimeError):
    pass


_QUOTED_VALUE = re.compile(r"'([^']*)'")
_WINDOWS_DRIVE_ROOT = re.compile(r"^[A-Za-z]:[\\/]")
_UNQUOTED_CONTEXT_PATH = re.compile(
    r"(?P<prefix>\bin )"
    r"(?P<path>(?:/[^\r\n]*?|[A-Za-z]:[\\/][^\r\n]*?|[\\]+[^\r\n]*?))"
    r"(?=: )"
)


def _sanitize_diagnostic(message: object) -> str:
    """Redact absolute paths while preserving deterministic error context."""

    def redact(match: re.Match[str]) -> str:
        value = match.group(1)
        is_absolute = (
            value.startswith("/")
            or value.startswith("\\")
            or _WINDOWS_DRIVE_ROOT.match(value) is not None
        )
        return "'<absolute-path>'" if is_absolute else match.group(0)

    sanitized = _QUOTED_VALUE.sub(redact, str(message))
    return _UNQUOTED_CONTEXT_PATH.sub(
        lambda match: f"{match.group('prefix')}<absolute-path>",
        sanitized,
    )


def _is_regular_file(path: Path) -> bool:
    return not path.is_symlink() and path.is_file()


def _count_regular_files(root: Path, repository_root: Path) -> int:
    try:
        root.relative_to(repository_root)
    except ValueError:
        raise InspectionError(
            "cannot traverse path outside repository"
        ) from None
    if root.is_symlink() or not root.is_dir():
        return 0
    try:
        root.resolve().relative_to(repository_root.resolve())
    except (OSError, ValueError):
        raise InspectionError(
            "cannot traverse path outside repository"
        ) from None

    def raise_traversal_error(error: OSError) -> None:
        reason = error.strerror or type(error).__name__
        relative_root = _repository_relative(root, repository_root)
        raise InspectionError(
            f"cannot traverse {relative_root}: {reason}"
        ) from error

    count = 0
    for directory, directory_names, file_names in os.walk(
        root,
        followlinks=False,
        onerror=raise_traversal_error,
    ):
        directory_path = Path(directory)
        directory_names[:] = [
            name
            for name in directory_names
            if not (directory_path / name).is_symlink()
        ]
        count += sum(
            _is_regular_file(directory_path / name) for name in file_names
        )
    return count


def _discover_plugin_root(config: OptimizerConfig) -> Path | None:
    candidate = config.target_root
    while True:
        if any(
            _is_regular_file(candidate / manifest)
            for manifest in PLUGIN_MANIFESTS
        ):
            return candidate
        if candidate == config.repository_root:
            return None
        candidate = candidate.parent


def _inspection_skill_root(
    target_root: Path,
    plugin_root: Path | None,
) -> Path:
    if _is_regular_file(target_root / "SKILL.md"):
        return target_root
    if plugin_root != target_root:
        return target_root

    skills_root = target_root / "skills"
    if skills_root.is_symlink() or not skills_root.is_dir():
        return target_root
    try:
        nested_skills = sorted(
            candidate
            for candidate in skills_root.iterdir()
            if not candidate.is_symlink()
            and candidate.is_dir()
            and _is_regular_file(candidate / "SKILL.md")
        )
    except OSError as error:
        reason = error.strerror or type(error).__name__
        raise InspectionError(f"cannot inspect nested skills: {reason}") from error
    if len(nested_skills) == 1:
        return nested_skills[0]
    return target_root


def _repository_relative(path: Path, repository_root: Path) -> str:
    return path.relative_to(repository_root).as_posix()


def _plugin_name(plugin_root: Path, repository_root: Path) -> str:
    names = set()
    for manifest in PLUGIN_MANIFESTS:
        manifest_path = plugin_root / manifest
        if not _is_regular_file(manifest_path):
            continue
        try:
            document = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(document, dict):
            continue
        name = document.get("name")
        if isinstance(name, str) and name and name == name.strip():
            names.add(name)

    plugin_path = _repository_relative(plugin_root, repository_root)
    if not names:
        raise InspectionError(
            f"cannot determine plugin name from manifests in {plugin_path}"
        )
    if len(names) > 1:
        raise InspectionError(f"conflicting plugin names in {plugin_path}")
    return names.pop()


def _source_references_path(source: Any, plugin_path: str) -> bool:
    if isinstance(source, str):
        source_path = source
    elif isinstance(source, dict) and isinstance(source.get("path"), str):
        source_path = source["path"]
    else:
        return False
    if plugin_path == "." and source_path in (".", "./"):
        return True
    return source_path.removeprefix("./") == plugin_path


def _adapter_references_plugin(
    adapter: Path,
    plugin_name: str,
    plugin_path: str,
) -> bool:
    if not _is_regular_file(adapter):
        return False
    try:
        document = json.loads(adapter.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    if not isinstance(document, dict):
        return False
    plugins = document.get("plugins")
    if not isinstance(plugins, list):
        return False
    return any(
        isinstance(entry, dict)
        and entry.get("name") == plugin_name
        and _source_references_path(entry.get("source"), plugin_path)
        for entry in plugins
    )


def inspect(config: OptimizerConfig) -> dict[str, object]:
    repository_root = config.repository_root
    target_root = config.target_root
    plugin_root = _discover_plugin_root(config)
    skill_root = _inspection_skill_root(target_root, plugin_root)

    plugin_manifests = []
    if plugin_root is not None:
        plugin_manifests = sorted(
            _repository_relative(plugin_root / manifest, repository_root)
            for manifest in PLUGIN_MANIFESTS
            if _is_regular_file(plugin_root / manifest)
        )

    marketplace_adapters = []
    if plugin_root is not None:
        plugin_path = _repository_relative(plugin_root, repository_root)
        plugin_name = _plugin_name(plugin_root, repository_root)
        marketplace_adapters = sorted(
            adapter
            for adapter in MARKETPLACE_ADAPTERS
            if _adapter_references_plugin(
                repository_root / adapter,
                plugin_name,
                plugin_path,
            )
        )

    if plugin_root is not None:
        tests_root = plugin_root / "tests"
    elif target_root == repository_root:
        tests_root = target_root / "tests"
    else:
        tests_root = target_root.parent / "tests"
    return {
        "schema_version": 1,
        "target": _repository_relative(target_root, repository_root),
        "skill": {
            "name": skill_root.name,
            "has_skill_md": _is_regular_file(skill_root / "SKILL.md"),
            "has_openai_yaml": _is_regular_file(
                skill_root / "agents" / "openai.yaml"
            ),
            "references": _count_regular_files(
                skill_root / "references",
                repository_root,
            ),
            "scripts": _count_regular_files(
                skill_root / "scripts",
                repository_root,
            ),
        },
        "plugin_manifests": plugin_manifests,
        "marketplace_adapters": marketplace_adapters,
        "tests": _count_regular_files(tests_root, repository_root),
        "has_optimizer_config": _is_regular_file(config.path),
    }


def render_human(inventory: dict[str, object]) -> str:
    skill = inventory["skill"]
    if not isinstance(skill, dict):
        raise TypeError("inventory skill must be an object")

    manifests = inventory["plugin_manifests"]
    adapters = inventory["marketplace_adapters"]
    if not isinstance(manifests, list) or not isinstance(adapters, list):
        raise TypeError("inventory paths must be arrays")

    yes_no = {True: "yes", False: "no"}
    lines = [
        f"Target: {inventory['target']}",
        f"Skill: {skill['name']}",
        f"SKILL.md: {yes_no[bool(skill['has_skill_md'])]}",
        f"OpenAI metadata: {yes_no[bool(skill['has_openai_yaml'])]}",
        f"References: {skill['references']}",
        f"Scripts: {skill['scripts']}",
        f"Plugin manifests: {len(manifests)}",
    ]
    lines.extend(f"  - {path}" for path in manifests)
    lines.append(f"Marketplace adapters: {len(adapters)}")
    lines.extend(f"  - {path}" for path in adapters)
    lines.extend(
        [
            f"Tests: {inventory['tests']}",
            "Optimizer config: "
            f"{yes_no[bool(inventory['has_optimizer_config'])]}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a configured skill's repository structure."
    )
    parser.add_argument("config", help="path to skill optimizer configuration")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="emit deterministic JSON",
    )
    arguments = parser.parse_args(argv)

    try:
        config = optimizer_config.load_config(arguments.config)
    except ConfigError as error:
        print(f"inspect_skill: {_sanitize_diagnostic(error)}", file=sys.stderr)
        return 2

    try:
        inventory = inspect(config)
    except InspectionError as error:
        print(f"inspect_skill: {error}", file=sys.stderr)
        return 2
    if arguments.as_json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    else:
        print(render_human(inventory))
    skill = inventory["skill"]
    has_skill_md = isinstance(skill, dict) and skill["has_skill_md"]
    if not has_skill_md:
        print(
            "inspect_skill: missing required file: "
            f"{inventory['target']}/SKILL.md",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
