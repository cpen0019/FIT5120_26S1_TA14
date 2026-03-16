<!-- <template>
  <div>
    <h2>UV Index: {{ UV.value }}</h2>
    <button @click="getRecommendation">Get Clothing Recommendation</button>

    <div v-if="loading">Loading...</div>
    <div v-if="recommendation" v-html="recommendation"></div>
  </div>
</template> -->

<template>
  <div class="uv-dashboard">

    <!-- Header Section -->
    <section class="uv-header">
      <h1 class="uv-title">UV Index</h1>
      <p class="uv-value">{{ UV.value }}</p>
    </section>

    <!-- Action Button -->
    <button class="uv-button" @click="getRecommendation">
      Get Clothing Recommendation
    </button>

    <!-- Loading State -->
    <div v-if="loading" class="uv-loading">
      Loading...
    </div>

    <!-- Recommendation Card -->
    <div v-if="recommendation" class="uv-card" v-html="recommendation"></div>

  </div>
</template>

<style>
.uv-dashboard {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
  font-family: "Inter", sans-serif;
  color: #1a1a1a;
}

.uv-header {
  background: #f5f8ff;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.uv-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 6px 0;
  color: #1e3a8a; /* deep blue */
}

.uv-value {
  font-size: 32px;
  font-weight: 700;
  color: #ea580c; /* warm orange */
}

.uv-button {
  background: #1e3a8a;
  color: white;
  padding: 12px 18px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background 0.2s ease;
}

.uv-button:hover {
  background: #334fb3;
}

.uv-loading {
  font-size: 16px;
  color: #475569;
  margin-bottom: 16px;
}

.uv-card {
  background: white;
  padding: 20px 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  line-height: 1.6;
}

</style>



<script setup>
import { ref } from "vue";
import Ollama from 'ollama/browser';
import { getWeatherData, fetchWeather } from "@/utils/shared.js";


const recommendation = ref("");
const loading = ref(false);

const weather = ref(null);
const UV = fetchWeather();

console.log(UV.value);

const API_KEY = "4545a1ea0b1a261b4ff0a01083f775ab";

async function getRecommendation() {
  loading.value = true;

  weather.value = await getWeatherData(API_KEY);

  // const res = await fetch("http://localhost:11434/api/generate", {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({
  //     model: "gemma2",
  //     prompt: `Clothes recommandation when the current location is (${weather.value.latitude}, ${weather.value.longitude}), the temperature of current location is ${weather.value.temperature} celsuis degree, UV index is ${UV.value} and the current weather is ${weather.value.weatherDescription} `,
  //     stream: false
  //   })
  // });

  const prompt = `Clothes recommandation when the current location is (${weather.value.latitude}, ${weather.value.longitude}), the temperature of current location is ${weather.value.temperature} celsuis degree, UV index is ${UV.value} and the current weather is ${weather.value.weatherDescription} `;
  const response = await Ollama.chat({
  model: "gemma2",
  messages: 
    [{ "role": "user", "content": prompt }],
  stream: false
})

  recommendation.value = response.message.content;

  loading.value = false;
}
</script>