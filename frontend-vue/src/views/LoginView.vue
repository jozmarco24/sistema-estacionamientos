<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-slate-50 dark:bg-slate-950">
    <!-- Top Theme Toggle -->
    <div class="absolute top-6 right-6 z-20">
      <ThemeToggle :show-label="true" />
    </div>

    <!-- Gradient Background Glows -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-sky-500/15 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none"></div>

    <!-- Container Card -->
    <div class="w-full max-w-md bg-white dark:bg-slate-900/90 dark:glass-card rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-8 z-10">
      <!-- Logo & Brand Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-lg shadow-sky-500/25 mb-4">
          <i class="fa-solid fa-square-parking text-2xl"></i>
        </div>
        <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">SmartPark</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Gestión Inteligente de Estacionamientos</p>
      </div>

      <!-- Mode Switch: Conductor / Empresa -->
      <div class="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-xl mb-6">
        <button
          type="button"
          @click="roleTab = 'conductor'"
          class="flex-1 py-2 text-xs font-semibold rounded-lg transition-all"
          :class="roleTab === 'conductor' 
            ? 'bg-white dark:bg-slate-700 text-sky-600 dark:text-sky-400 shadow-sm' 
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'"
        >
          <i class="fa-solid fa-car mr-1.5"></i> Conductor
        </button>
        <button
          type="button"
          @click="roleTab = 'empresa'"
          class="flex-1 py-2 text-xs font-semibold rounded-lg transition-all"
          :class="roleTab === 'empresa' 
            ? 'bg-white dark:bg-slate-700 text-sky-600 dark:text-sky-400 shadow-sm' 
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'"
        >
          <i class="fa-solid fa-building mr-1.5"></i> Empresa / Propietario
        </button>
      </div>

      <!-- Action Toggle: Iniciar Sesión / Registrarse -->
      <div class="flex justify-between items-center mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
        <h2 class="text-lg font-bold text-slate-800 dark:text-slate-100">
          {{ isRegister ? 'Crear Cuenta' : 'Iniciar Sesión' }}
        </h2>
        <button
          type="button"
          @click="toggleMode"
          class="text-xs text-sky-600 dark:text-sky-400 hover:underline font-semibold"
        >
          {{ isRegister ? '¿Ya tienes cuenta? Ingresa' : '¿No tienes cuenta? Regístrate' }}
        </button>
      </div>

      <!-- Formulario -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Nombre (solo registro) -->
        <div v-if="isRegister">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Nombre Completo
          </label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <i class="fa-regular fa-user text-sm"></i>
            </span>
            <input
              v-model="form.nombre"
              type="text"
              required
              placeholder="Juan Pérez"
              class="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 transition-colors"
            />
          </div>
        </div>

        <!-- Email -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Correo Electrónico
          </label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <i class="fa-regular fa-envelope text-sm"></i>
            </span>
            <input
              v-model="form.email"
              type="email"
              required
              placeholder="tu@correo.com"
              class="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 transition-colors"
            />
          </div>
        </div>

        <!-- Contraseña -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Contraseña
          </label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <i class="fa-solid fa-lock text-sm"></i>
            </span>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              placeholder="••••••••"
              class="w-full pl-10 pr-10 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 transition-colors"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <i :class="showPassword ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye'"></i>
            </button>
          </div>
        </div>

        <!-- Confirmación de contraseña (solo registro) -->
        <div v-if="isRegister">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
            Confirmar Contraseña
          </label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <i class="fa-solid fa-lock-open text-sm"></i>
            </span>
            <input
              v-model="form.confirmPassword"
              type="password"
              required
              placeholder="••••••••"
              class="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 transition-colors"
            />
          </div>
        </div>

        <!-- Botón Submit -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full mt-2 py-3 px-4 bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white font-bold rounded-xl shadow-lg shadow-sky-600/30 transition-all flex items-center justify-center gap-2"
        >
          <i v-if="loading" class="fa-solid fa-spinner fa-spin"></i>
          <span>{{ isRegister ? 'Crear Cuenta' : 'Iniciar Sesión' }}</span>
        </button>
      </form>

      <!-- Indicadores de Credenciales Rápidas para Demo -->
      <div v-if="!isRegister" class="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800/80 text-xs text-slate-500 dark:text-slate-400">
        <p class="font-semibold text-slate-700 dark:text-slate-300 mb-1">Accesos de demostración:</p>
        <div class="grid grid-cols-2 gap-2 text-[11px]">
          <button @click="fillCreds('admin@smartpark.com', 'Marco7057')" type="button" class="text-left p-1.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700">
            👑 Admin Global
          </button>
          <button @click="fillCreds('propietario@test.com', 'propietario123')" type="button" class="text-left p-1.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700">
            🏢 Propietario
          </button>
          <button @click="fillCreds('operador@test.com', 'operador123')" type="button" class="text-left p-1.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700">
            🅿️ Operador
          </button>
          <button @click="fillCreds('conductor@test.com', 'conductor123')" type="button" class="text-left p-1.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700">
            🚗 Conductor
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const roleTab = ref('conductor')
const isRegister = ref(false)
const showPassword = ref(false)
const loading = ref(false)

const form = ref({
  nombre: '',
  email: '',
  password: '',
  confirmPassword: ''
})

onMounted(() => {
  // En login vista clara por defecto
  themeStore.initTheme(false)
  if (route.query.mode === 'register') {
    isRegister.value = true
  }
})

const toggleMode = () => {
  isRegister.value = !isRegister.value
  router.replace({ query: isRegister.value ? { mode: 'register' } : {} })
}

const fillCreds = (email, pass) => {
  form.value.email = email
  form.value.password = pass
}

const handleSubmit = async () => {
  loading.value = true
  try {
    if (isRegister.value) {
      if (form.value.password !== form.value.confirmPassword) {
        showToast('Las contraseñas no coinciden', 'error')
        loading.value = false
        return
      }
      const rolTarget = roleTab.value === 'empresa' ? 'propietario' : 'conductor'
      await authStore.registro({
        nombre: form.value.nombre,
        email: form.value.email,
        password: form.value.password,
        rol: rolTarget
      })
      showToast('Registro exitoso. Iniciando sesión...', 'success')
    }

    // Login
    const user = await authStore.login(form.value.email, form.value.password)
    showToast(`¡Bienvenido, ${user.nombre}!`, 'success')

    // Redirigir según rol
    const rol = (user.rol || '').toLowerCase()
    if (rol === 'admin') router.push('/admin')
    else if (rol === 'propietario') router.push('/propietario')
    else if (rol === 'operador') router.push('/operador')
    else router.push('/dashboard')

  } catch (err) {
    const detail = err.response?.data?.detail || 'Error en las credenciales o en el servidor'
    showToast(typeof detail === 'string' ? detail : 'Error de autenticación', 'error')
  } finally {
    loading.value = false
  }
}
</script>
