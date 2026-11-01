---
name: foundation-before-goal
tags: [planning, order]
runs: 3
max_turns: 80
timeout_seconds: 1500
model: opus
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---

I want to start the project described in Documentation/Goal.md. Please design the system and then write the roadmap, using the project-planning skills.

I can't answer questions during this session, so here are my answers up front. Treat them as my answers to your questions and as my agreement to the design and the roadmap; don't wait for me.

- Platform: a Swift command-line tool and a local server on my Mac, with SQLite. A Mac app later.
- Docs go in Documentation/. Use the name Shop_Lab for the topic, so the roadmap is Documentation/Roadmap-Shop_Lab.md.
- The experiments are why I want this. Volume is what it is; I can't change it.
- API keys live in the Keychain.
- Commit as you normally would.

When you're done, give me a short summary of what you wrote and what comes next.
