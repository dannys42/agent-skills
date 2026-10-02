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