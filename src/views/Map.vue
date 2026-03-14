<script setup>
import { computed, onMounted, ref } from 'vue'

import UvAustraliaMap from '../components/UvAustraliaMap.vue'
import { fetchCitywise, fetchHourly, fetchRealtime, fetchWeekly } from '../lib/uvApi'
import {
  buildCityMarkers,
  buildSelectedSummary,
  buildStateSummaries,
  formatTimestamp,
  uvLegend,
} from '../lib/uvMapModel'

const overviewLoading = ref(false)
const detailsLoading = ref(false)
const error = ref('')
const citywise = ref([])
const selectedState = ref('')
const selectedPostcode = ref('')
const selectedRealtime = ref(null)
const selectedHourly = ref([])
const selectedWeekly = ref([])
const detailsCache = new Map()
const currentZoom = ref(1)

const markers = computed(() => buildCityMarkers(citywise.value))
const stateSummaries = computed(() => buildStateSummaries(citywise.value))
const selectedSummary = computed(() => buildSelectedSummary(selectedRealtime.value))
const hourlyPreview = computed(() => selectedHourly.value.slice(0, 8))
const weeklyPreview = computed(() => selectedWeekly.value.slice(0, 5))

async function loadOverview() {
  overviewLoading.value = true
  error.value = ''

  try {
    citywise.value = await fetchCitywise()
    if (citywise.value.length > 0) {
      const initialMarker = buildCityMarkers(citywise.value)[0]
      selectedState.value = initialMarker.state
      await selectMarker(initialMarker)
    }
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    overviewLoading.value = false
  }
}

async function selectMarker(marker) {
  if (!marker?.postcode) {
    return
  }

  selectedPostcode.value = marker.postcode
  selectedState.value = marker.state
  error.value = ''

  if (detailsCache.has(marker.postcode)) {
    const cached = detailsCache.get(marker.postcode)
    selectedRealtime.value = cached.realtime
    selectedHourly.value = cached.hourly
    selectedWeekly.value = cached.weekly
    return
  }

  detailsLoading.value = true

  try {
    const [realtimePayload, hourlyPayload, weeklyPayload] = await Promise.all([
      fetchRealtime(marker.postcode),
      fetchHourly(marker.postcode),
      fetchWeekly(marker.postcode),
    ])

    detailsCache.set(marker.postcode, {
      realtime: realtimePayload,
      hourly: hourlyPayload,
      weekly: weeklyPayload,
    })

    selectedRealtime.value = realtimePayload
    selectedHourly.value = hourlyPayload
    selectedWeekly.value = weeklyPayload
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    detailsLoading.value = false
  }
}

function onZoomChange(value) {
  currentZoom.value = value
}

function onSelectState(stateCode) {
  selectedState.value = stateCode
  const stateMarker = markers.value.find((marker) => marker.state === stateCode)
  if (stateMarker) {
    selectMarker(stateMarker)
  }
}

onMounted(loadOverview)
</script>

<template>
  <section class="map-page">
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">UV Forecast Map Concept</p>
        <h1>Interactive Australia UV map prototype</h1>
        <p class="lede">
          This prototype separates API retrieval, map-ready data processing, and interactive rendering.
          It starts with capital-city UV markers and is structured for suburb-level expansion later.
        </p>
      </div>

      <div class="architecture-card">
        <p class="card-title">Current frontend layering</p>
        <ul>
          <li><strong>Retrieval:</strong> `src/lib/uvApi.js`</li>
          <li><strong>Processing:</strong> `src/lib/uvMapModel.js`</li>
          <li><strong>Rendering:</strong> `src/components/UvAustraliaMap.vue`</li>
        </ul>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="workspace">
      <div class="map-column">
        <div v-if="overviewLoading" class="loading-card">Loading citywise UV overview...</div>
        <UvAustraliaMap
          v-else
          :markers="markers"
          :state-summaries="stateSummaries"
          :selected-postcode="selectedPostcode"
          :selected-state="selectedState"
          @select="selectMarker"
          @select-state="onSelectState"
          @zoom-change="onZoomChange"
        />
      </div>

      <aside class="details-column">
        <section class="panel spotlight">
          <p class="panel-label">Selected location</p>
          <div v-if="selectedSummary" class="spotlight-copy">
            <h2>{{ selectedSummary.city }}, {{ selectedSummary.state }}</h2>
            <p class="big-metric">{{ selectedSummary.uvLabel }}</p>
            <p class="severity">{{ selectedSummary.uvLevel }}</p>
            <dl class="facts">
              <div>
                <dt>Postcode</dt>
                <dd>{{ selectedSummary.postcode }}</dd>
              </div>
              <div>
                <dt>Time</dt>
                <dd>{{ selectedSummary.timestampLabel }}</dd>
              </div>
              <div>
                <dt>Temperature</dt>
                <dd>{{ selectedSummary.temperature ?? 'N/A' }} C</dd>
              </div>
              <div>
                <dt>Cloud cover</dt>
                <dd>{{ selectedSummary.cloud_cover ?? 'N/A' }}%</dd>
              </div>
              <div>
                <dt>Humidity</dt>
                <dd>{{ selectedSummary.relative_humidity ?? 'N/A' }}%</dd>
              </div>
              <div>
                <dt>Coordinates</dt>
                <dd>{{ selectedSummary.latitude }}, {{ selectedSummary.longitude }}</dd>
              </div>
            </dl>
          </div>
          <p v-else class="empty">Select a marker to inspect its UV forecast details.</p>
        </section>

        <section class="panel">
          <div class="panel-head">
            <p class="panel-label">Legend</p>
            <span class="micro">Marker color + size</span>
          </div>
          <div class="legend-list">
            <div v-for="item in uvLegend" :key="item.label" class="legend-item">
              <span class="legend-dot" :style="{ background: item.color }"></span>
              <span>{{ item.label }}</span>
              <span class="legend-range">{{ item.range }}</span>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <p class="panel-label">Interaction state</p>
            <span class="micro">{{ currentZoom.toFixed(2) }}x zoom</span>
          </div>
          <p class="interaction-copy">
            Hover reveals a quick tooltip. Click loads realtime, hourly, and weekly data for the
            selected city. State polygons are now UV-colored from API-derived state summaries.
            Zooming past 2.0x is where suburb-wise loading can be attached later.
          </p>
          <div class="future-gate" :class="{ ready: currentZoom >= 2 }">
            <strong>Phase 2 hook:</strong>
            {{ currentZoom >= 2 ? 'zoom threshold reached for suburb-level requests' : 'zoom further to simulate suburb-level activation' }}
          </div>
        </section>
      </aside>
    </div>

    <div class="forecast-grid">
      <section class="panel">
        <div class="panel-head">
          <p class="panel-label">Hourly preview</p>
          <span class="micro" v-if="detailsLoading">Refreshing...</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>UV</th>
                <th>Temp</th>
                <th>Cloud</th>
                <th>Humidity</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in hourlyPreview" :key="row.datetime">
                <td>{{ formatTimestamp(row.datetime) }}</td>
                <td>{{ row.uv_index ?? 'N/A' }}</td>
                <td>{{ row.temperature ?? 'N/A' }}</td>
                <td>{{ row.cloud_cover ?? 'N/A' }}%</td>
                <td>{{ row.relative_humidity ?? 'N/A' }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <p class="panel-label">Weekly outlook</p>
          <span class="micro">{{ weeklyPreview.length }} days shown</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Sunrise</th>
                <th>Sunset</th>
                <th>UV max</th>
                <th>Min temp</th>
                <th>Max temp</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in weeklyPreview" :key="row.date">
                <td>{{ row.date }}</td>
                <td>{{ formatTimestamp(row.sunrise) }}</td>
                <td>{{ formatTimestamp(row.sunset) }}</td>
                <td>{{ row.uv_index_max ?? 'N/A' }}</td>
                <td>{{ row.temperature_2m_min ?? row.temperature_min ?? 'N/A' }}</td>
                <td>{{ row.temperature_2m_max ?? row.temperature_max ?? 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.map-page {
  --paper: rgba(255, 251, 245, 0.86);
  --ink: #102a43;
  --muted: #486581;
  --line: rgba(16, 42, 67, 0.12);
  --accent: #cf5c36;
  min-height: 100vh;
  padding: 2rem;
  background:
    radial-gradient(circle at top left, rgba(255, 201, 107, 0.26), transparent 26%),
    radial-gradient(circle at top right, rgba(74, 144, 226, 0.18), transparent 28%),
    linear-gradient(180deg, #f8f2ea 0%, #eef7fc 52%, #fbfaf5 100%);
  color: var(--ink);
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 2.3fr) minmax(280px, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.eyebrow,
.panel-label,
.card-title,
.micro {
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.eyebrow,
.panel-label,
.card-title {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 800;
}

h1 {
  margin: 0;
  max-width: 10ch;
  font-size: clamp(2.8rem, 5vw, 5rem);
  line-height: 0.94;
}

.lede {
  max-width: 62ch;
  color: var(--muted);
  font-size: 1.04rem;
}

.architecture-card,
.panel,
.loading-card {
  border: 1px solid var(--line);
  border-radius: 28px;
  background: var(--paper);
  box-shadow: 0 20px 60px rgba(16, 42, 67, 0.08);
  backdrop-filter: blur(14px);
}

.architecture-card {
  padding: 1.3rem;
}

.architecture-card ul {
  margin: 0;
  padding-left: 1.2rem;
  color: var(--muted);
}

.error {
  margin: 0 0 1rem;
  padding: 0.9rem 1rem;
  border-radius: 18px;
  background: rgba(181, 38, 38, 0.12);
  color: #8a1c1c;
  font-weight: 700;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.95fr);
  gap: 1.25rem;
  align-items: start;
}

.loading-card,
.panel {
  padding: 1.2rem;
}

.details-column {
  display: grid;
  gap: 1rem;
}

.spotlight {
  background:
    radial-gradient(circle at top right, rgba(255, 187, 92, 0.24), transparent 32%),
    var(--paper);
}

.spotlight-copy h2 {
  margin: 0;
  font-size: 1.9rem;
}

.big-metric {
  margin: 0.4rem 0 0;
  font-size: clamp(3.4rem, 6vw, 4.8rem);
  font-weight: 800;
  line-height: 1;
}

.severity {
  margin: 0.3rem 0 1rem;
  color: var(--accent);
  font-weight: 700;
}

.facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.facts div {
  padding-top: 0.55rem;
  border-top: 1px solid var(--line);
}

dt {
  color: var(--muted);
  font-size: 0.85rem;
}

dd {
  margin: 0.2rem 0 0;
  font-weight: 700;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: baseline;
}

.micro {
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 700;
}

.legend-list {
  display: grid;
  gap: 0.8rem;
}

.legend-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.75rem;
  align-items: center;
  color: var(--ink);
}

.legend-dot {
  width: 16px;
  height: 16px;
  border-radius: 999px;
}

.legend-range {
  color: var(--muted);
  font-weight: 700;
}

.interaction-copy,
.empty {
  color: var(--muted);
}

.future-gate {
  margin-top: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 18px;
  background: rgba(16, 42, 67, 0.07);
  color: var(--ink);
}

.future-gate.ready {
  background: rgba(47, 158, 68, 0.14);
}

.forecast-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
  margin-top: 1.25rem;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
}

th,
td {
  padding: 0.75rem 0.35rem;
  text-align: left;
  border-bottom: 1px solid var(--line);
}

th {
  color: var(--muted);
  font-weight: 700;
}

@media (max-width: 1100px) {
  .hero,
  .workspace,
  .forecast-grid {
    grid-template-columns: 1fr;
  }

  h1 {
    max-width: none;
  }
}

@media (max-width: 720px) {
  .map-page {
    padding: 1rem;
  }

  .facts {
    grid-template-columns: 1fr;
  }
}
</style>
