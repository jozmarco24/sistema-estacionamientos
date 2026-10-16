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
                  {{ esDiurno ? '☀️ Franja Diurna Activa' : '🌙 Franja Nocturna Activa' }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <span class="auto-refresh-tag">
            <i class="fa-solid fa-arrows-rotate" :class="{ 'fa-spin': cargando }"></i> ↻ Auto cada 30s
          </span>
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
          <span v-if="busquedaPlaca.trim()" class="search-count-badge">
            ({{ slotsFiltradosPorGridYPlaca.length }} resultados)
          </span>
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

      <!-- ═══════════════════════════════════ -->
      <!-- TABS NAVEGACIÓN                     -->
      <!-- ═══════════════════════════════════ -->
      <div class="tabs-container">

        <!-- Headers de Tabs -->
        <div class="tabs-header">
          <button class="tab-btn" :class="{ active: activeTab === 'dashboard' }"
            @click="activeTab = 'dashboard'">
            <i class="fa-solid fa-gauge-high"></i> Dashboard
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'cajones' }"
            @click="activeTab = 'cajones'">
            <i class="fa-solid fa-table-cells"></i> Cajones
            <span v-if="tabBadgeCajones > 0" class="tab-badge ocupado">{{ tabBadgeCajones }}</span>
            <span v-else class="tab-badge libre">{{ cajones.length }}</span>
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'historial' }"
            @click="activeTab = 'historial'">
            <i class="fa-solid fa-clock-rotate-left"></i> Historial
            <span v-if="tabBadgeHistorial > 0" class="tab-badge pagado">{{ tabBadgeHistorial }}</span>
          </button>
        </div>

        <!-- ─── TAB 1: DASHBOARD ─── -->
        <div v-show="activeTab === 'dashboard'" class="tab-content">
          <div class="dashboard-tab-grid">

            <!-- Caja del Turno -->
            <div class="card">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <h2 class="card-title" style="margin-bottom:0;">
                  <i class="fa-solid fa-cash-register"></i> Caja del Turno (Hoy)
                </h2>
                <div style="display:flex;gap:8px;align-items:center;">
                  <span class="badge-tickets">{{ tabBadgeHistorial }} tickets</span>
                  <button @click="cerrarCaja" class="btn-cerrar-caja">
                    <i class="fa-solid fa-print"></i> Cerrar Caja
                  </button>
                </div>
              </div>
              <div class="caja-monto-grande">S/. {{ cajaTurnoHoy.toFixed(2) }}</div>
              <div class="caja-desglose-grid">
                <div class="desglose-item">
                  <span>💵 Efectivo</span>
                  <strong>S/. {{ cajaEfectivo?.toFixed(2) || '0.00' }}</strong>
                </div>
                <div class="desglose-item">
                  <span>💳 Online</span>
                  <strong>S/. {{ cajaOnline?.toFixed(2) || '0.00' }}</strong>
                </div>
                <div class="desglose-item">
                  <span>🚗 Autos</span>
                  <strong>S/. {{ cajaAutos?.toFixed(2) || '0.00' }}</strong>
                </div>
                <div class="desglose-item">
                  <span>🏍️ Motos</span>
                  <strong>S/. {{ cajaMotos?.toFixed(2) || '0.00' }}</strong>
                </div>
              </div>
              <!-- Barra de progreso meta -->
              <div style="margin-top:14px;">
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:var(--text-muted);margin-bottom:4px;">
                  <span>Meta: S/. {{ cajaTurnoHoy.toFixed(2) }} / S/. {{ metaTurno.toFixed(2) }}</span>
                  <span style="color:var(--accent);font-weight:700;">{{ metaPorcentaje }}%</span>
                </div>
                <div style="background:rgba(255,255,255,0.08);border-radius:8px;height:6px;overflow:hidden;">
                  <div :style="`width:${metaPorcentaje}%;background:var(--accent);height:100%;border-radius:8px;transition:width 0.5s;`"></div>
                </div>
              </div>
              <!-- Promedio -->
              <div style="margin-top:10px;font-size:0.82rem;color:var(--text-muted);">
                Promedio por cobro:
                <strong style="color:var(--accent);">
                  S/. {{ tabBadgeHistorial > 0 ? (cajaTurnoHoy / tabBadgeHistorial).toFixed(2) : '0.00' }}
                </strong>
              </div>
            </div>

            <!-- Estado General + Últimos cobros -->
            <div class="card">
              <h2 class="card-title"><i class="fa-solid fa-chart-pie"></i> Estado General</h2>
              <div class="estado-general-grid">
                <div class="estado-item libre">
                  <span class="estado-num" style="color:var(--color-libre);">{{ statsLibres }}</span>
                  <span class="estado-lbl">Libres</span>
                </div>
                <div class="estado-item ocupado">
                  <span class="estado-num" style="color:var(--color-ocupado);">{{ statsOcupados }}</span>
                  <span class="estado-lbl">Ocupados</span>
                </div>
                <div class="estado-item reservado">
                  <span class="estado-num" style="color:var(--color-reservado);">{{ statsReservados }}</span>
                  <span class="estado-lbl">Reservados</span>
                </div>
                <div class="estado-item">
                  <span class="estado-num" style="color:#a78bfa;">{{ cajones.length }}</span>
                  <span class="estado-lbl">Total</span>
                </div>
              </div>
              <!-- Últimos cobros -->
              <div style="margin-top:16px;">
                <div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:8px;font-weight:600;">
                  Últimos cobros:
                </div>
                <div v-for="h in historialLimpio.filter(x => (x.estado || '').toLowerCase() === 'pagado' || (x.estado || '').toLowerCase() === 'completado').slice(0,3)"
                     :key="h.reserva_id || h.placa"
                     style="display:flex;justify-content:space-between;font-size:0.83rem;padding:6px 0;border-bottom:1px solid var(--glass-border);">
                  <span style="color:var(--accent);font-weight:700;">{{ h.placa || getPlacaDeReserva(h.reserva_id) || 'N/A' }}</span>
                  <span style="color:var(--text-muted);">{{ formatearHoraPago(h.fecha_pago || h.fecha_creacion) }}</span>
                  <span style="color:#6ee7b7;font-weight:700;">S/. {{ Number(h.monto||0).toFixed(2) }}</span>
                </div>
                <p v-if="historialLimpio.filter(x => (x.estado || '').toLowerCase() === 'pagado' || (x.estado || '').toLowerCase() === 'completado').length === 0"
                   style="color:var(--text-muted);font-size:0.82rem;text-align:center;padding:16px 0;">
                  Sin cobros aún en este turno.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── TAB 2: CAJONES ─── -->
        <div v-show="activeTab === 'cajones'" class="tab-content">
          <div class="cajones-tab-layout">

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

                  <!-- MEJORA 2: Timer en tiempo real para cajones ocupados -->
                  <span
                    v-if="slot.estado === 'ocupado' && getIngresoDeCajon(slot.id)"
                    class="timer-badge"
                    :key="timerTick"
                  >
                    ⏱ {{ calcularTiempoTranscurrido(getIngresoDeCajon(slot.id)) }}
                  </span>

                  <div class="slot-status">
                    <i :class="getSlotIcon(slot)"></i> {{ slot.estado }}
                  </div>

                  <!-- MEJORA 3: Botón Cobrar rápido directo en cajón ocupado -->
                  <button
                    v-if="slot.estado === 'ocupado' && getReservaIdDeCajon(slot.id)"
                    class="btn-cobrar-rapido"
                    @click.stop="cobrarCasetaRapido(getReservaIdDeCajon(slot.id), getPlacaDeCajon(slot.id))"
                    title="Cobrar y liberar este cajón"
                  >
                    <i class="fa-solid fa-cash-register"></i> Cobrar
                  </button>
                </div>
              </div>
            </div>

            <!-- Tabla Vehículos SOLO activos -->
            <div class="card">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <h2 class="card-title" style="margin-bottom:0;">
                  <i class="fa-solid fa-car-on"></i> Vehículos en Caseta
                </h2>
                <span class="badge-tickets" style="background:rgba(16,185,129,0.2);color:#6ee7b7;border-color:rgba(16,185,129,0.4);">
                  {{ vehiculosActivos.length }} activos
                </span>
              </div>

              <div v-if="vehiculosActivos.length === 0"
                   style="text-align:center;padding:40px 20px;color:var(--text-muted);">
                <i class="fa-solid fa-parking" style="font-size:2.5rem;opacity:0.2;display:block;margin-bottom:10px;"></i>
                Sin vehículos activos en caseta
              </div>
              <div v-else class="table-wrapper max-h-table">
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
                    <tr v-for="v in vehiculosActivos" :key="v.id">
                      <td>
                        <strong class="text-accent"><i class="fa-solid fa-car-side"></i> {{ v.placa_vehiculo || v.placa || 'N/A' }}</strong>
                      </td>
                      <td><strong>{{ getSlotNumero(v.espacio_id) }}</strong></td>
                      <td>
                        <span :class="['status-badge', getReservaBadgeClass(v.estado)]">
                          {{ getReservaStatusText(v.estado) }}
                        </span>
                      </td>
                      <td>
                        <button
                          v-if="v.estado === 'confirmada'"
                          @click="darIngresoReserva(v.id, v.espacio_id)"
                          class="btn-action text-success"
                        >
                          <i class="fa-solid fa-arrow-right-to-bracket"></i> Ingreso
                        </button>
                        <div v-else-if="v.estado === 'pendiente'" class="action-flex-gap">
                          <span class="badge-retenido">
                            <i class="fa-solid fa-lock"></i> Retenido
                          </span>
                          <button
                            @click="handleLiberarReservaManual(v.id)"
                            class="btn-action text-danger"
                            title="Liberar cajón manualmente"
                          >
                            <i class="fa-solid fa-unlock"></i> Liberar
                          </button>
                        </div>
                        <button
                          v-else-if="v.estado !== 'finalizada' && v.estado !== 'completada' && v.estado !== 'cancelada'"
                          @click="prepararSalidaDirecta(v.id, v.espacio_id, v.placa_vehiculo)"
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
        </div>

        <!-- ─── TAB 3: HISTORIAL ─── -->
        <div v-show="activeTab === 'historial'" class="tab-content">
          <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
              <h2 class="card-title" style="margin-bottom:0;">
                <i class="fa-solid fa-clock-rotate-left"></i> Historial del Turno (Hoy)
              </h2>
              <div style="display:flex;gap:8px;align-items:center;">
                <span class="badge-tickets">{{ historialLimpio.length }} cobros</span>
                <select v-model="historialFiltroEstado"
                  style="background:var(--glass-bg);border:1px solid var(--glass-border);color:var(--text-main);padding:6px 10px;border-radius:8px;font-size:0.82rem;cursor:pointer;">
                  <option value="todos">Todos</option>
                  <option value="pagado">Pagados</option>
                  <option value="pendiente">Pendientes</option>
                </select>
              </div>
            </div>

            <div class="table-wrapper max-h-table-historial">
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
                  <tr v-if="historialPaginado.length === 0">
                    <td colspan="7" class="text-center-muted">Sin cobros registrados para el filtro seleccionado.</td>
                  </tr>
                  <tr v-for="h in historialPaginado" :key="h.id">
                    <td class="text-muted-sm">
                      {{ formatearHoraPago(h.fecha_pago || h.fecha_creacion) }}
                    </td>
                    <td>
                      <strong class="text-accent">{{ h.placa || getPlacaDeReserva(h.reserva_id) || 'N/D' }}</strong>
                    </td>
                    <td>
                      <span class="badge-vehiculo-table">
                        <i :class="(h.tipo_vehiculo || getTipoVehiculoDeReserva(h.reserva_id) || 'auto').toLowerCase() === 'moto' ? 'fa-solid fa-motorcycle text-warning' : 'fa-solid fa-car text-accent'"></i>
                        {{ ((h.tipo_vehiculo || getTipoVehiculoDeReserva(h.reserva_id) || 'auto').toLowerCase() === 'moto') ? 'Moto' : 'Auto' }}
                      </span>
                    </td>
                    <td class="text-muted-sm">
                      {{ calcularTiempoEstadia(h) }}
                    </td>
                    <td class="monto-table-val">S/. {{ Number(h.monto).toFixed(2) }}</td>
                    <td>
                      <span v-if="h.metodo_pago === 'efectivo'"><i class="fa-solid fa-money-bill-wave text-success"></i> Efectivo</span>
                      <span v-else-if="h.metodo_pago === 'yape'"><i class="fa-solid fa-mobile-screen-button text-purple"></i> Yape/Plin</span>
                      <span v-else-if="h.metodo_pago === 'tarjeta'"><i class="fa-solid fa-credit-card text-accent"></i> Tarjeta POS</span>
                      <span v-else><i class="fa-solid fa-globe text-accent"></i> Online / App</span>
                    </td>
                    <td>
                      <span :class="['status-badge', ((h.estado || '').toLowerCase() === 'pagado' || (h.estado || '').toLowerCase() === 'completado') ? 'libre' : ((h.estado || '').toLowerCase() === 'pendiente' ? 'reservado' : 'ocupado')]" class="capitalize">
                        {{ h.estado }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Paginación -->
            <div v-if="historialTotalPaginas > 1"
                 style="display:flex;justify-content:center;align-items:center;gap:12px;margin-top:16px;">
              <button @click="historialPagina--" :disabled="historialPagina===1" class="btn-page">
                ‹ Anterior
              </button>
              <span style="font-size:0.85rem;color:var(--text-muted);">
                Página {{ historialPagina }} de {{ historialTotalPaginas }}
              </span>
              <button @click="historialPagina++" :disabled="historialPagina===historialTotalPaginas" class="btn-page">
                Siguiente ›
              </button>
            </div>
          </div>
        </div>

      </div>
      <!-- FIN TABS -->
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
const searchPlaca = busquedaPlaca // Alias para compatibilidad

// MEJORA 2: Timer en tiempo real para cajones ocupados
const timerTick = ref(0)
let timerInterval = null

// MEJORA 7: Paginación del historial (10 por página)
const historialPagina = ref(1)
const historialPorPagina = 10

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

// ── Control de Tabs (NUEVO) ──
const activeTab = ref('dashboard')
const historialFiltroEstado = ref('todos')

// Aliases reactivos para compatibilidad con prompt
const cajones = slotsCache
const vehiculosEnCaseta = reservasCache
const historialTurno = pagosSede

// ── Computed NUEVOS (no reemplazan nada existente) ──

// Badge para tab cajones
const tabBadgeCajones = computed(() =>
  cajones.value.filter(c => c.estado === 'ocupado').length
)

// Badge para tab historial
const tabBadgeHistorial = computed(() =>
  historialTurno.value.filter(h => (h.estado || '').toLowerCase() === 'pagado' || (h.estado || '').toLowerCase() === 'completado').length
)

// Vehículos en caseta SOLO activos (para limpiar tabla visualmente)
const vehiculosActivos = computed(() =>
  vehiculosEnCaseta.value.filter(v =>
    ['en_curso', 'confirmada', 'activa'].includes(
      (v.estado || v.estado_reserva || '').toLowerCase()
    )
  )
)

// Historial sin duplicados por reserva_id
const historialLimpio = computed(() => {
  const seen = new Set()
  return historialTurno.value.filter(h => {
    const key = h.reserva_id || `${h.placa || getPlacaDeReserva(h.reserva_id)}-${h.fecha_pago || h.fecha_creacion}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
})

// Historial filtrado por estado
const historialFiltrado = computed(() => {
  if (historialFiltroEstado.value === 'todos') return historialLimpio.value
  return historialLimpio.value.filter(h => {
    const st = (h.estado || '').toLowerCase()
    if (historialFiltroEstado.value === 'pagado') {
      return st === 'pagado' || st === 'completado'
    }
    return st === historialFiltroEstado.value.toLowerCase()
  })
})

// Meta turno para barra de progreso
const metaTurno = computed(() =>
  Number(currentSedeData.value?.meta_turno || currentSedeData.value?.meta_diaria || 200)
)
const metaPorcentaje = computed(() =>
  Math.min(Math.round((cajaTurnoHoy.value / metaTurno.value) * 100), 100)
)

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

// 4.1 Computed esDiurno
const esDiurno = computed(() => {
  const hora = new Date().getHours()
  const inicioDia = currentSedeData.value?.hora_inicio_dia ?? 8
  const inicioNoche = currentSedeData.value?.hora_inicio_noche ?? 20
  return hora >= inicioDia && hora < inicioNoche
})
const esHorarioDiurno = esDiurno

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

// MEJORA 7: Historial Paginado (10 por página) con soporte de filtro de estado
const historialPaginado = computed(() => {
  const inicio = (historialPagina.value - 1) * historialPorPagina
  return historialFiltrado.value.slice(inicio, inicio + historialPorPagina)
})

const historialTotalPaginas = computed(() => {
  return Math.max(1, Math.ceil(historialFiltrado.value.length / historialPorPagina))
})

// #8 Últimos 10 registros ordenados desc (alias de compatibilidad)
const ultimosDiezPagos = computed(() => historialPaginado.value)

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
      const numero = String(s.numero || '')
      return (placa && placa.toUpperCase().includes(q)) || numero.toUpperCase().includes(q)
    })
  }

  return list
})

// MEJORA 1: Computed para filtrar la tabla de movimientos/vehículos en caseta
const vehiculosFiltered = computed(() => {
  if (!busquedaPlaca.value.trim()) return reservasCache.value
  const q = busquedaPlaca.value.trim().toUpperCase()
  return reservasCache.value.filter(v => {
    const placa = (v.placa_vehiculo || v.placa || '').toUpperCase()
    const numCajon = getSlotNumero(v.espacio_id).toUpperCase()
    return placa.includes(q) || numCajon.includes(q)
  })
})

const cajonesFiltered = slotsFiltradosPorGridYPlaca

// Helpers de relación de datos
function getPlacaDeCajon(espacioId) {
  const r = reservasCache.value.find(res => res.espacio_id === espacioId && res.estado !== 'finalizada' && res.estado !== 'completada' && res.estado !== 'cancelada')
  return r ? r.placa_vehiculo : null
}

function getIngresoDeCajon(espacioId) {
  const r = reservasCache.value.find(res => res.espacio_id === espacioId && res.estado !== 'finalizada' && res.estado !== 'completada' && res.estado !== 'cancelada')
  return r ? (r.fecha_inicio || r.fecha_creacion || null) : null
}

function getReservaIdDeCajon(espacioId) {
  const r = reservasCache.value.find(res => res.espacio_id === espacioId && res.estado !== 'finalizada' && res.estado !== 'completada' && res.estado !== 'cancelada')
  return r ? r.id : null
}

// MEJORA 2: Función helper para calcular tiempo transcurrido
function calcularTiempoTranscurrido(fechaIngreso) {
  if (!fechaIngreso) return null
  const ahora = new Date()
  const ingreso = new Date(fechaIngreso)
  const diffMs = ahora - ingreso
  if (isNaN(diffMs) || diffMs < 0) return '0m'
  const horas = Math.floor(diffMs / 3600000)
  const minutos = Math.floor((diffMs % 3600000) / 60000)
  if (horas > 0) return `${horas}h ${minutos}m`
  return `${minutos}m`
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

  // Iniciar timer cada 1 minuto para badges de tiempo transcurrido
  timerInterval = setInterval(() => {
    timerTick.value++
  }, 60000)

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
  if (timerInterval) clearInterval(timerInterval)
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

// MEJORA 6: Sonido de beep usando Web Audio API
function playBeepIngreso() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) return
    const ctx = new AudioCtx()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.frequency.value = 880
    osc.type = 'sine'
    gain.gain.setValueAtTime(0.3, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4)
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + 0.4)
  } catch (e) {
    /* silencioso si el navegador bloquea audio */
  }
}

// MEJORA 3: Cobrar rápido directo en cajón ocupado
async function cobrarCasetaRapido(reservaId, placa) {
  if (!confirm(`¿Cobrar y liberar el vehículo ${placa || ''}?`)) return
  try {
    cargando.value = true
    await reservasService.cobrarCaseta(reservaId, 'efectivo')
    showToast(`✅ Cobro registrado para ${placa || 'vehículo'}`)
    await refreshAll()
  } catch (e) {
    showToast(`❌ Error al cobrar: ${e.response?.data?.detail || e.message}`, 'error')
  } finally {
    cargando.value = false
  }
}

// MEJORA 4: Cerrar Caja -> Resumen Imprimible (PDF)
async function cerrarCaja() {
  if (!confirm('¿Cerrar la caja del turno actual y generar el resumen?')) return

  const ahora = new Date().toLocaleString('es-PE')
  const totalEfectivo = transaccionesValidasTurno.value
    .filter(h => (h.metodo_pago || '').toLowerCase() === 'efectivo')
    .reduce((s, h) => s + Number(h.monto || 0), 0)
  const totalOnline = transaccionesValidasTurno.value
    .filter(h => (h.metodo_pago || '').toLowerCase() !== 'efectivo')
    .reduce((s, h) => s + Number(h.monto || 0), 0)
  const totalTickets = transaccionesValidasTurno.value.length

  const filas = pagosSede.value.map(h => `
    <tr>
      <td>${formatearHoraPago(h.fecha_pago || h.fecha_creacion)}</td>
      <td><b>${h.placa || getPlacaDeReserva(h.reserva_id) || 'N/A'}</b></td>
      <td>${((h.tipo_vehiculo || getTipoVehiculoDeReserva(h.reserva_id) || 'auto').toLowerCase() === 'moto') ? 'Moto' : 'Auto'}</td>
      <td>${calcularTiempoEstadia(h)}</td>
      <td>S/. ${Number(h.monto || 0).toFixed(2)}</td>
      <td>${h.metodo_pago || 'efectivo'}</td>
      <td>${h.estado || 'completado'}</td>
    </tr>
  `).join('')

  const htmlResumen = `
    <!DOCTYPE html><html><head>
    <meta charset="UTF-8">
    <title>Cierre de Caja — ${currentSedeData.value?.nombre || 'SmartPark'}</title>
    <style>
      body { font-family: Arial, sans-serif; padding: 24px; color: #111; }
      h1 { font-size: 1.4rem; margin-bottom: 4px; }
      .sub { color: #555; font-size: 0.9rem; margin-bottom: 20px; }
      .resumen { display: flex; gap: 24px; margin-bottom: 20px; }
      .kpi { background: #f3f4f6; border-radius: 8px; padding: 12px 20px; text-align: center; }
      .kpi .val { font-size: 1.5rem; font-weight: 800; color: #0284c7; }
      .kpi .lbl { font-size: 0.8rem; color: #555; }
      table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
      th { background: #0284c7; color: white; padding: 8px; text-align: left; }
      td { padding: 7px 8px; border-bottom: 1px solid #e5e7eb; }
      tr:nth-child(even) td { background: #f9fafb; }
      .footer { margin-top: 20px; font-size: 0.8rem; color: #888; text-align: center; }
    </style>
    </head><body>
    <h1>🅿️ Cierre de Caja — ${currentSedeData.value?.nombre || 'SmartPark'}</h1>
    <div class="sub">Generado: ${ahora} | Operador: ${authStore.user?.nombre || authStore.user?.email || 'N/A'}</div>
    <div class="resumen">
      <div class="kpi"><div class="val">S/. ${cajaTurnoHoy.value.toFixed(2)}</div><div class="lbl">Total Recaudado</div></div>
      <div class="kpi"><div class="val">S/. ${totalEfectivo.toFixed(2)}</div><div class="lbl">Efectivo</div></div>
      <div class="kpi"><div class="val">S/. ${totalOnline.toFixed(2)}</div><div class="lbl">Online</div></div>
      <div class="kpi"><div class="val">${totalTickets}</div><div class="lbl">Tickets Pagados</div></div>
    </div>
    <table>
      <thead><tr><th>Hora</th><th>Placa</th><th>Vehículo</th><th>Tiempo</th><th>Monto</th><th>Pago</th><th>Estado</th></tr></thead>
      <tbody>${filas}</tbody>
    </table>
    <div class="footer">SmartPark Sistema de Estacionamientos — Reporte de Turno</div>
    </body></html>
  `

  const ventana = window.open('', '_blank', 'width=900,height=700')
  if (ventana) {
    ventana.document.write(htmlResumen)
    ventana.document.close()
    ventana.focus()
    setTimeout(() => ventana.print(), 500)
  }
}

// #9 Modal Cierre de Caja
function openModalCierreCaja() {
  modalCierreCajaVisible.value = true
}

// Carga de datos
async function refreshAll() {
  cargando.value = true
  historialPagina.value = 1
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
    const res = reservasCache.value.find(r => r.espacio_id === slot.id && r.estado !== 'finalizada' && r.estado !== 'completada' && r.estado !== 'cancelada')
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
    playBeepIngreso()
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
    playBeepIngreso()
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
  grid-template-columns: repeat(3, 1fr);
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

/* MEJORA 1, 2, 3, 5, 7: Nuevos Estilos de Funcionalidad y UX */
.auto-refresh-tag {
  font-size: 0.75rem;
  color: var(--text-muted);
  opacity: 0.85;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
}

.search-count-badge {
  position: absolute;
  right: 32px;
  font-size: 0.75rem;
  color: var(--accent);
  font-weight: 700;
  pointer-events: none;
}

.timer-badge {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  color: #fbbf24;
  background: rgba(251,191,36,0.15);
  border: 1px solid rgba(251,191,36,0.3);
  border-radius: 6px;
  padding: 2px 7px;
  margin-top: 4px;
}

.btn-cobrar-rapido {
  width: 100%;
  margin-top: 8px;
  padding: 6px 10px;
  background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(5,150,105,0.25));
  border: 1px solid rgba(16,185,129,0.5);
  border-radius: 8px;
  color: #6ee7b7;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-cobrar-rapido:hover {
  background: linear-gradient(135deg, rgba(16,185,129,0.4), rgba(5,150,105,0.4));
  transform: translateY(-1px);
}

.historial-pagination-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 14px;
  padding: 10px 0;
}

.page-indicator-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 600;
}

.btn-page {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-page:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.btn-page:not(:disabled):hover {
  background: rgba(2,132,199,0.2);
  border-color: var(--accent);
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

/* ══════════════════════════════════
   SISTEMA DE TABS
══════════════════════════════════ */
.tabs-container { margin-top: 16px; }

.tabs-header {
  display: flex;
  gap: 4px;
  background: rgba(255,255,255,0.04);
  border-radius: 14px 14px 0 0;
  padding: 6px;
  border: 1px solid var(--glass-border);
  border-bottom: none;
}
.tab-btn {
  flex: 1;
  padding: 11px 16px;
  background: transparent;
  border: none;
  border-radius: 10px;
  color: var(--text-muted);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}
.tab-btn:hover {
  background: rgba(255,255,255,0.06);
  color: var(--text-main);
}
.tab-btn.active {
  background: linear-gradient(135deg, rgba(2,132,199,0.25), rgba(3,105,161,0.25));
  color: var(--accent);
  border: 1px solid rgba(2,132,199,0.4);
}
.tab-badge {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}
.tab-badge.ocupado { background: rgba(239,68,68,0.2);   color: #fca5a5; }
.tab-badge.libre   { background: rgba(16,185,129,0.2);  color: #6ee7b7; }
.tab-badge.pagado  { background: rgba(2,132,199,0.2);   color: #7dd3fc; }

.tab-content {
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: 0 0 14px 14px;
  padding: 16px;
  min-height: 420px;
}

/* ── Tab 1: Dashboard ── */
.dashboard-tab-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 900px) {
  .dashboard-tab-grid { grid-template-columns: 1fr; }
}
.caja-monto-grande {
  font-size: 2.8rem;
  font-weight: 900;
  color: var(--accent);
  margin: 8px 0 12px;
}
.caja-desglose-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.desglose-item {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  font-size: 0.83rem;
}
.estado-general-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 8px;
}
.estado-item {
  background: rgba(255,255,255,0.04);
  border-radius: 10px;
  padding: 14px;
  text-align: center;
  border: 1px solid var(--glass-border);
}
.estado-item.libre    { border-color: rgba(16,185,129,0.3); }
.estado-item.ocupado  { border-color: rgba(239,68,68,0.3); }
.estado-item.reservado{ border-color: rgba(245,158,11,0.3); }
.estado-num { display: block; font-size: 2rem; font-weight: 800; }
.estado-lbl { font-size: 0.75rem; color: var(--text-muted); }

/* ── Tab 2: Cajones ── */
.cajones-tab-layout {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 16px;
}
@media (max-width: 1000px) {
  .cajones-tab-layout { grid-template-columns: 1fr; }
}

/* ── Tab 3: Historial ── */
.badge-tickets {
  background: rgba(2,132,199,0.15);
  border: 1px solid rgba(2,132,199,0.3);
  color: #7dd3fc;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}
</style>
