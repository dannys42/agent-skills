Validation plan

- Intended change classification: `behavior` because it changes a trigger description and a mandatory workflow.
- Repository caveat: the configured classifier currently reports mixed categories plus unknown paths, which requires `full`. Rerun against a clean/scoped baseline; use `behavior` only if the isolated result is behavior-only.
- State stopping criteria first: stop on failed/missing mandatory checks, artifact mismatch, mixed/unknown classification, or unavailable required evaluation.
- Run only the configured profile checks through `run_validation.py`.
- After deterministic checks pass, hash the exact distributable artifact and initialize one frozen cohort.
- Predeclare fresh positive-trigger, negative-trigger, and mandatory-workflow pressure cases with a complete rubric.
- Capture each prompt, verbatim response, run ID, rubric result, and separate verbatim `files_read`.
- Because the fresh-agent evaluator is unavailable, mark behavioral evidence incomplete/missing and stop. Never count it as passing.
- Label file-read evidence `agent-reported`; explicitly state it does not independently prove filesystem access, tool invocation, or context isolation.
- Restart the entire headline cohort after any artifact-byte change.

Relative target-skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`
- `assets/skill-optimizer.example.json`

I did not read `references/importer-threat-model.md` or any script source.