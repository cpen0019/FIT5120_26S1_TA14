<script setup>
import { computed, ref } from 'vue'

const selectedState = ref('VIC')
const hoveredState = ref(null)
const tooltip = ref({ visible: false, x: 0, y: 0, state: null })

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
    advice: 'Hat, sunglasses, sunscreen, and midday care recommended.',
    peakTime: '12:00 PM - 2:00 PM',
    temp: '24 C',
    path: 'M72 201 L105 133 L191 102 L255 114 L292 145 L297 187 L278 251 L219 344 L206 396 L145 416 L94 391 L71 333 L56 270 L58 234 Z',
    labelX: 150,
    labelY: 255,
  },
  {
    code: 'NT',
    name: 'Northern Territory',
    uv: 8.3,
    risk: 'Very High',
    summary: 'Strong UV intensity across central and northern regions.',
    advice: 'Minimise direct exposure during midday hours.',
    peakTime: '11:00 AM - 2:30 PM',
    temp: '31 C',
    path: 'M255 114 L356 102 L429 112 L428 198 L295 199 L297 187 L292 145 Z',
    labelX: 342,
    labelY: 150,
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
    path: 'M219 344 L278 251 L295 199 L428 198 L439 311 L410 382 L333 415 L248 408 L206 396 Z',
    labelX: 320,
    labelY: 300,
  },
  {
    code: 'QLD',
    name: 'Queensland',
    uv: 8.9,
    risk: 'Very High',
    summary: 'Very high UV across much of Queensland.',
    advice: 'Avoid prolonged sun exposure around midday.',
    peakTime: '10:30 AM - 2:30 PM',
    temp: '30 C',
    path: 'M429 112 L510 92 L577 110 L624 170 L639 231 L620 287 L592 332 L525 343 L484 313 L439 311 L428 198 Z',
    labelX: 536,
    labelY: 196,
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
    path: 'M439 311 L484 313 L525 343 L587 378 L575 437 L522 453 L463 445 L422 404 L410 382 Z',
    labelX: 505,
    labelY: 382,
  },
  {
    code: 'VIC',
    name: 'Victoria',
    uv: 2.4,
    risk: 'Low',
    summary: 'Relatively lower UV compared to northern states.',
    advice: 'Protection still recommended around midday.',
    peakTime: '11:30 AM - 1:30 PM',
    temp: '20 C',
    path: 'M410 382 L422 404 L463 445 L438 481 L382 484 L346 447 L333 415 Z',
    labelX: 403,
    labelY: 438,
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
    path: 'M437 554 L468 540 L492 553 L489 583 L462 594 L434 580 L427 564 Z',
    labelX: 460,
    labelY: 566,
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
    path: 'M505 398 L514 398 L514 407 L505 407 Z',
    labelX: 530,
    labelY: 403,
  },
]

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

const selectedStateData = computed(() => {
  return stateData.find((s) => s.code === selectedState.value) || stateData[0]
})

function handleMouseEnter(state, event) {
  hoveredState.value = state.code
  tooltip.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    state,
  }
}

function handleMouseMove(state, event) {
  tooltip.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    state,
  }
}

function handleMouseLeave() {
  hoveredState.value = null
  tooltip.value.visible = false
}

function handleClick(state) {
  selectedState.value = state.code
}
</script>

<template>
  <section class="map-page">
    <div class="hero">
      <div class="hero-copy">
        <p class="eyebrow">UV Forecast Map</p>
        <h1>Australia UV map</h1>
        <p class="lede">
          State-wise UV view with hover details. This is cleaner, simpler, and much closer to the
          Bureau of Meteorology style.
        </p>
      </div>

      <div class="summary-card">
        <p class="card-title">Map mode</p>
        <ul>
          <li><strong>Scope:</strong> State-wise only</li>
          <li><strong>Interaction:</strong> Hover for quick info, click for details</li>
          <li><strong>Data:</strong> Frontend demo data</li>
        </ul>
      </div>
    </div>

    <div class="workspace">
      <div class="map-shell">
        <div class="map-header">
          <div>
            <p class="eyebrow small">Australia map</p>
            <h2>Average UV by state</h2>
          </div>
        </div>

        <div class="map-board">
          <svg viewBox="0 0 700 620" class="map-svg" aria-label="Australia UV map by state">
            <rect x="0" y="0" width="700" height="620" rx="20" fill="#f6f6f2" />

            <g>
              <path
                d="M72 201 L105 133 L191 102 L356 102 L510 92 L577 110 L624 170 L639 231 L620 287 L587 378 L575 437 L522 453 L489 583 L462 594 L434 580 L438 481 L382 484 L346 447 L248 408 L145 416 L94 391 L71 333 L56 270 L58 234 Z"
                fill="#f0efe8"
                stroke="#5e5a52"
                stroke-width="2"
              />
            </g>

            <g>
              <path
                v-for="state in stateData"
                :key="state.code"
                :d="state.path"
                :fill="getUvColor(state.uv)"
                :stroke="selectedState === state.code ? '#17365c' : '#777164'"
                :stroke-width="selectedState === state.code ? 4 : 1.6"
                class="state-shape"
                @mouseenter="handleMouseEnter(state, $event)"
                @mousemove="handleMouseMove(state, $event)"
                @mouseleave="handleMouseLeave"
                @click="handleClick(state)"
              />
            </g>

            <g>
              <text
                v-for="state in stateData"
                :key="`${state.code}-label`"
                :x="state.labelX"
                :y="state.labelY"
                text-anchor="middle"
                dominant-baseline="middle"
                :fill="getTextColor(state.uv)"
                class="state-label"
              >
                {{ state.code }}
              </text>
            </g>

            <g class="legend-box">
              <text x="565" y="55" class="legend-title">UV Index</text>

              <g v-for="(item, index) in uvLegend" :key="item.label">
                <rect
                  :x="575"
                  :y="72 + index * 38"
                  width="16"
                  height="28"
                  :fill="item.color"
                />
                <text :x="600" :y="90 + index * 38" class="legend-text">
                  {{ item.label }}
                </text>
                <text :x="650" :y="90 + index * 38" class="legend-range">
                  {{ item.range }}
                </text>
              </g>
            </g>
          </svg>
        </div>
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
              <span>Risk Level</span>
              <strong>{{ selectedStateData.risk }}</strong>
            </div>
          </div>

          <div class="description-box">
            <p><strong>Summary:</strong> {{ selectedStateData.summary }}</p>
            <p><strong>Advice:</strong> {{ selectedStateData.advice }}</p>
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
      </aside>
    </div>

    <div
      v-if="tooltip.visible && tooltip.state"
      class="hover-tooltip"
      :style="{ left: `${tooltip.x + 14}px`, top: `${tooltip.y + 14}px` }"
    >
      <p class="tooltip-title">{{ tooltip.state.name }}</p>
      <p>Code: {{ tooltip.state.code }}</p>
      <p>UV: {{ tooltip.state.uv.toFixed(1) }}</p>
      <p>Risk: {{ tooltip.state.risk }}</p>
      <p>Peak: {{ tooltip.state.peakTime }}</p>
    </div>
  </section>
</template>

<style scoped>
.map-page {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f8f7f3 0%, #edf5fb 100%);
  color: #17365c;
}

.hero {
  display: grid;
  grid-template-columns: 1.7fr 0.9fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.hero-copy h1 {
  font-size: clamp(2.6rem, 6vw, 4.6rem);
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
  font-size: 0.82rem;
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
.panel {
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
.panel-label {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #d86236;
  font-weight: 800;
}

.workspace {
  display: grid;
  grid-template-columns: 1.55fr 0.95fr;
  gap: 1rem;
  align-items: start;
}

.map-shell {
  padding: 1rem;
}

.map-header h2 {
  margin: 0.2rem 0 0;
  font-size: 1.1rem;
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
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.state-shape:hover {
  opacity: 0.9;
}

.state-label {
  font-size: 0.95rem;
  font-weight: 900;
  pointer-events: none;
}

.legend-title {
  font-size: 0.95rem;
  font-weight: 800;
  fill: #102f54;
}

.legend-text,
.legend-range {
  font-size: 0.78rem;
  fill: #17365c;
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

.hover-tooltip {
  position: fixed;
  z-index: 9999;
  min-width: 180px;
  background: rgba(16, 47, 84, 0.96);
  color: white;
  padding: 0.85rem 0.95rem;
  border-radius: 0.85rem;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
  pointer-events: none;
  font-size: 0.86rem;
  line-height: 1.5;
}

.tooltip-title {
  margin: 0 0 0.4rem;
  font-weight: 800;
  font-size: 0.95rem;
}

.hover-tooltip p {
  margin: 0;
}

@media (max-width: 1100px) {
  .hero,
  .workspace {
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
}
</style>