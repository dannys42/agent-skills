Selected profile: `importer`, assuming the change is isolated to retry pacing and cache writes. These are explicitly importer risks. If inspection/classification reveals another changed category, unknown paths, or release scope, escalate to `full`.

Validation plan:

1. Establish the target repository configuration and an explicit clean base. Before finalizing the profile, run:

   - `inspect_skill.py <config> --json`
   - `classify_change.py <config> --base <clean-base> --json`

   Record both outputs and the classifier’s reasons. A missing config/base or incomplete inspection is missing evidence, not a pass.

2. Before checks, define stopping criteria: stop on any mandatory-check failure or omission, unsafe cache mutation, outside-boundary write, stale/mixed manifest-page pair, pacing violation, unexpected network access, unknown path, newly mixed change category, or evidence/artifact mismatch.

3. Add deterministic focused tests using fake clocks, scripted transports, temporary directories, and injected failures:

   - Enforce the minimum interval across ordinary requests, retries, redirects, and failures, measured from a monotonic clock.
   - Verify `Retry-After` may lengthen but never shorten the minimum delay.
   - Bound retry and redirect counts.
   - Validate every outbound URL before sending: HTTPS, exact allowed origin, permitted path family; reject userinfo, lookalike hosts, alternate ports, encoded escapes, and off-family redirects.
   - Reject traversal, symlinks, hardlinks where exclusive ownership is required, FIFOs, devices, and directories.
   - Exercise root/ancestor replacement and concurrent swaps; all reads, logs, staging, cleanup, and replacement operations must remain anchored to the retained trusted-directory boundary.
   - Inject short/failed writes, flush failures, replacement failures, and interruptions. Readers must see either the previous valid manifest/page pair or the new pair, never a mixture.
   - Verify temporary files are created exclusively inside the trusted boundary and cleanup removes only marker-proven importer-owned objects.
   - Verify closed handles and unsupported identity-preserving filesystem operations fail closed with stable deterministic errors.

4. Run only the checks configured for the importer profile:

   - `run_validation.py <config> importer --output <report.json>`

   Do not add behavioral cohorts, artifact hashing, content checks, or whole-repository gates unless classification expands the risk.

5. Treat a live-network check as a separately approved milestone, not routine validation. If approved, keep it small, paced, and restricted to the configured origin, then run the explicitly configured network-capable check with `--allow-network`. If it is not approved or unavailable, record it as not run—not passing.

6. Capture evidence:

   - Exact commands, clean base, changed-path list, inspection/classification JSON, reasons, tool/runtime versions, exit statuses, concise outputs, warnings, and durations.
   - A threat-to-test matrix covering every applicable importer threat.
   - Focused deterministic test output and the final importer-profile report.
   - Filesystem fixture identities and assertions showing no outside mutation, no unsafe fallback, no leaked owned temporary files, and preservation of unowned lookalikes.
   - Live milestone approval and result, if performed.
   - Work versus waiting time from `report_timing.py <report.json>`.
   - Skipped checks with rationale and the next escalation condition.

Completion requires all configured importer checks and applicable threat rows to pass with complete evidence. No behavioral frozen cohort or distributable artifact hash is required for this isolated non-behavioral change.

Files read, relative to `plugins/skill-development-optimizer/skills/optimizing-skill-development`:

```text
SKILL.md
assets/skill-optimizer.example.json
references/validation-profiles.md
references/importer-threat-model.md
```