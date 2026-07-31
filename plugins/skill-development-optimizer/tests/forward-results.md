# Frozen Forward Evaluation Results

## Headline result

Exactly one complete headline cohort, `final-v10`, evaluated one byte-identical
artifact. Strict scoring passed 39 of 40 declared judgments (five cases by
eight rubric items). The sole failure was
`importer-cache.unnecessary_checks_avoided`: that agent inspected optimizer
script excerpts and generated then removed graph artifacts that were not needed
to answer the plan-only scenario. The response is preserved verbatim below.

- Algorithm: `sha256-length-framed-v1`
- Digest: `c8dca4708fb78094c710fe9c6a10a9e8c88522678f5a35aadcce6f76ce4841cf`
- Declared prompts: `plugins/skill-development-optimizer/tests/evidence/final/cases.json`
- Files-read kind: `agent-reported` for every run. These lists are evidence,
  not independent instrumentation; they do not prove operating-system access,
  tool invocation, complete context isolation, or exhaustive reading.

All five agents ran sequentially. The artifact digest was checked between
cases; every run began against identical bytes. No semantic retries were made.

## Reproduction

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py verify \
  plugins/skill-development-optimizer/tests/evidence/final/evidence.json \
  plugins/skill-development-optimizer/tests/evidence/final/cases.json \
  plugins/skill-development-optimizer/tests/evaluation-rubric.json --json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py summarize \
  plugins/skill-development-optimizer/tests/evidence/final/evidence.json \
  plugins/skill-development-optimizer/tests/evidence/final/cases.json \
  plugins/skill-development-optimizer/tests/evaluation-rubric.json --json
```

## Runs and judgments

| Case | Run ID | Score |
|---|---|---:|
| metadata-only | `final-v10-metadata-only` | 8/8 |
| reference-attribution | `final-v10-reference-attribution` | 8/8 |
| selector-trigger | `final-v10-selector-trigger` | 8/8 |
| importer-cache | `final-v10-importer-cache` | 7/8 |
| mixed-release | `final-v10-mixed-release` | 8/8 |

## Historical cohorts and aborted attempts

- `final-v4` remains valid historical evidence at 40/40 for digest
  `213045c54c84e41f2917cd969799d924c52947e683bd095ca3ea7dae22adbfd1`.
- `final-v5` and `final-v6` preserve earlier plan-only failures.
- `final-v7` is historical at 39/40 for digest
  `3cd14d50ac045d66fef700fc51e10a249a3eae6b7136fe9da7a25f3a16bc7635`.
- V8 was aborted before a valid cohort. V9 was invalidated because an agent
  edited the frozen artifact while another case was running. Neither attempt
  is evidence; both unpublished drafts were removed.
- `final-v10` is the sole complete headline and matches the current
  distributable.

The pre-skill RED observations remain in `baseline-results.md`; they are
authoring evidence, not a frozen cohort.

## Exact headline prompts and verbatim responses

### metadata-only

#### Exact prompt

````text
Change only agents/openai.yaml display text in a portable skill plugin. Plan the validation and evidence needed.

Use the skill directory plugins/skill-development-optimizer/skills/optimizing-skill-development from the repository-root working directory. Report the validation plan and
write a separate list of relative skill files you actually read.
````

#### Verbatim response

````text
Validation plan:

- Selected profile: **Quick**, assuming the isolated diff changes only UI-facing text in `agents/openai.yaml`.
- Preflight evidence:
  - `inspect_skill.py --json` confirms the configured skill exists and includes both `SKILL.md` and `agents/openai.yaml`.
  - Re-run `classify_change.py --json` on the isolated patch; require metadata-only classification.
- Run the configured Quick profile through `run_validation.py`. Its sole configured check is `optimizer-tests`, with networking disabled and a 120-second timeout.
- Review the final diff to confirm only `agents/openai.yaml` display text changed.
- Confirm YAML remains parseable, the existing interface keys remain present, and the revised text accurately reflects `SKILL.md`.
- Changed-link validation is not applicable because no link changes are proposed.
- No frozen behavioral artifact, evaluation cohort, importer threat checks, live network check, or distributable hash is needed for Quick.
- Stop on a failed/missing mandatory check, YAML/schema failure, any additional changed path, or wording that affects triggering, selection, workflow, or judgment. Such behavioral or mixed scope escalates to Behavior or Full.

Evidence status: planning only; no validation run or evidence bundle generated. Expected validation runtime is bounded by the configured 120-second test timeout.

Classifier caveat: the current worktree contains unrelated behavioral, content, production, test, and unknown changes, so its aggregate classifier output is Full. Quick is valid only after classification against an isolated metadata-only diff.

No edit was made because replacement wording was not provided and the target skill instructs validation-plan requests not to edit.

Relative skill files actually read:

- `SKILL.md`
- `agents/openai.yaml`
- `references/validation-profiles.md`
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
agents/openai.yaml
references/validation-profiles.md
````

### reference-attribution

#### Exact prompt

````text
Correct an attributed reference and its code example without changing SKILL.md. Plan the validation and evidence needed.

Use the skill directory plugins/skill-development-optimizer/skills/optimizing-skill-development from the repository-root working directory. Report the validation plan and
write a separate list of relative skill files you actually read.
````

#### Verbatim response

````text
Selected profile: `content`.

The correction changes reference accuracy, attribution/provenance, and example correctness without changing behavioral instructions. The shared worktree classifier currently sees unrelated mixed/unknown changes, so classification must be rerun against the intended base after isolating the correction.

Validation plan:

1. Record the base commit and intended reference/example paths.
2. After editing, run `inspect_skill.py` and `classify_change.py --base <base>`. Confirm only content paths changed and `SKILL.md` is unchanged.
3. Run only the configured `content` profile through `run_validation.py`, preserving its JSON report.
4. Collect:
   - Quick evidence: structure, manifests/configuration, changed links, focused tests.
   - Content evidence: content contracts, exact runnable-example accuracy, attribution and authoritative source agreement, originality/provenance.
5. Record commands, configuration, base/head identities, changed paths, tool version, exit status, warnings/output, duration, and commit/diff artifact identity.
6. Skip behavioral artifact freezing/evaluations, importer checks, live-network checks, and unrelated repository gates unless classification escalates.
7. Stop on any failed or missing mandatory check, unverifiable source, inaccurate/non-runnable example, artifact mismatch, unexpected `SKILL.md` change, mixed/unknown category, or unapproved network requirement.

No validation suite was run because this was plan-only work. No files were changed.

Relative skill files actually read:

```text
SKILL.md
references/validation-profiles.md
assets/skill-optimizer.example.json
```
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
references/validation-profiles.md
assets/skill-optimizer.example.json
````

### selector-trigger

#### Exact prompt

````text
Change a skill's trigger description and mandatory recommendation workflow. The configured fresh-agent evaluator is unavailable and files read can only be self-reported. Plan the validation and evidence needed.

Use the skill directory plugins/skill-development-optimizer/skills/optimizing-skill-development from the repository-root working directory. Report the validation plan and
write a separate list of relative skill files you actually read.
````

#### Verbatim response

````text
Validation plan

- Proposed minimum profile: `behavior`, because both trigger-description and mandatory-workflow changes affect discovery and agent behavior. They remain one risk category, so `full` is unnecessary unless other categories or unknown paths enter the patch.
- Current precondition: no target `skill-optimizer*.json` configuration was found. Before formal profile selection, create the checked-in repository-relative config from the example, then run `inspect_skill.py --json` and `classify_change.py --json`. Until then, label `behavior` as the semantic plan, not a completed deterministic classification.
- Before editing, define baseline pressure cases covering:

  - New positive trigger phrasings.
  - Near-miss cases that should not trigger.
  - Requests where the mandatory recommendation must occur.
  - Pressure to skip, soften, or defer the recommendation.
  - Unavailable evaluator and missing-evidence handling.

- Declare the rubric before evaluation. Suggested keys include correct trigger/non-trigger decision, mandatory recommendation present at the required point, no workflow shortcut, correct stopping behavior when evidence is missing, required files reported as read, and unrelated references avoided.
- Run configured deterministic checks first: structure/frontmatter, metadata consistency with `agents/openai.yaml`, focused tests, inspection, and classification. Run only checks declared by the selected `behavior` profile.
- Freeze and hash the exact distributable artifact after deterministic checks. Initialize one cohort tied to that hash; any distributable-byte change makes the cohort historical and requires restarting all headline cases.
- The fresh-agent evaluator is unavailable, so fresh-case evidence cannot currently be produced. Record every fresh case as missing/unrun, stop the behavioral validation, and do not report the change as passing or fully validated. Deterministic success alone is insufficient.
- When the evaluator becomes available, give each fresh agent only the frozen skill and case prompt. Capture the prompt, evaluator-owned run ID, verbatim response, separate verbatim files-read report, and complete boolean rubric.
- Since files read are only self-reported, set `files_read_kind` to `agent-reported`. Treat that as evidence, not independent instrumentation; make no claims about OS access, tool invocation, complete isolation, or exhaustive context visibility.
- Complete, verify, and summarize the cohort through `manage_evidence.py`. Do not aggregate across hashes or mix historical and headline cohorts.
- Report selected profile, semantic and deterministic classification evidence, checks run/skipped, artifact hash, incomplete evaluator status, work/wait duration, and the escalation condition.
- Stop on any failed/missing mandatory check, artifact mismatch, incomplete run, rubric/schema mismatch, newly mixed category, unknown path, or need for unapproved network access.

Relative skill files actually read

```text
SKILL.md
agents/openai.yaml
assets/skill-optimizer.example.json
references/frozen-evaluations.md
references/validation-profiles.md
```

No files were changed.
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
agents/openai.yaml
assets/skill-optimizer.example.json
references/frozen-evaluations.md
references/validation-profiles.md
````

### importer-cache

#### Exact prompt

````text
Change retry pacing and cache writes in a skill's external research importer. Plan the validation and evidence needed.

Use the skill directory plugins/skill-development-optimizer/skills/optimizing-skill-development from the repository-root working directory. Report the validation plan and
write a separate list of relative skill files you actually read.
````

#### Verbatim response

````text
Validation plan

- Provisional minimum profile: `importer`, because retry pacing and managed cache writes are both explicitly importer risks.
- Final profile selection requires the actual importer target/config. The available optimizer configuration targets the optimizer skill itself, so its current `full` classification does not classify the hypothetical external-research importer.
- Before implementation, run `inspect_skill.py` and `classify_change.py` against the importer’s configuration. Escalate to `full` for mixed categories, unknown paths, or incomplete inspection.

Stopping criteria, declared before validation:

- Stop on any failed or missing mandatory check.
- Stop on artifact/hash mismatch, an unknown or newly mixed change category, or unsupported secure filesystem operations.
- Do not perform live network validation without explicit approval.

Checks and evidence:

1. Use TDD: add each deterministic regression test first and confirm the expected RED failure.
2. Retry pacing with a fake monotonic clock and scripted transport:
   - Minimum interval covers every outbound attempt, including retries, redirects, and attempts following failures.
   - A shorter `Retry-After` cannot reduce the minimum; a longer value extends it.
   - Retry and redirect counts remain bounded.
3. Request-policy regression coverage:
   - Redirects must remain HTTPS on the exact allowed origin and path family.
   - Reject userinfo, alternate ports, lookalike hosts, encoded escapes, and cross-family redirects.
4. Hostile-cache coverage using temporary directories and injected failures:
   - Reject traversal, symlinks, hardlinks, FIFOs, devices, and directories.
   - Ancestor/root replacement cannot redirect reads, logs, staging, or publication.
   - Temporary files are exclusive and anchored to a retained directory boundary.
   - Interrupted writes expose either the previous valid manifest/page pair or the new pair, never a mixture.
   - Cleanup removes only owned objects and preserves unowned lookalikes.
   - Closed handles and unsupported secure operations fail deterministically.
5. Run only commands configured for the selected `importer` profile through `run_validation.py`; avoid unrelated whole-repository, content, and behavioral evaluations.
6. Hash the final distributable with `hash_artifact.py`. Preserve the exact command, commit SHA, artifact hash, tool versions, exit status, concise output, threat-to-test mapping, and work/wait timing.
7. At an explicit milestone only, request approval for one small, paced live check restricted to the configured origin. Network unavailability must not invalidate deterministic importer evidence.

Evidence status: planned; no importer implementation or mandatory validation was run. `frozen-evaluations.md` was intentionally skipped because this is importer work, not a behavioral-skill evaluation.

Relative skill files actually read

- `SKILL.md`
- `assets/skill-optimizer.example.json`
- `references/validation-profiles.md`
- `references/importer-threat-model.md`
- `scripts/classify_change.py` (matched excerpts only)
- `scripts/optimizer_config.py` (matched excerpt only)

A temporary `scripts/graphify-out/` directory generated during inspection was removed; it contained only reproducible graph artifacts.
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
assets/skill-optimizer.example.json
references/validation-profiles.md
references/importer-threat-model.md
scripts/classify_change.py
scripts/optimizer_config.py
````

### mixed-release

#### Exact prompt

````text
Release a new plugin after changing SKILL.md, references, scripts, and marketplace manifests. Plan the validation and evidence needed.

Use the skill directory plugins/skill-development-optimizer/skills/optimizing-skill-development from the repository-root working directory. Report the validation plan and
write a separate list of relative skill files you actually read.
````

#### Verbatim response

````text
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
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
assets/skill-optimizer.example.json
references/validation-profiles.md
references/frozen-evaluations.md
references/importer-threat-model.md
````
