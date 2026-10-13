<template>
  <div class="fixed top-5 right-5 z-50 flex flex-col gap-2 pointer-events-none">
    <transition-group name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto px-4 py-3 rounded-xl shadow-lg border text-sm font-medium flex items-center gap-3 min-w-[280px] max-w-md backdrop-blur-md transition-all"
        :class="{
          'bg-emerald-950/90 border-emerald-500/40 text-emerald-200': toast.type === 'success',
          'bg-rose-950/90 border-rose-500/40 text-rose-200': toast.type === 'error',
          'bg-amber-950/90 border-amber-500/40 text-amber-200': toast.type === 'warning',
          'bg-sky-950/90 border-sky-500/40 text-sky-200': toast.type === 'info',
        }"
      >
        <i :class="{
          'fa-solid fa-circle-check text-emerald-400': toast.type === 'success',
          'fa-solid fa-circle-xmark text-rose-400': toast.type === 'error',
          'fa-solid fa-triangle-exclamation text-amber-400': toast.type === 'warning',
          'fa-solid fa-circle-info text-sky-400': toast.type === 'info',
        }"></i>
        <span class="flex-1">{{ toast.message }}</span>
        <button @click="remove(toast.id)" class="opacity-60 hover:opacity-100">
          <i class="fa-solid fa-xmark text-xs"></i>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { ref } from 'vue'

const toasts = ref([])
let idCounter = 0

export const showToast = (message, type = 'info', duration = 4000) => {
  const id = ++idCounter
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, duration)
}

export default {
  setup() {
    const remove = (id) => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }
    return { toasts, remove }
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease-out;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}
</style>
