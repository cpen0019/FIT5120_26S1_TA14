import { createRouter, createWebHistory } from 'vue-router'

import LaunchPage from '../views/LaunchPage.vue'
import Home from '../views/Home.vue'
import Map from '../views/Map.vue'
import Awareness from '../views/Awareness.vue'
import Clothes from '../views/Clothes.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [

    {
      path: '/',
      name: 'Launch',
      component: LaunchPage
    },

    {
      path: '/home',
      name: 'Home',
      component: Home
    },

    {
      path: '/map',
      name: 'Map',
      component: Map
    },

    {
      path: '/awareness',
      name: 'Awareness',
      component: Awareness
    },

    {
      path: '/clothes',
      name: 'Clothes',
      component: Clothes
    }

  ]
})

export default router