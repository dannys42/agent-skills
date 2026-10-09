import type { TaskRow, TaskStatus, TasklistRun } from '../types'

type Parsed = Pick<TaskRow, 'id' | 'title' | 'phase' | 'group' | 'status'>

const TASK = /^- \[([ x-])\] (T\d+)\s+(.*)$/
const HEADING = /^#{2,3} ([PG])\d+\b.*$/

export function parseTodo(text: string): Parsed[] {
  const rows: Parsed[] = []
  let phase = ''
  let group = ''
  for (const line of text.split('\n')) {
    const heading = HEADING.exec(line)
    if (heading) {
      const title = line.replace(/^#+ /, '')
      if (heading[1] === 'P') {
        phase = title
        group = ''
      } else group = title
      continue
    }
    const task = TASK.exec(line)
    if (!task) continue
    const mark = task[1]!, id = task[2]!, rest = task[3]!
    let status: TaskStatus = 'open'
    if (mark === 'x') status = 'done'
    else if (mark === '-') status = 'closed'
    else if (/^BLOCKED\b/.test(rest)) status = 'blocked'
    else if (/^USER\b/.test(rest)) status = 'user'
    rows.push({
      id,
      title: rest.replace(/^(BLOCKED\([^)]*\)|IN-PROGRESS|USER)\s*(—|-)?\s*/, ''),
      phase,
      group,
      status,
    })
  }
  return rows
}

export function taskIdsIn(prompt: string): string[] {
  const blocks = [...prompt.matchAll(/^- \[[ x-]\] (T\d+)\b/gm)].map(m => m[1]!)
  return [...new Set(blocks)]
}

/** Folds a fresh read of the TODO into the run, stamping tasks as they finish. */
export function mergeTodo(run: TasklistRun, text: string, now: number): TasklistRun {
  const old = new Map(run.tasks.map(t => [t.id, t]))
  const running = new Set(Object.values(run.agents).flatMap(a => a.taskIds))
  const tasks = parseTodo(text).map(p => {
    const prev = old.get(p.id)
    const task: TaskRow = { tokens: 0, costUsd: 0, ...prev, ...p }
    if (p.status === 'done' || p.status === 'closed') {
      if (prev && prev.status !== p.status && task.endedAt === undefined && !run.doneAtStart.includes(p.id)) task.endedAt = now
    } else if (p.status === 'open' && running.has(p.id) && task.startedAt !== undefined) {
      task.status = 'running'
    }
    return task
  })
  return { ...run, tasks, now }
}

// USD per million tokens, from the published first-party prices: [input, output, cache read].
// Cache writes are billed at 1.25x input (5-minute cache); a model not listed costs nothing here.
const RATES: [RegExp, [number, number, number]][] = [
  [/fable-5|mythos-5/, [10, 50, 0.25]],
  [/opus-5-5/, [4, 20, 0.2]],
  [/opus-(5|4)/, [5, 25, 0.5]],
  [/sonnet-5/, [2, 10, 0.2]],
  [/sonnet-4/, [3, 15, 0.3]],
  [/haiku-5/, [0.1, 0.5, 0.01]],
  [/haiku-4/, [1, 5, 0.1]],
]

export type Usage = {
  model: string
  input_tokens: number
  output_tokens: number
  cache_read_input_tokens: number
  cache_creation_input_tokens: number
}

export function costOf(u: Usage): number {
  const rate = RATES.find(([re]) => re.test(u.model))?.[1]
  if (!rate) return 0
  const [inp, out, read] = rate
  return (
    (u.input_tokens * inp + u.output_tokens * out + u.cache_read_input_tokens * read + u.cache_creation_input_tokens * inp * 1.25) /
    1e6
  )
}

export type Summary = { done: number; total: number; tokens: number; costUsd: number; elapsedMs: number }

export function summarize(run: TasklistRun): Summary {
  return {
    done: run.tasks.filter(t => t.status === 'done').length,
    total: run.tasks.filter(t => t.status !== 'closed').length,
    tokens: run.tasks.reduce((n, t) => n + t.tokens, 0) + run.orchestratorTokens,
    costUsd: run.tasks.reduce((n, t) => n + t.costUsd, 0) + run.orchestratorCostUsd,
    elapsedMs: run.now - run.startedAt,
  }
}

export type Line =
  | { kind: 'heading'; depth: number; title: string; tasks: TaskRow[] }
  | { kind: 'task'; depth: number; task: TaskRow }

/** Lays tasks out by whatever hierarchy the list has: phases, groups, both or neither. */
export function layout(tasks: TaskRow[]): Line[] {
  const hasPhases = tasks.some(t => t.phase)
  const hasGroups = tasks.some(t => t.group)
  const taskDepth = (hasPhases ? 1 : 0) + (hasGroups ? 1 : 0)
  const lines: Line[] = []
  let phase: string | undefined
  let group: string | undefined
  for (const t of tasks) {
    if (hasPhases && t.phase !== phase) {
      phase = t.phase
      group = undefined
      lines.push({ kind: 'heading', depth: 0, title: t.phase || 'Other', tasks: tasks.filter(x => x.phase === t.phase) })
    }
    if (hasGroups && t.group !== group) {
      group = t.group
      lines.push({
        kind: 'heading',
        depth: hasPhases ? 1 : 0,
        title: t.group || 'Other',
        tasks: tasks.filter(x => x.phase === t.phase && x.group === t.group),
      })
    }
    lines.push({ kind: 'task', depth: taskDepth, task: t })
  }
  return lines
}

export const fmtTokens = (n: number) =>
  n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : String(Math.round(n))

export const fmtCost = (n: number) => (n === 0 ? '' : n < 0.01 ? '<$0.01' : `$${n.toFixed(2)}`)

export function fmtDuration(ms: number) {
  const s = Math.max(0, Math.round(ms / 1000))
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  return h > 0 ? `${h}h${String(m).padStart(2, '0')}m` : m > 0 ? `${m}m${String(s % 60).padStart(2, '0')}s` : `${s}s`
}

export function fmtClock(ms: number) {
  const d = new Date(ms)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${p(d.getHours())}:${p(d.getMinutes())}`
}
