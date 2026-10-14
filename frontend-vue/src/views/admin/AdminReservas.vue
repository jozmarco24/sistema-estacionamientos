<template>
  <div class="section-view active-section">
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-clock-rotate-left"></i> Historial y Reservas Globales en Vivo</h2>
          <span class="status-badge libre">{{ reservasFiltradas.length }} reservas</span>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
          <select
            v-model="filtroReservaSede"
            style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 12px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; min-width: 170px;"
          >
            <option value="">🏢 Todos los Estacionamientos</option>
            <option v-for="s in sedesList" :key="s.id" :value="s.id">🏢 {{ s.nombre }}</option>
          </select>
          <select
            v-model="filtroReservaEstado"
            style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 12px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none;"
          >
            <option value="">Todos los Estados</option>
            <option value="confirmada">Confirmada</option>
            <option value="pendiente">Pendiente</option>
            <option value="cancelada">Cancelada</option>
            <option value="finalizada">Finalizada</option>
          </select>
          <input
            v-model="searchReservas"
            type="text"
            placeholder="Buscar por placa o ID..."
            style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 180px;"
          >
          <button @click="exportReservasExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
            <i class="fa-solid fa-file-excel"></i> Exportar Excel
          </button>
          <button @click="exportReservasCSV" class="btn-action" title="Exportar a CSV">
            <i class="fa-solid fa-file-csv"></i> Exportar CSV
          </button>
          <button @click="$emit('refresh-reservas')" class="btn-action"><i class="fa-solid fa-rotate"></i> Actualizar</button>
        </div>
      </div>
      <div class="table-wrapper" style="max-height: 500px;">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Estacionamiento / Sede</th>
              <th>Espacio</th>
              <th>Placa Vehículo</th>
              <th>Fecha Inicio</th>
              <th>Fecha Fin</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in reservasFiltradas" :key="r.id">
              <td><strong>#{{ r.id }}</strong></td>
              <td>
                <strong style="color:var(--primary);"><i class="fa-solid fa-square-parking"></i> {{ r.sede_nombre }}</strong>
              </td>
              <td>
                <span style="background:rgba(2,132,199,0.1); color:var(--accent); padding:2px 8px; border-radius:6px; font-weight:700;">
                  {{ r.espacio_numero }}
                </span>
              </td>
              <td><strong style="letter-spacing:0.5px;">{{ r.placa_vehiculo || 'N/A' }}</strong></td>
              <td><span style="font-size:0.82rem; color:var(--text-muted);">{{ formatearFecha(r.fecha_inicio) }}</span></td>
              <td><span style="font-size:0.82rem; color:var(--text-muted);">{{ formatearFecha(r.fecha_fin) }}</span></td>
              <td>
                <span
                  class="status-badge"
                  :class="r.estado === 'confirmada' ? 'activa' : (r.estado === 'cancelada' ? 'cancelada' : 'reservado')"
                >
                  {{ r.estado ? r.estado.toUpperCase() : 'CONFIRMADA' }}
                </span>
              </td>
            </tr>
            <tr v-if="reservasFiltradas.length === 0">
              <td colspan="7" style="text-align: center; color: var(--text-muted);">No se encontraron reservas con los filtros aplicados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'

const props = defineProps({
  reservasList: { type: Array, default: () => [] },
  sedesList: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh-reservas', 'toast'])

const filtroReservaSede = ref('')
const filtroReservaEstado = ref('')
const searchReservas = ref('')

const reservasFiltradas = computed(() => {
  return props.reservasList.filter(r => {
    if (filtroReservaSede.value && r.sede_id !== parseInt(filtroReservaSede.value)) return false
    if (filtroReservaEstado.value && (r.estado || '').toLowerCase() !== filtroReservaEstado.value.toLowerCase()) return false
    if (searchReservas.value.trim()) {
      const q = searchReservas.value.toLowerCase().trim()
      const matchId = `${r.id}`.includes(q)
      const matchPlaca = (r.placa_vehiculo || '').toLowerCase().includes(q)
      const matchSede = (r.sede_nombre || '').toLowerCase().includes(q)
      const matchEspacio = (r.espacio_numero || '').toLowerCase().includes(q)
      if (!matchId && !matchPlaca && !matchSede && !matchEspacio) return false
    }
    return true
  })
})

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

function exportReservasExcel() {
  if (reservasFiltradas.value.length === 0) return emit('toast', { msg: 'Sin reservas para exportar', isError: true })
  const headers = ['ID_Reserva', 'Estacionamiento', 'Espacio', 'Placa_Vehiculo', 'Fecha_Inicio', 'Fecha_Fin', 'Estado']
  const data = reservasFiltradas.value.map(r => [
    r.id, r.sede_nombre || 'Sede General', r.espacio_numero || `#${r.espacio_id}`, r.placa_vehiculo || 'N/A',
    r.fecha_inicio ? r.fecha_inicio.replace('T', ' ').slice(0, 19) : '',
    r.fecha_fin ? r.fecha_fin.replace('T', ' ').slice(0, 19) : '',
    (r.estado || '').toUpperCase()
  ])
  downloadExcel(`SmartPark_Reservas_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Reservas', headers, data)
}

function exportReservasCSV() {
  if (reservasFiltradas.value.length === 0) return emit('toast', { msg: 'Sin reservas para exportar', isError: true })
  const headers = ['ID_Reserva', 'Estacionamiento', 'Espacio', 'Placa_Vehiculo', 'Fecha_Inicio', 'Fecha_Fin', 'Estado']
  const data = reservasFiltradas.value.map(r => [
    r.id, r.sede_nombre || 'Sede General', r.espacio_numero || `#${r.espacio_id}`, r.placa_vehiculo || 'N/A',
    r.fecha_inicio ? r.fecha_inicio.replace('T', ' ').slice(0, 19) : '',
    r.fecha_fin ? r.fecha_fin.replace('T', ' ').slice(0, 19) : '',
    (r.estado || '').toUpperCase()
  ])
  downloadCSV(`SmartPark_Reservas_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}
</script>
