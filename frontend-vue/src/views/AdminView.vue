<template>
  <div class="min-h-screen flex bg-slate-900 text-slate-100">
    <!-- Sidebar Izquierdo -->
    <aside class="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0">
      <div>
        <!-- Brand -->
        <div class="p-6 border-b border-slate-800 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500 to-amber-600 flex items-center justify-center text-white shadow-md">
              <i class="fa-solid fa-shield-halved text-xl"></i>
            </div>
            <div>
              <h1 class="font-bold text-base leading-tight">SmartPark</h1>
              <span class="text-xs text-rose-400 font-semibold tracking-wide">ADMINISTRACIÓN</span>
            </div>
          </div>
        </div>

        <!-- Menú -->
        <nav class="p-4 space-y-1">
          <button
            v-for="item in menuItems"
            :key="item.id"
            @click="activeTab = item.id"
            class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all"
            :class="activeTab === item.id 
              ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/30' 
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'"
          >
            <i :class="item.icon" class="w-5 text-center"></i>
            <span>{{ item.label }}</span>
          </button>
        </nav>
      </div>

      <!-- Footer Perfil -->
      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center justify-between p-2 rounded-xl bg-slate-900 border border-slate-800 mb-3">
          <div class="truncate mr-2">
            <p class="text-xs font-bold text-slate-200 truncate">{{ authStore.userName }}</p>
            <p class="text-[11px] text-rose-400 font-semibold">Super Admin</p>
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

    <!-- Área de Contenido -->
    <main class="flex-1 overflow-y-auto p-8 bg-slate-900/60">
      <!-- Top Title -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl font-black text-white tracking-tight">{{ currentTitle }}</h2>
          <p class="text-sm text-slate-400">Control maestro de la plataforma SaaS y microservicios</p>
        </div>
      </div>

      <!-- Tab 1: Dashboard y Gráficos -->
      <section v-if="activeTab === 'dashboard'" class="space-y-6">
        <!-- 4 Tarjetas de Métricas -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Usuarios</span>
            <div class="text-3xl font-extrabold text-sky-400 mt-2">{{ usuariosTotal }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Sedes Globales</span>
            <div class="text-3xl font-extrabold text-emerald-400 mt-2">{{ sedesList.length }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Reservas</span>
            <div class="text-3xl font-extrabold text-indigo-400 mt-2">{{ reservasList.length }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Ingresos Totales</span>
            <div class="text-3xl font-extrabold text-amber-400 mt-2">S/. {{ totalIngresosCalculados.toFixed(2) }}</div>
          </div>
        </div>

        <!-- Gráfico Chart.js -->
        <div class="p-6 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
          <h3 class="font-bold text-base text-white mb-4"><i class="fa-solid fa-chart-column mr-2"></i>Volumen de Ingresos por Mes</h3>
          <div class="h-64">
            <canvas id="admin-chart"></canvas>
          </div>
        </div>
      </section>

      <!-- Tab 2: Propietarios CRUD -->
      <section v-if="activeTab === 'propietarios'" class="space-y-4">
        <div class="flex justify-between items-center">
          <input
            v-model="filtroProp"
            type="text"
            placeholder="Buscar propietario por nombre o email..."
            class="px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm w-72 text-white"
          />
          <div class="flex gap-2">
            <button
              @click="exportarPropietariosExcel"
              class="px-3.5 py-2 bg-emerald-600/80 hover:bg-emerald-600 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow"
            >
              <i class="fa-solid fa-file-excel"></i> Exportar Excel
            </button>
            <button
              @click="abrirModalCrearProp"
              class="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow"
            >
              <i class="fa-solid fa-user-plus"></i> Nuevo Propietario
            </button>
          </div>
        </div>

        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="px-5 py-3.5">ID</th>
                <th class="px-5 py-3.5">Nombre</th>
                <th class="px-5 py-3.5">Email</th>
                <th class="px-5 py-3.5">Estado</th>
                <th class="px-5 py-3.5 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/60">
              <tr v-for="p in propietariosFiltrados" :key="p.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ p.id }}</td>
                <td class="px-5 py-4 font-bold text-white">{{ p.nombre }}</td>
                <td class="px-5 py-4 text-xs">{{ p.email }}</td>
                <td class="px-5 py-4">
                  <span
                    class="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase"
                    :class="p.activo ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'"
                  >
                    {{ p.activo ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td class="px-5 py-4 text-right space-x-2">
                  <button
                    @click="toggleActivoProp(p)"
                    class="px-2.5 py-1 text-xs rounded border border-slate-600 hover:bg-slate-700"
                    :title="p.activo ? 'Desactivar' : 'Activar'"
                  >
                    <i :class="p.activo ? 'fa-solid fa-user-slash text-amber-400' : 'fa-solid fa-user-check text-emerald-400'"></i>
                  </button>
                  <button
                    @click="abrirModalEditarProp(p)"
                    class="px-2.5 py-1 text-xs rounded border border-slate-600 hover:bg-slate-700 text-sky-400"
                  >
                    <i class="fa-solid fa-pen"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 3: Sedes Globales -->
      <section v-if="activeTab === 'sedes'" class="space-y-4">
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="px-5 py-3.5">ID</th>
                <th class="px-5 py-3.5">Nombre Sede</th>
                <th class="px-5 py-3.5">Dirección</th>
                <th class="px-5 py-3.5">Propietario ID</th>
                <th class="px-5 py-3.5">Tarifa Base</th>
                <th class="px-5 py-3.5">Estado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/60">
              <tr v-for="s in sedesList" :key="s.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ s.id }}</td>
                <td class="px-5 py-4 font-bold text-white">{{ s.nombre }}</td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ s.direccion }}</td>
                <td class="px-5 py-4 font-mono text-xs">Propietario #{{ s.propietario_id }}</td>
                <td class="px-5 py-4 font-bold text-emerald-400">S/. {{ (s.tarifa_hora || 5).toFixed(2) }}</td>
                <td class="px-5 py-4">
                  <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Activa
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 4: Pagos Globales -->
      <section v-if="activeTab === 'pagos'" class="space-y-4">
        <div class="flex justify-end">
          <button
            @click="exportarPagosExcel"
            class="px-3.5 py-2 bg-emerald-600/80 hover:bg-emerald-600 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow"
          >
            <i class="fa-solid fa-file-excel"></i> Exportar Excel
          </button>
        </div>
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
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
              <tr v-for="p in pagosList" :key="p.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ p.id }}</td>
                <td class="px-5 py-4 text-xs font-bold uppercase text-slate-400">{{ p.tipo }}</td>
                <td class="px-5 py-4 font-bold text-white">S/. {{ (p.monto || 0).toFixed(2) }}</td>
                <td class="px-5 py-4 text-xs capitalize">{{ p.metodo_pago }}</td>
                <td class="px-5 py-4">
                  <span
                    class="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase border"
                    :class="p.estado === 'completado' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'"
                  >
                    {{ p.estado }}
                  </span>
                </td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ p.fecha_creacion || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 5: Reservas Globales -->
      <section v-if="activeTab === 'reservas'" class="space-y-4">
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="px-5 py-3.5">ID</th>
                <th class="px-5 py-3.5">Usuario ID</th>
                <th class="px-5 py-3.5">Espacio ID</th>
                <th class="px-5 py-3.5">Fecha Inicio</th>
                <th class="px-5 py-3.5">Fecha Fin</th>
                <th class="px-5 py-3.5">Estado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/60">
              <tr v-for="r in reservasList" :key="r.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ r.id }}</td>
                <td class="px-5 py-4 font-mono text-xs">Usuario #{{ r.usuario_id }}</td>
                <td class="px-5 py-4">Espacio #{{ r.espacio_id }}</td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ r.fecha_inicio }}</td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ r.fecha_fin }}</td>
                <td class="px-5 py-4">
                  <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase border bg-slate-800 border-slate-600">
                    {{ r.estado }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 6: Mapa Global -->
      <section v-if="activeTab === 'mapa'" class="space-y-4">
        <div class="rounded-2xl border border-slate-700 overflow-hidden shadow-xl h-[520px]">
          <div id="admin-map" class="w-full h-full"></div>
        </div>
      </section>

      <!-- Tab 7: Sistema / Health Checks -->
      <section v-if="activeTab === 'sistema'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div
            v-for="(svc, name) in healthStatus"
            :key="name"
            class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card flex items-center justify-between"
          >
            <div>
              <span class="text-xs uppercase tracking-wider font-bold text-slate-400">{{ name }}</span>
              <p class="text-xs text-slate-500 mt-1">Puerto: {{ svc.port }}</p>
            </div>
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-base"
              :class="svc.ok ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'"
            >
              <i :class="svc.ok ? 'fa-solid fa-check' : 'fa-solid fa-xmark'"></i>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Crear / Editar Propietario -->
    <div v-if="modalProp.open" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <h3 class="text-lg font-bold text-white mb-4">
          {{ modalProp.isEdit ? 'Editar Propietario' : 'Nuevo Propietario' }}
        </h3>
        <form @submit.prevent="guardarProp" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">Nombre</label>
            <input v-model="modalProp.form.nombre" type="text" required class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">Email</label>
            <input v-model="modalProp.form.email" type="email" required class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">{{ modalProp.isEdit ? 'Nueva Contraseña (opcional)' : 'Contraseña' }}</label>
            <input v-model="modalProp.form.password" :required="!modalProp.isEdit" type="password" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button @click="modalProp.open = false" type="button" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-bold">Cancelar</button>
            <button type="submit" class="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { usuariosService } from '@/services/usuarios'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { pagosService } from '@/services/pagos'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import L from 'leaflet'
import Chart from 'chart.js/auto'
import * as XLSX from 'xlsx'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const activeTab = ref('dashboard')
const sedesList = ref([])
const reservasList = ref([])
const pagosList = ref([])
const propietariosList = ref([])
const usuariosTotal = ref(0)
const filtroProp = ref('')

let adminMap = null
let adminChartInstance = null

const healthStatus = ref({
  'Usuarios': { port: 8001, ok: true },
  'Estacionamientos': { port: 8002, ok: true },
  'Reservas': { port: 8003, ok: true },
  'Pagos': { port: 8004, ok: true },
})

const modalProp = ref({
  open: false,
  isEdit: false,
  id: null,
  form: { nombre: '', email: '', password: '' }
})

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'fa-solid fa-chart-line' },
  { id: 'propietarios', label: 'Propietarios', icon: 'fa-solid fa-users' },
  { id: 'sedes', label: 'Sedes', icon: 'fa-solid fa-building' },
  { id: 'pagos', label: 'Pagos Globales', icon: 'fa-solid fa-credit-card' },
  { id: 'reservas', label: 'Reservas Globales', icon: 'fa-solid fa-list-check' },
  { id: 'mapa', label: 'Mapa Global', icon: 'fa-solid fa-earth-americas' },
  { id: 'sistema', label: 'Sistema / Health', icon: 'fa-solid fa-heart-pulse' },
]

const currentTitle = computed(() => {
  return menuItems.find(m => m.id === activeTab.value)?.label || 'Panel de Administración'
})

const totalIngresosCalculados = computed(() => {
  return pagosList.value.reduce((acc, p) => acc + (p.monto || 0), 0)
})

const propietariosFiltrados = computed(() => {
  if (!filtroProp.value.trim()) return propietariosList.value
  const q = filtroProp.value.toLowerCase()
  return propietariosList.value.filter(p => 
    p.nombre?.toLowerCase().includes(q) || p.email?.toLowerCase().includes(q)
  )
})

onMounted(async () => {
  themeStore.initTheme(true)
  await cargarTodo()
  checkHealth()
  renderChart()
})

watch(activeTab, (tab) => {
  if (tab === 'mapa') {
    nextTick(() => initMap())
  }
  if (tab === 'dashboard') {
    nextTick(() => renderChart())
  }
})

const cargarTodo = async () => {
  try {
    const [uRes, pRes, sRes, rRes, pagRes] = await Promise.allSettled([
      usuariosService.getUsuarios(0, 100),
      usuariosService.getPropietarios(),
      estacionamientosService.getSedes(0, 100),
      reservasService.getReservas(0, 100),
      pagosService.getPagos(0, 100)
    ])

    if (uRes.status === 'fulfilled') {
      const uData = uRes.value.data
      usuariosTotal.value = uData?.total || (Array.isArray(uData) ? uData.length : (uData?.data?.length || 0))
    }
    if (pRes.status === 'fulfilled') {
      propietariosList.value = pRes.value.data || []
    }
    if (sRes.status === 'fulfilled') {
      const sData = sRes.value.data
      sedesList.value = Array.isArray(sData) ? sData : (sData?.data || [])
    }
    if (rRes.status === 'fulfilled') {
      const rData = rRes.value.data
      reservasList.value = Array.isArray(rData) ? rData : (rData?.data || [])
    }
    if (pagRes.status === 'fulfilled') {
      const pData = pagRes.value.data
      pagosList.value = Array.isArray(pData) ? pData : (pData?.data || [])
    }
  } catch (err) {
    console.error('Error cargando datos admin:', err)
  }
}

const checkHealth = async () => {
  try {
    const [u, e, r, p] = await Promise.allSettled([
      usuariosService.health(),
      estacionamientosService.health(),
      reservasService.health(),
      pagosService.health()
    ])
    healthStatus.value['Usuarios'].ok = u.status === 'fulfilled'
    healthStatus.value['Estacionamientos'].ok = e.status === 'fulfilled'
    healthStatus.value['Reservas'].ok = r.status === 'fulfilled'
    healthStatus.value['Pagos'].ok = p.status === 'fulfilled'
  } catch (err) {}
}

const renderChart = () => {
  const canvas = document.getElementById('admin-chart')
  if (!canvas) return
  if (adminChartInstance) {
    adminChartInstance.destroy()
  }
  adminChartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct'],
      datasets: [{
        label: 'Ingresos MRR (S/.)',
        data: [1200, 1900, 3000, 2500, 4200, 5100, 4800, 6200, 7500, totalIngresosCalculados.value || 8900],
        backgroundColor: 'rgba(2, 132, 199, 0.75)',
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' } },
        x: { grid: { display: false } }
      }
    }
  })
}

const initMap = () => {
  if (adminMap) {
    adminMap.remove()
    adminMap = null
  }
  const el = document.getElementById('admin-map')
  if (!el) return
  adminMap = L.map('admin-map').setView([-12.046374, -77.042793], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(adminMap)

  sedesList.value.forEach(s => {
    if (s.latitud && s.longitud) {
      L.marker([s.latitud, s.longitud]).addTo(adminMap).bindPopup(`
        <strong>${s.nombre}</strong><br>${s.direccion}<br>Prop: #${s.propietario_id}
      `)
    }
  })
}

// Acciones Propietarios
const abrirModalCrearProp = () => {
  modalProp.value = { open: true, isEdit: false, id: null, form: { nombre: '', email: '', password: '' } }
}
const abrirModalEditarProp = (p) => {
  modalProp.value = { open: true, isEdit: true, id: p.id, form: { nombre: p.nombre, email: p.email, password: '' } }
}
const guardarProp = async () => {
  try {
    if (modalProp.value.isEdit) {
      await usuariosService.actualizarPropietario(modalProp.value.id, modalProp.value.form)
      showToast('Propietario actualizado', 'success')
    } else {
      await usuariosService.crearPropietario(modalProp.value.form)
      showToast('Propietario creado', 'success')
    }
    modalProp.value.open = false
    await cargarTodo()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar', 'error')
  }
}

const toggleActivoProp = async (p) => {
  try {
    await usuariosService.toggleActivoPropietario(p.id)
    showToast(`Estado de ${p.nombre} modificado`, 'success')
    await cargarTodo()
  } catch (err) {
    showToast('Error al cambiar estado', 'error')
  }
}

const exportarPropietariosExcel = () => {
  const ws = XLSX.utils.json_to_sheet(propietariosList.value)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Propietarios')
  XLSX.writeFile(wb, 'SmartPark_Propietarios.xlsx')
}

const exportarPagosExcel = () => {
  const ws = XLSX.utils.json_to_sheet(pagosList.value)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Pagos')
  XLSX.writeFile(wb, 'SmartPark_Pagos.xlsx')
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
