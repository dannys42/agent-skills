# Documentation templates

Starting content for the three standard files when they don't exist yet.
Replace bracketed text; don't leave placeholders in the committed file, and
don't pre-populate sections you have no real content for — an absent section
is better than a guessed one.

## Overview.md

```markdown
# Overview

_Last updated: <date>_

## Objectives

[What this project is for. Prefer the maintainer's own words — a README
tagline, a CLAUDE.md statement of purpose — over a paraphrase. If this is
inferred rather than stated by the user, say so explicitly and invite
correction rather than presenting it as settled.]

## Direction

[Where this is headed next, if that's actually known from an existing
roadmap, issue, or explicit statement. Leave this section out entirely
rather than guessing when nothing is known.]
```

## Structure.md

```markdown
# Structure

One entry per target. Add entries as they come up during retrospection;
don't pre-populate the whole project on the first run — an entry earns its
place when a task actually had to rediscover it.

## <target name>
- Directory: `<path>`
- Purpose: <one or two sentences>
```

## TODO-TokenEfficiency.md

```markdown
# Token-Efficiency Backlog

Recommendations from `/audit-token-efficiency` runs. Check an item off
only once it's actually done; move fully-completed sections to
`Completed/TODO-TokenEfficiency.md`.
```
