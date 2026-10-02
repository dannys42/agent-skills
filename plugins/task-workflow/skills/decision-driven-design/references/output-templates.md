# Output Templates

## Decision ledger file

Path: `<DocDir>/Decision-<Topic>.md` (see SKILL.md, “Record and reconcile”).

~~~markdown
# Decision Ledger — <design title>

Status: in progress | complete
Scope: <current scope in one line>
Future direction: <known direction and any preserved seams>

```yaml
DNN:
  topic: <decision>
  status: proposed | accepted | superseded | deferred | evidence-required
  choice: <selected direction>
  rationale: <short reason>
  consequences: [<downstream effect>]
  revisit_when: [<condition>]
  superseded_by: <DNN, only when superseded>
```
~~~

## Implementation task

```markdown
# Task NN — <outcome-oriented title>
## Outcome
## Dependencies and context
## Approved decisions
## Scope
## Ordered implementation steps
## Verification
## Non-goals
## Acceptance criteria
```

## Process retrospective

```markdown
## Process improvements
- Skill improvement: <friction>; generalized lesson; exact section to update; why it may recur.
- Project-rule candidate: <durable invariant and affected rule scope>, if warranted.
- User-rule candidate: <cross-project preference>, only if recurring or explicitly requested.
```

Omit categories without a material, evidence-backed candidate. Omit the whole section when no category has one.
