<template>
  <div class="modal-overlay" :class="{ 'light-mode': isLight }" :style="{ display: visible ? 'flex' : 'none' }">
    <div class="modal-card">
      <div class="modal-header">
        <h3 class="modal-title text-danger">
          <i class="fa-solid fa-triangle-exclamation"></i> Reportar Incidencia al Dueño
        </h3>
        <button type="button" @click="$emit('close')" class="modal-close-btn">&times;</button>
      </div>
      <form @submit.prevent="enviar">
        <div class="form-group">
          <label>Detalle del problema ocurrido</label>
          <textarea v-model="descripcion" rows="4" placeholder="Ej. Conductor dañó barrera, vehículo abandonado, etc." required></textarea>
        </div>
        <button type="submit" class="btn-submit btn-incidencia">
          <i class="fa-solid fa-paper-plane"></i> Enviar Alerta Inmediata
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  isLight: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'reportar'])

const descripcion = ref('')

watch(() => props.visible, (v) => {
  if (!v) descripcion.value = ''
})

function enviar() {
  emit('reportar', descripcion.value)
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
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  color: var(--text-main, #f8fafc);
  outline: none;
  font-family: inherit;
  resize: vertical;
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
.btn-incidencia {
  background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
}
.text-danger { color: #f87171; }
.modal-overlay.light-mode .modal-card {
  background: #ffffff;
  border-color: #e2e8f0;
}
.modal-overlay.light-mode .form-group textarea {
  background: #ffffff;
  color: #0f172a;
  border-color: #cbd5e1;
}
</style>
