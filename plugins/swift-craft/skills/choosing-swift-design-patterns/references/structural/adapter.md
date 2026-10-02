# Adapter

## Intent

Translate an existing interface or representation into the one a client expects. Adapter preserves the useful behavior of a type that cannot—or should not—be changed while containing the mismatch at a narrow boundary.

## Prefer Swift-native alternatives when

Add a protocol conformance in an extension when you own the type and the mapping is honest for every instance. Use a conversion initializer, computed property, or small free function when only data representation differs. These choices avoid a forwarding object and make the conversion visible. Reach for a separate adapter when the source is legacy or external, its semantics need interpretation, or one source needs multiple client-facing views.

## Choose this pattern when

Choose Adapter when valuable code has an incompatible API, clients should depend on a stable local vocabulary, and changing either side would spread vendor or legacy concepts through the application. It is particularly useful at SDK, persistence, and hardware boundaries. The adapter should make semantic differences explicit—for example, units, failure behavior, or optionality—not merely rename every member.

## Avoid it when

Avoid Adapter when a direct call is already clear, when you control both APIs and can align them, or when the wrapper only duplicates names. Do not silently discard precision, errors, or lifecycle requirements. If the real need is to simplify several subsystem operations, use a Facade. If two independently varying abstractions must evolve separately, consider Bridge.

## Design pressures

Look for repeated conversion arithmetic, legacy names leaking into domain code, mocks that must imitate a third-party API, or several call sites making slightly different assumptions about the same source. A strong boundary has one interpretation and tests around edge cases. A growing collection of one-to-one forwarding methods usually indicates that the local interface is too broad.

## Swift implementation

Define the interface from the consuming feature’s needs. A small struct adapter can hold the legacy reference, convert its output, and expose no mutation that the client does not require. Use an extension instead if the adaptee can safely conform without additional stored state. Keep conversions named with units and document rounding or invalid ranges. Generic adapters are useful only when many sources share the same mismatch; do not erase concrete types automatically.

## Concurrency and ownership

An adapter does not change the thread-safety of what it wraps. A value adapter around a mutable class still shares that class. Preserve actor annotations and asynchronous operations rather than presenting a falsely synchronous interface. If the underlying object is confined to an actor, isolate the adapter to the same actor or make every crossing explicit.

## Compare

Adapter changes the interface through which an existing object is used. Facade offers a simpler entry point to a broader subsystem and may coordinate several objects. Bridge is designed up front to separate two dimensions that vary. Decorator keeps the same interface while adding behavior. A conversion function is the better Swift-native choice when no enduring object boundary is needed.

## Example

```swift
final class LegacyTemperatureSensor {
    private let fahrenheitValue: Double

    init(fahrenheitValue: Double) {
        self.fahrenheitValue = fahrenheitValue
    }

    func readDegreesF() -> Double {
        fahrenheitValue
    }
}

protocol TemperatureReading {
    var degreesCelsius: Double { get }
}

struct LegacySensorAdapter: TemperatureReading {
    private let sensor: LegacyTemperatureSensor

    init(sensor: LegacyTemperatureSensor) {
        self.sensor = sensor
    }

    var degreesCelsius: Double {
        (sensor.readDegreesF() - 32) * 5 / 9
    }
}

func frostWarning(for reading: any TemperatureReading) -> String {
    reading.degreesCelsius <= 0 ? "Frost risk" : "Above freezing"
}

let oldSensor = LegacyTemperatureSensor(fahrenheitValue: 23)
let reading = LegacySensorAdapter(sensor: oldSensor)
print(frostWarning(for: reading))
```

The client speaks only in Celsius and has no knowledge of the legacy method or unit. If the sensor type were under local control, a direct conformance or `degreesCelsius` extension could be shorter.

## Review checklist

- Is there a genuine interface or semantic mismatch?
- Would an extension or conversion function be clearer?
- Does the adapter expose only what its clients require?
- Are units, errors, optionality, and precision translated explicitly?
- Is third-party or legacy vocabulary contained at the boundary?
- Does the wrapper preserve the adaptee’s ownership and isolation rules?
- Is this translation rather than subsystem coordination or independent variation?

## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Adapter in Swift](https://refactoring.guru/design-patterns/adapter/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
