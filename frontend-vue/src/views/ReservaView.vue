<template>
  <div class="reserva-root" :class="{ 'light-mode': themeStore.isLight }">
    <header>
      <router-link to="/dashboard" class="header-logo">
        <i class="fa-solid fa-square-parking"></i> SmartPark
      </router-link>
      <div style="display:flex; align-items:center; gap:12px;">
        <button
          @click="toggleTheme"
          id="theme-btn"
          style="background: rgba(255,255,255,0.08); border: 1px solid var(--glass-border); color: var(--text-light); padding: 8px 16px; border-radius: 99px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.85rem;"
        >
          <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
          {{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}
        </button>
        <router-link to="/dashboard" class="btn-back">
          <i class="fa-solid fa-arrow-left"></i> Volver al Mapa
        </router-link>
      </div>
    </header>

    <div class="main-card">
      <div class="sede-info">
        <h1 id="sede-nombre" class="sede-title">{{ sedeData?.nombre || 'Cargando Sede...' }}</h1>
        <p id="sede-direccion" class="sede-desc">
          <i class="fa-solid fa-map-pin"></i> {{ sedeData?.direccion || '...' }}
        </p>
      </div>

      <div v-if="alertMessage" id="alert-box" class="alert">
        {{ alertMessage }}
      </div>

      <div class="layout-spaces">
        <h2 class="layout-title">Selecciona un Espacio</h2>
        <div class="legend">
          <div class="legend-item"><div class="legend-color" style="background-color: var(--color-libre);"></div> Libre</div>
          <div class="legend-item"><div class="legend-color" style="background-color: #f59e0b;"></div> En Proceso / Bloqueado</div>
          <div class="legend-item"><div class="legend-color" style="background-color: var(--color-ocupado);"></div> Ocupado / Reservado</div>
        </div>
        
        <div id="spaces-container" class="spaces-grid">
          <p v-if="espacios.length === 0" style="grid-column: 1/-1; color: #94a3b8;">
            {{ cargando ? 'Cargando espacios...' : 'No hay espacios creados en esta sede.' }}
          </p>
          <div
            v-for="space in espacios"
            :key="space.id"
            :id="`space-${space.id}`"
            :class="['space-item', space.estado, { selected: selectedSpaceId === space.id }]"
            @click="selectSpace(space)"
          >
            <span class="number">{{ space.numero }}</span>
            <span class="status-lbl">{{ space.estado }}</span>
          </div>
        </div>
      </div>

      <form id="reservation-form" @submit.prevent="handleReserve">
        <div class="form-grid">
          <div class="input-group">
            <label for="fecha-inicio">Fecha/Hora Ingreso</label>
            <input type="datetime-local" id="fecha-inicio" v-model="fechaInicio" required @change="recalcularCotizacion" />
          </div>
          <div class="input-group">
            <label for="fecha-fin">Fecha/Hora Salida</label>
            <input type="datetime-local" id="fecha-fin" v-model="fechaFin" required @change="recalcularCotizacion" />
          </div>
          <div class="input-group">
            <label>Método de Pago</label>
            <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 10px; padding: 12px 14px; display:flex; align-items:center; gap:10px; color: var(--accent); font-weight:700; font-size:0.9rem;">
              <i class="fa-solid fa-credit-card"></i>
              <span>Pasarela Culqi (Tarjeta / Yape Online)</span>
            </div>
            <input type="hidden" id="metodo-pago" value="tarjeta" />
          </div>
          <div class="input-group">
            <label for="monto">Costo Estimado (S/.)</label>
            <input type="number" id="monto" :value="montoCotizado.toFixed(2)" step="0.01" readonly />
          </div>
          <div class="input-group" style="grid-column: 1 / -1;">
            <label for="vehiculo-select">Vehículo a Estacionar</label>
            <div style="display:flex; gap:10px;">
              <select id="vehiculo-select" v-model="vehiculoSelect" style="flex:1;">
                <option value="" disabled>-- Selecciona tu vehículo --</option>
                <option v-for="v in misVehiculos" :key="v.id" :value="v.placa">
                  {{ v.placa }} - {{ v.marca }} {{ v.modelo }}
                </option>
                <option v-if="misVehiculos.length === 0" value="">Sin vehículos registrados</option>
              </select>
              <input
                type="text"
                id="vehiculo-manual"
                v-model="vehiculoManual"
                placeholder="O escribe tu placa (Ej: ABC-123)"
                style="flex:1; text-transform:uppercase;"
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          class="btn-reserve"
          id="btn-submit"
          :disabled="!selectedSpaceId || procesando"
        >
          <span v-if="procesando" class="loader" style="margin-right:8px;"></span>
          <i v-else class="fa-solid fa-circle-check" style="margin-right:8px;"></i>
          <span>{{ procesando ? 'Procesando con Culqi...' : 'Confirmar y Generar Pago' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { usuariosService } from '@/services/usuarios'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const sedeId = parseInt(route.query.sede_id || '1')
const cargando = ref(false)
const procesando = ref(false)
const alertMessage = ref('')

const sedeData = ref(null)
const espacios = ref([])
const misVehiculos = ref([])
const selectedSpaceId = ref(null)
const montoCotizado = ref(25.0)

const fechaInicio = ref('')
const fechaFin = ref('')
const vehiculoSelect = ref('')
const vehiculoManual = ref('')

const getLocalDateTimeString = (date) => {
  const offsetMs = date.getTimezoneOffset() * 60000
  const localDate = new Date(date.getTime() - offsetMs)
  return localDate.toISOString().slice(0, 16)
}

onMounted(async () => {
  themeStore.initTheme(true)
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  const now = new Date()
  const afterTwoHours = new Date(now.getTime() + (2 * 60 * 60 * 1000))
  fechaInicio.value = getLocalDateTimeString(now)
  fechaFin.value = getLocalDateTimeString(afterTwoHours)

  await fetchSedeDetails()
  await fetchEspacios()
  await fetchVehiculos()
  await recalcularCotizacion()
})

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const fetchSedeDetails = async () => {
  try {
    const res = await estacionamientosService.getSede(sedeId)
    sedeData.value = res.data
  } catch (err) {
    alertMessage.value = 'No se pudo obtener información de la sede'
  }
}

const fetchEspacios = async () => {
  cargando.value = true
  try {
    const res = await estacionamientosService.getEspaciosPorSede(sedeId)
    const d = res.data
    espacios.value = Array.isArray(d) ? d : (d?.data || [])
  } catch (err) {
    alertMessage.value = 'No se pudieron obtener los espacios'
  } finally {
    cargando.value = false
  }
}

const fetchVehiculos = async () => {
  try {
    const res = await usuariosService.getVehiculos()
    const vehiculos = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    misVehiculos.value = vehiculos
    if (vehiculos.length > 0) {
      vehiculoSelect.value = vehiculos[0].placa
    }
  } catch (err) {
    console.warn('Error cargando vehículos:', err)
  }
}

const selectSpace = (space) => {
  if (space.estado !== 'libre') return
  selectedSpaceId.value = space.id
  recalcularCotizacion()
}

const recalcularCotizacion = async () => {
  if (!selectedSpaceId.value) return
  if (!fechaInicio.value || !fechaFin.value) return

  try {
    const startIso = new Date(fechaInicio.value).toISOString()
    const endIso = new Date(fechaFin.value).toISOString()
    const res = await reservasService.cotizarReserva(selectedSpaceId.value, startIso, endIso)
    const cot = res.data
    const montoFinal = cot.monto_estimado !== undefined ? cot.monto_estimado : (cot.monto_total || 25.0)
    montoCotizado.value = Number(montoFinal)
  } catch (e) {
    console.warn('Error cotizando reserva:', e)
  }
}

const handleReserve = async () => {
  if (!selectedSpaceId.value) return

  procesando.value = true
  alertMessage.value = ''

  let placa = vehiculoSelect.value
  const placaMan = vehiculoManual.value.trim().toUpperCase()
  if (placaMan) {
    placa = placaMan
  }

  if (!placa) {
    alertMessage.value = 'Por favor selecciona tu vehículo o ingresa tu placa en el campo de texto.'
    procesando.value = false
    return
  }

  const payload = {
    espacio_id: selectedSpaceId.value,
    fecha_inicio: new Date(fechaInicio.value).toISOString(),
    fecha_fin: new Date(fechaFin.value).toISOString(),
    metodo_pago: 'tarjeta',
    placa_vehiculo: placa
  }

  try {
    const response = await reservasService.crearReserva(payload)
    const data = response.data
    // Redirigir a la pantalla de pago con el ID generado
    router.push({ path: '/pago', query: { reserva_id: data.id } })
  } catch (err) {
    let errMsg = 'Ocurrió un error inesperado al procesar la reserva.'
    const status = err.response?.status
    const data = err.response?.data

    if (status === 409) {
      errMsg = 'El espacio seleccionado acaba de ser reservado por otro usuario. Por favor selecciona otro.'
    } else if (data && data.detail) {
      if (typeof data.detail === 'string') {
        errMsg = data.detail
      } else if (Array.isArray(data.detail)) {
        errMsg = data.detail.map(d => `${d.loc ? d.loc.slice(-1) : ''}: ${d.msg}`).join(' | ')
      } else {
        errMsg = JSON.stringify(data.detail)
      }
    }
    alertMessage.value = errMsg
    await fetchEspacios()
  } finally {
    procesando.value = false
  }
}
</script>

<style scoped>
.reserva-root {
  --bg-gradient: linear-gradient(135deg, #0b0f19 0%, #0f172a 100%);
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #38bdf8;
  --text-light: #f8fafc;
  --text-muted: #94a3b8;
  --glass-bg: rgba(17, 24, 39, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);
  --card-sub: rgba(15, 23, 42, 0.5);
  --color-libre: #10b981;
  --color-ocupado: #ef4444;
  --color-reservado: #f59e0b;

  background: var(--bg-gradient);
  background-attachment: fixed;
  min-height: 100vh;
  width: 100vw;
  color: var(--text-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 50px;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  overflow-y: auto;
}

.reserva-root.light-mode {
  --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0;
  --card-sub: #f8fafc;
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #0284c7;
  --text-light: #0f172a;
  --text-muted: #64748b;
}

.reserva-root.light-mode header {
  background: #ffffff;
  border-bottom-color: #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.reserva-root.light-mode .main-card {
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
  border-color: #e2e8f0;
}
.reserva-root.light-mode .sede-title, 
.reserva-root.light-mode .layout-title {
  color: #0f172a;
}
.reserva-root.light-mode .sede-info {
  border-bottom-color: #e2e8f0;
}
.reserva-root.light-mode .space-item {
  background: #ffffff;
  border-color: #e2e8f0;
  color: #0f172a;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}
.reserva-root.light-mode .space-item.libre {
  border-color: var(--color-libre);
  color: var(--color-libre);
}
.reserva-root.light-mode .space-item.libre:hover {
  background: rgba(16, 185, 129, 0.08);
}
.reserva-root.light-mode .space-item.selected {
  background: var(--primary) !important;
  border-color: #0284c7 !important;
  color: #ffffff !important;
  box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
}
.reserva-root.light-mode .input-group label {
  color: #475569;
}
.reserva-root.light-mode .input-group input, 
.reserva-root.light-mode .input-group select {
  background: #ffffff;
  color: #0f172a;
  border-color: #cbd5e1;
}
.reserva-root.light-mode .input-group input:focus, 
.reserva-root.light-mode .input-group select:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}
.reserva-root.light-mode .btn-back {
  background: #f1f5f9;
  border-color: #e2e8f0;
  color: #475569;
}
.reserva-root.light-mode .btn-back:hover {
  background: #e2e8f0;
  color: #0f172a;
}
.reserva-root.light-mode #theme-btn {
  background: #f1f5f9 !important;
  border-color: #e2e8f0 !important;
  color: #0f172a !important;
}

header {
  background: rgba(11, 15, 25, 0.85);
  backdrop-filter: blur(15px);
  border-bottom: 1px solid var(--glass-border);
  padding: 16px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 40px;
}

.header-logo {
  font-size: 1.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-back {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--glass-border);
  color: #94a3b8;
  padding: 8px 16px;
  border-radius: 99px;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.btn-back:hover {
  color: #fff;
  background: rgba(255,255,255,0.1);
}

.main-card {
  background: var(--glass-bg);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  width: 90%;
  max-width: 900px;
  padding: 40px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.sede-info {
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding-bottom: 20px;
}

.sede-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 6px;
}

.sede-desc {
  color: #94a3b8;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 25px;
  display: block;
}

.layout-spaces {
  margin-bottom: 35px;
}

.layout-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: #e2e8f0;
}

.spaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.space-item {
  background: rgba(15, 23, 42, 0.5);
  border: 2px solid var(--glass-border);
  border-radius: 12px;
  height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.space-item .number {
  font-size: 1.2rem;
  font-weight: 700;
}

.space-item .status-lbl {
  font-size: 0.7rem;
  text-transform: uppercase;
  font-weight: 600;
  margin-top: 4px;
  opacity: 0.8;
}

.space-item.libre {
  border-color: var(--color-libre);
  color: var(--color-libre);
}
.space-item.libre:hover {
  background: rgba(16, 185, 129, 0.1);
  transform: scale(1.05);
}

.space-item.ocupado {
  border-color: var(--color-ocupado);
  color: var(--color-ocupado);
  cursor: not-allowed;
  opacity: 0.6;
}

.space-item.reservado {
  border-color: var(--color-reservado);
  color: var(--color-reservado);
  cursor: not-allowed;
  opacity: 0.6;
}

.space-item.selected {
  background: var(--primary) !important;
  border-color: #fff !important;
  color: #fff !important;
  box-shadow: 0 0 15px rgba(2, 132, 199, 0.6);
  transform: scale(1.08);
}

.legend {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  font-size: 0.9rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.input-group {
  text-align: left;
}

.input-group label {
  display: block;
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 6px;
  font-weight: 600;
  text-transform: uppercase;
}

.input-group input, 
.input-group select {
  width: 100%;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 14px 16px;
  color: var(--text-light);
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.input-group input:focus, 
.input-group select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}

.btn-reserve {
  width: 100%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  border: none;
  border-radius: 12px;
  padding: 16px;
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn-reserve:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(2, 132, 199, 0.6);
  background: linear-gradient(135deg, var(--accent) 0%, var(--primary) 100%);
}

.btn-reserve:disabled {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.05);
  color: #64748b;
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
}

.loader {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  header { padding: 16px 20px; }
  .main-card { padding: 24px; }
}
</style>
