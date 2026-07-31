Selected profile: `importer` for an isolated retry-pacing/cache-write change. Semantic risk overrides a generic path classification.

Validation plan:

1. Establish scope before editing:
   - Run `inspect_skill.py --json <config>`.
   - Run `classify_change.py --json --base <pre-change-SHA> <config>`.
   - Use a clean, explicit base. The current worktree reports mixed/unknown changes and therefore classifies as `full`; it is unsuitable as the isolated importer baseline.
   - Escalate to `full` if final paths include another non-test category, unknown paths, or release work.

2. Use test-first RED/GREEN coverage with deterministic seams:
   - Fake monotonic clock and scripted transport for pacing.
   - Prove the minimum interval covers initial attempts, retries, redirects, and attempts after failures.
   - Prove `Retry-After` can lengthen but never shorten the minimum.
   - Verify retry/redirect bounds and exact HTTPS origin/path-family enforcement.
   - Temporary hostile-cache fixtures and injected failures for traversal, symlinks, hardlinks, FIFOs/devices/directories, ancestor replacement, closed handles, and unsupported platform operations.
   - Verify descriptor-anchored reads/logs/staging/replacement and cleanup ownership.
   - Inject interruption at each publication boundary; readers must see either the old manifest/page pair or the new pair, never a mixed pair.
   - Record a test-to-threat matrix, including explicit “not applicable” rationales.

3. Run only configured importer checks after focused tests:
   - `run_validation.py <config> importer --output <report.json>`
   - Do not add unrelated repository/profile checks unless scope escalates.
   - Summarize work versus waiting time with `report_timing.py <report.json>`.

4. Live evidence:
   - No routine network dependency.
   - At an explicit milestone only, request approval first, then run one small paced check restricted to the configured exact origin.
   - Record unavailable/unapproved live evidence as unavailable, never passing.

Evidence to retain:

- Inspection and classification JSON, explicit base SHA, final commit SHA, and changed-path list.
- RED output showing each new test failed for the intended missing behavior.
- Focused GREEN output and final importer-profile report with exact commands, tool/runtime versions, exit status, durations, warnings, and concise results.
- Threat matrix covering pacing, redirects, hostile cache state, concurrent replacement, interrupted publication, cleanup ownership, closed handles, and unsupported operations.
- Live-check approval/milestone/outcome when applicable.
- No personal paths or stable local identifiers in committed evidence; use placeholders such as `${REPO_ROOT}`.

Stopping criteria: stop on any failed or missing mandatory check, uncovered applicable threat, mixed/unknown classification, evidence/source mismatch, or need for unapproved live network access.

Relative skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/importer-threat-model.md`

No files were changed.