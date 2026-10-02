## Validation plan

**Profile: `full`.** Deterministic inspection found the skill, four plugin manifests, 18 script entries, and 181 tests. Classification reported `behavior`, `content`, `metadata`, `production`, `tests`, and `unknown`. A new plugin release, mixed categories, and unknown paths each independently require `full`.

Applicable risks:

- **Quick:** marketplace/plugin manifests, adapter metadata, package structure, paths, JSON/YAML, changed links.
- **Content:** changed references, examples, attribution, source accuracy, originality.
- **Behavior:** any `SKILL.md` edit may alter triggering, selection, workflow, judgment, or stopping criteria.
- **Importer:** applicable because the scripts manage durable evidence publication, locking, and recovery. There is no external acquisition in the described scope, so network threats and live importer checks are **not applicable**, not “passing.”
- **Executable tooling:** script changes require test-first evidence under TDD.

### Release gate sequence

1. **Declare stopping criteria before validation.** Stop on any failed or missing mandatory check, unresolved unknown path, unapproved live network requirement, artifact/evidence mismatch, mixed evaluation cohort, or distributable change after freezing.

2. **Clean and classify the exact release diff.**
   - Remove generated `__pycache__`, `.pyc`, transient `.evidence-data`, and similar files from the release package; ignore them where appropriate.
   - Resolve every `unknown` path explicitly.
   - Re-run from repository root:

     ```bash
     python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py \
       plugins/skill-development-optimizer/skill-optimizer.example.json --json

     python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py \
       plugins/skill-development-optimizer/skill-optimizer.example.json --base <release-base> --json
     ```

3. **Make the configured `full` profile complete.** The current configuration maps every profile only to `optimizer-tests`; that alone does not demonstrate all mandatory evidence. Before release, declare focused commands covering:
   - Skill structure/frontmatter and `agents/openai.yaml` consistency.
   - JSON/YAML/schema parsing for `.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, Gemini, and marketplace manifests.
   - Manifest identity/version/path parity and referenced-file existence.
   - Local plugin packaging/install/discovery smoke tests.
   - Changed links. If reachability requires live network access, pause for approval.
   - Content contracts, executable example accuracy, attribution/source checks, and originality.
   - Deterministic tests for every changed script.
   - Managed-store threats: traversal, symlinks, hardlinks, FIFOs/devices/directories, ancestor replacement, retained-boundary I/O, interrupted publication, cleanup ownership, closed handles, and unsupported operations.

4. **Preserve TDD evidence.**
   - For scripts: retain the failing test output from before implementation, expected failure reason, passing focused test, and passing regression run.
   - For skill behavior: retain pre-change/skill-absent RED cases, then run the same class of cases against the new skill. A post-hoc passing test does not replace missing RED evidence.

5. **Run only the configured union.**

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
     plugins/skill-development-optimizer/skill-optimizer.example.json full \
     --output <evidence-dir>/full-validation.json
   ```

   Do not add unrelated whole-repository checks. Do not use `--continue-on-failure` for the release gate.

6. **Freeze the behavioral artifact after deterministic checks pass.**

   ```bash
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
     plugins/skill-development-optimizer/skill-optimizer.example.json \
     --json --output <evidence-dir>/artifact.json
   ```

   Record the `sha256-length-framed-v1` identity. Also record the release commit and packaged-plugin checksum because the configured behavioral hash targets the skill directory rather than all marketplace manifests.

7. **Create one fresh behavioral cohort.**
   - Freeze cases and rubric before initialization.
   - Cover triggering/non-triggering, selector boundaries, mandatory workflow, stopping behavior, mixed-release classification, content handling, and importer/store judgment.
   - Initialize one cohort with `manage_evidence.py init`.
   - Give each fresh agent only the case prompt and frozen skill.
   - Capture prompt, verbatim response, generated run ID, files-read report, and every rubric Boolean.
   - Publish with `complete`, then run `verify` and `summarize`.
   - If any distributable byte changes, mark the cohort historical and restart every headline case. Never aggregate across artifact hashes.

8. **Record release-package evidence.**
   - Exact manifest files and versions.
   - Marketplace entry identity and ordering.
   - Package file inventory proving generated caches/evidence are excluded.
   - Local install/discovery smoke-test logs.
   - Link-check results or explicit approval-required status.
   - Validation report, artifact hash, cohort verification/summary, commit, and package checksum.

9. **Record duration.**
   - Preserve per-command work/wait timing from validation reports.
   - Summarize with:

     ```bash
     python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/report_timing.py \
       <evidence-dir>/*.json --json
     ```

10. **Release only when** all mandatory applicable checks pass, the frozen cohort verifies against the exact artifact, manifests/package agree on identity and version, no unknown paths remain, and evidence is complete.

### Current evidence status

Only deterministic preflight inspection and classification were run. No configured `full` validation, artifact hash, fresh cohort, package smoke test, or timing report was produced, so none should be reported as passing. Existing cohorts must not be reused unless their artifact hash exactly matches the final distributable.

## Relative skill files actually read

Relative to `plugins/skill-development-optimizer/skills/optimizing-skill-development/`:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`
- `references/importer-threat-model.md`
- `assets/skill-optimizer.example.json`

Required supporting skill instructions also read:

- `~/.codex/skills/.system/skill-creator/SKILL.md`
- `~/.agents/skills/writing-skills/SKILL.md`
- `~/.agents/skills/test-driven-development/SKILL.md`
