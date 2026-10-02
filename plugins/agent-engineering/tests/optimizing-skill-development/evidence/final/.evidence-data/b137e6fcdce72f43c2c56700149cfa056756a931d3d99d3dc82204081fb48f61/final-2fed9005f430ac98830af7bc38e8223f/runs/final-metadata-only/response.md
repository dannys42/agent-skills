Validation plan:

- Treat changes limited to `interface.display_name` and/or `interface.short_description` as **Quick**: they are UI metadata and do not alter agent instructions.
- Before editing, record stopping criteria: stop if any other path changes, `default_prompt` changes, YAML becomes invalid, inspection/classification is incomplete, or a mandatory check fails.
- Preserve all keys and quote all string values. Confirm `short_description` remains 25–64 characters and the display text accurately represents `SKILL.md`.
- Capture a path-limited diff proving only `agents/openai.yaml` changed.
- Run deterministic structure inspection:
  `python3 scripts/inspect_skill.py --json ../../../skill-development-optimizer/skill-optimizer.example.json`
- Run deterministic classification:
  `python3 scripts/classify_change.py --json ../../../skill-development-optimizer/skill-optimizer.example.json`
- Run the selected validation:
  `python3 scripts/run_validation.py ../../../skill-development-optimizer/skill-optimizer.example.json quick --output <temporary-evidence-path>`
- Record the profile, risk rationale, exact commands, exit statuses, concise results, elapsed duration, and skipped checks. Behavioral frozen evaluations, artifact hashing, importer threat checks, attribution/originality checks, and network checks are inapplicable for display-only UI metadata.
- Escalate to **Behavior** if `default_prompt` changes because that text is inserted into an invoking prompt. Escalate to **Full** for mixed/unknown paths or an unresolved classifier result.

Important current-state caveat: the worktree currently reports the entire new plugin and related files as untracked, so the classifier returns **Full**, not Quick. Quick can only be claimed against a clean/committed baseline that isolates this metadata-only diff. Otherwise retain Full and report why.

Relative skill files actually read:

- `SKILL.md`
- `agents/openai.yaml`
- `references/validation-profiles.md`
- `scripts/optimizer_config.py`