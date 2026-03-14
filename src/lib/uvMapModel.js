const MAP_WIDTH = 1000
const MAP_HEIGHT = 780
const DEGREE = Math.PI / 180

const PROJECTION_SETTINGS = {
  centerLongitude: 134,
  centerLatitude: -24.5,
  baseWidth: 800,
  baseScale: 650,
}

const UV_BANDS = [
  { max: 2, label: 'Low', color: '#2f9e44', halo: 'rgba(47, 158, 68, 0.24)', radius: 12 },
  { max: 5, label: 'Moderate', color: '#f08c00', halo: 'rgba(240, 140, 0, 0.24)', radius: 14 },
  { max: 7, label: 'High', color: '#e03131', halo: 'rgba(224, 49, 49, 0.24)', radius: 16 },
  { max: 10, label: 'Very High', color: '#9c36b5', halo: 'rgba(156, 54, 181, 0.24)', radius: 18 },
  { max: Number.POSITIVE_INFINITY, label: 'Extreme', color: '#5f3dc4', halo: 'rgba(95, 61, 196, 0.24)', radius: 20 },
]

const STATE_LABEL_POINTS = {
  WA: [121.4, -25.7],
  NT: [133.1, -19.8],
  SA: [135.2, -30.5],
  QLD: [145.5, -21.2],
  NSW: [146.8, -32.6],
  VIC: [144.8, -36.9],
  TAS: [146.7, -42.0],
}

export const mapViewport = {
  width: MAP_WIDTH,
  height: MAP_HEIGHT,
}

function mercatorY(latitude) {
  const radians = latitude * DEGREE
  return Math.log(Math.tan(Math.PI / 4 + radians / 2))
}

export function classifyUv(uvIndex) {
  const value = Number(uvIndex)
  if (!Number.isFinite(value)) {
    return {
      label: 'Unavailable',
      color: '#7c8894',
      halo: 'rgba(124, 136, 148, 0.18)',
      radius: 11,
    }
  }

  return UV_BANDS.find((band) => value <= band.max)
}

export function projectCoordinates(longitude, latitude) {
  const scale = (MAP_WIDTH / PROJECTION_SETTINGS.baseWidth) * PROJECTION_SETTINGS.baseScale
  const translateX = MAP_WIDTH / 2
  const translateY = MAP_HEIGHT / 1.9
  const centerX = PROJECTION_SETTINGS.centerLongitude * DEGREE
  const centerY = mercatorY(PROJECTION_SETTINGS.centerLatitude)

  const x = (longitude * DEGREE - centerX) * scale + translateX
  const y = (centerY - mercatorY(latitude)) * scale + translateY

  return { x, y }
}

function ringsToPath(rings) {
  return rings
    .map((ring) =>
      ring
        .map(([longitude, latitude], index) => {
          const point = projectCoordinates(longitude, latitude)
          return `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`
        })
        .join(' ') + ' Z',
    )
    .join(' ')
}

export function buildGeoFeaturePaths(geoJson) {
  return geoJson.features.map((feature) => {
    const { geometry, properties } = feature
    const path =
      geometry.type === 'Polygon'
        ? ringsToPath(geometry.coordinates)
        : geometry.coordinates.map((polygon) => ringsToPath(polygon)).join(' ')

    const code = stateCodeFromName(properties.STATE_NAME)
    const labelCoordinates = STATE_LABEL_POINTS[code]

    return {
      id: feature.id,
      name: properties.STATE_NAME,
      code,
      path,
      labelPoint: labelCoordinates
        ? projectCoordinates(labelCoordinates[0], labelCoordinates[1])
        : null,
    }
  })
}

export function buildCityMarkers(rows) {
  return rows.map((row) => {
    const severity = classifyUv(row.uv_index)
    return {
      ...row,
      point: projectCoordinates(row.longitude, row.latitude),
      severity,
      uvLevel: row.risk_category || severity.label,
      uvLabel: formatUv(row.uv_index),
      timestampLabel: formatTimestamp(row.datetime),
    }
  })
}

export function buildStateSummaries(rows) {
  const grouped = rows.reduce((result, row) => {
    const bucket = result.get(row.state) || []
    bucket.push(row)
    result.set(row.state, bucket)
    return result
  }, new Map())

  return new Map(
    Array.from(grouped.entries()).map(([state, records]) => {
      const uvValues = records.map((record) => Number(record.uv_index)).filter((value) => Number.isFinite(value))
      const averageUv =
        uvValues.length > 0 ? uvValues.reduce((sum, value) => sum + value, 0) / uvValues.length : null
      const peakUv = uvValues.length > 0 ? Math.max(...uvValues) : null
      const severity = classifyUv(averageUv)

      return [
        state,
        {
          code: state,
          averageUv,
          peakUv,
          severity,
          label: severity.label,
          uvLabel: formatUv(averageUv),
          peakLabel: formatUv(peakUv),
          locations: records.length,
        },
      ]
    }),
  )
}

export function buildSelectedSummary(record) {
  if (!record) {
    return null
  }

  const severity = classifyUv(record.uv_index)
  return {
    ...record,
    severity,
    uvLevel: record.risk_category || severity.label,
    uvLabel: formatUv(record.uv_index),
    timestampLabel: formatTimestamp(record.datetime),
  }
}

export function formatUv(value) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric.toFixed(1) : 'N/A'
}

export function formatTimestamp(value) {
  if (!value) {
    return 'Unavailable'
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }

  return parsed.toLocaleString('en-AU', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function stateCodeFromName(name) {
  const map = {
    'New South Wales': 'NSW',
    Victoria: 'VIC',
    Queensland: 'QLD',
    'South Australia': 'SA',
    'Western Australia': 'WA',
    Tasmania: 'TAS',
    'Northern Territory': 'NT',
    'Australian Capital Territory': 'ACT',
  }

  return map[name] || name
}

export const uvLegend = UV_BANDS.map(({ label, color, max }) => ({
  label,
  color,
  range: max === Number.POSITIVE_INFINITY ? '11+' : label === 'Low' ? '0-2' : label === 'Moderate' ? '3-5' : label === 'High' ? '6-7' : '8-10',
}))
