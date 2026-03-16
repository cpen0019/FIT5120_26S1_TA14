const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function fetchJson(path, params = {}) {
  const url = new URL(path, API_BASE_URL)

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value)
    }
  })

  const response = await fetch(url)
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Request failed')
  }

  return data
}

export function getRealtimeUV(lat, lon) {
  return fetchJson('/api/uv/realtime', { lat, lon })
}

export function getHourlyUV(lat, lon) {
  return fetchJson('/api/uv/hourly', { lat, lon })
}

export function getWeeklyUV(lat, lon) {
  return fetchJson('/api/uv/weekly', { lat, lon })
}

export function getCancerTrends() {
  return fetchJson('/api/cancer/trends')
}

export function getCancerAgeGroups() {
  return fetchJson('/api/cancer/age-groups')
}

export function getMapStates() {
  return fetchJson('/api/map/states')
}

export function getMapStateDetails(state) {
  return fetchJson(`/api/map/state/${encodeURIComponent(state)}`)
}

export function getMapComparison() {
  return fetchJson('/api/map/compare')
}