<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col">
    <!-- Header -->
    <header class="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-30">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <router-link to="/dashboard" class="flex items-center gap-2.5 font-bold text-slate-900 dark:text-white">
          <i class="fa-solid fa-arrow-left text-slate-400 hover:text-sky-500 transition-colors"></i>
          <span>Volver al Dashboard</span>
        </router-link>
        <ThemeToggle />
      </div>
    </header>

    <!-- Contenedor Principal -->
    <main class="flex-1 max-w-4xl mx-auto w-full px-4 py-8">
      <div v-if="loading" class="text-center py-16 text-slate-400">
        <i class="fa-solid fa-spinner fa-spin text-3xl mb-3"></i>
        <p class="text-sm">Cargando disponibilidad de la sede...</p>
      </div>

      <div v-else-if="sede" class="space-y-6">
        <!-- Tarjeta Informativa de la Sede -->
        <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div class="flex items-start justify-between">
            <div>
              <span class="text-xs font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400">Sede Seleccionada</span>
              <h1 class="text-2xl font-black mt-1">{{ sede.nombre }}</h1>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1"><i class="fa-solid fa-location-dot mr-1"></i>{{ sede.direccion }}</p>
            </div>
            <div class="text-right">
              <span class="text-xs text-slate-400">Tarifa por hora</span>
              <div class="text-2xl font-black text-emerald-600 dark:text-emerald-400">S/. {{ (sede.tarifa_hora || 5).toFixed(2) }}</div>
            </div>
          </div>
        </div>

        <!-- Paso 1: Selección de Cajón / Espacio -->
        <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <h2 class="text-base font-bold mb-2">1. Selecciona tu Espacio</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400 mb-4">Haz clic sobre un espacio libre para reservarlo:</p>

          <div class="grid grid-cols-3 sm:grid-cols-6 md:grid-cols-8 gap-2.5">
            <button
              v-for="esp in espacios"
              :key="esp.id"
              :disabled="esp.estado !== 'libre'"
              @click="espacioSeleccionado = esp"
              type="button"
              class="p-3 rounded-xl border text-center transition-all flex flex-col items-center justify-center gap-1"
              :class="{
                'bg-sky-500 text-white border-sky-400 ring-2 ring-sky-500 shadow-md': espacioSeleccionado?.id === esp.id,
                'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 border-emerald-300 dark:border-emerald-500/40 hover:scale-105': esp.estado === 'libre' && espacioSeleccionado?.id !== esp.id,
                'bg-rose-50 dark:bg-rose-950/20 text-rose-400 border-rose-200 dark:border-rose-900/40 opacity-40 cursor-not-allowed': esp.estado === 'ocupado',
                'bg-amber-50 dark:bg-amber-950/20 text-amber-500 border-amber-200 dark:border-amber-900/40 opacity-50 cursor-not-allowed': esp.estado === 'reservado',
              }"
            >
              <span class="text-xs font-black">{{ esp.numero }}</span>
              <i class="fa-solid fa-car text-sm"></i>
            </button>
          </div>
        </div>

        <!-- Paso 2: Configuración de Fecha y Horario -->
        <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <h2 class="text-base font-bold mb-4">2. Horario de Reserva</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">Fecha y Hora de Inicio</label>
              <input
                v-model="fechaInicio"
                type="datetime-local"
                class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">Fecha y Hora de Fin</label>
              <input
                v-model="fechaFin"
                type="datetime-local"
                class="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
              />
            </div>
          </div>

          <!-- Selector de Vehículo -->
          <div class="mt-4">
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1">Vehículo Asociado</label>
            <div class="flex gap-2">
              <select
                v-model="placaSeleccionada"
                class="flex-1 px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
              >
                <option value="">Selecciona tu vehículo registrado...</option>
                <option v-for="v in misVehiculos" :key="v.id" :value="v.placa">
                  {{ v.placa }} — {{ v.marca }} {{ v.modelo }}
                </option>
              </select>
              <input
                v-if="misVehiculos.length === 0"
                v-model="placaManual"
                type="text"
                placeholder="O escribe tu placa (ej: ABC-123)"
                class="w-48 px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm uppercase font-mono"
              />
            </div>
          </div>
        </div>

        <!-- Botón Continuar al Pago -->
        <div class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span class="text-xs text-slate-400">Total Estimado</span>
            <div class="text-2xl font-black text-sky-600 dark:text-sky-400">S/. {{ totalEstimado.toFixed(2) }}</div>
          </div>
          <button
            @click="crearReserva"
            :disabled="!espacioSeleccionado || procesando"
            class="px-8 py-3 bg-sky-600 hover:bg-sky-500 disabled:opacity-40 text-white font-bold rounded-xl shadow-lg shadow-sky-600/25 flex items-center gap-2"
          >
            <i v-if="procesando" class="fa-solid fa-spinner fa-spin"></i>
            <span>Continuar al Pago</span>
            <i class="fa-solid fa-arrow-right text-xs"></i>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { usuariosService } from '@/services/usuarios'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const loading = ref(true)
const procesando = ref(false)
const sede = ref(null)
const espacios = ref([])
const misVehiculos = ref([])
const espacioSeleccionado = ref(null)
const placaSeleccionada = ref('')
const placaManual = ref('')

const ahora = new Date()
const defaultInicio = new Date(ahora.getTime() + 10 * 60000).toISOString().slice(0, 16)
const defaultFin = new Date(ahora.getTime() + 130 * 60000).toISOString().slice(0, 16)

const fechaInicio = ref(defaultInicio)
const fechaFin = ref(defaultFin)

const totalEstimado = computed(() => {
  const tarifa = sede.value?.tarifa_hora || 5
  return tarifa * 2
})

onMounted(async () => {
  themeStore.initTheme(false) // Claro por default
  const sedeId = route.query.sede_id || 1
  await cargarSede(sedeId)
})

const cargarSede = async (id) => {
  loading.value = true
  try {
    const sResp = await estacionamientosService.getSede(id)
    sede.value = sResp.data

    const eResp = await estacionamientosService.getEspaciosPorSede(id, 0, 100)
    espacios.value = Array.isArray(eResp.data) ? eResp.data : (eResp.data?.data || [])

    const vResp = await usuariosService.getMisVehiculos()
    misVehiculos.value = vResp.data || []
    if (misVehiculos.value.length > 0) {
      placaSeleccionada.value = misVehiculos.value[0].placa
    }
  } catch (err) {
    showToast('Error cargando detalles de la sede', 'error')
  } finally {
    loading.value = false
  }
}

const crearReserva = async () => {
  if (!espacioSeleccionado.value) {
    showToast('Por favor selecciona un espacio libre', 'warning')
    return
  }
  const placa = placaSeleccionada.value || placaManual.value || 'PARTICULAR'
  procesando.value = true
  try {
    const payload = {
      usuario_id: authStore.user?.id || 1,
      espacio_id: espacioSeleccionado.value.id,
      fecha_inicio: new Date(fechaInicio.value).toISOString(),
      fecha_fin: new Date(fechaFin.value).toISOString(),
      monto_pago: totalEstimado.value,
      metodo_pago: 'tarjeta',
      placa_vehiculo: placa
    }
    const res = await reservasService.crearReserva(payload)
    const reservaId = res.data?.id
    showToast('¡Pre-reserva creada! Procede a completar el pago', 'success')
    router.push(`/pago?reserva_id=${reservaId}`)
  } catch (err) {
    showToast(err.response?.data?.detail || 'No se pudo crear la reserva', 'error')
  } finally {
    procesando.value = false
  }
}
</script>
