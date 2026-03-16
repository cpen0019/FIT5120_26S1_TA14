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

      <div class="chart-row" v-if="chartData">
        <div class="chart-wrapper">
          <Line :data="chartData" :options="chartOptions" />
        </div>

        <div class="legend-card">
          <div class="legend-header">
            <span class="legend-heading">Legend</span>
            <span class="legend-subtitle">UV classification</span>
          </div>

          <div class="legend-list">
            <div
              v-for="item in uvLegend"
              :key="item.label"
              class="legend-row"
            >
              <div class="legend-left">
                <span
                  class="legend-dot"
                  :style="{ backgroundColor: item.color }"
                ></span>
                <span class="legend-label">{{ item.label }}</span>
              </div>

              <span class="legend-range">{{ item.range }}</span>
            </div>
          </div>
        </div>
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

const uvLegend = [
  { label: 'Low', range: '0–2', color: '#1f9d55' },
  { label: 'Moderate', range: '3–5', color: '#f2e94e' },
  { label: 'High', range: '6–7', color: '#f39c34' },
  { label: 'Very High', range: '8–10', color: '#ef3340' },
  { label: 'Extreme', range: '11+', color: '#a23fa3' }
]

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
        label(context) {
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
  width: 100%;
  min-height: 100vh;
  padding: 36px 24px 60px;
  background: linear-gradient(180deg, #f8f5ec 0%, #f4efe3 100%);
  box-sizing: border-box;
  font-family: "DM Sans", sans-serif;
  color: #1f3d73;
}

.top-bar {
  display: grid;
  grid-template-columns: 1.5fr 0.9fr;
  gap: 24px;
  margin-bottom: 28px;
}

.page-title,
.search-box,
.section-card {
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 28px;
  box-shadow: 0 14px 34px rgba(31, 47, 86, 0.05);
}

.page-title {
  padding: 36px;
  margin: 0;
  font-size: 3rem;
  font-weight: 500;
  color: #1f3d73;
}

.search-box {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-label {
  font-size: .9rem;
  font-weight: 600;
  letter-spacing: .14em;
  color: #df6a3b;
  text-transform: uppercase;
}

.location-select,
.location-input {
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid #e6d9bf;
  background: #fffdf7;
  font-size: 15px;
  font-weight: 400;
  color: #1f3d73;
  outline: none;
  font-family: inherit;
}

.location-select:focus,
.location-input:focus {
  border-color: #df6a3b;
  box-shadow: 0 0 0 4px rgba(223,106,59,.12);
}

.search-button {
  padding: 14px;
  border: none;
  border-radius: 16px;
  background: #df6a3b;
  color: #fff;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
}

.uv-card {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  padding: 32px;
  border-radius: 28px;
  margin-bottom: 28px;
  border: 1px solid #e6d9bf;
}

.uv-left h2 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 500;
  color: #1f3d73;
}

.small-label {
  font-size: .85rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  font-weight: 600;
  color: #607395;
}

.uv-value {
  font-size: 4.8rem;
  margin: 10px 0;
  font-weight: 500;
  color: #1f3d73;
}

.uv-level {
  font-size: 1.7rem;
  font-weight: 500;
  color: #1f3d73;
}

.uv-advice,
.updated-time {
  color: #607395;
  font-weight: 400;
  line-height: 1.7;
}

.section-card {
  padding: 28px;
  margin-bottom: 24px;
}

.section-card h3 {
  font-size: 1.9rem;
  margin-bottom: 18px;
  font-weight: 500;
  color: #1f3d73;
}

.chart-row {
  display: flex;
  gap: 24px;
}

.chart-wrapper {
  flex: 1;
  height: 360px;
}

.legend-card {
  width: 320px;
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 24px;
  padding: 22px;
}

.legend-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 18px;
}

.legend-heading {
  font-size: .9rem;
  font-weight: 600;
  letter-spacing: .14em;
  color: #df6a3b;
  text-transform: uppercase;
}

.legend-subtitle {
  font-size: .9rem;
  font-weight: 500;
  color: #607395;
}

.legend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fffdf7;
  border-radius: 16px;
  padding: 14px 16px;
  border: 1px solid #eee3cf;
}

.legend-left {
  font-weight: 400;
}

.legend-label,
.legend-range {
  font-weight: 400;
  color: #1f3d73;
}

.table-wrapper {
  border-radius: 18px;
  border: 1px solid #eadfca;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #fffdf7;
}

th,
td {
  padding: 16px 14px;
  border-bottom: 1px solid #efe6d7;
  font-size: 15px;
  font-weight: 400;
  color: #607395;
  text-align: center;
}

th {
  background: #fff5de;
  color: #1f3d73;
  font-size: .8rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  font-weight: 600;
}

.status-text {
  margin-top: 12px;
  color: #607395;
}

.error-text {
  background: #fff3f1;
  border: 1px solid #efc3bd;
  border-radius: 16px;
  padding: 14px;
  color: #b94a48;
}

.uv-low {
  background: linear-gradient(135deg,#e5f6e8,#d5efd9);
}

.uv-moderate {
  background: linear-gradient(135deg,#fff7d6,#f8ecaa);
}

.uv-high {
  background: linear-gradient(135deg,#ffe9d5,#f5c48f);
}

.uv-very-high {
  background: linear-gradient(135deg,#ffdfe2,#f5b5bb);
}

.uv-extreme {
  background: linear-gradient(135deg,#eee4ff,#d3bef4);
}

@media (max-width:1100px){

.top-bar{
grid-template-columns:1fr;
}

.chart-row{
flex-direction:column;
}

.legend-card{
width:100%;
}

}

@media (max-width:768px){

.home-page{
padding:24px 16px 40px;
}

.page-title,
.search-box,
.section-card,
.legend-card{
border-radius:22px;
}

.page-title{
font-size:2.4rem;
}

.chart-wrapper{
height:300px;
}

}
</style>