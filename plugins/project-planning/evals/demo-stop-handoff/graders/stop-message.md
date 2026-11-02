---
type: llm
weight: 2
---

The stop message to the owner is short and self-contained.

Pass when ALL of these hold:
- The final message says what was done and asks for the demo ruling (accept, accept with follow-ups, or reject) without needing any file opened.
- It ends with `Next: /rung (Opus: /model opus)`.
- It shows no per-kind resume command (such as `/roadmap-plan-next-rung milestone-close M1`) and no bare IDs: M1 appears with its name at first mention.
