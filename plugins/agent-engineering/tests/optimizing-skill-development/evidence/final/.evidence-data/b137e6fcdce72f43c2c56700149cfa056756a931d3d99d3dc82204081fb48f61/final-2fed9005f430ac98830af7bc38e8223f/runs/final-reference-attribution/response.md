Selected profile: **Content** for an isolated attribution/reference and code-example correction. Provenance and example correctness are content risks; leaving `SKILL.md` unchanged avoids behavioral evaluation.

Validation plan:

1. Before editing, run `inspect_skill.py --json <config>` and `classify_change.py --json <config>`. Confirm the eventual diff contains only the intended reference/example files and no `SKILL.md` change. If the classifier reports Quick/metadata, semantic risk still raises this to Content.
2. State stopping criteria up front: stop on a failed/missing mandatory check, unsupported or ambiguous attribution, broken source link, example compile/typecheck failure, originality concern, `SKILL.md` diff, unrelated path, or newly mixed risk category.
3. Run `run_validation.py <config> content --output <report.json>`. Content includes Quick checks plus declared content contracts, changed links, examples, attribution, and originality.
4. Perform focused source-fidelity validation against the canonical attributed source. Record the canonical URL, revision/version or retrieval date, and a concise mapping showing that the corrected prose and example preserve the source’s roles and interactions.
5. Extract the example into the narrowest runnable fixture and compile/typecheck it with the relevant toolchain. For Swift, use a focused `swiftc -typecheck` fixture and retain exact command, Swift version, exit status, and output.
6. Run the repository’s configured originality audit. If its required research corpus/tool is unavailable, mark originality evidence unavailable and stop with incomplete evidence; do not report it as passing.
7. Finish with `git diff --check`, a path-scoped diff review, and an explicit `git diff -- SKILL.md` assertion showing no change.

Evidence to retain:

- Inspection and classification JSON.
- Content validation report.
- Exact changed-path list and final diff.
- Canonical-source identity and source-fidelity comparison.
- Link-check results.
- Example fixture plus compiler/typechecker version, command, output, and exit code.
- Originality audit result.
- Base commit and final patch/commit identity.
- Work time versus waiting time.

Frozen behavioral cohorts and artifact hashing are not required because no discovery, selector, mandatory workflow, judgment, or `SKILL.md` instruction changes. Importer threat-model checks, live-network importer tests, and the complete plugin suite are also out of scope unless the diff expands. Escalate to Behavior if instructional wording changes, and to Full for mixed categories, unknown paths, release work, or unrelated changes.

The current worktree-wide classifier reports `full` because the worktree contains many unrelated untracked behavior, production, metadata, test, and unknown paths. That result must not be used as evidence for the hypothetical isolated correction; rerun classification on the clean, scoped change.

Relative target-skill files actually read:

- `SKILL.md`
- `references/validation-profiles.md`