<template>
  <div class="operador-root" :class="{ 'light-mode': themeStore.isLight }">
    <!-- Sidebar Operador -->
    <aside class="sidebar" id="sidebar">
      <div class="logo-area"><i class="fa-solid fa-parking"></i> SmartPark Caseta</div>
      <ul class="nav-menu">
        <router-link
          v-if="authStore.isAdmin"
          to="/admin"
          id="operador-back-admin"
          class="nav-item"
          style="background: linear-gradient(135deg, rgba(2, 132, 199, 0.2) 0%, rgba(3, 105, 161, 0.2) 100%); color: var(--accent); border: 1px solid rgba(2, 132, 199, 0.4);"
        >
          <i class="fa-solid fa-arrow-left"></i> Volver a Admin
        </router-link>
        
        <div class="nav-divider">Operaciones</div>
        <a href="#" class="nav-item active"><i class="fa-solid fa-table-cells"></i> Control de Caseta</a>
        <router-link to="/dashboard" class="nav-item"><i class="fa-solid fa-map-location-dot"></i> Vista Conductor</router-link>
        
        <a href="#" class="nav-item logout-btn" @click.prevent="logout"><i class="fa-solid fa-right-from-bracket"></i> Cerrar Turno</a>
      </ul>
    </aside>

    <main class="main-content">
      <div class="top-header">
        <div class="greeting">
          <h1 id="sede-nombre">{{ currentSedeData?.nombre || 'Cargando Sede...' }}</h1>
          <p id="sede-direccion">
            <i class="fa-solid fa-map-pin"></i> {{ currentSedeData?.direccion || '...' }}
            <span v-if="currentSedeData" style="color:var(--accent); font-weight:700; margin-left:8px;">
              S/. {{ Number(currentSedeData.tarifa_hora || 5).toFixed(2) }} / hr
            </span>
            <div v-if="currentSedeData" style="margin-top:6px; display:flex; gap:10px; font-size:0.83rem; flex-wrap:wrap;">
              <span style="color:var(--accent); font-weight:700;">
                <i class="fa-solid fa-car"></i> Auto: ☀️ S/. {{ Number(currentSedeData.tarifa_auto_dia ?? currentSedeData.tarifa_hora ?? 6).toFixed(2) }} / 🌙 S/. {{ Number(currentSedeData.tarifa_auto_noche ?? 4).toFixed(2) }}
              </span>
              <span style="color:#f59e0b; font-weight:700;">
                <i class="fa-solid fa-motorcycle"></i> Moto: ☀️ S/. {{ Number(currentSedeData.tarifa_moto_dia ?? 3).toFixed(2) }} / 🌙 S/. {{ Number(currentSedeData.tarifa_moto_noche ?? 2).toFixed(2) }}
              </span>
              <span style="background:rgba(255,255,255,0.08); padding:2px 8px; border-radius:6px; font-weight:600; color:var(--text-main);">
                {{ esHorarioDiurno() ? '☀️ Franja Diurna Activa' : '🌙 Franja Nocturna Activa' }}
              </span>
            </div>
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <button @click="refreshAll" class="btn-action" title="Actualizar datos">
            <i class="fa-solid fa-rotate" :class="{ 'fa-spin': cargando }"></i> Actualizar
          </button>
          <button
            @click="toggleTheme"
            id="theme-btn"
            style="background: var(--glass-bg); border: 1px solid var(--glass-border); color: var(--text-main); padding: 10px 16px; border-radius: 12px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.9rem;"
          >
            <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
            {{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}
          </button>
        </div>
      </div>

      <!-- KPIs del Turno -->
      <div class="stats-row">
        <div class="stat-box libre">
          <span class="stat-label">Cajones Libres</span>
          <span class="stat-value" id="stat-libres" style="color: var(--color-libre);">{{ statsLibres }}</span>
        </div>
        <div class="stat-box ocupado">
          <span class="stat-label">Vehículos Dentro</span>
          <span class="stat-value" id="stat-ocupados" style="color: var(--color-ocupado);">{{ statsOcupados }}</span>
        </div>
        <div class="stat-box reservado">
          <span class="stat-label">Reservas Pendientes</span>
          <span class="stat-value" id="stat-reservados" style="color: var(--color-reservado);">{{ statsReservados }}</span>
        </div>
        <div class="stat-box ingresos">
          <span class="stat-label">Caja del Turno (Hoy)</span>
          <span class="stat-value" id="stat-caja-turno" style="color: var(--accent);">S/. {{ cajaTurnoHoy.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Barra de Acciones Rápidas de Caseta -->
      <div class="quick-actions-bar">
        <button @click="openModalValidarQR" class="btn-quick primary">
          <i class="fa-solid fa-qrcode"></i> Validar Ticket / Código QR
        </button>
        <button @click="openModalIngresoManual" class="btn-quick success">
          <i class="fa-solid fa-car-on"></i> + Ingreso Rápido (Walk-in)
        </button>
        <button @click="openModalIncidencia" class="btn-quick" style="background: rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); color:#fca5a5;">
          <i class="fa-solid fa-triangle-exclamation"></i> Reportar Incidencia
        </button>
      </div>

      <!-- Tablero Principal: Cajones Físicos + Movimientos -->
      <div class="dashboard-grid">
        <!-- Grid de Cajones Físicos -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-table-cells"></i> Cajones en Tiempo Real</h2>
            <span style="font-size:0.8rem; color:var(--text-muted);"><i class="fa-solid fa-hand-pointer"></i> Haz clic en un cajón para gestionar salida o ingreso</span>
          </div>
          <div id="slots-grid" class="slot-grid">
            <p v-if="slotsCache.length === 0" style="color: var(--text-muted); grid-column:1/-1; text-align:center;">
              {{ cargando ? 'Cargando espacios...' : 'No hay cajones disponibles.' }}
            </p>
            <div
              v-for="slot in slotsCache"
              :key="slot.id"
              :class="['slot-card', slot.estado]"
              @click="handleSlotClick(slot)"
            >
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                <div class="slot-num">{{ slot.numero }}</div>
                <span style="font-size:0.7rem; font-weight:700; background:rgba(255,255,255,0.08); padding:2px 6px; border-radius:4px; color:var(--text-muted);">
                  <i :class="(slot.tipo_vehiculo || 'auto').toLowerCase() === 'moto' ? 'fa-solid fa-motorcycle text-amber-500' : 'fa-solid fa-car text-sky-400'" style="margin-right:4px;"></i>
                  {{ ((slot.tipo_vehiculo || 'auto').toLowerCase() === 'moto') ? 'MOTO' : 'AUTO' }}
                </span>
              </div>
              <div class="slot-status">
                <i :class="getSlotIcon(slot)"></i> {{ slot.estado }}
              </div>
            </div>
          </div>
        </div>

        <!-- Movimientos y Reservas del Día -->
        <div class="card">
          <h2 class="card-title"><i class="fa-solid fa-clock-rotate-left"></i> Vehículos y Reservas en Caseta</h2>
          <div class="table-wrapper" style="max-height: 420px;">
            <table>
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Cajón</th>
                  <th>Estado</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody id="reservas-tbody">
                <tr v-if="reservasCache.length === 0">
                  <td colspan="4" style="text-align: center; color: var(--text-muted);">Sin movimientos hoy.</td>
                </tr>
                <tr v-for="r in reservasCache.slice(0, 15)" :key="r.id">
                  <td>
                    <strong style="color:var(--accent);"><i class="fa-solid fa-car-side"></i> {{ r.placa_vehiculo || 'N/A' }}</strong>
                  </td>
                  <td><strong>{{ getSlotNumero(r.espacio_id) }}</strong></td>
                  <td>
                    <span :class="['status-badge', getReservaBadgeClass(r.estado)]">
                      {{ getReservaStatusText(r.estado) }}
                    </span>
                  </td>
                  <td>
                    <button
                      v-if="r.estado === 'confirmada'"
                      @click="darIngresoReserva(r.id, r.espacio_id)"
                      class="btn-action"
                      style="color:#10b981;"
                    >
                      <i class="fa-solid fa-arrow-right-to-bracket"></i> Ingreso
                    </button>
                    <span v-else-if="r.estado === 'pendiente'" style="color:#f59e0b; font-size:0.75rem; font-weight:700;">
                      <i class="fa-solid fa-lock"></i> Retenido
                    </span>
                    <button
                      v-else-if="r.estado !== 'finalizada' && r.estado !== 'cancelada'"
                      @click="prepararSalidaDirecta(r.id, r.espacio_id, r.placa_vehiculo)"
                      class="btn-action"
                      style="color:#06b6d4;"
                    >
                      <i class="fa-solid fa-receipt"></i> Salida
                    </button>
                    <span v-else style="color:var(--text-muted); font-size:0.8rem;">Cerrada</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Historial de Pagos y Cobros del Turno en esta Sede -->
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
          <div>
            <h2 class="card-title" style="margin-bottom:2px;"><i class="fa-solid fa-receipt" style="color:var(--accent);"></i> Historial de Cobros de Caseta (Turno Actual)</h2>
            <p style="font-size:0.8rem; color:var(--text-muted); margin:0;">Registro de pagos procesados en esta sede (Online y Efectivo en Caseta).</p>
          </div>
          <span id="badge-operador-pagos" class="status-badge libre">{{ pagosSede.length }} cobros</span>
        </div>
        <div class="table-wrapper" style="max-height: 280px;">
          <table>
            <thead>
              <tr>
                <th>ID Pago</th>
                <th>Fecha & Hora</th>
                <th>Origen</th>
                <th>Monto Cobrado</th>
                <th>Método</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody id="operador-pagos-tbody">
              <tr v-if="pagosSede.length === 0">
                <td colspan="6" style="text-align: center; color: var(--text-muted);">Sin cobros registrados en esta sede durante el turno.</td>
              </tr>
              <tr v-for="p in pagosSede.slice(0, 20)" :key="p.id">
                <td style="font-weight:700; color:var(--primary);">#{{ p.id }}</td>
                <td style="color:var(--text-muted); font-size:0.85rem;">
                  {{ p.fecha_pago ? new Date(p.fecha_pago).toLocaleTimeString('es-PE', { hour:'2-digit', minute:'2-digit' }) : 'Hoy' }}
                </td>
                <td>Reserva #{{ p.reserva_id || 'Walk-in' }}</td>
                <td style="font-weight:800; color:#10b981; font-size:0.95rem;">S/. {{ Number(p.monto).toFixed(2) }}</td>
                <td>
                  <span v-if="p.metodo_pago === 'efectivo'"><i class="fa-solid fa-money-bill-wave" style="color:#10b981;"></i> Efectivo</span>
                  <span v-else><i class="fa-solid fa-credit-card" style="color:var(--accent);"></i> Online</span>
                </td>
                <td>
                  <span :class="['status-badge', (p.estado === 'pagado' || p.estado === 'completado') ? 'libre' : (p.estado === 'pendiente' ? 'reservado' : 'ocupado')]" style="text-transform:capitalize;">
                    {{ p.estado }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- MODAL 1: VALIDAR TICKET / QR -->
    <div class="modal-overlay" :style="{ display: modalQRVisible ? 'flex' : 'none' }">
      <div class="modal-card">
        <div class="modal-header">
          <h3 style="font-size:1.15rem; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-qrcode" style="color:var(--primary);"></i> Validar Ticket o Placa
          </h3>
          <button @click="modalQRVisible = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        <form @submit.prevent="handleBuscarReserva">
          <div class="form-group">
            <label>Código de Reserva o Placa</label>
            <input type="text" v-model="qrInput" placeholder="Ej. #12 o ABC-123" required autofocus />
          </div>
          <button type="submit" class="btn-submit" style="margin-top:4px;">
            <i class="fa-solid fa-magnifying-glass"></i> Consultar Reserva
          </button>
        </form>

        <div v-if="qrResultado" id="qr-resultado" style="margin-top:16px; padding:14px; border-radius:10px; background:rgba(255,255,255,0.04); border:1px solid var(--glass-border);">
          <div v-if="qrResultado.notFound">
            <span style="color:#ef4444;"><i class="fa-solid fa-xmark"></i> No se encontró reserva activa con "{{ qrInput }}".</span>
          </div>
          <div v-else>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <strong style="color:#10b981; font-size:1.05rem;"><i class="fa-solid fa-circle-check"></i> Ticket Válido</strong>
              <span class="status-badge libre">{{ qrResultado.reserva.estado.toUpperCase() }}</span>
            </div>
            <p style="font-size:0.85rem; margin-bottom:4px;"><strong>Placa:</strong> {{ qrResultado.reserva.placa_vehiculo || 'N/A' }}</p>
            <p style="font-size:0.85rem; margin-bottom:8px;"><strong>Cajón Asignado:</strong> {{ getSlotNumero(qrResultado.reserva.espacio_id) }}</p>
            <button
              @click="darIngresoReserva(qrResultado.reserva.id, qrResultado.reserva.espacio_id); modalQRVisible = false;"
              class="btn-submit"
              style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); padding:8px;"
            >
              <i class="fa-solid fa-arrow-right-to-bracket"></i> Autorizar Ingreso Ahora
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL 2: INGRESO RÁPIDO (WALK-IN) -->
    <div class="modal-overlay" :style="{ display: modalIngresoVisible ? 'flex' : 'none' }">
      <div class="modal-card">
        <div class="modal-header">
          <h3 style="font-size:1.15rem; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-car-on" style="color:var(--color-libre);"></i> Ingreso Rápido (Sin Reserva)
          </h3>
          <button @click="modalIngresoVisible = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        <form @submit.prevent="handleIngresoManual">
          <div class="form-group">
            <label>Tipo de Vehículo</label>
            <select v-model="ingresoTipoVehiculo" @change="onIngresoTipoVehiculoChange" required>
              <option value="auto">🚗 Auto / Camioneta</option>
              <option value="moto">🏍️ Moto Lineal</option>
            </select>
          </div>
          <div class="form-group">
            <label>Placa del Vehículo</label>
            <input type="text" v-model="ingresoPlaca" placeholder="Ej. B4Z-512" required maxlength="10" />
          </div>
          <div class="form-group">
            <label>Asignar Cajón Libre Compatible</label>
            <select v-model="ingresoEspacioId" required>
              <option v-if="cajonesCompatibles.length === 0" value="">
                No hay cajones libres para {{ ingresoTipoVehiculo === 'moto' ? 'Moto' : 'Auto' }}
              </option>
              <option v-for="s in cajonesCompatibles" :key="s.id" :value="s.id">
                Cajón {{ s.numero }} ({{ (s.tipo_vehiculo || 'auto').toUpperCase() }})
              </option>
            </select>
          </div>
          <!-- Banner Tarifa Dinámica en Vivo -->
          <div id="ingreso-tarifa-banner" style="background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.25); border-radius: 10px; padding: 10px 14px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 0.85rem; color: var(--text-muted);">
              <span id="ingreso-franja-tag" style="display:inline-block; font-weight: 700; color: #f59e0b; margin-right: 4px;">
                {{ esHorarioDiurno() ? '☀️ Turno Diurno' : '🌙 Turno Nocturno' }}
              </span>
              <span>Tarifa / hr calculada:</span>
            </div>
            <strong id="ingreso-tarifa-monto" style="font-size: 1.15rem; color: #10b981;">
              S/. {{ getTarifaActual(ingresoTipoVehiculo).toFixed(2) }}
            </strong>
          </div>
          <button type="submit" class="btn-submit" style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); margin-top:8px;">
            <i class="fa-solid fa-arrow-right-to-bracket"></i> Dar Ingreso y Abrir Barrera
          </button>
        </form>
      </div>
    </div>

    <!-- MODAL 3: REGISTRAR SALIDA Y COBRO -->
    <div class="modal-overlay" :style="{ display: modalSalidaVisible ? 'flex' : 'none' }">
      <div class="modal-card">
        <div class="modal-header">
          <h3 style="font-size:1.15rem; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-receipt" style="color:var(--accent);"></i> Salida y Cobro en Caseta
          </h3>
          <button @click="modalSalidaVisible = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        
        <div style="background:rgba(255,255,255,0.03); border:1px solid var(--glass-border); padding:16px; border-radius:12px; margin-bottom:14px;">
          <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span style="color:var(--text-muted); font-size:0.85rem;">Cajón:</span>
            <strong id="salida-cajon-lbl" style="color:var(--text-main);">{{ salidaModalData.cajon }}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span style="color:var(--text-muted); font-size:0.85rem;">Placa:</span>
            <strong id="salida-placa-lbl" style="color:var(--accent);">{{ salidaModalData.placa }}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span style="color:var(--text-muted); font-size:0.85rem;">Tarifa Base:</span>
            <span id="salida-tarifa-lbl">S/. {{ salidaModalData.monto.toFixed(2) }} / h</span>
          </div>
          <div style="display:flex; justify-content:space-between; border-top:1px solid var(--glass-border); padding-top:8px; margin-top:8px;">
            <span style="font-size:1rem; font-weight:700;">Monto a Cobrar:</span>
            <strong id="salida-monto-lbl" style="font-size:1.3rem; color:#10b981;">S/. {{ salidaModalData.monto.toFixed(2) }}</strong>
          </div>
        </div>

        <form @submit.prevent="handleProcesarSalida">
          <div class="form-group">
            <label>Método de Cobro</label>
            <select v-model="salidaMetodo">
              <option value="efectivo">Efectivo en Caja</option>
              <option value="yape">Yape / Plin QR</option>
              <option value="tarjeta">POS Tarjeta Débito/Crédito</option>
              <option value="app">Ya pagado por App</option>
            </select>
          </div>
          <button type="submit" class="btn-submit" style="background:linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); margin-top:8px;">
            <i class="fa-solid fa-check-circle"></i> Confirmar Cobro y Liberar Cajón
          </button>
        </form>
      </div>
    </div>

    <!-- MODAL 4: INCIDENCIA -->
    <div class="modal-overlay" :style="{ display: modalIncidenciaVisible ? 'flex' : 'none' }">
      <div class="modal-card">
        <div class="modal-header">
          <h3 style="font-size:1.15rem; color:#f87171; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-triangle-exclamation"></i> Reportar Incidencia al Dueño
          </h3>
          <button @click="modalIncidenciaVisible = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        <form @submit.prevent="handleReportarIncidencia">
          <div class="form-group">
            <label>Detalle del problema ocurrido</label>
            <textarea v-model="incidenciaDesc" rows="4" placeholder="Ej. Conductor dañó barrera, vehículo abandonado, etc." required></textarea>
          </div>
          <button type="submit" class="btn-submit" style="background:linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);">
            <i class="fa-solid fa-paper-plane"></i> Enviar Alerta Inmediata
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { pagosService } from '@/services/pagos'
import { showToast } from '@/components/ToastAlert.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const cargando = ref(false)
const currentSedeData = ref(null)
const slotsCache = ref([])
const reservasCache = ref([])
const pagosSede = ref([])
const cajaTurnoHoy = ref(0)

// Modales
const modalQRVisible = ref(false)
const modalIngresoVisible = ref(false)
const modalSalidaVisible = ref(false)
const modalIncidenciaVisible = ref(false)

const qrInput = ref('')
const qrResultado = ref(null)

const ingresoTipoVehiculo = ref('auto')
const ingresoPlaca = ref('')
const ingresoEspacioId = ref('')

const salidaModalData = ref({
  espacioId: null,
  reservaId: null,
  cajon: '--',
  placa: '--',
  monto: 5.0
})
const salidaMetodo = ref('efectivo')
const incidenciaDesc = ref('')

const statsLibres = computed(() => slotsCache.value.filter(s => s.estado === 'libre').length)
const statsOcupados = computed(() => slotsCache.value.filter(s => s.estado === 'ocupado').length)
const statsReservados = computed(() => slotsCache.value.filter(s => s.estado === 'reservado').length)

const cajonesCompatibles = computed(() => {
  return slotsCache.value.filter(s => s.estado === 'libre' && (s.tipo_vehiculo || 'auto').toLowerCase() === ingresoTipoVehiculo.value.toLowerCase())
})

onMounted(async () => {
  themeStore.initTheme(true)
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await refreshAll()
})

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const esHorarioDiurno = () => {
  if (!currentSedeData.value) return true
  const horaActual = new Date().getHours()
  const horaDia = currentSedeData.value.hora_inicio_dia !== undefined ? currentSedeData.value.hora_inicio_dia : 8
  const horaNoche = currentSedeData.value.hora_inicio_noche !== undefined ? currentSedeData.value.hora_inicio_noche : 20
  return horaActual >= horaDia && horaActual < horaNoche
}

const getTarifaActual = (tipoVehiculo = 'auto') => {
  if (!currentSedeData.value) return 6.0
  const esDiurno = esHorarioDiurno()
  if (tipoVehiculo.toLowerCase() === 'moto') {
    return esDiurno 
      ? (currentSedeData.value.tarifa_moto_dia !== undefined ? currentSedeData.value.tarifa_moto_dia : 3.0)
      : (currentSedeData.value.tarifa_moto_noche !== undefined ? currentSedeData.value.tarifa_moto_noche : 2.0)
  } else {
    return esDiurno 
      ? (currentSedeData.value.tarifa_auto_dia !== undefined ? currentSedeData.value.tarifa_auto_dia : (currentSedeData.value.tarifa_hora || 6.0))
      : (currentSedeData.value.tarifa_auto_noche !== undefined ? currentSedeData.value.tarifa_auto_noche : 4.0)
  }
}

const getSlotIcon = (slot) => {
  const isMoto = (slot.tipo_vehiculo || 'auto').toLowerCase() === 'moto'
  if (slot.estado === 'libre') return 'fa-solid fa-check-circle'
  if (slot.estado === 'ocupado') return isMoto ? 'fa-solid fa-motorcycle' : 'fa-solid fa-car'
  return 'fa-solid fa-clock'
}

const getSlotNumero = (espacioId) => {
  const s = slotsCache.value.find(slot => slot.id === espacioId)
  return s ? `#${s.numero}` : `#${espacioId}`
}

const getReservaBadgeClass = (estado) => {
  if (estado === 'confirmada' || estado === 'pendiente') return 'reservado'
  if (estado === 'cancelada') return 'ocupado'
  return 'libre'
}

const getReservaStatusText = (estado) => {
  if (estado === 'pendiente') return 'EN PAGO (10m)'
  return (estado || 'ACTIVA').toUpperCase()
}

const refreshAll = async () => {
  cargando.value = true
  try {
    const sedeId = authStore.user?.sede_id || 1
    const [sedeRes, slotsRes, reservasRes, pagosRes] = await Promise.allSettled([
      estacionamientosService.getSede(sedeId),
      estacionamientosService.getEspaciosPorSede(sedeId),
      reservasService.getReservas(0, 100),
      pagosService.getPagos()
    ])

    if (sedeRes.status === 'fulfilled') {
      currentSedeData.value = sedeRes.value.data
    }

    if (slotsRes.status === 'fulfilled') {
      const d = slotsRes.value.data
      slotsCache.value = Array.isArray(d) ? d : (d?.data || [])
    }

    if (reservasRes.status === 'fulfilled') {
      const allRes = Array.isArray(reservasRes.value.data) ? reservasRes.value.data : (reservasRes.value.data?.data || [])
      const slotsIds = slotsCache.value.map(s => s.id)
      reservasCache.value = allRes.filter(r => slotsIds.includes(r.espacio_id))
    }

    if (pagosRes.status === 'fulfilled') {
      const allPagos = Array.isArray(pagosRes.value.data) ? pagosRes.value.data : (pagosRes.value.data?.data || [])
      const reservasIds = reservasCache.value.map(r => r.id)
      const sedePagosFiltrados = allPagos.filter(p => 
        p.sede_id === sedeId || (p.reserva_id && reservasIds.includes(p.reserva_id))
      )
      pagosSede.value = sedePagosFiltrados

      let total = 0
      sedePagosFiltrados.forEach(p => {
        const st = (p.estado || '').toLowerCase()
        if (st === 'pagado' || st === 'completado' || st === 'aprobado') {
          total += Number(p.monto || 0)
        }
      })
      cajaTurnoHoy.value = total
    }
  } catch (err) {
    console.warn('Error refrescando operador:', err)
  } finally {
    cargando.value = false
  }
}

const handleSlotClick = (slot) => {
  const isMoto = (slot.tipo_vehiculo || 'auto').toLowerCase() === 'moto'
  const tarifa = getTarifaActual(slot.tipo_vehiculo || 'auto')

  if (slot.estado === 'ocupado') {
    const res = reservasCache.value.find(r => r.espacio_id === slot.id && r.estado !== 'finalizada' && r.estado !== 'cancelada')
    salidaModalData.value = {
      espacioId: slot.id,
      reservaId: res ? res.id : null,
      cajon: `Cajón ${slot.numero} (${isMoto ? 'Moto' : 'Auto'})`,
      placa: res ? (res.placa_vehiculo || 'No registrada') : 'Vehículo en Caseta',
      monto: tarifa
    }
    modalSalidaVisible.value = true
  } else if (slot.estado === 'reservado') {
    const res = reservasCache.value.find(r => r.espacio_id === slot.id && (r.estado === 'confirmada' || r.estado === 'pendiente'))
    if (res && res.estado === 'pendiente') {
      showToast(`Cajón ${slot.numero}: Bloqueado por cliente en proceso de pago online (Soft-lock).`, 'warning')
    } else if (res && res.estado === 'confirmada') {
      if (confirm(`¿Dar ingreso al vehículo con placa ${res.placa_vehiculo || 'reservado'}?`)) {
        darIngresoReserva(res.id, slot.id)
      }
    } else {
      updateSlotState(slot.id, 'ocupado')
    }
  } else {
    ingresoPlaca.value = ''
    ingresoTipoVehiculo.value = isMoto ? 'moto' : 'auto'
    ingresoEspacioId.value = slot.id
    modalIngresoVisible.value = true
  }
}

const openModalValidarQR = () => {
  qrInput.value = ''
  qrResultado.value = null
  modalQRVisible.value = true
}

const openModalIngresoManual = () => {
  ingresoPlaca.value = ''
  onIngresoTipoVehiculoChange()
  modalIngresoVisible.value = true
}

const openModalIncidencia = () => {
  incidenciaDesc.value = ''
  modalIncidenciaVisible.value = true
}

const onIngresoTipoVehiculoChange = () => {
  const compatibles = cajonesCompatibles.value
  ingresoEspacioId.value = compatibles.length > 0 ? compatibles[0].id : ''
}

const handleBuscarReserva = () => {
  const query = qrInput.value.trim().toUpperCase()
  const found = reservasCache.value.find(r => 
    (r.placa_vehiculo && r.placa_vehiculo.toUpperCase().includes(query)) ||
    (`#${r.id}` === query) ||
    (String(r.id) === query)
  )

  if (!found) {
    qrResultado.value = { notFound: true }
  } else {
    qrResultado.value = { notFound: false, reserva: found }
  }
}

const darIngresoReserva = async (reservaId, espacioId) => {
  try {
    await updateSlotState(espacioId, 'ocupado')
    await reservasService.actualizarEstadoReserva(reservaId, 'confirmada')
    showToast('¡Ingreso autorizado! Barrera abierta.', 'success')
    await refreshAll()
  } catch (err) {
    showToast('Error al autorizar ingreso', 'error')
  }
}

const prepararSalidaDirecta = (reservaId, espacioId, placa) => {
  const slot = slotsCache.value.find(s => s.id === espacioId)
  const isMoto = (slot?.tipo_vehiculo || 'auto').toLowerCase() === 'moto'
  const tarifa = getTarifaActual(slot?.tipo_vehiculo || 'auto')
  salidaModalData.value = {
    espacioId,
    reservaId,
    cajon: `Cajón ${slot ? slot.numero : espacioId}`,
    placa: placa || 'Vehículo',
    monto: tarifa
  }
  modalSalidaVisible.value = true
}

const updateSlotState = async (slotId, state) => {
  await estacionamientosService.actualizarEstadoEspacio(slotId, state)
}

const handleIngresoManual = async () => {
  const placa = ingresoPlaca.value.toUpperCase().trim()
  const espacioId = parseInt(ingresoEspacioId.value)
  if (!espacioId) {
    showToast('Seleccione un cajón libre', 'warning')
    return
  }

  const slot = slotsCache.value.find(s => s.id === espacioId)
  const tipoVehiculo = ingresoTipoVehiculo.value || (slot ? slot.tipo_vehiculo : 'auto')
  const tarifaCalculada = getTarifaActual(tipoVehiculo)

  try {
    await reservasService.crearReserva({
      usuario_id: authStore.userId,
      espacio_id: espacioId,
      fecha_inicio: new Date().toISOString(),
      fecha_fin: new Date(Date.now() + 3600000).toISOString(),
      monto_pago: tarifaCalculada,
      metodo_pago: 'efectivo',
      placa_vehiculo: placa
    })

    await updateSlotState(espacioId, 'ocupado')
    modalIngresoVisible.value = false
    showToast(`Vehículo ${placa} ingresado (${tipoVehiculo.toUpperCase()} - Tarifa S/. ${tarifaCalculada.toFixed(2)}). Barrera abierta.`, 'success')
    await refreshAll()
  } catch (err) {
    showToast('Error al registrar ingreso', 'error')
  }
}

const handleProcesarSalida = async () => {
  const { espacioId, reservaId, monto } = salidaModalData.value
  try {
    await updateSlotState(espacioId, 'libre')

    if (reservaId) {
      await reservasService.actualizarEstadoReserva(reservaId, 'finalizada')
    }

    await pagosService.crearPago({
      reserva_id: reservaId ? parseInt(reservaId) : 1,
      monto: monto,
      metodo_pago: salidaMetodo.value,
      estado: 'pagado'
    })

    modalSalidaVisible.value = false
    showToast(`Salida procesada. Cobro S/. ${monto.toFixed(2)} registrado en caja.`, 'success')
    await refreshAll()
  } catch (err) {
    showToast('Error al procesar salida', 'error')
  }
}

const handleReportarIncidencia = async () => {
  try {
    await estacionamientosService.crearIncidencia({
      sede_id: authStore.user?.sede_id || 1,
      operador_id: authStore.userId,
      descripcion: incidenciaDesc.value
    })
    modalIncidenciaVisible.value = false
    showToast('¡Alerta enviada al propietario!', 'success')
  } catch (err) {
    showToast('Error al reportar incidencia', 'error')
  }
}
</script>

<style scoped>
.operador-root {
  --bg-color: #0b0f19;
  --sidebar-bg: rgba(15, 23, 42, 0.85);
  --glass-bg: rgba(30, 41, 59, 0.65);
  --glass-border: rgba(255, 255, 255, 0.1);
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #38bdf8;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --color-libre: #10b981;
  --color-ocupado: #ef4444;
  --color-reservado: #f59e0b;

  background-color: var(--bg-color);
  background-image: 
    radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.1) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.08) 0px, transparent 50%);
  color: var(--text-main);
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

.operador-root.light-mode {
  --bg-color: #f8fafc; 
  --sidebar-bg: rgba(255, 255, 255, 0.95); 
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0; 
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #0284c7;
  --text-main: #0f172a; 
  --text-muted: #64748b;
}

.operador-root.light-mode .nav-item { color: #64748b; }
.operador-root.light-mode .nav-item:hover { background: #f1f5f9; color: #0f172a; }
.operador-root.light-mode .card {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05);
}
.operador-root.light-mode .card-title, .operador-root.light-mode td { color: #0f172a; }
.operador-root.light-mode th { 
  background: #f8fafc; 
  color: #64748b; 
  border-bottom-color: #e2e8f0; 
}
.operador-root.light-mode td { border-bottom-color: #f1f5f9; }
.operador-root.light-mode .form-group input, 
.operador-root.light-mode .form-group select, 
.operador-root.light-mode .form-group textarea { 
  background: #fff; 
  color: #0f172a; 
  border-color: #cbd5e1; 
}
.operador-root.light-mode .slot-card { 
  background: #ffffff; 
  box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
  border-color: #e2e8f0; 
}
.operador-root.light-mode .slot-card .slot-num { color: #0f172a; }
.operador-root.light-mode .stat-box { background: #ffffff; border: 1px solid #e2e8f0; }
.operador-root.light-mode .btn-action {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.operador-root.light-mode .btn-action:hover { background: #e2e8f0; }
.operador-root.light-mode .modal-card {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 20px 40px rgba(0,0,0,0.12);
}
.operador-root.light-mode .modal-header h3 { color: #0f172a; }

.sidebar {
  width: 280px;
  background: var(--sidebar-bg);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  padding: 24px 18px;
  z-index: 100;
  flex-shrink: 0;
}

.logo-area {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-left: 8px;
}
.logo-area i { color: #0284c7; -webkit-text-fill-color: initial; }

.nav-menu { list-style: none; display: flex; flex-direction: column; gap: 6px; flex: 1; }
.nav-item {
  padding: 12px 14px;
  border-radius: 12px;
  color: var(--text-muted);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.25s ease;
  cursor: pointer;
}
.nav-item:hover { background: rgba(255,255,255,0.04); color: var(--text-main); }
.nav-item.active {
  background: linear-gradient(90deg, rgba(2,132,199,0.18) 0%, rgba(2,132,199,0.03) 100%);
  color: var(--primary);
  border-left: 3px solid var(--primary);
  font-weight: 600;
}
.nav-item i { font-size: 1.1rem; width: 22px; text-align: center; }

.nav-divider {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 14px 12px 4px 12px;
  letter-spacing: 1px;
  font-weight: 700;
}

.logout-btn { margin-top: auto; color: #ef4444 !important; }
.logout-btn:hover { background: rgba(239,68,68,0.1) !important; }

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px 40px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.greeting h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
.greeting p { color: var(--text-muted); font-size: 0.95rem; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-box { 
  background: rgba(15, 23, 42, 0.4); 
  border: 1px solid var(--glass-border); 
  border-radius: 16px; 
  padding: 16px; 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
}
.stat-box.libre { border-bottom: 3px solid var(--color-libre); }
.stat-box.ocupado { border-bottom: 3px solid var(--color-ocupado); }
.stat-box.reservado { border-bottom: 3px solid var(--color-reservado); }
.stat-box.ingresos { border-bottom: 3px solid var(--accent); }
.stat-label { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
.stat-value { font-size: 1.8rem; font-weight: 800; }

.card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}
.card-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e2e8f0;
}

.quick-actions-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.btn-quick {
  padding: 12px 18px;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.btn-quick.primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3);
}
.btn-quick.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}
.btn-quick:hover { transform: translateY(-2px); }

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.6fr 1.2fr;
  gap: 22px;
}

.slot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 14px;
}
.slot-card {
  background: rgba(15, 23, 42, 0.6);
  border: 2px solid var(--glass-border);
  border-radius: 16px;
  padding: 18px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.slot-card:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
.slot-card.libre { border-color: var(--color-libre); background: linear-gradient(180deg, rgba(16,185,129,0.12) 0%, rgba(15,23,42,0.6) 100%); }
.slot-card.ocupado { border-color: var(--color-ocupado); background: linear-gradient(180deg, rgba(239,68,68,0.12) 0%, rgba(15,23,42,0.6) 100%); }
.slot-card.reservado { border-color: var(--color-reservado); background: linear-gradient(180deg, rgba(245,158,11,0.12) 0%, rgba(15,23,42,0.6) 100%); }
.slot-card .slot-num { font-size: 1.35rem; font-weight: 800; color: #fff; }
.slot-card .slot-status { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
.slot-card.libre .slot-status { color: var(--color-libre); }
.slot-card.ocupado .slot-status { color: var(--color-ocupado); }
.slot-card.reservado .slot-status { color: var(--color-reservado); }

.table-wrapper { overflow-x: auto; width: 100%; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th { padding: 12px 14px; font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--glass-border); }
td { padding: 12px 14px; font-size: 0.9rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: #e2e8f0; vertical-align: middle; }

.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; }
.status-badge.libre { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.ocupado { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.status-badge.reservado { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.form-group label { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
.form-group input, .form-group select, .form-group textarea {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--text-main);
  font-size: 0.95rem;
  outline: none;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--primary); }

.btn-submit {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 12px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
}
.btn-action {
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-action:hover { background: rgba(255,255,255,0.12); }

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.65); backdrop-filter: blur(6px);
  justify-content: center; align-items: center; z-index: 2000;
}
.modal-card {
  background: var(--bg-color); border: 1px solid var(--glass-border);
  border-radius: 18px; width: 440px; max-width: 90%; padding: 24px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5); position: relative;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 18px; border-bottom: 1px solid var(--glass-border); padding-bottom: 12px;
}

@media (max-width: 900px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: 1fr 1fr; }
}
</style>
