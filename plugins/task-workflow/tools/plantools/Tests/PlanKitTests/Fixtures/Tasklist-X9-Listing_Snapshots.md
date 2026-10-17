# Tasklist — X9 Per-version listing snapshots

Source: Roadmap rung X9; brief SystemDesign/Rung-X9-Listing_Snapshots.md

## G1 Gate: what can the read-only key reach?
Goal: one read-only probe answers whether snapshots are possible at all.

- [x] T1 Probe the version endpoints with the read-only key
  - Model: standard (Sonnet 5.5)
  - Context: Counts and field names only; nothing real is saved. Check the assumed fact "every app has a live version" with a count over the stored apps.
  - Verify: `swift run Probe versions --count-only`
  - Done when: the probe prints one line per endpoint with its status

- [ ] T2 USER — Confirm the draft-version question with the owner
  - Context: T3 needs to know whether drafts count as a change.
  - Steps:
    a. Open the app in the web console and choose **App Store → Prepare for Submission**.
    b. Note whether a draft listing exists.
  - Done when: reply yes or no; do not paste screenshots with account data.

## G2 Fetch and archive
Goal: each snapshot lands in Raw once and verifies.

- [ ] T3 Add the snapshot fetcher
  - Model: standard (Sonnet 5.5)
  - Needs: T1, T2
  - Context: One Raw record per app per snapshot; see D37.
  - Done when: a fixture-backed test archives two snapshots and re-reading verifies both

- [ ] T4 Add the snapshot route
  - Model: light (Haiku 4.5)
  - Needs: T3
  - Context: Mirror the existing timeline route.
  - Done when: the route test returns 404 for an unknown app

- [-] T5 SUPERSEDED→T6 — Per-field change flag
  - Why: the flag moved to the derived event (2026-10-02)

- [ ] T6 Derive listing events
  - Model: heavy (Opus 5.5)
  - Needs: T3
  - Context: Replaces T5; an empty snapshot list yields no events.
  - Done when: the derive test covers empty, one and many snapshots

- [ ] T7 Export events to CSV
  - Model: light (Haiku 4.5)
  - Needs: T6
  - Done when: the export test passes

- [ ] T8 BLOCKED(waiting on the owner's date) — Mark the past campaign on the chart
  - Model: standard (Sonnet 5.5)
  - Why: the campaign date is not known yet (2026-10-03)
  - Done when: the marker appears at the confirmed date

## G3 Scheduler — DEFERRED
Goal: snapshots run on a schedule.

- [ ] T9 Schedule the snapshot job
  - Model: standard (Sonnet 5.5)
  - Needs: T3
  - Done when: the scheduler test shows one snapshot per interval

- [-] T10 DEFERRED — Hourly polling
  - Why: daily is enough for the first release (2026-10-03)
  - Done when: not applicable

## G4 Real run
Goal: the result is seen on real data.

- [ ] T11 Run one real snapshot and compare it with the console
  - Model: standard (Sonnet 5.5)
  - Needs: T4, T10
  - Run: `swift run Portal snapshot --once`
  - Done when: the listing text matches the console
