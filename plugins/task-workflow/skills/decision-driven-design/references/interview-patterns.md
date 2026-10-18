# Interview Patterns

## Batch low-risk decisions

When several major decisions have a low-risk, reversible recommendation, or one that follows from an accepted principle, present them together for default acceptance:

```text
Recommendations for D05–D08 (reversible, follow from D02):

Needs your attention
⚑ D07 <topic>: <choice> (low confidence)
  Why: <a few words> · To settle it: <check or question>
  - <choice> (recommended). Pro: ... Con: ...
  - <alternative>. Pro: ... Con: ...

Everything else
- D05 <topic>: <choice> — <one-line reason>
- D06 <topic>: <choice> — <one-line reason>
- D07 ⚑ see above
Which option for D07? Reply only with the others you would change; the rest are accepted.
```

Flag at most three items in a batch: one you are unsure of (inferred, not checked, or it depends on the user's intent), or one whose reversal would touch several tasks. Give each why, what would settle it, and two options with a pro and con, recommended first; say "no real alternative" rather than invent one. With nothing to flag, leave the section out. Every item stays in the list, so nothing is accepted unseen.

Never batch identity, persistence, or migration decisions, or any decision whose options change the schema in materially different ways. Ask those one at a time.

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

## Failure modes

- Asking repository-discoverable questions.
- Running a full interview for a small, reversible feature.
- Asking low-risk decisions one at a time when they could be batched.
- Showing complete schemas on every turn.
- Treating a preference as an architecture requirement.
- Demanding exact preservation of behavior the current system never guaranteed.
- Designing both branches of an uncertain performance question without measuring.
- Letting a revised decision become an undocumented exception.
- Keeping the ledger only in conversation context.
- Generating tasks dependent on hidden conversation context.
