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

      <div class="hero-card">
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

    <template v-else>
      <section class="chart-card">
        <div class="card-header">
          <p class="eyebrow">TREND OVER TIME</p>
          <h2>Melanoma Incidence vs Mortality</h2>
          <p class="card-description">
            This chart compares how melanoma incidence and mortality rates have
            changed across the years in Australia.
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
            Melanoma risk generally rises with age due to cumulative UV exposure
            over time.
          </p>
        </div>

        <div class="chart-wrap">
          <Bar :data="barData" :options="barOptions" />
        </div>
      </section>

      <section class="insight-card">
        <p class="eyebrow">KEY INSIGHT</p>
        <p class="insight-text">
          Long-term UV damage builds up over time. Understanding incidence,
          mortality, and age-based risk can help young Australians build safer
          sun habits earlier.
        </p>
      </section>
    </template>
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
  grid-template-columns: 1.6fr 0.9fr;
  gap: 24px;
  align-items: stretch;
  margin-bottom: 28px;
}

.hero-left {
  background: rgba(255, 251, 243, 0.85);
  border: 1px solid #eadfca;
  border-radius: 28px;
  padding: 36px;
  box-shadow: 0 14px 30px rgba(31, 47, 86, 0.04);
}

.hero-card {
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 28px;
  padding: 28px;
  box-shadow: 0 14px 34px rgba(31, 47, 86, 0.05);
}

.hero-card ul {
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
  font-size: 4.2rem;
  line-height: 0.95;
  color: #1f3d73;
}

.hero-text {
  margin: 0;
  max-width: 720px;
  color: #5f7394;
  font-size: 1.08rem;
  line-height: 1.8;
}

.chart-card,
.insight-card,
.status-card {
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 28px;
  padding: 28px;
  box-shadow: 0 14px 34px rgba(31, 47, 86, 0.05);
  margin-bottom: 24px;
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
  height: 380px;
}

.insight-text {
  margin: 0;
  color: #5f7394;
  line-height: 1.8;
  font-size: 1.02rem;
}

.error-card {
  border-color: #efb5b5;
}

@media (max-width: 980px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .hero-left h1 {
    font-size: 3rem;
  }
}

@media (max-width: 768px) {
  .awareness-page {
    padding: 24px 16px 40px;
  }

  .hero-left,
  .hero-card,
  .chart-card,
  .insight-card,
  .status-card {
    border-radius: 22px;
    padding: 22px;
  }

  .hero-left h1 {
    font-size: 2.4rem;
  }

  .card-header h2 {
    font-size: 1.5rem;
  }

  .chart-wrap {
    height: 300px;
  }
}
</style>