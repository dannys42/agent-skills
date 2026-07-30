# Visitor

## Intent

Add operations across a stable family of element types without placing every operation inside those types. Visitor favors adding operations over adding element cases and encodes double dispatch when the operation depends on a concrete element type.

## Prefer Swift-native alternatives when

For a closed enum, start with an exhaustive switch in each operation. The compiler then identifies every operation that needs updating when a case is added. Put behavior in an enum extension when it naturally belongs to the domain. Protocol extensions work well when one operation applies uniformly through protocol requirements.

## Choose this pattern when

Choose Visitor when the element hierarchy is genuinely stable, new cross-cutting operations arrive frequently, and those operations need type-specific behavior. An expression library exposed to tooling might keep node types fixed while formatters, evaluators, dependency collectors, and optimizers evolve independently. Visitor can group each operation and keep node definitions from accumulating unrelated tooling concerns.

## Avoid it when

Avoid Visitor for a five-case enum and two operations; exhaustive switches are more transparent. Adding a new element type requires changing every visitor, so the pattern is costly when the hierarchy evolves. Associated return types, throwing behavior, and mutable context can make a visitor interface cumbersome. Do not simulate double dispatch if one enum switch already provides exact case information.

## Design pressures

Count both axes of change: element variants and operations. Visitor is attractive only when operations grow substantially faster than a stable element set. Determine whether operations return one shared type and whether traversal belongs to the visitor, the elements, or a separate sequence. Keep side effects visible; a visitor named “analyzer” should not silently rewrite nodes.

## Swift implementation

For a closed expression tree, use an `indirect enum` and free functions or extensions first. If Visitor becomes justified, a protocol for each node plus a visitor protocol can provide double dispatch, but generic return types often require additional design. An enum-based operation object can offer grouping without recreating the full classic structure.

## Concurrency and ownership

Pure operations over immutable value trees are naturally easier to use concurrently. Visitors that accumulate mutable results should be created per traversal or isolated to one owner. Do not share a stateful visitor across tasks without synchronization. If trees or results cross actor boundaries, assess `Sendable` from their stored values and module settings rather than applying unchecked conformance.

## Compare

An exhaustive enum switch optimizes for a closed variant set and makes new-case fallout explicit. Visitor optimizes for a stable element hierarchy with many independently added operations. Strategy selects one algorithm behind a uniform input contract; Visitor dispatches behavior based on multiple concrete element kinds. Iterator controls traversal order, while Visitor defines work performed at elements.

## Example

```swift
indirect enum Expression {
    case number(Double)
    case variable(String)
    case add(Expression, Expression)
    case multiply(Expression, Expression)
}

enum EvaluationError: Error {
    case unknownVariable(String)
}

func evaluate(
    _ expression: Expression,
    variables: [String: Double]
) throws -> Double {
    switch expression {
    case .number(let value):
        return value
    case .variable(let name):
        guard let value = variables[name] else {
            throw EvaluationError.unknownVariable(name)
        }
        return value
    case .add(let left, let right):
        return try evaluate(left, variables: variables)
            + evaluate(right, variables: variables)
    case .multiply(let left, let right):
        return try evaluate(left, variables: variables)
            * evaluate(right, variables: variables)
    }
}

func variables(in expression: Expression) -> Set<String> {
    switch expression {
    case .number:
        return []
    case .variable(let name):
        return [name]
    case .add(let left, let right),
         .multiply(let left, let right):
        return variables(in: left).union(variables(in: right))
    }
}

let expression = Expression.multiply(
    .add(.variable("x"), .number(2)),
    .variable("y")
)
let value = try evaluate(expression, variables: ["x": 3, "y": 4])
print(value, variables(in: expression))
```

Two operations over four closed cases remain clearer as exhaustive switches. If dozens of tooling operations appeared while cases stayed fixed, Visitor could group each operation and keep tool-specific dependencies outside the expression definition.

## Review checklist

- Is the element set more stable than the operation set?
- Would exhaustive enum switches be clearer and safer?
- Do operations need concrete element-specific behavior?
- How costly is adding a new element to every visitor?
- Is traversal separate from the operation?
- Are stateful visitors confined to one traversal or owner?
- Does the pattern reduce coupling enough to justify double dispatch?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Visitor in Swift](https://refactoring.guru/design-patterns/visitor/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
