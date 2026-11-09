export const SINGLE_HISTORY_KEY = 'churn-single-history'
export const BULK_HISTORY_KEY = 'churn-bulk-history'
export const LEGACY_HISTORY_KEY = 'churn-history'

function readRows(storage, key) {
  try {
    const value = JSON.parse(storage.getItem(key) || '[]')
    return Array.isArray(value) ? value.filter(row => row && typeof row === 'object') : []
  } catch {
    return []
  }
}

function sourceKey(source) {
  return source === 'bulk' ? BULK_HISTORY_KEY : SINGLE_HISTORY_KEY
}

function fingerprint(row, source) {
  if (row._id) return `${source}:${row._id}`
  const stable = Object.keys(row).filter(key => key !== '_source').sort().map(key => [key, row[key]])
  return `${source}:${JSON.stringify(stable)}`
}

function uniqueRows(rows, source) {
  const seen = new Set()
  return rows.filter(row => {
    const key = fingerprint(row, source)
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function tagRows(rows, source) {
  const label = source === 'bulk' ? 'Bulk CSV' : 'Individual'
  return rows.map(row => ({ ...row, _source: label }))
}

export function loadPredictionHistories(storage) {
  const savedSingle = readRows(storage, SINGLE_HISTORY_KEY)
  const savedBulk = readRows(storage, BULK_HISTORY_KEY)
  const legacy = readRows(storage, LEGACY_HISTORY_KEY)
  const legacySingle = legacy.filter(row => row._source === 'Individual' || (!row._source && !row._id))
  const legacyBulk = legacy.filter(row => row._source === 'Bulk CSV' || (!row._source && Boolean(row._id)))
  const single = uniqueRows([...tagRows(savedSingle, 'single'), ...tagRows(legacySingle, 'single')], 'single').slice(0, 200)
  const bulk = uniqueRows([...tagRows(savedBulk, 'bulk'), ...tagRows(legacyBulk, 'bulk')], 'bulk').slice(0, 200)
  storage.setItem(SINGLE_HISTORY_KEY, JSON.stringify(single))
  storage.setItem(BULK_HISTORY_KEY, JSON.stringify(bulk))
  storage.removeItem(LEGACY_HISTORY_KEY)
  return { single, bulk }
}

export function appendPredictionRows(storage, source, rows) {
  const key = sourceKey(source)
  const current = readRows(storage, key)
  const label = source === 'bulk' ? 'Bulk CSV' : 'Individual'
  const incoming = rows.map(row => ({
    ...row,
    _id: row._id || `${source}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
    _source: label,
  }))
  const updated = uniqueRows([...incoming, ...current], source).slice(0, 200)
  storage.setItem(key, JSON.stringify(updated))
  return updated
}
