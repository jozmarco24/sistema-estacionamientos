// frontend-vue/src/services/api.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create()

// Interceptor request: agregar Authorization: Bearer {token}
api.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// Interceptor response: si 401 → logout y redirigir a /login
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export const URLS = {
  usuarios:         import.meta.env.VITE_API_USUARIOS         || 'http://localhost:8001',
  estacionamientos: import.meta.env.VITE_API_ESTACIONAMIENTOS || 'http://localhost:8002',
  reservas:         import.meta.env.VITE_API_RESERVAS         || 'http://localhost:8003',
  pagos:            import.meta.env.VITE_API_PAGOS            || 'http://localhost:8004',
}

export default api
