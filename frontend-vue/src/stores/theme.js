import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: localStorage.getItem('smartpark-theme') 
      ? localStorage.getItem('smartpark-theme') === 'dark' 
      : true, // Default dark según requerimiento para paneles
  }),
  actions: {
    initTheme(forceDefault = null) {
      if (forceDefault !== null && !localStorage.getItem('smartpark-theme')) {
        this.isDark = forceDefault
      }
      this.applyTheme()
    },
    setTheme(dark) {
      this.isDark = dark
      localStorage.setItem('smartpark-theme', dark ? 'dark' : 'light')
      this.applyTheme()
    },
    toggleTheme() {
      this.setTheme(!this.isDark)
    },
    applyTheme() {
      const root = document.documentElement
      if (this.isDark) {
        root.classList.add('dark')
      } else {
        root.classList.remove('dark')
      }
    }
  }
})
