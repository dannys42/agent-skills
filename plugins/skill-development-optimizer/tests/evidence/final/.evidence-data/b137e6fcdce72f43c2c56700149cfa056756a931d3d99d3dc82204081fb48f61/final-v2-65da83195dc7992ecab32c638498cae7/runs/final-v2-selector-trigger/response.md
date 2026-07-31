Validation profile: **Behavior** for the scoped trigger-description and mandatory-workflow change.

The configured fresh-agent evaluator is unavailable, so both the required pre-edit baseline and post-edit behavioral cohort are missing. They must be reported as blocked—not passed. Deterministic checks may proceed, but the change cannot be called behaviorally validated or deployable.

Validation plan:

1. Isolate the intended diff, then run `inspect_skill.py` and `classify_change.py`.
2. Declare stopping criteria before checks: stop on failed deterministic checks, mixed/unknown paths, evaluator unavailability, artifact mismatch, incomplete evidence, or undeclared rubric fields.
3. Run only the configured Behavior checks through `run_validation.py`.
4. Finalize and freeze the distributable artifact; hash it with `hash_artifact.py`.
5. Predeclare fresh-agent cases and rubric covering:
   - Positive trigger selection.
   - Near-miss/non-trigger behavior.
   - Mandatory recommendation compliance.
   - Compliance under shortcut/time-pressure prompting.
   - Correct handling when a required capability is unavailable.
6. Once the evaluator returns, initialize one cohort and run every case with a fresh agent receiving only its prompt and the frozen skill.
7. Record prompt, owned run ID, verbatim response, separate verbatim `files_read`, and every declared boolean rubric result.
8. Label file evidence `agent-reported`; do not claim it independently proves filesystem access, tool use, or context isolation.
9. Complete, verify, and summarize the cohort. Any artifact-byte change makes the cohort historical and requires rerunning every headline case.

The current dirty-worktree classifier result escalates to Full because unrelated/untracked production, test, and evidence paths are present. It should not override the scoped Behavior classification; rerun classification against an isolated intended diff.

Relative target-skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`