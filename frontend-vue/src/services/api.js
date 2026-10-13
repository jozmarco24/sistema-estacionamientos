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
  usuarios:        'http://localhost:8001',
  estacionamientos:'http://localhost:8002',
  reservas:        'http://localhost:8003',
  pagos:           'http://localhost:8004',
}

export default api
