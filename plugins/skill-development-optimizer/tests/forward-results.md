# Frozen Forward Evaluation Results

## Headline result

Exactly one headline cohort, `final-v4`, evaluated one byte-identical artifact.
All 40 declared judgments passed (five cases by eight rubric items). Results
from prior artifact versions are historical and excluded from this headline.

- Algorithm: `sha256-length-framed-v1`
- Digest: `213045c54c84e41f2917cd969799d924c52947e683bd095ca3ea7dae22adbfd1`
- Declared prompts: `plugins/skill-development-optimizer/tests/evidence/final/cases.json`
- Files-read kind: `agent-reported` for every run. These lists are evidence,
  not independent instrumentation; they do not prove operating-system access,
  tool invocation, complete context isolation, or exhaustive reading.

The decoded prompt string declared in `cases.json` is exactly bound by evidence verification. The manager serializes it as UTF-8 plus one terminal newline. Managed and public prompt Markdown bytes match.

Each prompt establishes a repository-root working directory and uses only a
repository-relative skill path.

## Reproduction

Run from the repository root:

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
  plugins/skill-development-optimizer/skill-optimizer.example.json --json \
  --output plugins/skill-development-optimizer/tests/evidence/final/artifact.json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py verify \
  plugins/skill-development-optimizer/tests/evidence/final/evidence.json \
  plugins/skill-development-optimizer/tests/evidence/final/cases.json \
  plugins/skill-development-optimizer/tests/evaluation-rubric.json --json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py summarize \
  plugins/skill-development-optimizer/tests/evidence/final/evidence.json \
  plugins/skill-development-optimizer/tests/evidence/final/cases.json \
  plugins/skill-development-optimizer/tests/evaluation-rubric.json --json
```

The supported `complete` API consumed a schema-version-1 completion document
without caller-supplied run IDs. It preserved the IDs assigned by `init`.

## Runs and judgments

| Case | Run ID | correct_profile | risk_reasons_stated | mandatory_checks_present | unnecessary_checks_avoided | missing_checks_not_passed | frozen_artifact_required_when_behavioral | network_approval_explicit_when_needed | stopping_criteria_stated |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| metadata-only | `final-v4-metadata-only` | pass | pass | pass | pass | pass | pass | pass | pass |
| reference-attribution | `final-v4-reference-attribution` | pass | pass | pass | pass | pass | pass | pass | pass |
| selector-trigger | `final-v4-selector-trigger` | pass | pass | pass | pass | pass | pass | pass | pass |
| importer-cache | `final-v4-importer-cache` | pass | pass | pass | pass | pass | pass | pass | pass |
| mixed-release | `final-v4-mixed-release` | pass | pass | pass | pass | pass | pass | pass | pass |

The files-read reports below are preserved verbatim as agent-reported evidence.
They support reference-routing review but are not independent proof of
filesystem access, tool use, isolation, or completeness.

## Historical cohorts and refinements

`final` used digest
`facbd93d92da2174c1ad5f2109b106b343539ff39ad2923f38d75f1883997980`.
Strict re-scoring is 38/40: importer-cache failed
`mandatory_checks_present` and `unnecessary_checks_avoided`. It remains
historical and is excluded from the headline.

`final-v2` used digest
`8ce8e269feb5d5694c3c8662ff5d88812f89a6bb7e1ea44cd287ac46aeb4522b`.
Its rubric values total 40/40, but it is disqualified for a prompt-integrity
defect: the managed declared prompts did not include all delivered harness
instructions. Its rubric judgments remain preserved historically.

`final-v3` used digest
`1f4c4aa2bebba65cc0dc47e01a5d788cd712a8654bd5f76dec57975190f74c52`.
Its immutable stored rubric declaration totals 40/40. A later external semantic
audit scores it 37/40 because mixed-release should have
`correct_profile`, `mandatory_checks_present`, and
`unnecessary_checks_avoided` false. The stored declaration remains unchanged
as historical evidence, and the cohort is disqualified from the headline.

The v4 refinement makes the Full-profile boundary explicit. Managed persistent
evidence publication, locking, and recovery invoke Importer filesystem threats.
Network threats are not applicable without external acquisition. Ordinary
source or documentation edits are not importer work.

There were no v4 infrastructure retries: the correct repository-relative
symlink was provisioned before all five fresh runs, then removed and never
committed.

The pre-skill RED observations remain in `baseline-results.md`; they are
authoring evidence, not a frozen cohort.

## Exact headline prompts and verbatim responses

The following public prompts, responses, and separately captured files-read
lists are quoted verbatim from the headline mirrors.

### metadata-only

#### Exact prompt

````text
Change only agents/openai.yaml display text in a portable skill plugin. Plan the validation and evidence needed.

Use the skill directory plugins/skill-development-optimizer/skills/optimizing-skill-development from the repository-root working directory. Report the validation plan and
write a separate list of relative skill files you actually read.
````

#### Verbatim response

````text
Selected profile: **Quick**, conditional on an isolated diff changing only `interface.display_name` and/or `interface.short_description` in `agents/openai.yaml`. Changing `default_prompt` is behavioral and requires **Behavior** validation.

Validation plan:

1. Work from the repository root with `plugins/skill-development-optimizer/skill-optimizer.example.json`.
2. Establish a clean base containing only the intended edit. The current classifier reports **Full** because the plugin and unrelated files are untracked/mixed; that result cannot validate the isolated metadata patch.
3. Rerun deterministic inspection and classification with JSON output. Require a valid target and metadata-only/Quick classification.
4. Review the one-file diff and verify:
   - only `agents/openai.yaml` changed;
   - YAML parses and all strings remain quoted;
   - `short_description` is 25–64 characters;
   - display text accurately represents `SKILL.md`;
   - `default_prompt`, trigger metadata, instructions, references, scripts, manifests, and links are unchanged.
5. Run only the configured Quick profile:
   `python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py plugins/skill-development-optimizer/skill-optimizer.example.json quick --output <report.json>`
6. Preserve as evidence:
   - exact one-file diff;
   - inspector and classifier JSON;
   - Quick validation report, command, exit status, and tool/runtime version;
   - timing summary from `report_timing.py`;
   - base and resulting commit SHAs when available.
7. Skip artifact hashing/freezing, fresh-agent cohorts, rubric evaluations, importer/hostile-cache checks, live network checks, and whole-repository gates. They are unnecessary for isolated UI metadata.

Evidence status: inspection succeeded, but the current worktree classification is contaminated and reports Full; Quick evidence remains pending an isolated diff. No validation duration exists until the Quick report is run.

Stop and escalate if the diff is not one-file metadata-only, `default_prompt` changes semantically, classification remains Full/unknown, or any mandatory Quick check is missing or fails.

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
Validation plan

Provisional profile: `content`, because the change corrects attribution and a code example while leaving `SKILL.md` unchanged. Confirm before final selection:

1. Create or locate a repository-root optimizer configuration. Configure `content` to include:

   - Quick checks: structure, manifests/adapter JSON, changed links, focused tests.
   - Content contracts: attribution correctness, source-link validity, example accuracy, and originality.
   - A runnable syntax/typecheck/test command for the example using its declared dependency versions.

2. State stopping criteria before validation: stop on any missing or failed mandatory check, unverifiable attribution or example, artifact/evidence mismatch, unknown path, mixed risk category, an unexpected `SKILL.md` diff, or required live-network access without approval.

3. Run deterministic preflight from the repository root:

   ```sh
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py --json <config>
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py --json <config>
   ```

   Retain `content` only if inspection is complete and classification confirms content-only paths. Escalate to `full` for mixed or unknown paths.

4. Capture RED evidence before correction:

   - Add or identify a focused content-contract test that rejects the incorrect attribution.
   - Add or identify an executable example test that exposes the code defect.
   - Run both and record the expected failures. A missing test is not passing evidence.

5. Correct only the attributed reference and its example. Verify `git diff -- <target>/SKILL.md` is empty and compare its before/after checksum.

6. Validate provenance against the authoritative, version-specific source. Check author/title/location details and the changed link. Run the corrected example in a clean, deterministic environment. Check originality by comparing the correction with the source and recording whether wording/code was independently expressed or permissibly quoted. If authoritative verification requires live network access, stop and request approval.

7. Run only the configured Content profile:

   ```sh
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
     --output <evidence-path> <config> content
   ```

8. Preserve evidence containing:

   - repository commit SHA and dirty-state/diff identity;
   - optimizer configuration and hashes of changed distributable files;
   - inspect/classify JSON;
   - RED and passing rerun commands, tool versions, exit statuses, and concise logs;
   - attribution source and link-check result;
   - example runtime/typecheck result;
   - originality result;
   - explicit proof that `SKILL.md` did not change;
   - work duration versus waiting time.

9. Report skipped checks explicitly: frozen behavioral evaluations, importer threat checks, live-network checks, and the full repository gate are not applicable unless classification or uncertainty escalates. Never label them “passed.”

Files actually read

Repository-relative:

- `plugins/skill-development-optimizer/skills/optimizing-skill-development/SKILL.md`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/references/validation-profiles.md`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/assets/skill-optimizer.example.json`

Home-relative required sub-skills:

- `~/.codex/skills/.system/skill-creator/SKILL.md`
- `~/.agents/skills/writing-skills/SKILL.md`
- `~/.agents/skills/test-driven-development/SKILL.md`
````

#### Separate files-read list (`agent-reported`)

````text
plugins/skill-development-optimizer/skills/optimizing-skill-development/SKILL.md
plugins/skill-development-optimizer/skills/optimizing-skill-development/references/validation-profiles.md
plugins/skill-development-optimizer/skills/optimizing-skill-development/assets/skill-optimizer.example.json
~/.codex/skills/.system/skill-creator/SKILL.md
~/.agents/skills/writing-skills/SKILL.md
~/.agents/skills/test-driven-development/SKILL.md
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
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
references/validation-profiles.md
references/frozen-evaluations.md
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
Selected profile: `importer`.

Retry pacing and managed cache writes are both importer risks, so they do not by themselves require `full`. Structural inspection succeeded. The current classifier returned `full` only because the worktree contains unrelated untracked unknown paths; re-run classification against the isolated implementation diff. If it still reports unknown or mixed categories, retain `full`.

Validation plan:

1. Establish stopping criteria before implementation:
   - Stop for failed inspection, missing configuration/checks, unknown paths, a newly mixed category, or unapproved live-network access.
   - Stop if a RED test does not fail for the intended reason.
   - Stop on any mandatory threat without deterministic coverage, artifact/evidence mismatch, nondeterminism, or unsanitized local identifiers.

2. Follow test-first development:
   - Add focused failing tests before changing production code.
   - Use an injected monotonic clock, fake sleep, scripted transport, temporary directories, and injected filesystem failures—no real sleeps or network.

3. Validate retry pacing:
   - Assert the new pacing rule across ordinary requests, every retry, redirects, response-read failures, and immediately raised transport failures.
   - Assert attempt timestamps, not only sleep calls.
   - Verify `Retry-After` can lengthen but never shorten the configured minimum.
   - Retain bounded retry/redirect behavior and exact HTTPS origin/path enforcement.
   - Cover invalid/nonfinite `Retry-After`, exhausted retries, and response closure.

4. Validate cache writes:
   - Exercise page, manifest, catalog, and request-log writes.
   - Inject interruption at temporary creation, partial write, file flush, replacement, and directory flush boundaries.
   - Prove readers see the previous valid manifest/page pair or the new pair, never a mixed pair.
   - Verify exclusive in-boundary temporary files, correct durability ordering, and cleanup only of importer-owned staging files.
   - Re-run hostile-cache cases: traversal, symlink, hardlink, FIFO/device/directory, ancestor replacement, concurrent destination replacement, closed handles, and unsupported descriptor-relative operations.
   - Confirm failures preserve prior valid data and unowned lookalikes.

5. Validation tiers:
   - During RED/GREEN, run only the newly affected pacing or publication tests.
   - After each seam stabilizes, run the complete importer test module.
   - After the final production change, run only the configured importer profile through `run_validation.py`; do not add behavior evaluations, content checks, or whole-repository gates unless classification escalates.
   - Because pacing is timing-sensitive, repeat the deterministic importer profile after final integration if instability appears; do not introduce elapsed-time assertions.

6. Evidence:
   - Record exact command, final commit SHA, configuration identity, Python version, exit status, warnings, work duration, and concise machine-readable validation output.
   - Maintain a threat-to-test matrix covering pacing, redirects, cache attacks, ancestor replacement, interrupted publication, cleanup ownership, closed handles, and unsupported operations.
   - Pin evidence to the final production SHA and reject personal paths or machine identifiers.
   - No frozen behavioral artifact or behavioral cohort is required unless skill instructions/triggering behavior also changes.
   - Run a small, paced live check only at an explicit milestone with approval. Record origin, redirect outcome, attempt timing, and cache publication result. If unavailable, mark live acceptance blocked rather than passed.

Current baseline identity: commit `1bd71265be7e3b7534af6c0068b5f5c5cb34d680`; importer SHA-256 `e1d84689d6154b543aab90fb103b1a790148b158dc59dad8109c271b1463f3b0`; Python `3.14.6`. Validation evidence is planned, not executed, because no implementation patch exists yet.

Relative optimizer skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/importer-threat-model.md`
- `assets/skill-optimizer.example.json`

`references/frozen-evaluations.md` was intentionally not read because this is not a behavioral-profile change.
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
references/validation-profiles.md
references/importer-threat-model.md
assets/skill-optimizer.example.json
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
````

#### Separate files-read list (`agent-reported`)

````text
SKILL.md
references/validation-profiles.md
references/frozen-evaluations.md
references/importer-threat-model.md
assets/skill-optimizer.example.json
````
