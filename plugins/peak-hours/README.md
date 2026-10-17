# peak-hours

A Claude Code mod (hooks module, not a skill bundle). During the assumed peak
window, 5-11am US Pacific on weekdays (PST or PDT as observed), it draws a
right-aligned `🔴 PEAK · ends in 2h 15m` badge above the prompt. Off-peak it
draws nothing.

It never calls the model and adds nothing to the prompt, so it consumes no
tokens. CPU is one clock check a minute.

## Learning the real window

Anthropic documents no official peak window, so the mod records how fast the
5-hour rate-limit window fills per weighted token, binned by Pacific hour
(48 fixed bins, a few KB in the mod's `$.store`, capped at 16 KB). When at least
two bins confidently contradict the assumed window (20+ observations over 3+
days, 3 standard errors), the badge turns into `🟠 PEAK? data disagrees`.
`/peak-report` prints the bins. Usage from other sessions on the same account
adds noise.

## Install

```
/plugin install peak-hours --marketplace dannys42/agent-skills
```

Change the window in `START_HOUR` and `END_HOUR` in `hooks/peak.ts`.
