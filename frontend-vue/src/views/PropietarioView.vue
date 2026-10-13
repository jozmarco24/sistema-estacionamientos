<template>
  <div class="min-h-screen flex bg-slate-900 text-slate-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0">
      <div>
        <div class="p-6 border-b border-slate-800 flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-sky-600 flex items-center justify-center text-white shadow-md">
            <i class="fa-solid fa-building-user text-xl"></i>
          </div>
          <div>
            <h1 class="font-bold text-base leading-tight">SmartPark</h1>
            <span class="text-xs text-indigo-400 font-semibold tracking-wide">PROPIETARIO</span>
          </div>
        </div>

        <nav class="p-4 space-y-1">
          <button
            v-for="item in menuItems"
            :key="item.id"
            @click="activeTab = item.id"
            class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all"
            :class="activeTab === item.id 
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' 
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
            <p class="text-[11px] text-indigo-400 font-medium truncate">{{ authStore.user?.email }}</p>
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
          <p class="text-sm text-slate-400">Gestión de sedes comerciales, cajones, cobros y suscripción</p>
        </div>
        <div v-if="activeTab === 'sedes'">
          <button
            @click="abrirModalCrearSede"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow"
          >
            <i class="fa-solid fa-plus"></i> Nueva Sede
          </button>
        </div>
      </div>

      <!-- Tab 1: Dashboard Métricas -->
      <section v-if="activeTab === 'dashboard'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Mis Sedes</span>
            <div class="text-3xl font-extrabold text-indigo-400 mt-2">{{ misSedes.length }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Espacios Totales</span>
            <div class="text-3xl font-extrabold text-sky-400 mt-2">{{ espaciosList.length }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Reservas Recibidas</span>
            <div class="text-3xl font-extrabold text-emerald-400 mt-2">{{ reservasPropietario.length }}</div>
          </div>
          <div class="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Ganancias Netas</span>
            <div class="text-3xl font-extrabold text-amber-400 mt-2">S/. {{ totalGanancias.toFixed(2) }}</div>
          </div>
        </div>
      </section>

      <!-- Tab 2: Mis Sedes CRUD -->
      <section v-if="activeTab === 'sedes'" class="space-y-4">
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="px-5 py-3.5">ID</th>
                <th class="px-5 py-3.5">Nombre</th>
                <th class="px-5 py-3.5">Dirección</th>
                <th class="px-5 py-3.5">Tarifa Base</th>
                <th class="px-5 py-3.5">Estado</th>
                <th class="px-5 py-3.5 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/60">
              <tr v-for="s in misSedes" :key="s.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ s.id }}</td>
                <td class="px-5 py-4 font-bold text-white">{{ s.nombre }}</td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ s.direccion }}</td>
                <td class="px-5 py-4 font-bold text-emerald-400">S/. {{ (s.tarifa_hora || 5).toFixed(2) }}</td>
                <td class="px-5 py-4">
                  <span
                    class="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase border"
                    :class="s.activa ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'"
                  >
                    {{ s.activa ? 'Activa' : 'Inactiva' }}
                  </span>
                </td>
                <td class="px-5 py-4 text-right space-x-2">
                  <button
                    @click="toggleEstadoSede(s)"
                    class="px-2 py-1 text-xs border border-slate-600 rounded hover:bg-slate-700"
                    :title="s.activa ? 'Desactivar' : 'Activar'"
                  >
                    <i :class="s.activa ? 'fa-solid fa-power-off text-amber-400' : 'fa-solid fa-check text-emerald-400'"></i>
                  </button>
                  <button
                    @click="abrirModalEditarSede(s)"
                    class="px-2 py-1 text-xs border border-slate-600 rounded hover:bg-slate-700 text-sky-400"
                  >
                    <i class="fa-solid fa-pen"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 3: Espacios por Sede -->
      <section v-if="activeTab === 'espacios'" class="space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <label class="text-xs font-bold text-slate-400">Filtrar por Sede:</label>
            <select
              v-model="sedeSeleccionadaId"
              class="px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white"
            >
              <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
          </div>
          <button
            @click="abrirModalCrearEspacio"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow flex items-center gap-1.5"
          >
            <i class="fa-solid fa-plus"></i> Nuevo Espacio
          </button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
          <div
            v-for="esp in espaciosFiltrados"
            :key="esp.id"
            class="p-4 rounded-xl border flex flex-col items-center justify-center gap-1 glass-card"
            :class="{
              'border-emerald-500/30 text-emerald-400': esp.estado === 'libre',
              'border-rose-500/30 text-rose-400': esp.estado === 'ocupado',
              'border-amber-500/30 text-amber-400': esp.estado === 'reservado',
            }"
          >
            <span class="text-xs font-black">{{ esp.numero }}</span>
            <i class="fa-solid fa-car text-lg my-1"></i>
            <span class="text-[10px] uppercase font-bold">{{ esp.estado }}</span>
          </div>
        </div>
      </section>

      <!-- Tab 4: Pagos Recibidos -->
      <section v-if="activeTab === 'pagos'" class="space-y-4">
        <div class="rounded-2xl bg-slate-800/80 border border-slate-700 glass-card overflow-hidden">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="bg-slate-950/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th class="px-5 py-3.5">ID</th>
                <th class="px-5 py-3.5">Monto</th>
                <th class="px-5 py-3.5">Método</th>
                <th class="px-5 py-3.5">Estado</th>
                <th class="px-5 py-3.5">Fecha</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-700/60">
              <tr v-for="p in pagosPropietario" :key="p.id" class="hover:bg-slate-700/30">
                <td class="px-5 py-4 font-mono text-xs">#{{ p.id }}</td>
                <td class="px-5 py-4 font-bold text-white">S/. {{ (p.monto || 0).toFixed(2) }}</td>
                <td class="px-5 py-4 text-xs capitalize">{{ p.metodo_pago }}</td>
                <td class="px-5 py-4">
                  <span class="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {{ p.estado }}
                  </span>
                </td>
                <td class="px-5 py-4 text-xs text-slate-400">{{ p.fecha_creacion || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Tab 5: Suscripción SaaS & Culqi Checkout -->
      <section v-if="activeTab === 'suscripcion'" class="space-y-6 max-w-xl">
        <div class="p-6 rounded-2xl bg-slate-800/80 border border-slate-700 glass-card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-white">Plan SmartPark Activo</h3>
            <span class="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
              {{ suscripcionActual?.plan_nombre || 'Básico Pro' }}
            </span>
          </div>
          <p class="text-xs text-slate-400 leading-relaxed mb-6">
            Gestiona hasta 5 sedes simultáneas, reportes de auditoría en tiempo real y conciliación bancaria instantánea con Culqi.
          </p>

          <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 mb-6 flex justify-between items-center">
            <div>
              <span class="text-xs text-slate-400">Costo Mensual</span>
              <div class="text-2xl font-black text-white">S/. 99.00 <span class="text-xs font-normal text-slate-500">/ mes</span></div>
            </div>
            <button
              @click="abrirCulqiSuscripcion(99.00)"
              class="px-5 py-2.5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-sky-500/20 flex items-center gap-2"
            >
              <i class="fa-solid fa-bolt"></i> Actualizar con Culqi
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Crear Sede -->
    <div v-if="modalSede.open" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <h3 class="text-lg font-bold text-white mb-4">{{ modalSede.isEdit ? 'Editar Sede' : 'Nueva Sede' }}</h3>
        <form @submit.prevent="guardarSede" class="space-y-3">
          <div>
            <label class="block text-xs font-bold text-slate-400 mb-1">Nombre</label>
            <input v-model="modalSede.form.nombre" required type="text" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-400 mb-1">Dirección</label>
            <input v-model="modalSede.form.direccion" required type="text" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-400 mb-1">Latitud</label>
              <input v-model.number="modalSede.form.latitud" type="number" step="any" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 mb-1">Longitud</label>
              <input v-model.number="modalSede.form.longitud" type="number" step="any" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white" />
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button @click="modalSede.open = false" type="button" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-bold">Cancelar</button>
            <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold">Guardar Sede</button>
          </div>
        </form>
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
import { pagosService } from '@/services/pagos'
import { usuariosService } from '@/services/usuarios'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const activeTab = ref('dashboard')
const misSedes = ref([])
const espaciosList = ref([])
const reservasPropietario = ref([])
const pagosPropietario = ref([])
const suscripcionActual = ref(null)
const sedeSeleccionadaId = ref(null)

const modalSede = ref({
  open: false,
  isEdit: false,
  id: null,
  form: { nombre: '', direccion: '', latitud: -12.0463, longitud: -77.0427, tarifa_hora: 5 }
})

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'fa-solid fa-chart-pie' },
  { id: 'sedes', label: 'Mis Sedes', icon: 'fa-solid fa-building' },
  { id: 'espacios', label: 'Espacios', icon: 'fa-solid fa-border-all' },
  { id: 'pagos', label: 'Pagos / Ingresos', icon: 'fa-solid fa-coins' },
  { id: 'suscripcion', label: 'Suscripción SaaS', icon: 'fa-solid fa-crown' },
]

const currentTitle = computed(() => {
  return menuItems.find(m => m.id === activeTab.value)?.label || 'Panel de Propietario'
})

const espaciosFiltrados = computed(() => {
  if (!sedeSeleccionadaId.value) return espaciosList.value
  return espaciosList.value.filter(e => e.sede_id === sedeSeleccionadaId.value)
})

const totalGanancias = computed(() => {
  return pagosPropietario.value.reduce((acc, p) => acc + (p.monto || 0), 0)
})

onMounted(async () => {
  themeStore.initTheme(true)
  await cargarDatos()
})

const cargarDatos = async () => {
  try {
    const propId = authStore.user?.id
    if (!propId) return

    const [sRes, eRes, pRes, rRes, susRes] = await Promise.allSettled([
      estacionamientosService.getSedesPorPropietario(propId),
      estacionamientosService.getEspacios(0, 100),
      pagosService.getPagosPorPropietario(propId),
      reservasService.getReservas(0, 50),
      usuariosService.getMiSuscripcion()
    ])

    if (sRes.status === 'fulfilled') {
      const d = sRes.value.data
      misSedes.value = Array.isArray(d) ? d : (d?.data || [])
      if (misSedes.value.length > 0 && !sedeSeleccionadaId.value) {
        sedeSeleccionadaId.value = misSedes.value[0].id
      }
    }
    if (eRes.status === 'fulfilled') {
      const d = eRes.value.data
      espaciosList.value = Array.isArray(d) ? d : (d?.data || [])
    }
    if (pRes.status === 'fulfilled') {
      const d = pRes.value.data
      pagosPropietario.value = Array.isArray(d) ? d : (d?.data || [])
    }
    if (rRes.status === 'fulfilled') {
      const d = rRes.value.data
      reservasPropietario.value = Array.isArray(d) ? d : (d?.data || [])
    }
    if (susRes.status === 'fulfilled') {
      suscripcionActual.value = susRes.value.data
    }
  } catch (err) {
    console.warn('Error cargando propietario:', err)
  }
}

const abrirModalCrearSede = () => {
  modalSede.value = {
    open: true,
    isEdit: false,
    id: null,
    form: { nombre: '', direccion: '', latitud: -12.0463, longitud: -77.0427, tarifa_hora: 5 }
  }
}

const abrirModalEditarSede = (s) => {
  modalSede.value = {
    open: true,
    isEdit: true,
    id: s.id,
    form: { nombre: s.nombre, direccion: s.direccion, latitud: s.latitud, longitud: s.longitud, tarifa_hora: s.tarifa_hora }
  }
}

const guardarSede = async () => {
  try {
    if (modalSede.value.isEdit) {
      await estacionamientosService.actualizarSede(modalSede.value.id, modalSede.value.form)
      showToast('Sede actualizada', 'success')
    } else {
      await estacionamientosService.crearSede(modalSede.value.form)
      showToast('Sede creada exitosamente', 'success')
    }
    modalSede.value.open = false
    await cargarDatos()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar sede', 'error')
  }
}

const toggleEstadoSede = async (s) => {
  try {
    await estacionamientosService.toggleEstadoSede(s.id, !s.activa)
    showToast(`Sede ${s.activa ? 'desactivada' : 'activada'}`, 'success')
    await cargarDatos()
  } catch (err) {
    showToast('Error al cambiar estado de sede', 'error')
  }
}

const abrirModalCrearEspacio = async () => {
  const numero = prompt('Ingresa el número de cajón (ej: A-05):')
  if (!numero) return
  try {
    await estacionamientosService.crearEspacio({
      sede_id: sedeSeleccionadaId.value,
      numero: numero,
      tipo_vehiculo: 'auto',
      estado: 'libre'
    })
    showToast(`Espacio ${numero} registrado`, 'success')
    await cargarDatos()
  } catch (err) {
    showToast('Error creando espacio', 'error')
  }
}

const abrirCulqiSuscripcion = (monto) => {
  if (typeof window.Culqi === 'undefined') {
    showToast('Culqi Checkout no disponible en este momento', 'error')
    return
  }
  window.Culqi.publicKey = 'pk_test_e371ad52382b6b06'
  window.Culqi.settings({
    title: 'SmartPark Suscripción Pro',
    currency: 'PEN',
    amount: Math.round(monto * 100)
  })
  window.Culqi.open()
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
