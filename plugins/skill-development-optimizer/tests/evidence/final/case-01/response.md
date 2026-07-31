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
