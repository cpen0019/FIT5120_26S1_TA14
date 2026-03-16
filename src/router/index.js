import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Map from '../views/Map.vue'
import Awareness from '../views/Awareness.vue'
import Clothes from '../views/Clothes.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/map', component: Map },
  { path: '/awareness', component: Awareness},
  { path: '/clothes', component: Clothes}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router