# Validation Profiles

Choose the smallest profile that covers the actual risk. Classify changed paths
before selecting checks; do not infer risk only from file extensions or diff
size. Semantic risk overrides a lower path-based classification. For example,
an attribution or source-link edit in a README or installation-prose path
requires Content even if the path classifier reports metadata and Quick.

| Change | Minimum profile | Mandatory evidence |
|---|---|---|
| UI metadata, adapter JSON, installation prose | Quick | Structure, JSON, changed links, focused tests |
| References, examples, attribution, source links | Content | Quick plus content contracts, examples, attribution, originality |
| Trigger description, selector, mandatory workflow or judgment | Behavior | Frozen artifact, fresh cases, files read, rubric |
| Fetching, retries, redirects, pacing, cache or filesystem writes | Importer | Deterministic tests plus hostile-cache checks; approved live check at milestones |
| New plugin, release, mixed categories, unknown paths | Full | Every applicable profile |

## Apply the profiles

Use **Quick** for packaging and presentation changes that cannot alter an
agent's instructions. Validate directory structure, manifests and adapter JSON,
links changed by the patch, and focused tests for the affected surface.

Use **Content** when correctness, provenance, or examples change. Run Quick,
then check declared content contracts, example accuracy, attribution and source
links, and originality. Treat missing attribution or an unverifiable example as
a failed check, not a warning.

Use **Behavior** when wording can affect discovery, selection, required steps,
judgment, or stopping criteria. A `SKILL.md` wording edit is behavioral unless
a deterministic comparison proves it cannot affect triggering or instructions.
Freeze the exact distributable artifact and evaluate it with fresh cases. Record
the case prompts, run IDs, responses, files reported as read, and declared
rubric results. Follow `frozen-evaluations.md` for cohort integrity.

Use **Importer** only for external acquisition or cache code. Run deterministic
tests for request policy and hostile filesystem state. Read
`importer-threat-model.md` and cover every applicable threat. Perform a live
network check only at an explicit milestone and only after obtaining required
approval.

Use **Full** for a new plugin, a release, multiple risk categories, or paths the
classifier cannot establish safely. Full means the union of every applicable
profile; it is not a substitute for naming the individual risks and evidence.

## Escalate and downgrade

Escalate to Full when more than one non-test category changes. Test-only changes
do not trigger that rule, but their subject still determines which focused
checks are necessary. Escalate uncertainty: unknown paths, ambiguous
classification, or incomplete inspection must never reduce validation.

Downgrade only with a written rationale that cites deterministic evidence for
the lower risk. List every mandatory check from the original profile and show
where it is still satisfied. If any mandatory check is omitted, cannot run, or
produces missing evidence, do not downgrade and do not count it as passing.
