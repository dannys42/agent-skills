# Abstract Factory

## Intent

Create related values from one implementation family without making the caller select each concrete type independently. In Swift, an existential factory such as the one below centralizes that choice by convention; use associated types and a generic client when family compatibility must be enforced by the type system.

## Prefer Swift-native alternatives when

Use a generic configuration when the family can be selected once at composition time and concrete types need not vary at runtime. Inject a few creation closures when products are independent or tests only need lightweight substitutions. A value containing styles and callbacks is often clearer than three protocols plus a factory.

## Choose this pattern when

Choose Abstract Factory when a client creates several related products, the whole family changes together, and independently selecting products would be invalid or misleading. It is especially useful at a platform or rendering boundary where the application must switch complete backends at runtime while keeping the client ignorant of their concrete representations.

## Avoid it when

Avoid it for one product, for products that vary independently, or when an enum switch at the composition root is already exhaustive and small. Do not introduce a protocol for every value merely to make the diagram resemble the pattern. Adding a new product kind touches every factory, so a frequently growing product axis is a warning sign.

## Design pressures

Look for repeated switches that choose an axis, legend, and renderer from the same backend; call sites that independently assemble inconsistent combinations; or tests that cannot substitute a complete product family. The pressure is stronger when new families are expected and product roles are relatively stable.

## Swift implementation

Define protocols only for roles that clients genuinely substitute. A factory protocol exposes creation operations for the related products, while each concrete factory owns family-specific construction. Prefer methods returning opaque or existential values only where that boundary is necessary. Keep family selection at a composition root and pass the selected factory inward. This prevents ordinary clients from making each choice, but it does not make concrete product initializers mutually exclusive. If compile-time compatibility matters and selection is static, give the factory associated product types and make the client generic over the family instead of erasing those relationships.

## Concurrency and ownership

Factories are easiest to share when they are immutable and `Sendable`. Return value-semantic configuration where possible. If a product owns GPU or other thread-confined resources, isolate that product rather than assuming the factory makes it safe. A `@MainActor` or custom-actor boundary should reflect the resource contract and be visible to callers.

## Compare

Factory Method varies construction of one product through a creator seam; Abstract Factory supplies a coordinated family. Builder assembles one complicated result over several steps. Strategy changes an operation, not a set of constructed collaborators. A generic configuration is preferable when compatibility can be enforced statically with fewer abstractions.

## Example

```swift
protocol ChartFamily {
    func makeAxis() -> AxisStyle
    func makeLegend() -> LegendStyle
    func makeRenderer() -> any ChartRenderer
}

struct AxisStyle { let labelColor: String }
struct LegendStyle { let placement: String }

protocol ChartRenderer {
    func draw(values: [Double]) -> String
}

struct SVGRenderer: ChartRenderer {
    func draw(values: [Double]) -> String {
        "<svg data-count=\"\(values.count)\"></svg>"
    }
}

struct MetalRenderer: ChartRenderer {
    func draw(values: [Double]) -> String {
        "Metal commands for \(values.count) values"
    }
}

struct SVGChartFamily: ChartFamily {
    func makeAxis() -> AxisStyle { AxisStyle(labelColor: "currentColor") }
    func makeLegend() -> LegendStyle { LegendStyle(placement: "inline") }
    func makeRenderer() -> any ChartRenderer { SVGRenderer() }
}

struct MetalChartFamily: ChartFamily {
    func makeAxis() -> AxisStyle { AxisStyle(labelColor: "displayP3White") }
    func makeLegend() -> LegendStyle { LegendStyle(placement: "overlay") }
    func makeRenderer() -> any ChartRenderer { MetalRenderer() }
}

struct Chart {
    private let axis: AxisStyle
    private let legend: LegendStyle
    private let renderer: any ChartRenderer

    init(family: any ChartFamily) {
        axis = family.makeAxis()
        legend = family.makeLegend()
        renderer = family.makeRenderer()
    }

    func render(_ values: [Double]) -> String {
        "\(axis.labelColor), \(legend.placement): \(renderer.draw(values: values))"
    }
}

let chart = Chart(family: SVGChartFamily())
print(chart.render([3, 5, 8]))
```

The factory gives `Chart` one coherent backend choice and removes independent product selection from that client. Other code can still construct concrete values directly; this existential version centralizes the convention rather than proving compatibility at compile time.

## Review checklist

- Are at least two products required to change as one family?
- Is independently selecting inconsistent products a real defect?
- Would a generic configuration or injected closures be shorter and clearer?
- Are protocols placed at actual substitution boundaries?
- Does family selection occur in one obvious composition root?
- If compatibility must be type-enforced, should associated product types replace existential erasure?
- Is isolation of resource-owning products explicit?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Abstract Factory in Swift](https://refactoring.guru/design-patterns/abstract-factory/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
