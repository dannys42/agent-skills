Selected profile: `full`.

Reason: this is a release with mixed Quick, Content, Behavior, and production-script risks. The current deterministic classification also reports unknown paths, which independently requires `full`. Importer validation applies because this plugin manages durable evidence storage; network threats are not applicable unless the final scripts perform external acquisition.

### Validation and evidence plan

1. Establish the final validation target.

   - Copy `assets/skill-optimizer.example.json` to a checked-in, non-example repository configuration.
   - Configure repository-relative target, evaluation files, and commands.
   - Ensure the `full` profile declares every applicable check below.
   - Remove generated `__pycache__`/`.pyc` files from the release diff.

2. Freeze scope and stopping criteria.

   Stop immediately for any mandatory failure or omission, unknown final path, artifact/evidence hash mismatch, mixed evaluation cohort, newly discovered risk, or required unapproved network access. Do not release until all mandatory checks are present and passing.

3. Rerun deterministic inspection and classification on the final diff:

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py --json CONFIG.json
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py --json --base RELEASE_BASE CONFIG.json
   ```

   Retain `full`; no downgrade is justified for a new mixed-category release.

4. Run focused deterministic checks before the full gate.

   - Quick: plugin structure; JSON/YAML parsing and schemas; cross-marketplace identity/version/path consistency; changed links; local installation/discovery smoke tests.
   - Content: reference contracts, example accuracy, attribution, source-link validity, and originality.
   - Behavior: trigger/selector, mandatory workflow, judgment, and stopping-condition cases.
   - Scripts: focused unit and CLI integration tests, including regression tests that were observed failing before implementation where TDD evidence is expected.
   - Importer/storage: deterministic hostile-filesystem tests for traversal, symlinks, hardlinks, special files, ancestor replacement, interrupted publication, cleanup ownership, closed handles, and unsupported operations. Record the threat covered by each test.
   - If external acquisition exists, additionally test pacing, retries, redirects, URL boundaries, and injected transport failures using fake clocks/transports.

5. Run only the configured complete release gate:

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
     CONFIG.json full --output FULL_REPORT.json
   ```

   Record exact command, commit SHA, tool versions, exit status, warnings, and concise result. Do not add unrelated whole-repository checks.

6. Freeze the exact distributable after deterministic checks pass:

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
     CONFIG.json --json --output ARTIFACT.json
   ```

   Record the `sha256-length-framed-v1` identity. Marketplace/package validation and the behavioral artifact hash are distinct evidence surfaces; both must resolve to the same intended release revision.

7. Create one fresh behavioral evaluation cohort.

   - Predeclare cases and rubric.
   - Initialize against `ARTIFACT.json`.
   - Give each fresh agent only its case prompt and frozen skill.
   - Capture prompt, verbatim response, run ID, files read, files-read provenance, and every rubric boolean.
   - Complete, verify, and summarize through `manage_evidence.py`.
   - If any distributable byte changes, archive the cohort as historical, rehash, and rerun every headline case. Never aggregate across artifact hashes.

8. Capture timing:

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/report_timing.py \
     --json FULL_REPORT.json
   ```

   Report work and waiting time separately.

9. Release only when the final commit has:

   - Passing focused and configured `full` checks.
   - Valid marketplace/package manifests.
   - One complete, verified, hash-matched headline cohort.
   - Reproducible command/version/SHA attestations.
   - No unsanitized personal paths or local identifiers.
   - No post-attestation executable changes.

A live network check is skipped unless the final scripts acquire external resources. If acquisition exists, it becomes an explicit approval-gated milestone after deterministic tests.

Current evidence status: inspection completed; current classification is `full`. No complete validation gate or frozen release cohort was run for this planning request. Artifact identity and duration are therefore pending.

Next escalation condition: any final unknown path, external acquisition, missing mandatory configured check, or distributable edit after cohort initialization.

### Relative skill files actually read

```text
SKILL.md
assets/skill-optimizer.example.json
references/validation-profiles.md
references/frozen-evaluations.md
references/importer-threat-model.md
```