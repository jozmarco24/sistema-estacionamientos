<template>
  <div class="modal-overlay" :class="{ 'light-mode': isLight }" :style="{ display: visible ? 'flex' : 'none' }">
    <div class="modal-card">
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="fa-solid fa-triangle-exclamation text-warning"></i> ¿Cerrar turno?
        </h3>
        <button type="button" @click="$emit('cancel')" class="modal-close-btn">&times;</button>
      </div>
      
      <p class="modal-subtitle">
        Estás a punto de finalizar tu sesión operativa en esta caseta. Revisa el estado actual antes de salir:
      </p>

      <div class="resumen-turno-box">
        <div class="resumen-item">
          <span class="text-muted"><i class="fa-solid fa-car"></i> Vehículos aún dentro:</span>
          <strong class="text-danger font-bold">{{ vehiculosDentro }} vehículos</strong>
        </div>
        <div class="resumen-item">
          <span class="text-muted"><i class="fa-solid fa-sack-dollar"></i> Caja acumulada del turno:</span>
          <strong class="text-success font-bold">S/. {{ cajaTurno.toFixed(2) }}</strong>
        </div>
        <div class="resumen-item">
          <span class="text-muted"><i class="fa-solid fa-ticket"></i> Tickets procesados:</span>
          <strong class="text-accent font-bold">{{ totalTickets }} tickets</strong>
        </div>
      </div>

      <div class="modal-actions-grid">
        <button type="button" @click="$emit('cancel')" class="btn-cancelar">
          Cancelar
        </button>
        <button type="button" @click="$emit('confirmar')" class="btn-confirmar-cierre">
          <i class="fa-solid fa-right-from-bracket"></i> Sí, cerrar turno
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  isLight: { type: Boolean, default: false },
  vehiculosDentro: { type: Number, default: 0 },
  cajaTurno: { type: Number, default: 0 },
  totalTickets: { type: Number, default: 0 }
})

defineEmits(['cancel', 'confirmar'])
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
  max-width: 440px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.modal-title {
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-main, #f8fafc);
  margin: 0;
}
.modal-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted, #94a3b8);
  margin: 0 0 16px 0;
  line-height: 1.4;
}
.modal-close-btn {
  background: none;
  border: none;
  color: var(--text-muted, #94a3b8);
  font-size: 1.3rem;
  cursor: pointer;
}
.resumen-turno-box {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.resumen-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}
.text-muted { color: var(--text-muted, #94a3b8); }
.text-danger { color: #ef4444; }
.text-success { color: #10b981; }
.text-accent { color: var(--accent, #38bdf8); }
.text-warning { color: #f59e0b; }
.font-bold { font-weight: 700; }

.modal-actions-grid {
  display: flex;
  gap: 12px;
}
.btn-cancelar {
  flex: 1;
  padding: 10px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  color: var(--text-main, #f8fafc);
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-confirmar-cierre {
  flex: 1;
  padding: 10px;
  background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
  border: none;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.modal-overlay.light-mode .modal-card {
  background: #ffffff;
  border-color: #e2e8f0;
}
.modal-overlay.light-mode .modal-title {
  color: #0f172a;
}
.modal-overlay.light-mode .btn-cancelar {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
</style>
