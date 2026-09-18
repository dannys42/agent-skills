# Interview Patterns

## Revision protocol

```text
Earlier decision D02 is superseded by the confirmed choice: <choice>.
This invalidates D05 and D07 because <dependency>. D03 remains valid.
I will reopen D05 next.
```

Do not replay unaffected questions or preserve an exception merely to avoid revising a ledger entry.

## Evidence gate

```text
Measure compressed size and installed footprint.
If the result is below <threshold>, use automatic download.
Otherwise, prompt before download.
Record the threshold as a product policy, not a platform convention.
```

## Abstraction challenge

For every proposed layer or type, ask: does behavior vary, does it concentrate real policy, would deleting it spread meaningful complexity, is it needed now, and can a stable ID or value interface preserve the inexpensive future seam?

## Avoid over-interviewing

For a small reversible feature, resolve only decisions affecting user-visible behavior, public interfaces, persistence, migration, or task boundaries. Resolve the rest autonomously and state assumptions briefly.

Before requiring exact preservation of a migrated value, check what it was actually attached to pre-migration — the entity, or a position/index/derived slot instead. A goal like "make X stick to the entity" implies it didn't before, which should lower the fidelity bar, not raise it.

## Failure modes

- Asking repository-discoverable questions.
- Showing complete schemas on every turn.
- Treating a preference as an architecture requirement.
- Designing both branches of an uncertain performance question without measuring.
- Letting a revised decision become an undocumented exception.
- Generating tasks dependent on hidden conversation context.
