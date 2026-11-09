import test from 'node:test'
import assert from 'node:assert/strict'
import { appendPredictionRows, BULK_HISTORY_KEY, LEGACY_HISTORY_KEY, loadPredictionHistories, SINGLE_HISTORY_KEY } from './history.js'

function storageWith(data = {}) {
  const values = new Map(Object.entries(data))
  return {
    getItem: key => values.has(key) ? values.get(key) : null,
    setItem: (key, value) => values.set(key, value),
    removeItem: key => values.delete(key),
  }
}

const single = { tenure: 12, Churn_Probability: .31, Prediction: 'Unlikely to Churn', Risk_Level: 'Low', _createdAt: '2026-01-01T00:00:00Z' }
const bulk = { tenure: 18, Churn_Probability: .62, Prediction: 'Likely to Churn', Risk_Level: 'High', _id: 'bulk-1' }

test('legacy mixed history migrates into source-specific histories once', () => {
  const storage = storageWith({ [LEGACY_HISTORY_KEY]: JSON.stringify([single, bulk]) })
  const first = loadPredictionHistories(storage)
  const second = loadPredictionHistories(storage)
  assert.equal(first.single.length, 1)
  assert.equal(first.bulk.length, 1)
  assert.equal(second.single.length, 1)
  assert.equal(second.bulk.length, 1)
  assert.equal(first.single[0]._source, 'Individual')
  assert.equal(first.bulk[0]._source, 'Bulk CSV')
  assert.equal(storage.getItem(LEGACY_HISTORY_KEY), null)
})

test('new single and bulk results are persisted in separate keys', () => {
  const storage = storageWith()
  appendPredictionRows(storage, 'single', [single])
  appendPredictionRows(storage, 'bulk', [bulk])
  assert.equal(JSON.parse(storage.getItem(SINGLE_HISTORY_KEY)).length, 1)
  assert.equal(JSON.parse(storage.getItem(BULK_HISTORY_KEY)).length, 1)
  assert.equal(JSON.parse(storage.getItem(SINGLE_HISTORY_KEY))[0]._source, 'Individual')
  assert.equal(JSON.parse(storage.getItem(BULK_HISTORY_KEY))[0]._source, 'Bulk CSV')
})

test('replayed bulk record identifiers are not counted twice', () => {
  const storage = storageWith()
  appendPredictionRows(storage, 'bulk', [bulk])
  appendPredictionRows(storage, 'bulk', [bulk])
  assert.equal(JSON.parse(storage.getItem(BULK_HISTORY_KEY)).length, 1)
})
