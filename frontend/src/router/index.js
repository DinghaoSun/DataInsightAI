import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Datasets from '../views/Datasets.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/datasets',
    name: 'Datasets',
    component: Datasets,
  },
  {
    path: '/datasets/:id',
    name: 'DatasetDetail',
    component: () => import('../views/DatasetDetail.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router