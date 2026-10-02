---
name: naming-swift-tests
description: Use when generating, editing, or reviewing names in Swift unit tests using Swift Testing or XCTest, including test files, suites, functions, variables, fixtures, helpers, and parameterized arguments.
license: GPL-3.0-or-later
---

# Naming Swift Tests

## Conventions

- Apply these conventions strictly to generated code. In existing code, preserve a coherent local alternative when renaming would create inconsistency or unrelated churn.
- Name files and suites `<Subject>Tests`; a free function is its own subject. Use `<Subject><Platform>Tests` for platform variants and platform directories for extensive divergence. Split large subjects by facet, such as `ImageLoaderCacheTests` and `ImageLoaderNetworkTests`.
- Name Swift Testing functions `<scenario>[_With<condition>...]_Will<ObservableContract>` and XCTest functions `testThat_<Scenario>[_With<Condition>...]_Will<ObservableContract>`.
- Express the domain scenario and exact observable contract, not fixture literals: `percentageDiscount_WillReducePrice`, not `twentyPercentDiscount_WithPrice100_WillReturn80`.
- Keep sibling vocabulary symmetric. When the error type is known, name it in `WillThrow`, for example `testThat_DeleteDocument_WithUnauthorizedUser_WillThrowAuthorizationError`. Never claim state is unchanged unless the test observes that.
- Add a Swift Testing display name only when it improves clarity. Preserve a clear existing display name that agrees with the function.
- Before the action, generated tests declare the primary stimulus and concrete expectation as `inputValue`/`inputValues` and `expectedValue`; capture the result as `observedValue`. Input may enter by argument, property, or dependency. Use labeled `inputValues` for related stimuli; keep one collection or multi-field value singular. With multiple result roles, qualify names symmetrically (`expectedOutputValue`/`observedOutputValue`) while preserving cardinality (`expectedEventValue`/`observedEventValues`).
- Allow direct self-explanatory predicates such as `#expect(items.isEmpty)`. Keep obvious setup inline; otherwise use contextual names such as `existingUser`, `expirationDate`, or `initialItems`.
- Keep concrete expected values visible. Do not hide events or values behind a computed Boolean solely for aggregate equality.
- A test-only `Equatable` `OutputValues` is appropriate only when more than three related properties recur across many tests and share equality semantics; use it for one expected/observed equality. Never aggregate values with different matching semantics.
- Keep multiple expectations together when one action jointly produces them; otherwise split tests.
- Name doubles `<Role>Mock`, `<Role>Stub`, or `<Role>Spy`, and variables by domain role. Never use `sut` or a generic subject name; add a subject-under-test comment only when extensive setup obscures it.
- Use `create<Type>()` for one object. For reusable multi-object setup, use `TestEnvironment` and `let env = createTestEnvironment()`; use contextual environment types when multiple shapes exist.
- Parameterize simple cases with a direct collection. Otherwise use singular `TestArgument`, or contextual `<Scenario>TestArgument`, with `testArgument`. Use Cartesian products only for a shared invariant, an explicit argument type for correlated input and expectation, and `zip` only when trivial.

```swift
struct TestArgument {
    let inputValue: UserDraft
    let expectedOutputValue: [User]
    let expectedEventValue: UserEvent
}

@Test(arguments: [
    TestArgument(
        inputValue: UserDraft(name: "Ana"),
        expectedOutputValue: [User(name: "Ana")],
        expectedEventValue: .registered(name: "Ana")
    )
])
func registerUser_WillSaveUserAndEmitEvent(testArgument: TestArgument) {
    let env = createTestEnvironment()
    let inputValue = testArgument.inputValue
    let expectedOutputValue = testArgument.expectedOutputValue
    let expectedEventValue = testArgument.expectedEventValue

    env.userService.register(inputValue)

    let observedOutputValue = env.savedUsers
    let observedEventValues = env.eventSpy.recordedEvents
    #expect(observedOutputValue == expectedOutputValue)
    #expect(observedEventValues.contains(expectedEventValue))
}
```
