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
