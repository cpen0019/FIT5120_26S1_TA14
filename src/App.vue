<template>
  <div class="app-shell">

    <header class="navbar">

      <!-- Logo + Title -->
      <router-link to="/" class="logo-section">
        <div class="logo-box"></div>
        <div class="logo-text">
          <span>Sun</span>
          <span>Safety</span>
        </div>
      </router-link>

      <!-- Navigation -->
      <nav class="nav-menu">
        <RouterLink to="/" class="nav-item">Home</RouterLink>
        <RouterLink to="/map" class="nav-item">Map</RouterLink>
        <RouterLink to="/awareness" class="nav-item">Awareness</RouterLink>
        <RouterLink to="/clothes" class="nav-item">Clothes</RouterLink>
      </nav>

    </header>

    <main>
      <RouterView />
    </main>

  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>

.app-shell{
  min-height:100vh;
  background:#f8f5ec;
}

/* NAVBAR */

.navbar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:24px 40px;
  background:#fdf9f0;
  border-bottom:2px solid #000;
}

/* LOGO */

.logo-section{
  display:flex;
  align-items:center;
  gap:18px;
  text-decoration:none;
  color:#000;
}

.logo-box{
  width:40px;
  height:40px;
  border:3px solid #000;
  border-radius:6px;
  transform:rotate(-8deg);
}

.logo-text{
  display:flex;
  flex-direction:column;
  font-size:28px;
  font-weight:700;
  line-height:1;
}

/* NAV LINKS */

.nav-menu{
  display:flex;
  gap:40px;
}

.nav-item{
  text-decoration:none;
  color:#000;
  font-size:20px;
  font-weight:600;
  padding-bottom:4px;
  border-bottom:3px solid transparent;
}

.nav-item.router-link-active{
  border-bottom:3px solid #53c7b4;
}

main{
  padding:20px;
}

</style>