import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => {
    const saved = localStorage.getItem('smartpark-theme') || localStorage.getItem('theme')
    return {
      isDark: saved ? saved === 'dark' : true, // Default dark según requerimiento para paneles
    }
  },
  getters: {
    isLight: (state) => !state.isDark,
  },
  actions: {
    initTheme(forceDefault = null) {
      const saved = localStorage.getItem('smartpark-theme') || localStorage.getItem('theme')
      if (forceDefault !== null && !saved) {
        this.isDark = forceDefault
      }
      this.applyTheme()
    },
    setTheme(dark) {
      this.isDark = dark
      localStorage.setItem('smartpark-theme', dark ? 'dark' : 'light')
      localStorage.setItem('theme', dark ? 'dark' : 'light')
      this.applyTheme()
    },
    toggleTheme() {
      this.setTheme(!this.isDark)
    },
    applyTheme() {
      const root = document.documentElement
      const body = document.body
      if (this.isDark) {
        root.classList.add('dark')
        root.classList.remove('light-mode')
        body.classList.remove('light-mode')
      } else {
        root.classList.remove('dark')
        root.classList.add('light-mode')
        body.classList.add('light-mode')
      }
    }
  }
})

