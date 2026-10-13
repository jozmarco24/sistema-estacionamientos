import { useThemeStore } from '@/stores/theme'

export function useTheme() {
  const themeStore = useThemeStore()
  return {
    isDark: themeStore.isDark,
    toggleTheme: themeStore.toggleTheme,
    setTheme: themeStore.setTheme,
  }
}
