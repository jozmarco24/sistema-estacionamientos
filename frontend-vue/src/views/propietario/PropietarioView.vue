<template>
  <div class="propietario-app-root" :class="{ 'light-mode': themeStore.isLight }">
    <!-- Sidebar Propietario -->
    <aside class="sidebar" id="sidebar">
      <div class="logo-area">
        <i class="fa-solid fa-parking"></i> SmartPark Dueño
      </div>
      <ul class="nav-menu">
        <router-link
          v-if="authStore.user?.rol === 'admin'"
          to="/admin"
          class="nav-item back-admin-btn"
        >
          <i class="fa-solid fa-arrow-left"></i> Volver a Admin
        </router-link>

        <div class="nav-divider">Centro de Negocio</div>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-resumen' }"
          @click.prevent="switchSection('sec-resumen')"
        >
          <i class="fa-solid fa-chart-pie"></i> Resumen Operativo
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-finanzas' || currentSection === 'sec-cobros' }"
          @click.prevent="switchSection('sec-finanzas')"
        >
          <i class="fa-solid fa-wallet"></i> Finanzas & Cobros
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-sedes' || currentSection === 'sec-slots' }"
          @click.prevent="switchSection('sec-sedes')"
        >
          <i class="fa-solid fa-warehouse"></i> Mis Sedes & Slots
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-personal' }"
          @click.prevent="switchSection('sec-personal')"
        >
          <i class="fa-solid fa-users-gear"></i> Mi Personal
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-suscripcion' }"
          @click.prevent="switchSection('sec-suscripcion')"
        >
          <i class="fa-solid fa-gem"></i> Mi Suscripción
        </a>

        <a href="#" class="nav-item logout-btn" @click.prevent="logout">
          <i class="fa-solid fa-right-from-bracket"></i> Cerrar Sesión
        </a>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Toast Alert -->
      <div
        v-if="toast.show"
        class="alert-toast"
        :style="{ background: toast.isError ? 'rgba(239, 68, 68, 0.95)' : 'rgba(16, 185, 129, 0.95)' }"
      >
        {{ toast.msg }}
      </div>

      <!-- Header -->
      <div class="top-header">
        <div class="greeting">
          <h1>{{ sectionTitles[currentSection]?.title || 'Resumen Operativo' }}</h1>
          <p>{{ sectionTitles[currentSection]?.sub || 'Métricas en tiempo real, mapa de sedes y monitoreo de incidencias.' }}</p>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
          <!-- Widget Reloj Digital y Fecha en Vivo -->
          <div class="live-clock-widget">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="pulse-dot"></span>
              <div style="text-align: right;">
                <div class="clock-time">{{ liveTime }}</div>
                <div class="clock-date">{{ liveDate }}</div>
              </div>
            </div>
          </div>

          <button @click="refreshAll" class="btn-action" title="Recargar datos">
            <i class="fa-solid fa-rotate" :class="{ 'fa-spin': isRefreshing }"></i> Actualizar
          </button>
          <button @click="themeStore.toggleTheme" class="theme-toggle-btn">
            <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
            <span>{{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}</span>
          </button>
        </div>
      </div>

      <!-- Dynamic Subcomponents -->
      <component
        :is="currentSectionComponent"
        v-bind="currentSectionProps"
        @refresh="refreshAll"
        @refresh-supervision="loadSupervisionAndChart"
        @filtro-sede-change="onFiltroSedeChange"
        @toast="onChildToast"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { usuariosService } from '@/services/usuarios'
import { pagosService } from '@/services/pagos'

import PropResumen from './PropResumen.vue'
import PropFinanzas from './PropFinanzas.vue'
import PropSedes from './PropSedes.vue'
import PropPersonal from './PropPersonal.vue'
import PropSuscripcion from './PropSuscripcion.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const currentSection = ref('sec-resumen')
const isRefreshing = ref(false)

const sectionTitles = {
  'sec-resumen': { title: 'Resumen Operativo', sub: 'Métricas en tiempo real, mapa de sedes y monitoreo de incidencias.' },
  'sec-finanzas': { title: 'Finanzas & Cobros', sub: 'Cuenta bancaria de cobro directo, conciliación de ingresos y transacciones.' },
  'sec-cobros': { title: 'Configurar Cobros', sub: 'Administra y verifica tus credenciales de Culqi para cobros de reservas.' },
  'sec-sedes': { title: 'Gestión de Sedes y Slots', sub: 'Administra tus locales, tarifas por hora y cajones de estacionamiento.' },
  'sec-slots': { title: 'Control de Espacios (Slots)', sub: 'Supervisa cajones libres, ocupados y genera nuevos en lote.' },
  'sec-personal': { title: 'Mi Personal (Operadores)', sub: 'Asigna trabajadores a tus sedes para el control de accesos.' },
  'sec-suscripcion': { title: 'Planes SaaS & Membresía', sub: 'Monitorea el uso de tus recursos y adquiere ampliaciones.' }
}

const sectionComponentMap = {
  'sec-resumen': PropResumen,
  'sec-finanzas': PropFinanzas,
  'sec-cobros': PropFinanzas,
  'sec-sedes': PropSedes,
  'sec-slots': PropSedes,
  'sec-personal': PropPersonal,
  'sec-suscripcion': PropSuscripcion
}

const currentSectionComponent = computed(() => sectionComponentMap[currentSection.value] || PropResumen)

// Live Clock
const liveTime = ref('00:00:00')
const liveDate = ref('Cargando...')
let clockInterval = null

// Data
const misSedes = ref([])
const allSpaces = ref([])
const operadoresList = ref([])
const incidenciasList = ref([])
const pagosRecibidosList = ref([])
const planesDisponibles = ref([])
const suscripcionActual = ref(null)

// Metrics
const stats = reactive({ libres: 0, reservados: 0, ocupados: 0 })
const totalGanancia = ref(0)
const filtroFinanzasSede = ref('')

// Toast
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

const currentSectionProps = computed(() => {
  switch (currentSection.value) {
    case 'sec-resumen':
      return {
        misSedes: misSedes.value,
        stats,
        incidenciasList: incidenciasList.value
      }
    case 'sec-finanzas':
    case 'sec-cobros':
      return {
        misSedes: misSedes.value,
        pagosRecibidosList: pagosRecibidosList.value,
        totalGanancia: totalGanancia.value
      }
    case 'sec-sedes':
    case 'sec-slots':
      return {
        misSedes: misSedes.value,
        allSpaces: allSpaces.value,
        userId: authStore.user?.id || 0
      }
    case 'sec-personal':
      return {
        operadoresList: operadoresList.value,
        misSedes: misSedes.value
      }
    case 'sec-suscripcion':
      return {
        suscripcionActual: suscripcionActual.value,
        planesDisponibles: planesDisponibles.value,
        misSedes: misSedes.value,
        operadoresList: operadoresList.value
      }
    default:
      return {}
  }
})

function switchSection(secId) {
  currentSection.value = secId
}

function onFiltroSedeChange(sedeId) {
  filtroFinanzasSede.value = sedeId
  loadSupervisionAndChart()
}

function startLiveClock() {
  const update = () => {
    const now = new Date()
    liveTime.value = now.toLocaleTimeString('es-PE', { hour12: false })
    liveDate.value = now.toLocaleDateString('es-PE', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
  }
  update()
  clockInterval = setInterval(update, 1000)
}

async function refreshAll() {
  isRefreshing.value = true
  try {
    await Promise.all([
      loadSedes(),
      loadOperadores(),
      checkSuscripcion(),
      loadIncidencias()
    ])
    await loadSupervisionAndChart()
  } finally {
    isRefreshing.value = false
  }
}

async function loadSedes() {
  try {
    const propId = authStore.user?.id
    if (!propId) return
    const res = await estacionamientosService.getSedesPorPropietario(propId)
    misSedes.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    console.error('Error cargando sedes propietario:', err)
  }
}

async function loadOperadores() {
  try {
    const res = await usuariosService.getOperadores()
    operadoresList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    console.error('Error cargando operadores:', err)
  }
}

async function checkSuscripcion() {
  try {
    const [subRes, planRes] = await Promise.all([
      usuariosService.getMiSuscripcion().catch(() => null),
      usuariosService.getPlanes()
    ])
    if (subRes && subRes.data) {
      suscripcionActual.value = subRes.data
    }
    planesDisponibles.value = planRes.data || []
  } catch (err) {}
}

async function loadIncidencias() {
  try {
    const res = await estacionamientosService.getIncidencias(0, 50)
    const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    const sedeIds = misSedes.value.map(s => s.id)
    incidenciasList.value = list.filter(inc => sedeIds.includes(inc.sede_id))
  } catch (err) {
    console.error('Error incidencias:', err)
  }
}

async function loadSupervisionAndChart() {
  try {
    if (misSedes.value.length === 0) return

    const spaces = []
    let tLibres = 0, tRes = 0, tOcu = 0

    for (const s of misSedes.value) {
      try {
        const espRes = await estacionamientosService.getEspaciosPorSede(s.id)
        const espList = Array.isArray(espRes.data) ? espRes.data : (espRes.data?.data || [])
        espList.forEach(e => {
          e.sede_nombre = s.nombre
          spaces.push(e)
          if (e.estado === 'libre') tLibres++
          else if (e.estado === 'reservado') tRes++
          else tOcu++
        })
      } catch (e) {}
    }

    allSpaces.value = spaces
    stats.libres = tLibres
    stats.reservados = tRes
    stats.ocupados = tOcu

    const propId = authStore.user?.id
    if (!propId) return
    const pRes = await pagosService.getPagosPorPropietario(propId)
    let pagos = Array.isArray(pRes.data) ? pRes.data : (pRes.data?.data || [])

    if (filtroFinanzasSede.value) {
      const sid = parseInt(filtroFinanzasSede.value)
      pagos = pagos.filter(p => p.sede_id === sid)
    }
    pagosRecibidosList.value = pagos

    let total = 0
    pagos.forEach(p => {
      const st = (p.estado || '').toLowerCase()
      if (st === 'completado' || st === 'pagado' || st === 'aprobado') {
        total += (parseFloat(p.monto) || 0)
      }
    })
    totalGanancia.value = total
  } catch (err) {
    console.error('Error supervisión/finanzas:', err)
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
  startLiveClock()
  await refreshAll()
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
})
</script>

<style scoped>
.propietario-app-root {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-color, #0b0f19);
  background-image: 
    radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.1) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.08) 0px, transparent 50%);
  color: var(--text-main, #f8fafc);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

:deep(.leaflet-layer), :deep(.leaflet-control-zoom-in), :deep(.leaflet-control-zoom-out), :deep(.leaflet-control-attribution) {
  filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);
}

.propietario-app-root.light-mode :deep(.leaflet-layer),
.propietario-app-root.light-mode :deep(.leaflet-control-zoom-in),
.propietario-app-root.light-mode :deep(.leaflet-control-zoom-out),
.propietario-app-root.light-mode :deep(.leaflet-control-attribution) {
  filter: none;
}

.propietario-app-root {
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

.propietario-app-root.light-mode {
  --bg-color: #f8fafc;
  --sidebar-bg: rgba(255, 255, 255, 0.95);
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0;
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #0284c7;
  --text-main: #0f172a;
  --text-muted: #64748b;
}

/* ===== INNER TABS ===== */
:deep(.inner-tabs) {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--glass-border);
  padding-bottom: 0;
  flex-wrap: wrap;
}

:deep(.inner-tab-btn) {
  padding: 8px 18px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

:deep(.inner-tab-btn:hover) {
  color: var(--text-main);
  background: var(--glass-bg);
}

:deep(.inner-tab-btn.active) {
  color: var(--accent);
  border-bottom-color: var(--accent);
  background: var(--glass-bg);
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

.back-admin-btn {
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.2) 0%, rgba(3, 105, 161, 0.2) 100%);
  color: var(--accent);
  border: 1px solid rgba(2, 132, 199, 0.4);
}

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

/* Main */
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

/* Clock Widget */
.live-clock-widget {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  padding: 8px 16px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
.pulse-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 10px #10b981;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
.clock-time {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
}
.clock-date {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

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

/* Ocupacion banner */
:deep(.ocupacion-banner) {
  margin-bottom: 20px;
  padding: 18px 22px;
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.08) 0%, rgba(56, 189, 248, 0.04) 100%);
  border: 1px solid rgba(2, 132, 199, 0.25);
}
:deep(.progress-bar-bg) {
  background: rgba(255,255,255,0.06);
  border-radius: 12px;
  height: 12px;
  overflow: hidden;
}
:deep(.progress-bar-fill) {
  background: linear-gradient(90deg, #10b981 0%, #f59e0b 60%, #ef4444 100%);
  height: 100%;
  transition: width 0.8s ease;
}

/* Stats */
:deep(.stats-row) { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
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
:deep(.stat-box.ingresos) { border-bottom: 3px solid var(--accent); }
:deep(.stat-label) { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
:deep(.stat-value) { font-size: 1.8rem; font-weight: 800; }

:deep(.two-cols) { display: grid; grid-template-columns: 1.5fr 1fr; gap: 22px; }

/* Forms */
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
:deep(.form-group input:focus), :deep(.form-group select:focus) { border-color: var(--primary); }

:deep(.tarifas-matrix-box) {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--glass-border);
  padding: 14px;
  border-radius: 12px;
  margin-bottom: 14px;
}

:deep(.btn-submit) {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.2s, opacity 0.2s;
}
:deep(.btn-submit:active) { transform: scale(0.98); }
:deep(.btn-action) {
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
:deep(.btn-action:hover) { background: rgba(255,255,255,0.12); }
:deep(.btn-secondary) {
  background: transparent;
  border: 1px solid var(--glass-border);
  color: var(--text-muted);
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
}

:deep(#owner-map) { width: 100%; height: 400px; min-height: 400px; border-radius: 14px; border: 1px solid var(--glass-border); }
:deep(#map-picker-prop) { width: 100%; height: 260px; min-height: 260px; border-radius: 12px; border: 1px solid var(--glass-border); margin-bottom: 6px; }

/* Tables */
:deep(.table-wrapper) { overflow-x: auto; width: 100%; }
:deep(table) { width: 100%; border-collapse: collapse; text-align: left; }
:deep(th) { padding: 12px 16px; font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--glass-border); }
:deep(td) { padding: 12px 16px; font-size: 0.95rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: #e2e8f0; vertical-align: middle; }

:deep(.status-badge) { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; }
:deep(.status-badge.libre) { background: rgba(16, 185, 129, 0.15); color: #34d399; }
:deep(.status-badge.ocupado) { background: rgba(239, 68, 68, 0.15); color: #f87171; }
:deep(.status-badge.reservado) { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

:deep(.incidencia-row) {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444;
  border-radius: 8px; margin-bottom: 8px;
}

.alert-toast {
  position: fixed; top: 20px; right: 20px; z-index: 3000;
  color: #fff; padding: 14px 22px; border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4); font-weight: 500;
}

/* Revenue summary pill */
:deep(.revenue-summary-pill) {
  margin-top: 14px; padding: 12px 16px;
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.25);
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.suscripcion-status-card) {
  margin-bottom: 20px; padding: 20px; border-radius: 14px;
  background: rgba(2, 132, 199, 0.08); border: 1px solid var(--primary);
}
:deep(.plan-card-item) {
  background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border);
  padding: 16px; border-radius: 12px; display: flex;
  justify-content: space-between; align-items: center;
}

/* Payment modal */
:deep(.payment-modal-overlay) {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(6px);
  display: flex; justify-content: center; align-items: center; z-index: 2000;
}
:deep(.payment-modal) {
  background: var(--bg-color); border: 1px solid var(--glass-border);
  border-radius: 16px; width: 420px; max-width: 90%; padding: 24px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5); position: relative;
}
:deep(.payment-header) {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; border-bottom: 1px solid var(--glass-border); padding-bottom: 15px;
}
:deep(.card-preview) {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);
}
:deep(.pay-amount) { font-size: 1.8rem; font-weight: 800; color: #fff; }
:deep(.pay-plan-name) { color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
:deep(.btn-pay-now) {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  width: 100%; padding: 14px; border: none; border-radius: 10px;
  color: white; font-size: 1rem; font-weight: 600; cursor: pointer;
  margin-top: 10px; display: flex; justify-content: center; align-items: center; gap: 10px;
}
:deep(.info-alert-culqi) {
  background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.25);
  border-radius: 12px; padding: 14px; margin-bottom: 18px; font-size: 0.85rem; line-height: 1.5;
}

:deep(.alert-inline) {
  padding: 12px 16px; border-radius: 12px; font-size: 0.88rem;
  display: flex; align-items: center; gap: 10px; margin-top: 4px;
}
:deep(.alert-success) { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; }
:deep(.alert-danger) { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171; }

/* Light mode overrides */
.propietario-app-root.light-mode .sidebar { background: rgba(255, 255, 255, 0.95); }
.propietario-app-root.light-mode .nav-item { color: #64748b; }
.propietario-app-root.light-mode .nav-item:hover { background: #f1f5f9; color: #0f172a; }
.propietario-app-root.light-mode :deep(.card) { background: #ffffff; border-color: #e2e8f0; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05); }
.propietario-app-root.light-mode :deep(.card-title), .propietario-app-root.light-mode :deep(td) { color: #0f172a; }
.propietario-app-root.light-mode :deep(th) { background: #f8fafc; color: #64748b; border-bottom-color: #e2e8f0; }
.propietario-app-root.light-mode :deep(td) { border-bottom-color: #f1f5f9; }
.propietario-app-root.light-mode :deep(.form-group input), .propietario-app-root.light-mode :deep(.form-group select) { background: #fff; color: #0f172a; border-color: #cbd5e1; }
.propietario-app-root.light-mode :deep(.stat-box) { background: #ffffff; border: 1px solid #e2e8f0; }
.propietario-app-root.light-mode :deep(.btn-action) { background: #f1f5f9; border-color: #cbd5e1; color: #0f172a; }
.propietario-app-root.light-mode :deep(.btn-action:hover) { background: #e2e8f0; }

@media (max-width: 900px) {
  :deep(.two-cols) { grid-template-columns: 1fr; }
  :deep(.stats-row) { grid-template-columns: 1fr 1fr; }
}
</style>
