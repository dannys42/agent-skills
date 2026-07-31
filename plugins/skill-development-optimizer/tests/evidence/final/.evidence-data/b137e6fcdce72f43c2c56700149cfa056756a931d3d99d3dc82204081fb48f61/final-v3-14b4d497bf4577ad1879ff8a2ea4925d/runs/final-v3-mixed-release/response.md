Selected profile: `full`.

Deterministic inspection found behavior, content, metadata, production, tests, and unknown paths. A new plugin release independently requires `full`; the `SKILL.md`, references, scripts, and manifests make Quick + Content + Behavior applicable. Importer is not applicable unless script review finds external acquisition or cache management.

Validation plan:

1. Establish a clean release candidate.

   - Remove/exclude generated `__pycache__`, `.pyc`, lock files, staging directories, and temporary evidence from the candidate.
   - Ensure the optimizer config covers the exact target, distributable files, manifests, commands, evaluation cases, and rubric.
   - Run `inspect_skill.py` and `classify_change.py` from the repository root against the intended release base.
   - Resolve every unknown path before proceeding. Do not downgrade from `full`.

2. Verify test-first development evidence.

   - Preserve baseline/failing cases for changed skill behavior and each changed executable behavior.
   - Confirm the changed script tests failed for the intended reason before implementation, then passed after the minimal implementation.
   - Add focused regression cases for error paths, path safety, atomic outputs, configuration validation, and CLI contracts affected by the edits.

3. Configure and run the Full profile.

   - First audit that the configured `full` profile represents all mandatory checks; missing checks block validation.
   - Run only configured checks through:
     `python3 .../run_validation.py CONFIG full --output REPORT.json`
   - Quick evidence: plugin directory structure; all plugin/marketplace JSON parses; required manifest fields; consistent plugin name/version/source/skill inventory across adapters and marketplace registry; `agents/openai.yaml` alignment; changed-link checks; focused packaging tests.
   - Content evidence: reference contracts and examples are accurate; attribution/source links are valid; originality/provenance review passes.
   - Production evidence: focused and complete deterministic script tests pass with pristine output.
   - Importer checks remain explicitly “not applicable,” not “passed,” unless fetching/cache behavior is found. If found, add all threat-model checks and require approval before any live-network milestone.

4. Freeze behavioral evidence after deterministic checks pass.

   - Freeze the exact distributable with `hash_artifact.py`; record the `sha256-length-framed-v1` digest and manifest.
   - Declare fresh cases and rubric before initializing one headline cohort.
   - Initialize with `manage_evidence.py init`.
   - Run every case with a fresh agent receiving only the frozen skill and case prompt.
   - Capture prompt, verbatim response, generated run ID, separately reported files read, and every rubric result.
   - Complete, verify, and summarize with `manage_evidence.py`.
   - If any distributable byte changes, mark the cohort historical and rerun every headline case.

5. Capture release evidence once.

   - Record exact command, commit SHA, tool/Python versions, exit status, warnings, artifact digest, cohort ID, concise result, and full temporary log.
   - Use `report_timing.py` to separate work time from waiting time.
   - Sanitize personal paths and local identifiers.
   - Record checks skipped as not applicable with rationale; never treat unavailable evidence as passing.
   - Verify the packaged plugin from the release artifact, including install/discovery and a representative invocation, before publishing.

Stopping criteria, declared before checks: stop on any failed or missing mandatory check, unknown path, manifest/version mismatch, content or attribution failure, artifact/evidence mismatch, mixed or incomplete cohort, distributable mutation after freezing, newly discovered importer behavior, or need for unapproved live network access.

Current evidence status: inspection and classification were run; they selected `full` and exposed unknown/generated paths that must be cleaned or classified. No validation profile, artifact freeze, cohort, or release check was run, so none is reported as passing.

Relative skill files actually read:

```text
SKILL.md
agents/openai.yaml
assets/skill-optimizer.example.json
references/validation-profiles.md
references/frozen-evaluations.md
references/importer-threat-model.md
```