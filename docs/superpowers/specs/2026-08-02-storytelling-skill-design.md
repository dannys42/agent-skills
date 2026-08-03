# Storytelling Skill Design

**Date:** 2026-08-02

## Goal

Create a portable storytelling plugin that helps an agent plan, draft, and edit
compelling narratives across marketing copy, speeches, founder and product
stories, educational material, scripts, and fiction.

Use Joanna Wiebe's eight-principle psychology-of-storytelling framework as the
core source. Adapt the framework to the audience, medium, and communication
goal instead of forcing every principle into every output.

## Plugin Architecture

Create a standalone `storytelling` plugin containing one discoverable
`crafting-compelling-stories` skill. Match the repository's portable plugin and
marketplace adapter shapes for Codex, Claude Code, Cursor, Gemini CLI, and
compatible skill-directory hosts.

Use this structure:

```text
plugins/storytelling/
├── .codex-plugin/
├── .claude-plugin/
├── .cursor-plugin/
├── gemini-extension.json
├── skills/
│   └── crafting-compelling-stories/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       └── references/
│           └── joanna-wiebe-storytelling-transcript.txt
└── tests/
```

Add concise plugin installation documentation and update repository marketplace
metadata using existing conventions. Do not create scripts or output assets;
the skill controls judgment and writing rather than a deterministic file
transformation.

## Trigger Scope

Trigger when a user asks to create, reshape, or edit storytelling or
narrative-driven copy, including:

- marketing and conversion copy;
- founder, customer, brand, case-study, and product stories;
- speeches, talks, presentations, educational explanations, and scripts;
- fiction and other narrative prose;
- hooks, story openings, narrative arcs, tension, concrete imagery, and
  satisfying endings.

Do not trigger for ordinary factual prose, code, literal transcription,
grammar-only correction, or copy that has no narrative purpose unless the user
also asks to introduce or evaluate storytelling.

## Source and Attribution

Move `misc/psychology_storytelling_transcript.txt` to
`references/joanna-wiebe-storytelling-transcript.txt` inside the skill. Add a
plain provenance header that identifies:

- Joanna Wiebe as the framework's author and presenter;
- the original video, *The Psychology of Storytelling That Will Change Your
  Life*;
- <https://www.youtube.com/watch?v=oCnxnaVg0bY> as the source URL;
- the transcript's reference-only purpose.

Keep the transcript only as provenance and human reference. Instruct the agent
not to load or quote it during ordinary skill use. Distill the reusable ideas
into original, concise skill instructions and attribute the framework in
`SKILL.md` and plugin documentation.

Attribution does not itself establish redistribution permission. Preserve the
source and authorship notice, avoid representing the transcript as original
repository content, and flag licensing verification as a release consideration
if this full transcript will be redistributed publicly.

Do not repeat the transcript's uncited numerical research claims as established
facts. Present the eight principles as Wiebe's practical framework unless an
independent source has been verified.

## Operating Workflow

### 1. Frame the assignment

Extract the audience, purpose, medium, desired feeling or action, voice, length,
available evidence, and constraints from the request and supplied material.
Infer low-risk omissions and state consequential assumptions briefly. Ask a
question only when a missing answer would materially change the result or make
truthful completion impossible.

Never invent customer research, testimonials, product capabilities,
quantitative outcomes, scientific evidence, urgency, or biographical events.
Use clearly marked placeholders or request the missing facts when they are
essential.

### 2. Select the narrative structure

Choose one primary structure based on the intended audience experience:

| Intended effect | Default structure |
|---|---|
| Satisfaction and dramatic rhythm | Save the Cat-inspired beats |
| Urgency and problem awareness | Problem-agitation-solution |
| Transformation and identity change | Hero's journey |
| Causal clarity and compact momentum | And-but-therefore |

Adapt the structure to the medium. Do not force a long cinematic arc into a
headline, short advertisement, or brief product message.

### 3. Build the story

Apply only the relevant principles from Wiebe's framework:

1. Open a curiosity gap that is intriguing but honestly paid off.
2. Orient the audience quickly to place, people, tone, and focus.
3. Replace important abstractions with concrete, imaginable language.
4. Follow a recognizable structure suited to the intended response.
5. Make every emphasized detail earn its place and resolve its promise.
6. Define the obstacle or antagonist concretely without dehumanizing people or
   manufacturing fear.
7. Package necessary information inside attention-holding conflict, humor,
   movement, personality, or example.
8. Return to an opening image, question, or belief with a coherent but not
   mechanical ending.

Treat these principles as a selection palette, not a mandatory checklist for
every draft.

### 4. Add the marketing layer when applicable

For conversion-oriented work, connect the narrative to the audience's stage of
awareness, desired outcome, value proposition, objections, proof, offer, and
call to action. Let the story clarify the value rather than delaying or hiding
it.

Keep the villain focused on a problem, constraint, failed approach, or harmful
system. Do not shame the audience or attack a protected or identifiable group.
Use proof proportionate to the claim and preserve required qualifications.

Omit conversion mechanics from fiction, speeches, and personal stories unless
the request makes them relevant.

### 5. Draft for the medium

Produce the requested artifact in its expected shape and voice. Preserve the
author's voice during edits unless the user asks for a new one. Prefer one
strong version; offer a small set of alternate hooks or endings only when the
choice would be useful.

Do not bury the deliverable beneath a tutorial about the framework. Explain
craft decisions only when requested or when concise rationale helps the user
choose between meaningful alternatives.

### 6. Run the story audit

Before returning the work, verify:

- the opening creates relevant curiosity rather than empty sensationalism;
- the audience can orient quickly;
- the most memorable images reinforce the intended message;
- the structure matches the medium and goal;
- every emphasized detail has a named job;
- every opened loop is paid off or intentionally left open;
- the obstacle is specific, truthful, and ethically framed;
- facts, proof, urgency, and outcomes are supported or marked as placeholders;
- the ending resolves or transforms something planted earlier;
- marketing copy has a clear, proportionate next action.

Name a line's job as one of: orient, create tension, build desire, supply proof,
handle an objection, transition, clarify, resolve, or prompt action. Cut or
rewrite lines with no useful job.

## Output Behavior

Default to returning:

1. the finished or revised story/copy;
2. a short assumptions or placeholders note only when needed;
3. optional alternatives only where the user faces a meaningful choice.

When asked to critique rather than rewrite, diagnose the highest-impact issues
against the story audit, preserve what already works, and recommend focused
changes. Do not silently replace the user's voice or factual position.

## Validation Strategy

This is a new plugin with content and behavioral risk, so use the
`optimizing-skill-development` full profile. Apply `writing-skills` test-first
validation and freeze the final distributable artifact before headline forward
testing.

### Baseline cases

Run fresh agents without the skill on representative prompts and record the
verbatim responses, files read, and recurring failures. Include:

- a SaaS landing-page story with supplied customer evidence;
- a founder story assembled from rough factual notes;
- a short speech opening;
- a fictional scene with an abstract, slow opening;
- an incomplete marketing brief that tempts fabrication;
- an editing request that requires preserving voice while removing purposeless
  details.

Expected baseline risks include forcing a single formula across formats,
inventing unsupported proof, using sensational hooks without payoff, leaving
the audience unoriented, over-explaining the method, and flattening the source
voice.

### Forward cases

Run the same cases against the frozen skill, plus negative-trigger cases for
grammar-only editing and ordinary factual prose. Give each fresh agent only its
case prompt and the frozen skill. Do not disclose expected answers, baseline
results, diagnoses, or prior outputs.

Declare and score a rubric covering:

- appropriate triggering;
- audience, purpose, medium, and constraint handling;
- structure selection and adaptation;
- relevant use rather than forced use of Wiebe's principles;
- concrete language, orientation, purposeful details, payoff, and ending;
- preservation of supplied voice and facts;
- refusal to fabricate evidence, urgency, or outcomes;
- ethical marketing framing and a proportionate call to action;
- deliverable-first output without unnecessary framework exposition.

Any distributable change invalidates the behavioral cohort and requires a new
headline run.

### Deterministic and content checks

Validate:

- skill frontmatter and `agents/openai.yaml` metadata;
- Codex, Claude Code, Cursor, Gemini, and marketplace manifests;
- consistent plugin names, versions, paths, descriptions, and source links;
- transcript relocation and provenance header;
- attribution to Joanna Wiebe and the original video;
- original wording in the operational guidance;
- negative-trigger and content-contract fixtures;
- repository-focused tests declared by the full validation profile.

No importer checks apply because the plugin performs no fetching, caching,
network acquisition, or managed evidence publication of its own. Record those
threats as not applicable rather than passing.

## Success Criteria

- The skill triggers reliably for storytelling and narrative-copy work without
  capturing unrelated writing tasks.
- Outputs adapt to marketing, speech, educational, and fictional contexts.
- The agent selects relevant techniques instead of mechanically applying all
  eight principles.
- Hooks, concrete imagery, open loops, antagonists, and endings support the
  communication goal and remain truthful.
- Incomplete briefs never produce fabricated claims, evidence, urgency,
  testimonials, product features, or lived events.
- The delivered artifact remains primary and preserves requested voice and
  format.
- Joanna Wiebe and the source video are clearly credited, while unsupported
  scientific claims are not elevated into facts.
- Packaging, content, and the frozen behavioral cohort all pass the configured
  full-profile checks for one byte-identical distributable artifact.
