# Standalone Agent Skills Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved `naming-swift-tests` skill and its cross-agent distribution package in the intended standalone repository, then restore the reference repository to its untouched state.

**Architecture:** Use a plugin catalog with `plugins/swift-testing` as the first focused bundle. Keep the canonical Agent Skills artifact portable, then layer Claude, Codex, Cursor, and Gemini manifests around the shared `skills/` directory. Treat recovery of the mistakenly modified reference repository as a guarded final operation that runs only after the standalone repository passes validation.

**Tech Stack:** Markdown Agent Skills, JSON marketplace manifests, YAML skill interface metadata, Git, Claude/Codex plugin validators, Vercel `skills` discovery CLI

---

## File Map

| Path | Responsibility |
|---|---|
| `plugins/swift-testing/skills/naming-swift-tests/SKILL.md` | Canonical portable naming rules |
| `plugins/swift-testing/skills/naming-swift-tests/agents/openai.yaml` | OpenAI/Codex skill-picker metadata |
| `.claude-plugin/marketplace.json` | Claude repository marketplace |
| `.agents/plugins/marketplace.json` | Codex repository marketplace |
| `.cursor-plugin/marketplace.json` | Cursor repository marketplace |
| `plugins/swift-testing/.claude-plugin/plugin.json` | Claude plugin manifest |
| `plugins/swift-testing/.codex-plugin/plugin.json` | Codex plugin manifest |
| `plugins/swift-testing/.cursor-plugin/plugin.json` | Cursor plugin manifest |
| `plugins/swift-testing/gemini-extension.json` | Gemini extension metadata for the plugin archive |
| `README.md` | Repository description and complete installation matrix |
| `plugins/swift-testing/README.md` | Focused plugin/skill description |
| `plugins/swift-testing/CHANGELOG.md` | Plugin release history |
| `LICENSE` | MIT license |

The custom `registry.json` from the reference marketplace is intentionally not
part of this repository.

### Task 1: RED/GREEN — create and behavior-test `naming-swift-tests`

**Files:**
- Create: `plugins/swift-testing/skills/naming-swift-tests/SKILL.md`
- Create: `plugins/swift-testing/skills/naming-swift-tests/agents/openai.yaml`

- [ ] **Step 1: Run isolated baseline scenarios**

Use two fresh agents without the new skill. Do not let them read the design,
plan, interview, or reference repository.

Prompt A:

```text
Write one concise Swift Testing unit test for
PriceCalculator.price(afterApplying:to:). Given a 20% discount and price 100,
the result must be 80. Return code only.
```

Prompt B:

```text
Write one concise XCTest unit test proving
DocumentService.deleteDocument(id:user:) throws the exact known
AuthorizationError.unauthorized for an unauthorized user. Return code only.
```

Keep raw results outside the repository. Record whether the agents independently
produce these required names and roles:

```text
percentageDiscount_WillReducePrice
testThat_DeleteDocument_WithUnauthorizedUser_WillThrowAuthorizationError
inputValue/inputValues
expectedValue
observedValue
```

- [ ] **Step 2: Initialize the skill**

Run:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  naming-swift-tests \
  --path plugins/swift-testing/skills \
  --interface display_name="Naming Swift Tests" \
  --interface short_description="Name Swift unit tests consistently" \
  --interface default_prompt="Use \$naming-swift-tests to name or review Swift unit tests."
```

Expected: the skill directory contains `SKILL.md` and `agents/openai.yaml`,
with no optional resource directories.

- [ ] **Step 3: Replace `SKILL.md` with the approved portable artifact**

```markdown
---
name: naming-swift-tests
description: Use when generating, editing, or reviewing names in Swift unit tests using Swift Testing or XCTest, including test files, suites, functions, variables, fixtures, helpers, and parameterized arguments.
---

# Naming Swift Tests

## Apply consistently

Follow these conventions strictly in generated code. In existing code, preserve a coherent local alternative when renaming would create inconsistency or unrelated churn.

## Files and contracts

- Name files/suites `<Subject>Tests`; for free functions, use the function name as the subject. Use `<Subject><Platform>Tests` for platform variants and platform directories when divergence is extensive. Split large subjects by domain facet, such as `ImageLoaderCacheTests` and `ImageLoaderNetworkTests`.
- Swift Testing: `<scenario>[_With<condition>...]_Will<ObservableContract>`.
- XCTest: `testThat_<Scenario>[_With<Condition>...]_Will<ObservableContract>`.
- Function names describe domain scenarios and exact observable contracts, not fixture values: `percentageDiscount_WillReducePrice`, not `twentyPercentDiscount_WithPrice100_WillReturn80`. Keep sibling vocabulary symmetric: `cacheMiss_WithOnlineConnection_WillFetchFromNetwork` / `cacheMiss_WithOfflineConnection_WillThrowOfflineError`. Use known error types in `WillThrow<ErrorType>`. Say `testThat_DeleteDocument_WithUnauthorizedUser_WillThrowAuthorizationError`, not that state remains unchanged unless verified.
- Add a Swift Testing display name only when it improves clarity. Preserve a clear existing display name that agrees with the function.

## Values and setup

- Before the action, generated tests declare the primary stimulus and concrete expectation as `inputValue`/`inputValues` and `expectedValue`; capture the result as `observedValue`. Input may enter by argument, property, or dependency. Use labeled `inputValues` for related stimuli; keep one collection or multi-field value singular. With multiple result roles, qualify names symmetrically (`expectedOutputValue`/`observedOutputValue`) while preserving cardinality (`expectedEventValue`/`observedEventValues`).
- Allow direct self-explanatory checks such as `#expect(items.isEmpty)`.
- Inline obvious setup; otherwise use contextual names such as `existingUser`, `expirationDate`, or `initialItems`.
- Keep concrete expected values visible. Never hide a desired event/value behind a computed Boolean solely to aggregate equality.
- A test-only `Equatable` `OutputValues` aggregate may enable one expected/observed equality when more than three related properties recur across many tests and share comparison semantics. Do not aggregate different matching semantics.
- Keep multiple expectations together when one action must jointly produce them; otherwise split tests.

## Doubles, helpers, and arguments

- Name double types with `Mock`, `Stub`, or `Spy`; name variables by domain role/behavior. Never use `sut` or generic `subject`. If extensive setup obscures the subject, add `// Subject under test`.
- Use `create<Type>()` for one object. Reusable multi-object setup returns `TestEnvironment`: `let env = createTestEnvironment()`. When shapes differ, use contextual types such as `NetworkTestEnvironment` and `OfflineTestEnvironment`.
- A simple parameterized test may use one direct argument collection. Otherwise use singular `TestArgument`, or `<Scenario>TestArgument` for multiple shapes, with variable `testArgument`. Use Cartesian products only when every combination shares one invariant. Use an explicit argument type for correlated inputs and expectations; reserve `zip` for trivial pairs and otherwise avoid it.

```swift
struct TestArgument {
    let inputValue: UserDraft
    let expectedOutputValue: [User]
    let expectedEventValue: UserEvent
}

@Test(arguments: [
    TestArgument(
        inputValue: UserDraft(name: "Ana"),
        expectedOutputValue: [User(id: 42, name: "Ana")],
        expectedEventValue: .userCreated(id: 42)
    )
])
func validRegistration_WillPersistUserAndEmitCreatedEvent(testArgument: TestArgument) throws {
    let env = createTestEnvironment()
    let inputValue = testArgument.inputValue
    let expectedOutputValue = testArgument.expectedOutputValue
    let expectedEventValue = testArgument.expectedEventValue

    try env.registration.register(inputValue)
    let observedOutputValue = env.userRepository.savedUsers
    let observedEventValues = env.eventSpy.events

    #expect(observedOutputValue == expectedOutputValue)
    #expect(observedEventValues.contains(expectedEventValue))
}
```
```

- [ ] **Step 4: Confirm OpenAI skill metadata**

`plugins/swift-testing/skills/naming-swift-tests/agents/openai.yaml` must be:

```yaml
interface:
  display_name: "Naming Swift Tests"
  short_description: "Name Swift unit tests consistently"
  default_prompt: "Use $naming-swift-tests to name or review Swift unit tests."
```

- [ ] **Step 5: Validate syntax and word budget**

Run:

```bash
uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/swift-testing/skills/naming-swift-tests

test "$(wc -w < plugins/swift-testing/skills/naming-swift-tests/SKILL.md)" -le 500
```

Expected:

```text
Skill is valid!
```

The word-budget assertion exits zero.

- [ ] **Step 6: Forward-test with fresh agents**

Give each fresh agent only the new `SKILL.md` and one scenario:

1. Percentage discount: expect
   `percentageDiscount_WillReducePrice` and a labeled `inputValues` tuple.
2. Unauthorized XCTest deletion: expect
   `testThat_DeleteDocument_WithUnauthorizedUser_WillThrowAuthorizationError`.
3. Correlated shipping cases: expect singular `TestArgument`, `testArgument`,
   visible `expectedValue`, and `observedValue`.
4. Existing coherent `NormalizeEmailTests`: preserve clear display names and
   its established `given`/`actual` locals.
5. Cache miss online/offline siblings: expect symmetric
   `cacheMiss_WithOfflineNetwork_WillThrowNetworkError` and
   `cacheMiss_WithOnlineNetwork_WillDownloadImage`; a returned `[Image]`
   collection remains singular `expectedValue`/`observedValue`.
6. One action with persisted output plus an emitted event: expect symmetric
   `expectedOutputValue`/`observedOutputValue`, singular
   `expectedEventValue`, plural `observedEventValues`, and a visible
   `contains` check for the expected event.

If a real failure appears, refine the skill, rerun only the failed scenario and
the validator, and keep the skill at or below 500 words.

- [ ] **Step 7: Review Task 1**

Dispatch an independent specification reviewer, then an independent quality
reviewer. Resolve every Critical or Important finding and rerun affected
forward scenarios.

- [ ] **Step 8: Commit the skill task**

Run:

```bash
git add plugins/swift-testing/skills/naming-swift-tests
git commit -m "skill(swift-testing): add Swift test naming conventions"
```

Expected: the second repository commit contains only the skill artifact and its
OpenAI interface metadata.

### Task 2: Package the `1.0.0` cross-agent distribution

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `.cursor-plugin/marketplace.json`
- Create: `plugins/swift-testing/.claude-plugin/plugin.json`
- Create: `plugins/swift-testing/.codex-plugin/plugin.json`
- Create: `plugins/swift-testing/.cursor-plugin/plugin.json`
- Create: `plugins/swift-testing/gemini-extension.json`
- Create: `plugins/swift-testing/README.md`
- Create: `plugins/swift-testing/CHANGELOG.md`
- Create: `README.md`
- Create: `LICENSE`

- [ ] **Step 1: Create the Claude marketplace**

`.claude-plugin/marketplace.json`:

```json
{
  "name": "danny-sung-agent-skills",
  "owner": {
    "name": "Danny Sung"
  },
  "metadata": {
    "description": "Danny Sung's portable agent skills for Swift and Apple-platform development",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "swift-testing",
      "source": "./plugins/swift-testing",
      "version": "1.0.0",
      "description": "Swift unit-test naming conventions for Swift Testing and XCTest",
      "category": "testing",
      "keywords": ["swift", "ios", "unit-tests", "xctest", "agent-skills"],
      "tags": ["testing", "swift"]
    }
  ]
}
```

- [ ] **Step 2: Create the Claude plugin manifest**

`plugins/swift-testing/.claude-plugin/plugin.json`:

```json
{
  "name": "swift-testing",
  "version": "1.0.0",
  "description": "Swift unit-test naming conventions for Swift Testing and XCTest",
  "author": {
    "name": "Danny Sung"
  },
  "keywords": ["swift", "ios", "unit-tests", "xctest", "agent-skills"]
}
```

- [ ] **Step 3: Create the Codex marketplace**

`.agents/plugins/marketplace.json`:

```json
{
  "name": "danny-sung-agent-skills",
  "interface": {
    "displayName": "Danny Sung's Agent Skills"
  },
  "plugins": [
    {
      "name": "swift-testing",
      "source": {
        "source": "local",
        "path": "./plugins/swift-testing"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

- [ ] **Step 4: Create the current-schema Codex manifest**

`plugins/swift-testing/.codex-plugin/plugin.json`:

```json
{
  "name": "swift-testing",
  "version": "1.0.0",
  "description": "Swift unit-test naming conventions for Swift Testing and XCTest",
  "skills": "./skills/",
  "author": {
    "name": "Danny Sung",
    "url": "https://github.com/dannys42"
  },
  "repository": "https://github.com/dannys42/agent-skills",
  "keywords": ["swift", "ios", "unit-tests", "xctest", "agent-skills"],
  "interface": {
    "displayName": "Swift Testing",
    "shortDescription": "Name Swift unit tests consistently",
    "longDescription": "Name and review Swift Testing and XCTest code using precise observable contracts.",
    "developerName": "Danny Sung",
    "category": "Developer Tools",
    "capabilities": ["Unit test naming"],
    "defaultPrompt": [
      "Name and write Swift unit tests with exact observable contracts."
    ]
  }
}
```

- [ ] **Step 5: Create the Cursor marketplace**

`.cursor-plugin/marketplace.json`:

```json
{
  "name": "danny-sung-agent-skills",
  "owner": {
    "name": "Danny Sung"
  },
  "metadata": {
    "description": "Danny Sung's portable Swift and Apple-platform agent skills"
  },
  "plugins": [
    {
      "name": "swift-testing",
      "source": "plugins/swift-testing",
      "description": "Swift unit-test naming conventions for Swift Testing and XCTest"
    }
  ]
}
```

- [ ] **Step 6: Create the Cursor plugin manifest**

`plugins/swift-testing/.cursor-plugin/plugin.json`:

```json
{
  "name": "swift-testing",
  "displayName": "Swift Testing",
  "version": "1.0.0",
  "description": "Swift unit-test naming conventions for Swift Testing and XCTest",
  "author": {
    "name": "Danny Sung"
  },
  "repository": "https://github.com/dannys42/agent-skills",
  "keywords": ["swift", "ios", "unit-tests", "xctest", "agent-skills"],
  "category": "developer-tools",
  "tags": ["swift", "testing"],
  "skills": "./skills/"
}
```

- [ ] **Step 7: Create Gemini extension metadata**

`plugins/swift-testing/gemini-extension.json`:

```json
{
  "name": "swift-testing",
  "version": "1.0.0",
  "description": "Swift unit-test naming conventions for Swift Testing and XCTest"
}
```

- [ ] **Step 8: Create the MIT license**

`LICENSE`:

```text
MIT License

Copyright (c) 2026 Danny Sung

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 9: Create the plugin changelog**

`plugins/swift-testing/CHANGELOG.md`:

```markdown
# Changelog

## 1.0.0 — 2026-07-27

- Added `naming-swift-tests` for Swift Testing and XCTest naming conventions
- Added Claude, Codex, Cursor, and Gemini distribution adapters
- Added direct installation guidance for supported coding agents
```

- [ ] **Step 10: Create the focused plugin README**

`plugins/swift-testing/README.md`:

```markdown
# swift-testing

A cross-agent plugin for Swift unit-testing conventions.

## Skills

### `naming-swift-tests`

Names Swift Testing and XCTest files, suites, functions, values, fixtures,
test environments, and parameterized arguments so tests state exact observable
contracts.

## Install

See the repository [installation guide](../../README.md#install-naming-swift-tests)
for the complete supported-tool matrix and direct skill installation options.
```

- [ ] **Step 11: Create the root README**

`README.md`:

````markdown
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
````

- [ ] **Step 12: Validate all package metadata**

Run:

```bash
find . -path './.git' -prune -o -name '*.json' -print0 |
  xargs -0 -n1 jq empty

claude plugin validate .

uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/swift-testing
```

Expected: JSON parsing succeeds; Claude and Codex validation pass without an
error.

- [ ] **Step 13: Verify version and identity agreement**

Run:

```bash
jq -r '.metadata.version, .plugins[0].version' \
  .claude-plugin/marketplace.json

jq -r '.version' \
  plugins/swift-testing/.claude-plugin/plugin.json \
  plugins/swift-testing/.codex-plugin/plugin.json \
  plugins/swift-testing/.cursor-plugin/plugin.json \
  plugins/swift-testing/gemini-extension.json

rg -n 'danny-sung-agent-skills|Danny Sung.s Agent Skills|dannys42/agent-skills' \
  . README.md plugins
```

Expected: every version output is `1.0.0`; repository and marketplace identity
searches find only the approved names.

- [ ] **Step 14: Verify host documentation and local discovery**

Run:

```bash
rg -n \
  'Claude|Codex|Cursor|Gemini|GitHub Copilot|OpenCode|Roo Code|Zoo Code|ZCode|Zed|skills\.sh|SkillsMD|mdskills' \
  README.md

npx skills add ./plugins/swift-testing --list
```

Expected: every supported host and registry appears in the README. Discovery
reports exactly one available skill, `naming-swift-tests`.

- [ ] **Step 15: Review Task 2**

Dispatch independent specification and quality reviewers. Confirm:

- all adapter paths resolve;
- current schemas accept the manifests;
- install commands use `dannys42/agent-skills`;
- the marketplace identifier is `danny-sung-agent-skills`;
- no text implies external publication;
- the reference symlink is not tracked;
- no custom `registry.json` exists.

Resolve every Critical or Important finding and rerun affected checks.

- [ ] **Step 16: Commit the distribution task**

Run:

```bash
git add \
  .agents \
  .claude-plugin \
  .cursor-plugin \
  LICENSE \
  README.md \
  plugins/swift-testing

git commit -m "plugin(swift-testing): add cross-agent distribution"
```

Expected: the third repository commit contains the initial `1.0.0`
distribution and documentation.

### Task 3: Final verification and reference-repository recovery

**Files:**
- Verify: all tracked files in `~/projects/AITools/swift-testing-skill`
- Remove untracked symlink:
  `~/projects/AITools/swift-testing-skill/claude-marketplace`
- Restore Git state:
  `~/projects/AITools/claude-marketplace`

- [ ] **Step 1: Run final standalone-repository verification**

Run:

```bash
uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/swift-testing/skills/naming-swift-tests

test "$(wc -w < plugins/swift-testing/skills/naming-swift-tests/SKILL.md)" -le 500

find . -path './.git' -prune -o -name '*.json' -print0 |
  xargs -0 -n1 jq empty

claude plugin validate .

uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/swift-testing

npx skills add ./plugins/swift-testing --list

git diff --check
git status --short
git log --oneline --decorate -5
```

Expected: validators and discovery succeed; only the untracked
`claude-marketplace` symlink appears in status; history contains exactly the
three approved commits.

- [ ] **Step 2: Run a final black-box naming scenario**

Give a fresh agent only the installed `SKILL.md` and request:

```text
Return one parameterized Swift Testing test for correlated shipping inputs and
one XCTest unauthorized-deletion error test. Include filenames, suites/classes,
argument types, helpers where appropriate, and input/expected/observed values.
```

Expected:

- `ShippingCalculatorTests.swift` and `DocumentServiceTests.swift`;
- singular `TestArgument` and `testArgument`;
- visible `inputValues`, `expectedValue`, and `observedValue`;
- exact XCTest name
  `testThat_DeleteDocument_WithUnauthorizedUser_WillThrowAuthorizationError`;
- no `sut`, generic `subject`, hidden expected flags, or fixture literals in
  function names.

- [ ] **Step 3: Run a final independent branch review**

Review the complete three-commit history for specification coverage,
portability, token efficiency, adapter validity, README truthfulness, and
unintended reference content. Resolve any Critical or Important finding before
recovery.

- [ ] **Step 4: Audit the reference repository before destructive recovery**

Run:

```bash
reference_repo=/Users/dannys/projects/AITools/claude-marketplace

test -z "$(git -C "$reference_repo" status --porcelain)"

git -C "$reference_repo" log --oneline --reverse origin/main..main
```

Expected: the worktree is clean and the only commits after `origin/main` are:

```text
8ab02d7 docs: design portable Swift test naming skill
ded3053 docs: add distribution documentation requirement
2dd997b docs(swift-testing): plan portable naming skill
110b048 skill(swift-testing): add Swift test naming conventions
ce870a4 plugin(swift-testing): add cross-agent distribution
```

If the status or commit list differs, stop and ask the user instead of resetting.

- [ ] **Step 5: Restore the reference repository**

The user explicitly approved this destructive recovery after standalone
verification.

Run:

```bash
reference_repo=/Users/dannys/projects/AITools/claude-marketplace
git -C "$reference_repo" reset --hard origin/main
```

Expected:

```text
HEAD is now at 764a06c Add skill for creating MCPs
```

Verify:

```bash
git -C "$reference_repo" status --short
git -C "$reference_repo" log --oneline --decorate -3
```

Expected: clean status and local `main` at `origin/main`.

- [ ] **Step 6: Remove the reference symlink**

Run:

```bash
test -L claude-marketplace
unlink claude-marketplace
```

Expected: only the symlink is removed; the sibling reference repository remains
intact at `/Users/dannys/projects/AITools/claude-marketplace`.

- [ ] **Step 7: Confirm final local state**

Run:

```bash
git status --short
git log --oneline --decorate -5
git remote -v
```

Expected:

- the standalone repository is clean;
- history contains the three approved commits;
- no Git remote is configured;
- no GitHub repository has been created or pushed.
