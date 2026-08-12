# Repository skill-publishing rules

When adding a skill or plugin, keep every discovery surface in sync.

## Required registration

For each new skill:

1. Put the skill at `plugins/<plugin>/skills/<skill>/SKILL.md`.
2. Include `name`, `description`, and `license: GPL-3.0-or-later` in the
   `SKILL.md` frontmatter. The skill directory name must match `name`.
3. Register the plugin in `.claude-plugin/marketplace.json` with its relative
   `source` and `skills: "./skills/"`. The `skills` field is required for the
   `npx skills` CLI to discover skills inside a plugin that does not have a
   Claude plugin manifest.
4. Register the plugin in `.agents/plugins/marketplace.json` so Codex can list
   it.
5. Update the root `README.md` skill table and installation section, and add or
   update the plugin's agent metadata and other marketplace adapters when the
   plugin supports them.

## Verification before handoff

Run these checks from the repository root:

```bash
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
npx skills add . --list
```

The local skills CLI output must include the newly added skill and report the
expected total count. Also run `git diff --check`. After pushing, verify the
same result with `npx skills add <owner>/<repo> --list`; the remote repository
must contain the marketplace registration before users can discover the skill.
