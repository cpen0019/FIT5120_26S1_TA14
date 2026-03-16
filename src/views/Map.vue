<template>
  <div class="map-page">
    <section class="hero-grid">
      <div class="hero-card">
        <p class="eyebrow">REGIONAL CANCER VIEW</p>
        <h1>Australia Skin Cancer Map</h1>
        <p class="hero-text">
          Explore melanoma burden across Australian states and territories.
          The map uses backend data from your local API, not hardcoded values.
        </p>
      </div>

      <div class="hero-card summary-card">
        <p class="eyebrow">SELECTED REGION</p>
        <h2>{{ selectedStateName }}</h2>
        <p class="summary-number">{{ formatRate(selectedStateSummary?.avg_incidence_rate) }}</p>
        <p class="summary-label">Average incidence rate</p>
        <p class="summary-subtext">
          Total cases: {{ formatNumber(selectedStateSummary?.total_cases) }}
        </p>
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
            <h2>State-level melanoma comparison</h2>
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

        <div class="map-shell">
          <svg
            class="map-svg"
            :viewBox="`0 0 ${mapViewport.width} ${mapViewport.height}`"
            role="img"
            aria-label="Australia melanoma map"
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
                  {{ formatShortRate(stateStatsMap.get(feature.code)?.avg_incidence_rate) }}
                </text>
              </template>
            </g>

            <g v-if="actPoint">
              <circle :cx="actPoint.x" :cy="actPoint.y" r="7" class="act-dot" />
              <text :x="actPoint.x + 14" :y="actPoint.y - 10" class="state-label">ACT</text>
              <text :x="actPoint.x + 14" :y="actPoint.y + 16" class="state-value">
                {{ formatShortRate(stateStatsMap.get('ACT')?.avg_incidence_rate) }}
              </text>
            </g>
          </svg>
        </div>

        <div class="legend-panel">
          <div class="legend-item" v-for="item in legendItems" :key="item.label">
            <span class="legend-swatch" :style="{ background: item.color }"></span>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </section>

      <aside class="side-column">
        <section class="info-card">
          <p class="eyebrow">STATE DETAILS</p>
          <h3>{{ selectedStateName }}</h3>
          <div class="metric-grid">
            <div class="metric-box">
              <span class="metric-label">Avg incidence</span>
              <strong>{{ formatRate(selectedStateSummary?.avg_incidence_rate) }}</strong>
            </div>
            <div class="metric-box">
              <span class="metric-label">Total cases</span>
              <strong>{{ formatNumber(selectedStateSummary?.total_cases) }}</strong>
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

        <section class="info-card">
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
import { getMapStates, getMapStateDetails, getMapComparison } from '../lib/api'

const hoveredStateCode = ref('')
const selectedState = ref('VIC')
const loading = ref(true)
const error = ref('')

const stateStats = ref([])
const comparisonRows = ref([])
const selectedStateDetails = ref([])

const featurePaths = buildGeoFeaturePaths(australiaStatesGeoJson)

const stateOptions = [
  { code: 'NSW', name: 'New South Wales' },
  { code: 'VIC', name: 'Victoria' },
  { code: 'QLD', name: 'Queensland' },
  { code: 'SA', name: 'South Australia' },
  { code: 'WA', name: 'Western Australia' },
  { code: 'TAS', name: 'Tasmania' },
  { code: 'NT', name: 'Northern Territory' },
  { code: 'ACT', name: 'Australian Capital Territory' }
]

const stateStatsMap = computed(() => {
  return new Map(
    stateStats.value.map((row) => [stateCodeFromName(row.state), row])
  )
})

const selectedStateSummary = computed(() => stateStatsMap.value.get(selectedState.value) || null)

const selectedStateName = computed(() => {
  const found = stateOptions.find((item) => item.code === selectedState.value)
  return found ? found.name : selectedState.value
})

const latestComparisonRows = computed(() => {
  if (!comparisonRows.value.length) return []

  const latestYear = Math.max(...comparisonRows.value.map((row) => Number(row.year) || 0))
  return comparisonRows.value
    .filter((row) => Number(row.year) === latestYear)
    .sort((a, b) => (Number(b.age_standardised_rate) || 0) - (Number(a.age_standardised_rate) || 0))
})

const actPoint = computed(() => {
  if (!actAnnotation) return null
  return projectCoordinates(actAnnotation.longitude, actAnnotation.latitude)
})

const legendItems = [
  { label: 'Very low', color: '#dbeafe' },
  { label: 'Low', color: '#93c5fd' },
  { label: 'Moderate', color: '#60a5fa' },
  { label: 'High', color: '#2563eb' },
  { label: 'Very high', color: '#1d4ed8' }
]

function getStateFill(code) {
  const rate = Number(stateStatsMap.value.get(code)?.avg_incidence_rate)

  if (!Number.isFinite(rate)) return '#e5e7eb'
  if (rate < 40) return '#dbeafe'
  if (rate < 55) return '#93c5fd'
  if (rate < 70) return '#60a5fa'
  if (rate < 85) return '#2563eb'
  return '#1d4ed8'
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

function formatShortRate(value) {
  const num = Number(value)
  return Number.isFinite(num) ? num.toFixed(1) : '--'
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
    selectedStateDetails.value = await getMapStateDetails(selectedState.value)
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
.summary-label,
.summary-subtext,
.comparison-row p {
  color: #4d6288;
  line-height: 1.7;
}

.summary-number {
  margin: 8px 0 4px;
  font-size: 3rem;
  color: #2563eb;
  font-weight: 700;
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

.control-box {
  min-width: 220px;
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
  fill: #4d6288;
  font-size: 16px;
  font-weight: 600;
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
  color: #1f3d73;
  font-size: 1.2rem;
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
}

.comparison-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
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

.comparison-right {
  text-align: right;
  color: #1f3d73;
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