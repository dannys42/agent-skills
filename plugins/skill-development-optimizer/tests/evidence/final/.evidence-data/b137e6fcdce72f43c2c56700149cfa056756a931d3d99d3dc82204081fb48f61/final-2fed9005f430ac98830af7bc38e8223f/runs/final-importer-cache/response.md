Selected profile: `importer`, assuming only importer implementation and importer tests change. Retry pacing and cache publication are both explicitly importer risks.

Validation plan:

1. Before implementation, declare stopping criteria: stop on any mandatory test failure, nondeterministic timing, uncovered changed branch, cache escape, mixed manifest/page state, leaked temporary artifact, artifact/evidence mismatch, or need for unapproved network access.

2. Add deterministic regression tests using a fake monotonic clock and scripted transport:

   - Minimum interval across successful requests, retryable failures, exhausted failures, and redirects.
   - Delay measured from completion/failure of the prior attempt.
   - `Retry-After` shorter than the minimum cannot reduce pacing; longer valid values extend it; invalid values are ignored safely.
   - Bounded retry/backoff and redirect counts.
   - Every actually transmitted attempt is logged once; rejected/unsent redirect hops are not logged.
   - Exact HTTPS origin and path-family enforcement remains intact.

3. Exercise hostile cache states in temporary directories:

   - Traversal, symlinks, hardlinks, FIFOs, directories, and device-like stat results.
   - Cache-root or ancestor replacement during read, log append, staging, and replacement.
   - Destination replacement between validation and publication.
   - Closed cache-root handles and unsupported descriptor-relative operations fail with stable errors.
   - Permission errors and short/zero writes fail closed.
   - No outside file is modified and unowned lookalike staging files are preserved.

4. Inject failures at each cache-publication boundary:

   - Temporary creation/write.
   - File flush/close.
   - Page replacement and directory metadata flush.
   - Manifest staging/replacement and final directory flush.
   - Interruption between page and manifest operations.

   After every injected failure, assert readers see either the previous valid manifest/page pair or the complete new pair, never a checksum-mismatched mixture. Also assert owned temporary files are reclaimed without deleting unowned files. Record an ordered mock trace to prove file-data and directory-metadata flush ordering.

5. Run focused validation while developing:

   ```sh
   python3 -m unittest \
     plugins/swift-design-patterns/tests/test_import_refactoring_guru.py -v
   ```

   Run deterministic tests once per relevant change; repeat only if the implementation or result is genuinely timing-sensitive or unstable.

6. At the subsystem milestone, run the complete Swift-design-patterns test suite, followed by the repository’s complete gate once after the final production-code change. Through the optimizer, run:

   ```sh
   python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py \
     <optimizer-config> importer --output <evidence-file>
   ```

7. Run the existing five-second localhost integration test once to verify the standard-library transport boundary. This uses loopback, not external network access.

8. Skip a live Refactoring.Guru import during routine edit validation. If this is an explicit milestone, obtain approval first, keep the import small and origin-restricted, and retain request timestamps proving the configured spacing.

Evidence to retain:

- Exact post-change commit SHA plus SHA-256 identities for the importer and test file.
- Exact commands, Python/tool versions, exit codes, concise results, and relevant warnings.
- Threat-to-test matrix covering pacing, redirects, hostile cache objects, root replacement, interruption, cleanup ownership, closed handles, and unsupported operations.
- Ordered durability trace for injected write failures.
- Localhost observed interval.
- Diff/privacy check showing no `.research` downloads, request logs, cache files, temporary files, credentials, or personal paths.
- Work versus waiting duration recorded separately.
- Checks skipped and reasons, especially the unapproved live-network milestone.

Evidence status: planned, not executed. Frozen behavioral cohorts, content/originality checks, and Full validation are unnecessary for an importer-only change. Escalate to `full` if skill instructions, references/content, release metadata, multiple non-test categories, or unknown paths also change.

Relative files read from the provided skill directory:

```text
SKILL.md
references/validation-profiles.md
references/importer-threat-model.md
```