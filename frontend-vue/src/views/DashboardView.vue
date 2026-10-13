<template>
  <div class="min-h-screen flex bg-slate-900 text-slate-100">
    <!-- Sidebar Izquierdo -->
    <aside class="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0">
      <div>
        <!-- Brand -->
        <div class="p-6 border-b border-slate-800/80 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <i class="fa-solid fa-square-parking text-xl"></i>
            </div>
            <div>
              <h1 class="font-bold text-base leading-tight">SmartPark</h1>
              <span class="text-xs text-sky-400 font-medium">Panel Conductor</span>
            </div>
          </div>
        </div>

        <!-- Navegación -->
        <nav class="p-4 space-y-1">
          <button
            v-for="item in menuItems"
            :key="item.id"
            @click="activeTab = item.id"
            class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all"
            :class="activeTab === item.id 
              ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/30' 
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'"
          >
            <i :class="item.icon" class="w-5 text-center"></i>
            <span>{{ item.label }}</span>
          </button>
        </nav>
      </div>

      <!-- Footer Usuario & Logout -->
      <div class="p-4 border-t border-slate-800/80">
        <div class="flex items-center justify-between p-2 rounded-xl bg-slate-900 border border-slate-800 mb-3">
          <div class="truncate mr-2">
            <p class="text-xs font-bold text-slate-200 truncate">{{ authStore.userName }}</p>
            <p class="text-[11px] text-slate-500 truncate">{{ authStore.user?.email }}</p>
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

    <!-- Contenido Principal -->
    <main class="flex-1 overflow-y-auto p-8 bg-slate-900/60">
      <!-- Header Superior -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl font-black text-white tracking-tight">
            {{ currentSectionTitle }}
          </h2>
          <p class="text-sm text-slate-400">Encuentra tu lugar seguro en tiempo real</p>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="activeTab = 'sedes'"
            class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-sm font-bold shadow-md shadow-sky-600/20 flex items-center gap-2"
          >
            <i class="fa-solid fa-magnifying-glass-location"></i>
            <span>Buscar Estacionamiento</span>
          </button>
        </div>
      </div>

      <!-- Tab 1: Inicio / Resumen -->
      <section v-if="activeTab === 'inicio'" class="space-y-6">
        <!-- Tarjetas Estadísticas -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Reservas Activas</span>
            <div class="text-3xl font-extrabold text-sky-400 mt-2">{{ reservasActivasCount }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Sedes Disponibles</span>
            <div class="text-3xl font-extrabold text-emerald-400 mt-2">{{ sedes.length }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Mis Vehículos</span>
            <div class="text-3xl font-extrabold text-indigo-400 mt-2">{{ vehiculosCount }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Último Pago</span>
            <div class="text-2xl font-extrabold text-amber-400 mt-2 truncate">{{ ultimoPagoTexto }}</div>
          </div>
        </div>

        <!-- Vista Rápida de Sedes Populares -->
        <div class="p-6 rounded-2xl bg-slate-800/80 border border-slate-700/60 glass-card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-base text-white">Sedes Destacadas</h3>
            <button @click="activeTab = 'sedes'" class="text-xs text-sky-400 hover:underline font-semibold">Ver todas</button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="sede in sedes.slice(0, 3)"
              :key="sede.id"
              class="p-4 rounded-xl bg-slate-900/60 border border-slate-700/80 hover:border-sky-500/50 transition-all flex flex-col justify-between"
            >
              <div>
                <h4 class="font-bold text-slate-100">{{ sede.nombre }}</h4>
                <p class="text-xs text-slate-400 mt-1 line-clamp-1"><i class="fa-solid fa-location-dot mr-1"></i>{{ sede.direccion }}</p>
                <div class="mt-3 flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                    S/. {{ (sede.tarifa_hora || 5).toFixed(2) }} / hora
                  </span>
                </div>
              </div>
              <router-link
                :to="`/reserva?sede_id=${sede.id}`"
                class="mt-4 w-full py-2 bg-sky-600/90 hover:bg-sky-600 text-white rounded-lg text-xs font-bold text-center block"
              >
                Reservar Ahora
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- Tab 2: Buscar Sedes & Mapa Leaflet -->
      <section v-if="activeTab === 'sedes'" class="space-y-6">
        <!-- Buscador -->
        <div class="flex gap-4">
          <div class="flex-1 relative">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <i class="fa-solid fa-magnifying-glass"></i>
            </span>
            <input
              v-model="busquedaSede"
              type="text"
              placeholder="Buscar por nombre o dirección..."
              class="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 text-white"
            />
          </div>
        </div>

        <!-- Mapa Leaflet -->
        <div class="rounded-2xl border border-slate-700 overflow-hidden shadow-xl h-80 z-0">
          <div id="map-dashboard" class="w-full h-full"></div>
        </div>

        <!-- Listado de Sedes -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="s in sedesFiltradas"
            :key="s.id"
            class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card hover:border-sky-500/40 transition-all flex flex-col justify-between"
          >
            <div>
              <div class="flex items-start justify-between">
                <h4 class="font-bold text-base text-white">{{ s.nombre }}</h4>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Activa
                </span>
              </div>
              <p class="text-xs text-slate-400 mt-1"><i class="fa-solid fa-location-dot mr-1"></i>{{ s.direccion }}</p>
              
              <div class="mt-4 flex flex-wrap gap-2 text-xs">
                <div class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700/80">
                  <span class="text-slate-400">Tarifa:</span> <strong class="text-slate-100">S/. {{ (s.tarifa_hora || 5).toFixed(2) }}</strong>
                </div>
              </div>
            </div>

            <router-link
              :to="`/reserva?sede_id=${s.id}`"
              class="mt-5 w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-sm font-bold text-center block shadow-md"
            >
              Seleccionar Sede
            </router-link>
          </div>
        </div>
      </section>

      <!-- Tab 3: Mis Reservas -->
      <section v-if="activeTab === 'reservas'" class="space-y-4">
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-300">
              <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
                <tr>
                  <th class="px-5 py-3.5">ID</th>
                  <th class="px-5 py-3.5">Sede</th>
                  <th class="px-5 py-3.5">Espacio</th>
                  <th class="px-5 py-3.5">Inicio</th>
                  <th class="px-5 py-3.5">Fin</th>
                  <th class="px-5 py-3.5">Estado</th>
                  <th class="px-5 py-3.5 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-700/60">
                <tr v-for="r in reservas" :key="r.id" class="hover:bg-slate-700/30">
                  <td class="px-5 py-4 font-mono text-xs">#{{ r.id }}</td>
                  <td class="px-5 py-4 font-semibold text-white">{{ getSedeNombre(r.espacio_id) }}</td>
                  <td class="px-5 py-4">Espacio #{{ r.espacio_id }}</td>
                  <td class="px-5 py-4 text-xs text-slate-400">{{ formatearFecha(r.fecha_inicio) }}</td>
                  <td class="px-5 py-4 text-xs text-slate-400">{{ formatearFecha(r.fecha_fin) }}</td>
                  <td class="px-5 py-4">
                    <span
                      class="px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider border"
                      :class="getEstadoBadge(r.estado)"
                    >
                      {{ r.estado }}
                    </span>
                  </td>
                  <td class="px-5 py-4 text-right">
                    <button
                      v-if="r.estado === 'pendiente' || r.estado === 'confirmada'"
                      @click="cancelarReserva(r.id)"
                      class="px-3 py-1 bg-rose-600/20 hover:bg-rose-600/40 text-rose-400 border border-rose-500/30 rounded-lg text-xs font-semibold"
                    >
                      Cancelar
                    </button>
                    <span v-else class="text-xs text-slate-500">—</span>
                  </td>
                </tr>
                <tr v-if="reservas.length === 0">
                  <td colspan="7" class="text-center py-8 text-slate-500 text-sm">
                    No tienes reservas registradas.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- Tab 4: Mis Pagos -->
      <section v-if="activeTab === 'pagos'" class="space-y-4">
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-300">
              <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
                <tr>
                  <th class="px-5 py-3.5">ID</th>
                  <th class="px-5 py-3.5">Tipo</th>
                  <th class="px-5 py-3.5">Monto</th>
                  <th class="px-5 py-3.5">Método</th>
                  <th class="px-5 py-3.5">Estado</th>
                  <th class="px-5 py-3.5">Fecha</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-700/60">
                <tr v-for="p in pagos" :key="p.id" class="hover:bg-slate-700/30">
                  <td class="px-5 py-4 font-mono text-xs">#{{ p.id }}</td>
                  <td class="px-5 py-4 uppercase text-xs font-bold text-slate-400">{{ p.tipo }}</td>
                  <td class="px-5 py-4 font-bold text-white">S/. {{ (p.monto || 0).toFixed(2) }}</td>
                  <td class="px-5 py-4 text-xs capitalize">{{ p.metodo_pago }}</td>
                  <td class="px-5 py-4">
                    <span
                      class="px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider border"
                      :class="p.estado === 'completado' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'"
                    >
                      {{ p.estado }}
                    </span>
                  </td>
                  <td class="px-5 py-4 text-xs text-slate-400">{{ formatearFecha(p.fecha_creacion || p.fecha_pago) }}</td>
                </tr>
                <tr v-if="pagos.length === 0">
                  <td colspan="6" class="text-center py-8 text-slate-500 text-sm">
                    No tienes transacciones registradas.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { pagosService } from '@/services/pagos'
import { usuariosService } from '@/services/usuarios'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import L from 'leaflet'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const activeTab = ref('inicio')
const sedes = ref([])
const reservas = ref([])
const pagos = ref([])
const vehiculosCount = ref(0)
const busquedaSede = ref('')

let leafletMap = null

const menuItems = [
  { id: 'inicio', label: 'Inicio', icon: 'fa-solid fa-house' },
  { id: 'sedes', label: 'Buscar Sedes', icon: 'fa-solid fa-map-location-dot' },
  { id: 'reservas', label: 'Mis Reservas', icon: 'fa-solid fa-calendar-check' },
  { id: 'vehiculos', label: 'Mis Vehículos', icon: 'fa-solid fa-car' },
  { id: 'pagos', label: 'Mis Pagos', icon: 'fa-solid fa-credit-card' },
]

const currentSectionTitle = computed(() => {
  const item = menuItems.find(m => m.id === activeTab.value)
  return item ? item.label : 'Dashboard'
})

const sedesFiltradas = computed(() => {
  if (!busquedaSede.value.trim()) return sedes.value
  const q = busquedaSede.value.toLowerCase()
  return sedes.value.filter(s => 
    s.nombre.toLowerCase().includes(q) || s.direccion.toLowerCase().includes(q)
  )
})

const reservasActivasCount = computed(() => {
  return reservas.value.filter(r => r.estado === 'confirmada' || r.estado === 'pendiente').length
})

const ultimoPagoTexto = computed(() => {
  if (pagos.value.length === 0) return 'Ninguno'
  const p = pagos.value[0]
  return `S/. ${(p.monto || 0).toFixed(2)}`
})

onMounted(async () => {
  themeStore.initTheme(true) // Dark mode default para dashboard
  await cargarDatos()
})

watch(activeTab, (newTab) => {
  if (newTab === 'vehiculos') {
    router.push('/vehiculos')
    return
  }
  if (newTab === 'sedes') {
    nextTick(() => {
      initMap()
    })
  }
})

const cargarDatos = async () => {
  try {
    // Sedes
    const sResp = await estacionamientosService.getSedes(0, 50)
    sedes.value = Array.isArray(sResp.data) ? sResp.data : (sResp.data?.data || [])

    // Reservas
    const rResp = await reservasService.getReservas(0, 50)
    reservas.value = Array.isArray(rResp.data) ? rResp.data : (rResp.data?.data || [])

    // Pagos
    const pResp = await pagosService.getPagos(0, 50)
    pagos.value = Array.isArray(pResp.data) ? pResp.data : (pResp.data?.data || [])

    // Vehículos
    const vResp = await usuariosService.getMisVehiculos()
    vehiculosCount.value = (vResp.data || []).length

  } catch (err) {
    console.warn('Error cargando datos del dashboard:', err)
  }
}

const initMap = () => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
  }
  const mapElem = document.getElementById('map-dashboard')
  if (!mapElem) return

  // Default centrado en Lima, Perú
  leafletMap = L.map('map-dashboard').setView([-12.046374, -77.042793], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(leafletMap)

  // Marcadores de sedes
  sedes.value.forEach(s => {
    if (s.latitud && s.longitud) {
      const marker = L.marker([s.latitud, s.longitud]).addTo(leafletMap)
      marker.bindPopup(`
        <div style="font-family:sans-serif;">
          <strong>${s.nombre}</strong><br>
          <small>${s.direccion}</small><br>
          <a href="/reserva?sede_id=${s.id}" style="color:#0284c7;font-weight:bold;">Reservar aquí</a>
        </div>
      `)
    }
  })
}

const cancelarReserva = async (id) => {
  if (!confirm('¿Deseas cancelar esta reserva?')) return
  try {
    await reservasService.cancelarReserva(id)
    showToast('Reserva cancelada correctamente', 'success')
    await cargarDatos()
  } catch (err) {
    showToast(err.response?.data?.detail || 'No se pudo cancelar la reserva', 'error')
  }
}

const getSedeNombre = (espacioId) => {
  return `Estacionamiento Central`
}

const formatearFecha = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleString('es-PE', { dateStyle: 'short', timeStyle: 'short' })
}

const getEstadoBadge = (estado) => {
  switch (estado) {
    case 'confirmada':
      return 'bg-sky-500/10 text-sky-400 border-sky-500/20'
    case 'pendiente':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'cancelada':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20'
    case 'finalizada':
    case 'completada':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    default:
      return 'bg-slate-700 text-slate-300 border-slate-600'
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
