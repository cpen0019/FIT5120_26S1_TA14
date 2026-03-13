import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Map from '../views/Map.vue'
import Awareness from '../views/Awareness.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/map', component: Map },
  { path: '/awareness', component: Awareness}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router