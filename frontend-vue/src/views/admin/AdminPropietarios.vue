<template>
  <div class="section-view active-section">
    <!-- Header con Acciones y Contador -->
    <div class="card" style="padding: 20px 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
          <h2 class="card-title" style="margin-bottom: 4px;">
            <i class="fa-solid fa-users-gear" style="color:var(--primary);"></i> Control y Acceso de Propietarios
          </h2>
          <p style="font-size: 0.85rem; color: var(--text-muted);">
            Los propietarios se auto-registran al comprar un plan. Desde aquí puedes <strong>Dar de Baja / Bloquear acceso</strong> al sistema o modificar credenciales.
          </p>
        </div>
        <button
          @click="openModalPropietario(null)"
          class="btn-action"
          style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%); color: #fff; padding: 10px 16px; font-weight: 600; border-radius: 10px;"
        >
          <i class="fa-solid fa-user-plus"></i> Crear Propietario Manual
        </button>
      </div>
    </div>

    <!-- Tabla Principal de Propietarios -->
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <h3 style="font-size: 1rem; color: #e2e8f0;"><i class="fa-solid fa-address-book"></i> Directorio de Dueños de Parqueaderos</h3>
          <span class="status-badge libre">{{ propietariosFiltrados.length }} propietarios</span>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <input
            v-model="searchPropietarios"
            type="text"
            placeholder="Buscar por nombre o email..."
            style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 220px;"
          >
          <button @click="exportPropietariosExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
            <i class="fa-solid fa-file-excel"></i> Exportar Excel
          </button>
          <button @click="exportPropietariosCSV" class="btn-action" title="Exportar a CSV">
            <i class="fa-solid fa-file-csv"></i> Exportar CSV
          </button>
        </div>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Propietario & Contacto</th>
              <th>Plan SaaS Asignado</th>
              <th>Sedes Activas</th>
              <th>Estado de Acceso</th>
              <th>Acción Inmediata</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in propietariosFiltrados" :key="p.id">
              <td>#{{ p.id }}</td>
              <td>
                <strong>{{ p.nombre }}</strong><br>
                <span style="font-size:0.8rem; color:#94a3b8;"><i class="fa-solid fa-envelope"></i> {{ p.email }}</span>
              </td>
              <td>
                <span v-if="getPlanNameForProp(p.id)" style="color:var(--accent); font-weight:600;">
                  <i class="fa-solid fa-gem"></i> {{ getPlanNameForProp(p.id) }}
                </span>
                <span v-else style="color:#94a3b8; font-size:0.8rem;">Sin Plan Activo</span>
              </td>
              <td><span style="font-weight:600;">{{ countSedesForProp(p.id) }}</span> sedes</td>
              <td>
                <span class="status-badge" :class="p.activo ? 'libre' : 'ocupado'">
                  <i class="fa-solid" :class="p.activo ? 'fa-check' : 'fa-ban'"></i>
                  {{ p.activo ? 'Activo' : 'Bloqueado' }}
                </span>
              </td>
              <td>
                <button
                  @click="togglePropietarioAcceso(p)"
                  class="btn-action"
                  :style="{ color: p.activo ? '#ef4444' : '#10b981' }"
                  :title="p.activo ? 'Dar de baja / Bloquear acceso' : 'Reactivar acceso'"
                >
                  <i class="fa-solid" :class="p.activo ? 'fa-user-slash' : 'fa-user-check'"></i>
                  {{ p.activo ? 'Bloquear' : 'Desbloquear' }}
                </button>
                <button @click="openModalPropietario(p)" class="btn-action" title="Editar datos o clave">
                  <i class="fa-solid fa-key"></i>
                </button>
              </td>
            </tr>
            <tr v-if="propietariosFiltrados.length === 0">
              <td colspan="6" style="text-align: center; color: var(--text-muted);">No hay propietarios registrados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Propietario (Crear / Editar) -->
    <div v-if="modalProp.open" class="modal-overlay">
      <div class="card modal-content" style="width: 440px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h2 class="card-title" style="margin-bottom:0;">
            <i class="fa-solid fa-user-plus"></i> {{ modalProp.id ? `Editar Propietario #${modalProp.id}` : 'Registrar Propietario' }}
          </h2>
          <button @click="modalProp.open = false" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
        </div>
        <form @submit.prevent="handleSavePropietario">
          <div class="form-group">
            <label>Nombre Completo</label>
            <input v-model="modalProp.nombre" type="text" required placeholder="Ej. Carlos Mendoza">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="modalProp.email" type="email" required placeholder="carlos@gmail.com">
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input v-model="modalProp.password" type="password" :placeholder="modalProp.id ? '(En blanco para mantener actual)' : 'Contraseña segura'">
          </div>
          <div v-if="modalProp.id" class="form-group">
            <label>Estado de Acceso</label>
            <select v-model="modalProp.activo">
              <option :value="true">Activo (Permitir Ingreso)</option>
              <option :value="false">Bloqueado (Denegar Ingreso)</option>
            </select>
          </div>
          <button type="submit" class="btn-submit" style="margin-top: 10px;">Guardar Propietario</button>
          <button type="button" class="btn-secondary" style="margin-top:8px;" @click="modalProp.open = false">Cancelar</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { usuariosService } from '@/services/usuarios'
import * as XLSX from 'xlsx'

const props = defineProps({
  propietariosList: { type: Array, default: () => [] },
  sedesList: { type: Array, default: () => [] },
  planesList: { type: Array, default: () => [] },
  suscripcionesList: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh', 'toast'])

const searchPropietarios = ref('')

const modalProp = reactive({
  open: false,
  id: null,
  nombre: '',
  email: '',
  password: '',
  activo: true
})

const propietariosFiltrados = computed(() => {
  if (!searchPropietarios.value.trim()) return props.propietariosList
  const q = searchPropietarios.value.toLowerCase()
  return props.propietariosList.filter(p =>
    (p.nombre && p.nombre.toLowerCase().includes(q)) ||
    (p.email && p.email.toLowerCase().includes(q))
  )
})

function countSedesForProp(propId) {
  return props.sedesList.filter(s => s.propietario_id === propId).length
}

function getPlanNameForProp(propId) {
  const sub = props.suscripcionesList.find(s => s.propietario_id === propId && s.estado === 'activa')
  if (!sub) return null
  const plan = props.planesList.find(pl => pl.id === sub.plan_id)
  return plan ? plan.nombre : `Plan #${sub.plan_id}`
}

function openModalPropietario(p) {
  if (p) {
    modalProp.id = p.id
    modalProp.nombre = p.nombre
    modalProp.email = p.email
    modalProp.password = ''
    modalProp.activo = p.activo
  } else {
    modalProp.id = null
    modalProp.nombre = ''
    modalProp.email = ''
    modalProp.password = ''
    modalProp.activo = true
  }
  modalProp.open = true
}

async function handleSavePropietario() {
  try {
    const payload = {
      nombre: modalProp.nombre,
      email: modalProp.email
    }
    if (modalProp.password) payload.password = modalProp.password
    if (modalProp.id) {
      payload.activo = modalProp.activo
      await usuariosService.actualizarPropietario(modalProp.id, payload)
      emit('toast', { msg: 'Propietario actualizado' })
    } else {
      if (!modalProp.password) {
        emit('toast', { msg: 'La contraseña es obligatoria', isError: true })
        return
      }
      payload.rol = 'propietario'
      await usuariosService.crearPropietario(payload)
      emit('toast', { msg: 'Propietario registrado exitosamente' })
    }
    modalProp.open = false
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || 'Error al guardar propietario', isError: true })
  }
}

async function togglePropietarioAcceso(p) {
  try {
    await usuariosService.toggleActivoPropietario(p.id)
    emit('toast', { msg: `Acceso del propietario #${p.id} ${!p.activo ? 'activado' : 'bloqueado'}` })
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: 'Error al cambiar acceso del propietario', isError: true })
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

function exportPropietariosExcel() {
  if (props.propietariosList.length === 0) return emit('toast', { msg: 'No hay propietarios para exportar', isError: true })
  const headers = ['ID', 'Nombre', 'Email', 'Estado_Cuenta']
  const data = props.propietariosList.map(p => [
    p.id, p.nombre, p.email, p.activo ? 'Activo' : 'Bloqueado'
  ])
  downloadExcel(`SmartPark_Propietarios_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Propietarios', headers, data)
}

function exportPropietariosCSV() {
  if (props.propietariosList.length === 0) return emit('toast', { msg: 'No hay propietarios para exportar', isError: true })
  const headers = ['ID', 'Nombre', 'Email', 'Estado_Cuenta']
  const data = props.propietariosList.map(p => [
    p.id, p.nombre, p.email, p.activo ? 'Activo' : 'Bloqueado'
  ])
  downloadCSV(`SmartPark_Propietarios_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}
</script>
