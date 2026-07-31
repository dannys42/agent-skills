Validation plan

- Intended profile: `importer`, because retry pacing and cache writes cover external acquisition and managed persistent storage.
- Current inspection baseline: commit `1bd71265be7e3b7534af6c0068b5f5c5cb34d680`; importer SHA-256 `e1d84689d6154b543aab90fb103b1a790148b158dc59dad8109c271b1463f3b0`.
- `inspect_skill.py` found the target skill, OpenAI metadata, 23 references, 8 scripts, 4 plugin manifests, 3 marketplace adapters, and 7 test files.
- The current whole-worktree classifier returned `full` only because unrelated untracked paths are present. Run classification on an isolated intended diff before implementation; importer script plus importer tests should classify as `importer`. Any unknown or second non-test category escalates to `full`.

Implementation and validation should be test-first:

1. Add focused failing tests using fake monotonic clocks, scripted transports, temporary directories, and injected filesystem failures. Confirm each RED failure represents the missing pacing or publication guarantee.
2. Pacing coverage must include normal requests, retryable 429/5xx/`URLError`, exhausted retries, redirects, failures, minimum spacing, bounded backoff, and `Retry-After` lengthening but never shortening the configured minimum.
3. Cache-write coverage must include traversal, symlink, hardlink, FIFO, device, and directory rejection; retained-root behavior during ancestor replacement; exclusive in-boundary staging; file and directory durability ordering; interruption at every publication stage; old-or-new manifest/page visibility without mixtures; owned temporary cleanup while preserving unowned lookalikes; closed handles; and deterministic failure when descriptor-relative operations are unsupported.
4. Run the narrow focused suite during RED/GREEN:
   `python3 -m unittest discover -s plugins/swift-design-patterns/tests -p 'test_import_refactoring_guru.py' -v`
5. After the production behavior is frozen, run only checks declared by the configured importer profile through:
   `python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py <config> importer --output <evidence>`
6. Run the complete plugin test suite once at the subsystem milestone, provided that command is declared in the importer profile. Do not run unrelated content or behavioral evaluations.
7. A live external-network check is an explicit milestone only: obtain approval, restrict it to the configured HTTPS origin, keep it small and paced, and record the outcome. Without milestone approval, report it as not performed—not passing.

Required evidence

- Final implementation commit SHA and distributable importer hash.
- Exact commands, Python/tool versions, exit statuses, concise summaries, and full temporary logs.
- RED evidence showing each new regression test failed for the expected reason, followed by GREEN evidence.
- A threat-to-test matrix covering pacing, redirects, hostile cache objects, ancestor replacement, interruption safety, cleanup ownership, closed handles, and unsupported operations.
- Fake-clock attempt timestamps demonstrating spacing and `Retry-After` behavior.
- Injected-failure results demonstrating readers see only the prior valid pair or the new valid pair.
- Work versus mandatory-wait timing from `report_timing.py`.
- If approved, sanitized live-check request log and outcome, with no personal paths or machine identifiers.

Stopping criteria: stop on any missing or failed mandatory check, artifact/evidence hash mismatch, unknown path, mixed non-test category, unsafe cache fallback, flaky timing result, or need for unapproved live network access.

No validation suite or live check was run; this was a planning and inspection pass.

Relative files read from the specified skill directory

- `SKILL.md`
- `references/validation-profiles.md`
- `references/importer-threat-model.md`
- `assets/skill-optimizer.example.json`
- `scripts/inspect_skill.py`
- `scripts/classify_change.py`
- `scripts/optimizer_config.py`