import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import { isAssumedPeak, pacificParts, peakLabel } from './peak'
import {
  addObservation,
  assess,
  binKey,
  fitsStore,
  hasDisagreement,
  mergeBins,
  report,
  weighTokens,
} from './stats'
import type { Bins } from './stats'

const label = atom({ plugin: 'peak-hours', key: 'label' } as const, null)
const hasDisagreementAtom = atom({ plugin: 'peak-hours', key: 'hasDisagreement' } as const, false)

const STORE_KEY = 'bins-v1'
const PERSIST_EVERY = 20
const isAssumedKey = (key: string) => isAssumedPeak({ weekday: key[0] === 'w' ? 1 : 0, hour: Number(key.slice(1)) })

// Merge a session's observations into the store; the caller clears its delta.
async function persist($: EngineInterface, delta: Bins) {
  const stored = ((await $.store.get(STORE_KEY)) ?? {}) as Bins
  const merged = mergeBins(stored, delta)
  // Never write past the cap: keep the old data and drop this delta.
  if (fitsStore(merged)) await $.store.set(STORE_KEY, merged)
}

async function refreshAlert($: EngineInterface) {
  const stored = ((await $.store.get(STORE_KEY)) ?? {}) as Bins
  const flag = hasDisagreement(assess(stored, isAssumedKey))
  if (flag !== (await read($, hasDisagreementAtom))) await update($, hasDisagreementAtom, () => flag)
}

async function flush($: EngineInterface, delta: Bins) {
  await persist($, delta)
  await refreshAlert($)
}

export const register: Register = on => {
  // This session's observations only; merged into the store, then cleared.
  let delta: Bins = {}
  let unsaved = 0
  let lastPct: number | null = null
  let lastResetsAt: string | undefined
  let pendingTokens = 0
  let pendingTurns = 0

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'peak-report', description: 'Show observed rate-limit cost by hour vs the assumed peak window' })

    const refresh = async () => {
      const text = peakLabel(await $.clock.now())
      if (text !== (await read($, label))) await update($, label, () => text)
    }

    await refresh()
    await refreshAlert($)
    $.clock.every(60_000, refresh)

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const usage = (e as any).usage
    if (usage) {
      pendingTokens += weighTokens(usage)
      pendingTurns += 1
    }

    const { rateLimits } = await $.session.usage()
    const window = rateLimits.find(r => r.kind === 'five_hour')

    if (window) {
      const pct = window.percentUsed
      const isSameWindow = lastPct !== null && window.resetsAt === lastResetsAt && pct >= lastPct

      if (isSameWindow && pct > lastPct! && pendingTokens > 0) {
        const parts = pacificParts(await $.clock.now())
        addObservation(delta, binKey(parts), pct - lastPct!, pendingTokens, pendingTurns, parts.day)
        pendingTokens = 0
        pendingTurns = 0
        unsaved += 1
        lastPct = pct
        if (unsaved >= PERSIST_EVERY) {
          await flush($, delta)
          delta = {}
          unsaved = 0
        }
      } else if (!isSameWindow) {
        lastPct = pct
        pendingTokens = 0
        pendingTurns = 0
      }
      lastResetsAt = window.resetsAt
    }

    return next(e)
  })

  on('session.end', async ($, e, next) => {
    if (unsaved > 0) await persist($, delta)
    delta = {}
    unsaved = 0

    return next(e)
  })

  on('command.run', { command: 'peak-report' }, async $ => {
    if (unsaved > 0) await persist($, delta)
    delta = {}
    unsaved = 0
    const stored = ((await $.store.get(STORE_KEY)) ?? {}) as Bins

    return { text: report(assess(stored, isAssumedKey)) }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const text = await read($, label)
    const isDisagreeing = await read($, hasDisagreementAtom)

    if (text === null && !isDisagreeing) {
      return next(e)
    }

    const { Box, Text } = $.ui.resolve(e)

    return (
      <Box justifyContent="flex-end">
        {isDisagreeing ? (
          <Text color="yellow" bold>
            🟠 PEAK? data disagrees · /peak-report
          </Text>
        ) : (
          <Text color="red" bold>
            🔴 {text}
          </Text>
        )}
      </Box>
    )
  })
}
