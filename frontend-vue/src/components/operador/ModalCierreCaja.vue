<template>
  <div class="modal-overlay" :class="{ 'light-mode': isLight }" :style="{ display: visible ? 'flex' : 'none' }">
    <div class="modal-card print-modal-card">
      <div class="modal-header no-print">
        <h3 class="modal-title">
          <i class="fa-solid fa-receipt text-accent"></i> Acta de Cierre de Caja (Turno)
        </h3>
        <button type="button" @click="$emit('close')" class="modal-close-btn">&times;</button>
      </div>

      <div class="print-container" id="ticket-cierre-caja">
        <div class="print-header">
          <h2 class="print-brand"><i class="fa-solid fa-parking"></i> SmartPark Enterprise</h2>
          <p class="print-sede">{{ sedeNombre }}</p>
          <div class="print-meta">
            <span><strong>Fecha/Hora Cierre:</strong> {{ fechaHoraCierre }}</span>
            <span><strong>Operador:</strong> {{ operadorNombre }}</span>
          </div>
        </div>

        <div class="divider-dashed"></div>

        <div class="total-cierre-box">
          <span class="total-label">TOTAL RECAUDADO EN CAJA</span>
          <span class="total-amount">S/. {{ totalRecaudado.toFixed(2) }}</span>
        </div>

        <div class="divider-dashed"></div>

        <div class="desglose-section">
          <h4 class="desglose-title">Desglose por Canal de Pago:</h4>
          <div class="cierre-row">
            <span>💵 Efectivo en Caseta ({{ ticketsEfectivo }} tickets):</span>
            <strong>S/. {{ cajaEfectivo.toFixed(2) }}</strong>
          </div>
          <div class="cierre-row">
            <span>💳 Pagos Online / App ({{ ticketsOnline }} tickets):</span>
            <strong>S/. {{ cajaOnline.toFixed(2) }}</strong>
          </div>
        </div>

        <div class="divider-dashed"></div>

        <div class="desglose-section">
          <h4 class="desglose-title">Desglose por Tipo de Vehículo:</h4>
          <div class="cierre-row">
            <span>🚗 Autos / Camionetas:</span>
            <strong>S/. {{ cajaAutos.toFixed(2) }}</strong>
          </div>
          <div class="cierre-row">
            <span>🏍️ Motos Lineales:</span>
            <strong>S/. {{ cajaMotos.toFixed(2) }}</strong>
          </div>
        </div>

        <div class="divider-dashed"></div>

        <div class="stats-cierre-grid">
          <div class="stat-cierre-col">
            <span class="stat-cierre-lbl">Total Tickets</span>
            <strong class="stat-cierre-val">{{ totalTickets }}</strong>
          </div>
          <div class="stat-cierre-col">
            <span class="stat-cierre-lbl">Ticket Promedio</span>
            <strong class="stat-cierre-val">S/. {{ ticketPromedio.toFixed(2) }}</strong>
          </div>
        </div>

        <div class="firma-box">
          <div class="firma-line"></div>
          <span class="firma-text">Firma y Sello del Operador de Caseta</span>
        </div>
      </div>

      <div class="modal-footer no-print">
        <button type="button" @click="imprimirCierre" class="btn-imprimir">
          <i class="fa-solid fa-print"></i> Imprimir / Exportar Acta
        </button>
        <button type="button" @click="$emit('close')" class="btn-cerrar">
          Entendido
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  isLight: { type: Boolean, default: false },
  sedeNombre: { type: String, default: 'Sede Principal' },
  operadorNombre: { type: String, default: 'Operador' },
  totalRecaudado: { type: Number, default: 0 },
  cajaEfectivo: { type: Number, default: 0 },
  cajaOnline: { type: Number, default: 0 },
  cajaAutos: { type: Number, default: 0 },
  cajaMotos: { type: Number, default: 0 },
  ticketsEfectivo: { type: Number, default: 0 },
  ticketsOnline: { type: Number, default: 0 },
  totalTickets: { type: Number, default: 0 },
  ticketPromedio: { type: Number, default: 0 }
})

defineEmits(['close'])

const fechaHoraCierre = computed(() => {
  return new Date().toLocaleString('es-PE', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
})

function imprimirCierre() {
  window.print()
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
  max-width: 500px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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
.print-container {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  border-radius: 12px;
  padding: 18px;
  color: var(--text-main, #f8fafc);
  font-family: monospace, monospace;
}
.print-header {
  text-align: center;
  margin-bottom: 12px;
}
.print-brand {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--accent, #38bdf8);
  margin: 0 0 4px 0;
}
.print-sede {
  font-size: 0.9rem;
  color: var(--text-muted, #94a3b8);
  margin: 0 0 8px 0;
}
.print-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.8rem;
  color: var(--text-muted, #94a3b8);
}
.divider-dashed {
  border-top: 1px dashed var(--glass-border, rgba(255, 255, 255, 0.15));
  margin: 12px 0;
}
.total-cierre-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.total-label {
  font-size: 0.8rem;
  color: var(--text-muted, #94a3b8);
  letter-spacing: 0.5px;
}
.total-amount {
  font-size: 1.6rem;
  font-weight: 800;
  color: #10b981;
}
.desglose-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.84rem;
}
.desglose-title {
  font-size: 0.82rem;
  color: var(--accent, #38bdf8);
  margin: 0 0 4px 0;
  text-transform: uppercase;
}
.cierre-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stats-cierre-grid {
  display: flex;
  justify-content: space-around;
  margin: 8px 0;
}
.stat-cierre-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-cierre-lbl {
  font-size: 0.78rem;
  color: var(--text-muted, #94a3b8);
}
.stat-cierre-val {
  font-size: 1.05rem;
  color: var(--text-main, #f8fafc);
}
.firma-box {
  margin-top: 28px;
  text-align: center;
}
.firma-line {
  border-top: 1px solid var(--text-muted, #94a3b8);
  width: 70%;
  margin: 0 auto 6px auto;
}
.firma-text {
  font-size: 0.75rem;
  color: var(--text-muted, #94a3b8);
}
.modal-footer {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
.btn-imprimir {
  flex: 1;
  padding: 10px;
  background: var(--primary, #0284c7);
  border: none;
  color: white;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-cerrar {
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
  color: var(--text-main, #f8fafc);
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.text-accent { color: var(--accent, #38bdf8); }
.modal-overlay.light-mode .modal-card {
  background: #ffffff;
  border-color: #e2e8f0;
}
.modal-overlay.light-mode .modal-title,
.modal-overlay.light-mode .print-container,
.modal-overlay.light-mode .stat-cierre-val {
  color: #0f172a;
}
.modal-overlay.light-mode .print-container {
  background: #f8fafc;
  border-color: #cbd5e1;
}
.modal-overlay.light-mode .btn-cerrar {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}

@media print {
  .no-print {
    display: none !important;
  }
  .modal-overlay {
    position: static !important;
    background: none !important;
  }
  .modal-card {
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    max-width: 100% !important;
    color: #000 !important;
  }
  .print-container {
    background: #fff !important;
    border: 1px solid #000 !important;
    color: #000 !important;
  }
}
</style>
