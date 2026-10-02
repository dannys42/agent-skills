Selected profile: `full`.

Deterministic inspection found the configured skill, three marketplace adapters, four plugin manifests, 184 tests, and the optimizer configuration. Classification returned `full` with `behavior`, `content`, `metadata`, `production`, `tests`, and `unknown` categories. A release plus mixed SKILL/reference/script/manifest changes independently requires Full.

Validation plan:

1. Establish stopping criteria before validation: stop on any mandatory failure or omission, unresolved unknown path, artifact/evidence mismatch, mixed cohort, distributable edit after freezing, or need for unapproved network access.
2. Resolve classifier noise and unknowns first. Remove generated `__pycache__`/`.pyc` from release inputs, inspect every remaining unknown path, and rerun `inspect_skill.py` and `classify_change.py` from the repository root. Do not downgrade.
3. Confirm TDD provenance:
   - Skill behavior changes have genuine pre-edit RED/baseline evidence.
   - Script behavior has tests that failed for the intended reason before implementation.
   - Do not fabricate retroactive RED evidence.
4. Run only the configured Full gate:
   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
     plugins/skill-development-optimizer/skill-optimizer.example.json \
     full \
     --output <full-validation-report.json>
   ```
   The configured command runs the optimizer unit/integration suite once. Capture exact command, commit SHA, Python/tool versions, exit status, warnings, full temporary log, and concise machine-readable report.
5. Require the Full union’s evidence:
   - Quick: skill/plugin structure; all marketplace and plugin JSON parse; adapter source/version/name parity; changed links; focused packaging tests.
   - Content: content contracts, example accuracy, attribution/source-link verification, and originality checks. Missing attribution or unverifiable examples fail.
   - Behavior: triggering, profile selection, mandatory workflows, judgment, escalation, and stopping behavior.
   - Importer: deterministic hostile-filesystem tests for the managed evidence store—traversal, symlinks, hardlinks, FIFOs/devices/directories, ancestor replacement, retained-boundary anchoring, interrupted publication, cleanup ownership, closed handles, and unsupported operations.
   - Network threats/live checks are `not applicable`, not passing, because this target has no external acquisition. If acquisition appears, stop and request approval for a small milestone live check.
6. After deterministic checks pass, freeze and hash the exact distributable:
   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
     plugins/skill-development-optimizer/skill-optimizer.example.json \
     --json --output <artifact.json>
   ```
   Record the `sha256-length-framed-v1` identity and selected files.
7. Initialize exactly one headline cohort against that hash. Run every declared case with a fresh agent receiving only its prompt and frozen skill. Capture prompt, verbatim response, run ID, files-read report separately, and every declared boolean rubric result.
8. Complete, verify, and summarize with `manage_evidence.py`. Reject incomplete runs, prompt/rubric mismatch, duplicate IDs, missing file references, artifact mismatch, or mixed cohorts. Any distributable-byte change makes the cohort historical and requires rerunning every headline case.
9. Use `report_timing.py` to report work versus waiting time. Release only when the Full report passes, evidence verifies against the current artifact hash, manifests agree, the working tree contains no generated junk, and evidence contains no personal/local identifiers.

Evidence status: inspection and classification were run; the Full validation gate and frozen cohort were not run in this planning pass. Existing evidence must not be reused until its artifact hash and cohort verify against the final distributable.

Relative target-skill files actually read:

- `SKILL.md`
- `assets/skill-optimizer.example.json`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`
- `references/importer-threat-model.md`
