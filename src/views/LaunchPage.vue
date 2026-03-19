<template>
  <div class="launch-page">

    <!-- Title Section -->
    <section class="header">
      <h1>UV Guardian</h1>
      <p class="subtitle">
        A platform to understand UV exposure, skin cancer risk, and how to protect yourself in Australia.
      </p>
    </section>

    <!-- About Section -->
    <section class="about">
      <h2>About This Website</h2>
      <p>
        Australia has one of the highest skin cancer rates in the world.
        Many people underestimate how dangerous daily UV exposure can be.
      </p>
      <p>
        UV Guardian helps users explore UV conditions, understand health risks,
        and take simple actions like using sunscreen and wearing protective clothing.
      </p>
    </section>

    <!-- Navigation Section -->
    <section class="navigation">
      <h2>Go to Pages</h2>

      <div class="button-grid">
        <button @click="goTo('/home')">Home</button>
        <button @click="goTo('/map')">UV Map</button>
        <button @click="goTo('/awareness')">Awareness</button>
        <button @click="goTo('/clothes')">Clothing</button>
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
  padding: 40px 20px;
  background: #f4f8fb;
  font-family: Arial, sans-serif;
  color: #1f2937;
}

/* Header */
.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  font-size: 42px;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 18px;
  color: #555;
}

/* About */
.about {
  max-width: 800px;
  margin: 0 auto 40px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

.about h2 {
  margin-bottom: 15px;
}

.about p {
  line-height: 1.7;
  margin-bottom: 10px;
}

/* Navigation */
.navigation {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.navigation h2 {
  margin-bottom: 20px;
}

/* Buttons */
.button-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

button {
  padding: 18px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 10px;
  background: #2563eb;
  color: white;
  cursor: pointer;
  transition: 0.3s;
}

button:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}

/* Mobile */
@media (max-width: 600px) {
  .button-grid {
    grid-template-columns: 1fr;
  }
}
</style>