import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import AdminView from '@/views/admin/AdminView.vue'
import OperadorView from '@/views/OperadorView.vue'
import PropietarioView from '@/views/propietario/PropietarioView.vue'
import ReservaView from '@/views/ReservaView.vue'
import PagoView from '@/views/PagoView.vue'
import VehiculosView from '@/views/VehiculosView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/registro', redirect: '/login?mode=register' },
  { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true, roles: ['conductor'] } },
  { path: '/admin', component: AdminView, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/operador', component: OperadorView, meta: { requiresAuth: true, roles: ['operador'] } },
  { path: '/propietario', component: PropietarioView, meta: { requiresAuth: true, roles: ['propietario'] } },
  { path: '/reserva', component: ReservaView, meta: { requiresAuth: true } },
  { path: '/pago', component: PagoView, meta: { requiresAuth: true } },
  { path: '/vehiculos', component: VehiculosView, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.loadFromStorage()

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }

    if (to.meta.roles && to.meta.roles.length > 0) {
      const userRol = (authStore.user?.rol || '').toLowerCase()
      // Admin tiene acceso a todo si lo desea, pero respetamos roles específicos
      const matches = to.meta.roles.includes(userRol) || (userRol === 'admin' && to.path === '/admin')
      if (!matches) {
        if (userRol === 'admin') return next('/admin')
        if (userRol === 'propietario') return next('/propietario')
        if (userRol === 'operador') return next('/operador')
        return next('/dashboard')
      }
    }
  }

  // Si ya está logueado e intenta ir a login -> llevar a su panel
  if (to.path === '/login' && authStore.isAuthenticated) {
    const rol = (authStore.user?.rol || '').toLowerCase()
    if (rol === 'admin') return next('/admin')
    if (rol === 'propietario') return next('/propietario')
    if (rol === 'operador') return next('/operador')
    return next('/dashboard')
  }

  next()
})

export default router
