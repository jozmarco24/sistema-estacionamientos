<template>
  <div class="modal-overlay" :class="{ 'light-mode': isLight }" :style="{ display: visible ? 'flex' : 'none' }">
    <div class="modal-card">
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="fa-solid fa-car-on text-success"></i> Ingreso Rápido (Sin Reserva)
        </h3>
        <button type="button" @click="$emit('close')" class="modal-close-btn">&times;</button>
      </div>
      <form @submit.prevent="guardar">
        <div class="form-group">
          <label>Tipo de Vehículo</label>
          <select v-model="tipoVehiculo" @change="onTipoVehiculoChange" required>
            <option value="auto">🚗 Auto / Camioneta</option>
            <option value="moto">🏍️ Moto Lineal</option>
          </select>
        </div>
        <div class="form-group">
          <label>Placa del Vehículo</label>
          <input type="text" v-model="placa" placeholder="Ej. B4Z-512" required maxlength="10" />
        </div>
        <div class="form-group">
          <label>Asignar Cajón Libre Compatible</label>
          <select v-model="espacioId" required>
            <option v-if="cajonesCompatibles.length === 0" value="">
              No hay cajones libres para {{ tipoVehiculo === 'moto' ? 'Moto' : 'Auto' }}
            </option>
            <option v-for="s in cajonesCompatibles" :key="s.id" :value="s.id">
              Cajón {{ s.numero }} ({{ (s.tipo_vehiculo || 'auto').toUpperCase() }})
            </option>
          </select>
        </div>
        <!-- Banner Tarifa Dinámica en Vivo -->
        <div class="tarifa-dinamica-banner">
          <div class="tarifa-dinamica-info">
            <span class="franja-tag">
              {{ esHorarioDiurno ? '☀️ Turno Diurno' : '🌙 Turno Nocturno' }}
            </span>
            <span>Tarifa / hr calculada:</span>
          </div>
          <strong class="tarifa-monto-calc">
            S/. {{ tarifaActual.toFixed(2) }}
          </strong>
        </div>
        <button type="submit" class="btn-submit btn-ingreso">
          <i class="fa-solid fa-arrow-right-to-bracket"></i> Dar Ingreso y Abrir Barrera
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  slotsCache: { type: Array, default: () => [] },
  isLight: { type: Boolean, default: false },
  esHorarioDiurno: { type: Boolean, default: true },
  getTarifaActual: { type: Function, required: true }
})

const emit = defineEmits(['close', 'confirmar-ingreso'])

const tipoVehiculo = ref('auto')
const placa = ref('')
const espacioId = ref('')

const cajonesCompatibles = computed(() => {
  return props.slotsCache.filter(s => s.estado === 'libre' && (s.tipo_vehiculo || 'auto').toLowerCase() === tipoVehiculo.value.toLowerCase())
})

const tarifaActual = computed(() => {
  return props.getTarifaActual(tipoVehiculo.value)
})

function onTipoVehiculoChange() {
  const compatibles = cajonesCompatibles.value
  espacioId.value = compatibles.length > 0 ? compatibles[0].id : ''
}

watch(() => props.visible, (v) => {
  if (v) {
    placa.value = ''
    onTipoVehiculoChange()
  }
})

function guardar() {
  emit('confirmar-ingreso', {
    placa: placa.value.toUpperCase().trim(),
    tipoVehiculo: tipoVehiculo.value,
    espacioId: parseInt(espacioId.value)
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-card {
  background: var(--sidebar-bg, #0f172a);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.modal-title {
  font-size: 1.15rem;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-main, #f8fafc);
  margin: 0;
}
.modal-close-btn {
  background: none;
  border: none;
  color: var(--text-muted, #94a3b8);
  font-size: 1.3rem;
  cursor: pointer;
}
.form-group {
  margin-bottom: 14px;
}
.form-group label {
  display: block;
  font-size: 0.85rem;
  color: var(--text-muted, #94a3b8);
  margin-bottom: 6px;
}
.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  color: var(--text-main, #f8fafc);
  outline: none;
}
.tarifa-dinamica-banner {
  background: rgba(2, 132, 199, 0.08);
  border: 1px solid rgba(2, 132, 199, 0.25);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tarifa-dinamica-info {
  font-size: 0.85rem;
  color: var(--text-muted, #94a3b8);
}
.franja-tag {
  display: inline-block;
  font-weight: 700;
  color: #f59e0b;
  margin-right: 4px;
}
.tarifa-monto-calc {
  font-size: 1.15rem;
  color: #10b981;
}
.btn-submit {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-ingreso {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  margin-top: 8px;
}
.text-success { color: var(--color-libre, #10b981); }
.modal-overlay.light-mode .modal-card {
  background: #ffffff;
  border-color: #e2e8f0;
}
.modal-overlay.light-mode .form-group input,
.modal-overlay.light-mode .form-group select {
  background: #ffffff;
  color: #0f172a;
  border-color: #cbd5e1;
}
.modal-overlay.light-mode .modal-title {
  color: #0f172a;
}
</style>
