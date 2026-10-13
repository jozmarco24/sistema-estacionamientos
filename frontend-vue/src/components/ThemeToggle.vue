<template>
  <button
    @click="toggleTheme"
    type="button"
    class="p-2.5 rounded-xl border transition-all duration-200 flex items-center justify-center gap-2 text-sm font-medium shadow-sm"
    :class="isDark 
      ? 'bg-slate-800/80 hover:bg-slate-700/80 border-slate-700 text-amber-400' 
      : 'bg-white hover:bg-slate-100 border-slate-200 text-slate-700'"
    title="Cambiar tema (Oscuro / Claro)"
  >
    <i :class="isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon'"></i>
    <span v-if="showLabel" class="text-xs">{{ isDark ? 'Modo Claro' : 'Modo Oscuro' }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

defineProps({
  showLabel: {
    type: Boolean,
    default: false
  }
})

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
const toggleTheme = () => themeStore.toggleTheme()
</script>
