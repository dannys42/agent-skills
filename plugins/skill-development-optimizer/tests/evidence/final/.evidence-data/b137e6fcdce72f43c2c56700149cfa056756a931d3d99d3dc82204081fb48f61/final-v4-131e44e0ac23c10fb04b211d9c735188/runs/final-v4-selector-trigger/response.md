## Validation plan

The minimum semantic profile is **Behavior** because both the trigger description and mandatory recommendation workflow can change discovery, selection, and required agent actions. Formal profile selection must still wait for deterministic inspection/classification; a lower path-based result cannot override this semantic risk. Escalate to **Full** if inspection finds mixed categories, unknown paths, or additional behavioral/importer/content changes.

Stopping criteria, declared before checks:

- Stop on any failed or missing mandatory check.
- Stop on artifact/evidence hash mismatch, mixed cohorts, or incomplete fresh-agent runs.
- Stop if changed paths are unknown or introduce another risk category.
- Stop if validation needs unapproved network access.
- Never report the unavailable evaluator as passing.

Planned sequence:

1. Create or locate the checked-in target configuration. If absent, copy `assets/skill-optimizer.example.json` and set repository-relative target, validation command, and evaluation paths.
2. Run from the repository root:
   - `inspect_skill.py CONFIG --json`
   - `classify_change.py CONFIG --base BASE --json`
3. Before editing, declare baseline cases and rubric. Include:
   - clear positive trigger cases;
   - paraphrased and indirect trigger cases;
   - close negative/non-trigger cases;
   - competing-skill or ambiguous-selection cases;
   - cases requiring the mandatory recommendation workflow;
   - pressure cases encouraging omission, reordering, or shortcutting of that workflow;
   - missing-prerequisite and required-stop cases.
4. Run those cases against the unchanged skill with fresh agents to establish RED evidence. The configured fresh-agent evaluator is currently unavailable, so this step is blocked. Do not substitute the current context, reuse an agent, or author the behavior change before obtaining the required baseline. Restore the configured evaluator or approve an equivalent fresh, isolated evaluation surface first.
5. After the baseline exists, make the smallest skill edit that addresses the observed failures.
6. Run only checks declared by the configured `behavior` profile using `run_validation.py CONFIG behavior --output REPORT`. Record exact commands, exit statuses, tool versions, warnings, and changed-path classification.
7. After deterministic checks pass, hash the exact distributable artifact with `hash_artifact.py`. Record the `sha256-length-framed-v1` manifest and artifact hash.
8. Declare final cases and rubric before cohort initialization. Initialize exactly one headline cohort against that artifact hash with `manage_evidence.py init`.
9. Run every headline case with a separate fresh agent receiving only the case prompt and frozen skill. Capture:
   - case prompt;
   - verbatim response;
   - cohort-owned run ID;
   - files-read report, separately;
   - every declared boolean rubric result.
10. Because file reads are only self-reported, set `files_read_kind` to `agent-reported` and preserve the report verbatim. Explicitly state that it does not prove filesystem access, tool invocation, complete context isolation, or exhaustive reading. If independent proof is required, add separately labeled instrumentation rather than upgrading the self-report.
11. Complete, verify, and summarize the evidence with `manage_evidence.py`. Any distributable-byte change makes the cohort historical and requires restarting every headline case; never aggregate results across hashes.
12. Record work versus waiting time with `report_timing.py`.

Current evidence status: **incomplete/blocked**. No behavior validation has been run, no artifact has been frozen, and no headline cohort can be initialized while the configured fresh-agent evaluator is unavailable. No unavailable check counts as passed.

## Skill files actually read

Relative to `plugins/skill-development-optimizer/skills/optimizing-skill-development/`:

```text
SKILL.md
references/validation-profiles.md
references/frozen-evaluations.md
```
