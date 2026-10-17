# Roadmap: Synthetic

Design: SystemDesign/Overview.md
Updated: 2026-10-01 (synthetic fixture)

## Ladder (one line per rung, in order)

1. L1 — Can the server and client run together? [done]
2. L1b — Does the client get canned data? [done]
3. L2 — Can the server call the provider with a stored key? [done: with a caveat]
4. L3 — Can one day of data go Raw, then Derived, then onto a timeline? [in progress]
5. L3b — Can the client show it? [planned]
6. L4 — Can a rebuild equal the incremental result? [horizon]

## Why this order
Risk first.

## Rungs (detailed)

### L1: Skeleton
Prove the loop.

### L2: Authenticated call
Prove the key.

### L3: One day of data
Prove the pipeline.
- Done when: a timeline shows one day.

### L3b: Client chart
Show it.

## Learning log

- 2026-09-01 L1 (done): the pinned dependency was needed.
- 2026-09-02 L2 (done): no Keychain prompt appeared.
- 2026-09-05 L3 (spike): three values exist in the event column.
- 2026-09-06 L9 (done): this rung is not on the ladder.
