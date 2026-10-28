import Foundation

/// Shared plumbing for the executables: plain text out, exit codes 0 ok, 1 problem found, 2 usage or I/O.
public let planToolsVersion = "0.5.2"

public enum CLI {
    public static func fail(_ message: String, code: Int32 = 2) -> Never {
        FileHandle.standardError.write(Data((message + "\n").utf8))
        exit(code)
    }

    public static func read(_ path: String) -> String {
        guard let text = try? String(contentsOfFile: path, encoding: .utf8) else { fail("cannot read \(path)") }
        return text
    }

    public static func print(_ text: String) {
        FileHandle.standardOutput.write(Data((text.hasSuffix("\n") ? text : text + "\n").utf8))
    }

    public static func report(_ findings: [Finding]) -> Int32 {
        findings.forEach { print($0.rendered) }
        let errors = findings.filter { $0.severity == .error }.count
        print(findings.isEmpty ? "ok" : "\(errors) error(s), \(findings.count - errors) warning(s)")
        return errors == 0 ? 0 : 1
    }
}
