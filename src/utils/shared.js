import { ref } from "vue";

export async function fetchWeather() {
  const loading = ref(false);


  const currentUv = ref(null);
  const error = ref(null);
  loading.value = true
  error.value = ''
  const position = await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject);
  });

  const { latitude, longitude } = position.coords;


  try {
    const url =
      `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}` +
      `&current=uv_index` +
      `&hourly=uv_index` +
      `&daily=uv_index_max,temperature_2m_max,temperature_2m_min` +
      `&timezone=auto`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Failed to fetch weather data.');
    }

    const data = await response.json();

    currentUv.value = data.current?.uv_index ?? null;

    return {currentUv};
    
  } catch (err) {
    error.value = err.message || 'Something went wrong.';
  } finally {
    loading.value = false;
  }
}


export async function getWeatherData(apiKey) {
  
  // Step 1: Get current geolocation
  const position = await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject);
  });

  const { latitude, longitude } = position.coords;

  // Step 2: Fetch weather data from OpenWeather
  const url = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&units=metric&appid=${apiKey}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch weather data");
  }

  const data = await response.json();

  console.log(data);

  // Step 3: Extract required fields
  return {
    latitude,
    longitude,
    temperature: data.main.temp,
    weatherDescription: data.weather[0].description
  };
}
