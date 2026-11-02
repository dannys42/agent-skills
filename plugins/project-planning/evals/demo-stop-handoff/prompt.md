---
name: demo-stop-handoff
tags: [handoff, resume]
runs: 3
max_turns: 60
timeout_seconds: 1200
model: opus
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---

Every rung of milestone M1 (count words) in Documentation/Roadmap-Word_Count.md is done. Please close the milestone with the roadmap-plan-next-rung skill.

I can't answer questions during this session. Skip the tidy. When you reach the point where you need my ruling on the demo, stop there and leave things so that a new session tomorrow, with none of today's conversation, can pick up where you stopped once I answer. Commit as you normally would.
