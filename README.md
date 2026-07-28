# Danny Sung's Agent Skills

Portable agent skills for Swift and Apple-platform development.

## Plugins

| Plugin | Skills | Description |
|---|---|---|
| `swift-testing` | `naming-swift-tests` | Explicit contract naming for Swift Testing and XCTest |

## Skills

### `naming-swift-tests`

Names Swift Testing and XCTest files, suites, functions, values, fixtures,
test environments, and parameterized arguments so each test's inputs, expected
and observed values, and successful or failing outcome are immediately clear.

#### Intent

Tests are executable documentation. Their names should state the domain
scenario, relevant conditions, and observable contract without requiring the
reader to inspect the implementation. The same principle applies inside the
test: names should distinguish inputs, expectations, and observations so its
arrange-act-assert flow is visible at a glance.

#### Before and after

A conventional test often uses broad function and value names:

```swift
@Test
func discount() throws {
    let price = 100
    let discount = 20
    let expected = 80

    let result = try PriceCalculator()
        .applying(percentage: discount, to: price)

    #expect(result == expected)
}

@Test
func invalidDiscount() {
    let discount = -1

    #expect(throws: InvalidDiscountError.self) {
        try PriceCalculator().applying(percentage: discount, to: 100)
    }
}
```

With explicit contract naming, sibling tests describe both the scenario and
whether the observable outcome is a returned value or an error:

```swift
@Test
func percentageDiscount_WillReturnDiscountedPrice() throws {
    let inputValues = (price: 100, discountPercentage: 20)
    let expectedValue = 80
    let priceCalculator = PriceCalculator()

    let observedValue = try priceCalculator.applying(
        percentage: inputValues.discountPercentage,
        to: inputValues.price
    )

    #expect(observedValue == expectedValue)
}

@Test
func percentageDiscount_WithNegativePercentage_WillThrowInvalidDiscountError() {
    let inputValues = (price: 100, discountPercentage: -1)
    let priceCalculator = PriceCalculator()

    #expect(throws: InvalidDiscountError.self) {
        try priceCalculator.applying(
            percentage: inputValues.discountPercentage,
            to: inputValues.price
        )
    }
}
```

XCTest uses the same contract with a `testThat_` prefix.

#### Why use explicit contract naming?

Names such as `discount`, `invalidDiscount`, `expected`, and `result` are
familiar, but they leave important questions unanswered. A reader must inspect
the test body to learn what behavior is exercised, what success means, whether
a negative case returns a value or throws, and which values are stimuli versus
expected or observed outputs. These ambiguities become more costly as setup and
the number of sibling tests grow.

Explicit contract naming makes those roles visible:

- `<scenario>[_With<condition>...]_Will<ObservableContract>` makes positive and
  negative paths easy to distinguish, scan, and search.
- `inputValue` or labeled `inputValues` identifies the stimulus.
- `expectedValue` states the contract before the action occurs.
- `observedValue` identifies what the test actually captured.
- Symmetric vocabulary makes related tests easier to compare and keeps names
  honest about only the behavior each test observes.

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
