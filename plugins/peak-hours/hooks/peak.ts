// Peak window in US Pacific wall-clock time (PST or PDT, whichever is observed).
export const START_HOUR = 5
export const END_HOUR = 11

const HOUR = 3_600_000
const MINUTE = 60_000

// The nth Sunday of a month at the given UTC hour.
const nthSunday = (year: number, month: number, n: number, utcHour: number) => {
  const first = new Date(Date.UTC(year, month, 1))
  const day = 1 + ((7 - first.getUTCDay()) % 7) + 7 * (n - 1)
  return Date.UTC(year, month, day, utcHour)
}

// US DST: second Sunday of March 02:00 PST (10:00 UTC) to first Sunday of
// November 02:00 PDT (09:00 UTC).
const pacificOffsetMs = (ms: number) => {
  const year = new Date(ms).getUTCFullYear()
  const isDst = ms >= nthSunday(year, 2, 2, 10) && ms < nthSunday(year, 10, 1, 9)
  return (isDst ? -7 : -8) * HOUR
}

export const formatDuration = (ms: number) => {
  const minutes = Math.max(1, Math.ceil(ms / MINUTE))
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

export type PacificParts = { weekday: number; hour: number; sinceMidnightMs: number; day: number }

export const pacificParts = (ms: number): PacificParts => {
  const shifted = ms + pacificOffsetMs(ms)
  const local = new Date(shifted)
  const sinceMidnightMs =
    local.getUTCHours() * HOUR + local.getUTCMinutes() * MINUTE + local.getUTCSeconds() * 1000 + local.getUTCMilliseconds()

  return { weekday: local.getUTCDay(), hour: local.getUTCHours(), sinceMidnightMs, day: Math.floor(shifted / 86_400_000) }
}

export const isAssumedPeak = ({ weekday, hour }: { weekday: number; hour: number }) =>
  weekday !== 0 && weekday !== 6 && hour >= START_HOUR && hour < END_HOUR

// "PEAK · ends in 2h 15m" during peak, null otherwise.
export const peakLabel = (ms: number): string | null => {
  const parts = pacificParts(ms)
  if (!isAssumedPeak(parts)) return null

  return `PEAK · ends in ${formatDuration(END_HOUR * HOUR - parts.sinceMidnightMs)}`
}
