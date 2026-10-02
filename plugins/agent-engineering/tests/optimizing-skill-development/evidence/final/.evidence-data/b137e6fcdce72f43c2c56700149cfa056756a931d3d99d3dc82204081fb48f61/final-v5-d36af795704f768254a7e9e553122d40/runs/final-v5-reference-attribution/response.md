Validation plan

- Validation scope: provisional `content`. The requested attribution/reference and code-example correction requires Quick checks plus content contracts, example accuracy, attribution/source-link verification, and originality evidence.
- Before finalizing the profile, create or locate a repository-root optimizer config, then run:

```sh
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py --json <config>
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py --json <config>
```

- Retain `content` only if inspection is complete and classification confirms content-only paths. Escalate to `full` for unknown paths, mixed categories, or an unexpected behavioral change.
- Capture RED evidence first: a focused attribution/content-contract test must reject the old reference, and an executable example test must expose the code defect.
- Correct only the reference and example. Prove `SKILL.md` is unchanged using a scoped diff and before/after checksum.
- Verify attribution against the authoritative, version-specific source, including title/author/location and changed-link validity. If this requires unapproved live network access, stop and request approval.
- Run the example with declared dependency/toolchain versions in a clean deterministic environment.
- Record an originality result; unavailable inputs remain unavailable, never “passed.”
- Run only the configured profile:

```sh
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
  --output <evidence-path> <config> content
```

Evidence should preserve:

- Commit SHA, dirty-state/diff identity, optimizer config, and changed-file hashes.
- Inspection and classification JSON.
- RED and GREEN commands, tool versions, exit statuses, and concise logs.
- Canonical attribution/source-link result.
- Example compile/typecheck/test result.
- Originality result.
- Scoped diff and checksum proof that `SKILL.md` did not change.
- Work time versus waiting time.

Skip behavioral frozen evaluations, importer threat checks, live-network checks, and whole-repository gates unless risk classification escalates. Do not label skipped checks as passing.

Stopping criteria: stop on any failed or missing mandatory check, unverifiable attribution or example, evidence/artifact mismatch, unexpected `SKILL.md` change, unknown or mixed path classification, originality failure, unrelated diff, or required network access without approval.

Current evidence status: plan only; no target configuration or target reference was supplied, so no validation evidence has been collected.

Files actually read

Repository-relative skill files:

- `plugins/skill-development-optimizer/skills/optimizing-skill-development/SKILL.md`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/references/validation-profiles.md`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/assets/skill-optimizer.example.json`

Required sub-skill files:

- `~/.codex/skills/.system/skill-creator/SKILL.md`
- `~/.agents/skills/writing-skills/SKILL.md`
- `~/.agents/skills/test-driven-development/SKILL.md`