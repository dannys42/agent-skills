# Changelog

## 1.0.1

- `audit-token-efficiency` now writes its backlog in the `tasklist` format
  (document-wide IDs, `Model: tier (name)`, `Done when`) and recommends
  `Sonnet 5.5` instead of `Sonnet 5`
- It can append findings to a caller-named TODO file instead of
  `TODO-TokenEfficiency.md`, so a task runner can queue them in its own list

## 1.0.0 — consolidation

- Consolidated the former `skill-development-optimizer` and
  `audit-token-efficiency` plugins into `agent-engineering`
- Skill names are unchanged; install `agent-engineering` instead of the old plugins
