<template>
  <div class="section-view active-section">
    <div class="two-cols">
      <!-- Planes SaaS SmartPark -->
      <div class="card">
        <h2 class="card-title"><i class="fa-solid fa-box-open"></i> Planes SaaS SmartPark</h2>
        <div class="table-wrapper" style="max-height: 220px; margin-bottom: 20px;">
          <table>
            <thead>
              <tr>
                <th>Plan</th>
                <th>Precio</th>
                <th>Límites</th>
                <th>Editar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pl in planesList" :key="pl.id">
                <td>
                  <strong>{{ pl.nombre }}</strong><br>
                  <span class="status-badge" :class="pl.activo ? 'libre' : 'ocupado'">{{ pl.activo ? 'Activo' : 'Inactivo' }}</span>
                </td>
                <td>S/. {{ Number(pl.precio).toFixed(2) }}</td>
                <td><span style="font-size:0.75rem;">{{ pl.max_sedes }} sedes<br>{{ pl.max_operadores }} op.</span></td>
                <td>
                  <button @click="editPlan(pl)" class="btn-action"><i class="fa-solid fa-pen"></i></button>
                </td>
              </tr>
              <tr v-if="planesList.length === 0">
                <td colspan="4" style="text-align: center; color: var(--text-muted);">Cargando planes...</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Form Crear/Editar Plan -->
        <form @submit.prevent="handleSavePlan" style="border-top: 1px solid var(--glass-border); padding-top: 15px;">
          <div class="form-group">
            <label>{{ formPlan.id ? `Editando Plan #${formPlan.id} - ${formPlan.nombre}` : 'Crear / Modificar Plan' }}</label>
            <input v-model="formPlan.nombre" type="text" placeholder="Nombre (ej. Plan Pro)" required>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
            <div class="form-group">
              <label>Precio S/.</label>
              <input v-model.number="formPlan.precio" type="number" step="0.01" required>
            </div>
            <div class="form-group">
              <label>Max Sedes</label>
              <input v-model.number="formPlan.max_sedes" type="number" required>
            </div>
            <div class="form-group">
              <label>Max Op.</label>
              <input v-model.number="formPlan.max_operadores" type="number" required>
            </div>
          </div>
          <div v-if="formPlan.id" class="form-group">
            <label>Estado</label>
            <select v-model="formPlan.activo">
              <option :value="true">Activo</option>
              <option :value="false">Inactivo</option>
            </select>
          </div>
          <button type="submit" class="btn-submit" style="margin-top: 10px;">
            {{ formPlan.id ? 'Actualizar Plan' : 'Guardar Plan' }}
          </button>
          <button
            v-if="formPlan.id"
            type="button"
            class="btn-secondary"
            style="margin-top:8px;"
            @click="cancelPlanEdit"
          >
            Cancelar
          </button>
        </form>
      </div>

      <!-- Suscripciones Activas con Control -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-file-invoice"></i> Membresías Activas</h2>
          <span class="status-badge libre">{{ activeSubsCount }} activas</span>
        </div>
        <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:12px;">
          Administra el cobro y estado comercial de cada cliente (Cancelar, Reactivar o Extender +30 días).
        </p>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Propietario</th>
                <th>Plan</th>
                <th>Vencimiento</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in suscripcionesUnicas" :key="s.id">
                <td>
                  <strong>{{ getOwnerName(s.propietario_id) }}</strong><br>
                  <span style="font-size:0.75rem; color:var(--text-muted);">ID Propietario: #{{ s.propietario_id }}</span>
                </td>
                <td><strong>{{ getPlanName(s.plan_id) }}</strong></td>
                <td><span style="font-size:0.85rem;">{{ formatearFecha(s.fecha_vencimiento) }}</span></td>
                <td>
                  <span class="status-badge" :class="s.estado === 'activa' ? 'libre' : 'ocupado'">
                    {{ s.estado ? s.estado.toUpperCase() : 'INACTIVA' }}
                  </span>
                </td>
                <td>
                  <button
                    @click="abrirModalCambiarPlan(s.propietario_id, s.plan_id, getOwnerName(s.propietario_id))"
                    class="btn-action"
                    style="color:var(--accent);"
                    title="Cambiar Plan"
                  >
                    <i class="fa-solid fa-arrows-rotate"></i> Cambiar Plan
                  </button>
                  <button
                    @click="toggleSubscriptionEstado(s.id, 'activa', 30)"
                    class="btn-action"
                    title="Extender +30 días"
                  >
                    <i class="fa-solid fa-calendar-plus"></i> +30 días
                  </button>
                  <button
                    v-if="s.estado === 'activa'"
                    @click="toggleSubscriptionEstado(s.id, 'cancelada')"
                    class="btn-action"
                    style="color:#ef4444;"
                    title="Cancelar membresía"
                  >
                    <i class="fa-solid fa-ban"></i> Cancelar
                  </button>
                  <button
                    v-else
                    @click="toggleSubscriptionEstado(s.id, 'activa')"
                    class="btn-action"
                    style="color:#10b981;"
                    title="Reactivar membresía"
                  >
                    <i class="fa-solid fa-rotate-left"></i> Reactivar
                  </button>
                </td>
              </tr>
              <tr v-if="suscripcionesUnicas.length === 0">
                <td colspan="5" style="text-align: center; color: var(--text-muted);">Sin membresías registradas.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal Cambiar Plan de Membresía -->
    <div v-if="modalPlanAdmin.open" class="modal-overlay">
      <div class="card modal-content" style="width: 500px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid var(--glass-border); padding-bottom:12px;">
          <h3 style="font-size: 1.15rem; margin:0; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-arrows-rotate" style="color: var(--primary);"></i> Cambiar Plan de Membresía
          </h3>
          <button @click="modalPlanAdmin.open = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:14px;">
          Cambiando plan para <strong>{{ modalPlanAdmin.propNombre }}</strong> (Propietario #{{ modalPlanAdmin.propId }}). Su membresía actual quedará cancelada y la nueva se activará inmediatamente por 30 días.
        </p>

        <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:20px;">
          <div
            v-for="p in planesList"
            :key="p.id"
            @click="p.id !== modalPlanAdmin.currentPlanId ? modalPlanAdmin.selectedPlanId = p.id : null"
            :style="{
              padding: '14px 16px',
              borderRadius: '12px',
              border: `2px solid ${modalPlanAdmin.selectedPlanId === p.id ? 'var(--primary)' : 'var(--glass-border)'}`,
              background: modalPlanAdmin.selectedPlanId === p.id ? 'rgba(2, 132, 199, 0.12)' : (modalPlanAdmin.currentPlanId === p.id ? 'rgba(255, 255, 255, 0.02)' : 'rgba(15, 23, 42, 0.5)'),
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              cursor: p.id === modalPlanAdmin.currentPlanId ? 'not-allowed' : 'pointer',
              opacity: p.id === modalPlanAdmin.currentPlanId ? '0.6' : '1',
              transition: 'all 0.2s'
            }"
          >
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <strong :style="{ color: modalPlanAdmin.selectedPlanId === p.id ? 'var(--accent)' : 'var(--text-main)', fontSize: '1rem' }">{{ p.nombre }}</strong>
                <span v-if="p.id === modalPlanAdmin.currentPlanId" class="status-badge libre" style="font-size:0.65rem;">Actual</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">
                {{ p.max_sedes }} Sedes &bull; {{ p.max_operadores }} Operadores
              </div>
            </div>
            <div style="text-align:right;">
              <span style="font-size:1.1rem; font-weight:800; color:var(--text-main);">S/. {{ Number(p.precio).toFixed(2) }}</span>
              <span style="font-size:0.75rem; color:var(--text-muted);">/mes</span>
            </div>
          </div>
        </div>

        <div style="display:flex; justify-content:flex-end; gap:10px;">
          <button type="button" @click="modalPlanAdmin.open = false" class="btn-secondary" style="padding:10px 16px;">Cancelar</button>
          <button
            type="button"
            :disabled="!modalPlanAdmin.selectedPlanId || modalPlanAdmin.selectedPlanId === modalPlanAdmin.currentPlanId || modalPlanAdmin.saving"
            @click="confirmarCambioPlanAdmin"
            class="btn-submit"
            style="padding:10px 18px;"
          >
            <i class="fa-solid" :class="modalPlanAdmin.saving ? 'fa-spinner fa-spin' : 'fa-check'"></i>
            Confirmar Cambio
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { usuariosService } from '@/services/usuarios'

const props = defineProps({
  planesList: { type: Array, default: () => [] },
  suscripcionesList: { type: Array, default: () => [] },
  propietariosList: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh', 'toast'])

const formPlan = reactive({
  id: null,
  nombre: '',
  precio: 0,
  max_sedes: 1,
  max_operadores: 2,
  activo: true
})

const modalPlanAdmin = reactive({
  open: false,
  propId: null,
  currentPlanId: null,
  selectedPlanId: null,
  propNombre: '',
  saving: false
})

const suscripcionesUnicas = computed(() => {
  const map = {}
  props.suscripcionesList.forEach(s => {
    const pid = s.propietario_id
    if (!map[pid]) {
      map[pid] = s
    } else if (map[pid].estado !== 'activa' && s.estado === 'activa') {
      map[pid] = s
    }
  })
  return Object.values(map)
})

const activeSubsCount = computed(() => {
  return suscripcionesUnicas.value.filter(s => s.estado === 'activa').length
})

function getOwnerName(propId) {
  const p = props.propietariosList.find(x => x.id === propId)
  return p ? p.nombre : `Prop #${propId}`
}

function getPlanName(planId) {
  const plan = props.planesList.find(pl => pl.id === planId)
  return plan ? plan.nombre : `Plan #${planId}`
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

function editPlan(pl) {
  formPlan.id = pl.id
  formPlan.nombre = pl.nombre
  formPlan.precio = pl.precio
  formPlan.max_sedes = pl.max_sedes
  formPlan.max_operadores = pl.max_operadores
  formPlan.activo = pl.activo
}

function cancelPlanEdit() {
  formPlan.id = null
  formPlan.nombre = ''
  formPlan.precio = 0
  formPlan.max_sedes = 1
  formPlan.max_operadores = 2
  formPlan.activo = true
}

async function handleSavePlan() {
  try {
    const payload = {
      nombre: formPlan.nombre,
      precio: formPlan.precio,
      max_sedes: formPlan.max_sedes,
      max_operadores: formPlan.max_operadores,
      activo: formPlan.activo
    }
    if (formPlan.id) {
      await usuariosService.actualizarPlan(formPlan.id, payload)
      emit('toast', { msg: 'Plan actualizado' })
    } else {
      await usuariosService.crearPlan(payload)
      emit('toast', { msg: 'Plan creado exitosamente' })
    }
    cancelPlanEdit()
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || 'Error al guardar plan', isError: true })
  }
}

async function toggleSubscriptionEstado(subId, nuevoEstado, extenderDias = null) {
  try {
    const payload = { estado: nuevoEstado }
    if (extenderDias) payload.extender_dias = extenderDias
    await usuariosService.actualizarSuscripcionEstado(subId, payload)
    emit('toast', { msg: extenderDias ? `Membresía #${subId} renovada +30 días` : `Membresía #${subId} cambiada a ${nuevoEstado}` })
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: 'Error al actualizar membresía', isError: true })
  }
}

function abrirModalCambiarPlan(propId, currentPlanId, propNombre) {
  modalPlanAdmin.propId = propId
  modalPlanAdmin.currentPlanId = currentPlanId
  modalPlanAdmin.selectedPlanId = null
  modalPlanAdmin.propNombre = propNombre
  modalPlanAdmin.open = true
}

async function confirmarCambioPlanAdmin() {
  if (!modalPlanAdmin.selectedPlanId || !modalPlanAdmin.propId) return
  modalPlanAdmin.saving = true
  try {
    await usuariosService.cambiarPlanMembresia({
      propietario_id: modalPlanAdmin.propId,
      nuevo_plan_id: modalPlanAdmin.selectedPlanId
    })
    emit('toast', { msg: `¡Plan del propietario #${modalPlanAdmin.propId} cambiado con éxito!` })
    modalPlanAdmin.open = false
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || 'Error al cambiar plan', isError: true })
  } finally {
    modalPlanAdmin.saving = false
  }
}
</script>
