# Retrospective

Shared by `roadmap-plan-next-rung` (`retro [L3]`, and offered at the end of fold-back) and `system-design` (offered after sign-off, and `retro` any time). Its purpose is to tell the maintainer of these skills whether the design stayed thin enough while staying accurate, with evidence a clean agent can act on later.

Build it from the project's actual docs and history, not from memory. Apply nothing; the user decides what to do with it.

## Gather the evidence

- **Rung retro:** the brief, every design doc it lists as touched, the rung's tasklist (in `<DocDir>/` or `<DocDir>/Completed/`), and the rung's commits (`git log --oneline` over the rung's period, and `git log -- <DocDir>/SystemDesign` for doc changes).
- **System-design retro:** the Overview (and any subsystem doc written this session) and its git history.
- **Sizes:** lines before and after for each touched design doc (`git show <rev>:<path> | wc -l` against `wc -l <path>`).
- **Questions:** count the questions asked and how many answers changed the draft versus confirmed a default. From the same session this is `observed`; in a later session, infer it from assumption and decision rows (`confirmed` versus replaced) and mark it so.
- **Rework:** in the tasklist, items with `Found during`, `[-] INVALID`, or `SUPERSEDED`, and tasks whose `Model` was raised.

## Part 1: Summary

A few lines, each with its evidence:

- Was the brief (or the Overview) right-sized: too heavy (sections nobody used, detail the rung did not need) or too thin (gaps the tasks had to fill)?
- Questions asked; answers that changed the draft versus confirmed a default.
- Assumptions overturned at fold-back or during iteration.
- Drift found between the brief and the code, and which side was fixed.
- Tasks that needed rework or got `Found during` additions because the brief missed something.
- Docs created or touched; any subsystem promotion, and whether it met a warrant trigger.
- Diagram problems (render errors, wrong level, labels that did not match component names).
- Missing-sibling-skill notices hit, and what fallback was used.
- Whether the Overview grew unusually (lines before and after; about a page is the target).

## Part 2: Feedback prompt

One fenced block, self-contained and project-neutral by default: no project names, file paths, or code unless the user asks. Read skill versions from the plugin manifest (`../../.claude-plugin/plugin.json` relative to each skill's folder); if it is absent, write "version unknown (standalone install)".

```text
project-planning retrospective feedback
Skills: <skill> <version> (<plugin>); <other skills used, with versions>
Context: <rung retro | system-design retro>; <project kind, e.g. "macOS document app">; <new | adopted>
Evidence (tier per point: measured = counted from docs or git, observed = seen in this session, guess):
- [measured] ...
- [observed] ...
- [guess] ...
Keep (went well):
- ...
Suggested edits (skill, section, change, why; aim: thinner design, same accuracy):
- ...
In danny-agent-skills, run /roadmap-feedback and paste this block.
```

If nothing stands out (brief right-sized, few changed answers, no drift, no rework), say so in one line and skip the prompt. Keep each section short.

Offer to save the retrospective to the scratchpad or a path the user names. Do not write it into the project's design docs by default; they describe the system, not the process.
