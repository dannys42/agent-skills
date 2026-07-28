# Danny Sung's Agent Skills

Portable agent skills for Swift and Apple-platform development.

## Plugins

| Plugin | Skills | Description |
|---|---|---|
| `swift-testing` | `naming-swift-tests` | Precise naming conventions for Swift Testing and XCTest |

## Skills

### `naming-swift-tests`

Names Swift Testing and XCTest files, suites, functions, values, fixtures,
test environments, and parameterized arguments so tests state exact observable
contracts.

## Install `naming-swift-tests`

Canonical source:
[plugins/swift-testing/skills/naming-swift-tests](https://github.com/dannys42/agent-skills/tree/main/plugins/swift-testing/skills/naming-swift-tests)

### Claude Code

Install the complete `swift-testing` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install swift-testing@danny-sung-agent-skills
```

### Codex

Install the complete `swift-testing` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add swift-testing@danny-sung-agent-skills
```

### Cursor

```bash
gh skill install dannys42/agent-skills naming-swift-tests --scope user --agent cursor
```

### Gemini CLI

```bash
gh skill install dannys42/agent-skills naming-swift-tests --scope user --agent gemini-cli
```

### GitHub Copilot

```bash
gh skill install dannys42/agent-skills naming-swift-tests --scope user --agent github-copilot
```

### OpenCode

```bash
gh skill install dannys42/agent-skills naming-swift-tests --scope user --agent opencode
```

### Roo Code

```bash
gh skill install dannys42/agent-skills naming-swift-tests --scope user --agent roo
```

The open `skills` installer provides an equivalent path. For example:

```bash
npx skills add dannys42/agent-skills --skill naming-swift-tests --global --agent cursor
```

### Zoo Code

Zoo Code supports Roo-compatible skill directories:

```bash
npx skills add dannys42/agent-skills --skill naming-swift-tests --global --agent roo
```

This installs to `~/.roo/skills`, which Zoo Code scans along with `.agents`
skill locations.

### ZCode

```bash
npx skills add dannys42/agent-skills --skill naming-swift-tests --global --agent zcode
```

This installs to `~/.zcode/skills`. In ZCode, open **Settings → Skills** to
refresh and enable the skill or import it from an external skills directory.

### Zed

```bash
npx skills add dannys42/agent-skills --skill naming-swift-tests --global --agent zed
```

This installs to `~/.agents/skills`, where Zed discovers global Agent Skills.

## Marketplace adapters and open registries

- Claude marketplace: `.claude-plugin/marketplace.json`
- Codex marketplace: `.agents/plugins/marketplace.json`
- Cursor marketplace: `.cursor-plugin/marketplace.json`
- Gemini extension metadata: `plugins/swift-testing/gemini-extension.json`
- Ready for skills.sh, SkillsMD, and mdskills.ai indexing

Direct installation does not require marketplace submission. These files are
repository distribution metadata and do not imply publication in an external
gallery.

## License

MIT
