api = open('frontend-vue/src/services/api.js', 'w', encoding='utf-8')
api.write("""import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create()

api.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

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
""")
api.close()
print("OK api.js")

auth = open('frontend-vue/src/stores/auth.js', 'w', encoding='utf-8')
auth.write("""import { defineStore } from 'pinia'
import api, { URLS } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('smartpark-token') || '',
    user: JSON.parse(localStorage.getItem('smartpark-user') || 'null'),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin:         (state) => state.user?.rol === 'admin',
    isPropietario:   (state) => state.user?.rol === 'propietario',
    isOperador:      (state) => state.user?.rol === 'operador',
    isCliente:       (state) => state.user?.rol === 'conductor',
    userName:        (state) => state.user?.nombre || 'Usuario',
    userRole:        (state) => state.user?.rol || '',
  },
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('smartpark-token', token)
      localStorage.setItem('smartpark-user', JSON.stringify(user))
    },
    async login(email, password) {
      const res = await api.post(`${URLS.usuarios}/usuarios/login`, { email, password })
      const { access_token, user } = res.data
      this.setAuth(access_token, user)
      return user
    },
    async registro(data) {
      const res = await api.post(`${URLS.usuarios}/usuarios/registro`, data)
      return res.data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('smartpark-token')
      localStorage.removeItem('smartpark-user')
    },
    loadFromStorage() {
      const token = localStorage.getItem('smartpark-token')
      const user  = localStorage.getItem('smartpark-user')
      if (token && user) {
        this.token = token
        this.user  = JSON.parse(user)
      }
    }
  }
})
""")
auth.close()
print("OK auth.js")
