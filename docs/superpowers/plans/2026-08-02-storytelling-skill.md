# Storytelling Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a portable `storytelling` plugin whose `crafting-compelling-stories` skill applies Joanna Wiebe's storytelling framework across narrative and marketing work without fabricating facts or forcing one formula onto every medium.

**Architecture:** Package one concise behavioral skill with generated Codex UI metadata and an archival, attributed transcript reference. Protect the behavior with contract tests, cross-agent marketplace manifests, baseline and frozen forward evaluations, and a full skill-optimizer profile tied to one distributable artifact hash.

**Tech Stack:** Markdown skill instructions, JSON/YAML plugin metadata, Python 3 standard-library `unittest`, the repository's skill-development optimizer, and fresh-agent behavioral evaluation.

---

## File Map

Create these focused files:

- `plugins/storytelling/skills/crafting-compelling-stories/SKILL.md`: trigger and operating workflow.
- `plugins/storytelling/skills/crafting-compelling-stories/agents/openai.yaml`: Codex UI metadata.
- `plugins/storytelling/skills/crafting-compelling-stories/references/joanna-wiebe-storytelling-transcript.txt`: attributed archival transcript; never an ordinary runtime dependency.
- `plugins/storytelling/.codex-plugin/plugin.json`: Codex packaging and interface metadata.
- `plugins/storytelling/.claude-plugin/plugin.json`: Claude plugin metadata.
- `plugins/storytelling/.cursor-plugin/plugin.json`: Cursor plugin metadata.
- `plugins/storytelling/gemini-extension.json`: Gemini extension identity.
- `plugins/storytelling/README.md`: concise plugin purpose and installation pointer.
- `plugins/storytelling/CHANGELOG.md`: initial release record.
- `plugins/storytelling/LICENSE`: repository-standard MIT license for original plugin material.
- `plugins/storytelling/skill-optimizer.json`: distributable selection and full-profile commands.
- `plugins/storytelling/tests/test_plugin_contract.py`: deterministic packaging, attribution, content, and corpus contracts.
- `plugins/storytelling/tests/evaluation-cases.json`: frozen behavioral prompts.
- `plugins/storytelling/tests/evaluation-rubric.json`: Boolean scoring keys.
- `plugins/storytelling/tests/baseline-results.md`: pre-skill fresh-agent evidence.
- `plugins/storytelling/tests/artifact.json`: frozen final artifact identity.
- `plugins/storytelling/tests/evaluation-evidence.json`: one verified headline cohort.
- `plugins/storytelling/tests/validation-results.json`: full-profile deterministic results.

Modify these repository indexes:

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.cursor-plugin/marketplace.json`
- `README.md`

### Task 1: Freeze evaluation requirements and capture RED behavior

**Files:**
- Create: `plugins/storytelling/tests/evaluation-cases.json`
- Create: `plugins/storytelling/tests/evaluation-rubric.json`
- Create: `plugins/storytelling/tests/baseline-results.md`
- Create: `plugins/storytelling/tests/test_plugin_contract.py`

- [ ] **Step 1: Create the behavioral cases before the skill exists**

Write `evaluation-cases.json` with these exact case IDs and task-local prompts:

```json
[
  {
    "id": "saas-landing-page",
    "prompt": "Write the narrative opening and CTA for a landing page for Briefly, a meeting-summary tool. Audience: engineering managers. Supplied facts only: it turns an uploaded transcript into a summary; Acme's pilot reduced its weekly recap-writing time from 90 minutes to 25 minutes; Acme approved use of its name. Do not add product capabilities or results."
  },
  {
    "id": "founder-story",
    "prompt": "Turn these notes into a 250-word founder story: Mina ran a neighborhood bakery; a freezer failed at 4:40 a.m. before a wedding order; handwritten inventory made it hard to see what could be remade; she later built a simple batch tracker with her brother. Do not invent quotations, dates, customers, or outcomes."
  },
  {
    "id": "speech-opening",
    "prompt": "Write a 90-second opening for a talk to first-time managers about giving useful feedback. Desired feeling: recognized, then hopeful. Avoid sales language."
  },
  {
    "id": "fiction-scene",
    "prompt": "Rewrite this slow opening as a vivid 180-word scene while preserving third-person limited voice and the fact that Mara is avoiding a letter: 'Mara was nervous. The room was old and unpleasant. There was a letter on the table that she did not want to read.'"
  },
  {
    "id": "incomplete-marketing-brief",
    "prompt": "Write launch copy for a new meal-planning app. I have not supplied its features, audience research, testimonials, price, results, or launch date. Make it persuasive and urgent."
  },
  {
    "id": "preserve-voice-edit",
    "prompt": "Tighten this copy without changing its dry, understated voice: 'At 2:13 on Tuesday, the dashboard went red. This was inconvenient. We had, after all, promised the board that red dashboards were now mostly a historical artifact. The office ficus remained neutral. Our incident log did not.' Remove details that do not earn a place, but preserve any detail that establishes tone or pays off."
  },
  {
    "id": "grammar-only-negative-trigger",
    "prompt": "Correct grammar only: 'The reports is ready and it were sent yesterday.' Do not introduce narrative or marketing language."
  },
  {
    "id": "factual-prose-negative-trigger",
    "prompt": "Summarize these facts in two plain sentences without storytelling: Water freezes at 0°C at standard atmospheric pressure. Dissolved solutes can lower the freezing point."
  }
]
```

- [ ] **Step 2: Declare the frozen rubric**

Write `evaluation-rubric.json`:

```json
[
  "appropriate_triggering",
  "audience_goal_medium_constraints_handled",
  "structure_adapted_to_task",
  "principles_applied_selectively",
  "orientation_imagery_details_payoff_ending_effective",
  "supplied_voice_and_facts_preserved",
  "unsupported_claims_not_invented",
  "ethical_marketing_and_proportionate_cta",
  "deliverable_first_without_framework_lecture"
]
```

- [ ] **Step 3: Run every positive case through a fresh agent without the skill**

Use one fresh agent per case for the first six cases. Give it only the case prompt; do not mention the intended skill, framework, rubric, or expected failure. Record each verbatim response and agent-reported files read in `baseline-results.md` under the case ID.

Expected RED evidence: at least one response invents or overstates facts, forces conversion mechanics into non-marketing work, leaves a hook unpaid, flattens the supplied voice, or explains its method before delivering the artifact. If none fail, add one new ambiguity or pressure case before authoring the skill and record why it exposes a real requirement.

- [ ] **Step 4: Write contract tests before packaging**

Create `test_plugin_contract.py` using `unittest`. Define canonical constants and tests that require:

```python
PLUGIN_NAME = "storytelling"
SKILL_NAME = "crafting-compelling-stories"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = (
    "Audience-aware storytelling and narrative copy grounded in an "
    "attributed Joanna Wiebe framework"
)
SOURCE_URL = "https://www.youtube.com/watch?v=oCnxnaVg0bY"
REQUIRED_CASE_IDS = {
    "saas-landing-page",
    "founder-story",
    "speech-opening",
    "fiction-scene",
    "incomplete-marketing-brief",
    "preserve-voice-edit",
    "grammar-only-negative-trigger",
    "factual-prose-negative-trigger",
}
```

Test exact manifest identity across all four adapters; exact `agents/openai.yaml`; two-field SKILL frontmatter; every required evaluation ID; transcript relocation; a provenance header containing `Joanna Wiebe`, the video title, `SOURCE_URL`, and `Reference only`; absence of `misc/psychology_storytelling_transcript.txt`; and the following behavioral contract phrases in `SKILL.md`:

```python
for phrase in (
    "Do not read the archival transcript during ordinary use",
    "Never invent",
    "Choose one primary structure",
    "Apply only the principles that serve the assignment",
    "Preserve the author's voice",
    "Return the deliverable first",
):
    self.assertIn(phrase, skill_text)
```

Also assert that `SKILL.md` does not contain the transcript's unsupported `40%`, `70%`, or `twice as memorable` claims.

- [ ] **Step 5: Run the contract test to verify RED**

Run:

```bash
python3 -m unittest plugins/storytelling/tests/test_plugin_contract.py -v
```

Expected: FAIL because the plugin manifests, skill, metadata, transcript destination, and marketplace entries do not exist.

- [ ] **Step 6: Commit only the reproducible baseline artifacts**

Do not commit the intentionally failing contract test separately. Commit the cases, rubric, and baseline evidence:

```bash
git add plugins/storytelling/tests/evaluation-cases.json plugins/storytelling/tests/evaluation-rubric.json plugins/storytelling/tests/baseline-results.md
git commit -m "test(storytelling): capture baseline behavior"
```

### Task 2: Scaffold and package the minimal plugin

**Files:**
- Create: `plugins/storytelling/skills/crafting-compelling-stories/`
- Create: `plugins/storytelling/.codex-plugin/plugin.json`
- Create: `plugins/storytelling/.claude-plugin/plugin.json`
- Create: `plugins/storytelling/.cursor-plugin/plugin.json`
- Create: `plugins/storytelling/gemini-extension.json`
- Create: `plugins/storytelling/README.md`
- Create: `plugins/storytelling/CHANGELOG.md`
- Create: `plugins/storytelling/LICENSE`
- Move: `misc/psychology_storytelling_transcript.txt` to `plugins/storytelling/skills/crafting-compelling-stories/references/joanna-wiebe-storytelling-transcript.txt`
- Modify: `plugins/storytelling/tests/test_plugin_contract.py`

- [ ] **Step 1: Initialize the skill with the official scaffold**

Run from the repository worktree:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/init_skill.py crafting-compelling-stories --path plugins/storytelling/skills --resources references --interface 'display_name=Crafting Compelling Stories' --interface 'short_description=Shape vivid stories and narrative copy' --interface 'default_prompt=Use $crafting-compelling-stories to shape this material into an audience-aware story.'
```

Expected: a new skill directory containing `SKILL.md`, `agents/openai.yaml`, and `references/`.

- [ ] **Step 2: Create portable plugin manifests**

Use these canonical values in every adapter:

```json
{
  "name": "storytelling",
  "version": "1.0.0",
  "description": "Audience-aware storytelling and narrative copy grounded in an attributed Joanna Wiebe framework"
}
```

The Codex manifest additionally sets `"license": "MIT"`, `"skills": "./skills/"`, Danny Sung author/repository metadata, keywords `storytelling`, `copywriting`, `marketing`, `narrative`, `speeches`, `fiction`, and `agent-skills`, plus this interface:

```json
{
  "displayName": "Storytelling",
  "shortDescription": "Shape vivid stories and narrative copy",
  "longDescription": "Plan, draft, and edit audience-aware stories across marketing, speeches, education, scripts, and fiction without inventing support.",
  "developerName": "Danny Sung",
  "category": "Writing",
  "capabilities": [
    "Narrative structure selection",
    "Story and marketing copy drafting",
    "Story-focused editing and critique"
  ],
  "defaultPrompt": [
    "Shape this material into an audience-aware story while preserving supplied facts and voice."
  ]
}
```

The Cursor manifest uses `"displayName": "Storytelling"`, category `"writing"`, tags `storytelling`, `copywriting`, and `narrative`, and `"skills": "./skills/"`. Claude uses the canonical identity, MIT license, author name, and keywords. Gemini contains only the canonical identity.

- [ ] **Step 3: Move and attribute the transcript**

Move the user-supplied source from the primary checkout into the worktree destination, then prepend this provenance block without altering the transcript body:

```text
Reference only — not runtime skill instructions.
Framework author and presenter: Joanna Wiebe
Video: The Psychology of Storytelling That Will Change Your Life
Source: https://www.youtube.com/watch?v=oCnxnaVg0bY
Purpose: Archival provenance for the distilled, independently worded skill.

```

Do not represent attribution as a grant of redistribution rights. Keep that release caveat in plugin documentation.

- [ ] **Step 4: Add repository-standard plugin support files**

Copy the repository MIT `LICENSE` from `plugins/swift-testing/LICENSE`. Write `CHANGELOG.md` with a `1.0.0` initial-release entry. Write a concise `README.md` that names `crafting-compelling-stories`, credits Joanna Wiebe and links the video, describes the transcript as archival reference only, notes that redistribution permission should be verified for public distribution, and points to the root installation guide.

- [ ] **Step 5: Run the contract test and keep expected failures focused**

Run:

```bash
python3 -m unittest plugins/storytelling/tests/test_plugin_contract.py -v
```

Expected: packaging and transcript tests PASS; SKILL content and marketplace tests remain FAIL because those later behaviors are not implemented.

- [ ] **Step 6: Keep the RED contract beside the uncommitted scaffold**

Do not commit the scaffold separately while its behavioral contract is still
red. Task 3 completes the same test-first implementation unit and commits the
test with the implementation only after the complete plugin-local contract is
green.

### Task 3: Author the behavioral skill

**Files:**
- Modify: `plugins/storytelling/skills/crafting-compelling-stories/SKILL.md`
- Modify: `plugins/storytelling/skills/crafting-compelling-stories/agents/openai.yaml`
- Modify: `plugins/storytelling/tests/test_plugin_contract.py`

- [ ] **Step 1: Replace scaffold frontmatter and instructions**

Use exactly two frontmatter fields. The trigger description must describe use conditions, not summarize the workflow:

```yaml
---
name: crafting-compelling-stories
description: Use when creating, reshaping, or critiquing narrative-driven marketing copy, founder or product stories, customer stories, case studies, speeches, talks, scripts, educational explanations, fiction, hooks, story openings, narrative arcs, tension, concrete imagery, or endings
---
```

Write the body in imperative form and keep it below 900 words. It must contain these sections and rules:

```markdown
# Crafting Compelling Stories

## Core principle

Match the story to the audience, purpose, medium, and desired response. Use Joanna Wiebe's eight-principle storytelling synthesis as a selection palette, not a checklist.

This skill is informed by Joanna Wiebe's video [The Psychology of Storytelling That Will Change Your Life](https://www.youtube.com/watch?v=oCnxnaVg0bY). The underlying concepts have multiple origins; credit Wiebe for this synthesis. Treat uncited research claims in the source as unverified.

Do not read the archival transcript during ordinary use. Consult it only for a provenance audit explicitly requested by the user.

## Frame the assignment

Extract or safely infer the audience, purpose, medium, desired feeling or action, voice, length, supplied evidence, and constraints. Ask only when a missing fact would materially change the artifact or make truthful completion impossible.

Never invent customer research, testimonials, product capabilities, quantitative outcomes, scientific evidence, urgency, dates, quotations, or lived events. Use a labeled placeholder or request an essential fact.

## Choose one primary structure

| Desired audience experience | Default structure |
|---|---|
| Satisfaction and dramatic rhythm | Save the Cat-inspired beats |
| Urgency and problem awareness | Problem-agitation-solution |
| Transformation and identity change | Hero's journey |
| Compact causal clarity | And-but-therefore |

Scale the structure to the medium. Do not force a cinematic arc into a headline or short message.

## Build selectively

Apply only the principles that serve the assignment:

1. Open a relevant curiosity gap and pay it off honestly.
2. Orient quickly to place, people, tone, and focus.
3. Turn important abstractions into concrete, imaginable language.
4. Follow the selected structure without making it visible or mechanical.
5. Give every emphasized detail a job and resolve the promise it creates.
6. Define the obstacle concretely; do not dehumanize people or manufacture fear.
7. Carry necessary information inside conflict, humor, movement, personality, or example.
8. Return to an opening image, question, or belief with a coherent but non-obvious ending.

## Add conversion mechanics only when relevant

For marketing work, connect the narrative to audience awareness, desired outcome, value proposition, objections, proof, offer, and a proportionate call to action. Keep the antagonist focused on a problem, constraint, failed approach, or harmful system. Never shame the audience. Preserve qualifications and make proof support the claim actually made.

Omit conversion mechanics from fiction, speeches, and personal stories unless requested or naturally relevant.

## Draft and edit

Write in the requested format and voice. Preserve the author's voice during revision unless asked to replace it. Prefer one strong version; offer alternate hooks or endings only when the choice helps.

Assign every line one job: orient, create tension, build desire, supply proof, handle an objection, transition, clarify, resolve, or prompt action. Cut or rewrite a line with no useful job.

## Audit

Confirm that the opening earns attention, orientation arrives quickly, memorable images reinforce the message, open loops pay off, facts and urgency are supported, the ending transforms something planted earlier, and any CTA is clear and proportionate.

Return the deliverable first. Add assumptions, placeholders, or brief rationale only when they help the user act. When critiquing, preserve what works and diagnose the few highest-impact changes before suggesting a rewrite.
```

- [ ] **Step 2: Regenerate Codex UI metadata**

Run:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py plugins/storytelling/skills/crafting-compelling-stories --interface 'display_name=Crafting Compelling Stories' --interface 'short_description=Shape vivid stories and narrative copy' --interface 'default_prompt=Use $crafting-compelling-stories to shape this material into an audience-aware story.'
```

Expected exact `agents/openai.yaml`:

```yaml
interface:
  display_name: "Crafting Compelling Stories"
  short_description: "Shape vivid stories and narrative copy"
  default_prompt: "Use $crafting-compelling-stories to shape this material into an audience-aware story."
```

- [ ] **Step 3: Validate the skill and run focused contracts**

Run:

```bash
python3 /Users/dannys/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/storytelling/skills/crafting-compelling-stories
python3 -m unittest plugins/storytelling/tests/test_plugin_contract.py -v
```

Expected: quick validation PASS and every plugin-local contract test PASS.

- [ ] **Step 4: Commit the behavioral artifact**

```bash
git add plugins/storytelling
git commit -m "feat(storytelling): add audience-aware story workflow"
```

### Task 4: Publish repository metadata and installation guidance

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `.cursor-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `plugins/storytelling/tests/test_plugin_contract.py`

- [ ] **Step 1: Extend the contract test for repository integration and verify RED**

Add tests requiring exactly one canonical `storytelling` entry in each root
marketplace, a root plugin-table row, a `crafting-compelling-stories` overview,
all three installation commands below, and a nearby Joanna Wiebe/source-video
credit. Run:

```bash
python3 -m unittest plugins/storytelling/tests/test_plugin_contract.py -v
```

Expected: the new repository-integration tests FAIL while existing
plugin-local tests remain PASS.

- [ ] **Step 2: Add one canonical marketplace entry to each adapter**

Add this Codex marketplace entry:

```json
{
  "name": "storytelling",
  "source": {"source": "local", "path": "./plugins/storytelling"},
  "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
  "category": "Writing"
}
```

Add a Claude entry using source `./plugins/storytelling`, version `1.0.0`, the canonical description, category `writing`, the canonical keywords, and tags `storytelling`, `copywriting`, `narrative`. Add a Cursor entry using source `plugins/storytelling` and the canonical description only.

- [ ] **Step 3: Add root documentation and installation commands**

Add `storytelling` and `crafting-compelling-stories` to the plugin summary and skills sections. Add installation sections using:

```bash
claude plugin install storytelling@danny-sung-agent-skills
codex plugin add storytelling@danny-sung-agent-skills
npx skills add dannys42/agent-skills --skill crafting-compelling-stories --global --agent <agent>
```

Credit Joanna Wiebe and link the source video near the skill overview. State that the archived transcript is provenance, not runtime instructions or independently validated science.

- [ ] **Step 4: Run contract and whole-repository focused tests**

Run:

```bash
python3 -m unittest plugins/storytelling/tests/test_plugin_contract.py -v
python3 -m unittest discover -s plugins/skill-development-optimizer/tests -p 'test_*.py'
python3 -m unittest discover -s plugins/swift-code-organization/tests -p 'test_*.py'
python3 -m unittest discover -s plugins/swift-design-patterns/tests -p 'test_*.py'
```

Expected: all storytelling contracts PASS; existing suites remain at the clean baseline (250 passing with 1 skipped, 24 passing, 91 passing). The design-pattern suite may require permission to bind its temporary localhost socket.

- [ ] **Step 5: Commit marketplace and documentation integration**

```bash
git add .agents/plugins/marketplace.json .claude-plugin/marketplace.json .cursor-plugin/marketplace.json README.md plugins/storytelling
git commit -m "docs(storytelling): publish plugin installation metadata"
```

### Task 5: Configure full-profile validation and freeze the artifact

**Files:**
- Create: `plugins/storytelling/skill-optimizer.json`
- Create: `plugins/storytelling/tests/artifact.json`
- Create: `plugins/storytelling/tests/validation-results.json`

- [ ] **Step 1: Add the optimizer configuration**

Write a schema-version-1 configuration with target `plugins/storytelling/skills/crafting-compelling-stories`. Include `SKILL.md`, `agents/**/*.yaml`, and `references/**/*.txt`; exclude Python cache files. Define one `storytelling-contracts` command:

```json
{
  "argv": ["python3", "-m", "unittest", "plugins/storytelling/tests/test_plugin_contract.py", "-v"],
  "cwd": ".",
  "timeout_seconds": 120,
  "max_output_bytes": 1048576,
  "network": false,
  "timing_kind": "work"
}
```

Assign that command to `quick`, `content`, `behavior`, and `full`; include an
empty `importer` command list because the optimizer schema requires all five
profile keys and this plugin has no acquisition or managed storage. Point
evaluations to the case and rubric JSON files.

- [ ] **Step 2: Inspect and classify before selecting the profile**

Run:

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/inspect_skill.py plugins/storytelling/skill-optimizer.json --json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/classify_change.py plugins/storytelling/skill-optimizer.json --base af91e55 --json
```

Expected: inspection identifies a configured skill and evaluation corpus; classification selects `full` because this is a new plugin with packaging, content, and behavior changes.

- [ ] **Step 3: Run deterministic full validation**

State the stopping criteria before running: stop on any missing command, failed contract, attribution failure, unknown changed path, or newly introduced importer behavior.

Run:

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/run_validation.py plugins/storytelling/skill-optimizer.json full --output plugins/storytelling/tests/validation-results.json
```

Expected: PASS with `storytelling-contracts` recorded and no network check.

- [ ] **Step 4: Hash the byte-identical distributable**

Run:

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/hash_artifact.py plugins/storytelling/skill-optimizer.json --json --output plugins/storytelling/tests/artifact.json
```

Expected: `sha256-length-framed-v1` artifact identity listing the skill, UI metadata, and transcript reference.

- [ ] **Step 5: Commit configuration and deterministic evidence before forward evaluation**

```bash
git add plugins/storytelling/skill-optimizer.json plugins/storytelling/tests/artifact.json plugins/storytelling/tests/validation-results.json
git commit -m "test(storytelling): freeze validated artifact"
```

Do not edit any distributable file after this commit. If one changes, mark the cohort historical, rerun deterministic validation, regenerate the artifact, and restart every headline case.

### Task 6: Run the frozen forward cohort and final verification

**Files:**
- Create: `plugins/storytelling/tests/evaluation-evidence.json`
- Create temporarily: `/tmp/storytelling-evaluation-completion.json`

- [ ] **Step 1: Initialize one headline cohort**

Run:

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py init plugins/storytelling/tests/artifact.json plugins/storytelling/tests/evaluation-cases.json plugins/storytelling/tests/evaluation-rubric.json plugins/storytelling/tests/evaluation-evidence.json --cohort final
```

Expected: eight pending runs tied to the frozen artifact hash.

- [ ] **Step 2: Run each case in a fresh agent with only the frozen skill and prompt**

Use one fresh agent per case. Present it as an ordinary user task: `Use $crafting-compelling-stories at plugins/storytelling/skills/crafting-compelling-stories to solve: <exact case prompt>`. Do not reveal the rubric, baselines, intended answers, or suspected failures.

Capture the verbatim response and agent-reported files read. Score every Boolean rubric key against the declared case intent. A negative-trigger case passes `appropriate_triggering` only when it obeys the requested plain edit without injecting narrative technique.

- [ ] **Step 3: Complete, verify, and summarize the cohort**

Create schema-version-1 completion JSON in `/tmp/storytelling-evaluation-completion.json` with cohort `final`, exactly one run per case, and exactly the declared rubric keys. Then run:

```bash
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py complete plugins/storytelling/tests/evaluation-evidence.json plugins/storytelling/tests/evaluation-cases.json plugins/storytelling/tests/evaluation-rubric.json /tmp/storytelling-evaluation-completion.json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py verify plugins/storytelling/tests/evaluation-evidence.json plugins/storytelling/tests/evaluation-cases.json plugins/storytelling/tests/evaluation-rubric.json --json
python3 plugins/skill-development-optimizer/skills/optimizing-skill-development/scripts/manage_evidence.py summarize plugins/storytelling/tests/evaluation-evidence.json plugins/storytelling/tests/evaluation-cases.json plugins/storytelling/tests/evaluation-rubric.json --json
```

Expected: verification reports one complete, hash-consistent headline cohort. Stop rather than claim success if any run is missing, an artifact hash differs, or a rubric key is absent.

- [ ] **Step 4: Re-run the frozen hash and final checks**

Regenerate an artifact JSON to `/tmp/storytelling-final-artifact.json` and compare it byte-for-byte with `plugins/storytelling/tests/artifact.json`. Run `quick_validate.py`, storytelling contracts, all three existing plugin suites, `git diff --check`, and `git status --short`.

Expected: identical artifact identity; all tests at or above baseline; no whitespace errors; only intended evidence changes present.

- [ ] **Step 5: Commit verified behavioral evidence**

```bash
git add plugins/storytelling/tests/evaluation-evidence.json
git commit -m "test(storytelling): verify frozen behavior cohort"
```

- [ ] **Step 6: Review the completed branch**

Use `requesting-code-review` for a focused review of trigger precision, fabrication safeguards, attribution, transcript runtime isolation, marketplace consistency, and evidence/hash integrity. Resolve important findings, rerun any invalidated checks, and use `verification-before-completion` before claiming completion.

Report the selected full profile, risk reasons, commands run and skipped, artifact hash, cohort status, test totals, duration evidence if recorded, and the next escalation condition. State that importer/network checks were not applicable, not passed.
