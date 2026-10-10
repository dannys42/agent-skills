# Apple-platform guidance

Use this when the project targets macOS, iOS, iPadOS, watchOS, tvOS, or visionOS. It supplies defaults to propose, decisions that need the user, and risks that tend to belong in the register. These are starting points, not rules: version-specific facts change every year, so mark anything you are not sure of as "verify against current docs" and let the roadmap's early increments prove it.

## Defaults to propose (and flag as assumptions)

- **Language and UI:** Swift, SwiftUI first. Drop to AppKit/UIKit through representables when SwiftUI cannot do the job (rich text editing, custom drawing performance, printing, fine window control, some drag and drop). Say which parts you expect to need that.
- **Project shape:** an Xcode app project, with testable logic in a local Swift package or a separate target so it can be tested and run without the UI.
- **Concurrency:** Swift Concurrency (async/await, actors) for background work; keep heavy computation off the main actor.
- **Persistence:** pick by what the user sees.
  - The user opens, saves, and shares files → **document-based app** (`DocumentGroup` with a `FileDocument` or `ReferenceFileDocument`, or `NSDocument`), with a defined file type (UTType) and format.
  - Structured app-managed data → SwiftData or Core Data (check the minimum OS for SwiftData).
  - Simple preferences → `UserDefaults` / `@AppStorage`.
  - Prefer plain, inspectable file formats (JSON, property list, package) unless there is a reason not to.
- **Testing:** Swift Testing for logic, XCTest/XCUITest for UI, run through `xcodebuild` so an agent can verify without opening Xcode.
- **Minimum OS:** choose it deliberately; it decides which APIs exist (Observation, SwiftData, newer SwiftUI features).

## Decisions that usually need the user

- **Platforms:** one platform, or multiplatform (shared logic, per-platform UI)? Multiplatform multiplies the UI and risk surface; confirm it is wanted now, not "later".
- **Distribution:** Mac App Store, Developer ID with notarization, TestFlight/App Store for iOS, or personal use only. This drives sandboxing, entitlements, signing, review rules, and whether a paid developer account is required.
- **Sandbox and permissions:** file access, network, printing, camera, and other entitlements the design implies.
- **Accounts and services:** iCloud/CloudKit sync, in-app purchase, push, or sign-in all require capabilities and a paid account; each is its own risk.
- **Accessibility and localization:** whether VoiceOver, Dynamic Type, and multiple languages are in scope now.
- **Cross-app integration:** share sheet, App Intents/Shortcuts, widgets, Quick Look, Spotlight. List them as scope, not afterthoughts.

## Risks that often belong in the register

Seed the register with the ones that apply, then rank them for this project.

| Area | Typical unknown | Cheapest probe |
| --- | --- | --- |
| Skeleton | Does a signed app build, run, and launch on the target? | Smallest app that builds and runs, from the command line and in Xcode |
| Drawing | Can SwiftUI `Canvas`/`Path` or Core Graphics draw this at the needed fidelity and speed? | Draw the project's most basic repeated element |
| Text | Do fonts, sizing, color, and baselines read well at screen and print scale? | Render representative text at target sizes |
| Printing / PDF | Does output match the screen (page size, margins, vector quality)? | Export a PDF, print one page |
| Documents | Does the file type, open/save, and versioning behave as designed? | Round-trip a document through save and reopen |
| Performance | Does the core computation stay responsive at realistic size? | Time it with a realistic input, off the main thread |
| Sync | Do CloudKit/iCloud conflicts and capabilities behave? | Two-device round trip |
| Distribution | Will signing, notarization, sandbox, or review block shipping? | A signed, notarized build early if distribution matters |
| Platform API | Is the needed framework API available at the chosen minimum OS? | Call it in a throwaway target |

## Effects on the design document

- Section 7 (data): say whether the document is the file (document-based) or an app database; this decides the entire persistence story.
- Section 8 (architecture): show the logic core separate from the SwiftUI layer so the roadmap can prove logic with no UI.
- Section 10 (technology): record the SwiftUI vs AppKit/UIKit split and the minimum OS with reasons.
- Section 11 (verification): name the `xcodebuild` test command and what is checked manually in the running app.
- Section 12 (risks): include the platform probes above that apply; roadmap increments 1–3 usually come from them.
