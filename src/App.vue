<template>
  <div class="app">
    <nav class="navbar">
      <router-link to="/">Home</router-link>
      <router-link to="/map">Map</router-link>
      <router-link to="/awareness">Awareness</router-link>
    </nav>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, sans-serif;
}

.app {
  text-align: center;
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 25px;
  padding: 18px;
  background: white;
  font-size: 20px;
  border-bottom: 1px solid #eee;
}

.navbar a {
  text-decoration: none;
  padding: 8px 16px;
  color: #2c3e50;
  border-radius: 8px;
  transition: 0.2s;
}

.navbar a:hover {
  background: #f2f2f2;
}

.router-link-exact-active {
  background: #42b983;
  color: white;
}

.content {
  padding-top: 90px;
}
</style>