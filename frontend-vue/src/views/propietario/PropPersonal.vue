<template>
  <div class="section-view active-section">
    <!-- TABS INTERNOS -->
    <div class="inner-tabs">
      <button
        type="button"
        class="inner-tab-btn"
        :class="{ active: tabPersonal === 'directorio' }"
        @click="tabPersonal = 'directorio'"
      >
        <i class="fa-solid fa-address-book"></i> Directorio
      </button>
      <button
        type="button"
        class="inner-tab-btn"
        :class="{ active: tabPersonal === 'contratar' }"
        @click="tabPersonal = 'contratar'"
      >
        <i class="fa-solid fa-user-plus"></i> Contratar
      </button>
    </div>

    <!-- TAB: DIRECTORIO -->
    <div v-show="tabPersonal === 'directorio'">
      <div class="card" style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
          <div>
            <h2 class="card-title" style="margin-bottom:2px;"><i class="fa-solid fa-users-gear"></i> Directorio de Operadores</h2>
            <p style="font-size:0.8rem; color:var(--text-muted);">Personal autorizado para operar las casetas y escanear QR.</p>
          </div>
          <span class="status-badge libre">{{ operadoresList.length }} operadores</span>
        </div>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Operador</th>
                <th>Email</th>
                <th>Sede Asignada</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="op in operadoresList" :key="op.id">
                <td><strong style="color:var(--text-main);">{{ op.nombre }}</strong></td>
                <td style="color:var(--text-muted); font-size:0.85rem;">{{ op.email }}</td>
                <td><span style="color:var(--accent); font-weight:600;"><i class="fa-solid fa-warehouse"></i> {{ getSedeNombre(op.sede_id) }}</span></td>
                <td>
                  <span class="status-badge" :class="op.activo ? 'libre' : 'ocupado'">
                    {{ op.activo ? 'Habilitado' : 'Suspendido' }}
                  </span>
                </td>
                <td>
                  <div style="display:flex; gap:6px;">
                    <button
                      @click="toggleEstadoOperador(op.id)"
                      class="btn-action"
                      :title="op.activo ? 'Suspender' : 'Reactivar'"
                      :style="{ color: op.activo ? '#ef4444' : '#10b981' }"
                    >
                      <i class="fa-solid" :class="op.activo ? 'fa-ban' : 'fa-check'"></i>
                    </button>
                    <button @click="eliminarOperador(op.id)" class="btn-action" title="Eliminar" style="color:#ef4444;">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="operadoresList.length === 0">
                <td colspan="5" style="text-align: center; color: var(--text-muted);">No has contratado operadores todavía.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB: CONTRATAR -->
    <div v-show="tabPersonal === 'contratar'">
      <div class="card" style="max-width: 600px; margin-bottom: 24px;">
        <h2 class="card-title"><i class="fa-solid fa-user-plus"></i> Contratar / Asignar Operador</h2>
        <form @submit.prevent="handleCreateOperador">
          <div class="form-group">
            <label>Nombre Completo</label>
            <input v-model="formOperador.nombre" type="text" required placeholder="Ej. Mario Casas">
          </div>
          <div class="form-group">
            <label>Correo Electrónico (Login)</label>
            <input v-model="formOperador.email" type="email" required placeholder="mario@smartpark.com">
          </div>
          <div class="form-group">
            <label>Contraseña Temporal</label>
            <input v-model="formOperador.password" type="password" required placeholder="Mínimo 6 caracteres">
          </div>
          <div class="form-group">
            <label>Sede Asignada</label>
            <select v-model="formOperador.sede_id" required>
              <option value="">-- Selecciona una Sede --</option>
              <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
          </div>
          <button type="submit" class="btn-submit" style="width: 100%; margin-top: 10px;">Registrar Operador</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { usuariosService } from '@/services/usuarios'

const props = defineProps({
  operadoresList: { type: Array, default: () => [] },
  misSedes: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh', 'toast'])

const tabPersonal = ref('directorio')

const formOperador = reactive({
  nombre: '',
  email: '',
  password: '',
  sede_id: ''
})

function getSedeNombre(sedeId) {
  const s = props.misSedes.find(x => x.id === sedeId)
  return s ? s.nombre : (sedeId ? `Sede #${sedeId}` : 'General')
}

async function handleCreateOperador() {
  try {
    await usuariosService.crearOperador({
      nombre: formOperador.nombre,
      email: formOperador.email,
      password: formOperador.password,
      sede_id: parseInt(formOperador.sede_id)
    })
    emit('toast', { msg: 'Operador registrado exitosamente' })
    formOperador.nombre = ''
    formOperador.email = ''
    formOperador.password = ''
    formOperador.sede_id = ''
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || 'Error al registrar operador', isError: true })
  }
}

async function toggleEstadoOperador(id) {
  try {
    await usuariosService.toggleActivoOperador(id)
    emit('toast', { msg: 'Estado del operador actualizado' })
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: 'Error al modificar operador', isError: true })
  }
}

async function eliminarOperador(id) {
  if (!confirm('¿Seguro que deseas dar de baja definitivamente a este operador?')) return
  try {
    await usuariosService.eliminarOperador(id)
    emit('toast', { msg: 'Operador eliminado' })
    emit('refresh')
  } catch (err) {
    emit('toast', { msg: 'Error al eliminar operador', isError: true })
  }
}
</script>
