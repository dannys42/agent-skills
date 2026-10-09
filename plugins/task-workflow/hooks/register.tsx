import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { TaskRow, TasklistRun } from '../types'
import { costOf, hasLiveAgents, modelColumn, modelLabel, fmtClock, fmtCost, fmtDuration, fmtTokens, layout, mergeTodo, parseTodo, summarize, taskIdsMentioned } from './todo'

const PANE = 'tasklist-monitor'
const run = atom({ plugin: 'task-workflow', key: 'run' } as const, null)
const DIRS = ['.', 'docs', 'Docs', 'doc', 'Documentation']
const ICON = { open: '[ ]', running: '[~]', done: '[x]', closed: '[-]', blocked: '[!]', user: '[u]' } as const

async function findTodo($: any): Promise<string | undefined> {
  let best: { path: string; mtimeMs: number } | undefined
  for (const dir of DIRS) {
    const entries = await $.fs.list(dir).catch(() => [])
    for (const f of entries) {
      if (f.kind !== 'file' || !/^TODO.*\.md$/.test(f.name)) continue
      if (!best || f.mtimeMs > best.mtimeMs) best = { path: dir === '.' ? f.name : `${dir}/${f.name}`, mtimeMs: f.mtimeMs }
    }
  }
  return best?.path
}

// Runs in the mod's own process on a timer: no model call, so it costs no tokens.
async function refresh($: any) {
  const now = await $.clock.now()
  const current = await read($, run)
  if (!current?.isActive) return
  const text = await $.fs.read(current.file).catch(() => undefined)
  await update($, run, (r: TasklistRun | null) =>
    r ? (typeof text === 'string' ? mergeTodo(r, text, now) : { ...r, now }) : r,
  )
}

// Debug log only (`claude --debug`): never reaches the model, so diagnosing costs no tokens.
const trace = ($: any, text: string) => $.ui.log(`task-workflow: ${text}`, { to: 'debug' })

// Creates the run for the newest TODO. With isFresh false, a run already in memory is reactivated instead of reset.
async function startRun($: any, isFresh: boolean): Promise<TasklistRun | undefined> {
  const existing: TasklistRun | null = await read($, run)
  if (existing?.isActive && !isFresh) return existing
  if (existing && !isFresh) {
    await update($, run, (r: TasklistRun | null) => r && { ...r, isActive: true })
    return { ...existing, isActive: true }
  }
  const file = await findTodo($)
  if (!file) {
    trace($, 'startRun: no TODO*.md found')
    return undefined
  }
  const now = await $.clock.now()
  const text = await $.fs.read(file).catch(() => '')
  const base: TasklistRun = {
    isActive: true, file, startedAt: now, now, tasks: [], agents: {},
    doneAtStart: [], orchestratorTokens: 0, orchestratorCostUsd: 0,
  }
  const first = mergeTodo(base, text, now)
  const doneAtStart = first.tasks.filter(t => t.status === 'done' || t.status === 'closed').map(t => t.id)
  const started = { ...first, doneAtStart }
  await update($, run, () => started)
  trace($, `startRun: ${file}, ${started.tasks.length} tasks, ${doneAtStart.length} done at start`)
  void $.ui.open({ id: PANE, title: 'Tasklist run' })
  return started
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'tasklist-monitor',
      description: 'Show the tasklist-run progress pane',
    })
    $.clock.every(5000, () => void refresh($))
    return next(e)
  })

  on('command.run', { command: 'tasklist-monitor' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Tasklist run' })
    return { text: 'Tasklist pane opened.' }
  })

  on('skill.prompt', async ($, e, next) => {
    trace($, `skill.prompt skill=${JSON.stringify(e.skill)}`)
    if (e.skill.endsWith('tasklist-run')) await startRun($, true)
    return next(e)
  })

  // A typed /task-workflow:tasklist-run may reach the engine as a command rather than a skill prompt.
  on('command.run', async ($, e, next) => {
    if (e.command.endsWith('tasklist-run')) {
      trace($, `command.run command=${JSON.stringify(e.command)}`)
      const existing = await read($, run)
      if (!existing?.isActive) await startRun($, true)
    }
    return next(e)
  })

  on('agent.spawn', async ($, e, next) => {
    const result = await next(e)
    const mentioned = taskIdsMentioned(e.description, e.prompt)
    trace($, `agent.spawn description=${JSON.stringify(e.description)} ids=[${mentioned}] agentId=${result.agentId}`)
    if (mentioned.length === 0 || result.agentId === undefined) return result
    // The skill hook may not have fired (or the run ended): task IDs in a spawn mean a run is under way.
    // Only IDs the TODO has count, so a stray "T5" in an unrelated agent's description starts nothing.
    const file = (await read($, run))?.file ?? (await findTodo($))
    const known = new Set(parseTodo((file && (await $.fs.read(file).catch(() => ''))) || '').map(t => t.id))
    const ids = mentioned.filter(id => known.has(id))
    if (ids.length === 0) return result
    const current = await startRun($, false)
    if (!current) return result
    const now = await $.clock.now()
    const role: 'review' | 'implement' = /review/i.test(e.description) ? 'review' : 'implement'
    const agentId = result.agentId
    const model: string | undefined = (result as { model?: string }).model
    await update($, run, (r: TasklistRun | null) =>
      r && {
        ...r,
        now,
        agents: { ...r.agents, [agentId]: { taskIds: ids, role, model } },
        tasks: r.tasks
          .map(t =>
            ids.includes(t.id) && t.status === 'open'
              ? { ...t, status: 'running' as const, startedAt: t.startedAt ?? now }
              : t,
          )
          .map(t => (ids.includes(t.id) && role === 'implement' && model ? { ...t, model } : t)),
      },
    )
    return result
  }).catch(($, e, next) => next(e))

  on('turn.complete', async ($, e, next) => {
    const current = await read($, run)
    if (current?.isActive) {
      const u = e.usage
      const tokens = u ? u.input_tokens + u.output_tokens + u.cache_creation_input_tokens : 0
      const cost = u ? costOf(u) : 0
      const agent = e.agentId === undefined ? undefined : current.agents[e.agentId]
      if (agent) {
        await update($, run, (r: TasklistRun | null) =>
          r && {
            ...r,
            agents: { ...r.agents, [e.agentId!]: { ...agent, isDone: true } },
            tasks: r.tasks.map((t: TaskRow) =>
              agent.taskIds.includes(t.id)
                ? { ...t, tokens: t.tokens + tokens / agent.taskIds.length, costUsd: t.costUsd + cost / agent.taskIds.length }
                : t,
            ),
          },
        )
        await refresh($)
      } else if (e.agentId === undefined) {
        await update($, run, (r: TasklistRun | null) =>
          r && { ...r, orchestratorTokens: r.orchestratorTokens + tokens, orchestratorCostUsd: r.orchestratorCostUsd + cost },
        )
        await refresh($)
        // the orchestrator's turn ended: the run is over unless spawned agents are still working
        // (it resumes when they finish, and its next turn end re-checks)
        await update($, run, (r: TasklistRun | null) => r && (hasLiveAgents(r) ? r : { ...r, isActive: false }))
      }
    }
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const r = await read($, run)
    if (!r) {
      const todo = await findTodo($)
      return (
        <Text dimColor>
          Waiting for /tasklist-run or an agent spawn that names a task ID. TODO found: {todo ?? 'none'}
        </Text>
      )
    }
    const s = summarize(r)
    const width = (e as any).props?.bodyColumns ?? 80
    const mode = modelColumn(width)
    const modelW = mode === 'long' ? 10 : 6
    const cols = (tok: number, usd: number, ms: number | undefined, at?: number, model?: string) =>
      (mode === 'none' ? '' : `${(model ? modelLabel(model, mode === 'short') : '').padEnd(modelW)} `) +
      `${(tok > 0 ? fmtTokens(tok) : '').padStart(7)} ${fmtCost(usd).padStart(7)} ${(ms === undefined ? '' : fmtDuration(ms)).padStart(8)} ${at ? fmtClock(at) : '     '}`
    const row = (head: string, tail: string) => {
      const room = Math.max(10, width - tail.length - 1)
      return head.slice(0, room).padEnd(room) + ' ' + tail
    }
    const lines = layout(r.tasks)
    return (
      <Box flexDirection="column">
        <Text bold>
          {r.isActive ? 'Running' : 'Finished'} {s.done}/{s.total} done · {fmtTokens(s.tokens)} tokens · {fmtCost(s.costUsd) || '$0'} est. · {fmtDuration(s.elapsedMs)}
          {r.doneAtStart.length > 0 ? ` · ${r.doneAtStart.length} already done at start, not costed` : ''}
        </Text>
        <Text dimColor>{row('', `${mode === 'none' ? '' : 'model'.padEnd(modelW) + ' '}${'tokens'.padStart(7)} ${'cost'.padStart(7)} ${'duration'.padStart(8)} done `)}</Text>
        {lines.map(l => {
          if (l.kind === 'heading') {
            const ts = l.tasks
            const started = ts.map(t => t.startedAt).filter((x): x is number => x !== undefined)
            const isEnded = ts.every(t => t.endedAt !== undefined || t.status === 'closed')
            const end = isEnded ? Math.max(...ts.map(t => t.endedAt ?? 0)) : r.now
            const ms = started.length === 0 ? undefined : end - Math.min(...started)
            return (
              <Text bold>
                {row('  '.repeat(l.depth) + l.title, cols(ts.reduce((n, t) => n + t.tokens, 0), ts.reduce((n, t) => n + t.costUsd, 0), ms))}
              </Text>
            )
          }
          const t = l.task
          const ms = t.startedAt === undefined ? undefined : (t.endedAt ?? r.now) - t.startedAt
          return (
            <Text
              dimColor={t.status === 'done' || t.status === 'closed'}
              color={t.status === 'blocked' ? 'red' : t.status === 'running' ? 'yellow' : undefined}
            >
              {row('  '.repeat(l.depth) + `${ICON[t.status]} ${t.id} ${t.title}`, cols(t.tokens, t.costUsd, ms, t.endedAt, t.model))}
            </Text>
          )
        })}
      </Box>
    )
  })
}
