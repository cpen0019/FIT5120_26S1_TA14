<template>
  <div class="launch-page">
    <section class="hero">
      <div class="hero-content">
        <p class="eyebrow">UV Guardian</p>
        <h1 class="hero-title">Protect Yourself from Australia’s UV Risk</h1>
        <p class="hero-description">
          Australia has one of the highest skin cancer rates in the world.
          UV Guardian helps users understand UV exposure, explore cancer trends,
          and take protective action through simple, practical insights.
        </p>

        <div class="hero-actions">
          <button class="primary-btn" @click="goTo('/home')">Get Started</button>
          <button class="secondary-btn" @click="goTo('/uv-map')">Explore UV Map</button>
        </div>
      </div>

      <div class="hero-panel">
        <div class="info-card highlight-card">
          <h3>Why this matters</h3>
          <p>
            Many people underestimate daily UV exposure. This platform turns raw
            environmental and health data into useful actions for regular users.
          </p>
        </div>

        <div class="stats-grid">
          <div class="mini-stat">
            <h4>UV Forecast</h4>
            <p>Check short-term UV trends and risk levels.</p>
          </div>
          <div class="mini-stat">
            <h4>UV Map</h4>
            <p>View region-based exposure patterns across Australia.</p>
          </div>
          <div class="mini-stat">
            <h4>Skin Cancer</h4>
            <p>Understand cancer impact through visual analytics.</p>
          </div>
          <div class="mini-stat">
            <h4>Protection Tips</h4>
            <p>Get sunscreen and clothing guidance.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="navigation-section">
      <div class="section-header">
        <h2>Explore the Platform</h2>
        <p>Choose any section below to navigate through the application.</p>
      </div>

      <div class="nav-grid">
        <div class="nav-card" @click="goTo('/home')">
          <h3>Home Dashboard</h3>
          <p>View a summary of UV conditions, quick highlights, and project purpose.</p>
          <span>Open Page</span>
        </div>

        <div class="nav-card" @click="goTo('/uv-forecast')">
          <h3>UV Forecast</h3>
          <p>Check forecasted UV levels and understand short-term sun risk.</p>
          <span>Open Page</span>
        </div>

        <div class="nav-card" @click="goTo('/uv-map')">
          <h3>UV Map</h3>
          <p>Explore map-based UV exposure information across different regions.</p>
          <span>Open Page</span>
        </div>

        <div class="nav-card" @click="goTo('/impact')">
          <h3>Impact Analytics</h3>
          <p>Analyze skin cancer trends and understand the broader health impact.</p>
          <span>Open Page</span>
        </div>

        <div class="nav-card" @click="goTo('/customization')">
          <h3>Customization</h3>
          <p>Personalize the experience based on user needs and safety preferences.</p>
          <span>Open Page</span>
        </div>

        <div class="nav-card" @click="goTo('/sunscreen')">
          <h3>Sunscreen Guide</h3>
          <p>Get help with sunscreen usage, reapplication, and amount needed.</p>
          <span>Open Page</span>
        </div>

        <div class="nav-card" @click="goTo('/clothing')">
          <h3>Clothing Advice</h3>
          <p>See what kind of clothing is more suitable for UV protection.</p>
          <span>Open Page</span>
        </div>

        <div class="nav-card" @click="goTo('/about')">
          <h3>Quick Facts</h3>
          <p>Learn key facts about UV radiation, health risks, and prevention.</p>
          <span>Open Page</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.launch-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f4f9ff 0%, #eef6ff 50%, #ffffff 100%);
  color: #1f2937;
  padding: 40px 24px 60px;
  box-sizing: border-box;
}

.hero {
  max-width: 1300px;
  margin: 0 auto 60px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 32px;
  align-items: stretch;
}

.hero-content,
.hero-panel {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 24px;
  box-shadow: 0 15px 40px rgba(31, 41, 55, 0.08);
  padding: 36px;
}

.eyebrow {
  display: inline-block;
  margin-bottom: 12px;
  padding: 8px 14px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 700;
  font-size: 0.9rem;
  letter-spacing: 0.4px;
}

.hero-title {
  font-size: 3rem;
  line-height: 1.1;
  margin: 0 0 18px;
  color: #0f172a;
}

.hero-description {
  font-size: 1.08rem;
  line-height: 1.8;
  color: #475569;
  max-width: 680px;
  margin-bottom: 28px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 14px;
  padding: 14px 24px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.28s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.25);
}

.primary-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.32);
}

.secondary-btn {
  background: white;
  color: #1d4ed8;
  border: 1px solid #cbd5e1;
}

.secondary-btn:hover {
  transform: translateY(-3px);
  background: #eff6ff;
}

.highlight-card {
  margin-bottom: 22px;
  background: linear-gradient(135deg, #eff6ff, #f8fbff);
  border: 1px solid #dbeafe;
  border-radius: 20px;
  padding: 24px;
}

.highlight-card h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #0f172a;
  font-size: 1.3rem;
}

.highlight-card p {
  margin: 0;
  line-height: 1.7;
  color: #475569;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.mini-stat {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 20px;
  transition: all 0.28s ease;
}

.mini-stat:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.mini-stat h4 {
  margin: 0 0 10px;
  font-size: 1rem;
  color: #0f172a;
}

.mini-stat p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
  font-size: 0.95rem;
}

.navigation-section {
  max-width: 1300px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 30px;
}

.section-header h2 {
  font-size: 2rem;
  margin-bottom: 10px;
  color: #0f172a;
}

.section-header p {
  color: #64748b;
  font-size: 1rem;
  margin: 0;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 22px;
}

.nav-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
  border-radius: 22px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.nav-card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 18px 34px rgba(15, 23, 42, 0.12);
  border-color: #93c5fd;
}

.nav-card h3 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #0f172a;
  font-size: 1.15rem;
}

.nav-card p {
  margin: 0 0 18px;
  color: #64748b;
  line-height: 1.7;
  font-size: 0.96rem;
}

.nav-card span {
  font-weight: 700;
  color: #2563eb;
  font-size: 0.95rem;
}

@media (max-width: 1100px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 700px) {
  .launch-page {
    padding: 24px 16px 40px;
  }

  .hero-content,
  .hero-panel {
    padding: 24px;
  }

  .hero-title {
    font-size: 2.2rem;
  }

  .stats-grid,
  .nav-grid {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-direction: column;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
  }
}
</style>