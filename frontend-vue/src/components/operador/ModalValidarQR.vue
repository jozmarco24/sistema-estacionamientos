<template>
  <div class="modal-overlay" :class="{ 'light-mode': isLight }" :style="{ display: visible ? 'flex' : 'none' }">
    <div class="modal-card">
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="fa-solid fa-qrcode text-primary"></i> Validar Ticket o Placa
        </h3>
        <button type="button" @click="$emit('close')" class="modal-close-btn">&times;</button>
      </div>
      <form @submit.prevent="buscar">
        <div class="form-group">
          <label>Código de Reserva o Placa</label>
          <input type="text" v-model="localInput" placeholder="Ej. #12 o ABC-123" required autofocus />
        </div>
        <button type="submit" class="btn-submit modal-action-btn">
          <i class="fa-solid fa-magnifying-glass"></i> Consultar Reserva
        </button>
      </form>

      <div v-if="resultado" class="qr-result-box">
        <div v-if="resultado.notFound">
          <span class="text-danger"><i class="fa-solid fa-xmark"></i> No se encontró reserva activa con "{{ localInput }}".</span>
        </div>
        <div v-else>
          <div class="qr-result-header">
            <strong class="text-success qr-result-valid-title">
              <i class="fa-solid fa-circle-check"></i> Ticket Válido
            </strong>
            <span class="status-badge libre">{{ resultado.reserva.estado.toUpperCase() }}</span>
          </div>
          <p class="qr-info-p"><strong>Placa:</strong> {{ resultado.reserva.placa_vehiculo || 'N/A' }}</p>
          <p class="qr-info-p"><strong>Cajón Asignado:</strong> {{ getSlotNumero(resultado.reserva.espacio_id) }}</p>
          <button
            type="button"
            @click="$emit('autorizar-ingreso', { reservaId: resultado.reserva.id, espacioId: resultado.reserva.espacio_id })"
            class="btn-submit btn-autorizar"
          >
            <i class="fa-solid fa-arrow-right-to-bracket"></i> Autorizar Ingreso Ahora
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  resultado: { type: Object, default: null },
  isLight: { type: Boolean, default: false },
  getSlotNumero: { type: Function, required: true }
})

const emit = defineEmits(['close', 'buscar', 'autorizar-ingreso'])

const localInput = ref('')

watch(() => props.visible, (v) => {
  if (!v) localInput.value = ''
})

function buscar() {
  emit('buscar', localInput.value)
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
.form-group input {
  width: 100%;
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  color: var(--text-main, #f8fafc);
  outline: none;
}
.btn-submit {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--primary, #0284c7) 0%, var(--primary-hover, #0369a1) 100%);
  color: white;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.qr-result-box {
  margin-top: 16px;
  padding: 14px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
}
.qr-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.qr-result-valid-title {
  font-size: 1.05rem;
}
.qr-info-p {
  font-size: 0.85rem;
  margin: 0 0 6px 0;
}
.btn-autorizar {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  padding: 8px;
  margin-top: 8px;
}
.text-primary { color: var(--primary, #0284c7); }
.text-danger { color: #ef4444; }
.text-success { color: #10b981; }
.status-badge {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}
.status-badge.libre {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}
.modal-overlay.light-mode .modal-card {
  background: #ffffff;
  border-color: #e2e8f0;
}
.modal-overlay.light-mode .form-group input {
  background: #ffffff;
  color: #0f172a;
  border-color: #cbd5e1;
}
.modal-overlay.light-mode .modal-title,
.modal-overlay.light-mode .qr-info-p {
  color: #0f172a;
}
</style>
