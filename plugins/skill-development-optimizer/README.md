# skill-development-optimizer

Portable guidance and local tooling for choosing validation effort that matches
the risk of an agent-skill change. The plugin contains one skill,
`optimizing-skill-development`. It complements `skill-creator` and
`writing-skills`: those skills explain how to author effective skills, while
this one classifies the change, selects proportionate checks, and preserves
reproducible evidence.

## Workflows

For a new skill or plugin, start with the **Full** profile. Copy the standalone
bootstrap configuration from
[`skills/optimizing-skill-development/assets/skill-optimizer.example.json`](skills/optimizing-skill-development/assets/skill-optimizer.example.json)
into the target repository, then replace its repository-relative target,
commands, and evaluation paths. The asset is self-contained; an installed
skill does not depend on this repository's own example configuration.

For maintenance, inspect the configured target, classify its changed paths,
and use the smallest reported profile that covers the semantic risk. Run only
that profile's declared commands. Behavioral work also freezes and hashes the
distributable artifact before a fresh evaluation cohort; importer work adds the
applicable acquisition or managed-store threat checks. Escalate uncertainty or
mixed categories to Full. A downgrade requires a recorded rationale showing
how every mandatory check remains satisfied.

## Validation profiles

- **Quick** checks packaging, metadata, adapters, installation prose, and
  focused tests.
- **Content** adds content contracts, examples, attribution, originality, and
  source-link checks.
- **Behavior** adds a frozen artifact and fresh, rubric-scored agent cases for
  changes that affect discovery, selection, workflow, judgment, or stopping.
- **Importer** covers external acquisition and managed persistent-store
  publication, locking, cleanup, and recovery.
- **Full** is the union of all applicable profiles for new plugins, releases,
  mixed categories, and unknown paths.

See
[`validation-profiles.md`](skills/optimizing-skill-development/references/validation-profiles.md)
for selection and downgrade rules.

## Command families

The six public command families are intentionally separate, readable Python
programs. Consult their built-in help instead of copying flags from this
README:

```bash
python3 skills/optimizing-skill-development/scripts/inspect_skill.py --help
python3 skills/optimizing-skill-development/scripts/classify_change.py --help
python3 skills/optimizing-skill-development/scripts/run_validation.py --help
python3 skills/optimizing-skill-development/scripts/hash_artifact.py --help
python3 skills/optimizing-skill-development/scripts/manage_evidence.py --help
python3 skills/optimizing-skill-development/scripts/manage_evidence.py complete --help
python3 skills/optimizing-skill-development/scripts/report_timing.py --help
```

The paths above assume the plugin root. In normal use, invoke the corresponding
installed script path while the working directory is the target repository and
pass its checked-in optimizer configuration. Inspection inventories the target;
classification selects a minimum profile; validation executes bounded,
argv-only configured commands; hashing identifies the distributable artifact;
evidence supports `init`, `complete`, `verify`, and `summarize`; timing separates
active work from waiting. `optimizer_config.py`, `evidence_schema.py`, and
`evidence_store.py` are supporting modules rather than additional command
families.

## Configuration and safety

Keep the target's JSON configuration in its repository, normally near the
repository root. Targets, include/exclude patterns, command working
directories, and evaluation files must remain repository-relative. Commands
are explicit argument arrays with time and output bounds; shell command strings
are not accepted. A command's `network` declaration and the explicit
`--allow-network` option form a declaration-and-approval gate: a command marked
as networked is not run without the opt-in. The runner does not OS-sandbox a
subprocess's network access, so configured argument arrays are trusted; a
command incorrectly declared with `network: false` could still access the
network. The optimizer itself does not initiate network requests automatically,
but invoked configured commands may. It does not automatically install
dependencies or perform destructive Git operations.

Inspection, classification, and timing are portable ordinary Python workflows.
Hashing additionally relies on secure descriptor-relative filesystem
operations; validation relies on bounded subprocesses and POSIX process-group
termination; and evidence owns a managed persistent store with immutable
publication, locking, recovery, and ownership-checked cleanup. Those secure
filesystem and process capabilities are POSIX-specific. When a required
operation or identity guarantee is unavailable, hashing, validation, and
evidence fail closed with a deterministic error; they do not fall back to
unsafe path-based mutation or incomplete child cleanup. No Swift toolchain is
required.

## Frozen evaluation evidence

Behavioral results bind exact prompts, verbatim responses, files-read reports,
rubric judgments, and run IDs to one `sha256-length-framed-v1` artifact. Use the
supported evidence `complete` command to publish results; do not modify its
private store. Any distributable byte change makes the cohort historical and
requires a new complete cohort before reporting a headline result. The bundled
[`forward-results.md`](tests/forward-results.md) and
[`evidence/final`](tests/evidence/final) record the plugin's reproducible
five-case, 40-check forward evaluation. See
[`frozen-evaluations.md`](skills/optimizing-skill-development/references/frozen-evaluations.md)
for the lifecycle and limits of agent-reported files-read evidence.

## Install

### Claude Code

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install skill-development-optimizer@danny-sung-agent-skills
```

### Codex

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add skill-development-optimizer@danny-sung-agent-skills
```

### Open skill installer

Install the individual skill for Codex (or replace `codex` with another
supported agent):

```bash
npx skills add dannys42/agent-skills \
  --skill optimizing-skill-development \
  --global \
  --agent codex
```
