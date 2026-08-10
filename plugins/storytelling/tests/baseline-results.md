# Storytelling Baseline Results

These six runs used separately spawned fresh agents that did not load a
storytelling skill. Each agent received only the exact case prompt below: no
framework, rubric, expected result, or other case-specific context. The agents
did not report reading any files; no files are named in their responses.

## Recurring failure patterns

- **Supplied-fact drift:** The founder-story response adds habitual pre-sunrise
  work, dough, ovens, and broader order patterns. The fiction response assigns
  the letter to Mara's brother and adds a particular room history. Those
  invented details make prose vivid but breach source-grounding constraints.
- **Persuasion from an empty brief:** The incomplete marketing brief invents
  product behavior (using ingredients, schedules, and tastes), benefits, and
  a call to action before noting that the supporting information is missing.
  This is a meaningful gap: the required restraint is not reliably
  self-triggered under a request for urgency.
- **Constraint precision is not explicit:** The speech opening is a strong
  audience-aware opening, but it does not show timing calibration; the fiction
  response also treats the requested 180-word target as approximate. A skill
  should make goal, medium, and constraints deliberate before drafting.

## saas-landing-page

### Exact prompt

```text
Write the narrative opening and CTA for a landing page for Briefly, a meeting-summary tool. Audience: engineering managers. Supplied facts only: it turns an uploaded transcript into a summary; Acme's pilot reduced its weekly recap-writing time from 90 minutes to 25 minutes; Acme approved use of its name. Do not add product capabilities or results.
```

### Verbatim response

**Turn uploaded transcripts into clear summaries.**

Engineering management already has enough to recap. Briefly turns an uploaded transcript into a summary, so the next update can start from a concise record of the meeting.

In Acme’s pilot, weekly recap-writing time fell from 90 minutes to 25 minutes. Acme approved use of its name.

**CTA:** Upload a transcript

*Get a summary from the meeting record.*

### Agent-reported files read

No files reported.

## founder-story

### Exact prompt

```text
Turn these notes into a 250-word founder story: Mina ran a neighborhood bakery; a freezer failed at 4:40 a.m. before a wedding order; handwritten inventory made it hard to see what could be remade; she later built a simple batch tracker with her brother. Do not invent quotations, dates, customers, or outcomes.
```

### Verbatim response

Mina learned the rhythms of running a neighborhood bakery, where every day began before sunrise and every batch depended on timing. Dough had to rise, ovens had to hold steady, and orders had to be ready when people needed them. Most days, routines carried the bakery forward.

Then, at 4:40 a.m. one morning, a freezer failed ahead of a wedding order. It was more than a technical problem. It immediately turned inventory into a question: what ingredients and prepared items were available, what had been lost, and what could still be remade in time?

At the bakery, that information lived in handwritten inventory records. Those notes could capture what had been counted, but they were not built for a fast situation. Faced with the freezer failure, Mina could see how difficult it was to turn scattered handwritten information into a clear picture of the bakery’s next steps.

That experience shaped what came later. Rather than beginning with an abstract idea for software, Mina started with a problem she knew from the inside: keeping track of batches when the work was moving quickly. She and her brother built a simple batch tracker around that need.

The tracker grew from a bakery floor, not from a distant plan. Its starting point was straightforward: make it easier to see what was in progress, what had been recorded, and what still needed attention. For Mina, the work was grounded in the memory of a pre-dawn freezer failure and the pressure of deciding what to do next.

### Agent-reported files read

No files reported.

## speech-opening

### Exact prompt

```text
Write a 90-second opening for a talk to first-time managers about giving useful feedback. Desired feeling: recognized, then hopeful. Avoid sales language.
```

### Verbatim response

When you become a manager, feedback can suddenly feel heavier than it did before.

You notice the pause before you say, “Can I share something?” You replay conversations afterward. You worry about being too direct, too vague, too late—or about making someone feel smaller when you genuinely want to help them grow.

If that sounds familiar, it doesn’t mean you’re bad at feedback. It means you understand that your words now carry more weight.

The good news is that useful feedback does not require a perfect script or a forceful personality. It starts with paying close attention: naming what you saw, explaining why it mattered, and making space for the other person’s view. The goal isn’t to win a point or deliver a verdict. It’s to help someone see their work more clearly and leave the conversation knowing what to do next.

That can be a relief—for them and for you.

Today, we’ll focus on feedback that is specific, timely, and grounded in respect: feedback that helps people improve without losing trust.

### Agent-reported files read

No files reported.

## fiction-scene

### Exact prompt

```text
Rewrite this slow opening as a vivid 180-word scene while preserving third-person limited voice and the fact that Mara is avoiding a letter: 'Mara was nervous. The room was old and unpleasant. There was a letter on the table that she did not want to read.'
```

### Verbatim response

Mara stood in the doorway with one hand still on the brass knob, listening to the house breathe around her. The parlor smelled of wet plaster and dead roses; rain ticked through a crack in the window frame and darkened the warped boards beneath her boots. On the table, between a silver candlestick crusted with wax and a bowl of blackened apples, lay the envelope. Its cream paper looked indecently clean in the room's mildew and shadows. Her name crossed it in her brother's slanted hand.

She did not step closer. Instead, Mara rubbed her thumb over the knob until the metal warmed beneath her skin. The seal was unbroken. That mattered. So long as it remained whole, whatever waited inside had not happened yet. A floorboard sighed behind her. Mara flinched, then laughed once, softly, as if the house had told a joke. Still she watched the letter, willing the rain to rise, the walls to collapse, anyone to call her away. But the parlor held its breath, and the envelope waited, patient as a wound beneath the bandage.

### Agent-reported files read

No files reported.

## incomplete-marketing-brief

### Exact prompt

```text
Write launch copy for a new meal-planning app. I have not supplied its features, audience research, testimonials, price, results, or launch date. Make it persuasive and urgent.
```

### Verbatim response

**Meet [App Name] — meal planning that fits real life.**

Stop staring into the fridge and wondering what’s for dinner. With [App Name], you can turn everyday ingredients, busy schedules, and changing tastes into a meal plan you’ll actually want to follow.

Plan with less stress. Shop with more confidence. Make dinnertime easier—starting today.

**[Get early access / Join the waitlist / Download now]**

To make this genuinely persuasive and urgent, we’ll need the audience, core features, launch timing, pricing, and any proof points. Until then, avoid inventing scarcity, results, or testimonials.

### Agent-reported files read

No files reported.

## preserve-voice-edit

### Exact prompt

```text
Tighten this copy without changing its dry, understated voice: 'At 2:13 on Tuesday, the dashboard went red. This was inconvenient. We had, after all, promised the board that red dashboards were now mostly a historical artifact. The office ficus remained neutral. Our incident log did not.' Remove details that do not earn a place, but preserve any detail that establishes tone or pays off.
```

### Verbatim response

“At 2:13 Tuesday, the dashboard went red. Inconvenient: we’d promised the board red dashboards were mostly historical artifacts. The office ficus stayed neutral. Our incident log did not.”

### Agent-reported files read

No files reported.
