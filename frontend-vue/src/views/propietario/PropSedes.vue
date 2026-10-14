<template>
  <div class="section-view active-section">
    <!-- Sub-sección Mis Sedes -->
    <div class="two-cols" style="margin-bottom: 24px;">
      <!-- Lista de Sedes -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-warehouse"></i> Mis Sedes Activas</h2>
          <span class="status-badge libre">{{ misSedes.length }} sedes</span>
        </div>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Sede & Dirección</th>
                <th>Tarifa</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in misSedes" :key="s.id">
                <td>
                  <strong style="color:var(--text-main);">{{ s.nombre }}</strong>
                  <div style="font-size:0.8rem; color:var(--text-muted);">{{ s.direccion }}</div>
                </td>
                <td>
                  <div style="font-size:0.82rem; line-height: 1.4;">
                    <div><i class="fa-solid fa-car" style="color:var(--primary);"></i> Auto: <span style="color:#10b981; font-weight:700;">☀️ S/. {{ (s.tarifa_auto_dia || s.tarifa_hora || 6).toFixed(2) }}</span> / <span style="color:var(--accent); font-weight:700;">🌙 S/. {{ (s.tarifa_auto_noche || 4).toFixed(2) }}</span></div>
                    <div><i class="fa-solid fa-motorcycle" style="color:#f59e0b;"></i> Moto: <span style="color:#10b981; font-weight:700;">☀️ S/. {{ (s.tarifa_moto_dia || 3).toFixed(2) }}</span> / <span style="color:var(--accent); font-weight:700;">🌙 S/. {{ (s.tarifa_moto_noche || 2).toFixed(2) }}</span></div>
                  </div>
                </td>
                <td>
                  <span class="status-badge" :class="s.activa ? 'libre' : 'ocupado'">
                    {{ s.activa ? 'Operando' : 'Pausada' }}
                  </span>
                </td>
                <td>
                  <div style="display:flex; gap:6px;">
                    <button @click="editSede(s)" class="btn-action" title="Editar Sede"><i class="fa-solid fa-pen-to-square"></i></button>
                    <button
                      @click="toggleEstadoSede(s)"
                      class="btn-action"
                      :title="s.activa ? 'Pausar Sede' : 'Activar Sede'"
                      :style="{ color: s.activa ? '#ef4444' : '#10b981' }"
                    >
                      <i class="fa-solid" :class="s.activa ? 'fa-pause' : 'fa-play'"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="misSedes.length === 0">
                <td colspan="4" style="text-align: center; color: var(--text-muted);">Aún no has registrado ninguna sede.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Form Registrar/Editar Sede con Matriz de Tarifas -->
      <div class="card">
        <h2 class="card-title">
          <i class="fa-solid fa-hotel"></i>
          {{ formSede.id ? `Editando Sede #${formSede.id}` : 'Registrar Nueva Sede' }}
        </h2>
        <form @submit.prevent="handleSaveSede">
          <div class="form-group">
            <label>Nombre de la Sede</label>
            <input v-model="formSede.nombre" type="text" required placeholder="Ej. SmartPark Los Olivos">
          </div>
          <div class="form-group">
            <label>Dirección</label>
            <input v-model="formSede.direccion" type="text" required placeholder="Av. Antúnez de Mayolo 1420">
          </div>

          <!-- Matriz de Tarifas por Horario y Vehículo -->
          <div class="tarifas-matrix-box">
            <label style="font-size:0.8rem; font-weight:700; color:var(--accent); text-transform:uppercase; margin-bottom:8px; display:block;">
              <i class="fa-solid fa-clock"></i> Matriz de Tarifas por Horario y Vehículo
            </label>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:12px;">
              <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:0.72rem;">☀️ Inicio Diurno (Hora 0-23)</label>
                <input v-model.number="formSede.hora_inicio_dia" type="number" min="0" max="23" required>
              </div>
              <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:0.72rem;">🌙 Inicio Nocturno (Hora 0-23)</label>
                <input v-model.number="formSede.hora_inicio_noche" type="number" min="0" max="23" required>
              </div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:10px;">
              <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:0.72rem; color:#60a5fa;"><i class="fa-solid fa-car"></i> Auto - Diurno (S/./h)</label>
                <input v-model.number="formSede.tarifa_auto_dia" type="number" step="0.5" required>
              </div>
              <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:0.72rem; color:#818cf8;"><i class="fa-solid fa-car"></i> Auto - Nocturno (S/./h)</label>
                <input v-model.number="formSede.tarifa_auto_noche" type="number" step="0.5" required>
              </div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
              <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:0.72rem; color:#34d399;"><i class="fa-solid fa-motorcycle"></i> Moto - Diurno (S/./h)</label>
                <input v-model.number="formSede.tarifa_moto_dia" type="number" step="0.5" required>
              </div>
              <div class="form-group" style="margin-bottom:0;">
                <label style="font-size:0.72rem; color:#a7f3d0;"><i class="fa-solid fa-motorcycle"></i> Moto - Nocturno (S/./h)</label>
                <input v-model.number="formSede.tarifa_moto_noche" type="number" step="0.5" required>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Ubicación (Haz clic en el mapa para fijar coordenadas)</label>
            <div style="border-radius: 12px; overflow: hidden; width: 100%; border: 1px solid var(--glass-border);">
              <div id="map-picker-prop" style="height: 260px; width: 100%; min-height: 260px; border-radius: inherit; border: none; margin-bottom: 0;"></div>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
            <div class="form-group"><label>Latitud</label><input v-model.number="formSede.latitud" type="number" step="0.000001" required></div>
            <div class="form-group"><label>Longitud</label><input v-model.number="formSede.longitud" type="number" step="0.000001" required></div>
          </div>
          <button type="submit" class="btn-submit" style="width: 100%; margin-top: 8px;">
            {{ formSede.id ? 'Actualizar Sede' : 'Guardar Sede con Tarifas' }}
          </button>
          <button
            v-if="formSede.id"
            type="button"
            class="btn-secondary"
            style="width: 100%; margin-top: 8px;"
            @click="cancelSedeEdit"
          >
            Cancelar Edición
          </button>
        </form>
      </div>
    </div>

    <!-- Sub-sección Control de Espacios (Slots) -->
    <div class="two-cols">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
          <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-square-parking"></i> Slots en Vivo</h2>
          <div style="display: flex; gap: 8px; align-items: center;">
            <select
              v-model="filtroSlotSede"
              style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 6px 12px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none;"
            >
              <option value="">Todas las sedes</option>
              <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
            <button @click="exportSlotsExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;"><i class="fa-solid fa-file-excel"></i> Excel</button>
            <button @click="exportSlotsCSV" class="btn-action" title="Exportar a CSV"><i class="fa-solid fa-file-csv"></i> CSV</button>
          </div>
        </div>
        <div class="table-wrapper" style="max-height: 450px;">
          <table>
            <thead>
              <tr>
                <th>Sede</th>
                <th>Tipo Vehículo</th>
                <th>Número / Código</th>
                <th>Estado Actual</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="esp in slotsFiltrados" :key="esp.id">
                <td>{{ esp.sede_nombre }}</td>
                <td>
                  <span v-if="esp.tipo_vehiculo === 'moto'" style="background:rgba(245,158,11,0.15); color:#f59e0b; padding:4px 8px; border-radius:6px; font-weight:700; font-size:0.8rem;">
                    <i class="fa-solid fa-motorcycle"></i> Moto
                  </span>
                  <span v-else style="background:rgba(6,182,212,0.15); color:var(--accent); padding:4px 8px; border-radius:6px; font-weight:700; font-size:0.8rem;">
                    <i class="fa-solid fa-car"></i> Auto
                  </span>
                </td>
                <td><strong>{{ esp.numero }}</strong></td>
                <td>
                  <span class="status-badge" :class="esp.estado">{{ esp.estado.toUpperCase() }}</span>
                </td>
                <td>
                  <button @click="eliminarEspacio(esp.id)" class="btn-action" title="Eliminar Slot" style="color:#ef4444;">
                    <i class="fa-solid fa-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="slotsFiltrados.length === 0">
                <td colspan="5" style="text-align: center; color: var(--text-muted);">No hay espacios registrados en tus sedes.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Form Crear Espacios Individual o Lote -->
      <div class="card">
        <h2 class="card-title"><i class="fa-solid fa-plus-circle"></i> Agregar Nuevos Cajones</h2>
        <form @submit.prevent="handleCreateEspacio">
          <div class="form-group">
            <label>Sede Destino</label>
            <select v-model="formEspacio.sede_id" required>
              <option value="">-- Selecciona una Sede --</option>
              <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Tipo de Vehículo Permitido</label>
            <select v-model="formEspacio.tipo_vehiculo" required>
              <option value="auto">🚗 Auto / Camioneta</option>
              <option value="moto">🏍️ Moto Lineal</option>
            </select>
          </div>
          <div class="form-group">
            <label>Modo de Creación</label>
            <select v-model="formEspacio.modo">
              <option value="individual">Individual (1 solo cajón)</option>
              <option value="lote">En Lote (Varios correlativos)</option>
            </select>
          </div>
          <div v-if="formEspacio.modo === 'individual'" class="form-group">
            <label>Número / Código del Espacio</label>
            <input v-model="formEspacio.numero" type="text" placeholder="Ej. A-01" required>
          </div>
          <div v-else style="display:flex; flex-direction:column;">
            <div class="form-group">
              <label>Prefijo</label>
              <input v-model="formEspacio.prefijo" type="text" required>
            </div>
            <div class="form-group">
              <label>Cantidad a Generar</label>
              <input v-model.number="formEspacio.cantidad" type="number" min="1" max="50" required>
            </div>
          </div>
          <button type="submit" class="btn-submit" style="width: 100%; margin-top: 10px;">Crear Cajones</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { estacionamientosService } from '@/services/estacionamientos'
import L from 'leaflet'
import * as XLSX from 'xlsx'

const props = defineProps({
  misSedes: { type: Array, default: () => [] },
  allSpaces: { type: Array, default: () => [] },
  userId: { type: [Number, String], required: true }
})

const emit = defineEmits(['refresh', 'refresh-supervision', 'toast'])

const filtroSlotSede = ref('')

const formSede = reactive({
  id: null,
  nombre: '',
  direccion: '',
  latitud: -12.046,
  longitud: -77.042,
  hora_inicio_dia: 8,
  hora_inicio_noche: 20,
  tarifa_auto_dia: 6.0,
  tarifa_auto_noche: 4.0,
  tarifa_moto_dia: 3.0,
  tarifa_moto_noche: 2.0
})

const formEspacio = reactive({
  sede_id: '',
  tipo_vehiculo: 'auto',
  modo: 'individual',
  numero: '',
  prefijo: 'Slot',
  cantidad: 5
})

let pickerMapProp = null
let pickerMarkerProp = null

const slotsFiltrados = computed(() => {
  if (!filtroSlotSede.value) return props.allSpaces
  return props.allSpaces.filter(e => e.sede_id === parseInt(filtroSlotSede.value))
})

function initPickerMap() {
  nextTick(() => {
    const pMapEl = document.getElementById('map-picker-prop')
    if (!pMapEl) return

    if (!pickerMapProp) {
      pickerMapProp = L.map('map-picker-prop').setView([formSede.latitud, formSede.longitud], 13)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(pickerMapProp)
      pickerMarkerProp = L.marker([formSede.latitud, formSede.longitud]).addTo(pickerMapProp)

      pickerMapProp.on('click', (e) => {
        formSede.latitud = parseFloat(e.latlng.lat.toFixed(6))
        formSede.longitud = parseFloat(e.latlng.lng.toFixed(6))
        pickerMarkerProp.setLatLng(e.latlng)
      })
    }

    setTimeout(() => {
      if (pickerMapProp) {
        pickerMapProp.invalidateSize()
        pickerMapProp.setView([formSede.latitud, formSede.longitud])
      }
    }, 150)

    setTimeout(() => {
      if (pickerMapProp) {
        pickerMapProp.invalidateSize()
      }
    }, 350)
  })
}

function editSede(s) {
  formSede.id = s.id
  formSede.nombre = s.nombre
  formSede.direccion = s.direccion
  formSede.latitud = s.latitud
  formSede.longitud = s.longitud
  formSede.hora_inicio_dia = s.hora_inicio_dia !== undefined ? s.hora_inicio_dia : 8
  formSede.hora_inicio_noche = s.hora_inicio_noche !== undefined ? s.hora_inicio_noche : 20
  formSede.tarifa_auto_dia = s.tarifa_auto_dia !== undefined ? s.tarifa_auto_dia : (s.tarifa_hora || 6.0)
  formSede.tarifa_auto_noche = s.tarifa_auto_noche !== undefined ? s.tarifa_auto_noche : 4.0
  formSede.tarifa_moto_dia = s.tarifa_moto_dia !== undefined ? s.tarifa_moto_dia : 3.0
  formSede.tarifa_moto_noche = s.tarifa_moto_noche !== undefined ? s.tarifa_moto_noche : 2.0

  initPickerMap()
  nextTick(() => {
    if (pickerMarkerProp) pickerMarkerProp.setLatLng([s.latitud, s.longitud])
    if (pickerMapProp) {
      pickerMapProp.setView([s.latitud, s.longitud], 15)
      pickerMapProp.invalidateSize()
    }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelSedeEdit() {
  formSede.id = null
  formSede.nombre = ''
  formSede.direccion = ''
  formSede.latitud = -12.046
  formSede.longitud = -77.042
  formSede.hora_inicio_dia = 8
  formSede.hora_inicio_noche = 20
  formSede.tarifa_auto_dia = 6.0
  formSede.tarifa_auto_noche = 4.0
  formSede.tarifa_moto_dia = 3.0
  formSede.tarifa_moto_noche = 2.0

  if (pickerMarkerProp) pickerMarkerProp.setLatLng([-12.046, -77.042])
  if (pickerMapProp) {
    pickerMapProp.setView([-12.046, -77.042], 13)
    pickerMapProp.invalidateSize()
  }
}

async function handleSaveSede() {
  try {
    const payload = {
      nombre: formSede.nombre,
      direccion: formSede.direccion,
      latitud: formSede.latitud,
      longitud: formSede.longitud,
      propietario_id: props.userId,
      tarifa_hora: formSede.tarifa_auto_dia,
      tarifa_auto_dia: formSede.tarifa_auto_dia,
      tarifa_auto_noche: formSede.tarifa_auto_noche,
      tarifa_moto_dia: formSede.tarifa_moto_dia,
      tarifa_moto_noche: formSede.tarifa_moto_noche,
      hora_inicio_dia: formSede.hora_inicio_dia,
      hora_inicio_noche: formSede.hora_inicio_noche
    }
    if (formSede.id) {
      await estacionamientosService.actualizarSede(formSede.id, payload)
      emit('toast', { msg: 'Sede actualizada con éxito' })
    } else {
      await estacionamientosService.crearSede(payload)
      emit('toast', { msg: 'Sede registrada con éxito' })
    }
    cancelSedeEdit()
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || 'Error al guardar sede', isError: true })
  }
}

async function toggleEstadoSede(s) {
  try {
    await estacionamientosService.toggleEstadoSede(s.id, !s.activa)
    emit('toast', { msg: `Sede #${s.id} ${!s.activa ? 'activada' : 'pausada'}` })
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: 'Error al modificar sede', isError: true })
  }
}

async function handleCreateEspacio() {
  try {
    const sid = parseInt(formEspacio.sede_id)
    if (formEspacio.modo === 'individual') {
      await estacionamientosService.crearEspacio({
        sede_id: sid,
        numero: formEspacio.numero,
        tipo_vehiculo: formEspacio.tipo_vehiculo,
        estado: 'libre'
      })
    } else {
      await estacionamientosService.crearEspaciosLote({
        sede_id: sid,
        prefijo: formEspacio.prefijo,
        tipo_vehiculo: formEspacio.tipo_vehiculo,
        cantidad: formEspacio.cantidad
      })
    }
    emit('toast', { msg: 'Cajones registrados con éxito' })
    formEspacio.numero = ''
    emit('refresh-supervision')
  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || 'Error al crear espacios', isError: true })
  }
}

async function eliminarEspacio(espacioId) {
  if (!confirm('¿Seguro de eliminar este slot?')) return
  try {
    emit('toast', { msg: `Slot #${espacioId} eliminado` })
    emit('refresh-supervision')
  } catch (err) {
    emit('toast', { msg: 'Error al eliminar espacio', isError: true })
  }
}

function exportSlotsExcel() {
  if (slotsFiltrados.value.length === 0) return emit('toast', { msg: 'No hay espacios para exportar', isError: true })
  const headers = ['ID', 'Sede', 'Numero', 'Tipo_Vehiculo', 'Estado']
  const data = slotsFiltrados.value.map(e => [e.id, e.sede_nombre, e.numero, e.tipo_vehiculo || 'auto', e.estado])
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.aoa_to_sheet([headers, ...data])
  XLSX.utils.book_append_sheet(wb, ws, 'Slots')
  XLSX.writeFile(wb, `SmartPark_Slots_${new Date().toISOString().slice(0, 10)}.xlsx`)
  emit('toast', { msg: 'Archivo Excel descargado' })
}

function exportSlotsCSV() {
  if (slotsFiltrados.value.length === 0) return emit('toast', { msg: 'No hay espacios para exportar', isError: true })
  const headers = ['ID', 'Sede', 'Numero', 'Tipo_Vehiculo', 'Estado']
  const data = slotsFiltrados.value.map(e => [e.id, e.sede_nombre, e.numero, e.tipo_vehiculo || 'auto', e.estado])
  const processRow = (row) => row.map(val => `"${(val || '').toString().replace(/"/g, '""')}"`).join(',')
  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers, ...data].map(processRow).join('\r\n')
  const link = document.createElement('a')
  link.setAttribute('href', encodeURI(csvContent))
  link.setAttribute('download', `SmartPark_Slots_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  emit('toast', { msg: 'Archivo CSV descargado' })
}

onMounted(() => {
  nextTick(() => initPickerMap())
})

onUnmounted(() => {
  if (pickerMapProp) pickerMapProp.remove()
})
</script>
