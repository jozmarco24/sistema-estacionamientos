<template>
  <div class="section-view active-section">
    <div class="two-cols">
      <!-- Mapa Global de Sedes -->
      <div class="card" style="display: flex; flex-direction: column;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-earth-americas"></i> Sedes Activas en Mapa</h2>
          <button @click="recenterGlobalMap" class="btn-action" title="Centrar en todas las sedes">
            <i class="fa-solid fa-crosshairs"></i> Centrar Mapa
          </button>
        </div>
        <div id="global-map"></div>
      </div>

      <!-- Form Registrar/Editar Sede -->
      <div class="card">
        <h2 class="card-title">
          <i class="fa-solid fa-hotel"></i>
          {{ formSede.id ? `Editar Sede #${formSede.id}` : 'Registrar Nueva Sede' }}
        </h2>
        <form @submit.prevent="handleSaveSede">
          <div class="form-group">
            <label>Propietario Dueño</label>
            <select v-model="formSede.propietario_id" required>
              <option value="">-- Selecciona el Propietario --</option>
              <option v-for="p in propietariosList.filter(x => x.activo)" :key="p.id" :value="p.id">
                {{ p.nombre }} ({{ p.email }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Nombre de la Sede</label>
            <input v-model="formSede.nombre" type="text" required placeholder="Ej. SmartPark Central">
          </div>
          <div class="form-group">
            <label>Dirección</label>
            <input v-model="formSede.direccion" type="text" required placeholder="Jr. Asamblea 120">
          </div>
          <div class="form-group">
            <label>Tarifa por Hora (S/.)</label>
            <input v-model.number="formSede.tarifa_hora" type="number" step="0.5" required>
          </div>
          <div class="form-group">
            <label>Ubicación (Haz clic en el mapa para fijar coordenadas)</label>
            <div id="map-picker"></div>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div class="form-group">
              <label>Latitud</label>
              <input v-model.number="formSede.latitud" type="number" step="0.000001" required>
            </div>
            <div class="form-group">
              <label>Longitud</label>
              <input v-model.number="formSede.longitud" type="number" step="0.000001" required>
            </div>
          </div>
          <button type="submit" class="btn-submit" style="margin-top: 10px;">
            {{ formSede.id ? 'Guardar Cambios' : 'Crear Sede' }}
          </button>
          <button
            v-if="formSede.id"
            type="button"
            class="btn-secondary"
            style="margin-top:8px;"
            @click="cancelSedeEdit"
          >
            Cancelar Edición
          </button>
        </form>
      </div>
    </div>

    <!-- Tabla de Sedes Registradas con Buscador y Exportador -->
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-warehouse"></i> Listado General de Sedes</h2>
          <span class="status-badge libre">{{ sedesFiltradas.length }} sedes</span>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <input
            v-model="searchSedes"
            type="text"
            placeholder="Buscar por nombre o dirección..."
            style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 220px;"
          >
          <button @click="exportSedesExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
            <i class="fa-solid fa-file-excel"></i> Exportar Excel
          </button>
          <button @click="exportSedesCSV" class="btn-action" title="Exportar a CSV">
            <i class="fa-solid fa-file-csv"></i> Exportar CSV
          </button>
        </div>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre & Dirección</th>
              <th>Propietario</th>
              <th>Tarifa</th>
              <th>Estado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in sedesFiltradas" :key="s.id">
              <td>#{{ s.id }}</td>
              <td>
                <strong>{{ s.nombre }}</strong><br>
                <span style="font-size:0.75rem; color:#94a3b8;"><i class="fa-solid fa-location-dot"></i> {{ s.direccion }}</span>
              </td>
              <td>{{ getOwnerName(s.propietario_id) }}</td>
              <td>S/. {{ (s.tarifa_hora || 5.0).toFixed(2) }}</td>
              <td>
                <span class="status-badge" :class="s.activa ? 'libre' : 'ocupado'">
                  {{ s.activa ? 'Operando' : 'Cerrada' }}
                </span>
              </td>
              <td>
                <button @click="zoomToSede(s)" class="btn-action" title="Ver en mapa"><i class="fa-solid fa-map-pin"></i></button>
                <button @click="editSede(s)" class="btn-action" title="Editar"><i class="fa-solid fa-pen"></i></button>
                <button
                  @click="toggleSedeEstado(s)"
                  class="btn-action"
                  :title="s.activa ? 'Desactivar' : 'Activar'"
                >
                  <i class="fa-solid" :class="s.activa ? 'fa-pause' : 'fa-play'"></i>
                </button>
              </td>
            </tr>
            <tr v-if="sedesFiltradas.length === 0">
              <td colspan="6" style="text-align: center; color: var(--text-muted);">No se encontraron sedes.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { estacionamientosService } from '@/services/estacionamientos'
import L from 'leaflet'
import * as XLSX from 'xlsx'

const props = defineProps({
  sedesList: { type: Array, default: () => [] },
  propietariosList: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh', 'toast'])

const searchSedes = ref('')

const formSede = reactive({
  id: null,
  propietario_id: '',
  nombre: '',
  direccion: '',
  tarifa_hora: 5.0,
  latitud: -13.157661,
  longitud: -74.227060
})

let globalMap = null
let globalMapMarkers = null
let pickerMap = null
let pickerMarker = null

const sedesFiltradas = computed(() => {
  if (!searchSedes.value.trim()) return props.sedesList
  const q = searchSedes.value.toLowerCase()
  return props.sedesList.filter(s =>
    (s.nombre && s.nombre.toLowerCase().includes(q)) ||
    (s.direccion && s.direccion.toLowerCase().includes(q))
  )
})

function getOwnerName(propId) {
  const p = props.propietariosList.find(x => x.id === propId)
  return p ? p.nombre : `Prop #${propId}`
}

function initMaps() {
  const pickerEl = document.getElementById('map-picker')
  if (pickerEl && !pickerMap) {
    pickerMap = L.map('map-picker').setView([formSede.latitud, formSede.longitud], 14)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(pickerMap)
    pickerMarker = L.marker([formSede.latitud, formSede.longitud]).addTo(pickerMap)

    pickerMap.on('click', (e) => {
      formSede.latitud = parseFloat(e.latlng.lat.toFixed(6))
      formSede.longitud = parseFloat(e.latlng.lng.toFixed(6))
      pickerMarker.setLatLng(e.latlng)
    })
  }

  const globalEl = document.getElementById('global-map')
  if (globalEl && !globalMap) {
    globalMap = L.map('global-map').setView([-13.157661, -74.227060], 14)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(globalMap)
    globalMapMarkers = L.layerGroup().addTo(globalMap)
    updateGlobalMapMarkers()
  }

  setTimeout(() => {
    if (globalMap) globalMap.invalidateSize()
    if (pickerMap) pickerMap.invalidateSize()
  }, 100)
}

function updateGlobalMapMarkers() {
  if (!globalMapMarkers) return
  globalMapMarkers.clearLayers()

  props.sedesList.forEach(s => {
    if (s.latitud && s.longitud) {
      const markerColor = s.activa ? '#10b981' : '#ef4444'
      const icon = L.divIcon({
        className: 'custom-map-pin',
        html: `<div style="background:${markerColor}; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:13px; box-shadow:0 0 12px ${markerColor}; border:2px solid #fff;"><i class="fa-solid fa-parking"></i></div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      })

      const marker = L.marker([s.latitud, s.longitud], { icon })
      marker.bindPopup(`
        <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:180px;">
          <h3 style="margin:0 0 4px 0; color:#0f172a; font-size:1rem;">${s.nombre}</h3>
          <p style="margin:0 0 6px 0; color:#64748b; font-size:0.8rem;"><i class="fa-solid fa-location-dot"></i> ${s.direccion}</p>
          <div style="font-size:0.82rem; font-weight:600; color:#0f172a; margin-bottom:8px;">
            Tarifa: S/. ${(s.tarifa_hora || 5.0).toFixed(2)}/hr
          </div>
          <div style="font-size:0.75rem; color:#475569; margin-bottom:8px;">Dueño: <strong>${getOwnerName(s.propietario_id)}</strong></div>
        </div>
      `)
      globalMapMarkers.addLayer(marker)
    }
  })
}

function recenterGlobalMap() {
  if (!globalMap || props.sedesList.length === 0) return
  const valid = props.sedesList.filter(s => s.latitud && s.longitud)
  if (valid.length === 0) return
  const bounds = L.latLngBounds(valid.map(s => [s.latitud, s.longitud]))
  globalMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 })
}

function zoomToSede(s) {
  if (globalMap && s.latitud && s.longitud) {
    globalMap.setView([s.latitud, s.longitud], 17)
  }
}

function editSede(s) {
  formSede.id = s.id
  formSede.nombre = s.nombre
  formSede.direccion = s.direccion
  formSede.tarifa_hora = s.tarifa_hora || 5.0
  formSede.propietario_id = s.propietario_id
  formSede.latitud = s.latitud
  formSede.longitud = s.longitud

  if (pickerMarker) {
    pickerMarker.setLatLng([s.latitud, s.longitud])
    pickerMap.setView([s.latitud, s.longitud], 15)
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelSedeEdit() {
  formSede.id = null
  formSede.nombre = ''
  formSede.direccion = ''
  formSede.tarifa_hora = 5.0
  formSede.propietario_id = ''
  formSede.latitud = -13.157661
  formSede.longitud = -74.227060
  if (pickerMarker) pickerMarker.setLatLng([-13.157661, -74.227060])
}

async function handleSaveSede() {
  try {
    const payload = {
      nombre: formSede.nombre,
      direccion: formSede.direccion,
      tarifa_hora: formSede.tarifa_hora,
      propietario_id: formSede.propietario_id,
      latitud: formSede.latitud,
      longitud: formSede.longitud
    }
    if (formSede.id) {
      await estacionamientosService.actualizarSede(formSede.id, payload)
      emit('toast', { msg: 'Sede actualizada correctamente' })
    } else {
      await estacionamientosService.crearSede(payload)
      emit('toast', { msg: 'Sede registrada exitosamente' })
    }
    cancelSedeEdit()
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || 'Error al guardar la sede', isError: true })
  }
}

async function toggleSedeEstado(s) {
  try {
    await estacionamientosService.toggleEstadoSede(s.id, !s.activa)
    emit('toast', { msg: `Sede #${s.id} ${!s.activa ? 'activada' : 'desactivada'}` })
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: 'Error al cambiar estado de la sede', isError: true })
  }
}

function downloadExcel(filename, sheetName, headers, rows) {
  try {
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows])
    XLSX.utils.book_append_sheet(wb, ws, sheetName || 'Datos')
    XLSX.writeFile(wb, filename)
    emit('toast', { msg: 'Archivo Excel (.xlsx) generado exitosamente' })
  } catch (err) {
    downloadCSV(filename.replace(/\.xlsx$/i, '.csv'), [headers, ...rows])
  }
}

function downloadCSV(filename, rows) {
  const processRow = (row) => row.map(val => `"${(val || '').toString().replace(/"/g, '""')}"`).join(',')
  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + rows.map(processRow).join('\r\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  emit('toast', { msg: 'Archivo CSV exportado exitosamente' })
}

function exportSedesExcel() {
  if (props.sedesList.length === 0) return emit('toast', { msg: 'No hay sedes para exportar', isError: true })
  const headers = ['ID', 'Nombre', 'Dirección', 'Tarifa_Hora', 'Latitud', 'Longitud', 'Propietario_ID', 'Estado']
  const data = props.sedesList.map(s => [
    s.id, s.nombre, s.direccion, s.tarifa_hora || 5.0, s.latitud, s.longitud, s.propietario_id, s.activa ? 'Activa' : 'Inactiva'
  ])
  downloadExcel(`SmartPark_Sedes_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Sedes', headers, data)
}

function exportSedesCSV() {
  if (props.sedesList.length === 0) return emit('toast', { msg: 'No hay sedes para exportar', isError: true })
  const headers = ['ID', 'Nombre', 'Dirección', 'Tarifa_Hora', 'Latitud', 'Longitud', 'Propietario_ID', 'Estado']
  const data = props.sedesList.map(s => [
    s.id, s.nombre, s.direccion, s.tarifa_hora || 5.0, s.latitud, s.longitud, s.propietario_id, s.activa ? 'Activa' : 'Inactiva'
  ])
  downloadCSV(`SmartPark_Sedes_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}

onMounted(() => {
  nextTick(() => initMaps())
})

watch(() => props.sedesList, () => {
  updateGlobalMapMarkers()
}, { deep: true })

onUnmounted(() => {
  if (globalMap) globalMap.remove()
  if (pickerMap) pickerMap.remove()
})
</script>
