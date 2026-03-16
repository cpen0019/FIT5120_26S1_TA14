<template>
  <div class="app-shell">

    <!-- NAVBAR -->
    <header class="navbar">

      <!-- Logo + Title -->
      <router-link to="/" class="logo-section">
        <img src="@/assets/logo.png" class="logo-image" />
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

    <!-- PAGE CONTENT -->
    <main class="page-container">
      <RouterView />
    </main>

  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>

/* PAGE */

.app-shell{
  min-height:100vh;
  background:#f8f5ec;
  display:flex;
  flex-direction:column;
}

/* NAVBAR */

.navbar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:22px 40px;
  background:#fdf9f0;
  border-bottom:2px solid #111;
}

/* LOGO */

.logo-section{
  display:flex;
  align-items:center;
  gap:14px;
  text-decoration:none;
  color:#111;
}

.logo-image{
  width:44px;
  height:44px;
  object-fit:contain;
}

.logo-text{
  display:flex;
  flex-direction:column;
  font-size:24px;
  font-weight:700;
  line-height:1;
}

/* NAVIGATION */

.nav-menu{
  display:flex;
  align-items:center;
  gap:42px;
}

.nav-item{
  text-decoration:none;
  color:#111;
  font-size:20px;
  font-weight:600;
  padding-bottom:4px;
  border-bottom:3px solid transparent;
  transition:all 0.2s ease;
}

.nav-item:hover{
  color:#1f3d73;
}

.nav-item.router-link-active{
  border-bottom:3px solid #53c7b4;
  color:#1f3d73;
}

/* PAGE CONTENT */

.page-container{
  flex:1;
}

/* RESPONSIVE */

@media (max-width:900px){

  .navbar{
    flex-direction:column;
    align-items:flex-start;
    gap:18px;
    padding:20px;
  }

  .nav-menu{
    gap:22px;
    flex-wrap:wrap;
  }

  .nav-item{
    font-size:18px;
  }

}

</style>