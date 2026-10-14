<template>
  <div class="section-view active-section">
    <!-- Configurar Cobros (Culqi) Form Card -->
    <div class="card" style="max-width: 720px; border: 1px solid rgba(14, 165, 233, 0.35); background: linear-gradient(135deg, rgba(14, 165, 233, 0.05) 0%, rgba(2, 132, 199, 0.02) 100%); margin-bottom: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
        <div>
          <div style="display: flex; align-items: center; gap: 10px;">
            <h2 class="card-title" style="margin-bottom: 0; color: var(--accent); font-size: 1.25rem;">
              <i class="fa-solid fa-key"></i> Mis Credenciales Culqi
            </h2>
            <span class="status-badge" :class="cobrosState.verificada ? 'libre' : (cobrosState.configurada ? 'reservado' : 'ocupado')">
              {{ cobrosState.verificada ? '✅ Verificada' : (cobrosState.configurada ? '⚠️ Sin verificar' : '❌ No configurada') }}
            </span>
          </div>
          <p style="font-size: 0.84rem; color: var(--text-muted); margin: 6px 0 0 0;">
            Configura tus credenciales para recibir pagos directos de conductores por cada reserva.
          </p>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 16px; margin-top: 10px;">
        <div class="form-group" style="margin-bottom: 0;">
          <label><i class="fa-solid fa-key" style="color: var(--accent);"></i> Public Key:</label>
          <input v-model="cobrosForm.publicKey" type="text" placeholder="pk_test_xxxxxxxxxxxxxxxx" style="font-family: monospace;">
        </div>

        <div class="form-group" style="margin-bottom: 0;">
          <label><i class="fa-solid fa-lock" style="color: var(--accent);"></i> Secret Key:</label>
          <div style="position: relative; display: flex; align-items: center;">
            <input
              v-model="cobrosForm.secretKey"
              :type="showSecretKey ? 'text' : 'password'"
              placeholder="••••••••"
              style="font-family: monospace; width: 100%; padding-right: 45px;"
            >
            <button
              type="button"
              @click="showSecretKey = !showSecretKey"
              style="position: absolute; right: 12px; background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.15rem;"
            >
              {{ showSecretKey ? '🙈' : '👁️' }}
            </button>
          </div>
          <small style="color: var(--text-muted); font-size: 0.75rem; margin-top: 4px;">
            <i class="fa-solid fa-shield-halved" style="color: var(--accent);"></i> La secret_key se cifra con Fernet antes de guardarse y nunca viaja de vuelta al navegador.
          </small>
        </div>

        <div v-if="cobrosAlert.show" class="alert-inline" :class="cobrosAlert.success ? 'alert-success' : 'alert-danger'">
          <i :class="cobrosAlert.success ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i>
          <span>{{ cobrosAlert.msg }}</span>
        </div>

        <div style="display: flex; gap: 12px; margin-top: 8px; flex-wrap: wrap;">
          <button
            @click="guardarCredencialesCobros"
            :disabled="isSavingCobros"
            class="btn-action"
            style="background: var(--primary); color: #fff; font-weight: 700; padding: 10px 22px; border-radius: 10px; border: none;"
          >
            <i class="fa-solid" :class="isSavingCobros ? 'fa-spinner fa-spin' : 'fa-floppy-disk'"></i> Guardar Credenciales
          </button>
          <button
            @click="probarConexionCobros"
            :disabled="isTestingCobros"
            class="btn-action"
            style="padding: 10px 20px; font-weight: 700; border-radius: 10px;"
          >
            <i class="fa-solid" :class="isTestingCobros ? 'fa-spinner fa-spin' : 'fa-bolt'"></i>
            <span>{{ isTestingCobros ? 'Verificando...' : 'Probar Conexión' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Gráfica de Finanzas -->
    <div class="card" style="margin-bottom: 24px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <div>
          <h2 class="card-title" style="margin-bottom:2px;"><i class="fa-solid fa-chart-line"></i> Ingresos Recaudados</h2>
          <p style="font-size:0.8rem; color:var(--text-muted); margin:0;">Evolución de cobros por sede o consolidado.</p>
        </div>
        <select
          v-model="filtroFinanzasSede"
          @change="onFiltroChange"
          style="padding:6px 12px; border-radius:8px; background:var(--glass-bg); color:var(--text-main); border:1px solid var(--glass-border); font-size:0.85rem; font-weight:600;"
        >
          <option value="">Todas mis sedes (Consolidado)</option>
          <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
        </select>
      </div>
      <canvas id="revenueChartPropietario" height="140"></canvas>
      <div class="revenue-summary-pill">
        <span style="font-size: 0.82rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
          <i class="fa-solid fa-sack-dollar" style="color:#10b981;"></i> Total Recaudado (Periodo)
        </span>
        <span style="font-size: 1.4rem; font-weight: 800; color: #10b981;">
          S/. {{ totalGanancia.toFixed(2) }}
        </span>
      </div>
    </div>

    <!-- Historial de Pagos Recibidos -->
    <div class="card" style="margin-bottom: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div>
          <h2 class="card-title" style="margin-bottom: 2px;">
            <i class="fa-solid fa-money-bill-transfer" style="color: var(--accent);"></i> Historial de Cobros Recibidos
          </h2>
          <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0;">
            Supervisa los pagos de reservas online y los cobros manuales (Walk-in) realizados en caseta física.
          </p>
        </div>
        <span class="status-badge libre">{{ pagosRecibidosList.length }} transacciones</span>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID Pago</th>
              <th>Fecha & Hora</th>
              <th>Sede</th>
              <th>Tipo de Operación</th>
              <th>Monto Recibido</th>
              <th>Canal / Cuenta Destino</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pagosRecibidosList" :key="p.id">
              <td style="font-weight: 700; color: var(--primary);">#{{ p.id }}</td>
              <td style="font-size: 0.85rem; color: var(--text-muted);">{{ formatearFecha(p.fecha_pago || p.fecha_creacion) }}</td>
              <td><strong><i class="fa-solid fa-warehouse" style="font-size:0.8rem; margin-right:4px;"></i>{{ getSedeNombre(p.sede_id) }}</strong></td>
              <td>
                <span v-if="p.metodo_pago === 'efectivo' || !p.reserva_id" style="background:rgba(245,158,11,0.15); color:#f59e0b; padding:4px 8px; border-radius:6px; font-weight:700; font-size:0.78rem;">
                  <i class="fa-solid fa-hand-holding-dollar"></i> Manual (Caseta)
                </span>
                <span v-else style="background:rgba(6,182,212,0.15); color:var(--accent); padding:4px 8px; border-radius:6px; font-weight:700; font-size:0.78rem;">
                  <i class="fa-solid fa-mobile-screen-button"></i> Reserva Online
                </span>
              </td>
              <td style="font-weight: 800; color: #10b981; font-size: 1rem;">S/. {{ Number(p.monto).toFixed(2) }}</td>
              <td>
                <span v-if="p.metodo_pago === 'efectivo' || !p.reserva_id" style="color:var(--text-muted); font-size:0.83rem;">
                  <i class="fa-solid fa-money-bill-wave" style="color:#10b981;"></i> Caja física del Operador
                </span>
                <span v-else style="font-size:0.83rem; color:var(--text-main);">
                  <i class="fa-solid fa-building-columns" style="color:var(--accent);"></i> {{ p.cuenta_destino || 'Cuenta Bancaria Registrada' }}
                </span>
              </td>
              <td>
                <span
                  class="status-badge"
                  :class="(p.estado === 'completado' || p.estado === 'pagado' || p.estado === 'aprobado') ? 'libre' : (p.estado === 'pendiente' ? 'reservado' : 'ocupado')"
                  style="text-transform: capitalize;"
                >
                  {{ p.estado }}
                </span>
              </td>
            </tr>
            <tr v-if="pagosRecibidosList.length === 0">
              <td colspan="7" style="text-align: center; color: var(--text-muted);">No hay transacciones registradas.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { pagosService } from '@/services/pagos'
import Chart from 'chart.js/auto'

const props = defineProps({
  misSedes: { type: Array, default: () => [] },
  pagosRecibidosList: { type: Array, default: () => [] },
  totalGanancia: { type: Number, default: 0 }
})

const emit = defineEmits(['filtro-sede-change', 'toast', 'refresh'])

const filtroFinanzasSede = ref('')
const showSecretKey = ref(false)
const isSavingCobros = ref(false)
const isTestingCobros = ref(false)

const cobrosState = reactive({ configurada: false, verificada: false })
const cobrosForm = reactive({ publicKey: '', secretKey: '' })
const cobrosAlert = reactive({ show: false, success: false, msg: '' })

let chartInstance = null

function getSedeNombre(sedeId) {
  const s = props.misSedes.find(x => x.id === sedeId)
  return s ? s.nombre : (sedeId ? `Sede #${sedeId}` : 'General')
}

function formatearFecha(dateStr) {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('es-PE', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch (e) {
    return dateStr
  }
}

function onFiltroChange() {
  emit('filtro-sede-change', filtroFinanzasSede.value)
}

async function cargarEstadoCredencialesCobros() {
  try {
    const res = await pagosService.getCredencialesEstado()
    const d = res.data
    cobrosState.configurada = d.configurada
    cobrosState.verificada = d.verificada
    if (d.public_key_mask) cobrosForm.publicKey = d.public_key_mask
  } catch (err) {
    cobrosState.configurada = false
    cobrosState.verificada = false
  }
}

async function guardarCredencialesCobros() {
  if (!cobrosForm.publicKey || !cobrosForm.secretKey) {
    cobrosAlert.show = true
    cobrosAlert.success = false
    cobrosAlert.msg = 'Por favor ingresa tanto la Public Key como la Secret Key.'
    return
  }
  isSavingCobros.value = true
  cobrosAlert.show = false
  try {
    const res = await pagosService.guardarCredenciales({
      public_key: cobrosForm.publicKey.trim(),
      secret_key: cobrosForm.secretKey.trim()
    })
    cobrosForm.publicKey = res.data?.public_key_mask || cobrosForm.publicKey
    cobrosForm.secretKey = ''
    cobrosState.configurada = true
    cobrosState.verificada = res.data?.esta_verificada || false
    cobrosAlert.show = true
    cobrosAlert.success = true
    cobrosAlert.msg = 'Credenciales guardadas y cifradas con éxito.'
    emit('toast', { msg: 'Credenciales guardadas con éxito' })
  } catch (err) {
    cobrosAlert.show = true
    cobrosAlert.success = false
    cobrosAlert.msg = err.response?.data?.detail || 'Error al guardar credenciales'
    emit('toast', { msg: 'Error al guardar credenciales', isError: true })
  } finally {
    isSavingCobros.value = false
  }
}

async function probarConexionCobros() {
  isTestingCobros.value = true
  cobrosAlert.show = false
  try {
    const res = await pagosService.verificarCredenciales()
    if (res.data?.estado === 'verificada') {
      cobrosState.verificada = true
      cobrosAlert.show = true
      cobrosAlert.success = true
      cobrosAlert.msg = '✅ Conexión con Culqi exitosa: Credenciales verificadas correctamente.'
      emit('toast', { msg: '✅ Credenciales verificadas correctamente' })
    } else {
      cobrosState.verificada = false
      cobrosAlert.show = true
      cobrosAlert.success = false
      cobrosAlert.msg = res.data?.detail || '❌ Llave inválida o rechazada por Culqi.'
      emit('toast', { msg: 'Credenciales inválidas', isError: true })
    }
  } catch (err) {
    cobrosAlert.show = true
    cobrosAlert.success = false
    cobrosAlert.msg = '❌ Error de comunicación al conectar con Culqi.'
    emit('toast', { msg: 'Error de verificación', isError: true })
  } finally {
    isTestingCobros.value = false
  }
}

function renderChart() {
  const canvas = document.getElementById('revenueChartPropietario')
  if (!canvas) return
  if (chartInstance) chartInstance.destroy()

  const dailyRev = {}
  props.pagosRecibidosList.forEach(p => {
    const st = (p.estado || '').toLowerCase()
    if (st === 'completado' || st === 'pagado' || st === 'aprobado') {
      const m = parseFloat(p.monto) || 0
      const dateStr = new Date(p.fecha_creacion || p.fecha_pago).toLocaleDateString('es-PE', { month: 'short', day: 'numeric' })
      dailyRev[dateStr] = (dailyRev[dateStr] || 0) + m
    }
  })

  const labels = Object.keys(dailyRev)
  const data = labels.map(l => dailyRev[l])

  chartInstance = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['Sin ingresos en periodo'],
      datasets: [{
        label: filtroFinanzasSede.value ? 'Ganancias de Sede S/.' : 'Ganancias Consolidadas S/.',
        data: data.length ? data : [0],
        backgroundColor: filtroFinanzasSede.value ? 'rgba(16, 185, 129, 0.7)' : 'rgba(6, 182, 212, 0.7)',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  })
}

onMounted(() => {
  cargarEstadoCredencialesCobros()
  nextTick(() => renderChart())
})

watch(() => props.pagosRecibidosList, () => {
  nextTick(() => renderChart())
}, { deep: true })

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>
