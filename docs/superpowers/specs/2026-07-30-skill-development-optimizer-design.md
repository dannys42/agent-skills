# Skill Development Optimizer Design

**Date:** 2026-07-30

## Goal

Create a portable plugin that helps agents create and maintain skills with the
minimum validation work appropriate to the actual risk, while preserving
reproducible evidence for behavioral and release decisions.

The optimizer complements `skill-creator` and `writing-skills`. It does not
replace their authoring, test-first, or deployment guidance.

## Supported Environments

Package the optimizer for:

- Codex;
- Claude Code;
- Cursor;
- Gemini CLI;
- agents that support the open skill-directory convention.

Use Python 3 and its standard library for deterministic tooling. Do not add a
Swift CLI or require a Swift toolchain because the optimizer is
language-agnostic.

## Plugin Architecture

Create:

```text
plugins/skill-development-optimizer/
├── .codex-plugin/
├── .claude-plugin/
├── .cursor-plugin/
├── gemini-extension.json
├── skills/
│   └── optimizing-skill-development/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── references/
│       │   ├── validation-profiles.md
│       │   ├── frozen-evaluations.md
│       │   └── importer-threat-model.md
│       └── scripts/
│           ├── inspect_skill.py
│           ├── classify_change.py
│           ├── hash_artifact.py
│           ├── run_validation.py
│           ├── manage_evidence.py
│           └── report_timing.py
└── tests/
```

Add portable plugin and marketplace metadata using the repository's existing
adapter shapes.

## Skill Responsibilities

Keep `SKILL.md` below 500 words. It must:

- require `skill-creator` and `writing-skills` for authoring fundamentals;
- distinguish new-skill creation from existing-skill maintenance;
- identify the smallest adequate validation profile;
- require escalation when risk is mixed or uncertain;
- prohibit silent success for missing checks;
- require one frozen artifact for behavioral headline results;
- preserve failed and superseded evaluation history;
- direct agents to the detailed references only when applicable.

The skill orchestrates fresh-agent evaluation but does not implement agent
spawning itself. Host agents remain responsible for approvals and subagent or
thread management.

## Python Toolkit

Prefer multiple readable, task-focused scripts over one large CLI.

### `inspect_skill.py`

Inventory the target skill, resources, tests, plugin manifests, marketplace
adapters, and optional optimizer configuration. Produce deterministic human
and JSON output.

### `classify_change.py`

Compare a target against a Git base and classify changes by risk. Emit the
recommended validation profile plus reasons. Classification is advisory but
fail-safe: mixed or uncertain changes escalate.

### `hash_artifact.py`

Hash selected distributable files reproducibly. Sort normalized POSIX-relative
paths and frame each path and exact content with unambiguous lengths before
SHA-256 hashing. Exclude tests, caches, research, and evidence only when the
configuration says they are nondistributable.

### `run_validation.py`

Execute configured argv arrays without a shell. Restrict working directories
to the selected repository, apply timeouts and output bounds, capture exit
status and monotonic duration, and write atomic evidence. Never treat an absent
command as passing.

### `manage_evidence.py`

Initialize and verify frozen evaluation cohorts. Track artifact hash, run IDs,
exact prompts, verbatim outputs, files read, rubric results, and historical
status. Reject duplicate IDs, mixed hashes, missing artifacts, impossible
scores, and multiple headline cohorts.

Files-read evidence must be labeled as agent-reported unless independently
instrumented.

### `report_timing.py`

Aggregate phase and command timing, rank bottlenecks, and distinguish mandatory
external delay from avoidable iteration or review time.

Each script exposes small importable functions and a thin command-line entry
point. Add shared modules only when at least two scripts require the same
nontrivial invariant. Do not create generic utility modules for trivial path or
JSON operations.

## Configuration

Support an optional `skill-optimizer.json` for a target repository or plugin.
The schema declares:

- distributable include and exclude rules;
- validation commands as argv arrays;
- profile membership;
- command working directories, timeouts, and output limits;
- evaluation case and rubric locations;
- checks that require network access or external approval.

The toolkit may inspect an unconfigured target and suggest a configuration, but
it must not claim unavailable checks passed.

## Validation Profiles

### Quick

Use for metadata, adapter, or documentation-only changes that cannot alter
skill behavior. Validate structure, frontmatter, JSON, changed links, and
focused deterministic tests.

### Content

Use when references, examples, attribution, links, or domain guidance change.
Include quick checks plus content contracts, examples, attribution, originality,
and reference linkage.

### Behavior

Use when trigger descriptions, selectors, workflows, mandatory rules, or agent
judgment change. Include a frozen artifact, clean fresh-agent evaluation,
files-read evidence, and rubric verification.

### Importer

Use when external acquisition, caching, retry, redirect, pacing, or filesystem
code changes. Include deterministic importer tests and the hostile-cache threat
model. Run real network or delay checks only at explicit milestones with
required approval.

### Full

Use for releases, broad cross-category changes, new plugins, and uncertain
changes. Run every applicable profile.

Agents may always escalate. They may downgrade only with a recorded rationale
and no skipped mandatory checks.

## Workflows

### New skill

1. Use `skill-creator` and `writing-skills` to define examples and capture
   failing baseline behavior.
2. Inspect the scaffold and establish explicit optimizer configuration.
3. Run quick checks after scaffolding.
4. Run content checks while adding references and examples.
5. Run behavior checks only when the skill controls judgment or workflow.
6. Run importer checks only when external acquisition or caching exists.
7. Freeze one final artifact and run the full profile before release.

### Existing skill

1. Inventory the target and compare against a Git base.
2. Classify changed paths and content with explicit reasons.
3. Select the minimum adequate profile.
4. Escalate mixed or uncertain changes.
5. Record validation evidence and timing.
6. Invalidate behavioral results whenever the distributable hash changes.

## Safety

- Execute no configured command through a shell.
- Reject working directories outside the selected repository.
- Apply explicit timeouts and bounded output capture.
- Perform no destructive Git operation.
- Mark networked checks separately so the host agent can obtain approval.
- Use atomic evidence writes.
- Fail closed on malformed configuration or incomplete evidence.
- Use monotonic clocks for durations and wall-clock timestamps only for display.

## Test-First Development

Before creating the optimizer skill, capture baseline behavior from fresh agents
without it. Include scenarios where agents:

- over-test a metadata-only edit;
- under-test a selector or trigger-description change;
- overlook attribution after a reference edit;
- mix outputs from different artifact versions;
- treat missing commands or files-read evidence as passing;
- change importer code without hostile-cache or pacing tests.

Implement the smallest skill guidance and tooling that corrects observed
failures, then rerun the same cases with the skill.

## Deterministic Test Coverage

Test:

- stable artifact hashes and explicit selection rules;
- malformed, absolute, traversal, and escaping paths;
- risk classification for metadata, content, behavior, importer, and mixed
  changes;
- profile escalation and downgrade rationales;
- non-shell command execution, timeouts, and output bounds;
- atomic evidence writes;
- mixed hashes, duplicate runs, missing outputs, invalid scores, and competing
  headline cohorts;
- timing aggregation and bottleneck ranking.

## Forward Testing

Use fresh agents on both new-skill and maintenance scenarios. Give each agent
only the user request and the frozen optimizer artifact. Do not provide expected
answers, baseline results, diagnoses, or suspected fixes.

Every final cohort must record:

- one reproducible artifact hash;
- exact prompts and verbatim responses;
- run IDs;
- self-reported or independently observed files read;
- explicit rubric judgments;
- one authoritative headline result.

Any distributable change invalidates the cohort.

## Success Criteria

- Metadata-only changes select `quick`.
- Reference and example changes select `content`.
- Trigger, selector, workflow, and mandatory-rule changes select `behavior`.
- External acquisition and cache changes select `importer`.
- Releases, new plugins, and broad mixed changes select `full`.
- Missing checks remain visible and never count as passing.
- Inspect, classify, and hash overhead remains below roughly one second on a
  normal skill.
- `SKILL.md` remains under 500 words.
- All portable manifests and marketplace adapters validate.
- The optimizer measurably avoids unnecessary full validation without weakening
  the evidence required for high-risk changes.
