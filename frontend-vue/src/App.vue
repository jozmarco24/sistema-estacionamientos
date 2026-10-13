<template>
  <div class="min-h-screen">
    <router-view />
    <ToastAlert />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import ToastAlert from '@/components/ToastAlert.vue'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.applyTheme()
})
</script>
