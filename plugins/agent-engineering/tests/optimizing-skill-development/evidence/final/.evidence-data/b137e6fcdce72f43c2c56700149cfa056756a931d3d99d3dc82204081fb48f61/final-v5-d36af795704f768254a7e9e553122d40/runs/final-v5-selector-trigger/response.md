Selected profile: `behavior`. Trigger and mandatory-workflow changes affect discovery, selection, and required behavior. No `full` escalation is needed unless inspection finds mixed or unknown changes.

Validation plan:

1. Run configured inspection and classification from the repository root.
2. Run only checks declared by the `behavior` profile.
3. Record commands, commit SHA, versions, exit statuses, results, and timing.
4. Freeze cases and rubric, hash the exact distributable using `sha256-length-framed-v1`, and initialize one headline cohort.
5. Require fresh-agent runs against that frozen artifact, capturing prompts, run IDs, verbatim responses, rubric scores, and separate files-read reports.
6. Label files-read evidence `agent-reported`; it does not prove filesystem access, tool use, or context isolation.
7. Because the evaluator is unavailable, report behavioral evidence as blocked/incomplete—never passing. Resume only when fresh cases can run against the same artifact digest; then complete, verify, and summarize the cohort.
8. Stop on any failed/missing check, artifact mismatch, changed distributable, mixed/unknown classification, or unapproved network requirement. Importer and live-network checks are unnecessary here.

Relative target-skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/frozen-evaluations.md`
- `assets/skill-optimizer.example.json`

`references/importer-threat-model.md` was intentionally not read because this is not importer work.