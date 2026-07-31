---
name: optimizing-skill-development
description: Use when creating or changing an agent skill and validation effort risks being disproportionate, incomplete, non-reproducible, or mixed across artifact versions.
---

# Optimizing Skill Development

**REQUIRED SUB-SKILLS:** Use `skill-creator` and `writing-skills` for authoring fundamentals. Use `test-driven-development` for executable tooling.

## Core rule

Choose the smallest profile that covers the actual risk. Escalate uncertainty; never count a missing check as passing.

When asked for a validation plan, classify the stated change and plan its checks without requesting implementation details such as replacement wording. Do not edit unless asked to implement.

## Select the profile

1. Distinguish new creation from maintenance. Use `full` for a new plugin or release.
2. Read [validation-profiles.md](references/validation-profiles.md) first. Do not load unrelated profile references; count unnecessary reference loading as failing `unnecessary_checks_avoided`.
3. If no target configuration exists, copy `assets/skill-optimizer.example.json` into the target repository and edit its repository-relative target, command, and evaluation paths. Run optimizer scripts from that repository root.
4. Before naming or selecting any profile, run `scripts/inspect_skill.py` and `scripts/classify_change.py` against the target configuration. Use their outputs; do not reimplement deterministic inspection or classification.
5. Use `content` for references, examples, attribution, or source links. Do not load behavioral or importer references.
6. Use `behavior` for trigger descriptions, selectors, mandatory workflows, or judgment changes. Only then read [frozen-evaluations.md](references/frozen-evaluations.md) and freeze the artifact.
7. Use `importer` for fetching, retries, redirects, pacing, cache, or managed persistent-store publication, locking, and recovery. Ordinary source/document editing is not importer work. Only then read [importer-threat-model.md](references/importer-threat-model.md); apply network threats only when acquisition exists.
8. Use `full` for mixed categories, unknown paths, uncertainty, new plugins, and releases; read only references for applicable risks.

Run only checks declared by the selected configured profile through `scripts/run_validation.py`. Do not add whole-repository or unrelated-profile checks unless that profile declares them or risk escalates. Hash distributable behavioral artifacts with `scripts/hash_artifact.py`, manage cohorts with `scripts/manage_evidence.py`, and record work versus waiting time with `scripts/report_timing.py`. Use each script's `--help` for its interface.

Downgrade only with a recorded rationale. List every mandatory check from the original profile and show how it remains satisfied; otherwise retain the higher profile.

## Report and stop

Report the selected profile, risk reasons, checks run and skipped, artifact identity, evidence status, duration, and the next escalation condition. State stopping criteria before running checks. Stop on any failed or missing mandatory check, evidence/artifact mismatch, newly mixed category, unknown path, or need for unapproved live network access. Never report an unavailable check as passing.
