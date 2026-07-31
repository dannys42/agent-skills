Selected profile: **Quick**, conditional on an isolated diff changing only `interface.display_name` and/or `interface.short_description` in `agents/openai.yaml`. Changing `default_prompt` is behavioral and requires **Behavior** validation.

Validation plan:

1. Work from the repository root with `plugins/skill-development-optimizer/skill-optimizer.example.json`.
2. Establish a clean base containing only the intended edit. The current classifier reports **Full** because the plugin and unrelated files are untracked/mixed; that result cannot validate the isolated metadata patch.
3. Rerun deterministic inspection and classification with JSON output. Require a valid target and metadata-only/Quick classification.
4. Review the one-file diff and verify:
   - only `agents/openai.yaml` changed;
   - YAML parses and all strings remain quoted;
   - `short_description` is 25–64 characters;
   - display text accurately represents `SKILL.md`;
   - `default_prompt`, trigger metadata, instructions, references, scripts, manifests, and links are unchanged.
5. Run only the configured Quick profile:
   `python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py plugins/skill-development-optimizer/skill-optimizer.example.json quick --output <report.json>`
6. Preserve as evidence:
   - exact one-file diff;
   - inspector and classifier JSON;
   - Quick validation report, command, exit status, and tool/runtime version;
   - timing summary from `report_timing.py`;
   - base and resulting commit SHAs when available.
7. Skip artifact hashing/freezing, fresh-agent cohorts, rubric evaluations, importer/hostile-cache checks, live network checks, and whole-repository gates. They are unnecessary for isolated UI metadata.

Evidence status: inspection succeeded, but the current worktree classification is contaminated and reports Full; Quick evidence remains pending an isolated diff. No validation duration exists until the Quick report is run.

Stop and escalate if the diff is not one-file metadata-only, `default_prompt` changes semantically, classification remains Full/unknown, or any mandatory Quick check is missing or fails.

Relative skill files actually read:

- `SKILL.md`
- `agents/openai.yaml`
- `references/validation-profiles.md`
