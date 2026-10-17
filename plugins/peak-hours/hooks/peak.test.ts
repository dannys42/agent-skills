import { test, expect } from 'claude-code/testing'

import { peakLabel } from './peak'

const at = (iso: string) => Date.parse(iso)

test('peak during PDT weekday morning', () => {
  // 2026-10-16 is a Friday; 07:45 PDT = 14:45 UTC
  expect(peakLabel(at('2026-10-16T14:45:00Z'))).toBe('PEAK · ends in 3h 15m')
})

test('not peak at 11:00 PDT or before 5:00 PDT', () => {
  expect(peakLabel(at('2026-10-16T18:00:00Z'))).toBeNull()
  expect(peakLabel(at('2026-10-16T11:59:00Z'))).toBeNull()
  expect(peakLabel(at('2026-10-16T12:00:00Z'))).toBe('PEAK · ends in 6h 0m')
})

test('uses PST in winter', () => {
  // 2026-12-14 is a Monday; 05:30 PST = 13:30 UTC
  expect(peakLabel(at('2026-12-14T13:30:00Z'))).toBe('PEAK · ends in 5h 30m')
  expect(peakLabel(at('2026-12-14T12:59:00Z'))).toBeNull()
})

test('not peak on weekends', () => {
  expect(peakLabel(at('2026-10-17T15:00:00Z'))).toBeNull()
})

test('DST switch days', () => {
  // 2026-03-09 Monday, DST began 03-08: 06:00 PDT = 13:00 UTC
  expect(peakLabel(at('2026-03-09T13:00:00Z'))).toBe('PEAK · ends in 5h 0m')
  // 2026-11-02 Monday, DST ended 11-01: 06:00 PST = 14:00 UTC
  expect(peakLabel(at('2026-11-02T14:00:00Z'))).toBe('PEAK · ends in 5h 0m')
})
