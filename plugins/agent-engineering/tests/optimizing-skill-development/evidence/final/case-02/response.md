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
