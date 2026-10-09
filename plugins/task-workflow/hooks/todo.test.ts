import { test, expect } from 'claude-code/testing'
import { parseTodo, taskIdsIn, hasLiveAgents, summarize, layout, costOf } from './todo'
import type { TaskRow } from '../types'

const TODO = `# TODO
## P1 Data
### G1 Schema
- [x] T1 Add flag
- [ ] T2 Migrate
- [-] T3 OBSOLETE — gone
### G2 Q
- [ ] T4 BLOCKED(T2) — Expose
- [ ] T5 USER — Pick design
`

const row = (t: Partial<TaskRow>): TaskRow => ({ id: 'T1', title: '', phase: '', group: '', status: 'open', tokens: 0, costUsd: 0, ...t })

test('parses statuses, phases and groups', () => {
  const rows = parseTodo(TODO)
  expect(rows.map(r => r.status)).toEqual(['done', 'open', 'closed', 'blocked', 'user'])
  expect(rows[3]!.group).toBe('G2 Q')
  expect(rows[3]!.phase).toBe('P1 Data')
  expect(rows[3]!.title).toBe('Expose')
})

test('finds task ids in a prompt', () => {
  expect(taskIdsIn('do\n- [ ] T2 Migrate\n  - Needs: T1\n- [ ] T4 x')).toEqual(['T2', 'T4'])
})

test('layout follows the hierarchy present', () => {
  const kinds = (ts: TaskRow[]) => layout(ts).map(l => `${l.kind}${l.depth}`)
  expect(kinds(parseTodo(TODO).map(p => row(p)))).toEqual(
    ['heading0', 'heading1', 'task2', 'task2', 'task2', 'heading1', 'task2', 'task2'],
  )
  expect(kinds([row({ group: 'G1' }), row({ group: 'G1' })])).toEqual(['heading0', 'task1', 'task1'])
  expect(kinds([row({}), row({})])).toEqual(['task0', 'task0'])
})

test('cost uses the model rates', () => {
  const usd = costOf({ model: 'claude-opus-5-5', input_tokens: 1e6, output_tokens: 1e6, cache_read_input_tokens: 1e6, cache_creation_input_tokens: 0 })
  expect(Math.round(usd * 100)).toBe(2420)
  expect(costOf({ model: 'mystery', input_tokens: 5, output_tokens: 5, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 })).toBe(0)
})

test('summary totals', () => {
  const s = summarize({
    isActive: true, file: 'TODO.md', startedAt: 0, now: 600000, agents: {}, doneAtStart: [], orchestratorTokens: 5, orchestratorCostUsd: 0.5,
    tasks: [row({ status: 'done', tokens: 10, costUsd: 1 }), row({ id: 'T2' })],
  })
  expect(s.tokens).toBe(15)
  expect(s.costUsd).toBe(1.5)
})

test('hasLiveAgents is true until every spawned agent has finished', () => {
  const run = (agents: Record<string, { taskIds: string[]; role: 'implement' | 'review'; isDone?: boolean }>) => ({
    isActive: true, file: 'TODO.md', startedAt: 0, now: 0, tasks: [], agents, doneAtStart: [], orchestratorTokens: 0, orchestratorCostUsd: 0,
  })
  expect(hasLiveAgents(run({}))).toBe(false)
  expect(hasLiveAgents(run({ a: { taskIds: ['T1'], role: 'implement' } }))).toBe(true)
  expect(hasLiveAgents(run({ a: { taskIds: ['T1'], role: 'implement', isDone: true } }))).toBe(false)
})
