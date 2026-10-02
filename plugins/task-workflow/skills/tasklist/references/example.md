# Example: phased task list

A complete list mid-flight, showing every level, each closed state, and a qualifier. Counters are document-wide: `T6` appears once, under whichever group it belongs to.

```markdown
# TODO — Preferred Pronunciation

Source: Documentation/Decision-Preferred_Pronunciation.md

## P1 Data model
Goal: `isPreferred` is persisted and migrated; no UI yet.

### G1 Schema

- [x] T1 Add `isPreferred` to `PracticePronunciation`
  - Model: light (Haiku 4.5)
  - Context: Decision D04. Model lives in `Sources/Model/PracticePronunciation.swift`; default `false`.
  - Done when: project builds and `PracticePronunciationTests` pass

- [ ] T2 Migrate existing words to a single preferred pronunciation
  - Model: heavy (Opus 5.5)
  - Needs: T1
  - Context: Decision D07. Each word with pronunciations gets exactly one preferred, chosen by existing display order. Migration must be idempotent; user data is not recoverable.
  - Done when: migration test on a fixture store with 0, 1, and many pronunciations per word passes, and a second run changes nothing

- [-] T3 OBSOLETE — Add `preferredID` map on `Word`
  - Why: D04 chose a per-pronunciation flag instead (2026-10-02)

### G2 Queries

- [ ] T4 Expose preferred pronunciation on `WordSummary`
  - Model: standard (Sonnet 5.5)
  - Needs: T2
  - Context: Decision D05. Projection in `Sources/Query/WordSummary.swift`; must not trigger an extra fetch per row.
  - Done when: list screen shows the preferred pronunciation with no added fetches (verify with the existing fetch-count test)

## P2 Presentation
Goal: users can see and change the preferred pronunciation.

### G3 UI

- [ ] T8 USER — Confirm the word-list badge design
  - Context: T5 should not start until the badge style is chosen.
  - Steps:
    a. Open `Documentation/Mockups/word-list.png`.
    b. Pick badge style 1, 2, or 3.
    c. Reply with the number and any tweaks.
  - Done when: you reply with the chosen style number.

- [ ] T5 BLOCKED(T4) — Show preferred pronunciation in the word list
  - Model: standard (Sonnet 5.5)
  - Needs: T4, T8
  - Done when: snapshot tests updated and passing

- [-] T6 DEFERRED — Export preferred pronunciation to CSV
  - Model: light (Haiku 4.5)
  - Why: out of scope for first release (2026-10-02)

- [-] T7 INVALID — Remove the legacy `displayOrder` column
  - Why: column does not exist; ordering is derived from array position (2026-10-02)
```

## Short list

A single concern needs no headings or phases:

```markdown
# TODO — Importer crash fix

- [ ] T1 Reproduce the crash on malformed CSV headers
  - Model: light (Haiku 4.5)
  - Done when: a failing test captures the crash

- [ ] T2 Reject malformed headers with a descriptive error
  - Model: standard (Sonnet 5.5)
  - Needs: T1
  - Context: `CSVImporter.parseHeader` force-unwraps the first column.
  - Done when: T1's test passes; malformed input yields `ImportError.badHeader`
```
