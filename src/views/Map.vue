<template>
  <div class="map-page">
    <section class="hero-grid">
      <div class="hero-card">
        <p class="eyebrow">REGIONAL UV + CANCER VIEW</p>
        <h1>Australia UV & Skin Cancer Map</h1>
        <p class="hero-text">
          Switch between live UV conditions and long-term melanoma burden across
          Australian states and territories.
        </p>
      </div>

      <div class="hero-card summary-card">
        <p class="eyebrow">SELECTED REGION</p>
        <h2>{{ selectedStateName }}</h2>

        <div class="summary-stack" v-if="activeMode === 'uv'">
          <div>
            <p class="summary-mini-label">Current UV</p>
            <p class="summary-number">{{ formatUv(selectedStateUv?.uv) }}</p>
            <p class="summary-subtext">{{ getUvLevel(selectedStateUv?.uv).label }}</p>
          </div>

          <div>
            <p class="summary-mini-label">Temperature</p>
            <p class="summary-number small">{{ formatTempValue(selectedStateUv?.temperature) }}</p>
            <p class="summary-subtext">Current state capital estimate</p>
          </div>
        </div>

        <div class="summary-stack" v-else>
          <div>
            <p class="summary-mini-label">Average Cancer Rate</p>
            <p class="summary-number small">{{ formatRate(selectedStateSummary?.avg_incidence_rate) }}</p>
            <p class="summary-subtext">Average age-standardised rate</p>
          </div>

          <div>
            <p class="summary-mini-label">Total Cases</p>
            <p class="summary-number small">{{ formatNumber(selectedStateSummary?.total_cases) }}</p>
            <p class="summary-subtext">Across available years</p>
          </div>
        </div>
      </div>
    </section>

    <div v-if="loading" class="status-card">
      <p>Loading map analytics...</p>
    </div>

    <div v-else-if="error" class="status-card error-card">
      <p>{{ error }}</p>
    </div>

    <section v-else class="content-grid">
      <section class="map-card">
        <div class="card-header">
          <div>
            <p class="eyebrow">INTERACTIVE MAP</p>
            <h2>Switch between UV and Cancer views</h2>
            <p class="card-description">
              UV view shows live conditions by state. Cancer view shows long-term melanoma burden.
            </p>
          </div>

          <div class="right-controls">
            <div class="toggle-bar">
              <button
                class="toggle-btn"
                :class="{ active: activeMode === 'uv' }"
                @click="activeMode = 'uv'"
              >
                UV View
              </button>
              <button
                class="toggle-btn"
                :class="{ active: activeMode === 'cancer' }"
                @click="activeMode = 'cancer'"
              >
                Cancer View
              </button>
            </div>

            <div class="control-box">
              <label for="state-select">Choose state</label>
              <select id="state-select" v-model="selectedState" @change="handleStateSelect(selectedState)">
                <option v-for="item in stateOptions" :key="item.code" :value="item.code">
                  {{ item.code }} - {{ item.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="map-shell">
          <svg
            class="map-svg"
            :viewBox="`0 0 ${mapViewport.width} ${mapViewport.height}`"
            role="img"
            aria-label="Australia interactive map"
          >
            <g>
              <path
                v-for="feature in featurePaths"
                :key="feature.code"
                :d="feature.path"
                class="state-path"
                :class="{
                  selected: selectedState === feature.code,
                  hovered: hoveredStateCode === feature.code
                }"
                :fill="getStateFill(feature.code)"
                @mouseenter="hoveredStateCode = feature.code"
                @mouseleave="hoveredStateCode = ''"
                @click="handleStateSelect(feature.code)"
              />
            </g>

            <g
              v-for="feature in featurePaths"
              :key="`${feature.code}-label`"
            >
              <template v-if="feature.labelPoint && feature.code !== 'ACT'">
                <text
                  :x="feature.labelPoint.x"
                  :y="feature.labelPoint.y - 10"
                  class="state-label"
                >
                  {{ feature.code }}
                </text>
                <text
                  :x="feature.labelPoint.x"
                  :y="feature.labelPoint.y + 16"
                  class="state-value"
                >
                  {{ getStateLabelValue(feature.code) }}
                </text>
              </template>
            </g>

            <g v-if="actPoint">
              <circle :cx="actPoint.x" :cy="actPoint.y" r="7" class="act-dot" />
              <text :x="actPoint.x + 14" :y="actPoint.y - 10" class="state-label">ACT</text>
              <text :x="actPoint.x + 14" :y="actPoint.y + 16" class="state-value">
                {{ getStateLabelValue('ACT') }}
              </text>
            </g>
          </svg>
        </div>

        <div class="legend-panel">
          <div class="legend-item" v-for="item in activeLegend" :key="item.label">
            <span class="legend-swatch" :style="{ background: item.color }"></span>
            <span>{{ item.label }} ({{ item.range }})</span>
          </div>
        </div>
      </section>

      <aside class="side-column">
        <section class="info-card" v-if="activeMode === 'uv'">
          <p class="eyebrow">UV DETAILS</p>
          <h3>{{ selectedStateName }}</h3>

          <div class="metric-grid">
            <div class="metric-box">
              <span class="metric-label">Current UV</span>
              <strong>{{ formatUv(selectedStateUv?.uv) }}</strong>
              <small>{{ getUvLevel(selectedStateUv?.uv).label }}</small>
            </div>

            <div class="metric-box">
              <span class="metric-label">Temperature</span>
              <strong>{{ formatTempValue(selectedStateUv?.temperature) }}</strong>
              <small>Current</small>
            </div>
          </div>

          <div class="advice-box" :class="getUvLevel(selectedStateUv?.uv).className">
            <p class="advice-title">UV advice</p>
            <p class="advice-text">{{ getUvLevel(selectedStateUv?.uv).advice }}</p>
          </div>

          <div class="comparison-list">
            <div
              v-for="row in uvComparisonRows"
              :key="row.code"
              class="comparison-row"
            >
              <div>
                <strong>{{ row.code }}</strong>
                <p>{{ row.name }}</p>
              </div>

              <div class="comparison-right">
                <span>{{ formatTempValue(row.temperature) }}</span>
                <strong>UV {{ formatUv(row.uv) }}</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="info-card" v-else>
          <p class="eyebrow">CANCER DETAILS</p>
          <h3>{{ selectedStateName }}</h3>

          <div class="metric-grid">
            <div class="metric-box">
              <span class="metric-label">Avg cancer rate</span>
              <strong>{{ formatRate(selectedStateSummary?.avg_incidence_rate) }}</strong>
              <small>Across available years</small>
            </div>

            <div class="metric-box">
              <span class="metric-label">Total cases</span>
              <strong>{{ formatNumber(selectedStateSummary?.total_cases) }}</strong>
              <small>Accumulated</small>
            </div>
          </div>

          <div class="details-table-wrap">
            <table class="details-table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Cases</th>
                  <th>Rate</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in selectedStateDetails" :key="`${row.state}-${row.year}`">
                  <td>{{ row.year }}</td>
                  <td>{{ formatNumber(row.cases) }}</td>
                  <td>{{ formatRate(row.age_standardised_rate) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="info-card" v-if="activeMode === 'cancer'">
          <p class="eyebrow">COMPARISON SNAPSHOT</p>
          <h3>Latest available year</h3>

          <div class="comparison-list">
            <div
              v-for="row in latestComparisonRows"
              :key="`${row.state}-${row.year}`"
              class="comparison-row"
            >
              <div>
                <strong>{{ stateCodeFromName(row.state) }}</strong>
                <p>{{ row.state }}</p>
              </div>

              <div class="comparison-right">
                <span>{{ formatNumber(row.cases) }} cases</span>
                <strong>{{ formatRate(row.age_standardised_rate) }}</strong>
              </div>
            </div>
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { actAnnotation, australiaStatesGeoJson } from '../lib/australiaStatesGeoJson'
import { buildGeoFeaturePaths, mapViewport, projectCoordinates, stateCodeFromName } from '../lib/uvMapModel'
import { getMapStates, getMapStateDetails, getMapComparison, getRealtimeUV } from '../lib/api'

const hoveredStateCode = ref('')
const selectedState = ref('VIC')
const activeMode = ref('uv')
const loading = ref(true)
const error = ref('')

const stateStats = ref([])
const comparisonRows = ref([])
const selectedStateDetails = ref([])
const stateUvRows = ref([])

const featurePaths = buildGeoFeaturePaths(australiaStatesGeoJson)

const stateOptions = [
  { code: 'NSW', name: 'New South Wales', lat: -33.8688, lon: 151.2093 },
  { code: 'VIC', name: 'Victoria', lat: -37.8136, lon: 144.9631 },
  { code: 'QLD', name: 'Queensland', lat: -27.4698, lon: 153.0251 },
  { code: 'SA', name: 'South Australia', lat: -34.9285, lon: 138.6007 },
  { code: 'WA', name: 'Western Australia', lat: -31.9505, lon: 115.8605 },
  { code: 'TAS', name: 'Tasmania', lat: -42.8821, lon: 147.3272 },
  { code: 'NT', name: 'Northern Territory', lat: -12.4634, lon: 130.8456 },
  { code: 'ACT', name: 'Australian Capital Territory', lat: -35.2809, lon: 149.13 }
]

const uvLegend = [
  { label: 'Low', range: '0–2', color: '#1f9d55' },
  { label: 'Moderate', range: '3–5', color: '#f2e94e' },
  { label: 'High', range: '6–7', color: '#f39c34' },
  { label: 'Very High', range: '8–10', color: '#ef3340' },
  { label: 'Extreme', range: '11+', color: '#a23fa3' }
]

const cancerLegend = [
  { label: 'Low', range: '< 40', color: '#dbeafe' },
  { label: 'Moderate', range: '40–54', color: '#93c5fd' },
  { label: 'Elevated', range: '55–69', color: '#60a5fa' },
  { label: 'High', range: '70–84', color: '#2563eb' },
  { label: 'Very High', range: '85+', color: '#1d4ed8' }
]

const activeLegend = computed(() => activeMode.value === 'uv' ? uvLegend : cancerLegend)

const stateStatsMap = computed(() => {
  return new Map(
    stateStats.value.map((row) => [stateCodeFromName(row.state), row])
  )
})

const stateUvMap = computed(() => {
  return new Map(
    stateUvRows.value.map((row) => [row.code, row])
  )
})

const selectedStateSummary = computed(() => stateStatsMap.value.get(selectedState.value) || null)
const selectedStateUv = computed(() => stateUvMap.value.get(selectedState.value) || null)

const selectedStateName = computed(() => {
  const found = stateOptions.find((item) => item.code === selectedState.value)
  return found ? found.name : selectedState.value
})

const latestComparisonRows = computed(() => {
  if (!comparisonRows.value.length) return []

  const latestYear = Math.max(...comparisonRows.value.map((row) => Number(row.year) || 0))
  const filtered = comparisonRows.value.filter((row) => Number(row.year) === latestYear)

  const uniqueMap = new Map()
  filtered.forEach((row) => {
    uniqueMap.set(row.state, row)
  })

  return Array.from(uniqueMap.values()).sort(
    (a, b) => (Number(b.age_standardised_rate) || 0) - (Number(a.age_standardised_rate) || 0)
  )
})

const uvComparisonRows = computed(() => {
  return [...stateUvRows.value]
    .filter((row) => Number.isFinite(Number(row.uv)))
    .sort((a, b) => (Number(b.uv) || 0) - (Number(a.uv) || 0))
})

const actPoint = computed(() => {
  if (!actAnnotation) return null
  return projectCoordinates(actAnnotation.longitude, actAnnotation.latitude)
})

function getUvLevel(uv) {
  const num = Number(uv)

  if (!Number.isFinite(num)) {
    return {
      label: 'Unknown',
      advice: 'UV data is not available right now.',
      className: 'uv-unknown'
    }
  }

  if (num <= 2) {
    return {
      label: 'Low',
      advice: 'Minimal protection required for most people.',
      className: 'uv-low'
    }
  }

  if (num <= 5) {
    return {
      label: 'Moderate',
      advice: 'Use sunscreen, sunglasses, and basic sun protection.',
      className: 'uv-moderate'
    }
  }

  if (num <= 7) {
    return {
      label: 'High',
      advice: 'Reduce midday exposure and use stronger sun protection.',
      className: 'uv-high'
    }
  }

  if (num <= 10) {
    return {
      label: 'Very High',
      advice: 'Seek shade, wear sunscreen, and limit direct exposure.',
      className: 'uv-very-high'
    }
  }

  return {
    label: 'Extreme',
    advice: 'Avoid direct sun exposure where possible.',
    className: 'uv-extreme'
  }
}

function getCancerLevel(rate) {
  const num = Number(rate)

  if (!Number.isFinite(num)) return '#e5e7eb'
  if (num < 40) return '#dbeafe'
  if (num < 55) return '#93c5fd'
  if (num < 70) return '#60a5fa'
  if (num < 85) return '#2563eb'
  return '#1d4ed8'
}

function getStateFill(code) {
  if (activeMode.value === 'uv') {
    const uv = Number(stateUvMap.value.get(code)?.uv)

    if (!Number.isFinite(uv)) return '#e5e7eb'
    if (uv <= 2) return '#1f9d55'
    if (uv <= 5) return '#f2e94e'
    if (uv <= 7) return '#f39c34'
    if (uv <= 10) return '#ef3340'
    return '#a23fa3'
  }

  return getCancerLevel(stateStatsMap.value.get(code)?.avg_incidence_rate)
}

function getStateLabelValue(code) {
  if (activeMode.value === 'uv') {
    return `UV ${formatShortUv(stateUvMap.value.get(code)?.uv)}`
  }
  return formatRate(stateStatsMap.value.get(code)?.avg_incidence_rate)
}

async function loadStateUv() {
  const results = await Promise.all(
    stateOptions.map(async (state) => {
      try {
        const response = await getRealtimeUV(state.lat, state.lon)
        return {
          code: state.code,
          name: state.name,
          uv: response?.current?.uv_index ?? null,
          temperature: response?.current?.temperature_2m ?? null
        }
      } catch (err) {
        console.error(`UV fetch failed for ${state.code}`, err)
        return {
          code: state.code,
          name: state.name,
          uv: null,
          temperature: null
        }
      }
    })
  )

  stateUvRows.value = results
}

async function handleStateSelect(code) {
  selectedState.value = code
  try {
    selectedStateDetails.value = await getMapStateDetails(code)
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load state details.'
  }
}

function formatRate(value) {
  const num = Number(value)
  return Number.isFinite(num) ? num.toFixed(2) : '--'
}

function formatShortUv(value) {
  const num = Number(value)
  return Number.isFinite(num) ? num.toFixed(1) : '--'
}

function formatUv(value) {
  const num = Number(value)
  return Number.isFinite(num) ? num.toFixed(2) : '--'
}

function formatTempValue(value) {
  const num = Number(value)
  return Number.isFinite(num) ? `${num.toFixed(1)}°C` : '--'
}

function formatNumber(value) {
  const num = Number(value)
  return Number.isFinite(num) ? num.toLocaleString() : '--'
}

onMounted(async () => {
  try {
    const [states, comparison] = await Promise.all([
      getMapStates(),
      getMapComparison()
    ])

    stateStats.value = Array.isArray(states) ? states : []
    comparisonRows.value = Array.isArray(comparison) ? comparison : []

    await Promise.all([
      handleStateSelect(selectedState.value),
      loadStateUv()
    ])
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load map analytics.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.map-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 36px 24px 60px;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f5ec 0%, #f4efe3 100%);
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.5fr 0.85fr;
  gap: 24px;
  margin-bottom: 24px;
}

.hero-card,
.map-card,
.info-card,
.status-card {
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 28px;
  box-shadow: 0 14px 34px rgba(31, 47, 86, 0.05);
}

.hero-card {
  padding: 32px;
}

.eyebrow {
  margin: 0;
  color: #df6a3b;
  font-size: 0.82rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-weight: 700;
}

.hero-card h1,
.hero-card h2,
.card-header h2,
.info-card h3 {
  color: #1f3d73;
  margin: 10px 0 12px;
}

.hero-card h1 {
  font-size: 2.8rem;
  line-height: 1.05;
  font-weight: 500;
}

.hero-text,
.summary-subtext,
.card-description,
.comparison-row p {
  color: #4d6288;
  line-height: 1.7;
}

.summary-stack {
  display: grid;
  gap: 18px;
  margin-top: 12px;
}

.summary-mini-label {
  margin: 0 0 6px;
  color: #4d6288;
  font-size: 0.9rem;
  font-weight: 600;
}

.summary-number {
  margin: 0;
  font-size: 3rem;
  color: #2563eb;
  font-weight: 700;
}

.summary-number.small {
  font-size: 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.35fr 0.8fr;
  gap: 24px;
}

.map-card,
.info-card {
  padding: 28px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: end;
  margin-bottom: 18px;
}

.right-controls {
  display: grid;
  gap: 14px;
  min-width: 260px;
}

.toggle-bar {
  display: flex;
  background: #fff7ea;
  border: 1px solid #eadfc7;
  border-radius: 16px;
  padding: 4px;
}

.toggle-btn {
  flex: 1;
  border: none;
  background: transparent;
  color: #4d6288;
  font-weight: 700;
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: #1f3d73;
  color: #ffffff;
}

.control-box label {
  display: block;
  margin-bottom: 8px;
  color: #1f3d73;
  font-size: 0.9rem;
  font-weight: 600;
}

.control-box select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e6d9bf;
  border-radius: 14px;
  background: #fffdf7;
  color: #1f3d73;
}

.map-shell {
  background: #fffdf7;
  border: 1px solid #eadfc7;
  border-radius: 22px;
  padding: 16px;
}

.map-svg {
  width: 100%;
  height: auto;
  display: block;
}

.state-path {
  stroke: #f8f5ec;
  stroke-width: 2;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease, filter 0.2s ease;
}

.state-path:hover,
.state-path.hovered {
  opacity: 0.88;
  filter: brightness(1.03);
}

.state-path.selected {
  stroke: #1f3d73;
  stroke-width: 4;
}

.state-label {
  fill: #1f3d73;
  font-size: 18px;
  font-weight: 700;
  text-anchor: middle;
}

.state-value {
  fill: #2f3e5c;
  font-size: 16px;
  font-weight: 700;
  text-anchor: middle;
}

.act-dot {
  fill: #1f3d73;
}

.legend-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 18px;
  margin-top: 18px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f3d73;
  font-size: 0.92rem;
}

.legend-swatch {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1px solid rgba(31, 61, 115, 0.12);
}

.side-column {
  display: grid;
  gap: 24px;
}

.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin: 14px 0 20px;
}

.metric-box {
  padding: 16px;
  background: #fffdf7;
  border: 1px solid #eadfc7;
  border-radius: 18px;
}

.metric-label {
  display: block;
  color: #4d6288;
  margin-bottom: 6px;
  font-size: 0.9rem;
}

.metric-box strong {
  display: block;
  color: #1f3d73;
  font-size: 1.2rem;
  margin-bottom: 4px;
}

.metric-box small {
  color: #607395;
}

.advice-box {
  margin-bottom: 20px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid #eadfc7;
  background: #fffdf7;
}

.advice-title {
  margin: 0 0 8px;
  color: #1f3d73;
  font-weight: 700;
}

.advice-text {
  margin: 0;
  color: #2f3e5c;
  line-height: 1.6;
}

.uv-low {
  border-left: 6px solid #1f9d55;
}

.uv-moderate {
  border-left: 6px solid #f2e94e;
}

.uv-high {
  border-left: 6px solid #f39c34;
}

.uv-very-high {
  border-left: 6px solid #ef3340;
}

.uv-extreme {
  border-left: 6px solid #a23fa3;
}

.uv-unknown {
  border-left: 6px solid #94a3b8;
}

.details-table-wrap {
  max-height: 360px;
  overflow: auto;
  border: 1px solid #eadfc7;
  border-radius: 18px;
  background: #fffdf7;
}

.details-table {
  width: 100%;
  border-collapse: collapse;
}

.details-table th,
.details-table td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid #f0e7d6;
}

.details-table th {
  position: sticky;
  top: 0;
  background: #fff7ea;
  color: #1f3d73;
  font-weight: 700;
}

.details-table td {
  color: #2f3e5c !important;
  font-weight: 500 !important;
  opacity: 1 !important;
}

.comparison-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
  max-height: 420px;
  overflow: auto;
}

.comparison-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid #eadfc7;
  border-radius: 16px;
  background: #fffdf7;
}

.comparison-row p {
  margin: 4px 0 0;
  font-size: 0.92rem;
}

.comparison-row strong,
.comparison-right strong,
.comparison-right span {
  color: #1f2f56;
}

.comparison-right {
  text-align: right;
  display: grid;
  gap: 4px;
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

@media (max-width: 1100px) {
  .hero-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .right-controls {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .map-page {
    padding: 24px 16px 40px;
  }

  .hero-card h1 {
    font-size: 2.2rem;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>