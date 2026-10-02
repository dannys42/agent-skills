# Frozen Evaluations

Use a frozen evaluation for behavioral validation: triggering, selection,
mandatory workflow, judgment, and stopping criteria. Bind all headline results
to one byte-identical distributable artifact.

## Required sequence

1. Finish deterministic checks.
2. Hash the exact distributable artifact.
3. Initialize one cohort against that hash.
4. Give each fresh agent only its case prompt and frozen skill.
5. Capture prompt, verbatim response, run ID, and files read separately.
6. Score from the declared rubric.
7. If any distributable byte changes, mark the cohort historical and restart every headline case.
8. Keep exactly one headline cohort.

Do not edit the frozen artifact while a cohort is active. Keep older cohorts as
historical evidence, but never combine results from different artifact hashes
into a cross-version aggregate headline. A result belongs to the artifact hash
recorded when its cohort was initialized.

Treat agent-reported files read as evidence, not independent instrumentation.
Record the report verbatim and separately from the response. Do not claim that
it proves operating-system access, tool invocation, or complete context
isolation. If independent instrumentation is required, collect and label it as
a distinct evidence source.

## Artifact identity

Use `sha256-length-framed-v1`. Normalize every selected file to a safe,
repository-relative POSIX path, reject duplicates, sort entries by path, and
hash each entry in this exact order:

1. the UTF-8 path byte length as an unsigned 8-byte big-endian integer;
2. the UTF-8 path bytes;
3. the content byte length as an unsigned 8-byte big-endian integer;
4. the unmodified content bytes.

Do not hash concatenated paths and contents without the length frames. Do not
include timestamps, executable bits, or absolute paths. Use the checked-in
configuration to select include and exclude patterns:

```bash
python3 path/to/hash_artifact.py CONFIG.json --json --output ARTIFACT.json
```

## Evidence lifecycle

Declare cases and rubric before initializing the cohort. Use one stable cohort
identifier and one evidence output:

```bash
python3 path/to/manage_evidence.py init \
  ARTIFACT.json CASES.json RUBRIC.json EVIDENCE.json --cohort COHORT_ID
```

Run every case with a fresh agent that receives only the case prompt and frozen
skill. Do not disclose expected profiles, rubric answers, earlier responses, or
suspected failures. Prepare schema-version-1 completion JSON containing the
cohort ID and exactly one run for every declared case:

```json
{
  "schema_version": 1,
  "cohort_id": "final",
  "runs": [
    {
      "case_id": "case-01",
      "response": "Verbatim agent response",
      "files_read": "SKILL.md\nreferences/validation-profiles.md\n",
      "files_read_kind": "agent-reported",
      "rubric": {
        "correct_profile": true,
        "mandatory_checks_present": true
      }
    }
  ]
}
```

Each run must contain exactly `case_id`, `response`, `files_read`,
`files_read_kind`, and `rubric`. Set `files_read_kind` to `agent-reported` or
`independently-observed`; no other value is accepted. The rubric object must
contain every and only the keys declared in `RUBRIC.json`, with boolean values.
The example assumes those two displayed keys are the complete declared rubric.
Do not supply a run ID: initialization owns the draft IDs, and the completion
API preserves them.

Publish the completion document through the supported interface:

```bash
python3 path/to/manage_evidence.py complete \
  EVIDENCE.json CASES.json RUBRIC.json COMPLETION.json
```

Verify before reporting or scoring:

```bash
python3 path/to/manage_evidence.py verify \
  EVIDENCE.json CASES.json RUBRIC.json --json
python3 path/to/manage_evidence.py summarize \
  EVIDENCE.json CASES.json RUBRIC.json --json
```

Stop if verification reports an incomplete run, artifact mismatch, undeclared
rubric key, prompt mismatch, duplicate run ID, missing file reference, or mixed
cohort. Fix the evidence process; never convert a missing check into a pass.
