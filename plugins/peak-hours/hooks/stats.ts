// Fixed-size aggregate of rate-limit cost per Pacific hour, so the file cannot grow:
// 24 hours x weekday/weekend = 48 bins of 9 numbers each.

// Each observation is one rise of the 5-hour window's percentUsed (d, in points)
// over the weighted tokens spent since the last reading (t, in thousands).
// Bin = [observations, turns, sum d, sum t, sum d^2, sum t^2, sum d*t, days seen, last day]
export type Bin = [number, number, number, number, number, number, number, number, number]
export type Bins = Record<string, Bin>

export const MAX_STORE_BYTES = 16_000
export const MIN_OBSERVATIONS = 20
export const MIN_DAYS = 3
// A bin counts as elevated when its rate beats the off-peak baseline by this factor.
export const ELEVATED_FACTOR = 1.2
export const Z = 3
// Bins that must contradict the assumed window before the badge says so.
export const MIN_DISAGREEING_BINS = 2

// Relative token weights, from list-price ratios; an assumption, kept in one place.
export const weighTokens = (u: {
  input_tokens: number
  output_tokens: number
  cache_creation_input_tokens: number
  cache_read_input_tokens: number
}) => (u.input_tokens + 5 * u.output_tokens + 1.25 * u.cache_creation_input_tokens + 0.1 * u.cache_read_input_tokens) / 1000

export const binKey = (parts: { weekday: number; hour: number }) =>
  `${parts.weekday === 0 || parts.weekday === 6 ? 'e' : 'w'}${String(parts.hour).padStart(2, '0')}`

export const emptyBin = (): Bin => [0, 0, 0, 0, 0, 0, 0, 0, -1]

const round = (n: number) => Math.round(n * 1e6) / 1e6

export const addObservation = (bins: Bins, key: string, d: number, t: number, turns: number, day: number) => {
  const bin = (bins[key] ??= emptyBin())
  bin[0] += 1
  bin[1] += turns
  bin[2] = round(bin[2] + d)
  bin[3] = round(bin[3] + t)
  bin[4] = round(bin[4] + d * d)
  bin[5] = round(bin[5] + t * t)
  bin[6] = round(bin[6] + d * t)
  if (bin[8] !== day) {
    bin[7] += 1
    bin[8] = day
  }
}

export const mergeBins = (into: Bins, from: Bins): Bins => {
  for (const [key, b] of Object.entries(from)) {
    const a = (into[key] ??= emptyBin())
    for (let i = 0; i < 7; i++) a[i] = round(a[i]! + b[i]!)
    a[7] += b[7]
    a[8] = Math.max(a[8], b[8])
  }

  return into
}

export type Estimate = { rate: number; se: number; n: number; days: number }

// Ratio estimator R = sum d / sum t, standard error by linearisation.
export const estimate = (bin: Bin | undefined): Estimate | null => {
  if (!bin || bin[0] < 2 || bin[3] <= 0) return null
  const [n, , sd, st, sdd, stt, sdt, days] = bin
  const rate = sd / st
  const residual = Math.max(0, sdd - 2 * rate * sdt + rate * rate * stt)
  const meanT = st / n

  return { rate, se: Math.sqrt(residual / (n * (n - 1))) / meanT, n, days }
}

export type Verdict = 'elevated' | 'normal' | 'unsure'

const isConfident = (e: Estimate | null): e is Estimate => e !== null && e.n >= MIN_OBSERVATIONS && e.days >= MIN_DAYS

export type Row = { key: string; est: Estimate | null; times: number | null; verdict: Verdict; isAssumedPeak: boolean }

export type Assessment = { baseline: Estimate | null; rows: Row[]; disagreeing: Row[] }

// `isAssumed(key)` says whether a bin is inside the assumed peak window.
export const assess = (bins: Bins, isAssumed: (key: string) => boolean): Assessment => {
  const keys = Object.keys(bins).sort()
  const offKeys = keys.filter(k => !isAssumed(k))
  const total = emptyBin()
  const acc: Bins = { x: total }
  for (const k of offKeys) mergeBins(acc, { x: bins[k]! })
  const baseline = estimate(acc.x)
  const baselineOk = isConfident(baseline)

  const rows = keys.map((key): Row => {
    const est = estimate(bins[key])
    const times = est && baseline && baseline.rate > 0 ? est.rate / baseline.rate : null
    let verdict: Verdict = 'unsure'
    if (baselineOk && isConfident(est)) {
      const bar = baseline.rate * ELEVATED_FACTOR
      if (est.rate - Z * est.se > bar) verdict = 'elevated'
      else if (est.rate + Z * est.se < bar) verdict = 'normal'
    }

    return { key, est, times, verdict, isAssumedPeak: isAssumed(key) }
  })

  const disagreeing = rows.filter(r => (r.isAssumedPeak && r.verdict === 'normal') || (!r.isAssumedPeak && r.verdict === 'elevated'))

  return { baseline, rows, disagreeing }
}

export const hasDisagreement = (a: Assessment) => a.disagreeing.length >= MIN_DISAGREEING_BINS

export const fitsStore = (bins: Bins) => JSON.stringify(bins).length <= MAX_STORE_BYTES

export const report = (a: Assessment): string => {
  if (a.rows.length === 0) return 'peak-hours: no data collected yet.'
  const lines = [
    `peak-hours: cost per weighted kilotoken vs off-peak baseline (${a.baseline ? 'baseline known' : 'baseline not yet known'}).`,
    'bin  assumed  obs  days  x baseline  verdict',
  ]
  for (const r of a.rows) {
    const hour = `${r.key[0] === 'w' ? 'wkday' : 'wkend'} ${r.key.slice(1)}h`
    lines.push(
      `${hour}  ${r.isAssumedPeak ? 'peak   ' : 'off    '}  ${String(r.est?.n ?? 0).padStart(3)}  ${String(r.est?.days ?? 0).padStart(4)}  ${
        r.times === null ? '   -    ' : `${r.times.toFixed(2)} ±${((r.est!.se / a.baseline!.rate) * Z).toFixed(2)}`
      }  ${r.verdict}`,
    )
  }
  lines.push(
    hasDisagreement(a)
      ? `DISAGREES with the assumed window in: ${a.disagreeing.map(r => r.key).join(', ')}`
      : 'No confident disagreement with the assumed 5-11 PT weekday window.',
  )
  lines.push(`Confidence needs >= ${MIN_OBSERVATIONS} observations over >= ${MIN_DAYS} days per bin, ${Z} standard errors. Other sessions on the same account add noise.`)

  return lines.join('\n')
}
