Validation plan

- Selected profile: `behavior`, assuming the isolated patch changes only the skill trigger description and mandatory recommendation workflow.
- Risk reasons:
  - Trigger text changes discovery and selection.
  - A mandatory recommendation workflow changes required behavior and judgment.
- Deterministic inspection found a valid configured target. The current working-tree classification returned `full` because many unrelated categories and unknown paths are present. Before validating the actual patch, rerun classification against a clean base containing only the intended edit. Retain `behavior` only if that isolated result is behavioral-only; otherwise escalate to `full`.

Stopping criteria, declared before validation:

- Stop if classification finds mixed categories, importer changes, unknown paths, or release scope.
- Stop on any failed or missing configured mandatory check.
- Stop if the artifact changes after hashing, or evidence refers to a different artifact/cohort.
- Stop on incomplete runs, prompt/rubric mismatches, undeclared rubric keys, or mixed cohorts.
- Stop before any unapproved network access. None is currently needed because the configured command declares `network: false`.
- Do not report behavioral validation as passing while the fresh-agent evaluator is unavailable.

Execution sequence:

1. Before editing, use fresh-agent baseline cases against the old skill, including positive trigger, negative/non-trigger, ambiguous selector, and mandatory-workflow pressure cases. This is currently blocked by evaluator unavailability; do not substitute the current context or fabricate a baseline.
2. Make the minimal skill edit, then rerun:
   - `inspect_skill.py <config> --json`
   - `classify_change.py <config> --base <clean-base> --json`
3. Run only the configured `behavior` checks:
   - `run_validation.py <config> behavior --output <validation-report.json>`
   - In this configuration, the sole command is `optimizer-tests`; do not add content/importer/full checks unless classification escalates.
4. After deterministic checks pass, freeze the exact distributable and create its `sha256-length-framed-v1` identity:
   - `hash_artifact.py <config> --json --output <artifact.json>`
5. Declare case prompts and rubric before cohort initialization. Include trigger inclusion/exclusion and mandatory-workflow compliance. Initialize one headline cohort with `manage_evidence.py init`.
6. While the evaluator remains unavailable, leave the cohort incomplete and report fresh-agent evidence as unavailable—not failed and not passed.
7. Once restored, run every declared case with a fresh agent receiving only the case prompt and frozen skill. Capture:
   - case prompt
   - evaluator-owned run ID
   - verbatim response
   - files-read report in a separate field/file
   - every declared rubric boolean
8. Set `files_read_kind` to `agent-reported`. Preserve the report verbatim and state that it does not prove OS access, tool invocation, or complete context isolation. Do not relabel it as independently observed.
9. Complete, verify, and summarize with `manage_evidence.py complete`, `verify`, and `summarize`. Any byte change to the distributable makes the cohort historical and requires rerunning all headline cases.
10. Record work versus evaluator-waiting time and summarize it with `report_timing.py`.

Current evidence status: deterministic planning inspection/classification only; no validation suite or frozen cohort was run. Behavioral evidence is incomplete because the mandatory fresh-agent evaluator is unavailable. No artifact identity or passing headline result should be reported yet.

Relative skill files actually read

- `SKILL.md`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`

I did not read `references/importer-threat-model.md`, because importer risk is not applicable to the isolated requested change.