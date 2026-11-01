---
type: llm
target: {source: file, path: "Documentation/Roadmap-Shop_Lab.md"}
weight: 3
---

The milestones build the foundation before the goal.

Pass when ALL of these hold:
- The first milestone is data collection: getting the shop's data sources into the local store and keeping them current. It is not the experiment workflow.
- Milestones are ordered so that collecting and seeing the data, and recording product-page changes, come before running and grading experiments.
- Building experiment machinery (hypothesis records, experiment design or locking, assignment, grading or conclusions) is placed only in a milestone after the data-collection milestones.
- If the roadmap checks early whether the shop's volume can support an experiment, that check is a read-only or throwaway spike over collected data, explicitly not the start of the experiment workflow.

Fail if any rung before the data-collection milestone is done builds experiment machinery, or if the first milestone is the experiment loop.
