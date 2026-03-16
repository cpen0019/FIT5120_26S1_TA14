<template>
  <div class="clothes-page">
    <section class="hero-card">
      <p class="eyebrow">SMART CLOTHING GUIDE</p>
      <h1>UV-Based Clothing Recommendation</h1>
      <p class="hero-text">
        Get clothing and sun protection advice based on the current UV level at your location.
      </p>
    </section>

    <section class="control-card">
      <div class="control-grid">
        <div class="field-group">
          <label class="field-label">Location Type</label>
          <select v-model="locationType" class="input-field">
            <option value="current">Current Location</option>
            <option value="city">City</option>
            <option value="suburb">Suburb</option>
            <option value="postcode">Postcode</option>
          </select>
        </div>

        <div class="field-group" v-if="locationType !== 'current'">
          <label class="field-label">Location</label>
          <input
            v-model="searchQuery"
            class="input-field"
            :placeholder="getPlaceholder()"
            @keyup.enter="loadRecommendations"
          />
        </div>

        <div class="action-group">
          <button class="action-button" @click="loadRecommendations">
            Get Clothing Recommendation
          </button>
        </div>
      </div>
    </section>

    <div v-if="loading" class="status-card">
      <p>Loading...</p>
    </div>

    <div v-else-if="error" class="status-card error-card">
      <p>{{ error }}</p>
    </div>

    <section v-else class="content-grid">
      <div class="summary-card" :class="uvLevel.className">
        <p class="eyebrow">CURRENT UV</p>
        <h2>{{ formatUv(currentUv) }}</h2>
        <p class="uv-label">{{ uvLevel.label }}</p>
        <p class="location-text">{{ locationName }}</p>
        <p class="meta-text" v-if="temperature !== null">
          Temperature: {{ formatTemp(temperature) }}
        </p>
      </div>

      <div class="recommendation-card">
        <p class="eyebrow">WHAT TO WEAR</p>
        <h3>Recommended Protection</h3>

        <ul class="recommendation-list">
          <li v-for="item in clothingAdvice.items" :key="item">
            {{ item }}
          </li>
        </ul>

        <div class="tip-box">
          <p class="tip-title">Advice</p>
          <p class="tip-text">{{ clothingAdvice.note }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getRealtimeUV } from '../lib/api'

const locationType = ref('current')
const searchQuery = ref('')
const locationName = ref('Current Location')
const currentUv = ref(null)
const temperature = ref(null)
const loading = ref(false)
const error = ref('')

const uvLevel = computed(() => getUvLevel(currentUv.value))
const clothingAdvice = computed(() => getClothingAdvice(currentUv.value))

function getPlaceholder() {
  if (locationType.value === 'city') return 'Enter city (e.g. Melbourne)'
  if (locationType.value === 'suburb') return 'Enter suburb (e.g. Clayton)'
  if (locationType.value === 'postcode') return 'Enter postcode (e.g. 3168)'
  return 'Enter location'
}

function getUvLevel(uv) {
  const value = Number(uv)

  if (!Number.isFinite(value)) {
    return {
      label: 'Unknown',
      className: 'uv-unknown'
    }
  }

  if (value <= 2) {
    return {
      label: 'Low',
      className: 'uv-low'
    }
  }

  if (value <= 5) {
    return {
      label: 'Moderate',
      className: 'uv-moderate'
    }
  }

  if (value <= 7) {
    return {
      label: 'High',
      className: 'uv-high'
    }
  }

  if (value <= 10) {
    return {
      label: 'Very High',
      className: 'uv-very-high'
    }
  }

  return {
    label: 'Extreme',
    className: 'uv-extreme'
  }
}

function getClothingAdvice(uv) {
  const value = Number(uv)

  if (!Number.isFinite(value)) {
    return {
      items: ['UV data unavailable'],
      note: 'Try again after allowing location access or searching for a place.'
    }
  }

  if (value <= 2) {
    return {
      items: [
        'Regular T-shirt is fine',
        'Cap optional',
        'Sunglasses optional'
      ],
      note: 'Low UV. Basic clothing is usually enough.'
    }
  }

  if (value <= 5) {
    return {
      items: [
        'T-shirt or light full-sleeve shirt',
        'Hat recommended',
        'Sunglasses recommended',
        'Apply sunscreen'
      ],
      note: 'Moderate UV. Use normal outdoor protection.'
    }
  }

  if (value <= 7) {
    return {
      items: [
        'Light long-sleeve shirt preferred',
        'Wide-brim hat',
        'UV-protective sunglasses',
        'Apply SPF 30+ or SPF 50+ sunscreen'
      ],
      note: 'High UV. Reduce direct sun exposure during peak hours.'
    }
  }

  if (value <= 10) {
    return {
      items: [
        'Long sleeves strongly recommended',
        'Wide-brim hat',
        'Sunglasses',
        'SPF 50+ sunscreen',
        'Seek shade whenever possible'
      ],
      note: 'Very high UV. Strong sun protection is needed.'
    }
  }

  return {
    items: [
      'Full sleeve clothing recommended',
      'Wide-brim hat',
      'UV sunglasses',
      'SPF 50+ sunscreen',
      'Avoid direct outdoor exposure if possible'
    ],
    note: 'Extreme UV. Limit outdoor exposure and stay protected.'
  }
}

async function loadRecommendations() {
  error.value = ''

  if (locationType.value === 'current') {
    await loadCurrentLocation()
    return
  }

  if (!searchQuery.value.trim()) {
    error.value = 'Please enter a valid location.'
    return
  }

  await searchLocation(searchQuery.value.trim())
}

async function loadCurrentLocation() {
  loading.value = true
  error.value = ''

  try {
    const coords = await getBrowserLocation()
    locationName.value = 'Current Location'
    await fetchUv(coords.latitude, coords.longitude)
  } catch (err) {
    error.value = err.message || 'Failed to get current location.'
  } finally {
    loading.value = false
  }
}

function getBrowserLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by your browser.'))
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        })
      },
      () => reject(new Error('Unable to retrieve your current location.'))
    )
  })
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

    if (!Array.isArray(data) || !data.length) {
      throw new Error('No matching location found.')
    }

    const place = data[0]
    locationName.value = place.display_name

    await fetchUv(Number(place.lat), Number(place.lon))
  } catch (err) {
    error.value = err.message || 'Failed to search location.'
  } finally {
    loading.value = false
  }
}

async function fetchUv(lat, lon) {
  const response = await getRealtimeUV(lat, lon)
  currentUv.value = response?.current?.uv_index ?? null
  temperature.value = response?.current?.temperature_2m ?? null
}

function formatUv(value) {
  const num = Number(value)
  return Number.isFinite(num) ? num.toFixed(2) : '--'
}

function formatTemp(value) {
  const num = Number(value)
  return Number.isFinite(num) ? `${num.toFixed(1)}°C` : '--'
}

onMounted(() => {
  loadRecommendations()
})
</script>

<style scoped>
.clothes-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 36px 24px 60px;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f5ec 0%, #f4efe3 100%);
}

.hero-card,
.control-card,
.summary-card,
.recommendation-card,
.status-card {
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 28px;
  box-shadow: 0 14px 34px rgba(31, 47, 86, 0.05);
}

.hero-card {
  padding: 32px;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0;
  color: #df6a3b;
  font-size: 0.82rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-weight: 700;
}

.hero-card h1 {
  margin: 10px 0 12px;
  color: #1f3d73;
  font-size: 2.6rem;
  line-height: 1.08;
  font-weight: 500;
}

.hero-text {
  margin: 0;
  color: #4d6288;
  line-height: 1.7;
}

.control-card {
  padding: 24px;
  margin-bottom: 24px;
}

.control-grid {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 16px;
  align-items: end;
}

.field-group {
  display: grid;
  gap: 8px;
}

.field-label {
  color: #1f3d73;
  font-size: 0.92rem;
  font-weight: 600;
}

.input-field {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #e6d9bf;
  border-radius: 16px;
  background: #fffdf7;
  color: #1f3d73;
  font-size: 15px;
  outline: none;
}

.input-field:focus {
  border-color: #df6a3b;
  box-shadow: 0 0 0 4px rgba(223, 106, 59, 0.12);
}

.action-group {
  display: flex;
}

.action-button {
  padding: 14px 20px;
  border: none;
  border-radius: 16px;
  background: #1f3d73;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  min-width: 240px;
}

.content-grid {
  display: grid;
  grid-template-columns: 0.85fr 1.15fr;
  gap: 24px;
}

.summary-card,
.recommendation-card {
  padding: 28px;
}

.summary-card h2 {
  margin: 12px 0 6px;
  font-size: 3rem;
  color: #1f3d73;
  font-weight: 700;
}

.uv-label {
  margin: 0 0 10px;
  color: #1f3d73;
  font-size: 1.1rem;
  font-weight: 700;
}

.location-text,
.meta-text {
  margin: 0;
  color: #4d6288;
  line-height: 1.6;
}

.recommendation-card h3 {
  margin: 10px 0 16px;
  color: #1f3d73;
  font-size: 1.5rem;
}

.recommendation-list {
  margin: 0;
  padding-left: 20px;
  color: #1f2f56;
  line-height: 1.9;
}

.tip-box {
  margin-top: 20px;
  padding: 18px;
  border-radius: 18px;
  background: #fff7ea;
  border: 1px solid #eadfc7;
}

.tip-title {
  margin: 0 0 8px;
  color: #1f3d73;
  font-weight: 700;
}

.tip-text {
  margin: 0;
  color: #4d6288;
  line-height: 1.7;
}

.status-card {
  padding: 24px;
  text-align: center;
  color: #1f3d73;
}

.error-card {
  border-color: #e3b8b8;
  color: #9f2f2f;
  background: #fff5f5;
}

.uv-low {
  border-left: 8px solid #1f9d55;
}

.uv-moderate {
  border-left: 8px solid #f2e94e;
}

.uv-high {
  border-left: 8px solid #f39c34;
}

.uv-very-high {
  border-left: 8px solid #ef3340;
}

.uv-extreme {
  border-left: 8px solid #a23fa3;
}

.uv-unknown {
  border-left: 8px solid #94a3b8;
}

@media (max-width: 980px) {
  .control-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .action-button {
    width: 100%;
    min-width: unset;
  }
}

@media (max-width: 768px) {
  .clothes-page {
    padding: 24px 16px 40px;
  }

  .hero-card h1 {
    font-size: 2.1rem;
  }

  .summary-card h2 {
    font-size: 2.4rem;
  }
}
</style>