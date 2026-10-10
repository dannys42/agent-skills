# Apple-platform rung patterns

Use these to turn typical Apple-platform unknowns into rungs. They are starting points; keep only those that match the design's risk register, and verify version-specific API claims against current documentation.

## Rung 1 is almost always the skeleton

Build and run the most basic app of the final shape (document-based, menu bar, multiplatform, ...) from the command line (`xcodebuild`) and in Xcode, on the real target (My Mac, Simulator, or a device). Choosing the final shape now is deliberate: converting a single-window app to a document-based one later is a rewrite of the app's spine.

Put the testable logic in a separate target or Swift package at this point, even when empty, so later logic rungs run with no UI.

## Checks that make a rung verifiable by an agent

- Build: `xcodebuild -scheme <Scheme> -destination '<destination>' build`
- Tests: `xcodebuild ... test`, or `swift test` for a package.
- Visible result: a screenshot of the running app, a snapshot test, or an exported PDF or file that can be opened and inspected.
- Manual checks (printing, VoiceOver, drag and drop) go in "Done when" as an explicit action the user performs, so they are not forgotten.

## Typical probes, in usual order

| Unknown | Rung that answers it |
| --- | --- |
| Can the app build, launch, and be the right shape? | Skeleton (above) |
| Can the UI layer draw the core visual element? | Draw the basic repeated element at fixed size |
| Is text legible at screen and print scale? | Real content at target sizes; export a PDF |
| Does the core logic work and perform? | Logic in the package with tests and a timing check, no UI |
| Can the logic's output be seen? | Bind the output to the drawing |
| Does the document save, open, and version correctly? | Round-trip, then open an older file after a format change |
| Does the entitlement or capability work (sandbox, iCloud, camera)? | Smallest feature that needs it, in a signed build |
| Does distribution work (signing, notarization, review)? | A signed, notarized or TestFlight build of the current rung |
| Does it work on a second platform? | Same rung run on the second target, before building more UI on the first |

## Placement guidance

- Distribution and entitlements are late-looking but can be fatal. If the design says distribution is unproven or the app needs a sandbox entitlement, schedule a signed build early and repeat it, instead of finding out at the end.
- Drawing and text rungs come early when the product's value is how it looks or prints, and late when the visuals are standard controls.
- Pull a logic rung ahead of UI rungs when the logic is the frightening part, and it can be proven by tests alone.
- A second platform is its own risk. Do not add it until the first platform's ladder has reached the first end-to-end result.
