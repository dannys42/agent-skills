Selected profile: `full`.

Reason: this is a new plugin release spanning behavioral instructions (`SKILL.md`), content/references, production scripts, and marketplace metadata. The required inspector found the configured skill, three references, production scripts, four plugin manifests, and tests. The classifier returned `full` with behavior, content, metadata, production, tests, and unknown paths. No downgrade is justified.

Validation and evidence plan:

1. Before validation, remove or exclude generated `__pycache__`, `.pyc`, and temporary evidence outputs from the candidate release. Rerun `inspect_skill.py` and `classify_change.py` against the intended release base. Any remaining unknown path blocks release.
2. Declare stopping criteria before checks: stop on any failed or unavailable mandatory check, artifact/evidence mismatch, unknown path, newly discovered risk category, mixed evaluation cohort, or required live-network check lacking approval.
3. Run only the configured Full profile through:
   `run_validation.py CONFIG full --output TIMING.json`

   The current configuration declares the focused optimizer unit suite for Full. Do not add an unrelated repository-wide suite.
4. Quick/package checks:
   - Validate plugin directory structure.
   - Parse and validate all marketplace manifests.
   - Confirm plugin IDs, versions, skill paths, and release metadata agree across Claude, Codex, Cursor, and Gemini manifests.
   - Check links and installation prose changed by the patch.
5. Content checks:
   - Verify reference contracts, examples, attribution, source links, and originality.
   - Treat unverifiable examples or missing attribution as failures.
6. Script checks:
   - Preserve RED/GREEN evidence for each changed executable behavior.
   - Run focused unit/integration tests covering success, error, malformed-input, deterministic-output, and filesystem-boundary behavior.
   - Apply the Importer profile only if the changed scripts perform external acquisition or cache management. If applicable, cover every threat in `importer-threat-model.md`; request approval before any explicit live-network milestone. Otherwise record Importer and live-network checks as not applicable, not passed.
7. Behavioral evidence:
   - Finish deterministic checks first.
   - Hash the exact configured distributable with `hash_artifact.py`; record algorithm, digest, file list, and release commit SHA.
   - Declare cases and rubric before initializing one headline cohort.
   - Initialize evidence with `manage_evidence.py init`.
   - Run each case in a fresh agent receiving only its prompt and frozen skill.
   - Capture prompt, preserved run ID, verbatim response, separately reported files-read evidence, and every rubric boolean.
   - Publish with `complete`, then run `verify` and `summarize`.
   - If any hashed distributable byte changes, retain the old cohort only as historical evidence and rerun every headline case against a new cohort. Never aggregate across artifact versions.
8. Pin packaging evidence separately to the same commit SHA because the current behavioral artifact configuration hashes `SKILL.md`, `agents/**/*.yaml`, references, and scripts, but not parent-level marketplace manifests.
9. Summarize timing with `report_timing.py`, separating work from waiting time.
10. Release report must state: Full profile, risk reasons, exact checks run and skipped, artifact digest and commit, cohort/evidence status, durations, manifest/package evidence, and the next escalation condition.

Current evidence status: inspection and classification were performed; validation, frozen-artifact hashing, cohort execution, and timing evidence have not been run. Therefore none should be reported as passing yet.

Relative skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`
- `references/importer-threat-model.md`