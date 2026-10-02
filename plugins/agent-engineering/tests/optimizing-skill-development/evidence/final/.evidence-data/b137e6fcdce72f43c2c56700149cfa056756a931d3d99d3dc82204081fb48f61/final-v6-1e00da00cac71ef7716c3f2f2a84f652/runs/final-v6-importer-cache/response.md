Validation plan

- Provisional profile: `importer`.
- Risk basis: retry pacing affects every outbound attempt; cache writes are managed persistent-store publication.
- Finalize the profile only after running, from the repository root:

  ```sh
  python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py --json "${CONFIG}"
  python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py --json "${CONFIG}"
  ```

- If no configuration exists, copy and customize `assets/skill-optimizer.example.json` with repository-relative target, validation commands, and evaluation paths.
- Escalate to `full` for mixed categories, unknown paths, a new plugin, or a release. Do not downgrade unless every original mandatory check remains covered with recorded deterministic evidence.

Test-first validation:

1. Add focused failing regressions and verify each RED failure is caused by the missing behavior.
2. Retry/pacing tests use a fake monotonic clock and scripted transport:
   - Minimum interval applies before every attempt, including retries and requests following failures or redirects.
   - `Retry-After` can lengthen but never shorten the configured minimum.
   - Retry and redirect counts remain bounded.
   - Redirects enforce HTTPS, exact origin, allowed path family, and reject userinfo, alternate ports, lookalike hosts, encoded escapes, and origin/path-family changes.
3. Cache/publication tests use temporary directories and injected failures:
   - Reject traversal, symlinks, hardlinks, FIFOs, devices, and directories.
   - Root or ancestor replacement cannot redirect reads, logs, staging, replacement, or cleanup.
   - All I/O stays anchored to a retained trusted directory boundary.
   - Interrupted publication exposes either the previous or new valid manifest/page pair, never a mixture.
   - Staging uses exclusive creation; data and directory metadata are durably flushed in publication order.
   - Cleanup removes only owned, correctly typed objects and preserves lookalikes.
   - Closed handles and unsupported identity-preserving operations fail with stable deterministic errors.
4. Verify GREEN with the focused tests, then run only the configured importer checks:

   ```sh
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
     --output "${VALIDATION_REPORT}" "${CONFIG}" importer
   ```

Evidence to retain:

- Exact configured target and distributable artifact identity, preferably from:

  ```sh
  python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py \
    --json --output "${ARTIFACT_RECORD}" "${CONFIG}"
  ```

- Commit SHA, configuration, classifier/inspection JSON, exact command, tool versions, exit status, concise output, and full temporary log.
- A threat-to-test matrix covering every applicable network and filesystem threat.
- RED and GREEN outputs for each new regression.
- Importer validation report pinned to the same artifact identity.
- Timing reports separated into work and waiting time, summarized with `report_timing.py`.
- One small live-network result only at an explicit milestone, after approval, restricted and paced to the configured origin. Routine validation must remain deterministic and offline.

Stopping criteria, declared before execution:

- Stop on any failed or missing mandatory check.
- Stop on inspection/classification uncertainty, newly mixed risk, or artifact/evidence mismatch.
- Stop before any unapproved live-network access.
- Never report an unavailable check as passing.

Checks currently run: none; this was a plan-only task and no target configuration or concrete importer diff was supplied. Evidence status: pending. Duration: not measured. Next escalation condition: deterministic classification reports mixed/unknown/new-plugin/release risk, which requires `full`.

Relative skill files actually read

- `SKILL.md`
- `assets/skill-optimizer.example.json`
- `references/validation-profiles.md`
- `references/importer-threat-model.md`