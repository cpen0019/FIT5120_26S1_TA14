<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'

import { actAnnotation, australiaStatesGeoJson } from '../lib/australiaStatesGeoJson'
import { buildGeoFeaturePaths, mapViewport, projectCoordinates } from '../lib/uvMapModel'

const props = defineProps({
  markers: {
    type: Array,
    default: () => [],
  },
  stateSummaries: {
    type: Object,
    default: () => new Map(),
  },
  selectedPostcode: {
    type: String,
    default: '',
  },
  selectedState: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['select', 'select-state', 'zoom-change'])

const svgRef = ref(null)
const hoveredPostcode = ref('')
const hoveredStateCode = ref('')
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const dragState = ref(null)

const geoFeatures = buildGeoFeaturePaths(australiaStatesGeoJson)

const projectedAct = {
  centroid: projectCoordinates(149.15, -35.45),
  lineEnd: projectCoordinates(actAnnotation.lineEnd[0], actAnnotation.lineEnd[1]),
}

const hoveredMarker = computed(() =>
  props.markers.find((marker) => marker.postcode === hoveredPostcode.value) || null,
)

const hoveredState = computed(() =>
  geoFeatures.find((feature) => feature.code === hoveredStateCode.value) || null,
)

const hoveredStateSummary = computed(() =>
  hoveredState.value ? props.stateSummaries.get(hoveredState.value.code) || null : null,
)

const selectedMarker = computed(() =>
  props.markers.find((marker) => marker.postcode === props.selectedPostcode) || null,
)

const mapTransform = computed(() => `translate(${pan.value.x} ${pan.value.y}) scale(${zoom.value})`)

function markerScreenPoint(marker) {
  return {
    x: marker.point.x * zoom.value + pan.value.x,
    y: marker.point.y * zoom.value + pan.value.y,
  }
}

function stateScreenPoint(stateFeature) {
  if (!stateFeature?.labelPoint) {
    return { x: 24, y: 24 }
  }

  return {
    x: stateFeature.labelPoint.x * zoom.value + pan.value.x,
    y: stateFeature.labelPoint.y * zoom.value + pan.value.y,
  }
}

function setZoom(nextZoom) {
  const clamped = Math.min(3.2, Math.max(1, Number(nextZoom.toFixed(2))))
  if (clamped === zoom.value) {
    return
  }
  zoom.value = clamped
  emit('zoom-change', zoom.value)
}

function zoomIn() {
  setZoom(zoom.value + 0.25)
}

function zoomOut() {
  setZoom(zoom.value - 0.25)
}

function resetView() {
  zoom.value = 1
  pan.value = { x: 0, y: 0 }
  emit('zoom-change', zoom.value)
}

function beginDrag(event) {
  if (event.pointerType === 'mouse' && event.button !== 0) {
    return
  }

  const rect = svgRef.value?.getBoundingClientRect()
  if (!rect) {
    return
  }

  dragState.value = {
    startClientX: event.clientX,
    startClientY: event.clientY,
    startPanX: pan.value.x,
    startPanY: pan.value.y,
    scaleX: mapViewport.width / rect.width,
    scaleY: mapViewport.height / rect.height,
  }

  svgRef.value.setPointerCapture(event.pointerId)
}

function updateDrag(event) {
  if (!dragState.value) {
    return
  }

  const deltaX = (event.clientX - dragState.value.startClientX) * dragState.value.scaleX
  const deltaY = (event.clientY - dragState.value.startClientY) * dragState.value.scaleY

  pan.value = {
    x: dragState.value.startPanX + deltaX,
    y: dragState.value.startPanY + deltaY,
  }
}

function endDrag(event) {
  if (dragState.value && svgRef.value?.hasPointerCapture(event.pointerId)) {
    svgRef.value.releasePointerCapture(event.pointerId)
  }
  dragState.value = null
}

function onWheel(event) {
  event.preventDefault()
  setZoom(zoom.value + (event.deltaY < 0 ? 0.2 : -0.2))
}

function selectMarker(marker) {
  emit('select', marker)
}

function selectState(stateCode) {
  emit('select-state', stateCode)
}

function stateFill(stateCode) {
  const summary = props.stateSummaries.get(stateCode)
  if (!summary || summary.averageUv == null) {
    return '#e7ddc7'
  }
  return summary.severity.color
}

function stateOpacity(stateCode) {
  return hoveredStateCode.value === stateCode || props.selectedState === stateCode ? 0.86 : 0.72
}

function stateStrokeWidth(stateCode) {
  return hoveredStateCode.value === stateCode || props.selectedState === stateCode ? 4 : 2.6
}

onBeforeUnmount(() => {
  dragState.value = null
})
</script>

<template>
  <div class="map-shell">
    <div class="map-toolbar">
      <div class="toolbar-copy">
        <p class="eyebrow">Prototype Map</p>
        <h2>Capital-city UV overview</h2>
      </div>

      <div class="zoom-controls">
        <button type="button" @click="zoomOut">-</button>
        <span>{{ zoom.toFixed(2) }}x</span>
        <button type="button" @click="zoomIn">+</button>
        <button type="button" class="ghost" @click="resetView">Reset</button>
      </div>
    </div>

    <div class="map-board">
      <svg
        ref="svgRef"
        class="map-svg"
        :viewBox="`0 0 ${mapViewport.width} ${mapViewport.height}`"
        role="img"
        aria-label="Australia UV forecast map"
        @pointerdown="beginDrag"
        @pointermove="updateDrag"
        @pointerup="endDrag"
        @pointercancel="endDrag"
        @pointerleave="endDrag"
        @wheel="onWheel"
      >
        <defs>
          <linearGradient id="ocean" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#eef6fb" />
            <stop offset="100%" stop-color="#bfd9eb" />
          </linearGradient>
        </defs>

        <rect width="100%" height="100%" fill="url(#ocean)" rx="34" />

        <g :transform="mapTransform">
          <g class="states-layer">
            <path
              v-for="state in geoFeatures"
              :key="state.code"
              :d="state.path"
              class="state-shape"
              :style="{ fill: stateFill(state.code), opacity: stateOpacity(state.code), strokeWidth: stateStrokeWidth(state.code) }"
              @mouseenter="hoveredStateCode = state.code"
              @mouseleave="hoveredStateCode = ''"
              @click.stop="selectState(state.code)"
            />

            <text
              v-for="state in geoFeatures.filter((feature) => feature.code !== 'ACT' && feature.labelPoint)"
              :key="`${state.code}-label`"
              :x="state.labelPoint.x"
              :y="state.labelPoint.y"
              text-anchor="middle"
              class="state-code"
            >
              {{ state.code }}
            </text>

            <line
              :x1="projectedAct.centroid.x"
              :y1="projectedAct.centroid.y"
              :x2="projectedAct.lineEnd.x"
              :y2="projectedAct.lineEnd.y"
              class="act-line"
            />
            <text
              :x="projectedAct.lineEnd.x + 10"
              :y="projectedAct.lineEnd.y - 6"
              text-anchor="start"
              class="state-code act-code"
              @click.stop="selectState('ACT')"
            >
              ACT
            </text>
          </g>

          <g v-for="marker in markers" :key="marker.postcode">
            <circle :cx="marker.point.x" :cy="marker.point.y" :r="marker.severity.radius + 10" :fill="marker.severity.halo" />
            <circle
              :cx="marker.point.x"
              :cy="marker.point.y"
              :r="marker.severity.radius"
              :fill="marker.severity.color"
              :stroke="marker.postcode === selectedPostcode ? '#102a43' : 'white'"
              :stroke-width="marker.postcode === selectedPostcode ? 7 : 4"
              class="marker"
              @mouseenter="hoveredPostcode = marker.postcode"
              @mouseleave="hoveredPostcode = ''"
              @click.stop="selectMarker(marker)"
            />
            <text :x="marker.point.x" :y="marker.point.y - marker.severity.radius - 14" text-anchor="middle" class="city-label">
              {{ marker.city }}
            </text>
          </g>
        </g>

        <g v-if="hoveredMarker && hoveredMarker.postcode !== selectedPostcode">
          <template v-for="screenPoint in [markerScreenPoint(hoveredMarker)]" :key="hoveredMarker.postcode">
            <rect :x="Math.min(screenPoint.x + 16, mapViewport.width - 210)" :y="Math.max(screenPoint.y - 62, 18)" width="190" height="54" rx="16" fill="rgba(16, 42, 67, 0.9)" />
            <text :x="Math.min(screenPoint.x + 30, mapViewport.width - 196)" :y="Math.max(screenPoint.y - 36, 44)" class="tooltip-title">
              {{ hoveredMarker.city }}, {{ hoveredMarker.state }}
            </text>
            <text :x="Math.min(screenPoint.x + 30, mapViewport.width - 196)" :y="Math.max(screenPoint.y - 14, 66)" class="tooltip-copy">
              UV {{ hoveredMarker.uvLabel }} | {{ hoveredMarker.uvLevel }}
            </text>
          </template>
        </g>

        <g v-if="hoveredState && hoveredStateSummary">
          <template v-for="screenPoint in [stateScreenPoint(hoveredState)]" :key="hoveredState.code">
            <rect :x="Math.min(screenPoint.x + 16, mapViewport.width - 250)" :y="Math.max(screenPoint.y - 72, 18)" width="230" height="68" rx="16" fill="rgba(16, 42, 67, 0.88)" />
            <text :x="Math.min(screenPoint.x + 30, mapViewport.width - 236)" :y="Math.max(screenPoint.y - 44, 42)" class="tooltip-title">
              {{ hoveredState.code }} state summary
            </text>
            <text :x="Math.min(screenPoint.x + 30, mapViewport.width - 236)" :y="Math.max(screenPoint.y - 22, 64)" class="tooltip-copy">
              Avg UV {{ hoveredStateSummary.uvLabel }} | {{ hoveredStateSummary.label }}
            </text>
            <text :x="Math.min(screenPoint.x + 30, mapViewport.width - 236)" :y="Math.max(screenPoint.y, 86)" class="tooltip-copy">
              Peak UV {{ hoveredStateSummary.peakLabel }} | {{ hoveredStateSummary.locations }} {{ hoveredStateSummary.locations === 1 ? 'location' : 'locations' }}
            </text>
          </template>
        </g>
      </svg>

      <div class="map-notes">
        <p>Drag to pan. Use mouse wheel or controls to zoom. Click a marker to load details.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-shell { display: grid; gap: 1rem; }
.map-toolbar { display: flex; justify-content: space-between; gap: 1rem; align-items: end; }
.eyebrow { margin: 0 0 0.3rem; color: #a44a17; font-size: 0.76rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; }
h2 { margin: 0; color: #102a43; font-size: clamp(1.4rem, 2vw, 2rem); }
.zoom-controls { display: flex; gap: 0.55rem; align-items: center; flex-wrap: wrap; }
button, .zoom-controls span { min-height: 42px; border-radius: 999px; }
button { border: 0; padding: 0.7rem 1rem; background: #102a43; color: white; font-weight: 700; cursor: pointer; }
.ghost { background: rgba(16, 42, 67, 0.12); color: #102a43; }
.zoom-controls span { display: inline-flex; align-items: center; padding: 0 0.9rem; background: rgba(16, 42, 67, 0.08); color: #102a43; font-weight: 700; }
.map-board { border: 1px solid rgba(16, 42, 67, 0.14); border-radius: 30px; background: rgba(255, 250, 244, 0.86); box-shadow: 0 24px 60px rgba(16, 42, 67, 0.12); overflow: hidden; }
.map-svg { display: block; width: 100%; height: auto; touch-action: none; cursor: grab; }
.map-svg:active { cursor: grabbing; }
.state-shape { stroke: #7b6540; stroke-linejoin: round; cursor: pointer; }
.state-code { fill: rgba(16, 42, 67, 0.74); font-size: 22px; font-weight: 800; letter-spacing: 0.06em; }
.act-code { font-size: 18px; }
.act-line { stroke: rgba(16, 42, 67, 0.74); stroke-width: 3; pointer-events: none; }
.marker { cursor: pointer; }
.city-label { fill: #102a43; font-size: 24px; font-weight: 700; paint-order: stroke; stroke: rgba(255, 255, 255, 0.85); stroke-width: 4px; }
.tooltip-title { fill: white; font-size: 20px; font-weight: 700; }
.tooltip-copy { fill: rgba(255, 255, 255, 0.82); font-size: 18px; }
.map-notes { padding: 0.9rem 1.2rem 1.2rem; color: #486581; font-size: 0.95rem; }
@media (max-width: 760px) {
  .map-toolbar { flex-direction: column; align-items: stretch; }
}
</style>
