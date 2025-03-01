import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/AvatarView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/therapist',
      name: 'therapist',
      component: () => import('../views/TherapistView.vue'),
    },
    {
      path: '/therapist-dashboard',
      name: 'therapistDashboard',
      component: () => import('../views/TherapistDashboardView.vue'),
    },
    {
      path: '/transcribe',
      name: 'transcribe',
      component: () => import('../views/TranscribeView.vue'),
    },
    {
      path: '/mentalHealthScreen',
      name: 'mentalHealthScreen',
      component: () => import('../views/MentalHealthScreenView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFoundView.vue'),
    },
  ],
})

export default router