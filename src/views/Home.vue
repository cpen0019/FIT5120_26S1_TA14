<template>
  <div class="home-page">
    <div class="top-bar">
      <h1 class="page-title">Sun Safety Dashboard</h1>

      <div class="search-box">
        <label class="search-label">Location Type</label>
        <select v-model="locationType" class="location-select">
          <option value="current">Current Location</option>
          <option value="city">City</option>
          <option value="suburb">Suburb</option>
          <option value="postcode">Postcode</option>
        </select>

        <input
          v-if="locationType !== 'current'"
          v-model="searchQuery"
          type="text"
          class="location-input"
          :placeholder="getPlaceholder()"
          @keyup.enter="handleLocationChange"
        />

        <button class="search-button" @click="handleLocationChange">
          {{ locationType === 'current' ? 'Use Current Location' : 'Search Location' }}
        </button>
      </div>
    </div>

    <div class="uv-card" :class="uvCardClass">
      <div class="uv-left">
        <p class="small-label">Selected Location</p>
        <h2>{{ locationName }}</h2>

        <p class="updated-time" v-if="latitude !== null && longitude !== null">
          Lat: {{ Number(latitude).toFixed(4) }} | Lon: {{ Number(longitude).toFixed(4) }}
        </p>

        <p class="updated-time" v-if="currentTime">
          Updated: {{ formatDateTime(currentTime) }}
        </p>
      </div>

      <div class="uv-right">
        <p class="small-label">Current UV Index</p>
        <h2 class="uv-value">{{ displayUv(currentUv) }}</h2>
        <p class="uv-level">{{ uvLevel.label }}</p>
        <p class="uv-advice">{{ uvLevel.advice }}</p>
      </div>
    </div>

    <div class="section-card">
      <h3>Today's 24-Hour UV Index</h3>
      <div class="chart-wrapper" v-if="chartData">
        <Line :data="chartData" :options="chartOptions" />
      </div>
      <p v-else class="status-text">Loading chart...</p>
    </div>

    <div class="section-card">
      <h3>Next 7 Days Forecast</h3>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>UV Max</th>
              <th>Risk Level</th>
              <th>Max Temp (°C)</th>
              <th>Min Temp (°C)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="day in dailyRows" :key="day.date">
              <td>{{ formatDate(day.date) }}</td>
              <td>{{ displayUv(day.uv) }}</td>
              <td>{{ getUvLevel(day.uv).label }}</td>
              <td>{{ displayTemp(day.maxTemp) }}</td>
              <td>{{ displayTemp(day.minTemp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p v-if="loading" class="status-text">Loading weather data...</p>
    <p v-if="error" class="status-text error-text">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale
)

const locationType = ref('current')
const searchQuery = ref('')
const locationName = ref('Current Location')
const latitude = ref(null)
const longitude = ref(null)
const currentUv = ref(null)
const currentTime = ref('')
const dailyRows = ref([])
const hourlyLabels = ref([])
const hourlyUvValues = ref([])
const loading = ref(false)
const error = ref('')

const uvLevel = computed(() => getUvLevel(currentUv.value))
const uvCardClass = computed(() => uvLevel.value.className)

const chartData = computed(() => {
  if (!hourlyLabels.value.length) return null

  return {
    labels: hourlyLabels.value,
    datasets: [
      {
        label: 'UV Index',
        data: hourlyUvValues.value,
        tension: 0.4,
        borderWidth: 3,
        borderColor: '#3b82f6',
        backgroundColor: '#3b82f6',
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: false
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true
    },
    tooltip: {
      callbacks: {
        label: function (context) {
          return `UV Index: ${Number(context.raw).toFixed(2)}`
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      suggestedMax: 12,
      ticks: {
        stepSize: 2
      }
    }
  }
}

function getPlaceholder() {
  if (locationType.value === 'city') return 'Enter city (e.g. Melbourne)'
  if (locationType.value === 'suburb') return 'Enter suburb (e.g. Clayton)'
  if (locationType.value === 'postcode') return 'Enter postcode (e.g. 3168)'
  return 'Enter location'
}

function getUvLevel(uv) {
  if (uv === null || uv === undefined) {
    return {
      label: 'Unknown',
      advice: 'No data available.',
      className: 'uv-unknown'
    }
  }

  if (uv <= 2) {
    return {
      label: 'Low',
      advice: 'Minimal protection required.',
      className: 'uv-low'
    }
  } else if (uv <= 5) {
    return {
      label: 'Moderate',
      advice: 'Wear sunscreen and sunglasses.',
      className: 'uv-moderate'
    }
  } else if (uv <= 7) {
    return {
      label: 'High',
      advice: 'Reduce time in the sun at midday.',
      className: 'uv-high'
    }
  } else if (uv <= 10) {
    return {
      label: 'Very High',
      advice: 'Seek shade and use strong protection.',
      className: 'uv-very-high'
    }
  } else {
    return {
      label: 'Extreme',
      advice: 'Avoid direct sun exposure if possible.',
      className: 'uv-extreme'
    }
  }
}

async function handleLocationChange() {
  error.value = ''

  if (locationType.value === 'current') {
    getCurrentLocation()
    return
  }

  if (!searchQuery.value.trim()) {
    error.value = 'Please enter a valid location.'
    return
  }

  await searchLocation(searchQuery.value.trim())
}

function getCurrentLocation() {
  error.value = ''

  if (!navigator.geolocation) {
    error.value = 'Geolocation is not supported by your browser.'
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude
      const lon = position.coords.longitude

      latitude.value = lat
      longitude.value = lon
      locationName.value = 'Current Location'

      fetchWeather(lat, lon)
    },
    () => {
      error.value = 'Unable to retrieve your current location.'
    }
  )
}

async function searchLocation(query) {
  loading.value = true
  error.value = ''

  try {
    const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(query + ', Australia')}`
    const response = await fetch(url, {
      headers: {
        Accept: 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('Failed to search location.')
    }

    const data = await response.json()

    if (!data.length) {
      throw new Error('No matching location found.')
    }

    const place = data[0]
    const lat = Number(place.lat)
    const lon = Number(place.lon)

    latitude.value = lat
    longitude.value = lon
    locationName.value = place.display_name

    await fetchWeather(lat, lon)
  } catch (err) {
    error.value = err.message || 'Something went wrong while searching location.'
  } finally {
    loading.value = false
  }
}

async function fetchWeather(lat, lon) {
  loading.value = true
  error.value = ''

  try {
    const url =
      `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
      `&current=uv_index` +
      `&hourly=uv_index` +
      `&daily=uv_index_max,temperature_2m_max,temperature_2m_min` +
      `&timezone=auto`

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error('Failed to fetch weather data.')
    }

    const data = await response.json()

    currentUv.value = data.current?.uv_index ?? null
    currentTime.value = data.current?.time ?? ''

    const today = getLocalTodayDateString()

    const todayHourlyItems = data.hourly.time
      .map((time, index) => ({
        time,
        uv: data.hourly.uv_index[index]
      }))
      .filter((item) => item.time.startsWith(today))
      .slice(0, 24)

    hourlyLabels.value = todayHourlyItems.map((item) => formatHour(item.time))
    hourlyUvValues.value = todayHourlyItems.map((item) => item.uv)

    dailyRows.value = data.daily.time.slice(0, 7).map((date, index) => ({
      date,
      uv: data.daily.uv_index_max[index],
      maxTemp: data.daily.temperature_2m_max[index],
      minTemp: data.daily.temperature_2m_min[index]
    }))
  } catch (err) {
    error.value = err.message || 'Something went wrong.'
  } finally {
    loading.value = false
  }
}

function getLocalTodayDateString() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatHour(dateTimeStr) {
  const date = new Date(dateTimeStr)
  return date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString([], {
    weekday: 'short',
    day: 'numeric',
    month: 'short'
  })
}

function formatDateTime(dateTimeStr) {
  const date = new Date(dateTimeStr)
  return date.toLocaleString([], {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

function displayUv(value) {
  if (value === null || value === undefined) return '--'
  return Number(value).toFixed(2)
}

function displayTemp(value) {
  if (value === null || value === undefined) return '--'
  return Number(value).toFixed(1)
}

onMounted(() => {
  getCurrentLocation()
})
</script>

<style scoped>
.home-page {
  max-width: 1280px;
  margin: 0 auto;
  min-height: 100vh;
  padding: 36px 40px 48px;
  background:
    radial-gradient(circle at top left, #fff8d6 0%, #fffbea 35%, #f8fbff 100%);
  box-sizing: border-box;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #1f2937;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 28px;
  margin-bottom: 30px;
}

.page-title {
  margin: 0;
  font-size: 36px;
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #1e293b;
  text-align: left;
}

.search-box {
  display: flex;
  flex-direction: column;
  min-width: 320px;
  gap: 12px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(10px);
}

.search-label {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 2px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  text-align: left;
}

.location-select,
.location-input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #dbe3ee;
  border-radius: 14px;
  background: #ffffff;
  font-size: 15px;
  font-weight: 500;
  color: #1f2937;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.location-select:focus,
.location-input:focus {
  border-color: #60a5fa;
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.18);
}

.location-input::placeholder {
  color: #94a3b8;
}

.search-button {
  width: 100%;
  padding: 14px 18px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 55%, #60a5fa 100%);
  color: white;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.01em;
  cursor: pointer;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.28);
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.search-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(37, 99, 235, 0.34);
}

.search-button:active {
  transform: translateY(0);
  opacity: 0.95;
}

.uv-card {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  padding: 32px;
  border-radius: 26px;
  margin-bottom: 30px;
  color: #1f2937;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(6px);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.uv-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.14);
}

.uv-left,
.uv-right {
  flex: 1;
}

.uv-left {
  text-align: left;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.uv-left h2 {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  line-height: 1.2;
  color: #0f172a;
  word-break: break-word;
}

.uv-right {
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.small-label {
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  opacity: 0.75;
  margin-bottom: 10px;
}

.uv-value {
  font-size: 76px;
  line-height: 1;
  margin: 10px 0 12px;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.uv-level {
  font-size: 24px;
  font-weight: 800;
  margin: 0;
}

.uv-advice {
  margin-top: 10px;
  font-size: 16px;
  line-height: 1.55;
  color: #334155;
}

.updated-time {
  margin-top: 12px;
  color: #475569;
  font-size: 14px;
  line-height: 1.45;
}

.section-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.88);
  border-radius: 24px;
  padding: 26px;
  margin-bottom: 30px;
  box-shadow: 0 16px 38px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.section-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.1);
}

.section-card h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
  text-align: left;
  letter-spacing: -0.01em;
}

.chart-wrapper {
  height: 420px;
  padding: 8px 4px 4px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 18px;
  border: 1px solid #e5e7eb;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
  overflow: hidden;
}

th,
td {
  padding: 16px 14px;
  text-align: left;
  border-bottom: 1px solid #edf2f7;
  font-size: 15px;
}

th {
  background: linear-gradient(180deg, #fff7cf 0%, #fff0a8 100%);
  color: #334155;
  font-weight: 800;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

tbody tr {
  transition: background-color 0.18s ease;
}

tbody tr:hover {
  background-color: #f8fbff;
}

tbody tr:last-child td {
  border-bottom: none;
}

.status-text {
  color: #475569;
  margin-top: 14px;
  text-align: left;
  font-size: 15px;
  font-weight: 500;
}

.error-text {
  color: #b91c1c;
  background: #fff1f2;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid #fecdd3;
}

.uv-low {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
}

.uv-moderate {
  background: linear-gradient(135deg, #fef9c3 0%, #fde68a 100%);
}

.uv-high {
  background: linear-gradient(135deg, #ffedd5 0%, #fdba74 100%);
}

.uv-very-high {
  background: linear-gradient(135deg, #ffe4e6 0%, #fda4af 100%);
}

.uv-extreme {
  background: linear-gradient(135deg, #ede9fe 0%, #c4b5fd 100%);
}

.uv-unknown {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
}

@media (max-width: 992px) {
  .top-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    min-width: unset;
    width: 100%;
  }

  .uv-card {
    flex-direction: column;
  }

  .uv-right {
    text-align: left;
  }

  .uv-value {
    font-size: 64px;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding: 24px 18px 34px;
  }

  .page-title {
    font-size: 30px;
  }

  .search-box {
    padding: 16px;
    border-radius: 18px;
  }

  .uv-card,
  .section-card {
    padding: 20px;
    border-radius: 20px;
  }

  .uv-left h2 {
    font-size: 24px;
  }

  .uv-value {
    font-size: 56px;
  }

  .uv-level {
    font-size: 20px;
  }

  .chart-wrapper {
    height: 320px;
  }

  th,
  td {
    padding: 13px 10px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 26px;
  }

  .uv-value {
    font-size: 48px;
  }

  .section-card h3 {
    font-size: 20px;
  }
}
</style>