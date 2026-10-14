<template>
  <div class="operador-root" :class="{ 'light-mode': themeStore.isLight }">
    <!-- Overlay móvil para sidebar -->
    <div
      v-if="sidebarOpen"
      class="sidebar-mobile-overlay"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar Operador -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }" id="sidebar">
      <div class="logo-area">
        <i class="fa-solid fa-parking"></i> SmartPark Caseta
      </div>
      <ul class="nav-menu">
        <router-link
          v-if="authStore.isAdmin"
          to="/admin"
          id="operador-back-admin"
          class="nav-item back-admin-link"
        >
          <i class="fa-solid fa-arrow-left"></i> Volver a Admin
        </router-link>
        
        <div class="nav-divider">Operaciones</div>
        <a href="#" class="nav-item active"><i class="fa-solid fa-table-cells"></i> Control de Caseta</a>
        <router-link to="/dashboard" class="nav-item"><i class="fa-solid fa-map-location-dot"></i> Vista Conductor</router-link>
        
        <a href="#" class="nav-item logout-btn" @click.prevent="openModalConfirmCierre"><i class="fa-solid fa-right-from-bracket"></i> Cerrar Turno</a>
      </ul>
    </aside>

    <main class="main-content">
      <!-- Barra de progreso de auto-refresh cada 30 segundos -->
      <div class="auto-refresh-progress-bar">
        <div class="auto-refresh-progress-fill" :style="{ width: refreshProgress + '%' }"></div>
      </div>

      <div class="top-header">
        <div class="greeting-container">
          <button
            class="hamburger-btn"
            @click="sidebarOpen = !sidebarOpen"
            title="Abrir Menú"
            type="button"
          >
            <i class="fa-solid fa-bars"></i>
          </button>
          <div class="greeting">
            <div class="sede-header-row">
              <h1 id="sede-nombre">{{ currentSedeData?.nombre || 'Cargando Sede...' }}</h1>
              <!-- Reloj digital en tiempo real -->
              <span class="live-clock-badge">
                <i class="fa-regular fa-clock"></i> {{ horaActual }}
              </span>
            </div>
            <div id="sede-direccion" class="sede-direccion-text">
              <i class="fa-solid fa-map-pin"></i> {{ currentSedeData?.direccion || '...' }}
              <span v-if="currentSedeData" class="tarifa-hora-badge">
                S/. {{ Number(currentSedeData.tarifa_hora || 5).toFixed(2) }} / hr
              </span>
              <div v-if="currentSedeData" class="franja-horaria-pills">
                <span class="tarifa-auto-pill">
                  <i class="fa-solid fa-car"></i> Auto: ☀️ S/. {{ Number(currentSedeData.tarifa_auto_dia ?? currentSedeData.tarifa_hora ?? 6).toFixed(2) }} / 🌙 S/. {{ Number(currentSedeData.tarifa_auto_noche ?? 4).toFixed(2) }}
                </span>
                <span class="tarifa-moto-pill">
                  <i class="fa-solid fa-motorcycle"></i> Moto: ☀️ S/. {{ Number(currentSedeData.tarifa_moto_dia ?? 3).toFixed(2) }} / 🌙 S/. {{ Number(currentSedeData.tarifa_moto_noche ?? 2).toFixed(2) }}
                </span>
                <span class="franja-status-pill">
                  {{ esHorarioDiurno ? '☀️ Franja Diurna Activa' : '🌙 Franja Nocturna Activa' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <button @click="refreshAll" class="btn-action" title="Actualizar datos">
            <i class="fa-solid fa-rotate" :class="{ 'fa-spin': cargando }"></i> Actualizar
          </button>
          <button
            @click="toggleTheme"
            id="theme-btn"
            class="btn-theme-toggle"
          >
            <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
            {{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}
          </button>
        </div>
      </div>

      <!-- KPIs del Turno -->
      <div class="stats-row">
        <!-- KPI Cajones Libres -->
        <div class="stat-box libre">
          <div class="stat-box-header">
            <span class="stat-label">Cajones Libres</span>
            <i class="fa-solid fa-circle-check text-color-libre"></i>
          </div>
          <span class="stat-value text-color-libre" id="stat-libres">{{ statsLibres }}</span>
          <div class="stat-progress-container">
            <div
              class="stat-progress-bar"
              :class="ocupacionColorClass"
              :style="{ width: ocupacionPct + '%' }"
            ></div>
          </div>
          <span class="stat-subtext">{{ (100 - ocupacionPct).toFixed(0) }}% disponible</span>
        </div>

        <!-- KPI Vehículos Dentro -->
        <div class="stat-box ocupado">
          <div class="stat-box-header">
            <span class="stat-label">Vehículos Dentro</span>
            <i class="fa-solid fa-car text-color-ocupado"></i>
          </div>
          <span class="stat-value text-color-ocupado" id="stat-ocupados">{{ statsOcupados }}</span>
          <div class="stat-progress-container">
            <div
              class="stat-progress-bar"
              :class="ocupacionColorClass"
              :style="{ width: ocupacionPct + '%' }"
            ></div>
          </div>
          <span class="stat-subtext">{{ ocupacionPct }}% ocupación general</span>
        </div>

        <!-- KPI Reservas Pendientes -->
        <div class="stat-box reservado">
          <div class="stat-box-header">
            <span class="stat-label">Reservas Pendientes</span>
            <i class="fa-solid fa-clock text-color-reservado"></i>
          </div>
          <span class="stat-value text-color-reservado" id="stat-reservados">{{ statsReservados }}</span>
          <div class="stat-progress-container">
            <div class="stat-progress-bar bg-reservado" :style="{ width: Math.min(100, (statsReservados / Math.max(1, totalCajones)) * 100) + '%' }"></div>
          </div>
          <span class="stat-subtext">Por ingresar a caseta</span>
        </div>

        <!-- KPI Caja del Turno (Ampliado con Desglose) -->
        <div class="stat-box ingresos caja-card-expanded">
          <div class="caja-card-top">
            <div>
              <span class="stat-label">Caja del Turno (Hoy)</span>
              <div class="stat-value text-accent" id="stat-caja-turno">
                S/. {{ cajaTurnoHoy.toFixed(2) }}
              </div>
            </div>
            <div class="caja-actions-right">
              <span class="badge-tickets-turno">{{ totalTicketsTurno }} tickets</span>
              <button
                type="button"
                @click="openModalCierreCaja"
                class="btn-cerrar-caja"
                title="Generar e imprimir cierre de caja"
              >
                <i class="fa-solid fa-print"></i> Cerrar Caja
              </button>
            </div>
          </div>

          <div class="caja-divider"></div>

          <!-- Desglose Efectivo vs Online & Autos vs Motos -->
          <div class="caja-breakdown-grid">
            <div class="breakdown-item">
              <span class="breakdown-label">💵 Efectivo:</span>
              <strong class="breakdown-val text-success">
                S/. {{ cajaEfectivo.toFixed(2) }}
                <small class="breakdown-sub">({{ ticketsEfectivo }} tkts)</small>
              </strong>
            </div>
            <div class="breakdown-item">
              <span class="breakdown-label">💳 Online:</span>
              <strong class="breakdown-val text-accent">
                S/. {{ cajaOnline.toFixed(2) }}
                <small class="breakdown-sub">({{ ticketsOnline }} tkts)</small>
              </strong>
            </div>
            <div class="breakdown-item">
              <span class="breakdown-label">🚗 Autos:</span>
              <strong class="breakdown-val">S/. {{ cajaAutos.toFixed(2) }}</strong>
            </div>
            <div class="breakdown-item">
              <span class="breakdown-label">🏍️ Motos:</span>
              <strong class="breakdown-val">S/. {{ cajaMotos.toFixed(2) }}</strong>
            </div>
          </div>

          <!-- Meta del Turno con Barra de Progreso y Ticket Promedio -->
          <div class="caja-meta-section">
            <div class="caja-meta-labels">
              <span>Meta Turno: S/. {{ cajaTurnoHoy.toFixed(2) }} / S/. {{ metaDiaria.toFixed(2) }} ({{ metaPct }}%)</span>
              <span class="ticket-promedio-lbl">Promedio: S/. {{ ticketPromedio.toFixed(2) }}</span>
            </div>
            <div class="caja-meta-track">
              <div class="caja-meta-fill" :style="{ width: Math.min(100, metaPct) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Barra de Acciones Rápidas de Caseta + Buscador Rápido de Placa -->
      <div class="quick-actions-bar">
        <button @click="openModalValidarQR" class="btn-quick primary">
          <i class="fa-solid fa-qrcode"></i> Validar Ticket / QR
        </button>
        <button @click="openModalIngresoManual" class="btn-quick success">
          <i class="fa-solid fa-car-on"></i> + Ingreso Rápido (Walk-in)
        </button>
        <button @click="openModalIncidencia" class="btn-quick danger-light">
          <i class="fa-solid fa-triangle-exclamation"></i> Reportar Incidencia
        </button>

        <!-- Buscador rápido de placa -->
        <div class="quick-search-box">
          <i class="fa-solid fa-magnifying-glass search-icon"></i>
          <input
            type="text"
            v-model="busquedaPlaca"
            placeholder="🔍 Buscar placa..."
            class="search-placa-input"
          />
          <button
            v-if="busquedaPlaca"
            @click="busquedaPlaca = ''"
            type="button"
            class="search-clear-btn"
            title="Limpiar búsqueda"
          >
            &times;
          </button>
        </div>
      </div>

      <!-- Tablero Principal: Cajones Físicos + Movimientos -->
      <div class="dashboard-grid">
        <!-- Grid de Cajones Físicos -->
        <div class="card">
          <div class="grid-header-row">
            <div>
              <h2 class="card-title mb-0"><i class="fa-solid fa-table-cells"></i> Cajones en Tiempo Real</h2>
              <span class="hint-click-text"><i class="fa-solid fa-hand-pointer"></i> Haz clic en un cajón para gestionar salida o ingreso</span>
            </div>

            <!-- Filtros en Grid de Cajones: Todos | Libres | Ocupados | Reservados -->
            <div class="grid-filters-group">
              <button
                type="button"
                class="filter-pill-btn"
                :class="{ active: filtroGrid === 'todos' }"
                @click="filtroGrid = 'todos'"
              >
                Todos ({{ slotsCache.length }})
              </button>
              <button
                type="button"
                class="filter-pill-btn"
                :class="{ active: filtroGrid === 'libre' }"
                @click="filtroGrid = 'libre'"
              >
                Libres ({{ statsLibres }})
              </button>
              <button
                type="button"
                class="filter-pill-btn"
                :class="{ active: filtroGrid === 'ocupado' }"
                @click="filtroGrid = 'ocupado'"
              >
                Ocupados ({{ statsOcupados }})
              </button>
              <button
                type="button"
                class="filter-pill-btn"
                :class="{ active: filtroGrid === 'reservado' }"
                @click="filtroGrid = 'reservado'"
              >
                Reservados ({{ statsReservados }})
              </button>
            </div>
          </div>

          <div id="slots-grid" class="slot-grid">
            <p v-if="slotsFiltradosPorGridYPlaca.length === 0" class="no-slots-msg">
              <span v-if="busquedaPlaca">No se encontró ningún vehículo con esa placa.</span>
              <span v-else>{{ cargando ? 'Cargando espacios...' : 'No hay cajones disponibles para el filtro seleccionado.' }}</span>
            </p>
            <div
              v-for="slot in slotsFiltradosPorGridYPlaca"
              :key="slot.id"
              :class="['slot-card', slot.estado]"
              @click="handleSlotClick(slot)"
            >
              <div class="slot-card-top">
                <div class="slot-num">{{ slot.numero }}</div>
                <span class="slot-type-badge">
                  <i :class="(slot.tipo_vehiculo || 'auto').toLowerCase() === 'moto' ? 'fa-solid fa-motorcycle text-amber-500' : 'fa-solid fa-car text-sky-400'" class="slot-type-icon"></i>
                  {{ ((slot.tipo_vehiculo || 'auto').toLowerCase() === 'moto') ? 'MOTO' : 'AUTO' }}
                </span>
              </div>
              
              <!-- Placa si el cajón está ocupado o reservado -->
              <div v-if="getPlacaDeCajon(slot.id)" class="slot-placa-tag">
                <i class="fa-solid fa-id-card"></i> {{ getPlacaDeCajon(slot.id) }}
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
          <div class="table-wrapper max-h-table">
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
                  <td colspan="4" class="text-center-muted">Sin movimientos hoy.</td>
                </tr>
                <tr v-for="r in reservasCache.slice(0, 15)" :key="r.id">
                  <td>
                    <strong class="text-accent"><i class="fa-solid fa-car-side"></i> {{ r.placa_vehiculo || 'N/A' }}</strong>
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
                      class="btn-action text-success"
                    >
                      <i class="fa-solid fa-arrow-right-to-bracket"></i> Ingreso
                    </button>
                    <div v-else-if="r.estado === 'pendiente'" class="action-flex-gap">
                      <span class="badge-retenido">
                        <i class="fa-solid fa-lock"></i> Retenido
                      </span>
                      <button
                        @click="handleLiberarReservaManual(r.id)"
                        class="btn-action text-danger"
                        title="Liberar cajón manualmente"
                      >
                        <i class="fa-solid fa-unlock"></i> Liberar
                      </button>
                    </div>
                    <button
                      v-else-if="r.estado !== 'finalizada' && r.estado !== 'cancelada'"
                      @click="prepararSalidaDirecta(r.id, r.espacio_id, r.placa_vehiculo)"
                      class="btn-action text-info"
                    >
                      <i class="fa-solid fa-receipt"></i> Salida
                    </button>
                    <span v-else class="text-muted-sm">Cerrada</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Historial de Cobros del Turno (Sección Colapsable) -->
      <div class="card">
        <div class="historial-header-row">
          <div>
            <h2 class="card-title mb-2">
              <i class="fa-solid fa-receipt text-accent"></i> 📋 Historial del Turno (Hoy)
            </h2>
            <p class="historial-subtext">Registro detallado de los pagos y cobros procesados en esta sede.</p>
          </div>
          <div class="historial-actions">
            <span id="badge-operador-pagos" class="status-badge libre">{{ pagosSede.length }} cobros</span>
            <button
              type="button"
              @click="historialColapsado = !historialColapsado"
              class="btn-action"
            >
              {{ historialColapsado ? 'Ver historial ▼' : 'Ocultar ▲' }}
            </button>
          </div>
        </div>

        <div v-show="!historialColapsado" class="table-wrapper max-h-table-historial">
          <table>
            <thead>
              <tr>
                <th>Hora</th>
                <th>Placa</th>
                <th>Vehículo</th>
                <th>Tiempo</th>
                <th>Monto</th>
                <th>Tipo Pago</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody id="operador-pagos-tbody">
              <tr v-if="ultimosDiezPagos.length === 0">
                <td colspan="7" class="text-center-muted">Sin cobros registrados en esta sede durante el turno.</td>
              </tr>
              <tr v-for="p in ultimosDiezPagos" :key="p.id">
                <td class="text-muted-sm">
                  {{ formatearHoraPago(p.fecha_pago || p.fecha_creacion) }}
                </td>
                <td>
                  <strong class="text-accent">{{ p.placa || getPlacaDeReserva(p.reserva_id) || 'N/D' }}</strong>
                </td>
                <td>
                  <span class="badge-vehiculo-table">
                    <i :class="(p.tipo_vehiculo || 'auto').toLowerCase() === 'moto' ? 'fa-solid fa-motorcycle text-warning' : 'fa-solid fa-car text-accent'"></i>
                    {{ ((p.tipo_vehiculo || 'auto').toLowerCase() === 'moto') ? 'Moto' : 'Auto' }}
                  </span>
                </td>
                <td class="text-muted-sm">
                  {{ calcularTiempoEstadia(p) }}
                </td>
                <td class="monto-table-val">S/. {{ Number(p.monto).toFixed(2) }}</td>
                <td>
                  <span v-if="p.metodo_pago === 'efectivo'"><i class="fa-solid fa-money-bill-wave text-success"></i> Efectivo</span>
                  <span v-else-if="p.metodo_pago === 'yape'"><i class="fa-solid fa-mobile-screen-button text-purple"></i> Yape/Plin</span>
                  <span v-else-if="p.metodo_pago === 'tarjeta'"><i class="fa-solid fa-credit-card text-accent"></i> Tarjeta POS</span>
                  <span v-else><i class="fa-solid fa-globe text-accent"></i> Online / App</span>
                </td>
                <td>
                  <span :class="['status-badge', (p.estado === 'pagado' || p.estado === 'completado') ? 'libre' : (p.estado === 'pendiente' ? 'reservado' : 'ocupado')]" class="capitalize">
                    {{ p.estado }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- COMPONENTES MODALES SEPARADOS -->
    <ModalValidarQR
      :visible="modalQRVisible"
      :resultado="qrResultado"
      :is-light="themeStore.isLight"
      :get-slot-numero="getSlotNumero"
      @close="modalQRVisible = false"
      @buscar="handleBuscarReservaInput"
      @autorizar-ingreso="onAutorizarIngresoDesdeQR"
    />

    <ModalIngresoManual
      :visible="modalIngresoVisible"
      :slots-cache="slotsCache"
      :is-light="themeStore.isLight"
      :es-horario-diurno="esHorarioDiurno"
      :get-tarifa-actual="getTarifaActual"
      @close="modalIngresoVisible = false"
      @confirmar-ingreso="onConfirmarIngresoManual"
    />

    <ModalIncidencia
      :visible="modalIncidenciaVisible"
      :is-light="themeStore.isLight"
      @close="modalIncidenciaVisible = false"
      @reportar="onReportarIncidenciaSubmit"
    />

    <ModalConfirmCierreTurno
      :visible="modalConfirmCierreVisible"
      :is-light="themeStore.isLight"
      :vehiculos-dentro="statsOcupados"
      :caja-turno="cajaTurnoHoy"
      :total-tickets="totalTicketsTurno"
      @cancel="modalConfirmCierreVisible = false"
      @confirmar="ejecutarCierreTurno"
    />

    <ModalCierreCaja
      :visible="modalCierreCajaVisible"
      :is-light="themeStore.isLight"
      :sede-nombre="currentSedeData?.nombre || 'Sede Principal'"
      :operador-nombre="authStore.user?.nombre || 'Operador de Caseta'"
      :total-recaudado="cajaTurnoHoy"
      :caja-efectivo="cajaEfectivo"
      :caja-online="cajaOnline"
      :caja-autos="cajaAutos"
      :caja-motos="cajaMotos"
      :tickets-efectivo="ticketsEfectivo"
      :tickets-online="ticketsOnline"
      :total-tickets="totalTicketsTurno"
      :ticket-promedio="ticketPromedio"
      @close="modalCierreCajaVisible = false"
    />

    <!-- MODAL SALIDA Y COBRO DIRECTO EN CASETA -->
    <div class="modal-overlay" :style="{ display: modalSalidaVisible ? 'flex' : 'none' }">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title-custom">
            <i class="fa-solid fa-receipt text-accent"></i> Salida y Cobro en Caseta
          </h3>
          <button @click="modalSalidaVisible = false" type="button" class="modal-close-x">&times;</button>
        </div>
        
        <div class="salida-summary-card">
          <div class="salida-summary-row">
            <span class="text-muted-sm">Cajón:</span>
            <strong id="salida-cajon-lbl" class="text-main-val">{{ salidaModalData.cajon }}</strong>
          </div>
          <div class="salida-summary-row">
            <span class="text-muted-sm">Placa:</span>
            <strong id="salida-placa-lbl" class="text-accent">{{ salidaModalData.placa }}</strong>
          </div>
          <div class="salida-summary-row">
            <span class="text-muted-sm">Tarifa Base:</span>
            <span id="salida-tarifa-lbl">S/. {{ salidaModalData.monto.toFixed(2) }} / h</span>
          </div>
          <div class="salida-summary-total-row">
            <span class="font-bold-md">Monto a Cobrar:</span>
            <strong id="salida-monto-lbl" class="monto-cobrar-lg">S/. {{ salidaModalData.monto.toFixed(2) }}</strong>
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
          <button type="submit" class="btn-submit btn-salida-confirm">
            <i class="fa-solid fa-check-circle"></i> Confirmar Cobro y Liberar Cajón
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { pagosService } from '@/services/pagos'
import { showToast } from '@/components/ToastAlert.vue'

// Import de componentes modales extraídos
import ModalValidarQR from '@/components/operador/ModalValidarQR.vue'
import ModalIngresoManual from '@/components/operador/ModalIngresoManual.vue'
import ModalIncidencia from '@/components/operador/ModalIncidencia.vue'
import ModalConfirmCierreTurno from '@/components/operador/ModalConfirmCierreTurno.vue'
import ModalCierreCaja from '@/components/operador/ModalCierreCaja.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// Estados reactivos principales
const cargando = ref(false)
const currentSedeData = ref(null)
const slotsCache = ref([])
const reservasCache = ref([])
const pagosSede = ref([])
const cajaTurnoHoy = ref(0)

// #1 Reloj en tiempo real
const horaActual = ref(new Date().toLocaleTimeString('es-PE', { hour12: false }))
let relojInterval = null

// #2 Auto-refresh y barra de progreso
const refreshProgress = ref(0)
let autoRefreshTimer = null
let progressBarTimer = null

// #3 Buscador rápido de placa
const busquedaPlaca = ref('')

// #11 Filtro en grid de cajones
const filtroGrid = ref('todos')

// #8 Historial colapsable
const historialColapsado = ref(false)

// #13 Sidebar móvil
const sidebarOpen = ref(false)

// Modales reactivos
const modalQRVisible = ref(false)
const qrResultado = ref(null)
const modalIngresoVisible = ref(false)
const modalIncidenciaVisible = ref(false)
const modalConfirmCierreVisible = ref(false)
const modalCierreCajaVisible = ref(false)
const modalSalidaVisible = ref(false)

const salidaModalData = ref({
  espacioId: null,
  reservaId: null,
  cajon: '--',
  placa: '--',
  monto: 5.0
})
const salidaMetodo = ref('efectivo')

// Computed: Métricas de cajones
const totalCajones = computed(() => slotsCache.value.length)
const statsLibres = computed(() => slotsCache.value.filter(s => s.estado === 'libre').length)
const statsOcupados = computed(() => slotsCache.value.filter(s => s.estado === 'ocupado').length)
const statsReservados = computed(() => slotsCache.value.filter(s => s.estado === 'reservado').length)

// #10 Barra de % de ocupación y color dinámico
const ocupacionPct = computed(() => {
  if (totalCajones.value === 0) return 0
  return Math.min(100, Math.round((statsOcupados.value / totalCajones.value) * 100))
})

const ocupacionColorClass = computed(() => {
  if (ocupacionPct.value < 60) return 'bar-green'
  if (ocupacionPct.value <= 85) return 'bar-yellow'
  return 'bar-red'
})

// #15 Convertir esHorarioDiurno a computed
const esHorarioDiurno = computed(() => {
  const hora = new Date().getHours()
  if (!currentSedeData.value) {
    return hora >= 6 && hora < 20
  }
  const horaDia = currentSedeData.value.hora_inicio_dia !== undefined ? currentSedeData.value.hora_inicio_dia : 8
  const horaNoche = currentSedeData.value.hora_inicio_noche !== undefined ? currentSedeData.value.hora_inicio_noche : 20
  return hora >= horaDia && hora < horaNoche
})

// #5, #6 y #7 Desglose de Caja: Efectivo vs Online / Autos vs Motos / Tickets
const transaccionesValidasTurno = computed(() => {
  return pagosSede.value.filter(p => {
    const st = (p.estado || '').toLowerCase()
    return st === 'pagado' || st === 'completado' || st === 'aprobado'
  })
})

const totalTicketsTurno = computed(() => transaccionesValidasTurno.value.length)

const ticketsEfectivo = computed(() => {
  return transaccionesValidasTurno.value.filter(p => (p.metodo_pago || '').toLowerCase() === 'efectivo').length
})

const ticketsOnline = computed(() => {
  return transaccionesValidasTurno.value.filter(p => (p.metodo_pago || '').toLowerCase() !== 'efectivo').length
})

const cajaEfectivo = computed(() => {
  return transaccionesValidasTurno.value
    .filter(p => (p.metodo_pago || '').toLowerCase() === 'efectivo')
    .reduce((acc, p) => acc + Number(p.monto || 0), 0)
})

const cajaOnline = computed(() => {
  return transaccionesValidasTurno.value
    .filter(p => (p.metodo_pago || '').toLowerCase() !== 'efectivo')
    .reduce((acc, p) => acc + Number(p.monto || 0), 0)
})

const cajaAutos = computed(() => {
  return transaccionesValidasTurno.value
    .filter(p => {
      const tipo = (p.tipo_vehiculo || getTipoVehiculoDeReserva(p.reserva_id) || 'auto').toLowerCase()
      return tipo !== 'moto'
    })
    .reduce((acc, p) => acc + Number(p.monto || 0), 0)
})

const cajaMotos = computed(() => {
  return transaccionesValidasTurno.value
    .filter(p => {
      const tipo = (p.tipo_vehiculo || getTipoVehiculoDeReserva(p.reserva_id) || 'auto').toLowerCase()
      return tipo === 'moto'
    })
    .reduce((acc, p) => acc + Number(p.monto || 0), 0)
})

// #12 Ticket promedio
const ticketPromedio = computed(() => {
  if (totalTicketsTurno.value === 0) return 0
  return cajaTurnoHoy.value / totalTicketsTurno.value
})

// #17 Meta del turno con barra de progreso
const metaDiaria = computed(() => {
  return Number(currentSedeData.value?.meta_diaria || 200.0)
})

const metaPct = computed(() => {
  if (metaDiaria.value <= 0) return 0
  return Math.round((cajaTurnoHoy.value / metaDiaria.value) * 100)
})

// #8 Últimos 10 registros ordenados desc
const ultimosDiezPagos = computed(() => {
  return [...pagosSede.value]
    .sort((a, b) => new Date(b.fecha_pago || b.fecha_creacion || 0) - new Date(a.fecha_pago || a.fecha_creacion || 0))
    .slice(0, 10)
})

// #3 y #11 Filtrado combinado de cajones
const slotsFiltradosPorGridYPlaca = computed(() => {
  let list = slotsCache.value

  // Filtro de estado
  if (filtroGrid.value !== 'todos') {
    list = list.filter(s => s.estado === filtroGrid.value)
  }

  // Filtro por búsqueda de placa
  if (busquedaPlaca.value.trim()) {
    const q = busquedaPlaca.value.toUpperCase().trim()
    list = list.filter(s => {
      const placa = getPlacaDeCajon(s.id)
      return placa && placa.toUpperCase().includes(q)
    })
  }

  return list
})

// Helpers de relación de datos
function getPlacaDeCajon(espacioId) {
  const r = reservasCache.value.find(res => res.espacio_id === espacioId && res.estado !== 'finalizada' && res.estado !== 'cancelada')
  return r ? r.placa_vehiculo : null
}

function getPlacaDeReserva(reservaId) {
  if (!reservaId) return null
  const r = reservasCache.value.find(res => res.id === reservaId)
  return r ? r.placa_vehiculo : null
}

function getTipoVehiculoDeReserva(reservaId) {
  if (!reservaId) return 'auto'
  const r = reservasCache.value.find(res => res.id === reservaId)
  if (!r) return 'auto'
  const slot = slotsCache.value.find(s => s.id === r.espacio_id)
  return (slot?.tipo_vehiculo || 'auto').toLowerCase()
}

function formatearHoraPago(fechaStr) {
  if (!fechaStr) return 'Hoy'
  try {
    return new Date(fechaStr).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return 'Hoy'
  }
}

function calcularTiempoEstadia(pago) {
  if (pago.tiempo_minutos) {
    const h = Math.floor(pago.tiempo_minutos / 60)
    const m = pago.tiempo_minutos % 60
    return h > 0 ? `${h}h ${m}m` : `${m}m`
  }
  return '1 hr (Est.)'
}

function getTarifaActual(tipoVehiculo = 'auto') {
  if (!currentSedeData.value) return 6.0
  const esDiurno = esHorarioDiurno.value
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

function getSlotIcon(slot) {
  const isMoto = (slot.tipo_vehiculo || 'auto').toLowerCase() === 'moto'
  if (slot.estado === 'libre') return 'fa-solid fa-check-circle'
  if (slot.estado === 'ocupado') return isMoto ? 'fa-solid fa-motorcycle' : 'fa-solid fa-car'
  return 'fa-solid fa-clock'
}

function getSlotNumero(espacioId) {
  const s = slotsCache.value.find(slot => slot.id === espacioId)
  return s ? `#${s.numero}` : `#${espacioId}`
}

function getReservaBadgeClass(estado) {
  if (estado === 'confirmada' || estado === 'pendiente') return 'reservado'
  if (estado === 'cancelada') return 'ocupado'
  return 'libre'
}

function getReservaStatusText(estado) {
  if (estado === 'pendiente') return 'EN PAGO (10m)'
  return (estado || 'ACTIVA').toUpperCase()
}

// Lifecycle
onMounted(async () => {
  themeStore.initTheme(true)
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  // Iniciar reloj HH:MM:SS
  relojInterval = setInterval(() => {
    horaActual.value = new Date().toLocaleTimeString('es-PE', { hour12: false })
  }, 1000)

  // Iniciar auto-refresh cada 30s con barra animada
  const stepMs = 200
  const totalMs = 30000
  progressBarTimer = setInterval(() => {
    refreshProgress.value = Math.min(100, refreshProgress.value + (stepMs / totalMs) * 100)
  }, stepMs)

  autoRefreshTimer = setInterval(async () => {
    refreshProgress.value = 0
    await refreshAll()
  }, totalMs)

  await refreshAll()
})

onUnmounted(() => {
  if (relojInterval) clearInterval(relojInterval)
  if (autoRefreshTimer) clearInterval(autoRefreshTimer)
  if (progressBarTimer) clearInterval(progressBarTimer)
})

function toggleTheme() {
  themeStore.toggleTheme()
}

// #4 Modal Cierre de Turno
function openModalConfirmCierre() {
  modalConfirmCierreVisible.value = true
}

function ejecutarCierreTurno() {
  modalConfirmCierreVisible.value = false
  authStore.logout()
  router.push('/login')
}

// #9 Modal Cierre de Caja
function openModalCierreCaja() {
  modalCierreCajaVisible.value = true
}

// Carga de datos
async function refreshAll() {
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

function handleSlotClick(slot) {
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
    modalIngresoVisible.value = true
  }
}

function openModalValidarQR() {
  qrResultado.value = null
  modalQRVisible.value = true
}

function openModalIngresoManual() {
  modalIngresoVisible.value = true
}

function openModalIncidencia() {
  modalIncidenciaVisible.value = true
}

function handleBuscarReservaInput(queryRaw) {
  const query = queryRaw.trim().toUpperCase()
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

async function onAutorizarIngresoDesdeQR({ reservaId, espacioId }) {
  modalQRVisible.value = false
  await darIngresoReserva(reservaId, espacioId)
}

async function darIngresoReserva(reservaId, espacioId) {
  try {
    await updateSlotState(espacioId, 'ocupado')
    await reservasService.actualizarEstadoReserva(reservaId, 'confirmada')
    showToast('¡Ingreso autorizado! Barrera abierta.', 'success')
    await refreshAll()
  } catch {
    showToast('Error al autorizar ingreso', 'error')
  }
}

function prepararSalidaDirecta(reservaId, espacioId, placa) {
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

async function updateSlotState(slotId, state) {
  await estacionamientosService.actualizarEstadoEspacio(slotId, state)
}

async function onConfirmarIngresoManual({ placa, tipoVehiculo, espacioId }) {
  if (!espacioId) {
    showToast('Seleccione un cajón libre', 'warning')
    return
  }
  const placaLimpia = (placa || '').trim().toUpperCase()
  if (!placaLimpia) {
    showToast('Ingrese la placa del vehículo', 'warning')
    return
  }

  try {
    cargando.value = true
    const response = await reservasService.walkin({
      espacio_id: espacioId,
      placa_vehiculo: placaLimpia,
      tipo_vehiculo: tipoVehiculo || 'auto',
      fecha_inicio: new Date().toISOString(),
      fecha_fin: new Date(Date.now() + 7200000).toISOString(),
      metodo_pago: 'efectivo'
    })

    modalIngresoVisible.value = false
    showToast(`✅ Ingreso registrado correctamente (${placaLimpia}). Barrera abierta.`, 'success')
    await refreshAll()
  } catch (error) {
    const msg = error.response?.data?.detail || 'Error al registrar ingreso'
    showToast(`❌ ${msg}`, 'error')
  } finally {
    cargando.value = false
  }
}

async function handleProcesarSalida() {
  const { espacioId, reservaId, monto } = salidaModalData.value
  try {
    cargando.value = true
    if (reservaId) {
      // Usar endpoint de cobro en caseta que calcula tiempo real, registra pago y libera cajón
      await reservasService.cobrarCaseta(reservaId, salidaMetodo.value)
    } else {
      // Si fue un slot ocupado manualmente sin reserva, liberar slot y registrar pago
      await updateSlotState(espacioId, 'libre')
      await pagosService.crearPago({
        reserva_id: 1,
        monto: monto,
        metodo_pago: salidaMetodo.value,
        estado: 'completado'
      })
    }

    modalSalidaVisible.value = false
    showToast(`✅ Salida procesada. Cobro registrado en caja y cajón liberado.`, 'success')
    await refreshAll()
  } catch (error) {
    const msg = error.response?.data?.detail || 'Error al procesar salida'
    showToast(`❌ ${msg}`, 'error')
  } finally {
    cargando.value = false
  }
}

async function handleLiberarReservaManual(reservaId) {
  if (!confirm('¿Desea liberar manualmente este cajón retenido/expirado?')) return
  try {
    cargando.value = true
    await reservasService.liberarManual(reservaId)
    showToast('✅ Reserva cancelada y cajón liberado exitosamente', 'success')
    await refreshAll()
  } catch (error) {
    const msg = error.response?.data?.detail || 'Error al liberar reserva'
    showToast(`❌ ${msg}`, 'error')
  } finally {
    cargando.value = false
  }
}

async function onReportarIncidenciaSubmit(desc) {
  try {
    await estacionamientosService.crearIncidencia({
      sede_id: authStore.user?.sede_id || 1,
      operador_id: authStore.userId,
      descripcion: desc
    })
    modalIncidenciaVisible.value = false
    showToast('¡Alerta enviada al propietario!', 'success')
  } catch {
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
  position: relative;
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

/* Sidebar */
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
  transition: transform 0.3s ease;
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

.nav-menu { list-style: none; display: flex; flex-direction: column; gap: 6px; flex: 1; padding: 0; margin: 0; }
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

.back-admin-link {
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.2) 0%, rgba(3, 105, 161, 0.2) 100%);
  color: var(--accent);
  border: 1px solid rgba(2, 132, 199, 0.4);
}

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

/* Main Content */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 36px 36px 36px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

/* #2 Barra de auto-refresh */
.auto-refresh-progress-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: transparent;
  z-index: 50;
}
.auto-refresh-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent) 0%, var(--primary) 100%);
  transition: width 0.2s linear;
}

/* Top Header */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.greeting-container {
  display: flex;
  align-items: center;
  gap: 14px;
}
.hamburger-btn {
  display: none;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 1.2rem;
  cursor: pointer;
}
.sede-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.greeting h1 { font-size: 1.75rem; font-weight: 800; margin: 0; }

/* #1 Reloj Digital Badge */
.live-clock-badge {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  font-family: monospace, monospace;
  color: var(--accent);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.sede-direccion-text { color: var(--text-muted); font-size: 0.9rem; margin-top: 4px; }
.tarifa-hora-badge { color: var(--accent); font-weight: 700; margin-left: 8px; }

.franja-horaria-pills {
  margin-top: 6px;
  display: flex;
  gap: 10px;
  font-size: 0.82rem;
  flex-wrap: wrap;
}
.tarifa-auto-pill { color: var(--accent); font-weight: 700; }
.tarifa-moto-pill { color: #f59e0b; font-weight: 700; }
.franja-status-pill {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
  color: var(--text-main);
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
.btn-theme-toggle {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 10px 16px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1.6fr;
  gap: 16px;
}
.stat-box { 
  background: rgba(15, 23, 42, 0.4); 
  border: 1px solid var(--glass-border); 
  border-radius: 16px; 
  padding: 16px 18px; 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
}
.stat-box.libre { border-bottom: 3px solid var(--color-libre); }
.stat-box.ocupado { border-bottom: 3px solid var(--color-ocupado); }
.stat-box.reservado { border-bottom: 3px solid var(--color-reservado); }
.stat-box.ingresos { border-bottom: 3px solid var(--accent); }

.stat-box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-label { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
.stat-value { font-size: 1.85rem; font-weight: 800; line-height: 1; }

.stat-progress-container {
  width: 100%;
  height: 5px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 4px;
}
.stat-progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}
.bar-green { background: #10b981; }
.bar-yellow { background: #f59e0b; }
.bar-red { background: #ef4444; }
.bg-reservado { background: var(--color-reservado); }

.stat-subtext {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* #5 y #6 Caja del turno expandida */
.caja-card-expanded {
  padding: 14px 18px;
}
.caja-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.caja-actions-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}
.badge-tickets-turno {
  background: rgba(56, 189, 248, 0.15);
  color: var(--accent);
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}
.btn-cerrar-caja {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  border: none;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.caja-divider {
  border-top: 1px solid var(--glass-border);
  margin: 8px 0;
}
.caja-breakdown-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 12px;
  font-size: 0.8rem;
}
.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.breakdown-label { color: var(--text-muted); font-size: 0.75rem; }
.breakdown-val { font-weight: 700; }
.breakdown-sub { font-size: 0.7rem; color: var(--text-muted); font-weight: normal; margin-left: 2px; }

/* #17 Meta del Turno */
.caja-meta-section {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.caja-meta-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--text-muted);
}
.ticket-promedio-lbl {
  color: var(--accent);
  font-weight: 600;
}
.caja-meta-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  overflow: hidden;
}
.caja-meta-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, var(--accent) 100%);
  border-radius: 4px;
  transition: width 0.4s ease;
}

/* Quick Actions Bar + Buscador de Placa */
.quick-actions-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}
.btn-quick {
  padding: 11px 16px;
  border-radius: 12px;
  font-size: 0.92rem;
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
.btn-quick.danger-light {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.btn-quick:hover { transform: translateY(-2px); }

/* #3 Buscador rápido de placa */
.quick-search-box {
  margin-left: auto;
  position: relative;
  display: flex;
  align-items: center;
  min-width: 240px;
}
.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  font-size: 0.85rem;
}
.search-placa-input {
  width: 100%;
  padding: 10px 32px 10px 34px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-main);
  outline: none;
  font-size: 0.9rem;
}
.search-placa-input:focus {
  border-color: var(--accent);
}
.search-clear-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.1rem;
  cursor: pointer;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.6fr 1.2fr;
  gap: 22px;
}

.card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 22px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}
.card-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e2e8f0;
}

.grid-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.hint-click-text {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* #11 Botonera de Filtros Grid */
.grid-filters-group {
  display: flex;
  gap: 6px;
  background: rgba(15, 23, 42, 0.5);
  padding: 4px;
  border-radius: 10px;
  border: 1px solid var(--glass-border);
}
.filter-pill-btn {
  padding: 5px 10px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-pill-btn:hover {
  color: var(--text-main);
}
.filter-pill-btn.active {
  background: var(--glass-bg);
  color: var(--accent);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* Slot Grid */
.slot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(115px, 1fr));
  gap: 14px;
}
.no-slots-msg {
  color: var(--text-muted);
  grid-column: 1 / -1;
  text-align: center;
  padding: 30px 10px;
}
.slot-card {
  background: rgba(15, 23, 42, 0.6);
  border: 2px solid var(--glass-border);
  border-radius: 16px;
  padding: 16px 10px;
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

.slot-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.slot-num { font-size: 1.35rem; font-weight: 800; color: #fff; }
.slot-type-badge {
  font-size: 0.68rem;
  font-weight: 700;
  background: rgba(255,255,255,0.08);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--text-muted);
}
.slot-type-icon { margin-right: 3px; }

.slot-placa-tag {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--accent);
  background: rgba(56, 189, 248, 0.12);
  padding: 2px 4px;
  border-radius: 4px;
  truncate: ellipsis;
}
.slot-status { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
.slot-card.libre .slot-status { color: var(--color-libre); }
.slot-card.ocupado .slot-status { color: var(--color-ocupado); }
.slot-card.reservado .slot-status { color: var(--color-reservado); }

/* Table Wrapper */
.table-wrapper { overflow-x: auto; width: 100%; }
.max-h-table { max-height: 420px; }
.max-h-table-historial { max-height: 320px; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th { padding: 12px 14px; font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--glass-border); }
td { padding: 12px 14px; font-size: 0.88rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: #e2e8f0; vertical-align: middle; }

/* Status Badges */
.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; }
.status-badge.libre { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.ocupado { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.status-badge.reservado { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.badge-retenido { color: #f59e0b; font-size: 0.75rem; font-weight: 700; }
.badge-vehiculo-table { font-weight: 600; font-size: 0.82rem; }

/* Historial Sección */
.historial-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 10px;
}
.historial-subtext {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 0;
}
.historial-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Modal Salida Card */
.modal-title-custom {
  font-size: 1.15rem;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-main);
  margin: 0;
}
.modal-close-x {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.3rem;
  cursor: pointer;
}
.salida-summary-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 14px;
}
.salida-summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}
.salida-summary-total-row {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--glass-border);
  padding-top: 8px;
  margin-top: 8px;
}
.monto-cobrar-lg { font-size: 1.3rem; color: #10b981; }
.btn-salida-confirm {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  margin-top: 8px;
}

/* Utilitarios de estilo (Reemplazo de inline styles) */
.mb-0 { margin-bottom: 0 !important; }
.mb-2 { margin-bottom: 2px !important; }
.capitalize { text-transform: capitalize; }
.text-center-muted { text-align: center; color: var(--text-muted); }
.text-muted-sm { color: var(--text-muted); font-size: 0.82rem; }
.text-color-libre { color: var(--color-libre); }
.text-color-ocupado { color: var(--color-ocupado); }
.text-color-reservado { color: var(--color-reservado); }
.text-accent { color: var(--accent); }
.text-success { color: #10b981; }
.text-warning { color: #f59e0b; }
.text-info { color: #06b6d4; }
.text-danger { color: #ef4444; }
.text-purple { color: #a855f7; }
.text-main-val { color: var(--text-main); }
.font-bold-md { font-size: 1rem; font-weight: 700; }
.monto-table-val { font-weight: 800; color: #10b981; font-size: 0.95rem; }
.action-flex-gap { display: flex; align-items: center; gap: 8px; }

.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.form-group label { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
.form-group select {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--text-main);
  font-size: 0.95rem;
  outline: none;
}
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

/* Light Mode Overrides */
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
.operador-root.light-mode .form-group select {
  background: #fff; 
  color: #0f172a; 
  border-color: #cbd5e1;
}
.operador-root.light-mode .search-placa-input {
  background: #ffffff;
  border-color: #cbd5e1;
  color: #0f172a;
}
.operador-root.light-mode .grid-filters-group {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

/* Responsividad y Móvil (#13) */
@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 900px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .hamburger-btn { display: inline-flex; align-items: center; justify-content: center; }
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    transform: translateX(-100%);
    box-shadow: 0 0 40px rgba(0,0,0,0.6);
  }
  .sidebar.sidebar-open {
    transform: translateX(0);
  }
  .sidebar-mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    z-index: 95;
  }
  .main-content {
    padding: 16px;
  }
  .quick-search-box {
    margin-left: 0;
    width: 100%;
  }
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
