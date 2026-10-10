# Danny Sung's Agent Skills

[![skills.sh](https://skills.sh/b/dannys42/agent-skills)](https://skills.sh/dannys42/agent-skills)

Portable agent skills for Swift and Apple-platform development, agent-skill
engineering, storytelling, and writing.

## Plugins

| Plugin | Skills | Description |
|---|---|---|
| `swift-craft` | `naming-swift-tests`, `choosing-swift-design-patterns`, `organizing-swift-files` | Personal Swift conventions: explicit test naming, Swift-native design-pattern selection, and focused file organization |
| `agent-engineering` | `optimizing-skill-development`, `audit-token-efficiency` | Risk-proportional skill validation with reproducible evidence, and post-task token-efficiency retrospectives |
| `task-workflow` | `decision-driven-design`, `tasklist`, `tasklist-run` | Resolve consequential design decisions before implementation, then plan and execute the resulting tasks |
| `project-planning` | `system-design`, `risk-first-roadmap` | Shape a high-level design for a large, vague project (tuned for Apple-platform apps), then plan it as risk-ordered, end-to-end increments |
| `storytelling` | `crafting-compelling-stories` | Audience-aware storytelling and narrative copy grounded in an attributed Joanna Wiebe framework |

## Skills

### `organizing-swift-files`

Organizes Swift source so every struct, class, and actor has a focused file,
related files live in feature or domain directories, and structural refactors
remain reviewable separately from behavioral changes.

### `decision-driven-design`

Inspects an existing system, interviews for high-leverage product and engineering decisions, reconciles revisions, and produces dependency-ordered implementation tasks without speculative abstractions.

### `system-design`

Drafts a high-level system design for a large or ambiguous project with
flagged assumptions, asks only the few questions that change the design, and
iterates to agreement. Produces `<DocDir>/Design-<Topic>.md` with scope,
requirements, entities, architecture, technology direction, and a ranked risk
register. Tuned for Apple-platform apps.

### `risk-first-roadmap`

Turns the design into a roadmap of end-to-end increments, each answering the
riskiest unknown reachable from where the project is. Writes
`<DocDir>/Roadmap-<Topic>.md`, details only the next few rungs, and re-plans
after each one.

### `tasklist`

Writes and maintains a `TODO.md` checklist with document-wide unique phase,
group, and task IDs, dependencies, minimum-model tiers, and standard markers
for done, obsolete, invalid, superseded, deferred, and blocked work.

### `tasklist-run`

Runs the open tasks in a `TODO.md` serially: each batch is implemented by a
subagent on the right model, verified by a reviewer subagent, corrected if
needed, and committed on its own before the next batch. Scope, commit
behavior, and parallel worktrees can be overridden per invocation.

### `optimizing-skill-development`

Chooses the smallest validation profile that covers the actual risk of a new
or changed agent skill. It separates packaging, content, behavioral, importer,
and release risk; runs only configured bounded checks; freezes behavioral
artifacts; and keeps rubric-scored evaluation evidence tied to one artifact
hash. It complements `skill-creator` and `writing-skills` and requires only
Python, not a Swift toolchain.

### `audit-token-efficiency`

Reviews the task just completed — its tool calls, searches, and edits — for
token-efficiency opportunities: repeated discovery a script or documented
structure could avoid, hand-run integration work an MCP server could absorb,
and wasted exploration caused by unwritten direction. Records findings in a
`Documentation/` folder as durable direction (`Overview.md`), an
organizational map (`Structure.md`), and an actionable, model-tagged backlog
(`TODO-TokenEfficiency.md`). Manual invocation only, via
`/audit-token-efficiency`.

### `crafting-compelling-stories`

Shapes supplied material into audience-aware stories, marketing and conversion
copy, speeches, talks, scripts, and fiction. It selectively synthesizes an
attributed [Joanna Wiebe presentation](https://www.youtube.com/watch?v=oCnxnaVg0bY)
without fabricating facts, outcomes, quotations, or evidence. The archived
transcript is provenance, not runtime instructions, and not independently
validated science; it remains subject to the third-party redistribution caveat
in [THIRD_PARTY_NOTICES.md](plugins/storytelling/THIRD_PARTY_NOTICES.md).

### `choosing-swift-design-patterns`

Selects among all 22 patterns in the Refactoring.Guru Swift catalog for
greenfield Swift design and existing-code review while preferring no change or
a clearer Swift-native construct. A compact decision index routes the request,
then progressive disclosure loads only the one or two detailed pattern guides
needed for trade-offs and contraindications.
The original guidance is informed by and attributed to the
[Refactoring.Guru Swift design-pattern catalog](https://refactoring.guru/design-patterns/swift)
under its [Content Usage Policy](https://refactoring.guru/content-usage-policy);
source code and illustrations are not redistributed.

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
[plugins/swift-craft/skills/naming-swift-tests](https://github.com/dannys42/agent-skills/tree/main/plugins/swift-craft/skills/naming-swift-tests)

### Claude Code

Install the complete `swift-craft` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install swift-craft@danny-sung-agent-skills
```

### Codex

Install the complete `swift-craft` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add swift-craft@danny-sung-agent-skills
```

### Other agents

Install the individual skill with the open `skills` installer, replacing
`<agent>` with a value from the table:

```bash
npx skills add dannys42/agent-skills \
  --skill naming-swift-tests \
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

## Install `organizing-swift-files`

Canonical source:
[plugins/swift-craft/skills/organizing-swift-files](https://github.com/dannys42/agent-skills/tree/main/plugins/swift-craft/skills/organizing-swift-files)

### Claude Code

Install the complete `swift-craft` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install swift-craft@danny-sung-agent-skills
```

### Codex

Install the complete `swift-craft` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add swift-craft@danny-sung-agent-skills
```

### Other agents

Install the individual skill with the open `skills` installer:

```bash
npx skills add dannys42/agent-skills \
  --skill organizing-swift-files \
  --global \
  --agent <agent>
```

Use the `<agent>` values in the table above. Gemini CLI is supported through
this installer with `gemini-cli`, or by installing or linking
`plugins/swift-craft/` as the local extension root. Use the plugin
directory, not the monorepo repository root, as the Gemini extension root.

## Install `crafting-compelling-stories`

Canonical source:
[plugins/storytelling/skills/crafting-compelling-stories](https://github.com/dannys42/agent-skills/tree/main/plugins/storytelling/skills/crafting-compelling-stories)

### Claude Code

Install the complete `storytelling` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install storytelling@danny-sung-agent-skills
```

### Codex

Install the complete `storytelling` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add storytelling@danny-sung-agent-skills
```

### Other agents

Install the individual skill with the open `skills` installer:

```bash
npx skills add dannys42/agent-skills \
  --skill crafting-compelling-stories \
  --global \
  --agent <agent>
```

Use the `<agent>` values in the table above for Cursor, Gemini CLI, GitHub
Copilot, OpenCode, Roo Code, Zoo Code, ZCode, and Zed.

## Install `choosing-swift-design-patterns`

Canonical source:
[plugins/swift-craft/skills/choosing-swift-design-patterns](https://github.com/dannys42/agent-skills/tree/main/plugins/swift-craft/skills/choosing-swift-design-patterns)

### Claude Code

Install the complete `swift-craft` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install swift-craft@danny-sung-agent-skills
```

### Codex

Install the complete `swift-craft` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add swift-craft@danny-sung-agent-skills
```

### Other agents

Install the individual skill with the open `skills` installer:

```bash
npx skills add dannys42/agent-skills \
  --skill choosing-swift-design-patterns \
  --global \
  --agent <agent>
```

Use the `<agent>` values in the table above for Cursor, Gemini CLI, GitHub
Copilot, OpenCode, Roo Code, Zoo Code, ZCode, and Zed.

## Install `optimizing-skill-development`

Canonical source:
[plugins/agent-engineering/skills/optimizing-skill-development](https://github.com/dannys42/agent-skills/tree/main/plugins/agent-engineering/skills/optimizing-skill-development)

### Claude Code

Install the complete `agent-engineering` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install agent-engineering@danny-sung-agent-skills
```

### Codex

Install the complete `agent-engineering` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add agent-engineering@danny-sung-agent-skills
```

### Other agents

Install the individual skill with the open `skills` installer:

```bash
npx skills add dannys42/agent-skills \
  --skill optimizing-skill-development \
  --global \
  --agent codex
```

Replace `codex` with another supported agent value when needed.

## Install `audit-token-efficiency`

Canonical source:
[plugins/agent-engineering/skills/audit-token-efficiency](https://github.com/dannys42/agent-skills/tree/main/plugins/agent-engineering/skills/audit-token-efficiency)

### Claude Code

Install the complete `agent-engineering` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install agent-engineering@danny-sung-agent-skills
```

### Codex

Install the complete `agent-engineering` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add agent-engineering@danny-sung-agent-skills
```

### Other agents

Install the individual skill with the open `skills` installer:

```bash
npx skills add dannys42/agent-skills \
  --skill audit-token-efficiency \
  --global \
  --agent <agent>
```

Use the `<agent>` values in the table above.

## Install `decision-driven-design`

Canonical source:
[plugins/task-workflow/skills/decision-driven-design](https://github.com/dannys42/agent-skills/tree/main/plugins/task-workflow/skills/decision-driven-design)

### Claude Code

Install the complete `task-workflow` plugin:

```bash
claude plugin marketplace add dannys42/agent-skills
claude plugin install task-workflow@danny-sung-agent-skills
```

### Codex

Install the complete `task-workflow` plugin:

```bash
codex plugin marketplace add dannys42/agent-skills
codex plugin add task-workflow@danny-sung-agent-skills
```

### Other agents

Install the individual skill with the open `skills` installer:

```bash
npx skills add dannys42/agent-skills \
  --skill decision-driven-design \
  --global \
  --agent <agent>
```

To install the task-list skills alone, use `--skill tasklist` or `--skill tasklist-run`.

Use the `<agent>` values in the table above.

## Marketplace adapters and open registries

- Claude marketplace: `.claude-plugin/marketplace.json`
- Codex marketplace: `.agents/plugins/marketplace.json`
- Cursor marketplace: `.cursor-plugin/marketplace.json`
- Gemini extension metadata:
  `plugins/swift-craft/gemini-extension.json`,
  `plugins/agent-engineering/gemini-extension.json`,
  `plugins/task-workflow/gemini-extension.json`, and
  `plugins/storytelling/gemini-extension.json`
- Ready for skills.sh, SkillsMD, and mdskills.ai indexing

Direct installation does not require marketplace submission. These files are
repository distribution metadata and do not imply publication in an external
gallery.

## License

Repository-authored content is licensed under GPL-3.0-or-later. The repository license
does not cover the archival transcript; its redistribution rights are not
established.
