export async function request(url, options) {
  const response = await fetch(url, options)
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`)
  return data
}
export const getHealth = () => request('/api/health')
export const getModelInfo = () => request('/api/model-info')
export const predictOne = (values) => request('/api/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values) })
export const predictBulk = (file) => { const data = new FormData(); data.append('file', file); return request('/api/predict/bulk', { method: 'POST', body: data }) }
