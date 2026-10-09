export type TaskStatus = 'open' | 'running' | 'done' | 'closed' | 'blocked' | 'user'

export type TaskRow = {
  id: string
  title: string
  /** Phase heading (`## P1 ...`), empty when the list has none. */
  phase: string
  /** Group heading (`### G1 ...`), empty when the list has none. */
  group: string
  status: TaskStatus
  /** Model of the implementer agent, as the engine resolved it. */
  model?: string
  tokens: number
  costUsd: number
  startedAt?: number
  endedAt?: number
}

export type AgentRow = { taskIds: string[]; role: 'implement' | 'review'; model?: string; isDone?: boolean }

export type TasklistRun = {
  isActive: boolean
  file: string
  startedAt: number
  now: number
  tasks: TaskRow[]
  agents: Record<string, AgentRow>
  doneAtStart: string[]
  orchestratorTokens: number
  orchestratorCostUsd: number
}

declare module 'claude-code' {
  interface PluginState {
    'task-workflow': { run: TasklistRun | null }
  }
}
