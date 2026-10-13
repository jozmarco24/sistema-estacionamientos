<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col justify-between">
    <!-- Header -->
    <header class="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
      <div class="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
        <router-link to="/dashboard" class="flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-sky-600">
          <i class="fa-solid fa-arrow-left"></i> Cancelar y volver
        </router-link>
        <ThemeToggle />
      </div>
    </header>

    <!-- Main Card Checkout -->
    <main class="flex-1 flex items-center justify-center p-4">
      <div class="w-full max-w-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-xl p-8 relative overflow-hidden">
        
        <!-- Timer de cuenta regresiva (10 minutos) -->
        <div class="flex items-center justify-between p-3.5 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 text-amber-800 dark:text-amber-300 text-xs font-semibold mb-6">
          <div class="flex items-center gap-2">
            <i class="fa-solid fa-clock text-amber-500 fa-spin"></i>
            <span>Tiempo restante para completar el pago:</span>
          </div>
          <span class="font-mono font-black text-sm">{{ minutosRestantes }}:{{ segundosRestantes }}</span>
        </div>

        <div v-if="loading" class="text-center py-10 text-slate-400">
          <i class="fa-solid fa-spinner fa-spin text-2xl mb-2"></i>
          <p class="text-xs">Cargando orden de pago...</p>
        </div>

        <div v-else class="space-y-6">
          <div class="text-center">
            <h1 class="text-2xl font-black text-slate-900 dark:text-white">Checkout Seguro</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Confirma tu reserva en SmartPark</p>
          </div>

          <!-- Resumen de la Reserva -->
          <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 space-y-2.5 text-xs">
            <div class="flex justify-between">
              <span class="text-slate-500 dark:text-slate-400">Reserva ID</span>
              <strong class="font-mono text-slate-900 dark:text-white">#{{ reserva?.id }}</strong>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500 dark:text-slate-400">Espacio Asignado</span>
              <strong class="text-slate-900 dark:text-white">Cajón #{{ reserva?.espacio_id }}</strong>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500 dark:text-slate-400">Vehículo Placa</span>
              <strong class="font-mono uppercase text-slate-900 dark:text-white">{{ reserva?.placa_vehiculo || '—' }}</strong>
            </div>
            <div class="pt-2 border-t border-slate-200 dark:border-slate-700 flex justify-between items-center text-sm">
              <span class="font-bold text-slate-700 dark:text-slate-300">Total a Pagar:</span>
              <span class="text-xl font-black text-sky-600 dark:text-sky-400">S/. {{ montoTotal.toFixed(2) }}</span>
            </div>
          </div>

          <!-- Método de Pago -->
          <div class="space-y-3">
            <label class="block text-xs font-bold text-slate-600 dark:text-slate-400">Selecciona Medio de Pago:</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                @click="metodoPago = 'culqi'"
                class="p-4 rounded-xl border text-center transition-all flex flex-col items-center justify-center gap-2"
                :class="metodoPago === 'culqi' ? 'border-sky-500 bg-sky-50 dark:bg-sky-950/30 text-sky-600 ring-2 ring-sky-500' : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'"
              >
                <i class="fa-solid fa-credit-card text-xl"></i>
                <span class="text-xs font-bold">Tarjeta (Culqi)</span>
              </button>
              <button
                type="button"
                @click="metodoPago = 'efectivo'"
                class="p-4 rounded-xl border text-center transition-all flex flex-col items-center justify-center gap-2"
                :class="metodoPago === 'efectivo' ? 'border-sky-500 bg-sky-50 dark:bg-sky-950/30 text-sky-600 ring-2 ring-sky-500' : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'"
              >
                <i class="fa-solid fa-money-bill-wave text-xl"></i>
                <span class="text-xs font-bold">Efectivo en Puerta</span>
              </button>
            </div>
          </div>

          <!-- Botón de Pago -->
          <button
            @click="procesarPago"
            :disabled="pagando"
            class="w-full py-3.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-extrabold rounded-2xl shadow-lg shadow-sky-600/30 transition-all flex items-center justify-center gap-2"
          >
            <i v-if="pagando" class="fa-solid fa-spinner fa-spin"></i>
            <span>{{ metodoPago === 'culqi' ? 'Pagar con Culqi Seguro' : 'Confirmar Reserva en Efectivo' }}</span>
          </button>
        </div>
      </div>
    </main>

    <!-- Overlay Éxito Modal Ticket -->
    <div v-if="pagoExitoso" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-3xl p-8 max-w-sm w-full text-center shadow-2xl">
        <div class="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center mx-auto text-3xl mb-4">
          <i class="fa-solid fa-check"></i>
        </div>
        <h3 class="text-xl font-black text-slate-900 dark:text-white">¡Pago Exitoso!</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Tu reserva ha sido confirmada y el cajón está apartado.</p>
        
        <div class="mt-6 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-left space-y-1.5 font-mono">
          <div>Ticket: #SP-{{ reserva?.id }}-{{ Math.floor(1000 + Math.random()*9000) }}</div>
          <div>Monto: S/. {{ montoTotal.toFixed(2) }}</div>
          <div>Cajón: #{{ reserva?.espacio_id }}</div>
        </div>

        <button
          @click="irADashboard"
          class="mt-6 w-full py-3 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold"
        >
          Ir a mis reservas
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { reservasService } from '@/services/reservas'
import { pagosService } from '@/services/pagos'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const themeStore = useThemeStore()

const loading = ref(true)
const pagando = ref(false)
const pagoExitoso = ref(false)
const reserva = ref(null)
const metodoPago = ref('culqi')
const tiempoSegundos = ref(600) // 10 minutos
let timerInterval = null

const montoTotal = computed(() => {
  return reserva.value?.monto_pago || 10.00
})

const minutosRestantes = computed(() => {
  const m = Math.floor(tiempoSegundos.value / 60)
  return m < 10 ? `0${m}` : `${m}`
})

const segundosRestantes = computed(() => {
  const s = tiempoSegundos.value % 60
  return s < 10 ? `0${s}` : `${s}`
})

onMounted(async () => {
  themeStore.initTheme(false) // Claro por defecto
  const reservaId = route.query.reserva_id
  if (!reservaId) {
    showToast('ID de reserva no proporcionado', 'error')
    router.push('/dashboard')
    return
  }
  await cargarReserva(reservaId)

  // Iniciar timer
  timerInterval = setInterval(() => {
    if (tiempoSegundos.value > 0) {
      tiempoSegundos.value--
    } else {
      clearInterval(timerInterval)
      showToast('El tiempo de reserva ha expirado', 'warning')
      router.push('/dashboard')
    }
  }, 1000)

  // Configurar Culqi Checkout Callback
  window.culqi = function() {
    if (window.Culqi.token) {
      const token = window.Culqi.token.id
      completarCobroCulqi(token)
    } else {
      showToast(window.Culqi.error?.user_message || 'Error con la tarjeta', 'error')
      pagando.value = false
    }
  }
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

const cargarReserva = async (id) => {
  loading.value = true
  try {
    const res = await reservasService.getReserva(id)
    reserva.value = res.data
  } catch (err) {
    showToast('Error cargando datos de la reserva', 'error')
  } finally {
    loading.value = false
  }
}

const procesarPago = async () => {
  pagando.value = true
  if (metodoPago.value === 'efectivo') {
    // Confirmación directa en efectivo
    try {
      await reservasService.confirmarReserva(reserva.value.id)
      pagoExitoso.value = true
      clearInterval(timerInterval)
    } catch (err) {
      showToast('Error al confirmar reserva en efectivo', 'error')
    } finally {
      pagando.value = false
    }
  } else {
    // Culqi Checkout
    if (typeof window.Culqi === 'undefined') {
      showToast('Culqi no está cargado. Revisa tu conexión a internet.', 'error')
      pagando.value = false
      return
    }
    window.Culqi.publicKey = 'pk_test_e371ad52382b6b06'
    window.Culqi.settings({
      title: `SmartPark Reserva #${reserva.value.id}`,
      currency: 'PEN',
      amount: Math.round(montoTotal.value * 100)
    })
    window.Culqi.open()
  }
}

const completarCobroCulqi = async (tokenId) => {
  try {
    // Simulación de cobro con backend
    await reservasService.confirmarReserva(reserva.value.id)
    pagoExitoso.value = true
    clearInterval(timerInterval)
    showToast('¡Pago procesado exitosamente por Culqi!', 'success')
  } catch (err) {
    showToast('Error al registrar cobro con Culqi', 'error')
  } finally {
    pagando.value = false
  }
}

const irADashboard = () => {
  router.push('/dashboard')
}
</script>
