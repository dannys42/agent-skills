import { test, expect, mock } from 'claude-code/testing'

const TODO = '## P1 A\n- [ ] T1 First\n- [ ] T2 Second\n'
const BLOCK = 'Implement:\n- [ ] T1 First\n'

let n = 0
function setup($: any, on: any) {
  mock.clock(on)
  on('fs.list', () => ({ value: [{ name: 'TODO.md', kind: 'file', size: 1, mtimeMs: 1 }] }))
  on('fs.read', () => ({ value: TODO }))
  on('agent.spawn', () => ({ model: 'claude-opus-5-5', agentId: `agent-${(n += 1)}` }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('skill.prompt', () => ({ text: '' }))
  on('turn.complete', () => ({ text: '' }))
  on('ui.log', () => ({ value: undefined }))
}
const pane = async ($: any, bodyColumns?: number) => {
  const ui = await $.ui.mount({ plugin: 'task-workflow', surface: 'terminal', component: 'Pane', props: { bodyColumns }, requestId: 'tasklist-monitor' })
  const text = JSON.stringify(await ui.drawn())
  await ui.unmount()
  return text
}
const spawn = ($: any) => $.agent.spawn({ prompt: BLOCK, description: 'implement T1' })
const complete = ($: any, agentId?: string) => $.turn.complete({ reason: 'answer', answer: '', agentId })

test('a spawn with task blocks starts the run when skill.prompt never fired', async ($, on) => {
  setup($, on)
  expect(await pane($)).toContain('Waiting for /tasklist-run')
  await spawn($)
  expect(await pane($)).toContain('Running')
})

test('the orchestrator turn ending keeps the run alive while an agent is live', async ($, on) => {
  setup($, on)
  const { agentId } = await spawn($)
  await complete($)
  expect(await pane($)).toContain('Running')
  await complete($, agentId)
  await complete($)
  expect(await pane($)).toContain('Finished')
})

test('a spawn after the run ended reactivates it', async ($, on) => {
  setup($, on)
  await $.skill.prompt({ skill: 'task-workflow:tasklist-run', text: '' })
  await complete($)
  expect(await pane($)).toContain('Finished')
  await spawn($)
  expect(await pane($)).toContain('Running')
})

test('the slash-command path still creates the run', async ($, on) => {
  setup($, on)
  await $.skill.prompt({ skill: 'tasklist-run', text: '' })
  expect(await pane($)).toContain('Running')
})

test('other skills do not start a run', async ($, on) => {
  setup($, on)
  await $.skill.prompt({ skill: 'commit', text: '' })
  expect(await pane($)).toContain('Waiting for /tasklist-run')
})

test('a spawn naming the ID only in its description starts the run', async ($, on) => {
  setup($, on)
  await $.agent.spawn({ prompt: 'Task: keep the key out of git', description: 'Implement T1 gitignore' })
  expect(await pane($)).toContain('Running')
})

test('a spawn with no task ID starts nothing', async ($, on) => {
  setup($, on)
  await $.agent.spawn({ prompt: 'Task: keep the key out of git', description: 'Implement gitignore' })
  expect(await pane($)).toContain('Waiting for /tasklist-run')
})

test('an ID the TODO does not have starts nothing', async ($, on) => {
  setup($, on)
  await $.agent.spawn({ prompt: 'x', description: 'Implement T99' })
  expect(await pane($)).toContain('Waiting for /tasklist-run')
})

test('a typed slash command starts the run', async ($, on) => {
  setup($, on)
  on('command.run', () => ({ text: '' }))
  await $.command.run({ command: 'task-workflow:tasklist-run' })
  expect(await pane($)).toContain('Running')
})

test('the empty pane names the TODO it found', async ($, on) => {
  setup($, on)
  expect(await pane($)).toContain('TODO.md')
})

test('the model column follows the pane width', async ($, on) => {
  setup($, on)
  await spawn($)
  const wide = await pane($, 120)
  expect(wide).toContain('Opus 5.5')
  expect(wide).toContain('duration')
  expect(await pane($, 80)).toContain('Opu5.5')
  const narrow = await pane($, 50)
  expect(narrow).not.toContain('Opu5.5')
  expect(narrow).not.toContain('model')
})
