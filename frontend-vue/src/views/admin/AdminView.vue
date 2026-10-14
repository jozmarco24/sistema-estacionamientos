<template>
  <div class="admin-app-root" :class="{ 'light-mode': themeStore.isLight }">
    <!-- Mobile Top Bar -->
    <div class="mobile-bar">
      <div class="logo-area" style="margin-bottom:0; font-size:1.3rem;">
        <i class="fa-solid fa-square-parking"></i> SmartPark Admin
      </div>
      <button class="toggle-btn" @click="sidebarOpen = !sidebarOpen">
        <i class="fa-solid fa-bars"></i>
      </button>
    </div>

    <!-- Sidebar Navigation Organizada por Secciones -->
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="logo-area">
        <i class="fa-solid fa-square-parking"></i> SmartPark
      </div>
      <ul class="nav-menu">
        <div class="nav-divider">Centro de Control</div>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-dashboard' }"
          @click.prevent="switchSection('sec-dashboard')"
        >
          <i class="fa-solid fa-chart-pie"></i> Resumen General
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-sedes' }"
          @click.prevent="switchSection('sec-sedes')"
        >
          <i class="fa-solid fa-warehouse"></i> Sedes y Mapa
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-propietarios' }"
          @click.prevent="switchSection('sec-propietarios')"
        >
          <i class="fa-solid fa-users-gear"></i> Propietarios
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-saas' }"
          @click.prevent="switchSection('sec-saas')"
        >
          <i class="fa-solid fa-box-open"></i> Planes & Suscripciones
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-pagos' }"
          @click.prevent="switchSection('sec-pagos')"
        >
          <i class="fa-solid fa-credit-card"></i> Pagos & Transacciones
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-reservas' }"
          @click.prevent="switchSection('sec-reservas')"
        >
          <i class="fa-solid fa-clock-rotate-left"></i> Reservas en Vivo
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-conductores' }"
          @click.prevent="switchSection('sec-conductores')"
        >
          <i class="fa-solid fa-users"></i> Conductores
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-incidencias' }"
          @click.prevent="switchSection('sec-incidencias')"
        >
          <i class="fa-solid fa-bell"></i> Incidencias
        </a>

        <a href="#" class="nav-item logout-btn" @click.prevent="logout">
          <i class="fa-solid fa-right-from-bracket"></i> Cerrar Sesión
        </a>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Toast Alert Notification -->
      <div
        v-if="toast.show"
        class="alert-toast"
        :style="{ background: toast.isError ? 'rgba(239, 68, 68, 0.95)' : 'rgba(16, 185, 129, 0.95)' }"
      >
        {{ toast.msg }}
      </div>

      <!-- Top Header -->
      <div class="top-header">
        <div class="greeting">
          <h1>{{ sectionTitles[currentSection]?.title || 'Centro de Control Global' }}</h1>
          <p>{{ sectionTitles[currentSection]?.sub || 'Monitoreo y métricas clave de SmartPark en tiempo real.' }}</p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <button @click="refreshAll" class="btn-action" title="Recargar datos">
            <i class="fa-solid fa-rotate" :class="{ 'fa-spin': isRefreshing }"></i> Actualizar
          </button>
          <button @click="themeStore.toggleTheme" class="theme-toggle-btn">
            <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
            <span>{{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}</span>
          </button>
        </div>
      </div>

      <!-- Secciones dinámicas montadas con <component :is="..." /> -->
      <component
        :is="currentSectionComponent"
        v-bind="currentSectionProps"
        @check-health="checkHealth"
        @refresh="refreshAll"
        @refresh-pagos="loadPagosGlobales"
        @refresh-reservas="loadReservasGlobales"
        @toast="onChildToast"
      />

      <!-- Sección Incidencias -->
      <section v-show="currentSection === 'sec-incidencias'" class="section-view active-section">
        <div class="card">
          <h2 class="card-title" style="color: #f87171;">
            <i class="fa-solid fa-bell"></i> Incidencias Reportadas por Operadores de Caseta
          </h2>
          <div style="max-height: 500px; overflow-y: auto;">
            <div v-for="inc in incidenciasList" :key="inc.id" class="incidencia-row">
              <div>
                <div style="font-weight: 600;">Sede #{{ inc.sede_id }} (Operador #{{ inc.operador_id }})</div>
                <div class="desc">{{ inc.descripcion }}</div>
              </div>
              <div class="date">{{ formatearFecha(inc.fecha_reporte) }}</div>
            </div>
            <p v-if="incidenciasList.length === 0" style="color: var(--text-muted); text-align: center; padding: 20px;">
              No hay incidencias recientes.
            </p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { usuariosService } from '@/services/usuarios'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { pagosService } from '@/services/pagos'

import AdminDashboard from './AdminDashboard.vue'
import AdminSedes from './AdminSedes.vue'
import AdminPropietarios from './AdminPropietarios.vue'
import AdminPlanes from './AdminPlanes.vue'
import AdminPagos from './AdminPagos.vue'
import AdminReservas from './AdminReservas.vue'
import AdminConductores from './AdminConductores.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// Sections
const currentSection = ref('sec-dashboard')
const sidebarOpen = ref(false)
const isRefreshing = ref(false)
const isCheckingHealth = ref(false)
const lastHealthCheckTime = ref('')

const sectionTitles = {
  'sec-dashboard': { title: 'Centro de Control Global', sub: 'Monitoreo y métricas clave de SmartPark en tiempo real.' },
  'sec-sedes': { title: 'Gestión de Sedes y Mapa', sub: 'Control geográfico y administración de tarifas por sede.' },
  'sec-propietarios': { title: 'Gestión de Propietarios', sub: 'Cuentas de propietarios y dueños de parqueaderos.' },
  'sec-saas': { title: 'Planes SaaS y Suscripciones', sub: 'Configuración de paquetes mensuales y membresías activas.' },
  'sec-pagos': { title: 'Pagos & Transacciones Globales', sub: 'Auditoría financiera y flujo de caja de todas las transacciones procesadas.' },
  'sec-reservas': { title: 'Reservas Globales en Vivo', sub: 'Supervisión en tiempo real de espacios y vehículos reservados.' },
  'sec-conductores': { title: 'Directorio de Conductores', sub: 'Usuarios finales registrados en la plataforma móvil y web.' },
  'sec-incidencias': { title: 'Reporte de Incidencias', sub: 'Alertas y sucesos reportados por operadores en caseta.' }
}

const sectionComponentMap = {
  'sec-dashboard': AdminDashboard,
  'sec-sedes': AdminSedes,
  'sec-propietarios': AdminPropietarios,
  'sec-saas': AdminPlanes,
  'sec-pagos': AdminPagos,
  'sec-reservas': AdminReservas,
  'sec-conductores': AdminConductores
}

const currentSectionComponent = computed(() => sectionComponentMap[currentSection.value] || null)

// Data Lists
const sedesList = ref([])
const propietariosList = ref([])
const conductoresList = ref([])
const reservasList = ref([])
const pagosList = ref([])
const planesList = ref([])
const suscripcionesList = ref([])
const incidenciasList = ref([])
const espaciosMap = ref({}) // id -> { sede_id, sede_nombre, numero }

// Metrics
const stats = reactive({ libres: 0, reservados: 0, ocupados: 0 })
const mrrTotal = ref(0)

// Toast Notification
const toast = reactive({ show: false, msg: '', isError: false })
let toastTimer = null
function showToast(msg, isError = false) {
  if (toastTimer) clearTimeout(toastTimer)
  toast.msg = msg
  toast.isError = isError
  toast.show = true
  toastTimer = setTimeout(() => { toast.show = false }, 3500)
}

function onChildToast({ msg, isError = false }) {
  showToast(msg, isError)
}

// Health status
const healthStatus = reactive({
  usuarios: { ok: true, ms: 0 },
  estacionamientos: { ok: true, ms: 0 },
  reservas: { ok: true, ms: 0 },
  pagos: { ok: true, ms: 0 }
})

let healthInterval = null

const currentSectionProps = computed(() => {
  switch (currentSection.value) {
    case 'sec-dashboard':
      return {
        healthStatus,
        isCheckingHealth: isCheckingHealth.value,
        lastHealthCheckTime: lastHealthCheckTime.value,
        stats,
        sedesList: sedesList.value,
        reservasList: reservasList.value,
        mrrTotal: mrrTotal.value,
        suscripcionesList: suscripcionesList.value,
        planesList: planesList.value
      }
    case 'sec-sedes':
      return {
        sedesList: sedesList.value,
        propietariosList: propietariosList.value
      }
    case 'sec-propietarios':
      return {
        propietariosList: propietariosList.value,
        sedesList: sedesList.value,
        planesList: planesList.value,
        suscripcionesList: suscripcionesList.value
      }
    case 'sec-saas':
      return {
        planesList: planesList.value,
        suscripcionesList: suscripcionesList.value,
        propietariosList: propietariosList.value
      }
    case 'sec-pagos':
      return {
        pagosList: pagosList.value
      }
    case 'sec-reservas':
      return {
        reservasList: reservasList.value,
        sedesList: sedesList.value
      }
    case 'sec-conductores':
      return {
        conductoresList: conductoresList.value
      }
    default:
      return {}
  }
})

function switchSection(secId) {
  currentSection.value = secId
  sidebarOpen.value = false
}

function formatearFecha(dateStr) {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('es-PE', {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch (e) {
    return dateStr
  }
}

// Health check with latency measurement
async function checkHealth() {
  if (isCheckingHealth.value) return
  isCheckingHealth.value = true

  const ping = async (fn) => {
    const start = performance.now()
    try {
      await fn()
      const end = performance.now()
      return { ok: true, ms: Math.max(1, Math.round(end - start)) }
    } catch (err) {
      return { ok: false, ms: 0 }
    }
  }

  try {
    const [u, e, r, p] = await Promise.all([
      ping(() => usuariosService.health()),
      ping(() => estacionamientosService.health()),
      ping(() => reservasService.health()),
      ping(() => pagosService.health())
    ])

    healthStatus.usuarios.ok = u.ok
    healthStatus.usuarios.ms = u.ms

    healthStatus.estacionamientos.ok = e.ok
    healthStatus.estacionamientos.ms = e.ms

    healthStatus.reservas.ok = r.ok
    healthStatus.reservas.ms = r.ms

    healthStatus.pagos.ok = p.ok
    healthStatus.pagos.ms = p.ms

    lastHealthCheckTime.value = new Date().toLocaleTimeString()
  } catch (err) {
    console.error('Error health check:', err)
  } finally {
    isCheckingHealth.value = false
  }
}

// Data loaders
async function refreshAll() {
  isRefreshing.value = true
  try {
    await checkHealth()
    await Promise.all([
      loadPropietarios(),
      loadConductores(),
      loadSedesAndStats(),
      loadSaaS(),
      loadPagosGlobales(),
      loadIncidencias()
    ])
    await loadReservasGlobales()
  } finally {
    isRefreshing.value = false
  }
}

async function loadPropietarios() {
  try {
    const res = await usuariosService.getPropietarios()
    propietariosList.value = res.data || []
  } catch (err) {
    console.error('Error cargando propietarios:', err)
  }
}

async function loadConductores() {
  try {
    const res = await usuariosService.getUsuarios(0, 300)
    const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    conductoresList.value = list.filter(u => u.rol === 'conductor')
  } catch (err) {
    console.error('Error cargando conductores:', err)
  }
}

async function loadSedesAndStats() {
  try {
    const res = await estacionamientosService.getSedes(0, 200)
    sedesList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])

    let lib = 0, resv = 0, ocu = 0
    for (const s of sedesList.value) {
      try {
        const espRes = await estacionamientosService.getEspaciosPorSede(s.id)
        const espacios = espRes.data || []
        espacios.forEach(e => {
          if (e.estado === 'libre') lib++
          else if (e.estado === 'reservado') resv++
          else if (e.estado === 'ocupado') ocu++
        })
      } catch (e) {}
    }
    stats.libres = lib
    stats.reservados = resv
    stats.ocupados = ocu
  } catch (err) {
    console.error('Error cargando sedes:', err)
  }
}

async function loadReservasGlobales() {
  try {
    if (Object.keys(espaciosMap.value).length === 0) {
      try {
        const espRes = await estacionamientosService.getEspacios(0, 500)
        const espList = Array.isArray(espRes.data) ? espRes.data : (espRes.data?.data || [])
        espList.forEach(esp => {
          const sedeObj = sedesList.value.find(s => s.id === esp.sede_id)
          espaciosMap.value[esp.id] = {
            sede_id: esp.sede_id,
            sede_nombre: sedeObj ? sedeObj.nombre : `Sede #${esp.sede_id}`,
            numero: esp.numero
          }
        })
      } catch (e) {}
    }

    const res = await reservasService.getReservas(0, 500)
    const rawList = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    reservasList.value = rawList.map(r => {
      const info = espaciosMap.value[r.espacio_id] || {}
      return {
        ...r,
        sede_id: info.sede_id || null,
        sede_nombre: info.sede_nombre || 'Sede General',
        espacio_numero: info.numero || `#${r.espacio_id}`
      }
    })
  } catch (err) {
    console.error('Error cargando reservas:', err)
  }
}

async function loadPagosGlobales() {
  try {
    const res = await pagosService.getPagos(0, 500)
    pagosList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    console.error('Error cargando pagos:', err)
  }
}

async function loadSaaS() {
  try {
    const [pRes, sRes] = await Promise.all([
      usuariosService.getPlanes(),
      usuariosService.getSuscripcionesTodas()
    ])
    planesList.value = pRes.data || []
    suscripcionesList.value = sRes.data || []

    const pMap = {}
    planesList.value.forEach(p => { pMap[p.id] = p.precio })
    let m = 0
    suscripcionesList.value.forEach(s => {
      if (s.estado === 'activa') {
        m += (pMap[s.plan_id] || 0)
      }
    })
    mrrTotal.value = m
  } catch (err) {
    console.error('Error cargando SaaS:', err)
  }
}

async function loadIncidencias() {
  try {
    const res = await estacionamientosService.getIncidencias(0, 50)
    incidenciasList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    console.error('Error incidencias:', err)
  }
}

function logout() {
  authStore.logout()
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('user_info')
  router.push('/login')
}

onMounted(async () => {
  themeStore.initTheme(true)
  await refreshAll()
  healthInterval = setInterval(checkHealth, 30000)
})

onUnmounted(() => {
  if (healthInterval) clearInterval(healthInterval)
})
</script>

<style scoped>
.admin-app-root {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-color, #0b0f19);
  background-image: radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.1) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.08) 0px, transparent 50%);
  color: var(--text-main, #f8fafc);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

:deep(.leaflet-layer), :deep(.leaflet-control-zoom-in), :deep(.leaflet-control-zoom-out), :deep(.leaflet-control-attribution) {
  filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);
}

.admin-app-root.light-mode :deep(.leaflet-layer),
.admin-app-root.light-mode :deep(.leaflet-control-zoom-in),
.admin-app-root.light-mode :deep(.leaflet-control-zoom-out),
.admin-app-root.light-mode :deep(.leaflet-control-attribution) {
  filter: none;
}

.admin-app-root {
  --bg-color: #0b0f19;
  --sidebar-bg: rgba(15, 23, 42, 0.85);
  --glass-bg: rgba(30, 41, 59, 0.65);
  --glass-border: rgba(255, 255, 255, 0.1);
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #38bdf8;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --color-libre: #10b981;
  --color-ocupado: #ef4444;
  --color-reservado: #f59e0b;
}

.admin-app-root.light-mode {
  --bg-color: #f8fafc;
  --sidebar-bg: rgba(255, 255, 255, 0.95);
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0;
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #0284c7;
  --text-main: #0f172a;
  --text-muted: #64748b;
  background-image: radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.05) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(2, 132, 199, 0.03) 0px, transparent 50%);
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: var(--sidebar-bg);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  padding: 24px 18px;
  z-index: 100;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.logo-area {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-left: 8px;
}
.logo-area i { color: #0284c7; -webkit-text-fill-color: initial; }

.nav-menu { list-style: none; display: flex; flex-direction: column; gap: 6px; flex: 1; padding: 0; margin: 0; }
.nav-item {
  padding: 12px 14px;
  border-radius: 12px;
  color: var(--text-muted);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.25s ease;
  cursor: pointer;
}
.nav-item:hover { background: rgba(255,255,255,0.04); color: var(--text-main); }
.nav-item.active {
  background: linear-gradient(90deg, rgba(2,132,199,0.18) 0%, rgba(2,132,199,0.03) 100%);
  color: var(--primary);
  border-left: 3px solid var(--primary);
  font-weight: 600;
}
.nav-item i { font-size: 1.1rem; width: 22px; text-align: center; }

.nav-divider {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 14px 12px 4px 12px;
  letter-spacing: 1px;
  font-weight: 700;
}

.logout-btn { margin-top: auto; color: #ef4444 !important; }
.logout-btn:hover { background: rgba(239,68,68,0.1) !important; }

/* Main Content */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px 40px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.top-header { display: flex; justify-content: space-between; align-items: center; }
.greeting h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
.greeting p { color: var(--text-muted); font-size: 0.95rem; }

.theme-toggle-btn {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 10px 16px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

/* Sections */
:deep(.section-view) { display: flex; flex-direction: column; gap: 22px; animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

:deep(.card) {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
:deep(.card-title) {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e2e8f0;
}

/* Stats 6 items */
:deep(.stats-row) { display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; }
:deep(.stat-box) {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
:deep(.stat-box.libre) { border-bottom: 3px solid var(--color-libre); }
:deep(.stat-box.reservado) { border-bottom: 3px solid var(--color-reservado); }
:deep(.stat-box.ocupado) { border-bottom: 3px solid var(--color-ocupado); }
:deep(.stat-box.ingresos) { border-bottom: 3px solid var(--primary); }
:deep(.stat-box.sedes) { border-bottom: 3px solid var(--accent); }
:deep(.stat-box.reservas-count) { border-bottom: 3px solid #ec4899; }
:deep(.stat-label) { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
:deep(.stat-value) { font-size: 1.7rem; font-weight: 800; }

/* Health Service Status Badges */
:deep(.health-grid) { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
:deep(.health-item) {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--glass-border);
  padding: 14px 18px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}
:deep(.health-info) { display: flex; flex-direction: column; gap: 3px; }
:deep(.health-name) { font-weight: 600; display: flex; align-items: center; gap: 8px; }
:deep(.health-meta) { font-size: 0.75rem; color: var(--text-muted); }

:deep(.health-status-badge) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}
:deep(.health-status-badge.online) {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
:deep(.health-status-badge.offline) {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
:deep(.health-dot) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
:deep(.health-dot.online) {
  background: var(--color-libre);
  box-shadow: 0 0 8px var(--color-libre);
}
:deep(.health-dot.offline) {
  background: var(--color-ocupado);
  box-shadow: 0 0 8px var(--color-ocupado);
}

/* Forms & Buttons */
:deep(.form-group) { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
:deep(.form-group label) { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
:deep(.form-group input), :deep(.form-group select) {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--text-main);
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
}
:deep(.form-group input:focus), :deep(.form-group select:focus) {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}
:deep(.btn-submit) {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}
:deep(.btn-submit:hover) { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(2, 132, 199, 0.5); }
:deep(.btn-secondary) {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-main);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 12px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
}
:deep(.btn-secondary:hover) { background: rgba(255, 255, 255, 0.15); }

:deep(#map-picker) { 
  width: 100%; 
  height: 210px; 
  min-height: 210px; 
  border-radius: 12px; 
  border: 1px solid var(--glass-border); 
  margin-bottom: 6px; 
  position: relative;
  z-index: 1;
}

:deep(#global-map) { 
  width: 100%; 
  height: 440px; 
  min-height: 440px; 
  border-radius: 14px; 
  border: 1px solid var(--glass-border); 
  position: relative;
  z-index: 1;
}

:deep(.leaflet-pane img),
:deep(.leaflet-tile),
:deep(.leaflet-marker-icon),
:deep(.leaflet-marker-shadow) {
  max-width: none !important;
  max-height: none !important;
}

:deep(.leaflet-container) {
  font-family: 'Plus Jakarta Sans', sans-serif;
  width: 100% !important;
  height: 100% !important;
}

/* Tables */
:deep(.table-wrapper) { overflow-x: auto; overflow-y: auto; max-height: 400px; margin-top: 10px; border-radius: 10px; }
:deep(table) { width: 100%; border-collapse: collapse; text-align: left; }
:deep(th) {
  padding: 12px 14px;
  font-size: 0.78rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 600;
  border-bottom: 1px solid var(--glass-border);
  position: sticky;
  top: 0;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(5px);
  z-index: 2;
}
:deep(td) {
  padding: 12px 14px;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  color: #e2e8f0;
}
:deep(.status-badge) { padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; display: inline-block; }
:deep(.status-badge.libre) { background: rgba(16, 185, 129, 0.15); color: #34d399; }
:deep(.status-badge.ocupado) { background: rgba(239, 68, 68, 0.15); color: #f87171; }
:deep(.status-badge.reservado) { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
:deep(.status-badge.activa) { background: rgba(16, 185, 129, 0.15); color: #34d399; }
:deep(.status-badge.cancelada) { background: rgba(239, 68, 68, 0.15); color: #f87171; }

:deep(.btn-action) {
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--glass-border);
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
:deep(.btn-action:hover) { background: rgba(255,255,255,0.18); transform: translateY(-1px); }

/* Toast */
.alert-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  color: #fff;
  padding: 14px 20px;
  border-radius: 12px;
  font-weight: 500;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  animation: slideIn 0.3s ease forwards;
}
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

.incidencia-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(239, 68, 68, 0.08);
  border-left: 3px solid #ef4444;
  border-radius: 8px;
  margin-bottom: 8px;
}
.incidencia-row .date { font-size: 0.75rem; color: #94a3b8; }
.incidencia-row .desc { font-size: 0.9rem; margin-top: 2px; }

:deep(.two-cols) { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; }

/* Modal overlay */
:deep(.modal-overlay) {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(6px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
:deep(.modal-content) {
  max-width: 92%;
  position: relative;
}

/* Mobile Bar */
.mobile-bar {
  display: none;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--sidebar-bg);
  border-bottom: 1px solid var(--glass-border);
  width: 100%;
}
.mobile-bar .toggle-btn {
  background: none;
  border: none;
  color: var(--text-main);
  font-size: 1.4rem;
  cursor: pointer;
}

/* Light mode overrides */
.admin-app-root.light-mode .nav-item { color: #64748b; }
.admin-app-root.light-mode .nav-item:hover { background: #f1f5f9; color: #0f172a; }
.admin-app-root.light-mode :deep(.card) {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05);
}
.admin-app-root.light-mode :deep(.card-title), 
.admin-app-root.light-mode :deep(td),
.admin-app-root.light-mode h1,
.admin-app-root.light-mode :deep(h2),
.admin-app-root.light-mode :deep(h3) { color: #0f172a !important; }
.admin-app-root.light-mode :deep(th) {
  background: #f8fafc;
  color: #64748b;
  border-bottom-color: #e2e8f0;
}
.admin-app-root.light-mode :deep(td) { border-bottom-color: #f1f5f9; }
.admin-app-root.light-mode :deep(.form-group input), 
.admin-app-root.light-mode :deep(.form-group select),
.admin-app-root.light-mode :deep(input[type="text"]),
.admin-app-root.light-mode :deep(input[type="email"]),
.admin-app-root.light-mode :deep(input[type="password"]),
.admin-app-root.light-mode :deep(input[type="number"]),
.admin-app-root.light-mode :deep(select) {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: #cbd5e1 !important;
}
.admin-app-root.light-mode :deep(input::placeholder) {
  color: #94a3b8 !important;
}
.admin-app-root.light-mode :deep(.stat-box) { background: #ffffff; border: 1px solid #e2e8f0; }
.admin-app-root.light-mode :deep(.health-item) { background: #ffffff; border-color: #e2e8f0; }
.admin-app-root.light-mode :deep(.btn-action) {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.admin-app-root.light-mode :deep(.btn-action:hover) { background: #e2e8f0; }
.admin-app-root.light-mode :deep(.btn-secondary) {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.admin-app-root.light-mode :deep(.btn-secondary:hover) { background: #e2e8f0; }
.admin-app-root.light-mode .theme-toggle-btn {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.admin-app-root.light-mode .theme-toggle-btn:hover { background: #e2e8f0; }
.admin-app-root.light-mode .incidencia-row { background: rgba(239, 68, 68, 0.05); }

@media (max-width: 1200px) {
  :deep(.stats-row) { grid-template-columns: repeat(3, 1fr); }
  :deep(.health-grid) { grid-template-columns: repeat(2, 1fr); }
  :deep(.two-cols) { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .admin-app-root { flex-direction: column; height: auto; overflow: auto; }
  .mobile-bar { display: flex; }
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 260px;
    transform: translateX(-100%);
    box-shadow: 5px 0 25px rgba(0,0,0,0.5);
  }
  .sidebar.open { transform: translateX(0); }
  .main-content { padding: 20px 15px; }
  :deep(.stats-row) { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .top-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  :deep(.health-grid) { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  :deep(.stats-row) { grid-template-columns: 1fr; }
  :deep(.stat-value) { font-size: 1.5rem; }
}
</style>
