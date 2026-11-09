import test from 'node:test'
import assert from 'node:assert/strict'
import { summarizePredictions } from './analytics.js'

const individual = [
  { Churn_Probability: .25, Prediction: 'Unlikely to Churn', Risk_Level: 'Low', _source: 'Individual' },
  { Churn_Probability: .45, Prediction: 'Likely to Churn', Risk_Level: 'Medium', _source: 'Individual' },
]
const bulk = [
  { Churn_Probability: .72, Prediction: 'Likely to Churn', Risk_Level: 'High', _source: 'Bulk CSV' },
]

test('source summaries count only the records passed to each section', () => {
  const singleSummary = summarizePredictions(individual)
  const bulkSummary = summarizePredictions(bulk)
  assert.equal(singleSummary.total, 2)
  assert.equal(singleSummary.avg, .35)
  assert.deepEqual(singleSummary.risks, [{ name: 'Low', value: 1 }, { name: 'Medium', value: 1 }])
  assert.equal(bulkSummary.total, 1)
  assert.equal(bulkSummary.avg, .72)
  assert.deepEqual(bulkSummary.risks, [{ name: 'High', value: 1 }])
})

test('probability bins preserve threshold edges and per-source counts', () => {
  const singleSummary = summarizePredictions(individual)
  const bulkSummary = summarizePredictions(bulk)
  assert.equal(singleSummary.histogram[2].count, 1)
  assert.equal(singleSummary.histogram[4].count, 1)
  assert.equal(bulkSummary.histogram[7].count, 1)
  assert.equal(bulkSummary.histogram.reduce((sum, bin) => sum + bin.count, 0), bulk.length)
})
