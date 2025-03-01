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
      path: '/transcribe',
      name: 'transcribe',
      component: () => import('../views/TranscribeView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFoundView.vue'),
    },
    { path: '/:pathMatch(.*)*', component: NotFound }, // Catch-all for 404
  ],
})

export default router
