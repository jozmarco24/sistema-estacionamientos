<template>
  <div class="section-view active-section">
    <!-- KPIs de Pagos -->
    <div class="stats-row" style="grid-template-columns: repeat(4, 1fr);">
      <div class="stat-box ingresos">
        <span class="stat-label">Total Transacciones</span>
        <span class="stat-value" style="color: var(--primary);">{{ pagosList.length }}</span>
      </div>
      <div class="stat-box libre">
        <span class="stat-label">Pagos Aprobados</span>
        <span class="stat-value" style="color: var(--color-libre);">{{ statsPagos.aprobados }}</span>
      </div>
      <div class="stat-box reservado">
        <span class="stat-label">Pagos Pendientes</span>
        <span class="stat-value" style="color: var(--color-reservado);">{{ statsPagos.pendientes }}</span>
      </div>
      <div class="stat-box sedes">
        <span class="stat-label">Monto Total Facturado</span>
        <span class="stat-value" style="color: var(--accent);">S/. {{ statsPagos.totalMonto.toFixed(2) }}</span>
      </div>
    </div>

    <!-- Tabla de Pagos & Transacciones -->
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-receipt"></i> Historial Global de Transacciones</h2>
          <span class="status-badge libre">{{ pagosFiltrados.length }} pagos</span>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <input
            v-model="searchPagos"
            type="text"
            placeholder="Buscar por método o ID..."
            style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 220px;"
          >
          <button @click="exportPagosExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
            <i class="fa-solid fa-file-excel"></i> Exportar Excel
          </button>
          <button @click="exportPagosCSV" class="btn-action" title="Exportar a CSV">
            <i class="fa-solid fa-file-csv"></i> Exportar CSV
          </button>
          <button @click="$emit('refresh-pagos')" class="btn-action"><i class="fa-solid fa-rotate"></i> Actualizar</button>
        </div>
      </div>
      <div class="table-wrapper" style="max-height: 480px;">
        <table>
          <thead>
            <tr>
              <th>ID Transacción</th>
              <th>Reserva Asociada</th>
              <th>Monto</th>
              <th>Método de Pago</th>
              <th>Fecha y Hora</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pagosFiltrados" :key="p.id">
              <td><strong>#TX-{{ p.id }}</strong></td>
              <td>
                <span style="color:var(--text-muted);">{{ p.suscripcion_id ? "Suscripción" : "Reserva" }}</span>
                <strong> #{{ p.suscripcion_id || p.reserva_id || "-" }}</strong>
              </td>
              <td><span style="color:#10b981; font-weight:700;">S/. {{ Number(p.monto || 0).toFixed(2) }}</span></td>
              <td>
                <span style="display:inline-flex; align-items:center; gap:6px; font-size:0.85rem; text-transform:capitalize;">
                  <i
                    class="fa-solid"
                    :class="p.metodo_pago === 'yape' || p.metodo_pago === 'plin' ? 'fa-mobile-screen-button' : (p.metodo_pago === 'efectivo' ? 'fa-money-bill-1' : 'fa-credit-card')"
                    style="color:var(--accent);"
                  ></i>
                  {{ p.metodo_pago || 'Tarjeta' }}
                </span>
              </td>
              <td style="font-size:0.85rem; color:var(--text-muted);">{{ formatearFecha(p.fecha_creacion || p.fecha_pago) }}</td>
              <td>
                <span
                  class="status-badge"
                  :class="(p.estado === 'completado' || p.estado === 'aprobado' || p.estado === 'exitoso') ? 'libre' : (p.estado === 'fallido' || p.estado === 'cancelado' ? 'ocupado' : 'reservado')"
                >
                  {{ p.estado ? p.estado.toUpperCase() : 'PENDIENTE' }}
                </span>
              </td>
            </tr>
            <tr v-if="pagosFiltrados.length === 0">
              <td colspan="6" style="text-align: center; color: var(--text-muted);">No hay transacciones registradas.</td>
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
  pagosList: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh-pagos', 'toast'])

const searchPagos = ref('')

const pagosFiltrados = computed(() => {
  if (!searchPagos.value.trim()) return props.pagosList
  const q = searchPagos.value.toLowerCase()
  return props.pagosList.filter(p =>
    (`${p.id}`.includes(q)) ||
    (p.metodo_pago && p.metodo_pago.toLowerCase().includes(q)) ||
    (p.estado && p.estado.toLowerCase().includes(q))
  )
})

const statsPagos = computed(() => {
  let aprobados = 0
  let pendientes = 0
  let totalMonto = 0
  props.pagosList.forEach(p => {
    const m = parseFloat(p.monto) || 0
    totalMonto += m
    const st = (p.estado || '').toLowerCase()
    if (st === 'completado' || st === 'aprobado' || st === 'exitoso') {
      aprobados++
    } else {
      pendientes++
    }
  })
  return { aprobados, pendientes, totalMonto }
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

function exportPagosExcel() {
  if (props.pagosList.length === 0) return emit('toast', { msg: 'No hay transacciones para exportar', isError: true })
  const headers = ['ID_Transaccion', 'Reserva_ID', 'Monto', 'Metodo_Pago', 'Fecha_Pago', 'Estado']
  const data = props.pagosList.map(p => [
    p.id, p.reserva_id || p.suscripcion_id, parseFloat(p.monto) || 0, p.metodo_pago || 'tarjeta',
    p.fecha_creacion || p.fecha_pago || '', p.estado || 'pendiente'
  ])
  downloadExcel(`SmartPark_Transacciones_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Transacciones', headers, data)
}

function exportPagosCSV() {
  if (props.pagosList.length === 0) return emit('toast', { msg: 'No hay transacciones para exportar', isError: true })
  const headers = ['ID_Transaccion', 'Reserva_ID', 'Monto', 'Metodo_Pago', 'Fecha_Pago', 'Estado']
  const data = props.pagosList.map(p => [
    p.id, p.reserva_id || p.suscripcion_id, p.monto, p.metodo_pago || 'tarjeta',
    p.fecha_creacion || p.fecha_pago || '', p.estado || 'pendiente'
  ])
  downloadCSV(`SmartPark_Transacciones_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}
</script>
