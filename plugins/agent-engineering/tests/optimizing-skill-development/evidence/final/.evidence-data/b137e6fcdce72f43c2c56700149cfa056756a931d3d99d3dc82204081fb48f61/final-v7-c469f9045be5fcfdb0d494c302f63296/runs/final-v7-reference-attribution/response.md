Selected profile: `content`.

Reason: correcting an attribution, source/reference material, and its code example changes correctness and provenance, while leaving `SKILL.md` and behavioral instructions unchanged. The deterministic inspection succeeded. The current shared worktree classifier sees unrelated mixed changes, so the implementation must rerun classification against the intended base with only this correction in scope; the expected result is `content`. Any behavioral, importer, mixed, or unknown path escalates to `full`.

Validation plan:

1. Before editing, record the base commit and intended reference/example paths. Do not request replacement wording merely to classify the change.
2. After editing, run `inspect_skill.py` and `classify_change.py --base <base>` using the repository configuration. Stop unless the changed set is limited to reference/example content and `SKILL.md` is unchanged.
3. State stopping criteria before validation: stop on any mandatory failure or missing check, unverifiable attribution/source, inaccurate or non-runnable example, artifact mismatch, newly mixed/unknown classification, or need for unapproved live network access.
4. Run only the configured `content` profile through `run_validation.py`, saving its JSON report. Required evidence is:
   - Quick checks: skill/package structure, configuration/manifests, changed links, and configured focused tests.
   - Content checks: declared content contracts, exact code-example accuracy, attribution details and authoritative source-link agreement, and originality/provenance.
5. Capture the exact command, configuration path, base/head commit identities, changed paths, tool version, exit status, concise output, warnings, and work-versus-wait duration. Identify this content artifact by commit/diff identity.
6. Skip frozen behavioral evaluations, cohort management, behavioral artifact hashing, importer threat checks, live-network checks, and unrelated whole-repository gates. They are outside this change’s risk unless classification escalates.
7. Report the profile, risk rationale, checks passed/failed/skipped, artifact identity, evidence status, duration, and next escalation condition. An unavailable check remains missing, never passing.

No validation suite was run because the request asks for a plan, and no correction or replacement content was supplied. No files were changed.

Relative skill files deliberately read for this plan:

- `SKILL.md`
- `references/validation-profiles.md`
- `assets/skill-optimizer.example.json`