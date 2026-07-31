# Skill Development Optimization Baseline

These responses were captured before `optimizing-skill-development` existed.
Each case preserves the exact prompt and verbatim response, then records:
selected profile, unnecessary checks, missing checks, artifact-freezing errors,
and evidence-integrity errors.

Local home-directory prefixes in the verbatim responses were redacted as
`<REDACTED_HOME>`. No other response content was changed.

## metadata-only

### Exact prompt

```text
Change only agents/openai.yaml display text in a portable skill plugin. Plan the validation and evidence needed.

Respond with your chosen validation scope, commands or evidence categories, and stopping criteria.
```

### Verbatim response

Chosen scope: focused YAML contract, portable plugin ingestion, and one-file diff proof. No behavioral or corpus testing is needed for display-only metadata.

Evidence:

- Before/after `agents/openai.yaml` content.
- Exact parsed values and required key structure.
- `validate_plugin.py` pass.
- `quick_validate.py` regression pass.
- `git diff --check` pass.
- Only the intended `agents/openai.yaml` differs from the pre-task state.

Stop on any malformed YAML, unexpected key/file change, incorrect or empty copy, broken `$skill-name` prompt, validator failure, or whitespace error.

### Observed categories

- Selected profile: quick.
- Unnecessary checks: none observed; the response explicitly rejected behavioral and corpus testing.
- Missing checks: none material for the proposed metadata-only change.
- Artifact-freezing errors: before/after content and command passes were requested, but no durable artifact path, immutable revision, or transcript format was specified.
- Evidence-integrity errors: none observed.

## reference-attribution

### Exact prompt

```text
Correct an attributed reference and its code example without changing SKILL.md. Plan the validation and evidence needed.

Respond with your chosen validation scope, commands or evidence categories, and stopping criteria.
```

### Verbatim response

Chosen validation scope:

- Targeted reference correctness and canonical attribution.
- Swift example syntax/type-checking.
- Full corpus regression validation.
- Confirmation that `SKILL.md` is unchanged.
- Originality audit when local research inputs are available.

Commands:

```bash
git diff --check -- <target-reference>
git diff -- plugins/swift-design-patterns/skills/choosing-swift-design-patterns/SKILL.md

python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns

python3 -m unittest discover \
  -s plugins/swift-design-patterns/tests \
  -p 'test_*.py'
```

Also inspect the canonical attributed page and compare pattern roles/interactions with the local prose and example. If `.research/` exists, run `audit_originality.py`; otherwise record that check as unavailable.

Stopping criteria: all checks exit successfully, the canonical source supports the attribution, the example type-checks, `SKILL.md` has no diff, and no unrelated files changed. Stop and report any compiler failure, broken or ambiguous attribution, originality match, validator failure, or unrelated diff.

### Observed categories

- Selected profile: content.
- Unnecessary checks: the full 22-guide corpus validator and complete plugin unit suite are broader than a single attributed reference and code-example correction.
- Missing checks: no material content check was omitted.
- Artifact-freezing errors: the source-fidelity comparison and command results were not assigned a durable artifact, revision, or transcript.
- Evidence-integrity errors: none observed; unavailable originality inputs were to be recorded as unavailable rather than passing.

## selector-trigger

### Exact prompt

```text
Change a skill's trigger description and mandatory recommendation workflow. The configured fresh-agent evaluator is unavailable and files read can only be self-reported. Plan the validation and evidence needed.

Respond with your chosen validation scope, commands or evidence categories, and stopping criteria.
```

### Verbatim response

Chosen validation scope:

1. **Static trigger contract**
   - Frontmatter parses.
   - Description contains only concrete “when to use” conditions, not workflow instructions.
   - Trigger coverage includes both greenfield Swift design and existing-code review.
   - Description remains within skill metadata limits.

2. **Mandatory workflow contract**
   - Existing-code review without source context must request the missing files and make no recommendation.
   - With source supplied, the response must ground its recommendation in file-specific symbols or behavior.
   - Greenfield and direct named-pattern requests must still follow the native-first/no-change-first priority.
   - Recommendation output must include primary choice, rationale, costs/contraindications, and no more than two alternatives.

3. **Regression and hygiene**
   - Existing content validator and unit suite remain green.
   - No unrelated files, malformed links, whitespace errors, or accidental generated artifacts enter the diff.

Commands/evidence:

```bash
python3 -m unittest discover \
  -s plugins/swift-design-patterns/tests \
  -p 'test_*.py'

python3 \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns

git diff --check
git diff -- \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns/SKILL.md \
  plugins/swift-design-patterns/tests
```

Add focused automated tests for frontmatter and required workflow language where practical. Preserve a scenario matrix and rubric covering:

- Missing review source → asks for context, no recommendation.
- Supplied review source → cites exact types/functions/branches from the fixture.
- Clear no-change case → recommends no change.
- Swift-native case → prefers closure/enum/`AsyncSequence` as appropriate.
- Justified GoF case → recommends the correct pattern.
- Named-pattern pressure → challenges an inferior requested pattern.

The unavailable fresh-agent evaluator is a real acceptance gap. Historical baseline transcripts can establish prior failure modes, and self-reported `FILES_READ` manifests can aid debugging, but neither proves discovery or actual file access. File-specific observations not present in the prompt provide stronger behavioral evidence, though still not tool-level proof.

Stopping criteria:

- Stop implementation when static checks, validators, focused tests, and diff hygiene pass.
- Report the result as **source-level validated; fresh-agent behavioral acceptance pending** while the evaluator remains unavailable.
- Do not claim trigger-routing or actual-reference-loading verification from self-report alone.
- Once the evaluator returns, require two independent fresh runs per mandatory scenario with 100% compliance on blocking workflow rules before declaring the change fully validated.

### Observed categories

- Selected profile: behavior.
- Unnecessary checks: none clearly unnecessary.
- Missing checks: executable fresh-agent acceptance is unavailable, and the response correctly leaves behavioral acceptance pending.
- Artifact-freezing errors: it says to preserve a scenario matrix and rubric, but gives no concrete artifact path or immutable transcript format for those scenarios or the future fresh-agent runs.
- Evidence-integrity errors: none observed. It explicitly refuses to count the unavailable evaluator or self-reported `FILES_READ` instrumentation as passing.

## importer-cache

### Exact prompt

```text
Change retry pacing and cache writes in a skill's external research importer. Plan the validation and evidence needed.

Respond with your chosen validation scope, commands or evidence categories, and stopping criteria.
```

### Verbatim response

Chosen validation scope: **Importer profile**, not full release validation. It covers retry, pacing, caching, and filesystem safety without unrelated content or behavioral-agent evidence.

Evidence required:

- Deterministic pacing tests using `FakeClock`: normal requests, 429/5xx/`URLError`, bounded exponential backoff, valid/invalid `Retry-After`, redirects, slow responses, and failures. Verify exact sleep durations and that delay begins after the prior attempt completes.
- Cache-write fault injection: partial/zero writes, sync/replace failures, destination swaps, interruption, temporary-file cleanup, and page/manifest checksum consistency.
- Hostile-cache regression coverage: symlinks, hardlinks, FIFOs, directories, renamed roots, permission failures, and traversal attempts must fail closed without mutating outside files.
- One local loopback integration check at the milestone proving real standard-library requests remain at least five seconds apart.
- Diff hygiene: no caches, request logs, research downloads, local paths, or temporary artifacts.

Commands:

```sh
cd plugins/swift-design-patterns/tests
python3 -m unittest -v \
  test_import_refactoring_guru.ImportClientTests \
  test_import_refactoring_guru.CacheAndImportTests \
  test_import_refactoring_guru.ImportRunTests \
  test_import_refactoring_guru.RedirectPolicyTests
```

Repeat that deterministic suite three times because pacing is timing-sensitive, then run:

```sh
python3 -m unittest discover -s plugins/swift-design-patterns/tests -v
python3 -m unittest -v \
  test_import_refactoring_guru.StandardLibraryIntegrationTests.test_default_interval_spaces_real_local_requests_by_five_seconds
git diff --check
git status --short
```

Stopping criteria: zero failures/errors; stable repeated runs; real interval ≥5 seconds; every changed retry/write branch has regression coverage; no stale page/manifest pair, outside-file mutation, or leaked temporary file. Any flaky timing, uncovered failure path, checksum mismatch, or cache escape blocks completion. A live Refactoring.Guru import is optional, separately approved evidence—not required for this change.

### Observed categories

- Selected profile: importer.
- Unnecessary checks: repeating an injected-clock deterministic suite three times is redundant unless the implementation contains nondeterminism; the five-second loopback milestone is broader than focused deterministic coverage but directly checks the pacing integration boundary.
- Missing checks: none material; retry semantics, hostile cache states, atomicity, and integration pacing are covered.
- Artifact-freezing errors: the response asks for extensive behavioral evidence but does not freeze command output or the timing result in a named, revision-linked artifact.
- Evidence-integrity errors: none observed; optional live-network evidence is explicitly separated from required evidence.

## mixed-release

### Exact prompt

```text
Release a new plugin after changing SKILL.md, references, scripts, and marketplace manifests. Plan the validation and evidence needed.

Respond with your chosen validation scope, commands or evidence categories, and stopping criteria.
```

### Verbatim response

Validation scope: skill behavior, reference integrity, script tests, cross-platform manifest consistency, and fresh-install smoke testing.

Core commands:

```bash
python3 -m unittest discover \
  -s plugins/swift-design-patterns/tests \
  -p 'test_*.py' -v

python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns

python3 <REDACTED_HOME>/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns

python3 <REDACTED_HOME>/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/swift-design-patterns

git diff --check
git status --short
git diff --stat
```

Evidence must include:

- RED/forward scenario results for any changed skill behavior.
- Complete reference corpus validation and Swift example typechecking.
- Script unit-test output.
- Originality audit when source research inputs are available and references changed.
- JSON/schema and name/version/source consistency across all plugin and marketplace manifests.
- Diff/privacy inspection excluding caches, research downloads, credentials, and local identifiers.
- Reinstall from the intended marketplace/revision and discovery plus representative prompt verification in a fresh Codex task.
- Commit SHA/tag, toolchain versions, commands, exit codes, and concise results.

Release stops on any validator/test failure, missing baseline for newly claimed behavior, manifest/version drift, unavailable required originality evidence, marketplace/source mismatch, or failed fresh-install discovery.

### Observed categories

- Selected profile: full.
- Unnecessary checks: none observed for a release spanning skill behavior, content, executable scripts, and all manifests.
- Missing checks: the manifest schema/consistency evidence category is named, but no concrete command is supplied for it.
- Artifact-freezing errors: commit identity and reproducibility metadata are required, but the behavioral and install-smoke outputs still have no named artifact or immutable transcript format.
- Evidence-integrity errors: unavailable required originality evidence blocks release rather than being counted as passing, but the verbatim response originally embedded a stable local `<REDACTED_HOME>/...` path in proposed commands instead of a portable placeholder.

## Overall observation

BASELINE_FAILURE_OBSERVED. The reference case expands a targeted content correction
into corpus-wide and full-suite checks, and the behavior/importer/release cases request
behavioral or runtime evidence without specifying a durable frozen artifact. No response
counted the unavailable evaluator or self-reported files-read instrumentation as passing.
The mixed-release response also proposed commands containing an unsanitized local path;
it remains above only because this baseline is required to preserve the response verbatim.
