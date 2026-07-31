Selected profile: **Content**, provided the final diff contains only the attributed reference and code example. No files were changed.

The current shared worktree classifies as **Full** because it includes unrelated branch-wide changes, including an existing `SKILL.md` edit. Re-run classification against the isolated correction before validation; retain Full if that mixed scope remains.

Validation plan:

1. Run `inspect_skill.py --json` and `classify_change.py --json` against the target configuration.
2. Confirm the effective diff excludes `SKILL.md`, behavioral instructions, production scripts, and unrelated paths.
3. State stopping criteria: stop for any failed or missing mandatory check, unverifiable attribution, broken source, inaccurate/non-runnable example, originality concern, `SKILL.md` change, unknown path, or mixed risk.
4. Run the configured Content profile:
   `run_validation.py <config> content --output <report.json>`.
5. Verify the corrected attribution against the canonical source, recording its URL, revision/version or retrieval date, and a concise source-to-reference mapping.
6. Extract the code example into the narrowest runnable fixture and compile/typecheck or execute it with the relevant toolchain.
7. Check changed links, content contracts, licensing/originality, plugin structure/manifests, and focused tests required by Quick plus Content.
8. Record skipped checks and rationale. Frozen behavioral cohorts, artifact hashing, importer threat checks, and live-network milestones are unnecessary unless the scope changes.

Evidence to retain:

- Inspection and isolated-diff classification JSON.
- Diff proof that `SKILL.md` is unchanged.
- Content validation report and exit status.
- Canonical-source identity and fidelity comparison.
- Link-check results.
- Example fixture, exact command, toolchain version, output, and exit status.
- Attribution/licensing/originality review.
- Artifact identity via commit SHA or patch identity, elapsed duration, skipped checks, and escalation conditions.

Evidence status: planned, not executed.

Relative skill files actually read:

```text
SKILL.md
references/frozen-evaluations.md
references/importer-threat-model.md
references/validation-profiles.md
```