import { defineStore } from 'pinia'
import api, { URLS } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => {
    let initialUser = null
    try {
      const rawUser = localStorage.getItem('smartpark-user')
      if (rawUser) initialUser = JSON.parse(rawUser)
    } catch (e) {
      console.warn('Error al parsear smartpark-user desde localStorage:', e)
      initialUser = null
    }

    return {
      token: localStorage.getItem('smartpark-token') || '',
      user: initialUser,
    }
  },
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
      const userStr = localStorage.getItem('smartpark-user')
      if (token && userStr) {
        this.token = token
        try {
          this.user = JSON.parse(userStr)
        } catch (e) {
          console.warn('Error al parsear user en loadFromStorage:', e)
          this.user = null
        }
      }
    }
  }
})