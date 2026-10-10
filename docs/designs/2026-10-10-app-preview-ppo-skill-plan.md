# Plan: `app-preview-ppo` skill (plugin `app-store-growth`)

Status: **PARKED**. Resume after the App Store data tool exists (separate effort).
Date: 2026-10-10

## Purpose

Help decide what an App Store app preview video should show, and how to test it with
Product Page Optimization (PPO). Covers the lifecycle: plan the initial deployment,
collect data, report changes from the App Store, and refine from the user's manual
descriptions. Each step may run in a clean agent context, so state lives in files.

## Decisions made

| Decision | Choice |
|---|---|
| Plugin | New plugin `app-store-growth` (not `project-planning`, not `storytelling`). Same per-domain layout as existing plugins: README, CHANGELOG, `gemini-extension.json`, entry in `.claude-plugin/marketplace.json`. |
| Skill name | `app-preview-ppo` |
| Structure | **One skill with four modes** (plan, collect, report, refine). Split later only if `SKILL.md` outgrows 500 lines, or if collect/report become deterministic enough to move into the data tool. |
| Ledger location (in each app repo) | `docs/appstore/app-preview/` |
| Apple docs | Verify live against developer.apple.com and App Store Connect Help. No blogs. |
| `asc` CLI | Installed `asc` 5.14.1 (Homebrew). Check commands against `asc --help` rather than guessing. |
| Evals | Light: 3 prompts, with/without skill, assertions only on verifiable behavior (see Evals). |

## Modes

| Mode | Purpose | Reads | Writes |
|---|---|---|---|
| plan | Initial deployment plan | Ledger, app context | Hypotheses, storyboard, test design |
| collect | Data to refine judgment | Running experiments | Results snapshot per experiment |
| report | Updates and changes from the App Store | Last snapshot vs. current state | Change report, ledger entry |
| refine | Updates from the user's manual description | User input, ledger | Revised plan, decision entry |

A router at the top of `SKILL.md` picks the mode, reading `STATE.md` first.

## Ledger contract (`docs/appstore/app-preview/` in the app repo)

- `STATE.md`: short index. Current phase, live experiment, next action, links.
  Every clean context reads this first.
- `experiments/EXP-NNN-<slug>.md`: hypothesis, variants, locale, dates, results,
  decision, `app_context`.
- `decisions.md`: append-only log with dates and reasons, so later contexts do not
  re-litigate settled choices.

### `app_context` block (required in each experiment and snapshot)

App Store changes run on a different cycle from builds (dev builds, TestFlight,
production), so every record notes:

- **Store state:** live App Store marketing version, build number, release date,
  review state.
- **Pending state:** any TestFlight build or in-review version that could change the
  product page soon.
- **Version change in window:** whether a version change fell inside the test window
  (confound flag).

Why: preview footage may not match the live UI; a release mid-test can change ratings,
"What's New" or icon and confound results.

## Skill content outline

`SKILL.md` (under 500 lines): router, workflow checklist
(hypothesis -> storyboard -> capture -> upload -> test -> decision), common mistakes,
pointers to references. Trigger description: PPO, app preview, A/B test product page,
preview video strategy (pushy, per skill-creator guidance).

`references/`:

1. `apple-rules.md`: PPO mechanics and preview constraints. Every fact has a doc URL
   and a "verified on <date>" line. Unconfirmed items marked **UNVERIFIED**.
   - PPO: up to 3 treatments vs. original; testable assets (icon, screenshots,
     previews); previews/screenshots reviewed separately from the binary while icons
     ship in the binary; per-localization scoping; traffic split; reporting
     (conversion rate, confidence, improvement range); minimum duration and
     impressions; low-traffic handling.
   - Preview constraints: length, count, formats, resolution per device,
     portrait vs. landscape, search vs. product page, in-app footage only, muted
     autoplay, poster frame selection.
2. `strategy.md`: choosing 1-3 distinct hypotheses (core "wow" feature vs. problem vs.
   social/outcome), first 3-5 seconds, caption pacing and read time, directing the eye
   to a tap target (spotlight, ring pulse, hold after action), per-scene time budget
   worksheet, what to cut when over budget.
3. `measurement.md`: what to record, how to read results, when to declare a winner,
   template to append to the project's metrics docs. Prefer `asc` for data pulls.
4. `ledger-templates.md`: `STATE.md`, experiment, and decision templates, plus the
   snapshot format.
5. `manual-intake.md`: template for pasting numbers from the ASC web UI with required
   fields and a validity check. Likely the main data path if `asc` does not expose
   PPO results (to verify in research).
6. `low-traffic.md`: fallback to sequential before/after comparison, with loud
   confound warnings. Do not present it as a real A/B test.
7. `data-tool-interface.md`: the interface the skill expects from the data tool
   (see below), with the manual-paste fallback.

## Data tool dependency (the reason this is parked)

Decision direction: build a dedicated App Store data collection tool so the skill can
query just what it needs. Reasons: queries over stored history ("what was live on date
X?", "what changed since last snapshot?"), deterministic pull/normalize/diff, no agent
tokens spent parsing raw `asc` JSON, and clean contexts only ask questions.

To be designed in a **separate clean context**:

- Form: small CLI wrapping `asc`, script bundle, or standalone repo.
- Storage: SQLite vs. JSONL vs. markdown snapshots; per app, in-repo, or under `~/`.
- Scope: versions and review state, PPO tests, analytics reports
  (see the `asc-analytics-reports` skill).
- What `asc` 5.14.1 can actually expose for PPO and previews (unknown until researched).

The skill will call a defined interface, tentatively `app-preview-data <query>`, with
a manual-paste fallback so it works before the tool exists. Leave a marked
`TODO: storage` hook until the tool design settles.

Small snapshots to store regardless of tool: the numbers behind each decision
(impressions, CVR, confidence, dates) and the store/review state needed for the
"report" diff.

## Evals (light)

Three prompts, with-skill vs. without-skill:

1. **Plan:** habit-tracking iOS app, about 400 impressions/day, no preview yet. Plan
   the first preview and how to test it.
2. **Low traffic:** about 30 impressions/day; can we run a PPO test on the preview?
   Expect a fallback plan with caveats, not a test design.
3. **Refine:** ASC shows Treatment A at +6% (range -2% to +14%), 11 days in; ship it?
   Expect: reads the interval correctly, does not declare a winner, writes a ledger
   entry.

Assertions only on verifiable behavior: cites a source for every Apple limit, marks
unverified items, does not declare a winner when the interval crosses zero, writes to
the ledger. Strategy quality is judged by the user in the viewer.

## Resume checklist

1. Data tool exists, or its spec is settled; confirm `app-preview-data` interface.
2. Confirm plugin/skill names still `app-store-growth` / `app-preview-ppo`.
3. Research Apple docs (WebSearch/WebFetch) and `asc` 5.14.1 capabilities; fill
   `apple-rules.md` with sources and verified dates.
4. Scaffold plugin, write skill via `skill-creator`, run the three evals, review in
   the viewer.
5. Run description optimization; register in `marketplace.json`; add README and
   CHANGELOG; bump version.
