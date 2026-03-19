<template>
  <div class="launch-page">
    <!-- Background decorations -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <span class="tag">Sun Safety in Australia</span>
        <h1>UV Guardian</h1>
        <p class="subtitle">
          Understand UV exposure, explore skin cancer risk, and take practical steps
          to protect yourself with data-driven insights.
        </p>

        <div class="hero-actions">
          <button class="primary-btn" @click="goTo('/home')">Explore Dashboard</button>
          <button class="secondary-btn" @click="scrollToSections">Learn More</button>
        </div>
      </div>

      <div class="hero-stats">
        <div class="stat-card">
          <h3>UV Insights</h3>
          <p>Track UV conditions and understand when protection matters most.</p>
        </div>
        <div class="stat-card">
          <h3>Risk Awareness</h3>
          <p>Visualize skin cancer trends and build stronger awareness.</p>
        </div>
        <div class="stat-card">
          <h3>Protective Action</h3>
          <p>Get sunscreen and clothing guidance for safer outdoor activity.</p>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section class="about" ref="aboutSection">
      <div class="section-heading">
        <span class="section-label">Why this matters</span>
        <h2>About This Website</h2>
      </div>

      <div class="about-grid">
        <div class="about-card">
          <h3>The problem</h3>
          <p>
            Australia has one of the highest skin cancer rates in the world.
            Many people still underestimate how harmful daily UV exposure can be,
            even when the weather feels mild.
          </p>
        </div>

        <div class="about-card">
          <h3>The solution</h3>
          <p>
            UV Guardian helps users explore UV conditions, understand regional risk,
            and make safer choices using practical guidance backed by visual data.
          </p>
        </div>
      </div>
    </section>

    <!-- Navigation Section -->
    <section class="navigation">
      <div class="section-heading center">
        <span class="section-label">Explore the platform</span>
        <h2>Go to Pages</h2>
        <p>
          Each page focuses on a different part of UV awareness, health risk, and protection.
        </p>
      </div>

      <div class="nav-grid">
        <div class="nav-card" @click="goTo('/home')">
          <div class="icon-circle">🏠</div>
          <h3>Home</h3>
          <p>
            Start with the main dashboard and get an overview of UV safety information.
          </p>
          <span class="card-link">Open Page →</span>
        </div>

        <div class="nav-card" @click="goTo('/map')">
          <div class="icon-circle">🗺️</div>
          <h3>UV Map</h3>
          <p>
            Explore UV-related or regional health insights through visual geographic data.
          </p>
          <span class="card-link">Open Page →</span>
        </div>

        <div class="nav-card" @click="goTo('/awareness')">
          <div class="icon-circle">📊</div>
          <h3>Awareness</h3>
          <p>
            Learn about skin cancer trends, UV risk, and why prevention matters.
          </p>
          <span class="card-link">Open Page →</span>
        </div>

        <div class="nav-card" @click="goTo('/clothes')">
          <div class="icon-circle">🧢</div>
          <h3>Clothing</h3>
          <p>
            Understand how clothing choices can improve sun protection in daily life.
          </p>
          <span class="card-link">Open Page →</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const aboutSection = ref(null)

const goTo = (path) => {
  router.push(path)
}

const scrollToSections = () => {
  aboutSection.value?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.launch-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 40px 24px 80px;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 30%),
    radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.12), transparent 30%),
    linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
  font-family: Arial, sans-serif;
  color: #1f2937;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  z-index: 0;
  opacity: 0.35;
}

.shape-1 {
  width: 260px;
  height: 260px;
  background: #60a5fa;
  top: -60px;
  left: -80px;
}

.shape-2 {
  width: 320px;
  height: 320px;
  background: #38bdf8;
  bottom: -100px;
  right: -100px;
}

/* Shared */
.hero,
.about,
.navigation {
  position: relative;
  z-index: 1;
}

.section-heading {
  margin-bottom: 24px;
}

.section-heading.center {
  text-align: center;
}

.section-label {
  display: inline-block;
  margin-bottom: 10px;
  padding: 6px 12px;
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.section-heading h2 {
  font-size: 32px;
  margin: 0 0 10px;
  color: #0f172a;
}

.section-heading p {
  max-width: 680px;
  margin: 0 auto;
  color: #475569;
  line-height: 1.7;
}

/* Hero */
.hero {
  max-width: 1200px;
  margin: 0 auto 70px;
  display: grid;
  grid-template-columns: 1.2fr 0.9fr;
  gap: 32px;
  align-items: center;
  min-height: 80vh;
}

.hero-content {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  padding: 48px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
}

.tag {
  display: inline-block;
  margin-bottom: 16px;
  padding: 8px 14px;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
}

.hero-content h1 {
  font-size: 58px;
  line-height: 1.05;
  margin: 0 0 18px;
  color: #0f172a;
}

.subtitle {
  font-size: 18px;
  line-height: 1.8;
  color: #475569;
  max-width: 620px;
  margin-bottom: 28px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 14px;
  padding: 14px 24px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  color: white;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.25);
}

.primary-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 30px rgba(37, 99, 235, 0.3);
}

.secondary-btn {
  background: white;
  color: #1d4ed8;
  border: 1px solid #cbd5e1;
}

.secondary-btn:hover {
  transform: translateY(-3px);
  background: #f8fafc;
}

/* Hero stats */
.hero-stats {
  display: grid;
  gap: 18px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  padding: 26px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.1);
}

.stat-card h3 {
  margin: 0 0 10px;
  font-size: 20px;
  color: #0f172a;
}

.stat-card p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}

/* About */
.about {
  max-width: 1200px;
  margin: 0 auto 70px;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.about-card {
  background: white;
  padding: 30px;
  border-radius: 22px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
  transition: transform 0.3s ease;
}

.about-card:hover {
  transform: translateY(-5px);
}

.about-card h3 {
  margin: 0 0 14px;
  font-size: 22px;
  color: #0f172a;
}

.about-card p {
  margin: 0;
  color: #475569;
  line-height: 1.8;
}

/* Navigation */
.navigation {
  max-width: 1200px;
  margin: 0 auto;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.nav-card {
  background: white;
  padding: 30px;
  border-radius: 22px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 38px rgba(15, 23, 42, 0.11);
  border-color: #93c5fd;
}

.icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #dbeafe, #e0f2fe);
  font-size: 26px;
  margin-bottom: 18px;
}

.nav-card h3 {
  margin: 0 0 12px;
  font-size: 24px;
  color: #0f172a;
}

.nav-card p {
  margin: 0 0 20px;
  color: #475569;
  line-height: 1.75;
}

.card-link {
  font-weight: 700;
  color: #2563eb;
  font-size: 15px;
}

/* Responsive */
@media (max-width: 960px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .hero-content {
    padding: 36px 28px;
  }

  .hero-content h1 {
    font-size: 44px;
  }

  .about-grid,
  .nav-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .launch-page {
    padding: 24px 16px 60px;
  }

  .hero-content h1 {
    font-size: 36px;
  }

  .subtitle {
    font-size: 16px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
  }

  .section-heading h2 {
    font-size: 26px;
  }
}
</style>