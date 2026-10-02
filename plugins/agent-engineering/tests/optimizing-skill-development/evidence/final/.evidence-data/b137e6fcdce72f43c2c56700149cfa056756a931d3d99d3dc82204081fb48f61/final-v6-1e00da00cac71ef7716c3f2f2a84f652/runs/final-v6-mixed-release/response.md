Selected profile: `full`.

Inspection found 3 marketplace adapters, 4 plugin manifests, `SKILL.md`, 3 references, scripts, and tests. Classification reported `behavior`, `content`, `metadata`, `production`, `tests`, and `unknown`; a new release plus mixed/unknown paths requires Full. Managed evidence-store publication/locking/recovery makes the importer filesystem profile applicable.

Validation plan:

1. Preserve RED evidence before accepting the changes:

   - Behavioral skill cases must show baseline failures against the prior artifact.
   - Every script behavior change must have a focused test that failed for the expected reason before implementation.
   - Missing baseline evidence blocks release.

2. Re-run `inspect_skill.py` and `classify_change.py` from the repository root against the checked-in configuration after the final diff. Stop if unknown paths remain unexplained or a new category appears.

3. Ensure the configured `full` profile declares coverage for all mandatory surfaces. The current configuration exposes only `optimizer-tests`; if that suite does not cover every item below, add focused commands to the configuration before validation. Run checks only through:

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
     plugins/skill-development-optimizer/skill-optimizer.example.json full \
     --output VALIDATION_REPORT.json
   ```

4. Required Full-profile checks:

   - Quick: plugin structure; JSON/YAML validity; manifest and marketplace consistency across all adapters; changed links; focused packaging tests.
   - Content: content contracts, example accuracy, attribution/source links, and originality.
   - Behavior: trigger/selector/workflow/stopping behavior evaluated with fresh cases and a declared rubric.
   - Importer/storage: deterministic hostile-filesystem tests for traversal, links/nonregular objects, ancestor replacement, boundary anchoring, interrupted publication, cleanup ownership, closed handles, and unsupported operations.
   - Network pacing, redirects, and a live check are `not applicable` if there is no external acquisition. If acquisition exists, add deterministic transport tests and require approval for one explicit, restricted live milestone.

5. After deterministic checks pass, freeze the exact distributable:

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
     plugins/skill-development-optimizer/skill-optimizer.example.json \
     --json --output ARTIFACT.json
   ```

   Record the `sha256-length-framed-v1` hash and selected relative files. Any distributable-byte change invalidates the cohort and requires all headline cases to restart.

6. Initialize one headline cohort from predeclared cases and rubric. Run every case with a fresh agent given only its prompt and frozen skill. Capture prompt, generated run ID, verbatim response, separately reported files-read list, and every rubric boolean. Complete, verify, and summarize through `manage_evidence.py`; retain older cohorts only as historical evidence.

7. Record work time versus waiting time and summarize it with `report_timing.py`.

Release evidence should contain:

- Inspection and classification JSON
- Full validation report and focused test logs
- RED-to-GREEN evidence for script and behavioral changes
- Manifest/marketplace consistency results
- Artifact identity JSON
- Declared cases and rubric
- One verified, complete headline cohort
- Per-run prompts, responses, run IDs, and files-read reports
- Threat-to-test mapping, with network items explicitly marked applicable or not applicable
- Work/wait duration report

Stopping criteria: stop on any failed or missing mandatory check, unexplained path, evidence/artifact mismatch, incomplete cohort, distributable-byte change, newly mixed risk, or need for unapproved live network access. Do not report unavailable checks as passing.

Current status: inspection and classification completed; validation, artifact freezing, cohort evidence, and duration measurement remain pending.

Separate relative skill files actually read:

```text
SKILL.md
assets/skill-optimizer.example.json
references/validation-profiles.md
references/frozen-evaluations.md
references/importer-threat-model.md
```