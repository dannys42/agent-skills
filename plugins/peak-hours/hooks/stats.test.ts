import { test, expect } from 'claude-code/testing'

import { addObservation, assess, binKey, estimate, fitsStore, mergeBins, report } from './stats'
import type { Bins } from './stats'

const isAssumed = (key: string) => key[0] === 'w' && Number(key.slice(1)) >= 5 && Number(key.slice(1)) < 11

// deterministic noise
const noise = (i: number) => 1 + 0.1 * Math.sin(i * 12.9898)

const fill = (bins: Bins, key: string, rate: number, n: number, days: number) => {
  for (let i = 0; i < n; i++) {
    const t = 10 + (i % 7)
    addObservation(bins, key, rate * t * noise(i), t, 1, i % days)
  }
}

test('binKey splits weekday and weekend', () => {
  expect(binKey({ weekday: 3, hour: 7 })).toBe('w07')
  expect(binKey({ weekday: 6, hour: 7 })).toBe('e07')
})

test('estimate recovers the rate with a small error', () => {
  const bins: Bins = {}
  fill(bins, 'w08', 0.5, 60, 5)
  const e = estimate(bins.w08)!
  expect(Math.abs(e.rate - 0.5)).toBeLessThan(0.05)
  expect(e.se).toBeLessThan(0.05)
})

test('peak confirmed: no disagreement', () => {
  const bins: Bins = {}
  for (let h = 12; h < 18; h++) fill(bins, `w${h}`, 0.2, 40, 5)
  for (let h = 5; h < 11; h++) fill(bins, `w0${h}`.replace('w010', 'w10'), 0.5, 40, 5)
  const a = assess(bins, isAssumed)
  expect(a.disagreeing.length).toBe(0)
  expect(a.rows.filter(r => r.verdict === 'elevated').length).toBe(6)
})

test('flat data inside the assumed window disagrees', () => {
  const bins: Bins = {}
  for (let h = 12; h < 18; h++) fill(bins, `w${h}`, 0.2, 40, 5)
  for (const k of ['w06', 'w07', 'w08']) fill(bins, k, 0.2, 40, 5)
  const a = assess(bins, isAssumed)
  expect(a.disagreeing.length).toBe(3)
  expect(report(a)).toContain('DISAGREES')
})

test('too little data stays unsure', () => {
  const bins: Bins = {}
  for (let h = 12; h < 18; h++) fill(bins, `w${h}`, 0.2, 40, 5)
  fill(bins, 'w07', 0.9, 5, 5)
  expect(assess(bins, isAssumed).rows.find(r => r.key === 'w07')!.verdict).toBe('unsure')
})

test('merging adds sums and the store stays small', () => {
  const a: Bins = {}
  const b: Bins = {}
  fill(a, 'w08', 0.5, 10, 2)
  fill(b, 'w08', 0.5, 10, 2)
  const merged = mergeBins(a, b)
  expect(merged.w08![0]).toBe(20)

  const all: Bins = {}
  for (const w of ['w', 'e']) for (let h = 0; h < 24; h++) fill(all, `${w}${String(h).padStart(2, '0')}`, 0.3, 50, 7)
  expect(JSON.stringify(all).length).toBeLessThan(6000)
  expect(fitsStore(all)).toBe(true)
})
