import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/AnalyticsView.vue')
    },
    {
      path: '/funds',
      name: 'funds',
      component: () => import('../views/FundsView.vue')
    },
    {
      path: '/investments',
      name: 'investments',
      component: () => import('../views/InvestmentsView.vue')
    },
    {
      path: '/market-gainers',
      name: 'market-gainers',
      component: () => import('../views/MarketGainersView.vue')
    },
    {
      path: '/memberships',
      name: 'memberships',
      component: () => import('../views/MembershipsView.vue')
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue')
    },
    {
      path: '/support',
      name: 'support',
      component: () => import('../views/SupportView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

router.beforeEach((to) => {
  const isAuthenticated = !!localStorage.getItem('auth_token')
  const isPublicRoute = to.name === 'login'

  if (!isAuthenticated && !isPublicRoute) {
    return { name: 'login' }
  } else if (isAuthenticated && isPublicRoute) {
    return { name: 'home' }
  }
})

export default router
