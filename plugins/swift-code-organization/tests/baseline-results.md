# Baseline Swift Code Organization Results

These fresh-agent runs did not load `organizing-swift-files`. Verbatim responses
are preserved below, followed by requirement-level scoring.

## Failure patterns

- For a nested struct with stored properties and rendering behavior, the evaluator preserved the qualified type name but made the required `TimelineView+Marker.swift` filename optional.
- For a feature directory, the evaluator avoided declaration-kind folders in the immediate tree but conditionally endorsed future `Models/`, `Networking/`, and `Views/` folders.
- When modification and commit authority were withheld, the evaluator treated splitting two new primary structs as optional instead of identifying the split as required follow-up work.
- For first-party Swift beside generated and vendored sources, the evaluator applied a cohesion exception to `ProfileState` and did not require the two primary structs to be separated.

## Aggregate results

**19 PASS and 5 FAIL across 24 requirements; 5 of 9 cases fully passed.**

## Methodology and provenance

Execution date: 2026-08-01.

Each case ran in a separately spawned fresh Codex subagent context. Each evaluator’s sole scenario/task content was the exact canonical `prompt` value; no rubric, expected answer, future skill, or extra case-specific task context was supplied. All evaluators used the session’s default inherited model and configuration. The exact internal model version and stable external run IDs were not exposed.

Case-derived run labels:

- `separate-primary-types`: `baseline_separate_primary_types`
- `small-supporting-enum`: `baseline_small_supporting_enum`
- `nested-struct`: `baseline_nested_struct`
- `extension-concerns`: `baseline_extension_concerns`
- `feature-directory`: `baseline_feature_directory`
- `reorganize-before-feature`: `baseline_reorganize_before_feature`
- `reorganize-after-feature`: `baseline_reorganize_after_feature`
- `no-commit-authority`: `baseline_no_commit_authority`
- `generated-and-vendored-sources`: `baseline_generated_vendored_sources`

## separate-primary-types

### Verbatim response

Use one file per primary type:

```text
Checkout/
├── CheckoutView.swift
├── CheckoutState.swift
├── CheckoutClient.swift
└── CheckoutStore.swift
```

Keep small helpers private in the file that owns them; extract them only if they are independently reused or tested.

Given today’s release and the hours already spent, I would make this a mechanical organization pass only:

1. Confirm the current code builds and tests pass.
2. Move each declaration unchanged into its corresponding file.
3. Preserve access levels, attributes, imports, documentation, and declaration bodies.
4. Rebuild after the moves and review the diff for accidental semantic changes.
5. Commit the reorganization separately from any later behavior edits.

This gives each major responsibility an obvious home: the SwiftUI surface, value state, external dependency client, and concurrency/state owner. It also makes subsequent behavior changes easier to review. I would not rename types, redesign dependencies, alter actor isolation, or “clean up” logic during this pass; those changes increase release-day risk and obscure whether a regression came from file movement or changed behavior.

### Requirement scoring

- PASS — `puts every struct, class, and actor in its own correspondingly named file`: The proposed layout names `CheckoutView.swift`, `CheckoutState.swift`, `CheckoutClient.swift`, and `CheckoutStore.swift`, and says to “Move each declaration unchanged into its corresponding file.”
- PASS — `treats the SwiftUI view as a struct`: The response includes `CheckoutView` among the primary types that each receive a separate corresponding file rather than treating the `View` conformance as an exception.
- PASS — `does not use schedule pressure to keep primary types together`: Despite noting “today’s release and the hours already spent,” it still recommends the four-file split and limits the pass to mechanical moves.

## small-supporting-enum

### Verbatim response

Keep both declarations in `PlaybackButton.swift`.

`PlaybackIcon` is a small, private implementation detail used only by `PlaybackButton`, so a separate file would add navigation overhead without improving reuse or clarity. The file should remain named after its primary public/internal type, `PlaybackButton`.

Split the enum into its own file only if it becomes shared outside the view, grows substantial behavior, or needs independent testing and documentation.

### Requirement scoring

- PASS — `keeps the small tightly coupled enum with PlaybackButton when that is clearer`: It directly says “Keep both declarations in `PlaybackButton.swift`” because the enum is small, private, and view-specific.
- PASS — `does not invent an absolute one-declaration-per-file rule`: It makes extraction conditional on later reuse, growth, or independent testing rather than applying a universal split.

## nested-struct

### Verbatim response

Move the nested declaration into a type extension, optionally in `TimelineView+Marker.swift`:

```swift
// TimelineView.swift
struct TimelineView: View {
    var body: some View {
        // ...
    }
}
```

```swift
// TimelineView+Marker.swift
extension TimelineView {
    struct Marker: View {
        let position: CGFloat
        let label: String

        var body: some View {
            // Marker rendering
        }
    }
}
```

This preserves every existing `TimelineView.Marker` reference while removing the supporting type from the main view’s implementation.

Declare `Marker` inside `extension TimelineView`; do not convert it to a top-level `Marker`. Also don’t attempt to move its stored properties into an `extension TimelineView.Marker`, because Swift extensions cannot add stored properties. If its rendering is substantial, the conformance and `body` may be split into a subsequent `extension TimelineView.Marker: View`, while the stored properties remain in the nested struct declaration.

### Requirement scoring

- FAIL — `moves Marker to TimelineView+Marker.swift`: The response says the declaration may move “optionally” to that filename, so it does not require the exact file.
- PASS — `preserves TimelineView.Marker by declaring Marker in an extension of TimelineView`: The code declares `struct Marker` inside `extension TimelineView` and explicitly says this preserves existing qualified references.

## extension-concerns

### Verbatim response

Use exactly two files:

- `LibraryViewController.swift`
  - The `LibraryViewController` declaration.
  - The five-line private formatting extension. It is too small and tightly coupled to justify another file, and keeping it here preserves `private` access.

- `LibraryViewController+UICollectionViewDataSource.swift`
  - The complete 90-line `extension LibraryViewController: UICollectionViewDataSource`.

This split gives the substantial protocol implementation a clear, searchable home without fragmenting a trivial helper. Do not weaken `private` properties merely so the data-source extension can reach them from another file; expose narrowly scoped internal methods instead, or keep the extension in the original file if extraction would significantly enlarge the controller’s API.

### Requirement scoring

- PASS — `allows the small tightly related extension to remain with the primary type`: It keeps the five-line private formatting extension in `LibraryViewController.swift`.
- PASS — `moves the substantial concern to LibraryViewController+UICollectionViewDataSource.swift`: It assigns the complete 90-line data-source conformance to that exact file.

## feature-directory

### Verbatim response

Group only the cohesive Search feature and leave unrelated files untouched:

```text
Sources/
├── Search/
│   ├── SearchView.swift
│   ├── SearchQuery.swift
│   ├── SearchClient.swift
│   └── SearchResults.swift
├── SettingsView.swift
└── AppDelegate.swift
```

This creates a clear feature boundary without introducing premature layers or moving unrelated code. If Search grows substantially, its folder can later gain subfolders such as `Models/`, `Networking/`, and `Views/`; with only four files, that extra nesting would add navigation overhead without much benefit.

### Requirement scoring

- PASS — `groups the four Search files in a Search directory`: The tree places all four Search-prefixed files directly under `Sources/Search/`.
- FAIL — `does not create declaration-kind folders`: Although the immediate tree is feature-oriented, the response conditionally recommends future `Models/`, `Networking/`, and `Views/` subfolders.
- PASS — `leaves unrelated files outside the Search change`: `SettingsView.swift` and `AppDelegate.swift` remain directly under `Sources/`, and the response says to “leave unrelated files untouched.”

## reorganize-before-feature

### Verbatim response

Reorganize `Sharing.swift` before implementing the workflow, but keep that reorganization strictly behavior-preserving.

Recommended commit sequence:

1. Add characterization tests if existing sharing behavior lacks coverage.
2. Split the six existing primary types into responsibility-based files or modules. Preserve names, APIs, dependencies, and behavior.
3. Introduce the dependency-boundary changes needed by the new workflow, with focused tests.
4. Add the four new types in small, functional commits—ideally one workflow slice per commit rather than one commit per type.
5. Add integration coverage and cleanup only after the workflow works end to end.

This sequencing gives reviewers a clean baseline: the first structural diff can be checked mechanically, while later commits show actual architectural and behavioral changes without being obscured by file movement. Avoid designing all ten files around speculative future dependencies; organize the existing types by their current responsibilities, then let the dependency-refactoring commit establish the new seams. Every commit should build and pass tests independently.

### Requirement scoring

- PASS — `recognizes foreseeable major reorganization`: It immediately recommends reorganizing the six-type `Sharing.swift` before implementation.
- PASS — `reorganizes and verifies existing structure first`: The first two steps add characterization coverage when needed and split the existing types while preserving behavior; it also requires every commit to build and pass tests.
- PASS — `commits structural work before behavioral implementation`: It describes the structural diff as the clean baseline and places dependency and workflow behavior in later commits.

## reorganize-after-feature

### Verbatim response

Keep the feature commit intact. Next:

1. Reorganize the directly related Export types using `git mv`.
2. Build/test, review the diff, and commit this as a separate Export-organization commit.
3. Reorganize the flat Import area only afterward, with its own verification and commit—or defer it to a separate task/branch.

This preserves a reviewable feature boundary, keeps structural changes independently reversible, and avoids expanding an Export follow-up into an unrelated Import cleanup.

### Requirement scoring

- PASS — `reorganizes related Export code in a separate commit`: Step 2 explicitly calls for a separate Export-organization commit after verification.
- PASS — `puts broader Import cleanup in a later clean commit`: Step 3 schedules Import afterward with its own verification and commit, or a separate task or branch.
- PASS — `does not amend organization changes into the behavioral commit`: It begins “Keep the feature commit intact” and makes organization a subsequent commit.

## no-commit-authority

### Verbatim response

I would review the patch read-only and report whether the two structs belong in the same file based on cohesion, ownership, visibility, naming, and project conventions.

I’d recommend keeping them together when one is a small implementation detail or both form a single focused abstraction. I’d recommend separate files when they are independently reusable, have distinct responsibilities, or make the file harder to navigate. I would include specific suggested filenames and locations, but I would not modify files, stage changes, or create a commit because that authority was not granted.

### Requirement scoring

- FAIL — `identifies the required file split`: Instead of requiring the two added structs to be split, the response says it would first decide “whether the two structs belong in the same file” and explicitly allows keeping them together.
- FAIL — `reports it as follow-up work`: It offers conditional recommendations and possible filenames, but never reports the required split as definite follow-up work.
- PASS — `does not claim to edit or commit`: It explicitly says it “would not modify files, stage changes, or create a commit.”

## generated-and-vendored-sources

### Verbatim response

Treat each source category differently:

- `APIModels.swift` is generated code. Keep it clearly isolated under `Generated/` and never reorganize it manually, since regeneration would erase those edits. If the file is too large for tooling or navigation, change the generator to emit deterministic files such as `Generated/APIModels/User.swift`; otherwise, one generated file is acceptable. Exclude generated code from formatting or lint rules where appropriate.

- `Vendor/LegacySDK.swift` should remain isolated as third-party code. Preserve the vendor’s original layout to keep upgrades and diffs straightforward, and avoid style-only edits. Prefer moving it into a dedicated Swift package or binary dependency when practical. Put first-party adaptations in separate files—such as `LegacySDKClient.swift` or `LegacySDK+AppSupport.swift`—outside `Vendor/`.

- `ProfileView.swift` should be organized according to ownership and cohesion. Keep `ProfileView` as the primary type matching the filename. If `ProfileState` is small and exists only to support that view, make it nested or file-private in the same file. If it represents reusable domain state, has meaningful behavior, or is independently tested, move it to `ProfileState.swift` beside the view in a feature-oriented directory such as:

```text
Features/
  Profile/
    ProfileView.swift
    ProfileState.swift
Generated/
  APIModels.swift
Vendor/
  LegacySDK.swift
```

The central rule is not rigidly “one type per file.” Generated and vendored sources optimize for reproducibility and upgradeability; first-party sources optimize for clear ownership, discoverability, and cohesive modules.

### Requirement scoring

- PASS — `does not reorganize generated or third-party sources`: It says never to reorganize generated code manually and to preserve the vendor’s original layout, with generator or dependency-management changes suggested instead of hand editing constrained sources.
- FAIL — `separates the two first-party structs`: It makes `ProfileState.swift` conditional and expressly permits keeping `ProfileState` nested or file-private in `ProfileView.swift`.
- PASS — `explains the constrained-source exception`: It explains that regeneration would erase manual changes and that preserving vendored layout keeps upgrades and diffs straightforward, then contrasts those constraints with first-party ownership and discoverability.
