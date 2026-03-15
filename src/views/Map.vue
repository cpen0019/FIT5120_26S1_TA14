<script setup>
import { computed, ref } from 'vue'
import { actAnnotation, australiaStatesGeoJson } from '../lib/australiaStatesGeoJson'
import { buildGeoFeaturePaths, mapViewport, projectCoordinates } from '../lib/uvMapModel'

const selectedState = ref('VIC')
const hoveredStateCode = ref('')

const uvLegend = [
  { label: 'Low', range: '0-2', color: '#1f9d55' },
  { label: 'Moderate', range: '3-5', color: '#f2e94e' },
  { label: 'High', range: '6-7', color: '#f39c34' },
  { label: 'Very High', range: '8-10', color: '#ef3340' },
  { label: 'Extreme', range: '11+', color: '#a23fa3' },
]

const stateData = [
  {
    code: 'WA',
    name: 'Western Australia',
    uv: 4.2,
    risk: 'Moderate',
    summary: 'Moderate UV conditions across most of the state.',
    advice: 'Use sunscreen, sunglasses, and a hat during midday hours.',
    peakTime: '12:00 PM - 2:00 PM',
    temp: '24 C',
    cancerRate: 71,
    cancerLabel: 'Elevated',
  },
  {
    code: 'NT',
    name: 'Northern Territory',
    uv: 8.3,
    risk: 'Very High',
    summary: 'Strong UV intensity across central and northern regions.',
    advice: 'Minimise direct sun exposure around midday.',
    peakTime: '11:00 AM - 2:30 PM',
    temp: '31 C',
    cancerRate: 88,
    cancerLabel: 'High',
  },
  {
    code: 'SA',
    name: 'South Australia',
    uv: 5.1,
    risk: 'Moderate',
    summary: 'Moderate UV with some higher inland exposure.',
    advice: 'Basic sun protection is recommended.',
    peakTime: '11:30 AM - 2:00 PM',
    temp: '26 C',
    cancerRate: 67,
    cancerLabel: 'Elevated',
  },
  {
    code: 'QLD',
    name: 'Queensland',
    uv: 8.9,
    risk: 'Very High',
    summary: 'Very high UV across much of Queensland.',
    advice: 'Avoid prolonged sun exposure in peak hours.',
    peakTime: '10:30 AM - 2:30 PM',
    temp: '30 C',
    cancerRate: 96,
    cancerLabel: 'Very High',
  },
  {
    code: 'NSW',
    name: 'New South Wales',
    uv: 3.2,
    risk: 'Moderate',
    summary: 'Lower coastal UV, moderate inland UV.',
    advice: 'Use sunscreen and protective clothing.',
    peakTime: '11:00 AM - 1:30 PM',
    temp: '23 C',
    cancerRate: 61,
    cancerLabel: 'Moderate',
  },
  {
    code: 'VIC',
    name: 'Victoria',
    uv: 2.4,
    risk: 'Low',
    summary: 'Relatively lower UV compared to northern states.',
    advice: 'Light protection is still recommended around noon.',
    peakTime: '11:30 AM - 1:30 PM',
    temp: '20 C',
    cancerRate: 49,
    cancerLabel: 'Moderate',
  },
  {
    code: 'TAS',
    name: 'Tasmania',
    uv: 2.0,
    risk: 'Low',
    summary: 'Lower UV conditions overall.',
    advice: 'Light sun protection is generally enough.',
    peakTime: '11:30 AM - 1:00 PM',
    temp: '17 C',
    cancerRate: 42,
    cancerLabel: 'Lower',
  },
  {
    code: 'ACT',
    name: 'Australian Capital Territory',
    uv: 3.0,
    risk: 'Moderate',
    summary: 'Moderate UV conditions in the capital region.',
    advice: 'Standard UV protection is recommended.',
    peakTime: '11:30 AM - 1:30 PM',
    temp: '21 C',
    cancerRate: 46,
    cancerLabel: 'Lower',
  },
]

const geoFeatures = buildGeoFeaturePaths(australiaStatesGeoJson)

const projectedAct = {
  centroid: projectCoordinates(149.15, -35.45),
  lineEnd: projectCoordinates(actAnnotation.lineEnd[0], actAnnotation.lineEnd[1]),
}

const stateMap = computed(() => {
  return new Map(stateData.map((state) => [state.code, state]))
})

const selectedStateData = computed(() => {
  return stateMap.value.get(selectedState.value) || stateData[0]
})

const hoveredStateData = computed(() => {
  return stateMap.value.get(hoveredStateCode.value) || null
})

const cancerRanking = computed(() => {
  return [...stateData].sort((a, b) => b.cancerRate - a.cancerRate)
})

const maxCancerRate = computed(() => {
  return Math.max(...cancerRanking.value.map((item) => item.cancerRate), 1)
})

const highestCancerState = computed(() => cancerRanking.value[0])

const averageUv = computed(() => {
  const total = stateData.reduce((sum, state) => sum + state.uv, 0)
  return (total / stateData.length).toFixed(1)
})

const averageCancerRate = computed(() => {
  const total = stateData.reduce((sum, state) => sum + state.cancerRate, 0)
  return Math.round(total / stateData.length)
})

function getUvColor(uv) {
  if (uv <= 2) return '#1f9d55'
  if (uv <= 5) return '#f2e94e'
  if (uv <= 7) return '#f39c34'
  if (uv <= 10) return '#ef3340'
  return '#a23fa3'
}

function getTextColor(uv) {
  return uv >= 8 ? '#ffffff' : '#17365c'
}

function getCancerColor(rate) {
  if (rate < 45) return '#8fd3a8'
  if (rate < 60) return '#f2e94e'
  if (rate < 75) return '#f39c34'
  if (rate < 90) return '#ef3340'
  return '#a23fa3'
}

function stateFill(code) {
  const state = stateMap.value.get(code)
  if (!state) return '#d8d4ca'
  return getUvColor(state.uv)
}

function stateOpacity(code) {
  if (selectedState.value === code) return 0.96
  if (hoveredStateCode.value === code) return 0.92
  return 0.82
}

function stateStroke(code) {
  return selectedState.value === code || hoveredStateCode.value === code ? '#17365c' : '#6f695d'
}

function stateStrokeWidth(code) {
  return selectedState.value === code || hoveredStateCode.value === code ? 4 : 1.8
}

function cancerBarWidth(rate) {
  return `${(rate / maxCancerRate.value) * 100}%`
}

function selectState(code) {
  selectedState.value = code
}

function enterState(code) {
  hoveredStateCode.value = code
}

function leaveState() {
  hoveredStateCode.value = ''
}
</script>

<template>
  <section class="map-page">
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">UV Forecast Map</p>
        <h1>Australia UV map</h1>
        <p class="lede">
          State-wise UV view using proper map borders. Hover to preview a state and click to see
          full details.
        </p>
      </div>

      <div class="summary-card">
        <p class="card-title">Map mode</p>
        <ul>
          <li><strong>Scope:</strong> State-wise only</li>
          <li><strong>Map source:</strong> Real border data</li>
          <li><strong>Interaction:</strong> Hover and click</li>
        </ul>
      </div>
    </div>

    <div class="insight-strip">
      <section class="insight-card">
        <p class="insight-label">Highest Cancer Burden</p>
        <h3>{{ highestCancerState.name }}</h3>
        <p class="insight-value">{{ highestCancerState.cancerRate }} / 100k</p>
      </section>

      <section class="insight-card">
        <p class="insight-label">Average UV</p>
        <h3>Australia-wide</h3>
        <p class="insight-value">UV {{ averageUv }}</p>
      </section>

      <section class="insight-card">
        <p class="insight-label">Average Cancer Burden</p>
        <h3>Across States</h3>
        <p class="insight-value">{{ averageCancerRate }} / 100k</p>
      </section>
    </div>

    <div class="workspace">
      <div class="map-column">
        <div class="map-shell">
          <div class="map-header">
            <div>
              <p class="eyebrow small">Australia Map</p>
              <h2>Average UV by state</h2>
            </div>
          </div>

          <div class="map-board">
            <svg
              :viewBox="`0 0 ${mapViewport.width} ${mapViewport.height}`"
              class="map-svg"
              aria-label="Australia UV map by state"
            >
              <defs>
                <linearGradient id="oceanFill" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#f5f6f3" />
                  <stop offset="100%" stop-color="#e4edf3" />
                </linearGradient>
              </defs>

              <rect width="100%" height="100%" rx="26" fill="url(#oceanFill)" />

              <g class="states-layer">
                <path
                  v-for="feature in geoFeatures"
                  :key="feature.code"
                  :d="feature.path"
                  class="state-shape"
                  :style="{
                    fill: stateFill(feature.code),
                    opacity: stateOpacity(feature.code),
                    stroke: stateStroke(feature.code),
                    strokeWidth: stateStrokeWidth(feature.code),
                  }"
                  @mouseenter="enterState(feature.code)"
                  @mouseleave="leaveState"
                  @click="selectState(feature.code)"
                />

                <g
                  v-for="feature in geoFeatures.filter((item) => item.code !== 'ACT' && item.labelPoint)"
                  :key="`${feature.code}-label`"
                >
                  <text
                    :x="feature.labelPoint.x"
                    :y="feature.labelPoint.y - 8"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    class="state-code"
                    :fill="getTextColor(stateMap.get(feature.code)?.uv || 0)"
                  >
                    {{ feature.code }}
                  </text>

                  <text
                    :x="feature.labelPoint.x"
                    :y="feature.labelPoint.y + 18"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    class="state-uv"
                    :fill="getTextColor(stateMap.get(feature.code)?.uv || 0)"
                  >
                    UV {{ (stateMap.get(feature.code)?.uv || 0).toFixed(1) }}
                  </text>
                </g>

                <line
                  :x1="projectedAct.centroid.x"
                  :y1="projectedAct.centroid.y"
                  :x2="projectedAct.lineEnd.x"
                  :y2="projectedAct.lineEnd.y"
                  class="act-line"
                />

                <g
                  class="act-label-group"
                  @mouseenter="enterState('ACT')"
                  @mouseleave="leaveState"
                  @click="selectState('ACT')"
                >
                  <text
                    :x="projectedAct.lineEnd.x + 10"
                    :y="projectedAct.lineEnd.y - 8"
                    text-anchor="start"
                    class="state-code act-code"
                    :fill="getTextColor(stateMap.get('ACT')?.uv || 0)"
                  >
                    ACT
                  </text>

                  <text
                    :x="projectedAct.lineEnd.x + 10"
                    :y="projectedAct.lineEnd.y + 16"
                    text-anchor="start"
                    class="state-uv act-uv"
                    :fill="getTextColor(stateMap.get('ACT')?.uv || 0)"
                  >
                    UV {{ (stateMap.get('ACT')?.uv || 0).toFixed(1) }}
                  </text>
                </g>

                <g v-if="hoveredStateData" class="hover-box">
                  <rect x="655" y="70" width="255" height="142" rx="18" fill="rgba(17, 44, 73, 0.94)" />
                  <text x="676" y="100" class="hover-title">
                    {{ hoveredStateData.name }}
                  </text>
                  <text x="676" y="126" class="hover-copy">
                    Code: {{ hoveredStateData.code }}
                  </text>
                  <text x="676" y="150" class="hover-copy">
                    UV: {{ hoveredStateData.uv.toFixed(1) }} | {{ hoveredStateData.risk }}
                  </text>
                  <text x="676" y="174" class="hover-copy">
                    Peak: {{ hoveredStateData.peakTime }}
                  </text>
                  <text x="676" y="198" class="hover-copy">
                    Cancer: {{ hoveredStateData.cancerRate }} / 100k
                  </text>
                </g>

                <g class="legend-box">
                  <text x="820" y="255" class="legend-title">UV Index</text>

                  <g v-for="(item, index) in uvLegend" :key="item.label">
                    <rect :x="835" :y="275 + index * 34" width="18" height="26" :fill="item.color" />
                    <text :x="865" :y="293 + index * 34" class="legend-text">
                      {{ item.label }}
                    </text>
                    <text :x="930" :y="293 + index * 34" class="legend-range">
                      {{ item.range }}
                    </text>
                  </g>
                </g>
              </g>
            </svg>
          </div>
        </div>

        <section class="panel cancer-panel">
          <div class="panel-head">
            <p class="panel-label">Region-wise cancer burden</p>
            <span class="micro">Indicative skin cancer cases per 100,000 people</span>
          </div>

          <div class="cancer-chart">
            <div
              v-for="item in cancerRanking"
              :key="item.code"
              class="cancer-row"
              @click="selectState(item.code)"
            >
              <div class="cancer-row-head">
                <div class="cancer-state">
                  <strong>{{ item.name }}</strong>
                  <span>{{ item.code }}</span>
                </div>
                <div class="cancer-meta">
                  <strong>{{ item.cancerRate }}</strong>
                  <span>{{ item.cancerLabel }}</span>
                </div>
              </div>

              <div class="cancer-track">
                <div
                  class="cancer-fill"
                  :style="{
                    width: cancerBarWidth(item.cancerRate),
                    background: getCancerColor(item.cancerRate),
                  }"
                ></div>
              </div>
            </div>
          </div>

          <p class="prediction-note">
            This chart compares estimated regional skin cancer burden. Click any row to sync the
            state details on the right panel.
          </p>
        </section>
      </div>

      <aside class="details-column">
        <section class="panel spotlight">
          <p class="panel-label">Selected state</p>
          <h2>{{ selectedStateData.name }}</h2>
          <p class="big-metric">UV {{ selectedStateData.uv.toFixed(1) }}</p>
          <p class="risk">{{ selectedStateData.risk }}</p>

          <div class="detail-grid">
            <div class="info-box">
              <span>State Code</span>
              <strong>{{ selectedStateData.code }}</strong>
            </div>
            <div class="info-box">
              <span>Peak Time</span>
              <strong>{{ selectedStateData.peakTime }}</strong>
            </div>
            <div class="info-box">
              <span>Temperature</span>
              <strong>{{ selectedStateData.temp }}</strong>
            </div>
            <div class="info-box">
              <span>Cancer Burden</span>
              <strong>{{ selectedStateData.cancerRate }} / 100k</strong>
            </div>
          </div>

          <div class="description-box">
            <p><strong>Summary:</strong> {{ selectedStateData.summary }}</p>
            <p><strong>Advice:</strong> {{ selectedStateData.advice }}</p>
            <p><strong>Cancer Risk Level:</strong> {{ selectedStateData.cancerLabel }}</p>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <p class="panel-label">Legend</p>
            <span class="micro">UV classification</span>
          </div>

          <div class="legend-list">
            <div v-for="item in uvLegend" :key="item.label" class="legend-row">
              <div class="legend-left">
                <span class="legend-dot" :style="{ background: item.color }"></span>
                <span>{{ item.label }}</span>
              </div>
              <strong>{{ item.range }}</strong>
            </div>
          </div>
        </section>

        <section class="panel note-panel">
          <div class="panel-head">
            <p class="panel-label">Quick note</p>
            <span class="micro">Interpretation</span>
          </div>
          <p class="note-text">
            Higher UV regions generally align with higher long-term skin cancer burden, but this
            panel shows indicative regional burden only, not live clinical diagnoses.
          </p>
        </section>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.map-page {
  min-height: 100vh;
  padding: 2rem;
  background:
    radial-gradient(circle at top left, rgba(244, 230, 201, 0.45), transparent 28%),
    linear-gradient(135deg, #f8f7f3 0%, #edf5fb 100%);
  color: #17365c;
}

.hero {
  display: grid;
  grid-template-columns: 1.7fr 0.9fr;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: start;
}

.hero-copy h1 {
  font-size: clamp(2.6rem, 6vw, 4.4rem);
  line-height: 0.95;
  margin: 0.35rem 0 0.7rem;
  color: #102f54;
}

.eyebrow {
  margin: 0;
  font-size: 0.92rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #d86236;
  font-weight: 800;
}

.eyebrow.small {
  font-size: 0.8rem;
}

.lede {
  margin: 0;
  max-width: 48rem;
  font-size: 1.05rem;
  line-height: 1.6;
  color: #4b6788;
}

.summary-card,
.map-shell,
.panel,
.insight-card {
  background: rgba(255, 251, 245, 0.9);
  border: 1px solid rgba(194, 183, 156, 0.65);
  border-radius: 1.4rem;
  box-shadow: 0 10px 28px rgba(16, 47, 84, 0.08);
}

.summary-card {
  padding: 1.2rem;
}

.summary-card ul {
  margin: 0;
  padding-left: 1.1rem;
  line-height: 1.8;
  color: #496683;
}

.card-title,
.panel-label,
.insight-label {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #d86236;
  font-weight: 800;
}

.insight-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.insight-card {
  padding: 1rem 1.1rem;
}

.insight-card h3 {
  margin: 0 0 0.35rem;
  font-size: 1.15rem;
  color: #102f54;
}

.insight-value {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 900;
  color: #d86236;
}

.workspace {
  display: grid;
  grid-template-columns: 1.55fr 0.95fr;
  gap: 1rem;
  align-items: start;
}

.map-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.map-shell {
  padding: 1rem;
}

.map-header h2 {
  margin: 0.2rem 0 0;
  font-size: 1.08rem;
  color: #17365c;
}

.map-board {
  margin-top: 0.6rem;
}

.map-svg {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 1rem;
}

.state-shape {
  cursor: pointer;
  stroke-linejoin: round;
  transition: opacity 0.18s ease, stroke-width 0.18s ease, transform 0.18s ease;
}

.state-shape:hover {
  opacity: 0.95;
}

.state-code {
  font-size: 22px;
  font-weight: 900;
  letter-spacing: 0.05em;
  pointer-events: none;
}

.state-uv {
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.03em;
  pointer-events: none;
}

.act-code {
  font-size: 18px;
  pointer-events: none;
}

.act-uv {
  pointer-events: none;
}

.act-label-group {
  cursor: pointer;
}

.act-line {
  stroke: rgba(16, 42, 67, 0.75);
  stroke-width: 3;
}

.hover-title {
  fill: #ffffff;
  font-size: 20px;
  font-weight: 800;
}

.hover-copy {
  fill: rgba(255, 255, 255, 0.88);
  font-size: 17px;
}

.legend-title {
  fill: #17365c;
  font-size: 18px;
  font-weight: 800;
}

.legend-text,
.legend-range {
  fill: #17365c;
  font-size: 16px;
}

.cancer-panel {
  padding: 1.1rem;
}

.cancer-chart {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-top: 0.6rem;
}

.cancer-row {
  padding: 0.85rem 0.95rem;
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.55);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  cursor: pointer;
}

.cancer-row:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 47, 84, 0.08);
}

.cancer-row-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.6rem;
}

.cancer-state,
.cancer-meta {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.cancer-state strong,
.cancer-meta strong {
  color: #17365c;
}

.cancer-state span,
.cancer-meta span {
  font-size: 0.82rem;
  color: #55728f;
  font-weight: 700;
}

.cancer-meta {
  text-align: right;
}

.cancer-track {
  width: 100%;
  height: 14px;
  border-radius: 999px;
  background: rgba(192, 204, 216, 0.42);
  overflow: hidden;
}

.cancer-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.25s ease;
}

.prediction-note {
  margin: 0.9rem 0 0;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #55728f;
}

.details-column {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.panel {
  padding: 1.1rem;
}

.spotlight h2 {
  margin: 0 0 0.3rem;
  font-size: 1.6rem;
}

.big-metric {
  margin: 0.2rem 0;
  font-size: 2rem;
  font-weight: 900;
  color: #102f54;
}

.risk {
  margin: 0 0 0.9rem;
  color: #d86236;
  font-weight: 800;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.7rem;
  margin-bottom: 0.9rem;
}

.info-box {
  background: rgba(255, 255, 255, 0.58);
  border-radius: 0.9rem;
  padding: 0.8rem;
}

.info-box span {
  display: block;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6c84a1;
  margin-bottom: 0.2rem;
}

.info-box strong {
  color: #17365c;
}

.description-box {
  background: rgba(255, 255, 255, 0.55);
  border-radius: 0.9rem;
  padding: 0.9rem;
  line-height: 1.6;
  color: #476380;
}

.description-box p {
  margin: 0 0 0.55rem;
}

.description-box p:last-child {
  margin-bottom: 0;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.micro {
  font-size: 0.82rem;
  color: #55728f;
  font-weight: 700;
}

.legend-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.legend-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.55);
  padding: 0.8rem 0.9rem;
  border-radius: 0.9rem;
}

.legend-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.legend-dot {
  width: 1rem;
  height: 1rem;
  border-radius: 999px;
  display: inline-block;
}

.note-panel {
  background: linear-gradient(135deg, rgba(255, 251, 245, 0.95), rgba(243, 246, 251, 0.95));
}

.note-text {
  margin: 0;
  line-height: 1.65;
  color: #476380;
}

@media (max-width: 1100px) {
  .hero,
  .workspace,
  .insight-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .map-page {
    padding: 1rem;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .state-code {
    font-size: 18px;
  }

  .state-uv {
    font-size: 12px;
  }

  .cancer-row-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .cancer-meta {
    text-align: left;
  }
}
</style>