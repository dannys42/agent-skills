Validation plan

- Provisional minimum profile: `importer`, because retry pacing and managed cache writes are both explicitly importer risks.
- Final profile selection requires the actual importer target/config. The available optimizer configuration targets the optimizer skill itself, so its current `full` classification does not classify the hypothetical external-research importer.
- Before implementation, run `inspect_skill.py` and `classify_change.py` against the importer’s configuration. Escalate to `full` for mixed categories, unknown paths, or incomplete inspection.

Stopping criteria, declared before validation:

- Stop on any failed or missing mandatory check.
- Stop on artifact/hash mismatch, an unknown or newly mixed change category, or unsupported secure filesystem operations.
- Do not perform live network validation without explicit approval.

Checks and evidence:

1. Use TDD: add each deterministic regression test first and confirm the expected RED failure.
2. Retry pacing with a fake monotonic clock and scripted transport:
   - Minimum interval covers every outbound attempt, including retries, redirects, and attempts following failures.
   - A shorter `Retry-After` cannot reduce the minimum; a longer value extends it.
   - Retry and redirect counts remain bounded.
3. Request-policy regression coverage:
   - Redirects must remain HTTPS on the exact allowed origin and path family.
   - Reject userinfo, alternate ports, lookalike hosts, encoded escapes, and cross-family redirects.
4. Hostile-cache coverage using temporary directories and injected failures:
   - Reject traversal, symlinks, hardlinks, FIFOs, devices, and directories.
   - Ancestor/root replacement cannot redirect reads, logs, staging, or publication.
   - Temporary files are exclusive and anchored to a retained directory boundary.
   - Interrupted writes expose either the previous valid manifest/page pair or the new pair, never a mixture.
   - Cleanup removes only owned objects and preserves unowned lookalikes.
   - Closed handles and unsupported secure operations fail deterministically.
5. Run only commands configured for the selected `importer` profile through `run_validation.py`; avoid unrelated whole-repository, content, and behavioral evaluations.
6. Hash the final distributable with `hash_artifact.py`. Preserve the exact command, commit SHA, artifact hash, tool versions, exit status, concise output, threat-to-test mapping, and work/wait timing.
7. At an explicit milestone only, request approval for one small, paced live check restricted to the configured origin. Network unavailability must not invalidate deterministic importer evidence.

Evidence status: planned; no importer implementation or mandatory validation was run. `frozen-evaluations.md` was intentionally skipped because this is importer work, not a behavioral-skill evaluation.

Relative skill files actually read

- `SKILL.md`
- `assets/skill-optimizer.example.json`
- `references/validation-profiles.md`
- `references/importer-threat-model.md`
- `scripts/classify_change.py` (matched excerpts only)
- `scripts/optimizer_config.py` (matched excerpt only)

A temporary `scripts/graphify-out/` directory generated during inspection was removed; it contained only reproducible graph artifacts.
