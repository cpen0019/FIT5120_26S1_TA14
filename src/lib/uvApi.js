const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function fetchJson(path, postcode) {
  const url = new URL(path, API_BASE_URL)
  if (postcode && path !== '/api/uv/citywise') {
    url.searchParams.set('postcode', postcode)
  }

  const response = await fetch(url)
  const payload = await response.json()
  if (!response.ok) {
    throw new Error(payload.error || 'Request failed.')
  }
  return payload
}

export function fetchRealtime(postcode) {
  return fetchJson('/api/uv/realtime', postcode)
}

export function fetchHourly(postcode) {
  return fetchJson('/api/uv/hourly', postcode)
}

export function fetchWeekly(postcode) {
  return fetchJson('/api/uv/weekly', postcode)
}

export function fetchCitywise() {
  return fetchJson('/api/uv/citywise')
}
