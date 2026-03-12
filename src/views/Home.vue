<template>
  <div class="home-page">
    <div class="top-bar">
      <h1 class="page-title">Sun Safety Dashboard</h1>

      <div class="search-box">
        <label class="search-label">Location</label>
        <select v-model="selectedLocation" @change="handleLocationChange" class="location-select">
          <option value="current">Current Location</option>
        </select>
      </div>
    </div>

    <div class="uv-card" :class="uvCardClass">
      <div class="uv-left">
        <p class="small-label">Selected Location</p>
        <h2>{{ locationName }}</h2>
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

const selectedLocation = ref('current')
const locationName = ref('Current Location')
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

function handleLocationChange() {
  if (selectedLocation.value === 'current') {
    getCurrentLocation()
  }
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
      locationName.value = 'Current Location'
      fetchWeather(lat, lon)
    },
    () => {
      error.value = 'Unable to retrieve your current location.'
    }
  )
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
      .filter(item => item.time.startsWith(today))
      .slice(0, 24)

    hourlyLabels.value = todayHourlyItems.map(item => formatHour(item.time))
    hourlyUvValues.value = todayHourlyItems.map(item => item.uv)

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
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  padding: 32px 40px;
  background: #fffbea;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 28px;
}

.page-title {
  margin: 0;
  font-size: 32px;
  line-height: 1.25;
  color: #333;
  text-align: left;
}

.search-box {
  display: flex;
  flex-direction: column;
  min-width: 260px;
}

.search-label {
  font-size: 14px;
  margin-bottom: 8px;
  color: #666;
  text-align: left;
}

.location-select {
  padding: 12px 14px;
  border: 1px solid #d8d8d8;
  border-radius: 14px;
  background: #fff;
  font-size: 15px;
  outline: none;
}

.uv-card {
  display: flex;
  justify-content: space-between;
  gap: 28px;
  padding: 28px;
  border-radius: 22px;
  margin-bottom: 28px;
  color: #222;
}

.uv-left,
.uv-right {
  flex: 1;
}

.uv-left {
  text-align: left;
}

.uv-right {
  text-align: center;
}

.small-label {
  font-size: 13px;
  text-transform: uppercase;
  opacity: 0.75;
  margin-bottom: 10px;
}

.uv-value {
  font-size: 64px;
  line-height: 1;
  margin: 12px 0;
}

.uv-level {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
}

.uv-advice {
  margin-top: 10px;
  font-size: 16px;
}

.updated-time {
  margin-top: 12px;
  color: #555;
  font-size: 15px;
}

.section-card {
  width: 100%;
  background: #ffffff;
  border-radius: 22px;
  padding: 24px;
  margin-bottom: 28px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
}

.section-card h3 {
  margin-top: 0;
  margin-bottom: 18px;
  font-size: 22px;
  color: #34495e;
  text-align: left;
}

.chart-wrapper {
  height: 420px;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

th,
td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
  font-size: 15px;
}

th {
  background: #fff4bf;
}

.status-text {
  color: #666;
  margin-top: 10px;
  text-align: left;
}

.error-text {
  color: #c62828;
}

.uv-low {
  background: #d8f3dc;
}

.uv-moderate {
  background: #fff3b0;
}

.uv-high {
  background: #ffd6a5;
}

.uv-very-high {
  background: #ffadad;
}

.uv-extreme {
  background: #d0b3ff;
}

.uv-unknown {
  background: #eeeeee;
}

@media (max-width: 768px) {
  .home-page {
    padding: 24px 20px;
  }

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

  .chart-wrapper {
    height: 320px;
  }
}
</style>