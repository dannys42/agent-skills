# Portable Swift Design Patterns Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable `swift-design-patterns` plugin that helps agents choose among all 22 GoF patterns while preferring clearer Swift-native designs and using original, correctly attributed guidance.

**Architecture:** One discoverable `choosing-swift-design-patterns` skill routes greenfield and review requests through a compact decision index, then progressively loads one or two focused pattern references. A standard-library Python importer performs the one-time, rate-limited Refactoring.Guru research import; separate validators enforce corpus completeness, attribution, originality, reference linkage, and Swift example validity.

**Tech Stack:** Agent Skills Markdown, Python 3 standard library, `unittest`, Swift 6 toolchain, JSON plugin manifests, Codex/Claude/Cursor/Gemini marketplace adapters

---

## File Map

### Plugin and distribution

- `plugins/swift-design-patterns/.codex-plugin/plugin.json` — Codex manifest and UI metadata.
- `plugins/swift-design-patterns/.claude-plugin/plugin.json` — Claude Code manifest.
- `plugins/swift-design-patterns/.cursor-plugin/plugin.json` — Cursor manifest.
- `plugins/swift-design-patterns/gemini-extension.json` — Gemini CLI metadata.
- `plugins/swift-design-patterns/README.md` — installation, scope, attribution, and usage examples.
- `plugins/swift-design-patterns/.gitignore` — excludes `.research/`.
- `.agents/plugins/marketplace.json` — adds the Codex marketplace entry.
- `.claude-plugin/marketplace.json` — adds the Claude marketplace entry.
- `.cursor-plugin/marketplace.json` — adds the Cursor marketplace entry.
- `README.md` — lists the new plugin and skill.

### Skill

- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/SKILL.md` — selector workflow and progressive-loading rules.
- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/agents/openai.yaml` — Codex skill UI metadata.
- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/decision-index.md` — symptom, alternative, contraindication, and pattern routing table.
- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/{creational,structural,behavioral}/*.md` — 22 original pattern guides.

### Import and validation

- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/pattern_catalog.py` — canonical metadata for the 22 expected patterns.
- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/import_refactoring_guru.py` — polite resumable importer.
- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py` — structure, attribution, links, and Swift example checks.
- `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/audit_originality.py` — long exact-match audit against raw research pages.
- `plugins/swift-design-patterns/tests/test_import_refactoring_guru.py` — importer unit and fixture-server tests.
- `plugins/swift-design-patterns/tests/test_validate_content.py` — corpus validator tests.
- `plugins/swift-design-patterns/tests/selection-cases.json` — reusable behavioral scenarios and expected decisions.
- `plugins/swift-design-patterns/tests/baseline-results.md` — verbatim pre-skill agent outputs and observed failure modes.
- `plugins/swift-design-patterns/tests/forward-results.md` — verbatim post-skill outputs and rubric results.

## Reference Matrix

Use these exact filenames, source URLs, Swift-first alternatives, and example domains:

| Category | File | Source slug | Consider first | Original example domain |
|---|---|---|---|---|
| Creational | `abstract-factory.md` | `abstract-factory` | Generic configuration or injected closures | Compatible chart renderer families |
| Creational | `builder.md` | `builder` | Initializer defaults, configuration value, result builder | Validated HTTP request assembly |
| Creational | `factory-method.md` | `factory-method` | Direct initializer or injected creation closure | Document decoder selection |
| Creational | `prototype.md` | `prototype` | Struct copy and copy-on-write values | Deep copy of a linked workflow graph |
| Creational | `singleton.md` | `singleton` | Dependency injection or explicit environment value | Process-wide schema registry |
| Structural | `adapter.md` | `adapter` | Extension or small conversion function | Legacy temperature sensor adaptation |
| Structural | `bridge.md` | `bridge` | Generic parameter or protocol composition | Notifications across delivery channels |
| Structural | `composite.md` | `composite` | `indirect enum` for a closed tree | Document outline totals |
| Structural | `decorator.md` | `decorator` | Closure composition, protocol extension, property wrapper | Layered request middleware |
| Structural | `facade.md` | `facade` | Focused service with direct composition | Media import coordination |
| Structural | `flyweight.md` | `flyweight` | Shared immutable value and cache | Reused glyph styles |
| Structural | `proxy.md` | `proxy` | Actor-isolated cache or explicit wrapper | Permission-aware image repository |
| Behavioral | `chain-of-responsibility.md` | `chain-of-responsibility` | Array of closures or validation functions | Purchase validation pipeline |
| Behavioral | `command.md` | `command` | Closure or `UndoManager` registration | Reversible text edit history |
| Behavioral | `iterator.md` | `iterator` | `Sequence`, `IteratorProtocol`, or `AsyncSequence` | Depth-first tree sequence |
| Behavioral | `mediator.md` | `mediator` | Coordinator closure or shared observable model | Checkout field coordination |
| Behavioral | `memento.md` | `memento` | Value snapshot or `Codable` state | Drawing editor snapshots |
| Behavioral | `observer.md` | `observer` | Observation, `AsyncStream`, or direct callback | Typed sensor event stream |
| Behavioral | `state.md` | `state` | Enum plus exhaustive switch | Connection lifecycle behavior |
| Behavioral | `strategy.md` | `strategy` | Closure or generic algorithm parameter | Shipping-price calculation |
| Behavioral | `template-method.md` | `template-method` | Protocol extension and composition | Data import pipeline |
| Behavioral | `visitor.md` | `visitor` | Enum switch or protocol extension | Operations over an expression tree |

Construct every source URL by passing the exact slug in the matrix to the
`pattern_url` function defined in Task 3.

Do not copy source prose, code, or illustrations into the references.

### Task 1: Establish a clean execution workspace

**Files:**
- Verify: `.gitignore`
- Create at execution time: `.worktrees/swift-design-patterns`

- [ ] **Step 1: Confirm the repository is clean apart from known local reference material**

Run:

```bash
git status --short
git check-ignore -v .worktrees/
```

Expected: `claude-marketplace` may appear as the existing untracked reference symlink; `.worktrees/` is ignored by the root `.gitignore`.

- [ ] **Step 2: Create the isolated worktree**

Run:

```bash
git worktree add .worktrees/swift-design-patterns -b codex/swift-design-patterns
```

Expected: a new worktree on branch `codex/swift-design-patterns`.

- [ ] **Step 3: Verify the reference marketplace resolves outside the worktree changes**

Run:

```bash
git -C claude-marketplace status --short
git status --short
```

Expected: no changes inside the reference repository and no tracked changes in the implementation worktree.

### Task 2: Capture baseline pattern-selection failures

**Files:**
- Create: `plugins/swift-design-patterns/tests/selection-cases.json`
- Create: `plugins/swift-design-patterns/tests/baseline-results.md`

- [ ] **Step 1: Create the reusable selection cases**

Create `selection-cases.json` with these cases:

```json
[
  {
    "id": "greenfield-pricing",
    "mode": "greenfield",
    "prompt": "Design a Swift shipping calculator with three small interchangeable formulas selected at startup.",
    "expected": "Prefer a closure or generic function; Strategy is secondary if algorithms gain state or runtime substitution."
  },
  {
    "id": "review-small-state",
    "mode": "review",
    "prompt": "Review a Swift media control with enum State { case stopped, playing, paused } and one exhaustive switch containing one line per case.",
    "expected": "Keep the enum and switch; reject State as unnecessary."
  },
  {
    "id": "greenfield-product-family",
    "mode": "greenfield",
    "prompt": "Design a charting package that must create compatible axis, legend, and renderer implementations for SVG and Metal backends.",
    "expected": "Recommend Abstract Factory after comparing a generic configuration."
  },
  {
    "id": "review-scattered-coordination",
    "mode": "review",
    "prompt": "Review three call sites that repeat file loading, format detection, decoding, metadata extraction, and persistence.",
    "expected": "Recommend a focused Facade because subsystem coordination is repeated."
  },
  {
    "id": "greenfield-undo",
    "mode": "greenfield",
    "prompt": "Design reversible text edits that can be queued, replayed, undone, and redone.",
    "expected": "Recommend Command and explain why a bare closure becomes insufficient."
  },
  {
    "id": "review-event-stream",
    "mode": "review",
    "prompt": "Review a Swift sensor service that manually maintains an array of observer objects only to broadcast typed readings.",
    "expected": "Prefer AsyncStream or Observation when lifecycle semantics fit; Observer is secondary."
  },
  {
    "id": "named-visitor",
    "mode": "named",
    "prompt": "Use Visitor for a closed Swift enum representing five expression cases and two operations.",
    "expected": "Challenge the requested pattern and prefer exhaustive enum switches unless operations greatly outnumber stable cases."
  },
  {
    "id": "review-no-change",
    "mode": "review",
    "prompt": "Review a value-semantic configuration struct with a direct memberwise initializer and no branching creation logic.",
    "expected": "Recommend no change and reject Builder and Factory Method."
  }
]
```

- [ ] **Step 2: Run fresh agents without the new skill**

For each case, send only its `prompt` to a fresh agent with no new plugin files in context. Ask for one recommendation, up to two alternatives, and trade-offs. Record every response verbatim.

Expected: baseline responses reveal at least one of these failure classes: pattern overuse, failure to prefer Swift-native features, weak contraindications, missing trade-offs, or uncertain pattern differentiation.

- [ ] **Step 3: Write the baseline report**

Create `baseline-results.md` with:

```markdown
# Baseline Swift Pattern Selection Results

The responses below were captured before `choosing-swift-design-patterns`
existed. Each case records the unedited response followed by observed failure
classes chosen from: pattern overuse, missed Swift-native alternative,
incorrect pattern, weak contraindication, missing trade-off, or acceptable.
```

Append each case ID, exact prompt, verbatim response, and observed failure classes. Do not summarize in place of the raw response.

- [ ] **Step 4: Commit the baseline**

Run:

```bash
git add plugins/swift-design-patterns/tests
git commit -m "test(swift-design-patterns): capture selector baseline"
```

Expected: the two baseline files are committed before any skill content exists.

### Task 3: Define and test the canonical catalog

**Files:**
- Create: `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/pattern_catalog.py`
- Create: `plugins/swift-design-patterns/tests/test_import_refactoring_guru.py`

- [ ] **Step 1: Initialize the skill resource directories**

Run:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  choosing-swift-design-patterns \
  --path plugins/swift-design-patterns/skills \
  --resources scripts,references \
  --interface display_name="Choosing Swift Design Patterns" \
  --interface short_description="Choose clear Swift architecture" \
  --interface default_prompt="Use $choosing-swift-design-patterns to choose or review a Swift design."
```

Expected: the skill directory, generated template `SKILL.md`, `agents/openai.yaml`,
`scripts/`, and `references/` are created after the baseline has been captured.
Do not customize the skill body yet.

- [ ] **Step 2: Write the failing catalog test**

Add:

```python
class PatternCatalogTests(unittest.TestCase):
    def test_catalog_contains_22_unique_expected_patterns(self):
        self.assertEqual(len(PATTERNS), 22)
        self.assertEqual(len({pattern.slug for pattern in PATTERNS}), 22)
        self.assertEqual(
            {pattern.category for pattern in PATTERNS},
            {"creational", "structural", "behavioral"},
        )
        self.assertEqual(
            pattern_url("abstract-factory"),
            "https://refactoring.guru/design-patterns/abstract-factory/swift/example",
        )
```

Load `pattern_catalog.py` with `importlib.util.spec_from_file_location` because the skill directory contains hyphens.

- [ ] **Step 3: Run the test and verify RED**

Run:

```bash
python3 -m unittest plugins/swift-design-patterns/tests/test_import_refactoring_guru.py -v
```

Expected: import failure because `pattern_catalog.py` does not exist.

- [ ] **Step 4: Implement the catalog**

Define:

```python
from dataclasses import dataclass

CATALOG_URL = "https://refactoring.guru/design-patterns/swift"
CONTENT_POLICY_URL = "https://refactoring.guru/content-usage-policy"

@dataclass(frozen=True)
class Pattern:
    name: str
    slug: str
    category: str

PATTERNS = (
    Pattern("Abstract Factory", "abstract-factory", "creational"),
    Pattern("Builder", "builder", "creational"),
    Pattern("Factory Method", "factory-method", "creational"),
    Pattern("Prototype", "prototype", "creational"),
    Pattern("Singleton", "singleton", "creational"),
    Pattern("Adapter", "adapter", "structural"),
    Pattern("Bridge", "bridge", "structural"),
    Pattern("Composite", "composite", "structural"),
    Pattern("Decorator", "decorator", "structural"),
    Pattern("Facade", "facade", "structural"),
    Pattern("Flyweight", "flyweight", "structural"),
    Pattern("Proxy", "proxy", "structural"),
    Pattern("Chain of Responsibility", "chain-of-responsibility", "behavioral"),
    Pattern("Command", "command", "behavioral"),
    Pattern("Iterator", "iterator", "behavioral"),
    Pattern("Mediator", "mediator", "behavioral"),
    Pattern("Memento", "memento", "behavioral"),
    Pattern("Observer", "observer", "behavioral"),
    Pattern("State", "state", "behavioral"),
    Pattern("Strategy", "strategy", "behavioral"),
    Pattern("Template Method", "template-method", "behavioral"),
    Pattern("Visitor", "visitor", "behavioral"),
)

def pattern_url(slug: str) -> str:
    return f"https://refactoring.guru/design-patterns/{slug}/swift/example"
```

- [ ] **Step 5: Run the catalog test and verify GREEN**

Run the same `unittest` command.

Expected: one catalog test passes.

### Task 4: Implement the polite resumable importer test-first

**Files:**
- Create: `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/import_refactoring_guru.py`
- Modify: `plugins/swift-design-patterns/tests/test_import_refactoring_guru.py`
- Create: `plugins/swift-design-patterns/.gitignore`

- [ ] **Step 1: Add failing importer tests**

Define these deterministic test helpers:

```python
class ByteResponse:
    def __init__(self, content):
        self.content = content
        self.status = 200
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.content

class RecordingOpener:
    def __init__(self, results):
        self.results = list(results)
        self.urls = []

    def open(self, request, timeout=30):
        self.urls.append(request.full_url)
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return ByteResponse(result)

def http_error(status, headers):
    return urllib.error.HTTPError(
        url="https://refactoring.guru/test",
        code=status,
        msg="fixture error",
        hdrs=headers,
        fp=io.BytesIO(b"fixture error"),
    )

def write_cached_page(output, slug, content):
    (output / f"{slug}.html").write_bytes(content)
    manifest = {
        "patterns": {
            slug: {
                "sha256": hashlib.sha256(content).hexdigest(),
                "source_url": pattern_url(slug),
            }
        }
    }
    (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
```

Test these public seams:

```python
class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

class ImportClientTests(unittest.TestCase):
    def test_rejects_interval_below_five_seconds(self):
        with self.assertRaisesRegex(ValueError, "at least 5"):
            ImportClient(min_interval=4.99)

    def test_waits_five_seconds_between_requests(self):
        clock = FakeClock()
        opener = RecordingOpener([b"catalog", b"pattern"])
        client = ImportClient(
            min_interval=5.0,
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )
        client.fetch("https://refactoring.guru/design-patterns/swift")
        client.fetch("https://refactoring.guru/design-patterns/state/swift/example")
        self.assertEqual(clock.sleeps, [5.0])

    def test_retry_after_never_shortens_normal_interval(self):
        clock = FakeClock()
        opener = RecordingOpener([
            http_error(429, {"Retry-After": "2"}),
            b"ok",
        ])
        client = ImportClient(
            min_interval=5.0,
            opener=opener,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )
        self.assertEqual(client.fetch("https://refactoring.guru/test"), b"ok")
        self.assertGreaterEqual(sum(clock.sleeps), 5.0)

    def test_valid_cached_page_is_not_refetched(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_cached_page(output, "state", b"cached")
            opener = RecordingOpener([])
            import_pattern("state", output, ImportClient(opener=opener))
            self.assertEqual(opener.urls, [])
```

Also test catalog parsing, redirects through the opener, checksum mismatch
refetch, bounded retries, interruption preserving completed manifest entries,
and a catalog missing one expected slug.

Add one localhost integration test using `ThreadingHTTPServer`. Serve two URLs,
record `time.monotonic()` in the handler for each request, fetch both with the
default five-second interval, and assert the second timestamp minus the first
is at least `5.0`. Shut down and join the server thread in `addCleanup` so the
test cannot leave a background server running.

- [ ] **Step 2: Run importer tests and verify RED**

Run:

```bash
python3 -m unittest plugins/swift-design-patterns/tests/test_import_refactoring_guru.py -v
```

Expected: failures for undefined importer types and functions.

- [ ] **Step 3: Implement the importer**

Implement these exact interfaces and behavior:

```python
MINIMUM_INTERVAL = 5.0
DEFAULT_USER_AGENT = (
    "danny-sung-agent-skills research importer/1.0 "
    "(contact: https://github.com/dannys42/agent-skills)"
)

class ImportClient:
    """Fetch Refactoring.Guru pages sequentially with bounded retries."""

    def __init__(
        self,
        min_interval=MINIMUM_INTERVAL,
        retries=2,
        opener=None,
        monotonic=time.monotonic,
        sleep=time.sleep,
    ):
        if min_interval < MINIMUM_INTERVAL:
            raise ValueError("request interval must be at least 5 seconds")
        self.min_interval = min_interval
        self.retries = retries
        self._opener = opener or urllib.request.build_opener()
        self._monotonic = monotonic
        self._sleep = sleep
        self._last_request_at = None
```

Add `fetch(url) -> bytes`, `discover_pattern_urls(catalog_html)`,
`sha256_bytes(content)`, `load_manifest(output)`,
`cached_page_is_valid(output, slug, manifest)`,
`import_pattern(slug, output, client)`, `run_import(output, min_interval,
refresh)`, and `main(argv=None)`. Use the parameter names exactly as written so
the tests can call them directly.

`ImportClient.fetch` starts every attempt with:

```python
if self._last_request_at is not None:
    elapsed = self._monotonic() - self._last_request_at
    self._sleep(max(0.0, self.min_interval - elapsed))

self._last_request_at = self._monotonic()
```

Use `urllib.request.Request`, `urllib.request.build_opener`, and the descriptive user agent. Retry only HTTP 429 and 5xx responses plus `URLError`; honor numeric `Retry-After` with `max(min_interval, retry_after)`. Write HTML through a temporary sibling file followed by `Path.replace`. Store `manifest.json` with catalog URL, content-policy URL, timestamps, status, byte count, SHA-256, and source URL. Append each real attempt timestamp and URL to `requests.jsonl`. Save the catalog response as `catalog.html` and each pattern response under its canonical slug, such as `state.html`.

`discover_pattern_urls` must parse links matching:

```python
r"^/design-patterns/([a-z-]+)/swift/example$"
```

and require exact equality with the 22 canonical slugs.

CLI:

```text
usage: import_refactoring_guru.py OUTPUT [--min-interval SECONDS] [--refresh]
```

- [ ] **Step 4: Exclude raw research**

Create `plugins/swift-design-patterns/.gitignore`:

```gitignore
.research/
```

- [ ] **Step 5: Run importer tests and verify GREEN**

Run:

```bash
python3 -m unittest plugins/swift-design-patterns/tests/test_import_refactoring_guru.py -v
```

Expected: all importer tests pass without network access and without real five-second sleeps.

- [ ] **Step 6: Commit the importer**

Run:

```bash
git add plugins/swift-design-patterns/.gitignore \
  plugins/swift-design-patterns/tests/test_import_refactoring_guru.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts
git commit -m "feat(swift-design-patterns): add polite research importer"
```

### Task 5: Perform and verify the one-time live import

**Files:**
- Create but do not track: `plugins/swift-design-patterns/.research/`

- [ ] **Step 1: Run the live importer**

Run:

```bash
python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/import_refactoring_guru.py \
  plugins/swift-design-patterns/.research \
  --min-interval 5
```

Expected: catalog plus 22 pattern pages downloaded sequentially; runtime is at least 110 seconds after the catalog request.

- [ ] **Step 2: Verify completeness and request spacing**

Run:

```bash
python3 - <<'PY'
import json
from pathlib import Path

root = Path("plugins/swift-design-patterns/.research")
manifest = json.loads((root / "manifest.json").read_text())
events = [json.loads(line) for line in (root / "requests.jsonl").read_text().splitlines()]
intervals = [
    right["monotonic"] - left["monotonic"]
    for left, right in zip(events, events[1:])
]
assert len(manifest["patterns"]) == 22
assert len(list(root.glob("*.html"))) == 23
assert all(interval >= 5.0 for interval in intervals), intervals
print(f"verified {len(manifest['patterns'])} patterns; minimum interval={min(intervals):.3f}s")
PY
```

Expected: `verified 22 patterns; minimum interval=` followed by a value at least `5.000s`.

- [ ] **Step 3: Verify research remains ignored**

Run:

```bash
git status --short --ignored plugins/swift-design-patterns/.research
```

Expected: only `!! plugins/swift-design-patterns/.research/`.

### Task 6: Scaffold portable plugin manifests

**Files:**
- Create: `plugins/swift-design-patterns/.codex-plugin/plugin.json`
- Create: `plugins/swift-design-patterns/.claude-plugin/plugin.json`
- Create: `plugins/swift-design-patterns/.cursor-plugin/plugin.json`
- Create: `plugins/swift-design-patterns/gemini-extension.json`

- [ ] **Step 1: Scaffold the Codex plugin with the plugin-creator script**

Run the installed `plugin-creator` scaffold with:

```bash
python3 /Users/dannys/.codex/skills/.system/plugin-creator/scripts/create_basic_plugin.py \
  swift-design-patterns \
  --path plugins \
  --with-skills \
  --force
```

Use `--force` only because the importer tests already created the intended plugin directory. Verify the script preserves those files before continuing.

- [ ] **Step 2: Replace the Codex manifest with final metadata**

Use:

```json
{
  "name": "swift-design-patterns",
  "version": "1.0.0",
  "description": "Original Swift design-pattern selection guidance informed by and attributed to Refactoring.Guru",
  "license": "MIT",
  "skills": "./skills/",
  "author": {
    "name": "Danny Sung",
    "url": "https://github.com/dannys42"
  },
  "repository": "https://github.com/dannys42/agent-skills",
  "keywords": [
    "swift",
    "ios",
    "macos",
    "design-patterns",
    "architecture",
    "refactoring",
    "agent-skills"
  ],
  "interface": {
    "displayName": "Swift Design Patterns",
    "shortDescription": "Choose clear Swift architecture",
    "longDescription": "Choose, compare, and review Swift designs across 22 common patterns while preferring simpler Swift-native constructs.",
    "developerName": "Danny Sung",
    "category": "Developer Tools",
    "capabilities": [
      "Swift-native architecture selection",
      "GoF pattern comparison",
      "Existing-code design review"
    ],
    "defaultPrompt": [
      "Choose or review a Swift design, preferring the clearest Swift-native approach."
    ]
  }
}
```

- [ ] **Step 3: Add Claude, Cursor, and Gemini manifests**

Match the existing `swift-testing` shapes. Use the same version, description, license, author, repository, and keywords. Set Cursor `displayName` to `Swift Design Patterns`, category to `developer-tools`, tags to `["swift", "architecture", "design-patterns"]`, and skills to `./skills/`.

- [ ] **Step 4: Validate the manifest JSON and record deferred plugin validation**

Run:

```bash
python3 -m json.tool plugins/swift-design-patterns/.codex-plugin/plugin.json
python3 -m json.tool plugins/swift-design-patterns/.claude-plugin/plugin.json
python3 -m json.tool plugins/swift-design-patterns/.cursor-plugin/plugin.json
python3 -m json.tool plugins/swift-design-patterns/gemini-extension.json
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/swift-design-patterns
```

Expected: all four JSON validation commands succeed. Plugin validation reports
only that `skills/choosing-swift-design-patterns/SKILL.md` is missing because
the selector is intentionally authored in Task 12. Full plugin validation is
deferred until Task 12 and remains part of final verification in Task 15. The
`uv` invocation supplies PyYAML in a temporary environment and keeps its cache
under `/tmp`, without changing repository or system dependencies.

- [ ] **Step 5: Commit manifests**

Run:

```bash
git add plugins/swift-design-patterns/.codex-plugin \
  plugins/swift-design-patterns/.claude-plugin \
  plugins/swift-design-patterns/.cursor-plugin \
  plugins/swift-design-patterns/gemini-extension.json \
  docs/superpowers/plans/2026-07-30-swift-design-patterns-plugin.md
git commit -m "feat(swift-design-patterns): scaffold portable plugin"
```

### Task 7: Build the content validator test-first

**Files:**
- Create: `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py`
- Create: `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/audit_originality.py`
- Create: `plugins/swift-design-patterns/tests/test_validate_content.py`

- [ ] **Step 1: Write failing validator tests**

Create temporary miniature corpora. Use this complete representative test and
repeat the same arrange/validate/assert structure for the five named failure
conditions:

```python
class ContentValidatorTests(unittest.TestCase):
    def test_reports_missing_required_section(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "state.md"
            reference.write_text(
                "# State\n\n## Intent\n\nKeep state behavior focused.\n",
                encoding="utf-8",
            )

            errors = validate_reference(
                reference,
                Pattern("State", "state", "behavioral"),
            )

            self.assertIn(
                "state.md: missing heading '## Avoid it when'",
                errors,
            )
```

Add `test_reports_missing_pattern_reference`,
`test_reports_missing_pattern_specific_attribution`,
`test_reports_reference_missing_from_decision_index`,
`test_accepts_complete_reference`, and
`test_originality_audit_reports_twenty_word_exact_match`. Each test must assert
the complete diagnostic string, not only that an error occurred.

The required headings are:

```python
REQUIRED_HEADINGS = (
    "## Intent",
    "## Prefer Swift-native alternatives when",
    "## Choose this pattern when",
    "## Avoid it when",
    "## Design pressures",
    "## Swift implementation",
    "## Concurrency and ownership",
    "## Compare",
    "## Example",
    "## Review checklist",
    "## Attribution",
)
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest plugins/swift-design-patterns/tests/test_validate_content.py -v
```

Expected: import failure for missing validator modules.

- [ ] **Step 3: Implement validation**

Expose `validate_reference(path, pattern)`, `validate_decision_index(path)`,
`extract_swift_examples(markdown)`, `typecheck_swift_examples(paths)`, and
`validate_all(skill_root)`. Every validation function returns a deterministic
`list[str]`; the CLI prints one diagnostic per line and exits 1 when the list
is non-empty. Support `--allow-incomplete` only for incremental authorship: it
may suppress missing-reference and missing-index diagnostics, but it must still
validate every file that is present.

Require exactly one fenced Swift example per pattern reference. Type-check each example in an isolated temporary `.swift` file with:

```python
subprocess.run(
    ["xcrun", "swiftc", "-typecheck", str(example_path)],
    check=False,
    capture_output=True,
    text=True,
)
```

`audit_originality.py` must strip HTML, normalize whitespace, compare case-folded 20-word shingles, ignore URLs and headings, and report the distributable file, raw source file, and matching words for every exact match.

- [ ] **Step 4: Run tests and verify GREEN**

Run both test modules:

```bash
python3 -m unittest discover -s plugins/swift-design-patterns/tests -v
```

Expected: importer and validator tests pass.

- [ ] **Step 5: Commit validators**

Run:

```bash
git add plugins/swift-design-patterns/tests/test_validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts
git commit -m "test(swift-design-patterns): validate pattern corpus"
```

### Task 8: Author the five creational references

**Files:**
- Create: `references/creational/abstract-factory.md`
- Create: `references/creational/builder.md`
- Create: `references/creational/factory-method.md`
- Create: `references/creational/prototype.md`
- Create: `references/creational/singleton.md`

All paths are relative to `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/`.

- [ ] **Step 1: Author each reference from the reference matrix**

Use all required headings from Task 7. Keep each file focused, original, and approximately 500–900 words. Each example must be self-contained, use only the Swift standard library or Foundation, and demonstrate the example domain in the matrix.

End Abstract Factory with:

```markdown
## Attribution

Original Swift guidance informed by
[Refactoring.Guru: Abstract Factory in Swift](https://refactoring.guru/design-patterns/abstract-factory/swift/example).
Used in accordance with the
[Refactoring.Guru Content Usage Policy](https://refactoring.guru/content-usage-policy).
No source code or illustrations are reproduced.
```

Apply the identical attribution structure with the correct title and slug to the other four files.

- [ ] **Step 2: Run content validation**

Run:

```bash
python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns \
  --allow-incomplete
```

Expected: the five present references pass; only the 17 not-yet-authored references are reported as intentionally missing.

- [ ] **Step 3: Run originality audit**

Run:

```bash
python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/audit_originality.py \
  plugins/swift-design-patterns/.research \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
```

Expected: no 20-word exact matches.

- [ ] **Step 4: Commit creational references**

Run:

```bash
git add plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/creational
git commit -m "docs(swift-design-patterns): add creational guidance"
```

### Task 9: Author the seven structural references

**Files:**
- Create: `references/structural/adapter.md`
- Create: `references/structural/bridge.md`
- Create: `references/structural/composite.md`
- Create: `references/structural/decorator.md`
- Create: `references/structural/facade.md`
- Create: `references/structural/flyweight.md`
- Create: `references/structural/proxy.md`

- [ ] **Step 1: Author the references**

Follow the same exact contract as Task 8, using the structural rows of the reference matrix. Explicitly distinguish:

- Adapter from Facade and Bridge.
- Bridge from Strategy and Adapter.
- Composite from a closed `indirect enum`.
- Decorator from middleware closure composition and Proxy.
- Facade from Mediator and a generic “manager” type.
- Flyweight from ordinary caching.
- Proxy from Decorator and actor-isolated caching.

- [ ] **Step 2: Validate and type-check**

Run `validate_content.py --allow-incomplete`.

Expected: all 12 authored references pass; only the 10 behavioral files remain missing.

- [ ] **Step 3: Audit originality**

Run the Task 8 originality command.

Expected: no 20-word exact matches.

- [ ] **Step 4: Commit structural references**

Run:

```bash
git add plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/structural
git commit -m "docs(swift-design-patterns): add structural guidance"
```

### Task 10: Author the ten behavioral references

**Files:**
- Create: `references/behavioral/chain-of-responsibility.md`
- Create: `references/behavioral/command.md`
- Create: `references/behavioral/iterator.md`
- Create: `references/behavioral/mediator.md`
- Create: `references/behavioral/memento.md`
- Create: `references/behavioral/observer.md`
- Create: `references/behavioral/state.md`
- Create: `references/behavioral/strategy.md`
- Create: `references/behavioral/template-method.md`
- Create: `references/behavioral/visitor.md`

- [ ] **Step 1: Author the references**

Follow the same exact contract as Task 8, using the behavioral rows of the reference matrix. Explicitly distinguish:

- Chain of Responsibility from a simple loop of validators.
- Command from one-off closures.
- Iterator from native `Sequence` and `AsyncSequence`.
- Mediator from Facade and a shared observable model.
- Memento from ordinary value snapshots and persistence.
- Observer from Observation, `AsyncStream`, notifications, and callbacks.
- State from an enum switch and Strategy.
- Strategy from closures and generic parameters.
- Template Method from protocol extensions and composition.
- Visitor from exhaustive enum switching.

- [ ] **Step 2: Run complete content validation**

Run:

```bash
python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns \
  --allow-incomplete
```

Expected: all 22 references satisfy structure, attribution, and Swift
type-checking; the not-yet-authored decision index is the only suppressed
missing file.

- [ ] **Step 3: Audit originality**

Run the Task 8 originality command.

Expected: no 20-word exact matches.

- [ ] **Step 4: Commit behavioral references**

Run:

```bash
git add plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/behavioral
git commit -m "docs(swift-design-patterns): add behavioral guidance"
```

### Task 11: Create the decision index

**Files:**
- Create: `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/decision-index.md`

- [ ] **Step 1: Write the index**

Start with:

```markdown
# Swift Design Pattern Decision Index

Use this index only after identifying a concrete design pressure. Prefer no
change or the listed Swift-native alternative when it remains clearer. Load at
most two linked pattern references before recommending an approach.
```

Add one row per reference-matrix entry with columns:

```markdown
| Pressure or symptom | Consider first | Pattern when pressure persists | Avoid when | Reference |
```

Use direct relative links such as:

```markdown
[Strategy](behavioral/strategy.md)
```

Add a “Commonly confused choices” table covering Factory Method versus Abstract Factory versus Builder, Adapter versus Bridge versus Facade, Decorator versus Proxy, State versus Strategy, and Observer versus Mediator.

- [ ] **Step 2: Run complete content validation**

Run `validate_content.py` without `--allow-incomplete`.

Expected: all 22 references are linked exactly once or more and validation passes.

- [ ] **Step 3: Commit the index**

Run:

```bash
git add plugins/swift-design-patterns/skills/choosing-swift-design-patterns/references/decision-index.md
git commit -m "docs(swift-design-patterns): add pattern decision index"
```

### Task 12: Create the selector skill

**Files:**
- Create: `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/SKILL.md`
- Create: `plugins/swift-design-patterns/skills/choosing-swift-design-patterns/agents/openai.yaml`

- [ ] **Step 1: Regenerate final skill metadata**

Run:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns \
  --interface display_name="Choosing Swift Design Patterns" \
  --interface short_description="Choose clear Swift architecture" \
  --interface default_prompt="Use $choosing-swift-design-patterns to choose or review a Swift design."
```

Expected: `agents/openai.yaml` contains only the final three interface values.

- [ ] **Step 2: Write `SKILL.md`**

Use this frontmatter:

```yaml
---
name: choosing-swift-design-patterns
description: Use when designing or reviewing Swift code that may need a GoF design pattern, when comparing named patterns, or when code shows creation, interface, hierarchy, state, event, traversal, coordination, undo, behavior-variation, or access-control pressures.
---
```

The body must:

- state that clarity wins over pattern use;
- apply the same “no change, Swift-native, GoF pattern” priority to greenfield and review work;
- instruct the agent to identify concrete pressure before opening the index;
- link directly to `references/decision-index.md`;
- limit detailed loading to one or two references;
- require one recommendation and at most two lower-ranked alternatives;
- require costs and contraindications;
- prohibit recommendations for uninspected existing code;
- direct named-pattern requests through the same Swift-native challenge;
- include catalog and Content Usage Policy attribution;
- include a quick response template.

Keep the body under 600 words.

- [ ] **Step 3: Validate skill structure**

Run:

```bash
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
wc -w plugins/swift-design-patterns/skills/choosing-swift-design-patterns/SKILL.md
```

Expected: validation succeeds and the word count is below 600.

- [ ] **Step 4: Commit the complete skill**

Run:

```bash
git add plugins/swift-design-patterns/skills/choosing-swift-design-patterns/SKILL.md \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns/agents/openai.yaml
git commit -m "feat(swift-design-patterns): add pattern selector skill"
```

### Task 13: Forward-test and refine the skill

**Files:**
- Create: `plugins/swift-design-patterns/tests/forward-results.md`
- Modify if failures demand it: selector, index, or references

- [ ] **Step 1: Run every selection case with the skill**

Use fresh agents. Provide only the case prompt plus the completed skill directory. Do not provide the expected answer, baseline result, or suspected failure. Record exact responses.

- [ ] **Step 2: Score responses**

For every case, record pass/fail for:

```text
correct primary recommendation
Swift-native alternative considered
GoF pattern rejected when unnecessary
at most two alternatives
costs and contraindications stated
correct detailed reference loaded
no unrelated references loaded
attribution preserved when source guidance is discussed
```

Create `forward-results.md` with raw responses followed by the rubric.

- [ ] **Step 3: Close observed gaps**

Make the smallest change to the selector, index, or one reference that directly addresses each failed rubric item. Do not add generic prose unrelated to an observed failure.

- [ ] **Step 4: Re-run failed and neighboring cases**

Expected: all eight cases pass, including the small enum, named Visitor, event stream, and no-change counterexamples.

- [ ] **Step 5: Re-run structural validation**

Run:

```bash
python3 -m unittest discover -s plugins/swift-design-patterns/tests -v
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
```

Expected: all checks pass.

- [ ] **Step 6: Commit forward-test results and refinements**

Run:

```bash
git add plugins/swift-design-patterns/tests/forward-results.md \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
git commit -m "test(swift-design-patterns): verify selector behavior"
```

### Task 14: Add portable marketplace metadata and documentation

**Files:**
- Create: `plugins/swift-design-patterns/README.md`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.cursor-plugin/marketplace.json`
- Modify: `README.md`

- [ ] **Step 1: Write plugin documentation**

Document installation for Codex, Claude Code, and open skill installers using the same command patterns as `swift-testing`. Include:

```markdown
## Attribution

This plugin contains original Swift guidance informed by the
[Refactoring.Guru Swift design-pattern catalog](https://refactoring.guru/design-patterns/swift)
and used in accordance with its
[Content Usage Policy](https://refactoring.guru/content-usage-policy).
The plugin does not redistribute Refactoring.Guru source code or illustrations.
Each pattern reference links to its specific source page.
```

- [ ] **Step 2: Add marketplace entries**

Append `swift-design-patterns` after `swift-testing` in all three marketplace files. Codex uses:

```json
{
  "name": "swift-design-patterns",
  "source": {
    "source": "local",
    "path": "./plugins/swift-design-patterns"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Developer Tools"
}
```

Claude and Cursor entries must mirror the existing `swift-testing` shapes with version `1.0.0`, the attribution-aware description, and architecture/design-pattern keywords.

- [ ] **Step 3: Update the repository README**

Add a plugin-table row for `swift-design-patterns` and a concise skill section that explains the selector, progressive disclosure, Swift-native priority, and attribution.

- [ ] **Step 4: Validate JSON and plugin manifests**

Run:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .cursor-plugin/marketplace.json >/dev/null
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/swift-design-patterns
```

Expected: all JSON parses and plugin validation succeeds.

- [ ] **Step 5: Commit distribution metadata**

Run:

```bash
git add .agents/plugins/marketplace.json \
  .claude-plugin/marketplace.json \
  .cursor-plugin/marketplace.json \
  README.md \
  plugins/swift-design-patterns/README.md
git commit -m "docs(swift-design-patterns): add portable distribution"
```

### Task 15: Run final verification and request review

**Files:**
- Verify all new and modified files

- [ ] **Step 1: Run the full deterministic suite**

Run:

```bash
python3 -m unittest discover -s plugins/swift-design-patterns/tests -v
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
UV_CACHE_DIR=/tmp/codex-uv-cache uv run --with pyyaml python \
  /Users/dannys/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/swift-design-patterns
python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/validate_content.py \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
python3 plugins/swift-design-patterns/skills/choosing-swift-design-patterns/scripts/audit_originality.py \
  plugins/swift-design-patterns/.research \
  plugins/swift-design-patterns/skills/choosing-swift-design-patterns
git diff --check main...HEAD
```

Expected: all tests and validators pass, all 22 Swift examples type-check, the originality audit finds no 20-word exact matches, and Git reports no whitespace errors.

- [ ] **Step 2: Prove the reference marketplace was untouched**

Run:

```bash
git -C /Users/dannys/projects/AITools/claude-marketplace status --short
git diff --name-only main...HEAD | rg '^claude-marketplace/' && exit 1 || true
```

Expected: no output from the reference repository and no changed path under `claude-marketplace/`.

- [ ] **Step 3: Prove raw research is excluded**

Run:

```bash
git ls-files plugins/swift-design-patterns/.research
git status --short --ignored plugins/swift-design-patterns/.research
```

Expected: the first command prints nothing; the second reports only the ignored research directory.

- [ ] **Step 4: Inspect final change scope**

Run:

```bash
git status --short
git diff --stat main...HEAD
git log --oneline main..HEAD
```

Expected: clean worktree, only the planned plugin/docs/marketplace changes, and focused commits for baseline, importer, manifests, references, selector, behavioral validation, and distribution.

- [ ] **Step 5: Request code and content review**

Use `requesting-code-review` to review:

- selector correctness and restraint;
- importer delay and retry safety;
- attribution and originality;
- Swift example validity;
- portable manifest consistency;
- token-efficient progressive disclosure.

Resolve any findings, rerun Step 1, and create a focused fix commit if files change.
