// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "plantools",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "tasklist", targets: ["tasklist"]),
        .executable(name: "roadmap", targets: ["roadmap"]),
        .executable(name: "metrics", targets: ["metrics"]),
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-argument-parser", from: "1.3.0"),
    ],
    targets: [
        .target(name: "PlanKit"),
        .executableTarget(name: "tasklist", dependencies: ["PlanKit", .product(name: "ArgumentParser", package: "swift-argument-parser")]),
        .executableTarget(name: "roadmap", dependencies: ["PlanKit", .product(name: "ArgumentParser", package: "swift-argument-parser")]),
        .executableTarget(name: "metrics", dependencies: ["PlanKit", .product(name: "ArgumentParser", package: "swift-argument-parser")]),
        .testTarget(name: "PlanKitTests", dependencies: ["PlanKit"], exclude: ["Fixtures"]),
    ]
)
