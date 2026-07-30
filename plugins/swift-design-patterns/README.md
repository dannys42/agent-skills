# swift-design-patterns

Portable, original guidance for choosing and reviewing common design patterns
in Swift. The plugin contains one discoverable skill:
`choosing-swift-design-patterns`.

## How the selector works

The selector starts from the design pressure rather than from a pattern name.
For both greenfield work and existing-code review, it recommends keeping a
clear design unchanged or using a simpler Swift-native construct before adding
a GoF pattern. Relevant native options include value types, enums, closures,
generics, protocols, dependency injection, actors, `AsyncSequence`, and
Observation.

When a recurring pressure remains, the skill uses a compact decision index to
identify the strongest candidate, then progressively loads only one or two of
the 22 focused pattern guides. This keeps the always-visible skill instructions
small while making detailed trade-offs, contraindications, and original Swift
examples available when needed. In code review, the same native-first rule
applies: the recommendation may be no change or a simpler Swift-native design.

## Install

### Claude Code

Install the complete plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install swift-design-patterns@danny-sung-agent-skills
```

### Codex

Install the complete plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add swift-design-patterns@danny-sung-agent-skills
```

### Cursor, Gemini CLI, and other agents

Install the individual skill with the open `skills` installer. Replace
`<agent>` with a value from the table:

```bash
npx skills add dannys42/agent-skills \
  --skill choosing-swift-design-patterns \
  --global \
  --agent <agent>
```

| Tool | `<agent>` value |
|---|---|
| Cursor | `cursor` |
| Gemini CLI | `gemini-cli` |
| GitHub Copilot | `github-copilot` |
| OpenCode | `opencode` |
| Roo Code | `roo` |
| Zoo Code | `roo` |
| ZCode | `zcode` |
| Zed | `zed` |

Zoo Code uses `roo` because it supports Roo-compatible skill directories. In
ZCode, open **Settings → Skills** after installation to refresh and enable the
skill.

Repository metadata also includes a Cursor marketplace adapter and Gemini CLI
extension metadata. These adapters do not imply publication in an external
gallery.

## Research import

The pattern guides are bundled with the plugin and require no runtime network
access. The standard-library
[`import_refactoring_guru.py`](skills/choosing-swift-design-patterns/scripts/import_refactoring_guru.py)
script is retained only so maintainers can reproduce the one-time research
import. It downloads into the ignored `.research/` directory, is resumable, and
waits at least five seconds between web requests. Downloaded pages are research
inputs, not distributed skill content.

## Attribution

This plugin contains original Swift guidance informed by the
[Refactoring.Guru Swift design-pattern catalog](https://refactoring.guru/design-patterns/swift)
and used in accordance with its
[Content Usage Policy](https://refactoring.guru/content-usage-policy).
The plugin does not redistribute Refactoring.Guru source code or illustrations.
Each pattern reference links to its specific source page.
