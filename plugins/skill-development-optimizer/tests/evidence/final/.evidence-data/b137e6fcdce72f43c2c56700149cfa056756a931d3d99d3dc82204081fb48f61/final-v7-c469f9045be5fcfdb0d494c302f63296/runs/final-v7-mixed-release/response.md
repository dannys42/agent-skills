Selected profile: **Full**.

Reason: this is a release and spans behavior (`SKILL.md`), content (`references/`), executable production code (`scripts/`), and metadata/packaging (marketplace manifests). Deterministic classification also reported mixed categories and unknown paths, independently requiring Full.

Validation plan:

1. State the gate up front: stop on any failed or missing mandatory check, artifact/evidence mismatch, newly discovered risk category, unknown path, or need for unapproved live network access.
2. From the repository root, rerun `inspect_skill.py` and `classify_change.py` against the checked-in target configuration and intended release base. Resolve every unknown path before release; do not downgrade.
3. Run only the configured Full profile:
   `run_validation.py CONFIG full --output VALIDATION_REPORT.json`
   Do not use `--allow-network` unless importer behavior exists and live access is explicitly approved.
4. Collect Quick evidence:
   - valid plugin/skill directory structure;
   - every plugin and marketplace manifest parses;
   - marketplace entries agree on name, version, target paths, and package contents;
   - changed links resolve;
   - focused packaging/adapter tests pass.
5. Collect Content evidence:
   - reference contracts and examples are accurate;
   - attribution and source links are present and verifiable;
   - originality checks pass.
6. Collect executable-tooling evidence:
   - deterministic unit/integration tests cover changed scripts, failure paths, and CLI contracts;
   - no unexpected filesystem or network dependency;
   - importer checks remain N/A unless scripts add fetching, redirects, pacing, cache/publication, locking, recovery, or comparable managed-storage behavior. If they do, read the importer threat model and add hostile-cache/filesystem tests plus an approved milestone live check.
7. After all deterministic checks pass, freeze the exact distributable with `hash_artifact.py`. Record its `sha256-length-framed-v1` digest, selected repository-relative paths, and artifact manifest.
8. Because `SKILL.md` is behavioral, initialize one evidence cohort against that exact hash. Run every declared case with a fresh agent receiving only the case prompt and frozen skill. Preserve prompt, verbatim response, generated run ID, separately reported files-read evidence, and every declared rubric boolean.
9. Complete, verify, and summarize the cohort with `manage_evidence.py`. Keep exactly one headline cohort. Any distributable byte change makes it historical and requires rerunning every headline case.
10. Record work versus waiting time in the validation reports and summarize with `report_timing.py`.

Checks actually run for this planning request: deterministic skill inspection and change classification only. No Full validation command, release test, artifact hash, cohort, or timing report was produced.

Current evidence status: **not release-ready; validation evidence has not been generated**. Duration is therefore not yet available. The next escalation condition is any importer semantics, unresolved unknown path, failing/missing mandatory evidence, artifact mutation after hashing, mixed cohort, or required live-network access.

Relative skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`