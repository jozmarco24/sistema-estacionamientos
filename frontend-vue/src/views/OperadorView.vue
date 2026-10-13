<template>
  <div class="min-h-screen flex bg-slate-900 text-slate-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0">
      <div>
        <div class="p-6 border-b border-slate-800 flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-md">
            <i class="fa-solid fa-square-parking text-xl"></i>
          </div>
          <div>
            <h1 class="font-bold text-base leading-tight">SmartPark</h1>
            <span class="text-xs text-emerald-400 font-semibold tracking-wide">OPERADOR</span>
          </div>
        </div>

        <nav class="p-4 space-y-1">
          <button
            v-for="item in menuItems"
            :key="item.id"
            @click="activeTab = item.id"
            class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all"
            :class="activeTab === item.id 
              ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30' 
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'"
          >
            <i :class="item.icon" class="w-5 text-center"></i>
            <span>{{ item.label }}</span>
          </button>
        </nav>
      </div>

      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center justify-between p-2 rounded-xl bg-slate-900 border border-slate-800 mb-3">
          <div class="truncate mr-2">
            <p class="text-xs font-bold text-slate-200 truncate">{{ authStore.userName }}</p>
            <p class="text-[11px] text-emerald-400 font-medium">Turno Operativo</p>
          </div>
          <ThemeToggle />
        </div>
        <button
          @click="logout"
          class="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-bold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-xl transition-all"
        >
          <i class="fa-solid fa-arrow-right-from-bracket"></i>
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>

    <!-- Contenido -->
    <main class="flex-1 overflow-y-auto p-8 bg-slate-900/60">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl font-black text-white tracking-tight">{{ currentTitle }}</h2>
          <p class="text-sm text-slate-400">Control visual de espacios, entradas, salidas e incidencias</p>
        </div>
      </div>

      <!-- Tab 1: Resumen del Turno -->
      <section v-if="activeTab === 'resumen'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-emerald-400">Espacios Libres</span>
            <div class="text-3xl font-extrabold text-white mt-2">{{ libresCount }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-rose-400">Espacios Ocupados</span>
            <div class="text-3xl font-extrabold text-white mt-2">{{ ocupadosCount }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-amber-400">Reservados</span>
            <div class="text-3xl font-extrabold text-white mt-2">{{ reservadosCount }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-sky-400">Total Espacios</span>
            <div class="text-3xl font-extrabold text-white mt-2">{{ espacios.length }}</div>
          </div>
        </div>

        <!-- Quick Walk-in -->
        <div class="p-6 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
          <h3 class="font-bold text-base text-white mb-3">Atención Rápida en Puerta (Walk-in)</h3>
          <p class="text-xs text-slate-400 mb-4">Ingresa vehículo directamente sin reserva previa asignando un cajón libre.</p>
          <div class="flex gap-3">
            <input
              v-model="walkinPlaca"
              type="text"
              placeholder="Placa (ej: ABC-123)"
              class="px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm font-mono uppercase text-white"
            />
            <button
              @click="registrarEntradaWalkin"
              class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-bold shadow"
            >
              Registrar Entrada
            </button>
          </div>
        </div>
      </section>

      <!-- Tab 2: Mapa de Espacios (Visual Grid) -->
      <section v-if="activeTab === 'espacios'" class="space-y-4">
        <div class="flex items-center justify-between">
          <p class="text-xs text-slate-400">Haz clic en cualquier espacio para cambiar su estado o registrar salida.</p>
          <div class="flex gap-4 text-xs font-bold">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-emerald-500"></span> Libre</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-rose-500"></span> Ocupado</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-500"></span> Reservado</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-slate-600"></span> Bloqueado</span>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
          <button
            v-for="e in espacios"
            :key="e.id"
            @click="abrirModalEspacio(e)"
            type="button"
            class="p-4 rounded-xl border flex flex-col items-center justify-center gap-1 transition-all hover:scale-105 shadow-sm"
            :class="getEspacioClase(e.estado)"
          >
            <span class="text-xs font-black tracking-wider uppercase">{{ e.numero }}</span>
            <i class="fa-solid fa-car text-lg my-1"></i>
            <span class="text-[10px] font-bold uppercase">{{ e.estado }}</span>
          </button>
        </div>
      </section>

      <!-- Tab 3: Reservas Activas -->
      <section v-if="activeTab === 'reservas'" class="space-y-4">
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="px-5 py-3.5">ID</th>
                <th class="px-5 py-3.5">Espacio</th>
                <th class="px-5 py-3.5">Placa</th>
                <th class="px-5 py-3.5">Inicio</th>
                <th class="px-5 py-3.5">Estado</th>
                <th class="px-5 py-3.5 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/60">
              <tr v-for="r in reservas" :key="r.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ r.id }}</td>
                <td class="px-5 py-4 font-bold text-white">Espacio #{{ r.espacio_id }}</td>
                <td class="px-5 py-4 font-mono text-xs uppercase">{{ r.placa_vehiculo || '—' }}</td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ r.fecha_inicio }}</td>
                <td class="px-5 py-4">
                  <span class="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase border bg-slate-800 border-slate-600">
                    {{ r.estado }}
                  </span>
                </td>
                <td class="px-5 py-4 text-right space-x-2">
                  <button
                    v-if="r.estado === 'pendiente'"
                    @click="confirmarEntrada(r.id)"
                    class="px-2.5 py-1 text-xs bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/40 rounded border border-emerald-500/30"
                  >
                    Confirmar
                  </button>
                  <button
                    v-if="r.estado === 'confirmada' || r.estado === 'pendiente'"
                    @click="cancelarReserva(r.id)"
                    class="px-2.5 py-1 text-xs bg-rose-600/20 text-rose-400 hover:bg-rose-600/40 rounded border border-rose-500/30"
                  >
                    Cancelar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 4: Incidencias -->
      <section v-if="activeTab === 'incidencias'" class="space-y-6">
        <!-- Registrar Incidencia -->
        <div class="p-6 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
          <h3 class="font-bold text-base text-white mb-4">Reportar Nueva Incidencia</h3>
          <form @submit.prevent="registrarIncidencia" class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-slate-400 mb-1">Sede ID</label>
                <input v-model.number="formIncidencia.sede_id" type="number" required class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white" />
              </div>
              <div>
                <label class="block text-xs font-bold text-slate-400 mb-1">Espacio (opcional)</label>
                <input v-model="formIncidencia.espacio" type="text" placeholder="Ej: A-01" class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 mb-1">Descripción del Incidente</label>
              <textarea v-model="formIncidencia.descripcion" required rows="2" placeholder="Detalla el problema ocurrido..." class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white"></textarea>
            </div>
            <button type="submit" class="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold shadow">
              Registrar Incidencia
            </button>
          </form>
        </div>

        <!-- Lista Incidencias -->
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="px-5 py-3.5">ID</th>
                <th class="px-5 py-3.5">Sede</th>
                <th class="px-5 py-3.5">Descripción</th>
                <th class="px-5 py-3.5">Fecha Reporte</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/60">
              <tr v-for="inc in incidencias" :key="inc.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ inc.id }}</td>
                <td class="px-5 py-4 font-semibold text-white">Sede #{{ inc.sede_id }}</td>
                <td class="px-5 py-4 text-xs">{{ inc.descripcion }}</td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ inc.fecha_reporte }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 5: Escáner QR / Búsqueda Manual -->
      <section v-if="activeTab === 'qr'" class="space-y-4">
        <div class="p-6 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card max-w-lg">
          <h3 class="font-bold text-base text-white mb-2"><i class="fa-solid fa-qrcode mr-2"></i>Búsqueda y Validación de Reserva</h3>
          <p class="text-xs text-slate-400 mb-4">Ingresa el ID de la reserva o el código escaneado del ticket.</p>
          <div class="flex gap-3">
            <input
              v-model="qrInput"
              type="text"
              placeholder="Código o # ID Reserva"
              class="flex-1 px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-sm font-mono text-white"
            />
            <button
              @click="buscarReservaQR"
              class="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-sm font-bold"
            >
              Buscar
            </button>
          </div>

          <div v-if="reservaEncontrada" class="mt-5 p-4 rounded-xl bg-slate-900 border border-slate-700">
            <h4 class="font-bold text-sm text-sky-400">Reserva #{{ reservaEncontrada.id }}</h4>
            <p class="text-xs text-slate-300 mt-1">Espacio: Cajón #{{ reservaEncontrada.espacio_id }}</p>
            <p class="text-xs text-slate-300">Estado: <span class="uppercase font-bold">{{ reservaEncontrada.estado }}</span></p>
            <div class="mt-3 flex gap-2">
              <button
                @click="confirmarEntrada(reservaEncontrada.id)"
                class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg"
              >
                Confirmar Ingreso
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Acción Espacio -->
    <div v-if="modalEspacio.open" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <h3 class="text-lg font-bold text-white mb-2">Cajón {{ modalEspacio.espacio?.numero }}</h3>
        <p class="text-xs text-slate-400 mb-4">Estado actual: <strong class="uppercase text-white">{{ modalEspacio.espacio?.estado }}</strong></p>
        
        <div class="space-y-2">
          <button
            @click="cambiarEstadoEspacio('libre')"
            class="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold"
          >
            Marcar Libre (Salida)
          </button>
          <button
            @click="cambiarEstadoEspacio('ocupado')"
            class="w-full py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold"
          >
            Marcar Ocupado (Entrada)
          </button>
          <button
            @click="cambiarEstadoEspacio('bloqueado')"
            class="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-xs font-bold"
          >
            Bloquear Cajón (Mantenimiento)
          </button>
        </div>
        <button @click="modalEspacio.open = false" class="w-full mt-4 py-2 bg-slate-800 text-slate-400 rounded-xl text-xs font-bold">
          Cerrar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const activeTab = ref('resumen')
const espacios = ref([])
const reservas = ref([])
const incidencias = ref([])
const walkinPlaca = ref('')
const qrInput = ref('')
const reservaEncontrada = ref(null)

const modalEspacio = ref({
  open: false,
  espacio: null
})

const formIncidencia = ref({
  sede_id: 1,
  espacio: '',
  descripcion: ''
})

const menuItems = [
  { id: 'resumen', label: 'Resumen del Turno', icon: 'fa-solid fa-gauge-high' },
  { id: 'espacios', label: 'Mapa de Espacios', icon: 'fa-solid fa-border-all' },
  { id: 'reservas', label: 'Reservas Activas', icon: 'fa-solid fa-calendar-check' },
  { id: 'incidencias', label: 'Incidencias', icon: 'fa-solid fa-triangle-exclamation' },
  { id: 'qr', label: 'Escáner QR / Entrada', icon: 'fa-solid fa-qrcode' },
]

const currentTitle = computed(() => {
  return menuItems.find(m => m.id === activeTab.value)?.label || 'Panel de Operador'
})

const libresCount = computed(() => espacios.value.filter(e => e.estado === 'libre').length)
const ocupadosCount = computed(() => espacios.value.filter(e => e.estado === 'ocupado').length)
const reservadosCount = computed(() => espacios.value.filter(e => e.estado === 'reservado').length)

onMounted(async () => {
  themeStore.initTheme(true)
  await cargarDatos()
})

const cargarDatos = async () => {
  try {
    const [eRes, rRes, iRes] = await Promise.allSettled([
      estacionamientosService.getEspacios(0, 100),
      reservasService.getReservas(0, 50),
      estacionamientosService.getIncidencias(0, 50)
    ])

    if (eRes.status === 'fulfilled') {
      const d = eRes.value.data
      espacios.value = Array.isArray(d) ? d : (d?.data || [])
    }
    if (rRes.status === 'fulfilled') {
      const d = rRes.value.data
      reservas.value = Array.isArray(d) ? d : (d?.data || [])
    }
    if (iRes.status === 'fulfilled') {
      const d = iRes.value.data
      incidencias.value = Array.isArray(d) ? d : (d?.data || [])
    }
  } catch (err) {
    console.warn('Error cargando operador:', err)
  }
}

const getEspacioClase = (estado) => {
  switch (estado) {
    case 'libre':
      return 'bg-emerald-950/40 border-emerald-500/40 text-emerald-400 hover:border-emerald-400'
    case 'ocupado':
      return 'bg-rose-950/40 border-rose-500/40 text-rose-400 hover:border-rose-400'
    case 'reservado':
      return 'bg-amber-950/40 border-amber-500/40 text-amber-400 hover:border-amber-400'
    default:
      return 'bg-slate-800 border-slate-700 text-slate-500 hover:border-slate-500'
  }
}

const abrirModalEspacio = (e) => {
  modalEspacio.value = { open: true, espacio: e }
}

const cambiarEstadoEspacio = async (nuevoEstado) => {
  if (!modalEspacio.value.espacio) return
  try {
    await estacionamientosService.actualizarEstadoEspacio(modalEspacio.value.espacio.id, nuevoEstado)
    showToast(`Espacio ${modalEspacio.value.espacio.numero} marcado como ${nuevoEstado}`, 'success')
    modalEspacio.value.open = false
    await cargarDatos()
  } catch (err) {
    showToast('Error al actualizar estado', 'error')
  }
}

const registrarEntradaWalkin = async () => {
  if (!walkinPlaca.value.trim()) {
    showToast('Ingresa la placa del vehículo', 'warning')
    return
  }
  const libre = espacios.value.find(e => e.estado === 'libre')
  if (!libre) {
    showToast('No hay espacios libres disponibles', 'error')
    return
  }
  try {
    await estacionamientosService.actualizarEstadoEspacio(libre.id, 'ocupado')
    showToast(`Vehículo ${walkinPlaca.value} asignado a cajón ${libre.numero}`, 'success')
    walkinPlaca.value = ''
    await cargarDatos()
  } catch (err) {
    showToast('Error registrando entrada', 'error')
  }
}

const confirmarEntrada = async (reservaId) => {
  try {
    await reservasService.confirmarReserva(reservaId)
    showToast(`Reserva #${reservaId} confirmada exitosamente`, 'success')
    await cargarDatos()
  } catch (err) {
    showToast('Error al confirmar reserva', 'error')
  }
}

const cancelarReserva = async (reservaId) => {
  if (!confirm('¿Deseas cancelar esta reserva?')) return
  try {
    await reservasService.cancelarReserva(reservaId)
    showToast(`Reserva #${reservaId} cancelada`, 'success')
    await cargarDatos()
  } catch (err) {
    showToast('Error al cancelar reserva', 'error')
  }
}

const registrarIncidencia = async () => {
  try {
    await estacionamientosService.crearIncidencia(formIncidencia.value)
    showToast('Incidencia registrada exitosamente', 'success')
    formIncidencia.value.descripcion = ''
    formIncidencia.value.espacio = ''
    await cargarDatos()
  } catch (err) {
    showToast('Error al reportar incidencia', 'error')
  }
}

const buscarReservaQR = async () => {
  if (!qrInput.value) return
  const idNum = parseInt(qrInput.value.replace(/\D/g, ''))
  const r = reservas.value.find(res => res.id === idNum)
  if (r) {
    reservaEncontrada.value = r
    showToast(`Reserva #${r.id} localizada`, 'success')
  } else {
    showToast('No se encontró reserva con ese código', 'error')
    reservaEncontrada.value = null
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
