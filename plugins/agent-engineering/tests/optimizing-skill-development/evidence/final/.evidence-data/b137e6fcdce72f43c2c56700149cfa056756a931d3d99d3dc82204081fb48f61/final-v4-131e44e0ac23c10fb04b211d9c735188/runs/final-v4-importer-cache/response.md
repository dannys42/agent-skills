Selected profile: `importer`.

Retry pacing and managed cache writes are both importer risks, so they do not by themselves require `full`. Structural inspection succeeded. The current classifier returned `full` only because the worktree contains unrelated untracked unknown paths; re-run classification against the isolated implementation diff. If it still reports unknown or mixed categories, retain `full`.

Validation plan:

1. Establish stopping criteria before implementation:
   - Stop for failed inspection, missing configuration/checks, unknown paths, a newly mixed category, or unapproved live-network access.
   - Stop if a RED test does not fail for the intended reason.
   - Stop on any mandatory threat without deterministic coverage, artifact/evidence mismatch, nondeterminism, or unsanitized local identifiers.

2. Follow test-first development:
   - Add focused failing tests before changing production code.
   - Use an injected monotonic clock, fake sleep, scripted transport, temporary directories, and injected filesystem failures—no real sleeps or network.

3. Validate retry pacing:
   - Assert the new pacing rule across ordinary requests, every retry, redirects, response-read failures, and immediately raised transport failures.
   - Assert attempt timestamps, not only sleep calls.
   - Verify `Retry-After` can lengthen but never shorten the configured minimum.
   - Retain bounded retry/redirect behavior and exact HTTPS origin/path enforcement.
   - Cover invalid/nonfinite `Retry-After`, exhausted retries, and response closure.

4. Validate cache writes:
   - Exercise page, manifest, catalog, and request-log writes.
   - Inject interruption at temporary creation, partial write, file flush, replacement, and directory flush boundaries.
   - Prove readers see the previous valid manifest/page pair or the new pair, never a mixed pair.
   - Verify exclusive in-boundary temporary files, correct durability ordering, and cleanup only of importer-owned staging files.
   - Re-run hostile-cache cases: traversal, symlink, hardlink, FIFO/device/directory, ancestor replacement, concurrent destination replacement, closed handles, and unsupported descriptor-relative operations.
   - Confirm failures preserve prior valid data and unowned lookalikes.

5. Validation tiers:
   - During RED/GREEN, run only the newly affected pacing or publication tests.
   - After each seam stabilizes, run the complete importer test module.
   - After the final production change, run only the configured importer profile through `run_validation.py`; do not add behavior evaluations, content checks, or whole-repository gates unless classification escalates.
   - Because pacing is timing-sensitive, repeat the deterministic importer profile after final integration if instability appears; do not introduce elapsed-time assertions.

6. Evidence:
   - Record exact command, final commit SHA, configuration identity, Python version, exit status, warnings, work duration, and concise machine-readable validation output.
   - Maintain a threat-to-test matrix covering pacing, redirects, cache attacks, ancestor replacement, interrupted publication, cleanup ownership, closed handles, and unsupported operations.
   - Pin evidence to the final production SHA and reject personal paths or machine identifiers.
   - No frozen behavioral artifact or behavioral cohort is required unless skill instructions/triggering behavior also changes.
   - Run a small, paced live check only at an explicit milestone with approval. Record origin, redirect outcome, attempt timing, and cache publication result. If unavailable, mark live acceptance blocked rather than passed.

Current baseline identity: commit `1bd71265be7e3b7534af6c0068b5f5c5cb34d680`; importer SHA-256 `e1d84689d6154b543aab90fb103b1a790148b158dc59dad8109c271b1463f3b0`; Python `3.14.6`. Validation evidence is planned, not executed, because no implementation patch exists yet.

Relative optimizer skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`
- `references/importer-threat-model.md`
- `assets/skill-optimizer.example.json`

`references/frozen-evaluations.md` was intentionally not read because this is not a behavioral-profile change.
