<template>
  <div class="section-view active-section">
    <!-- Healthcheck Status Bar 100% Funcional -->
    <div class="card" style="padding: 20px 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <div>
          <span style="font-size: 0.9rem; font-weight: 700; color: #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px;">
            <i class="fa-solid fa-server" style="color:var(--primary); margin-right: 6px;"></i>
            Estado de Microservicios (Healthcheck en Vivo)
          </span>
          <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
            Comprobación de conectividad, latencia y disponibilidad de endpoints
          </p>
        </div>
        <button @click="$emit('check-health')" class="btn-action" style="padding: 4px 10px; font-size: 0.8rem;">
          <i class="fa-solid fa-arrows-rotate" :class="{ 'fa-spin': isCheckingHealth }"></i> Probar Ahora
        </button>
      </div>

      <div class="health-grid">
        <div class="health-item">
          <div class="health-info">
            <span class="health-name"><i class="fa-solid fa-user-shield" style="color:var(--primary);"></i> Usuarios</span>
            <span class="health-meta">Puerto 8001 | {{ healthStatus.usuarios.ms ? healthStatus.usuarios.ms + ' ms' : '--' }}</span>
          </div>
          <div class="health-status-badge" :class="healthStatus.usuarios.ok ? 'online' : 'offline'">
            <span class="health-dot" :class="healthStatus.usuarios.ok ? 'online' : 'offline'"></span>
            <span>{{ healthStatus.usuarios.ok ? 'Operativo' : 'Caído' }}</span>
          </div>
        </div>

        <div class="health-item">
          <div class="health-info">
            <span class="health-name"><i class="fa-solid fa-square-parking" style="color:#06b6d4;"></i> Estacionamientos</span>
            <span class="health-meta">Puerto 8002 | {{ healthStatus.estacionamientos.ms ? healthStatus.estacionamientos.ms + ' ms' : '--' }}</span>
          </div>
          <div class="health-status-badge" :class="healthStatus.estacionamientos.ok ? 'online' : 'offline'">
            <span class="health-dot" :class="healthStatus.estacionamientos.ok ? 'online' : 'offline'"></span>
            <span>{{ healthStatus.estacionamientos.ok ? 'Operativo' : 'Caído' }}</span>
          </div>
        </div>

        <div class="health-item">
          <div class="health-info">
            <span class="health-name"><i class="fa-solid fa-clock-rotate-left" style="color:#f59e0b;"></i> Reservas</span>
            <span class="health-meta">Puerto 8003 | {{ healthStatus.reservas.ms ? healthStatus.reservas.ms + ' ms' : '--' }}</span>
          </div>
          <div class="health-status-badge" :class="healthStatus.reservas.ok ? 'online' : 'offline'">
            <span class="health-dot" :class="healthStatus.reservas.ok ? 'online' : 'offline'"></span>
            <span>{{ healthStatus.reservas.ok ? 'Operativo' : 'Caído' }}</span>
          </div>
        </div>

        <div class="health-item">
          <div class="health-info">
            <span class="health-name"><i class="fa-solid fa-credit-card" style="color:#10b981;"></i> Pagos</span>
            <span class="health-meta">Puerto 8004 | {{ healthStatus.pagos.ms ? healthStatus.pagos.ms + ' ms' : '--' }}</span>
          </div>
          <div class="health-status-badge" :class="healthStatus.pagos.ok ? 'online' : 'offline'">
            <span class="health-dot" :class="healthStatus.pagos.ok ? 'online' : 'offline'"></span>
            <span>{{ healthStatus.pagos.ok ? 'Operativo' : 'Caído' }}</span>
          </div>
        </div>
      </div>

      <div style="margin-top: 12px; font-size: 0.75rem; color: var(--text-muted); text-align: right;">
        <i class="fa-solid fa-clock"></i> Última comprobación: {{ lastHealthCheckTime || '--' }} (Auto-refresco cada 30s)
      </div>
    </div>

    <!-- Metrics Stats Row (6 Items) -->
    <div class="stats-row">
      <div class="stat-box libre">
        <span class="stat-label">Espacios Libres</span>
        <span class="stat-value" style="color: var(--color-libre);">{{ stats.libres }}</span>
      </div>
      <div class="stat-box reservado">
        <span class="stat-label">Reservados</span>
        <span class="stat-value" style="color: var(--color-reservado);">{{ stats.reservados }}</span>
      </div>
      <div class="stat-box ocupado">
        <span class="stat-label">Ocupados</span>
        <span class="stat-value" style="color: var(--color-ocupado);">{{ stats.ocupados }}</span>
      </div>
      <div class="stat-box sedes">
        <span class="stat-label">Sedes Activas</span>
        <span class="stat-value" style="color: var(--accent);">{{ sedesList.length }}</span>
      </div>
      <div class="stat-box reservas-count">
        <span class="stat-label">Total Reservas</span>
        <span class="stat-value" style="color: #ec4899;">{{ reservasList.length }}</span>
      </div>
      <div class="stat-box ingresos">
        <span class="stat-label">MRR (SaaS Activo)</span>
        <span class="stat-value" style="color: var(--primary);">S/. {{ mrrTotal.toFixed(2) }}</span>
      </div>
    </div>

    <!-- Revenue Chart -->
    <div class="card">
      <h2 class="card-title"><i class="fa-solid fa-chart-line"></i> MRR SaaS (Ingresos Recurrentes por Membresías)</h2>
      <canvas id="revenueChart" height="85"></canvas>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  healthStatus: { type: Object, required: true },
  isCheckingHealth: { type: Boolean, default: false },
  lastHealthCheckTime: { type: String, default: '' },
  stats: { type: Object, required: true },
  sedesList: { type: Array, default: () => [] },
  reservasList: { type: Array, default: () => [] },
  mrrTotal: { type: Number, default: 0 },
  suscripcionesList: { type: Array, default: () => [] },
  planesList: { type: Array, default: () => [] }
})

defineEmits(['check-health'])

let revenueChart = null

function renderRevenueChart() {
  const canvas = document.getElementById('revenueChart')
  if (!canvas) return
  if (revenueChart) revenueChart.destroy()

  const pMap = {}
  props.planesList.forEach(p => { pMap[p.id] = p.precio })

  const dailyRevenue = {}
  props.suscripcionesList.forEach(s => {
    if (s.estado === 'activa') {
      const precio = pMap[s.plan_id] || 0
      const d = s.fecha_creacion ? new Date(s.fecha_creacion).toLocaleDateString() : 'Activo'
      dailyRevenue[d] = (dailyRevenue[d] || 0) + precio
    }
  })

  let labels = Object.keys(dailyRevenue).sort()
  if (labels.length > 7) labels = labels.slice(-7)
  const data = labels.map(l => dailyRevenue[l])

  revenueChart = new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: {
      labels: labels.length > 0 ? labels : ['Semana Actual'],
      datasets: [{
        label: 'MRR Diario (S/.)',
        data: data.length > 0 ? data : [props.mrrTotal],
        borderColor: '#0284c7',
        backgroundColor: 'rgba(2, 132, 199, 0.15)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' }, beginAtZero: true },
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
      }
    }
  })
}

onMounted(() => {
  nextTick(() => renderRevenueChart())
})

watch(() => [props.suscripcionesList, props.planesList, props.mrrTotal], () => {
  nextTick(() => renderRevenueChart())
}, { deep: true })

onUnmounted(() => {
  if (revenueChart) revenueChart.destroy()
})
</script>
