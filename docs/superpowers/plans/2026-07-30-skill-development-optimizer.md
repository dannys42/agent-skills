# Skill Development Optimizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable plugin that selects the minimum adequate skill-validation profile and records reproducible evidence, timing, and frozen behavioral evaluations.

**Architecture:** A concise `optimizing-skill-development` skill complements `skill-creator` and `writing-skills`. Six focused Python entry scripts own inventory, classification, hashing, command execution, evidence verification, and timing; one small shared configuration module exists because path containment and schema parsing are common security invariants.

**Tech Stack:** Markdown agent skills, Python 3 standard library, `unittest`, JSON, Git, Codex/Claude/Cursor/Gemini plugin manifests.

---

## File Map

Create:

```text
plugins/skill-development-optimizer/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── README.md
├── gemini-extension.json
├── skill-optimizer.example.json
├── skills/
│   └── optimizing-skill-development/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── references/
│       │   ├── frozen-evaluations.md
│       │   ├── importer-threat-model.md
│       │   └── validation-profiles.md
│       └── scripts/
│           ├── classify_change.py
│           ├── hash_artifact.py
│           ├── inspect_skill.py
│           ├── manage_evidence.py
│           ├── optimizer_config.py
│           ├── report_timing.py
│           └── run_validation.py
└── tests/
    ├── baseline-results.md
    ├── evidence/
    │   └── final/
    │       ├── artifact.json
    │       ├── evidence.json
    │       ├── case-01/
    │       │   ├── files-read.txt
    │       │   ├── prompt.md
    │       │   └── response.md
    │       ├── case-02/
    │       │   ├── files-read.txt
    │       │   ├── prompt.md
    │       │   └── response.md
    │       ├── case-03/
    │       │   ├── files-read.txt
    │       │   ├── prompt.md
    │       │   └── response.md
    │       ├── case-04/
    │       │   ├── files-read.txt
    │       │   ├── prompt.md
    │       │   └── response.md
    │       └── case-05/
    │           ├── files-read.txt
    │           ├── prompt.md
    │           └── response.md
    ├── evaluation-cases.json
    ├── forward-results.md
    ├── support.py
    ├── test_classify_change.py
    ├── test_cli_integration.py
    ├── test_hash_artifact.py
    ├── test_inspect_skill.py
    ├── test_manage_evidence.py
    ├── test_optimizer_config.py
    ├── test_report_timing.py
    └── test_run_validation.py
```

Modify:

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
.cursor-plugin/marketplace.json
README.md
```

`optimizer_config.py` is the only initially shared production module. It owns
the configuration dataclasses, canonical repository-relative path resolution,
and JSON schema checks needed by classification, hashing, and validation.
Do not add a generic utilities module.

## Configuration Contract

Use this versioned shape:

```json
{
  "schema_version": 1,
  "target": "plugins/example-plugin/skills/example-skill",
  "distributable": {
    "include": [
      "SKILL.md",
      "agents/**/*.yaml",
      "references/**/*.md",
      "scripts/**/*.py"
    ],
    "exclude": [
      "**/__pycache__/**",
      "**/*.pyc"
    ]
  },
  "commands": {
    "quick-validate": {
      "argv": ["python3", "scripts/quick_validate.py", "plugins/example-plugin/skills/example-skill"],
      "cwd": ".",
      "timeout_seconds": 60,
      "max_output_bytes": 1048576,
      "network": false,
      "timing_kind": "work"
    }
  },
  "profiles": {
    "quick": ["quick-validate"],
    "content": ["quick-validate"],
    "behavior": ["quick-validate"],
    "importer": ["quick-validate"],
    "full": ["quick-validate"]
  },
  "evaluations": {
    "cases": "tests/evaluation-cases.json",
    "rubric": "tests/evaluation-rubric.json"
  }
}
```

Paths are relative to the enclosing Git repository root. Discover it with
`git -C CONFIG_PARENT rev-parse --show-toplevel`; when the configuration is not
inside a Git worktree, use the configuration parent as the selected repository.
Reject absolute paths, `..` traversal, symlink escapes, missing targets,
duplicate command IDs after JSON parsing, unknown profile command IDs, shell
strings in place of argv arrays, invalid timeouts, and output bounds outside
`1...16_777_216`.

### Task 1: Capture baseline optimization failures

**Files:**
- Create: `plugins/skill-development-optimizer/tests/evaluation-cases.json`
- Create: `plugins/skill-development-optimizer/tests/baseline-results.md`

- [ ] **Step 1: Create five baseline cases**

Write:

```json
[
  {
    "id": "metadata-only",
    "prompt": "Change only agents/openai.yaml display text in a portable skill plugin. Plan the validation and evidence needed.",
    "expected_profile": "quick"
  },
  {
    "id": "reference-attribution",
    "prompt": "Correct an attributed reference and its code example without changing SKILL.md. Plan the validation and evidence needed.",
    "expected_profile": "content"
  },
  {
    "id": "selector-trigger",
    "prompt": "Change a skill's trigger description and mandatory recommendation workflow. The configured fresh-agent evaluator is unavailable and files read can only be self-reported. Plan the validation and evidence needed.",
    "expected_profile": "behavior"
  },
  {
    "id": "importer-cache",
    "prompt": "Change retry pacing and cache writes in a skill's external research importer. Plan the validation and evidence needed.",
    "expected_profile": "importer"
  },
  {
    "id": "mixed-release",
    "prompt": "Release a new plugin after changing SKILL.md, references, scripts, and marketplace manifests. Plan the validation and evidence needed.",
    "expected_profile": "full"
  }
]
```

- [ ] **Step 2: Run fresh agents without the new skill**

Give each fresh agent only one prompt. Ask for the chosen validation scope,
commands or evidence categories, and stopping criteria. Do not provide the
expected profile, this plan, the design, or results from other cases.

Expected: at least one agent over-tests `metadata-only`, under-tests
`selector-trigger` or `importer-cache`, or proposes behavioral evidence without
freezing one artifact. Record whether any response incorrectly counts the
unavailable evaluator or files-read instrumentation as passing.

- [ ] **Step 3: Record exact baseline responses**

Create `baseline-results.md` with this header:

```markdown
# Skill Development Optimization Baseline

These responses were captured before `optimizing-skill-development` existed.
Each case preserves the exact prompt and verbatim response, then records:
selected profile, unnecessary checks, missing checks, artifact-freezing errors,
and evidence-integrity errors.
```

Append each exact prompt, verbatim response, and observed failure categories.
Do not rewrite or summarize the response in place of raw output.

- [ ] **Step 4: Commit baseline evidence**

Run:

```bash
git add plugins/skill-development-optimizer/tests/evaluation-cases.json \
  plugins/skill-development-optimizer/tests/baseline-results.md
git commit -m "test(skill-optimizer): capture validation baseline"
```

### Task 2: Scaffold the portable plugin and skill resource directories

**Files:**
- Create: `plugins/skill-development-optimizer/.codex-plugin/plugin.json`
- Create: `plugins/skill-development-optimizer/.claude-plugin/plugin.json`
- Create: `plugins/skill-development-optimizer/.cursor-plugin/plugin.json`
- Create: `plugins/skill-development-optimizer/gemini-extension.json`
- Create temporarily, then remove: `plugins/skill-development-optimizer/skills/optimizing-skill-development/SKILL.md`
- Create temporarily, then remove: `plugins/skill-development-optimizer/skills/optimizing-skill-development/agents/openai.yaml`
- Create: resource directories under `skills/optimizing-skill-development/`

- [ ] **Step 1: Initialize the skill only after baseline capture**

Run:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  optimizing-skill-development \
  --path plugins/skill-development-optimizer/skills \
  --resources scripts,references \
  --interface display_name="Optimizing Skill Development" \
  --interface short_description="Choose proportional skill validation" \
  --interface default_prompt="Use $optimizing-skill-development to optimize creation or maintenance of this skill."
```

Expected: generated skill, agents metadata, scripts, and references directories.
Delete the generated `SKILL.md` and `agents/openai.yaml` immediately so no
production skill exists before the forward-test RED phase is complete. Later
tasks recreate every shipped resource with test-first content.

- [ ] **Step 2: Add exact portable manifests**

Create `.codex-plugin/plugin.json`:

```json
{
  "name": "skill-development-optimizer",
  "version": "1.0.0",
  "description": "Risk-proportional validation and reproducible evidence for developing agent skills",
  "license": "MIT",
  "skills": "./skills/",
  "author": {
    "name": "Danny Sung",
    "url": "https://github.com/dannys42"
  },
  "repository": "https://github.com/dannys42/agent-skills",
  "keywords": [
    "agent-skills",
    "skill-development",
    "validation",
    "evaluation",
    "testing",
    "optimization"
  ],
  "interface": {
    "displayName": "Skill Development Optimizer",
    "shortDescription": "Validate skill changes proportionally",
    "longDescription": "Classify skill-development risk, run proportional validation, and preserve reproducible behavioral evidence.",
    "developerName": "Danny Sung",
    "category": "Developer Tools",
    "capabilities": [
      "Skill change-risk classification",
      "Validation profile selection",
      "Frozen evaluation evidence",
      "Timing and bottleneck reporting"
    ],
    "defaultPrompt": [
      "Optimize this skill-development task while preserving adequate evidence."
    ]
  }
}
```

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "skill-development-optimizer",
  "version": "1.0.0",
  "description": "Risk-proportional validation and reproducible evidence for developing agent skills",
  "license": "MIT",
  "author": {
    "name": "Danny Sung"
  },
  "keywords": [
    "agent-skills",
    "skill-development",
    "validation",
    "evaluation",
    "testing",
    "optimization"
  ]
}
```

Create `.cursor-plugin/plugin.json`:

```json
{
  "name": "skill-development-optimizer",
  "displayName": "Skill Development Optimizer",
  "version": "1.0.0",
  "description": "Risk-proportional validation and reproducible evidence for developing agent skills",
  "license": "MIT",
  "author": {
    "name": "Danny Sung"
  },
  "repository": "https://github.com/dannys42/agent-skills",
  "keywords": [
    "agent-skills",
    "skill-development",
    "validation",
    "evaluation",
    "testing",
    "optimization"
  ],
  "category": "developer-tools",
  "tags": [
    "agent-skills",
    "validation",
    "testing"
  ],
  "skills": "./skills/"
}
```

Create `gemini-extension.json`:

```json
{
  "name": "skill-development-optimizer",
  "version": "1.0.0",
  "description": "Risk-proportional validation and reproducible evidence for developing agent skills"
}
```

- [ ] **Step 3: Validate manifest JSON**

Run:

```bash
python3 -m json.tool plugins/skill-development-optimizer/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/skill-development-optimizer/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/skill-development-optimizer/.cursor-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/skill-development-optimizer/gemini-extension.json >/dev/null
```

Expected: all commands exit 0.

- [ ] **Step 4: Commit scaffold**

Run:

```bash
git add plugins/skill-development-optimizer
git commit -m "feat(skill-optimizer): scaffold portable plugin"
```

### Task 3: Implement secure configuration parsing test-first

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/optimizer_config.py`
- Create: `plugins/skill-development-optimizer/tests/support.py`
- Create: `plugins/skill-development-optimizer/tests/test_optimizer_config.py`

- [ ] **Step 1: Add dynamic-import test support**

Create `support.py`:

```python
from importlib import util
from pathlib import Path
import sys

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = (
    PLUGIN_ROOT
    / "skills"
    / "optimizing-skill-development"
    / "scripts"
)


def load_script(name: str):
    path = SCRIPTS_ROOT / f"{name}.py"
    spec = util.spec_from_file_location(f"skill_optimizer_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
```

- [ ] **Step 2: Write failing configuration tests**

Cover the valid contract and exact errors:

```python
class OptimizerConfigTests(unittest.TestCase):
    def test_loads_valid_configuration(self):
        with configured_repository() as (repository, config_path):
            config = optimizer_config.load_config(config_path)

            self.assertEqual(config.repository_root, repository.resolve())
            self.assertEqual(config.target_root, (repository / "skills/example").resolve())
            self.assertEqual(config.profiles["quick"], ("quick-validate",))

    def test_rejects_escaping_command_working_directory(self):
        with configured_repository(command_cwd="../outside") as (_, config_path):
            with self.assertRaisesRegex(
                optimizer_config.ConfigError,
                r"command 'quick-validate' cwd escapes repository: \.\./outside",
            ):
                optimizer_config.load_config(config_path)

    def test_rejects_shell_string_argv(self):
        with configured_repository(command_argv="python3 validate.py") as (_, config_path):
            with self.assertRaisesRegex(
                optimizer_config.ConfigError,
                "command 'quick-validate' argv must be a non-empty array of strings",
            ):
                optimizer_config.load_config(config_path)
```

Also test: schema version, absolute/traversal target, missing target, symlink
target escape, empty argv element, timeout outside `1...3600`, output limit
outside `1...16_777_216`, invalid `network`/`timing_kind`, unknown command IDs,
missing profiles, evaluation paths escaping the repository, and malformed JSON.

- [ ] **Step 3: Run tests and verify RED**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_optimizer_config.py -v
```

Expected: import failure because `optimizer_config.py` does not exist.

- [ ] **Step 4: Implement the minimal typed configuration**

Define:

```python
from dataclasses import dataclass
import json
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


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be an object")
    return value


def _contained_path(root: Path, value: Any, label: str, must_exist: bool) -> Path:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{label} must be a non-empty relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ConfigError(f"{label} escapes repository: {value}")
    resolved = (root / candidate).resolve(strict=must_exist)
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ConfigError(f"{label} escapes repository: {value}") from error
    return resolved
```

Implement `discover_repository_root(config_parent)` with the Git command above
using an argv array and `shell=False`. Fall back to the resolved config parent
only when Git reports that it is not a repository. Implement
`load_config(path)` with the exact validation bounds above. Require every
profile key and reject profile command IDs absent from `commands`.

- [ ] **Step 5: Run tests and verify GREEN**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_optimizer_config.py -v
```

Expected: all configuration tests pass.

- [ ] **Step 6: Commit configuration module**

Run:

```bash
git add plugins/skill-development-optimizer/tests/support.py \
  plugins/skill-development-optimizer/tests/test_optimizer_config.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/optimizer_config.py
git commit -m "feat(skill-optimizer): parse validation configuration"
```

### Task 4: Implement skill inventory test-first

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py`
- Create: `plugins/skill-development-optimizer/tests/test_inspect_skill.py`

- [ ] **Step 1: Write failing inventory tests**

Use a temporary plugin containing one skill, two references, one script, plugin
manifests, tests, and a configuration. Assert this exact result:

```python
expected = {
    "target": "skills/example",
    "skill": {
        "name": "example",
        "has_skill_md": True,
        "has_openai_yaml": True,
        "references": 2,
        "scripts": 1,
    },
    "plugin_manifests": [
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        "gemini-extension.json",
    ],
    "marketplace_adapters": [],
    "tests": 1,
    "has_optimizer_config": True,
}
self.assertEqual(inspect_skill.inspect(config), expected)
```

Add tests for a standalone skill without plugin manifests, missing `SKILL.md`,
symlinked resources excluded from counts, and deterministic sorted JSON CLI
output.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_inspect_skill.py -v
```

Expected: import failure for missing `inspect_skill.py`.

- [ ] **Step 3: Implement inventory**

Expose:

```python
def inspect(config: OptimizerConfig) -> dict[str, object]:
    ...


def render_human(inventory: dict[str, object]) -> str:
    ...


def main(argv: list[str] | None = None) -> int:
    ...
```

Count only regular, nonsymlink files beneath the resolved target. Discover the
plugin root from the configuration root and emit repository-relative POSIX
paths. CLI:

```text
inspect_skill.py CONFIG [--json]
```

Return 2 for configuration errors and 1 when required `SKILL.md` is absent.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_inspect_skill.py -v
```

Expected: all inventory tests pass.

- [ ] **Step 5: Commit inventory**

Run:

```bash
git add plugins/skill-development-optimizer/tests/test_inspect_skill.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py
git commit -m "feat(skill-optimizer): inspect skill structure"
```

### Task 5: Implement risk classification test-first

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py`
- Create: `plugins/skill-development-optimizer/tests/test_classify_change.py`

- [ ] **Step 1: Write failing path-classification tests**

Define the public API:

```python
class ClassificationTests(unittest.TestCase):
    def test_metadata_only_selects_quick(self):
        result = classify_change.classify_paths(
            ["skills/example/agents/openai.yaml"],
            target_prefix="skills/example",
        )
        self.assertEqual(result.profile, "quick")
        self.assertEqual(result.categories, ("metadata",))

    def test_reference_change_selects_content(self):
        result = classify_change.classify_paths(
            ["skills/example/references/policy.md"],
            target_prefix="skills/example",
        )
        self.assertEqual(result.profile, "content")

    def test_skill_body_selects_behavior(self):
        result = classify_change.classify_paths(
            ["skills/example/SKILL.md"],
            target_prefix="skills/example",
        )
        self.assertEqual(result.profile, "behavior")

    def test_importer_change_selects_importer(self):
        result = classify_change.classify_paths(
            ["skills/example/scripts/import_catalog.py"],
            target_prefix="skills/example",
        )
        self.assertEqual(result.profile, "importer")

    def test_mixed_categories_escalate_to_full(self):
        result = classify_change.classify_paths(
            [
                "skills/example/SKILL.md",
                "skills/example/references/policy.md",
            ],
            target_prefix="skills/example",
        )
        self.assertEqual(result.profile, "full")
```

Also test ordinary non-importer scripts and unknown paths select `full`;
tests-only changes select `quick`; no changes returns `quick` with reason
`no distributable changes`; and Git collection includes committed, modified,
staged, and untracked paths without duplicates.

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_classify_change.py -v
```

Expected: missing-module import failure.

- [ ] **Step 3: Implement classification**

Define:

```python
from dataclasses import dataclass
from pathlib import PurePosixPath
import subprocess


@dataclass(frozen=True)
class Classification:
    profile: str
    categories: tuple[str, ...]
    paths: tuple[str, ...]
    reasons: tuple[str, ...]


IMPORTER_TERMS = (
    "import",
    "fetch",
    "download",
    "cache",
    "crawl",
    "scrape",
    "sync",
)
```

Rules in order:

1. `SKILL.md` → behavior.
2. `references/**`, examples, attribution, or content policy → content.
3. script basename containing an importer term → importer.
4. any other production script or unknown distributable path → full.
5. `agents/openai.yaml`, plugin/marketplace JSON, README, license, and tests →
   quick.
6. More than one non-test category → full.

Expose `collect_git_paths(repository, base)` using:

```bash
git diff --name-only main...HEAD
git diff --name-only
git diff --cached --name-only
git status --porcelain=v1 --untracked-files=all
```

Invoke with `subprocess.run` argv arrays, never a shell. Normalize and sort
paths, reject newline-bearing names, and return path-specific reasons.

CLI:

```text
classify_change.py CONFIG [--base REF] [--json]
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_classify_change.py -v
```

Expected: all classification tests pass.

- [ ] **Step 5: Commit classifier**

Run:

```bash
git add plugins/skill-development-optimizer/tests/test_classify_change.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py
git commit -m "feat(skill-optimizer): classify skill change risk"
```

### Task 6: Implement reproducible artifact hashing test-first

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py`
- Create: `plugins/skill-development-optimizer/tests/test_hash_artifact.py`

- [ ] **Step 1: Write failing hashing tests**

Test:

```python
class ArtifactHashTests(unittest.TestCase):
    def test_hash_is_length_framed_and_path_order_independent(self):
        files = {
            "SKILL.md": b"skill",
            "references/a.md": b"reference",
        }
        first = hash_artifact.digest_entries(files.items())
        second = hash_artifact.digest_entries(reversed(tuple(files.items())))
        expected = independent_length_framed_digest(files.items())
        self.assertEqual(first, second)
        self.assertEqual(first, expected)

    def test_content_boundary_ambiguity_changes_hash(self):
        self.assertNotEqual(
            hash_artifact.digest_entries([("a", b"bc")]),
            hash_artifact.digest_entries([("ab", b"c")]),
        )
```

Define `independent_length_framed_digest` in the test with a short local
reference implementation using `struct.pack(">Q", length)`. It must not call
production helpers.

Also test sorted POSIX paths, include/exclude behavior, empty selection failure,
symlink rejection, nonregular-file rejection, changed bytes, executable-bit
independence, JSON manifest output, and no traversal outside target.

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_hash_artifact.py -v
```

Expected: missing-module import failure.

- [ ] **Step 3: Implement hashing**

Define:

```python
import hashlib
from pathlib import Path, PurePosixPath
import struct

ALGORITHM = "sha256-length-framed-v1"


def digest_entries(entries) -> str:
    digest = hashlib.sha256()
    normalized = sorted(
        (PurePosixPath(path).as_posix(), bytes(content))
        for path, content in entries
    )
    for path, content in normalized:
        encoded_path = path.encode("utf-8")
        digest.update(struct.pack(">Q", len(encoded_path)))
        digest.update(encoded_path)
        digest.update(struct.pack(">Q", len(content)))
        digest.update(content)
    return digest.hexdigest()
```

Use `glob.glob(..., root_dir=target, recursive=True)` for includes. Filter
excludes with `PurePosixPath.match`, require regular nonsymlink files, ensure
every resolved file remains beneath target, and deduplicate overlapping globs.

CLI:

```text
hash_artifact.py CONFIG [--json] [--output MANIFEST]
```

Manifest:

```json
{
  "schema_version": 1,
  "algorithm": "sha256-length-framed-v1",
  "digest": "<64 lowercase hex>",
  "target": "skills/example-skill",
  "files": [
    {"path": "SKILL.md", "bytes": 123}
  ]
}
```

- [ ] **Step 4: Verify GREEN and independent reproduction**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_hash_artifact.py -v
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
  plugins/skill-development-optimizer/skill-optimizer.example.json --json
```

Expected: tests pass. Task 10 creates the repository example configuration.
At this task, run the same CLI against a temporary fixture configuration and
verify its digest with the independent test implementation.

- [ ] **Step 5: Commit hasher**

Run:

```bash
git add plugins/skill-development-optimizer/tests/test_hash_artifact.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py
git commit -m "feat(skill-optimizer): hash frozen skill artifacts"
```

### Task 7: Implement bounded validation execution test-first

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py`
- Create: `plugins/skill-development-optimizer/tests/test_run_validation.py`

- [ ] **Step 1: Write failing command-execution tests**

Test real subprocesses with temporary scripts:

```python
class ValidationRunnerTests(unittest.TestCase):
    def test_runs_profile_commands_in_declared_order_without_shell(self):
        report = run_validation.run_profile(
            config,
            "quick",
            clock=SteppingClock([10.0, 10.25, 11.0, 11.5]),
        )
        self.assertEqual(
            [command["id"] for command in report["commands"]],
            ["first", "second"],
        )
        self.assertEqual(report["status"], "passed")

    def test_missing_command_is_not_treated_as_passing(self):
        with self.assertRaisesRegex(
            run_validation.ValidationError,
            "profile 'quick' references unavailable command 'missing'",
        ):
            run_validation.run_profile(config_with_missing_command, "quick")

    def test_shell_metacharacters_are_literal_arguments(self):
        report = run_validation.run_profile(config_with_argument("$(touch nope)"), "quick")
        self.assertFalse((repository / "nope").exists())
        self.assertIn("$(touch nope)", report["commands"][0]["stdout"])
```

Also test timeout status, process termination, stdout and stderr truncation at
the exact configured byte bound, invalid UTF-8 replacement, cwd containment,
network commands marked `approval_required` unless `--allow-network` is set,
stop-on-failure default, `--continue-on-failure`, monotonic duration, atomic
report creation, and no partial report replacing a prior valid report.

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_run_validation.py -v
```

Expected: missing-module import failure.

- [ ] **Step 3: Implement the subprocess runner**

Use temporary files so captured output is bounded when read rather than stored
unbounded in memory:

```python
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


class ValidationError(RuntimeError):
    pass


def _read_bounded(stream, limit: int) -> tuple[str, bool]:
    stream.seek(0)
    content = stream.read(limit + 1)
    truncated = len(content) > limit
    return content[:limit].decode("utf-8", errors="replace"), truncated


def run_command(command, *, allow_network: bool, clock=time.monotonic):
    if command.network and not allow_network:
        return {
            "id": command.identifier,
            "status": "approval_required",
            "duration_seconds": 0.0,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "stdout_truncated": False,
            "stderr_truncated": False,
            "timing_kind": command.timing_kind,
        }
    started = clock()
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            completed = subprocess.run(
                command.argv,
                cwd=command.cwd,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                timeout=command.timeout_seconds,
                check=False,
                shell=False,
            )
            status = "passed" if completed.returncode == 0 else "failed"
            exit_code = completed.returncode
        except subprocess.TimeoutExpired:
            status = "timed_out"
            exit_code = None
        output, output_truncated = _read_bounded(stdout, command.max_output_bytes)
        errors, errors_truncated = _read_bounded(stderr, command.max_output_bytes)
    return {
        "id": command.identifier,
        "status": status,
        "duration_seconds": max(0.0, clock() - started),
        "exit_code": exit_code,
        "stdout": output,
        "stderr": errors,
        "stdout_truncated": output_truncated,
        "stderr_truncated": errors_truncated,
        "timing_kind": command.timing_kind,
    }
```

Implement `run_profile(config, profile, allow_network=False,
continue_on_failure=False, clock=time.monotonic)`. Overall status is `passed`
only when every command passed; `approval_required`, `timed_out`, and `failed`
remain distinct.

Write reports atomically with `tempfile.NamedTemporaryFile` in the destination
directory, `flush`, `os.fsync`, and `os.replace`.

CLI:

```text
run_validation.py CONFIG PROFILE
  [--allow-network]
  [--continue-on-failure]
  [--output REPORT.json]
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_run_validation.py -v
```

Expected: all runner tests pass.

- [ ] **Step 5: Commit validation runner**

Run:

```bash
git add plugins/skill-development-optimizer/tests/test_run_validation.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py
git commit -m "feat(skill-optimizer): run bounded validation profiles"
```

### Task 8: Implement frozen-cohort evidence management test-first

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py`
- Create: `plugins/skill-development-optimizer/tests/test_manage_evidence.py`

- [ ] **Step 1: Write failing evidence tests**

Use this evidence contract:

```json
{
  "schema_version": 1,
  "artifact": {
    "algorithm": "sha256-length-framed-v1",
    "digest": "<64 lowercase hex>",
    "manifest": "artifact.json"
  },
  "headline_cohort": "final",
  "cohorts": [
    {
      "id": "final",
      "status": "headline",
      "artifact_digest": "<same digest>",
      "runs": [
        {
          "id": "final-case-1",
          "case_id": "case-1",
          "prompt": "runs/final-case-1/prompt.md",
          "response": "runs/final-case-1/response.md",
          "files_read": "runs/final-case-1/files-read.txt",
          "files_read_kind": "agent-reported",
          "rubric": {
            "correct_profile": true,
            "mandatory_checks_present": true
          }
        }
      ]
    }
  ]
}
```

Tests:

```python
class EvidenceTests(unittest.TestCase):
    def test_rejects_mixed_artifact_hashes_in_headline_cohort(self):
        evidence = valid_evidence()
        evidence["cohorts"][0]["artifact_digest"] = "b" * 64
        self.assertEqual(
            manage_evidence.validate_evidence(root, evidence, cases, rubric),
            ["cohort 'final' artifact digest does not match frozen artifact"],
        )

    def test_rejects_multiple_headline_cohorts(self):
        evidence = valid_evidence()
        evidence["cohorts"].append(
            {**evidence["cohorts"][0], "id": "other", "status": "headline"}
        )
        self.assertIn(
            "evidence must contain exactly one headline cohort",
            manage_evidence.validate_evidence(root, evidence, cases, rubric),
        )

    def test_computes_score_from_declared_rubric(self):
        summary = manage_evidence.summarize(valid_evidence(), rubric)
        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["total"], 2)
```

Also test duplicate cohort/run IDs, unknown/missing case IDs, exact one run per
case in headline, missing/escaping/symlink prompt-response-read-list files,
empty verbatim response, unknown/missing rubric keys, nonboolean scores,
impossible reported totals, invalid digest, missing artifact manifest, manifest
digest mismatch, historical cohort preservation, and `files_read_kind` limited
to `agent-reported` or `independently-observed`.

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_manage_evidence.py -v
```

Expected: missing-module import failure.

- [ ] **Step 3: Implement evidence initialization and verification**

Expose:

```python
def initialize_evidence(
    artifact_manifest: Path,
    cases_path: Path,
    rubric_path: Path,
    output: Path,
    cohort_id: str,
) -> dict[str, object]:
    ...


def validate_evidence(
    root: Path,
    evidence: dict[str, object],
    cases: tuple[dict[str, object], ...],
    rubric_items: tuple[str, ...],
) -> list[str]:
    ...


def summarize(
    evidence: dict[str, object],
    rubric_items: tuple[str, ...],
) -> dict[str, object]:
    ...
```

`initialize_evidence` creates directories and exact prompt files from the case
JSON, but leaves response, files-read, and rubric results explicitly absent.
It must not create passing placeholders. Use atomic JSON writes.

CLI:

```text
manage_evidence.py init ARTIFACT.json CASES.json RUBRIC.json OUTPUT.json --cohort ID
manage_evidence.py verify EVIDENCE.json CASES.json RUBRIC.json [--json]
manage_evidence.py summarize EVIDENCE.json RUBRIC.json [--json]
```

Return 1 when verification diagnostics exist and print one deterministic
diagnostic per line.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_manage_evidence.py -v
```

Expected: all evidence tests pass.

- [ ] **Step 5: Commit evidence manager**

Run:

```bash
git add plugins/skill-development-optimizer/tests/test_manage_evidence.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py
git commit -m "feat(skill-optimizer): verify frozen evaluation evidence"
```

### Task 9: Implement timing reports test-first

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/report_timing.py`
- Create: `plugins/skill-development-optimizer/tests/test_report_timing.py`

- [ ] **Step 1: Write failing timing tests**

Use validation reports from Task 7:

```python
class TimingReportTests(unittest.TestCase):
    def test_ranks_bottlenecks_and_separates_mandatory_wait(self):
        reports = [
            report(
                ("forward-evaluation", 30.0, "work"),
                ("polite-download", 20.0, "mandatory_wait"),
                ("quick-validation", 2.0, "work"),
            )
        ]
        summary = report_timing.summarize_reports(reports)

        self.assertEqual(summary["total_seconds"], 52.0)
        self.assertEqual(summary["work_seconds"], 32.0)
        self.assertEqual(summary["mandatory_wait_seconds"], 20.0)
        self.assertEqual(
            [item["id"] for item in summary["bottlenecks"]],
            ["forward-evaluation", "polite-download", "quick-validation"],
        )
```

Also test multiple reports, stable tie sorting by command ID, failed/timed-out
command counts, empty reports, malformed negative/nonfinite duration rejection,
human output rounding, and JSON output preserving full precision.

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_report_timing.py -v
```

Expected: missing-module import failure.

- [ ] **Step 3: Implement timing aggregation**

Expose:

```python
import math


class TimingError(ValueError):
    pass


def summarize_reports(reports: list[dict[str, object]]) -> dict[str, object]:
    commands = []
    for report in reports:
        for command in report.get("commands", []):
            duration = command.get("duration_seconds")
            if (
                not isinstance(duration, (int, float))
                or isinstance(duration, bool)
                or not math.isfinite(duration)
                or duration < 0
            ):
                raise TimingError(
                    f"command '{command.get('id', '<missing>')}' has invalid duration"
                )
            commands.append(command)
    bottlenecks = sorted(
        commands,
        key=lambda command: (
            -float(command["duration_seconds"]),
            str(command["id"]),
        ),
    )
    ...
```

Return totals, counts by status, totals by `timing_kind`, and bottlenecks with
percentage of total. Human output must say `No timing evidence.` for no
commands rather than claiming optimization.

CLI:

```text
report_timing.py REPORT.json [REPORT.json ...] [--json]
```

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python3 -m unittest plugins/skill-development-optimizer/tests/test_report_timing.py -v
```

Expected: all timing tests pass.

- [ ] **Step 5: Commit timing reporter**

Run:

```bash
git add plugins/skill-development-optimizer/tests/test_report_timing.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/report_timing.py
git commit -m "feat(skill-optimizer): report validation bottlenecks"
```

### Task 10: Add the example configuration and integrated CLI tests

**Files:**
- Create: `plugins/skill-development-optimizer/skill-optimizer.example.json`
- Create: `plugins/skill-development-optimizer/tests/test_cli_integration.py`

- [ ] **Step 1: Add a failing integration test**

Create a temporary repository from the example configuration, replacing its
target and command paths with fixture paths. Run each CLI with `subprocess.run`
and assert:

```python
self.assertEqual(inspect_result.returncode, 0)
self.assertEqual(classify_result.returncode, 0)
self.assertEqual(hash_result.returncode, 0)
self.assertEqual(validation_result.returncode, 0)
self.assertEqual(evidence_verify_result.returncode, 0)
self.assertEqual(timing_result.returncode, 0)
```

Assert all JSON outputs parse, share schema version 1, and contain no absolute
paths. First run before the example file exists must fail with a missing-file
diagnostic.

- [ ] **Step 2: Verify RED**

Run:

```bash
python3 -m unittest discover -s plugins/skill-development-optimizer/tests -v
```

Expected: integration failure because `skill-optimizer.example.json` is absent.

- [ ] **Step 3: Create the example configuration**

Use the Configuration Contract from this plan with:

```json
{
  "schema_version": 1,
  "target": "plugins/skill-development-optimizer/skills/optimizing-skill-development",
  "distributable": {
    "include": [
      "SKILL.md",
      "agents/**/*.yaml",
      "references/**/*.md",
      "scripts/**/*.py"
    ],
    "exclude": [
      "**/__pycache__/**",
      "**/*.pyc"
    ]
  },
  "commands": {
    "optimizer-tests": {
      "argv": [
        "python3",
        "-m",
        "unittest",
        "discover",
        "-s",
        "plugins/skill-development-optimizer/tests",
        "-v"
      ],
      "cwd": ".",
      "timeout_seconds": 120,
      "max_output_bytes": 1048576,
      "network": false,
      "timing_kind": "work"
    }
  },
  "profiles": {
    "quick": ["optimizer-tests"],
    "content": ["optimizer-tests"],
    "behavior": ["optimizer-tests"],
    "importer": ["optimizer-tests"],
    "full": ["optimizer-tests"]
  },
  "evaluations": {
    "cases": "plugins/skill-development-optimizer/tests/evaluation-cases.json",
    "rubric": "plugins/skill-development-optimizer/tests/evaluation-rubric.json"
  }
}
```

The enclosing Git worktree is the selected repository root. Task 12 creates
`evaluation-rubric.json`; integration fixtures may supply it until then.

- [ ] **Step 4: Verify all script tests GREEN**

Run:

```bash
python3 -m unittest discover -s plugins/skill-development-optimizer/tests -v
python3 -m py_compile \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/*.py
```

Expected: all tests and compilation pass.

- [ ] **Step 5: Measure local overhead**

Run inspect, classify with explicit fixture paths, and hash ten times each
against both existing plugins. Record median durations in the implementation
notes. Expected: each median is less than 1.0 second. Do not add benchmark
claims to shipped documentation if the threshold is not met.

- [ ] **Step 6: Commit integrated toolkit**

Run:

```bash
git add plugins/skill-development-optimizer/skill-optimizer.example.json \
  plugins/skill-development-optimizer/tests
git commit -m "test(skill-optimizer): verify integrated toolkit"
```

### Task 11: Write the optimizer references

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/references/validation-profiles.md`
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/references/frozen-evaluations.md`
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/references/importer-threat-model.md`

- [ ] **Step 1: Write validation profile guidance**

Use this table as the authoritative routing contract:

```markdown
| Change | Minimum profile | Mandatory evidence |
|---|---|---|
| UI metadata, adapter JSON, installation prose | Quick | Structure, JSON, changed links, focused tests |
| References, examples, attribution, source links | Content | Quick plus content contracts, examples, attribution, originality |
| Trigger description, selector, mandatory workflow or judgment | Behavior | Frozen artifact, fresh cases, files read, rubric |
| Fetching, retries, redirects, pacing, cache or filesystem writes | Importer | Deterministic tests plus hostile-cache checks; approved live check at milestones |
| New plugin, release, mixed categories, unknown paths | Full | Every applicable profile |
```

Explain that a SKILL.md wording edit is behavioral unless a deterministic
comparison proves it cannot affect triggering or instructions. More than one
non-test category escalates to full. A downgrade requires a written rationale
and a list of mandatory checks still satisfied.

- [ ] **Step 2: Write frozen-evaluation guidance**

Require this sequence:

```markdown
1. Finish deterministic checks.
2. Hash the exact distributable artifact.
3. Initialize one cohort against that hash.
4. Give each fresh agent only its case prompt and frozen skill.
5. Capture prompt, verbatim response, run ID, and files read separately.
6. Score from the declared rubric.
7. If any distributable byte changes, mark the cohort historical and restart every headline case.
8. Keep exactly one headline cohort.
```

State that agent-reported files read are evidence, not independent
instrumentation. Prohibit cross-version aggregate headlines. Include the
length-framed hash algorithm and evidence verifier commands.

- [ ] **Step 3: Write the importer threat model**

Use this checklist:

```markdown
- Minimum request interval survives retries, redirects, and failures.
- Retry-After may lengthen but never shorten the minimum.
- Redirects remain on the exact allowed HTTPS origin and path family.
- Cache paths reject traversal, symlinks, hardlinks, FIFOs, devices, and directories.
- Root/ancestor replacement cannot redirect managed I/O.
- Reads, logs, temporary files, and replacements are anchored to a retained directory boundary.
- Interrupted writes preserve the last valid manifest/page pair.
- Closed handles fail closed; unsupported platform operations produce deterministic errors.
- Live network checks are explicit milestones, not routine edit checks.
```

Make clear that this profile applies only when a skill contains external
acquisition or cache code.

- [ ] **Step 4: Review reference length and links**

Run:

```bash
wc -w plugins/skill-development-optimizer/skills/optimizing-skill-development/references/*.md
rg -n -e 'TO[D]O|TB[D]|FIXM[E]' \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/references
```

Expected: each reference is 250–700 words and no placeholders are found.

- [ ] **Step 5: Commit references**

Run:

```bash
git add plugins/skill-development-optimizer/skills/optimizing-skill-development/references
git commit -m "docs(skill-optimizer): define validation profiles"
```

### Task 12: Create and forward-test the optimizer skill

**Files:**
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/SKILL.md`
- Create: `plugins/skill-development-optimizer/skills/optimizing-skill-development/agents/openai.yaml`
- Create: `plugins/skill-development-optimizer/tests/evaluation-rubric.json`
- Create: `plugins/skill-development-optimizer/tests/forward-results.md`
- Create: `plugins/skill-development-optimizer/tests/evidence/final/artifact.json`
- Create: `plugins/skill-development-optimizer/tests/evidence/final/evidence.json`
- Create: `plugins/skill-development-optimizer/tests/evidence/final/case-01/prompt.md`
- Create: `plugins/skill-development-optimizer/tests/evidence/final/case-01/response.md`
- Create: `plugins/skill-development-optimizer/tests/evidence/final/case-01/files-read.txt`
- Create equivalent `prompt.md`, `response.md`, and `files-read.txt` files for
  `case-02` through `case-05`
- Modify only if observed failures require it: skill, references, or scripts

- [ ] **Step 1: Create the explicit rubric**

Write:

```json
[
  "correct_profile",
  "risk_reasons_stated",
  "mandatory_checks_present",
  "unnecessary_checks_avoided",
  "missing_checks_not_passed",
  "frozen_artifact_required_when_behavioral",
  "network_approval_explicit_when_needed",
  "stopping_criteria_stated"
]
```

- [ ] **Step 2: Write the minimal skill**

Use exact frontmatter:

```yaml
---
name: optimizing-skill-development
description: Use when creating or changing an agent skill and validation effort risks being disproportionate, incomplete, non-reproducible, or mixed across artifact versions.
---
```

The body must be imperative, under 500 words, and contain:

```markdown
# Optimizing Skill Development

**REQUIRED SUB-SKILLS:** Use `skill-creator` and `writing-skills` for authoring fundamentals. Use `test-driven-development` for executable tooling.

## Core rule

Choose the smallest profile that covers the actual risk. Escalate uncertainty; never count a missing check as passing.
```

Then require:

1. distinguish new creation from maintenance;
2. inspect and classify before selecting a profile;
3. link `references/validation-profiles.md`;
4. invoke the scripts rather than reimplement deterministic work;
5. require `content` for references and examples;
6. require `behavior` for trigger, selector, workflow, or judgment changes;
7. link `references/frozen-evaluations.md` only for behavioral work;
8. link `references/importer-threat-model.md` only for importer work;
9. use `full` for new plugins, releases, mixed categories, and uncertainty;
10. require a recorded rationale for downgrade;
11. report selected profile, reasons, checks run/skipped, artifact identity,
    evidence status, duration, and next escalation condition.

- [ ] **Step 3: Generate final UI metadata**

Run:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development \
  --interface display_name="Optimizing Skill Development" \
  --interface short_description="Choose proportional skill validation" \
  --interface default_prompt="Use $optimizing-skill-development to optimize creation or maintenance of this skill."
```

Expected `agents/openai.yaml`:

```yaml
interface:
  display_name: "Optimizing Skill Development"
  short_description: "Choose proportional skill validation"
  default_prompt: "Use $optimizing-skill-development to optimize creation or maintenance of this skill."
```

- [ ] **Step 4: Validate structure and word count**

Run:

```bash
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development
wc -w plugins/skill-development-optimizer/skills/optimizing-skill-development/SKILL.md
```

Expected: `Skill is valid!` and fewer than 500 words.

- [ ] **Step 5: Run a clean frozen forward cohort**

Hash the completed skill with `hash_artifact.py`. Run all five cases from
`evaluation-cases.json` using fresh agents. For each run, replace
`CASE_PROMPT` with that case's exact `prompt` value and `SKILL_PATH` with the
resolved skill-directory path; the agent receives only:

```text
CASE_PROMPT

Use the skill directory SKILL_PATH. Report the validation plan and
write a separate list of relative skill files you actually read.
```

Do not provide the expected profile, baseline, rubric, design, or suspected
failure. Store each exact prompt, verbatim response, and files-read list under
`plugins/skill-development-optimizer/tests/evidence/final/case-01` through
`case-05`. Write the hash manifest to
`plugins/skill-development-optimizer/tests/evidence/final/artifact.json`, and
use `manage_evidence.py` to write and verify
`plugins/skill-development-optimizer/tests/evidence/final/evidence.json`.

Expected: 40/40 rubric checks pass against one artifact hash. If any
distributable file changes, mark the cohort historical and rerun all five
cases—not only failed cases.

- [ ] **Step 6: Write transparent forward results**

`forward-results.md` must include:

- artifact hash algorithm and digest;
- exact reproduction command;
- all five run IDs;
- exact prompts and verbatim responses;
- files-read kind and paths;
- all 40 rubric judgments;
- historical failed cohorts and refinements;
- exactly one headline result from one artifact.

- [ ] **Step 7: Commit skill and behavioral evidence**

Run:

```bash
git add plugins/skill-development-optimizer/skills/optimizing-skill-development \
  plugins/skill-development-optimizer/tests/evaluation-rubric.json \
  plugins/skill-development-optimizer/tests/forward-results.md \
  plugins/skill-development-optimizer/tests/evidence/final
git commit -m "feat(skill-optimizer): add proportional validation skill"
```

### Task 13: Add portable distribution metadata and documentation

**Files:**
- Create: `plugins/skill-development-optimizer/README.md`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.cursor-plugin/marketplace.json`
- Modify: `README.md`

- [ ] **Step 1: Document installation and operation**

The plugin README must cover:

- purpose and relationship to `skill-creator` and `writing-skills`;
- new-skill and maintenance workflows;
- six script commands with `--help` rather than duplicating flags;
- the five profiles;
- configuration location and safety boundaries;
- frozen evaluation evidence;
- Codex, Claude Code, and open skill-installer commands;
- no Swift toolchain requirement;
- no automatic network or destructive Git operations.

- [ ] **Step 2: Add marketplace entries**

Append after `swift-design-patterns`.

Codex:

```json
{
  "name": "skill-development-optimizer",
  "source": {
    "source": "local",
    "path": "./plugins/skill-development-optimizer"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Developer Tools"
}
```

Claude entry:

```json
{
  "name": "skill-development-optimizer",
  "source": "./plugins/skill-development-optimizer",
  "version": "1.0.0",
  "description": "Risk-proportional validation and reproducible evidence for developing agent skills",
  "keywords": [
    "agent-skills",
    "skill-development",
    "validation",
    "evaluation",
    "testing",
    "optimization"
  ]
}
```

Cursor entry:

```json
{
  "name": "skill-development-optimizer",
  "source": "plugins/skill-development-optimizer",
  "version": "1.0.0",
  "description": "Risk-proportional validation and reproducible evidence for developing agent skills",
  "keywords": [
    "agent-skills",
    "skill-development",
    "validation",
    "evaluation",
    "testing",
    "optimization"
  ]
}
```

Preserve each marketplace's existing top-level shape and ordering.

- [ ] **Step 3: Update root README**

Add a plugin table row and concise skill section. Add installation commands:

```bash
claude plugin install skill-development-optimizer@danny-sung-agent-skills
codex plugin add skill-development-optimizer@danny-sung-agent-skills
npx skills add dannys42/agent-skills \
  --skill optimizing-skill-development \
  --global \
  --agent codex
```

- [ ] **Step 4: Validate distribution**

Run:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .cursor-plugin/marketplace.json >/dev/null
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/skill-development-optimizer
```

Expected: JSON parsing and plugin validation pass.

- [ ] **Step 5: Commit portable distribution**

Run:

```bash
git add .agents/plugins/marketplace.json \
  .claude-plugin/marketplace.json \
  .cursor-plugin/marketplace.json \
  README.md \
  plugins/skill-development-optimizer/README.md
git commit -m "docs(skill-optimizer): add portable distribution"
```

### Task 14: Run final verification and request review

**Files:**
- Verify all files changed by Tasks 1–13

- [ ] **Step 1: Run the optimizer suite**

Run:

```bash
python3 -m unittest discover -s plugins/skill-development-optimizer/tests -v
python3 -m py_compile \
  plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/*.py
```

Expected: all tests and compilation pass.

- [ ] **Step 2: Run official validators**

Run:

```bash
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/skill-development-optimizer/skills/optimizing-skill-development
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/skill-development-optimizer
```

Expected: skill and plugin validation pass.

- [ ] **Step 3: Verify the example and frozen evidence**

Run:

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py \
  plugins/skill-development-optimizer/skill-optimizer.example.json --json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
  plugins/skill-development-optimizer/skill-optimizer.example.json --json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py \
  verify \
  plugins/skill-development-optimizer/tests/evidence/final/evidence.json \
  plugins/skill-development-optimizer/tests/evaluation-cases.json \
  plugins/skill-development-optimizer/tests/evaluation-rubric.json
```

Expected: all commands exit 0 and report one artifact hash.

- [ ] **Step 4: Verify change scope**

Run:

```bash
git diff --check main...HEAD
git status --short
git diff --stat main...HEAD
git log --oneline main..HEAD
rg -n -e 'TO[D]O|TB[D]|FIXM[E]|PLACEHOLDE[R]' \
  plugins/skill-development-optimizer \
  docs/superpowers/plans/2026-07-30-skill-development-optimizer.md
```

Expected: clean worktree, focused commits, no whitespace errors, and no
placeholders.

- [ ] **Step 5: Run the existing repository regression suite**

Run:

```bash
python3 -m unittest discover -s plugins/swift-design-patterns/tests -v
```

Expected: all existing tests pass. The localhost pacing integration may require
the same scoped sandbox approval used by the existing plan.

- [ ] **Step 6: Request two-stage final review**

Use `requesting-code-review` to inspect:

- classification accuracy and conservative escalation;
- configuration/path security;
- shell-free bounded command execution;
- artifact-hash reproducibility;
- evidence integrity and mixed-version rejection;
- timing accuracy;
- skill restraint and token efficiency;
- manifest and marketplace consistency.

Resolve findings test-first. If files change, use one focused fix commit and
rerun Steps 1–5.
