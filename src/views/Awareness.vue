<template>
  <div class="awareness-page">
    <section class="hero-section">
      <div class="hero-left">
        <p class="eyebrow">UV AWARENESS DASHBOARD</p>
        <h1>Skin Cancer Awareness</h1>
        <p class="hero-text">
          Explore long-term melanoma trends in Australia and understand how risk
          changes across years and age groups.
        </p>
      </div>

      <div class="hero-summary">
        <p class="card-label">WHY THIS MATTERS</p>
        <ul>
          <li>Australia has very high UV exposure</li>
          <li>Melanoma risk increases over time</li>
          <li>Early protection reduces long-term harm</li>
        </ul>
      </div>
    </section>

    <div v-if="loading" class="status-card">
      <p>Loading data...</p>
    </div>

    <div v-else-if="error" class="status-card error-card">
      <p>{{ error }}</p>
    </div>

    <section v-else class="content-grid">
      <div class="charts-column">
        <section class="chart-card">
          <div class="card-header">
            <p class="eyebrow">TREND OVER TIME</p>
            <h2>Melanoma Incidence vs Mortality</h2>
            <p class="card-description">
              This chart compares how melanoma incidence and mortality rates
              have changed across the years in Australia.
            </p>
          </div>

          <div class="chart-wrap">
            <Line :data="lineData" :options="lineOptions" />
          </div>
        </section>

        <section class="chart-card">
          <div class="card-header">
            <p class="eyebrow">AGE RISK</p>
            <h2>Melanoma Risk by Age Group</h2>
            <p class="card-description">
              Melanoma risk generally rises with age due to cumulative UV
              exposure over time.
            </p>
          </div>

          <div class="chart-wrap">
            <Bar :data="barData" :options="barOptions" />
          </div>
        </section>

        <section class="insight-card">
          <p class="eyebrow">KEY INSIGHT</p>
          <p class="insight-text">
            Melanoma incidence in Australia has increased over time due to high UV exposure. 
            Although mortality has remained relatively stable thanks to improved detection and treatment, prevention remains essential. 
            Building safe sun habits early can significantly reduce long-term skin cancer risk.
          </p>
        </section>
      </div>

      <aside class="sidebar-card">
        <div class="sidebar-sticky">
          <p class="eyebrow">COMMON UV MYTHS</p>
          <h3>Myth vs Fact</h3>
          <p class="sidebar-intro">
            Many young people underestimate UV risk. These common misconceptions
            can lead to unsafe sun habits.
          </p>

          <div class="myth-item">
            <p class="myth-label">Myth</p>
            <p class="myth-text">Cloudy days don’t cause sunburn.</p>
            <p class="fact-label">Fact</p>
            <p class="fact-text">
              UV rays can still pass through clouds and damage the skin.
            </p>
          </div>

          <div class="myth-item">
            <p class="myth-label">Myth</p>
            <p class="myth-text">Sunscreen is only needed at the beach.</p>
            <p class="fact-label">Fact</p>
            <p class="fact-text">
              UV exposure happens whenever you are outdoors, even during daily
              activities.
            </p>
          </div>

          <div class="myth-item">
            <p class="myth-label">Myth</p>
            <p class="myth-text">Sunburn only happens in summer.</p>
            <p class="fact-label">Fact</p>
            <p class="fact-text">
              Australia experiences harmful UV radiation all year round.
            </p>
          </div>

          <div class="tip-box">
            <p class="tip-title">Sun Safety Tip</p>
            <p class="tip-text">
              Sun protection is recommended whenever the UV Index is 3 or above.
            </p>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import Papa from 'papaparse'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Line, Bar } from 'vue-chartjs'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  BarElement,
  CategoryScale,
  LinearScale
)

const incidenceData = ref([])
const mortalityData = ref([])
const loading = ref(true)
const error = ref('')

const incidenceCsv =
  '../../filtered_datasets/aihw-can-122-CDiA-2023-Book-1a-Cancer-incidence-age-standardised-rates-5-year-age-groups__melanoma_of_the_skin.csv'

const mortalityCsv =
  '../../filtered_datasets/aihw-can-122-CDiA-2023-Book-2a-Cancer-mortality-and-age-standardised-rates-by-age-5-year-groups__melanoma_of_the_skin.csv'

function loadCSV(path) {
  return new Promise((resolve, reject) => {
    Papa.parse(path, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => resolve(results.data),
      error: (err) => reject(err)
    })
  })
}

onMounted(async () => {
  try {
    const [incidence, mortality] = await Promise.all([
      loadCSV(incidenceCsv),
      loadCSV(mortalityCsv)
    ])

    incidenceData.value = incidence
    mortalityData.value = mortality
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load data.'
  } finally {
    loading.value = false
  }
})

const RATE = 'Age-specific rate (per 100,000)'
const AGE = 'Age group (years)'
const SEX = 'Sex'
const YEAR = 'Year'

const lineData = computed(() => {
  const incidence = incidenceData.value
    .filter((r) => r[AGE] === 'All ages combined' && r[SEX] === 'Persons')
    .sort((a, b) => Number(a[YEAR]) - Number(b[YEAR]))

  const mortality = mortalityData.value
    .filter((r) => r[AGE] === 'All ages combined' && r[SEX] === 'Persons')
    .sort((a, b) => Number(a[YEAR]) - Number(b[YEAR]))

  return {
    labels: incidence.map((r) => r[YEAR]),
    datasets: [
      {
        label: 'Incidence',
        data: incidence.map((r) => Number(r[RATE]) || 0),
        borderColor: '#e36a3a',
        backgroundColor: '#e36a3a',
        borderWidth: 3,
        pointRadius: 2,
        pointHoverRadius: 4,
        tension: 0.35
      },
      {
        label: 'Mortality',
        data: mortality.map((r) => Number(r[RATE]) || 0),
        borderColor: '#1f3d73',
        backgroundColor: '#1f3d73',
        borderWidth: 3,
        pointRadius: 2,
        pointHoverRadius: 4,
        tension: 0.35
      }
    ]
  }
})

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false
  },
  plugins: {
    legend: {
      position: 'top',
      align: 'start',
      labels: {
        color: '#1f2f56',
        usePointStyle: true,
        padding: 18,
        font: {
          size: 12,
          weight: '600'
        }
      }
    },
    tooltip: {
      backgroundColor: '#fffdf7',
      titleColor: '#1f2f56',
      bodyColor: '#4d6288',
      borderColor: '#e5d8bf',
      borderWidth: 1,
      padding: 12
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#607395',
        maxTicksLimit: 8
      },
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true,
      ticks: {
        color: '#607395'
      },
      title: {
        display: true,
        text: 'Rate per 100,000',
        color: '#1f2f56',
        font: {
          size: 12,
          weight: '600'
        }
      },
      grid: {
        color: 'rgba(31, 47, 86, 0.08)',
        drawBorder: false
      }
    }
  }
}

const ageOrder = [
  '00–04',
  '05–09',
  '10–14',
  '15–19',
  '20–24',
  '25–29',
  '30–34',
  '35–39',
  '40–44',
  '45–49',
  '50–54',
  '55–59',
  '60–64',
  '65–69',
  '70–74',
  '75–79',
  '80–84',
  '85–89',
  '90+'
]

const barData = computed(() => {
  const latestYear = Math.max(
    ...incidenceData.value.map((r) => Number(r[YEAR])).filter((n) => !Number.isNaN(n))
  )

  const rows = incidenceData.value
    .filter(
      (r) =>
        Number(r[YEAR]) === latestYear &&
        r[SEX] === 'Persons' &&
        ageOrder.includes(r[AGE])
    )
    .sort((a, b) => ageOrder.indexOf(a[AGE]) - ageOrder.indexOf(b[AGE]))

  return {
    labels: rows.map((r) => r[AGE]),
    datasets: [
      {
        label: 'Incidence rate',
        data: rows.map((r) => Number(r[RATE]) || 0),
        backgroundColor: '#f0b84b',
        borderRadius: 8,
        borderSkipped: false,
        maxBarThickness: 28
      }
    ]
  }
})

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: '#fffdf7',
      titleColor: '#1f2f56',
      bodyColor: '#4d6288',
      borderColor: '#e5d8bf',
      borderWidth: 1,
      padding: 12
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#607395',
        maxRotation: 45,
        minRotation: 45
      },
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true,
      ticks: {
        color: '#607395'
      },
      title: {
        display: true,
        text: 'Rate per 100,000',
        color: '#1f2f56',
        font: {
          size: 12,
          weight: '600'
        }
      },
      grid: {
        color: 'rgba(31, 47, 86, 0.08)',
        drawBorder: false
      }
    }
  }
}
</script>

<style scoped>
.awareness-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 36px 24px 60px;
  background: linear-gradient(180deg, #f8f5ec 0%, #f4efe3 100%);
  min-height: 100vh;
}

.hero-section {
  display: grid;
  grid-template-columns: 1.5fr 0.9fr;
  gap: 24px;
  align-items: stretch;
  margin-bottom: 28px;
}

.hero-left,
.hero-summary,
.chart-card,
.insight-card,
.status-card,
.sidebar-card {
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 28px;
  box-shadow: 0 14px 34px rgba(31, 47, 86, 0.05);
}

.hero-left {
  padding: 36px;
}

.hero-summary {
  padding: 28px;
}

.hero-summary ul {
  margin: 14px 0 0;
  padding-left: 20px;
  color: #607395;
  line-height: 1.9;
}

.eyebrow,
.card-label {
  margin: 0 0 8px;
  font-size: 0.92rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: #df6a3b;
  text-transform: uppercase;
}

.hero-left h1 {
  margin: 0 0 14px;
  font-size: 3.4rem;
  line-height: 1;
  color: #1f3d73;
}

.hero-text {
  margin: 0;
  max-width: 720px;
  color: #5f7394;
  font-size: 1.08rem;
  line-height: 1.8;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: start;
}

.charts-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-card,
.insight-card,
.status-card,
.sidebar-card {
  padding: 28px;
}

.card-header {
  margin-bottom: 18px;
}

.card-header h2 {
  margin: 0 0 10px;
  font-size: 2rem;
  color: #1f3d73;
  line-height: 1.12;
}

.card-description {
  margin: 0;
  color: #607395;
  line-height: 1.7;
  max-width: 760px;
}

.chart-wrap {
  position: relative;
  height: 360px;
}

.sidebar-sticky {
  position: sticky;
  top: 24px;
}

.sidebar-card h3 {
  margin: 0 0 10px;
  font-size: 1.8rem;
  color: #1f3d73;
}

.sidebar-intro {
  margin: 0 0 20px;
  color: #607395;
  line-height: 1.7;
}

.myth-item {
  padding: 16px 0;
  border-top: 1px solid #eadfca;
}

.myth-item:first-of-type {
  border-top: none;
  padding-top: 4px;
}

.myth-label,
.fact-label {
  margin: 0 0 6px;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.myth-label {
  color: #df6a3b;
}

.fact-label {
  color: #1f3d73;
  margin-top: 12px;
}

.myth-text,
.fact-text {
  margin: 0;
  color: #5f7394;
  line-height: 1.7;
}

.tip-box {
  margin-top: 20px;
  padding: 18px;
  border-radius: 18px;
  background: #fff5de;
  border: 1px solid #f0ddb0;
}

.tip-title {
  margin: 0 0 8px;
  font-weight: 700;
  color: #1f3d73;
}

.tip-text,
.insight-text {
  margin: 0;
  color: #5f7394;
  line-height: 1.8;
}

.error-card {
  border-color: #efb5b5;
}

@media (max-width: 1100px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .sidebar-sticky {
    position: static;
  }
}

@media (max-width: 980px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .hero-left h1 {
    font-size: 2.8rem;
  }
}

@media (max-width: 768px) {
  .awareness-page {
    padding: 24px 16px 40px;
  }

  .hero-left,
  .hero-summary,
  .chart-card,
  .insight-card,
  .status-card,
  .sidebar-card {
    border-radius: 22px;
    padding: 22px;
  }

  .hero-left h1 {
    font-size: 2.3rem;
  }

  .card-header h2,
  .sidebar-card h3 {
    font-size: 1.45rem;
  }

  .chart-wrap {
    height: 300px;
  }
}
</style>