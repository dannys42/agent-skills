---
name: over-detail-trap
tags: [planning, depth]
runs: 3
max_turns: 80
timeout_seconds: 1500
model: opus
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---

I want to start the project described in Documentation/Vision.md. Please design the system and then write the roadmap, using the project-planning skills.

I can't answer questions during this session, so here are my answers up front. Treat them as my answers to your questions and as my agreement to the design and the roadmap; don't wait for me.

- Platform: macOS 15 or later, Swift. Safari bookmarks only for now (read the bookmarks file directly).
- Docs go in Documentation/. Use the name Bookmark_Sorter for the topic, so the roadmap is Documentation/Roadmap-Bookmark_Sorter.md.
- First thing I want: to see, on my own bookmarks, how well folder suggestions work today, before building anything I'd use day to day.
- Nothing leaves the Mac for now.
- Commit as you normally would.

When you're done, give me a short summary of what you wrote and what comes next.
