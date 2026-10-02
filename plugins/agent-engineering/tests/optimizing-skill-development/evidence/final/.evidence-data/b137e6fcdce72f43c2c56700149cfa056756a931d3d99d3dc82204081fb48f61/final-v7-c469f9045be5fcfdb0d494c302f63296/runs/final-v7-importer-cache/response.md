Validation plan

- Profile: **Importer**, provisionally selected from the stated change. Retry pacing is external-acquisition risk; cache writes are managed persistent-storage risk. Both remain within one category, so they do not alone require Full.
- Deterministic classification is currently pending: the repository has no target `skill-optimizer` configuration, and no concrete patch/base was supplied. Do not count inspection or classification as passing until a repository-relative config exists and both `inspect_skill.py` and `classify_change.py` succeed.

Planned evidence:

1. Run configured inspection and classification against the exact patch/base. Escalate to Full for unknown paths or any additional non-test category.
2. Run only the configured Importer-profile command through `run_validation.py`.
3. Add deterministic fake-clock/scripted-transport coverage proving:
   - minimum spacing applies to every outbound attempt;
   - pacing is measured from completion/failure as intended;
   - retries and accepted redirect hops cannot bypass the gate;
   - `Retry-After` may extend but never shorten the minimum;
   - invalid `Retry-After` is ignored;
   - retry counts/backoff remain bounded;
   - failed and redirected attempts are logged exactly once.
4. Add injected-filesystem-failure coverage proving:
   - writes and replacements remain anchored to the retained cache directory;
   - temp files are created exclusively inside that boundary;
   - file data is flushed before replacement and directory metadata afterward;
   - interruption at write, flush, replace, or manifest publication preserves the old valid page/manifest pair or exposes the complete new pair, never a mixture;
   - traversal, symlink, hardlink, FIFO, device, directory, ancestor-swap, and destination-replacement attacks fail closed;
   - cleanup removes only importer-owned temporary artifacts;
   - closed handles and unsupported descriptor-relative operations return stable errors.
5. Preserve regression evidence for redirects, cache reads, logging, resume behavior, corrupt manifests, and permission errors.
6. Record threat-to-test mapping, command output, exit status, elapsed work versus mandatory waiting time, repository base/HEAD, changed-path list, config identity, and hashes of changed importer/test files.
7. Run one small, approved, origin-restricted live request only at an explicit milestone; routine validation must remain offline.

Stopping criteria:

- Stop on failed/missing inspection, classification, or mandatory configured check.
- Stop on evidence/artifact mismatch, an unknown/mixed category, or any need for unapproved live network access.
- Do not report unavailable checks as passing.

Evidence status: plan only; no profile validation command or live network check was run. No files were edited.

Relative skill files actually read

- `plugins/skill-development-optimizer/skills/optimizing-skill-development/SKILL.md`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/references/validation-profiles.md`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/references/importer-threat-model.md`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/assets/skill-optimizer.example.json`
- `plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/optimizer_config.py`
- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/import_refactoring_guru.py`

Supporting non-skill file read

- `plugins/swift-design-patterns/tests/test_import_refactoring_guru.py`