export function summarizePredictions(records) {
  const countsByRisk = Object.fromEntries(['Low', 'Medium', 'High'].map(level => [
    level,
    records.filter(row => row.Risk_Level === level).length,
  ]))
  const probabilities = records.map(row => Number(row.Churn_Probability)).filter(Number.isFinite)

  return {
    total: records.length,
    likely: records.filter(row => row.Prediction === 'Likely to Churn').length,
    high: countsByRisk.High,
    avg: probabilities.length ? probabilities.reduce((sum, value) => sum + value, 0) / probabilities.length : 0,
    risks: ['Low', 'Medium', 'High'].map(name => ({ name, value: countsByRisk[name] })).filter(item => item.value),
    histogram: Array.from({ length: 10 }, (_, index) => ({
      bucket: `${index * 10}–${index * 10 + 10}%`,
      count: probabilities.filter(value => value >= index / 10 && (index === 9 ? value <= 1 : value < (index + 1) / 10)).length,
    })),
    legendCounts: countsByRisk,
  }
}

export function predictionActivity(records) {
  return Object.values(records.slice().reverse().reduce((groups, row) => {
    const date = row._createdAt ? new Date(row._createdAt) : null
    const day = date && !Number.isNaN(date.getTime())
      ? date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
      : 'Undated'
    groups[day] ??= { day, count: 0 }
    groups[day].count += 1
    return groups
  }, {})).slice(-7)
}
