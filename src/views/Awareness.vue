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
            Although mortality has remained relatively stable thanks to improved detection and treatment,
            prevention remains essential. Building safe sun habits early can significantly reduce long-term
            skin cancer risk.
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
              UV exposure happens whenever you are outdoors, even during daily activities.
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
import { getCancerTrends, getCancerAgeGroups } from '../lib/api'

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

const loading = ref(true)
const error = ref('')
const trendRows = ref([])
const ageRows = ref([])

onMounted(async () => {
  try {
    const [trends, ages] = await Promise.all([
      getCancerTrends(),
      getCancerAgeGroups()
    ])

    trendRows.value = Array.isArray(trends) ? trends : []
    ageRows.value = Array.isArray(ages) ? ages : []
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load cancer analytics data.'
  } finally {
    loading.value = false
  }
})

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

const sortedAgeRows = computed(() => {
  return [...ageRows.value].sort((a, b) => {
    const aIndex = ageOrder.indexOf(a.age_group)
    const bIndex = ageOrder.indexOf(b.age_group)
    if (aIndex === -1 && bIndex === -1) return String(a.age_group).localeCompare(String(b.age_group))
    if (aIndex === -1) return 1
    if (bIndex === -1) return -1
    return aIndex - bIndex
  })
})

const lineData = computed(() => ({
  labels: trendRows.value.map((row) => row.year),
  datasets: [
    {
      label: 'Incidence',
      data: trendRows.value.map((row) => Number(row.incidence_rate) || 0),
      borderColor: '#e36a3a',
      backgroundColor: '#e36a3a',
      borderWidth: 3,
      pointRadius: 2,
      pointHoverRadius: 4,
      tension: 0.35
    },
    {
      label: 'Mortality',
      data: trendRows.value.map((row) => Number(row.mortality_rate) || 0),
      borderColor: '#1f3d73',
      backgroundColor: '#1f3d73',
      borderWidth: 3,
      pointRadius: 2,
      pointHoverRadius: 4,
      tension: 0.35
    }
  ]
}))

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

const barData = computed(() => ({
  labels: sortedAgeRows.value.map((row) => row.age_group),
  datasets: [
    {
      label: 'Incidence rate',
      data: sortedAgeRows.value.map((row) => Number(row.incidence_rate) || 0),
      backgroundColor: '#f0b84b',
      borderRadius: 8,
      borderSkipped: false,
      maxBarThickness: 28
    }
  ]
}))

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
  margin-bottom: 24px;
}

.hero-left,
.hero-summary,
.chart-card,
.insight-card,
.sidebar-card,
.status-card {
  background: #fdf9f0;
  border: 1px solid #e6d9bf;
  border-radius: 28px;
  box-shadow: 0 14px 34px rgba(31, 47, 86, 0.05);
}

.hero-left {
  padding: 32px;
}

.hero-left h1 {
  margin: 10px 0 14px;
  font-size: 2.9rem;
  line-height: 1.05;
  color: #1f3d73;
  font-weight: 500;
}

.hero-text {
  margin: 0;
  max-width: 780px;
  color: #4d6288;
  font-size: 1rem;
  line-height: 1.7;
}

.hero-summary {
  padding: 28px;
}

.card-label,
.eyebrow {
  margin: 0;
  color: #df6a3b;
  font-size: 0.82rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-weight: 700;
}

.hero-summary ul {
  margin: 18px 0 0;
  padding-left: 18px;
  color: #1f2f56;
  line-height: 1.8;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.5fr 0.75fr;
  gap: 24px;
}

.charts-column {
  display: grid;
  gap: 24px;
}

.chart-card,
.insight-card,
.sidebar-card {
  padding: 28px;
}

.card-header h2 {
  margin: 10px 0 10px;
  color: #1f3d73;
  font-size: 1.45rem;
  font-weight: 600;
}

.card-description,
.sidebar-intro,
.fact-text,
.myth-text,
.insight-text,
.tip-text {
  color: #4d6288;
  line-height: 1.7;
}

.chart-wrap {
  height: 360px;
  margin-top: 18px;
}

.insight-text {
  margin-top: 12px;
}

.sidebar-sticky {
  position: sticky;
  top: 24px;
}

.sidebar-card h3 {
  margin: 10px 0;
  color: #1f3d73;
  font-size: 1.35rem;
}

.myth-item {
  margin-top: 18px;
  padding: 18px;
  border: 1px solid #eadfc7;
  border-radius: 18px;
  background: #fffdf7;
}

.myth-label,
.fact-label,
.tip-title {
  margin: 0 0 6px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #1f3d73;
  text-transform: uppercase;
}

.myth-text,
.fact-text {
  margin: 0;
}

.fact-label {
  margin-top: 12px;
  color: #df6a3b;
}

.tip-box {
  margin-top: 18px;
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fff4e5, #fffaf2);
  border: 1px solid #f0d6b2;
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
  .hero-section,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .sidebar-sticky {
    position: static;
  }
}

@media (max-width: 768px) {
  .awareness-page {
    padding: 24px 16px 40px;
  }

  .hero-left h1 {
    font-size: 2.2rem;
  }

  .chart-wrap {
    height: 300px;
  }
}
</style>