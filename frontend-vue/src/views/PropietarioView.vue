<template>
  <div class="propietario-app-root" :class="{ 'light-mode': themeStore.isLight }">
    <!-- Sidebar Propietario -->
    <aside class="sidebar" id="sidebar">
      <div class="logo-area">
        <i class="fa-solid fa-parking"></i> SmartPark Dueño
      </div>
      <ul class="nav-menu">
        <router-link
          v-if="authStore.user?.rol === 'admin'"
          to="/admin"
          class="nav-item back-admin-btn"
        >
          <i class="fa-solid fa-arrow-left"></i> Volver a Admin
        </router-link>

        <div class="nav-divider">Centro de Negocio</div>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-resumen' }"
          @click.prevent="switchSection('sec-resumen')"
        >
          <i class="fa-solid fa-chart-pie"></i> Resumen Operativo
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-finanzas' }"
          @click.prevent="switchSection('sec-finanzas')"
        >
          <i class="fa-solid fa-wallet"></i> Finanzas & Cobros
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-cobros' }"
          @click.prevent="switchSection('sec-cobros')"
        >
          <i class="fa-solid fa-credit-card"></i> Configurar Cobros
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-sedes' }"
          @click.prevent="switchSection('sec-sedes')"
        >
          <i class="fa-solid fa-warehouse"></i> Mis Sedes
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-slots' }"
          @click.prevent="switchSection('sec-slots')"
        >
          <i class="fa-solid fa-square-parking"></i> Espacios (Slots)
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-personal' }"
          @click.prevent="switchSection('sec-personal')"
        >
          <i class="fa-solid fa-users-gear"></i> Mi Personal
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-suscripcion' }"
          @click.prevent="switchSection('sec-suscripcion')"
        >
          <i class="fa-solid fa-gem"></i> Mi Suscripción
        </a>

        <a href="#" class="nav-item logout-btn" @click.prevent="logout">
          <i class="fa-solid fa-right-from-bracket"></i> Cerrar Sesión
        </a>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Toast Alert -->
      <div
        v-if="toast.show"
        class="alert-toast"
        :style="{ background: toast.isError ? 'rgba(239, 68, 68, 0.95)' : 'rgba(16, 185, 129, 0.95)' }"
      >
        {{ toast.msg }}
      </div>

      <!-- Header -->
      <div class="top-header">
        <div class="greeting">
          <h1>{{ sectionTitles[currentSection]?.title || 'Resumen Operativo' }}</h1>
          <p>{{ sectionTitles[currentSection]?.sub || 'Métricas en tiempo real, mapa de sedes y monitoreo de incidencias.' }}</p>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
          <!-- Widget Reloj Digital y Fecha en Vivo -->
          <div class="live-clock-widget">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="pulse-dot"></span>
              <div style="text-align: right;">
                <div class="clock-time">{{ liveTime }}</div>
                <div class="clock-date">{{ liveDate }}</div>
              </div>
            </div>
          </div>

          <button @click="refreshAll" class="btn-action" title="Recargar datos">
            <i class="fa-solid fa-rotate" :class="{ 'fa-spin': isRefreshing }"></i> Actualizar
          </button>
          <button @click="themeStore.toggleTheme" class="theme-toggle-btn">
            <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
            <span>{{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}</span>
          </button>
        </div>
      </div>

      <!-- ================= SECCIÓN 1: RESUMEN OPERATIVO ================= -->
      <section v-show="currentSection === 'sec-resumen'" class="section-view active-section">
        <!-- Barra de Ocupación Global -->
        <div class="card ocupacion-banner">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <div style="display:flex; align-items:center; gap:10px;">
              <i class="fa-solid fa-gauge-high" style="color:var(--accent); font-size:1.2rem;"></i>
              <div>
                <strong style="font-size:0.95rem;">Nivel de Ocupación General (Todas las Sedes)</strong>
                <div style="font-size:0.75rem; color:var(--text-muted);">Capacidad física utilizada en tiempo real</div>
              </div>
            </div>
            <span style="font-size:1.3rem; font-weight:800; color:var(--text-main);">{{ ocupacionPct }}%</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ width: ocupacionPct + '%' }"></div>
          </div>
        </div>

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
          <div class="stat-box ingresos">
            <span class="stat-label">Total Espacios (Capacidad)</span>
            <span class="stat-value" style="color: var(--primary);">{{ totalEspacios }}</span>
          </div>
        </div>

        <!-- Fila 1: Cobertura en Mapa y Buzón de Incidencias -->
        <div class="two-cols" style="margin-bottom: 24px;">
          <!-- Cobertura en Mapa -->
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-earth-americas"></i> Cobertura de tus Sucursales</h2>
              <div style="display: flex; gap: 8px; align-items: center;">
                <span class="status-badge libre">{{ misSedes.length }} sedes</span>
                <button @click="recenterOwnerMap" class="btn-action" title="Centrar en todas mis sedes">
                  <i class="fa-solid fa-crosshairs"></i> Centrar
                </button>
              </div>
            </div>
            <div id="owner-map"></div>
          </div>

          <!-- Incidencias Reportadas -->
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <div>
                <h2 class="card-title" style="margin-bottom:2px; color: #f87171;"><i class="fa-solid fa-triangle-exclamation"></i> Buzón de Incidencias</h2>
                <p style="font-size:0.8rem; color:var(--text-muted); margin:0;">Alertas operativas reportadas por tus operadores.</p>
              </div>
              <span class="status-badge ocupado">{{ incidenciasList.length }} incidencias</span>
            </div>
            <div style="max-height: 280px; overflow-y: auto;">
              <div v-for="inc in incidenciasList" :key="inc.id" class="incidencia-row">
                <div>
                  <div style="font-weight: 600; font-size:0.9rem;">Sede: {{ getSedeNombre(inc.sede_id) }}</div>
                  <div style="font-size: 0.85rem; margin-top: 3px; color:#fca5a5;">{{ inc.descripcion }}</div>
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8;">{{ formatearFecha(inc.fecha_reporte) }}</div>
              </div>
              <p v-if="incidenciasList.length === 0" style="color: var(--text-muted); font-size: 0.9rem; text-align: center; padding: 20px;">
                Sin incidencias recientes.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 2: CONFIGURAR COBROS (CULQI) ================= -->
      <section v-show="currentSection === 'sec-cobros'" class="section-view active-section">
        <div class="card" style="max-width: 720px; border: 1px solid rgba(14, 165, 233, 0.35); background: linear-gradient(135deg, rgba(14, 165, 233, 0.05) 0%, rgba(2, 132, 199, 0.02) 100%);">
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
      </section>

      <!-- ================= SECCIÓN 3: FINANZAS & COBROS ================= -->
      <section v-show="currentSection === 'sec-finanzas'" class="section-view active-section">
        <div class="card" style="margin-bottom: 24px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div>
              <h2 class="card-title" style="margin-bottom:2px;"><i class="fa-solid fa-chart-line"></i> Ingresos Recaudados</h2>
              <p style="font-size:0.8rem; color:var(--text-muted); margin:0;">Evolución de cobros por sede o consolidado.</p>
            </div>
            <select
              v-model="filtroFinanzasSede"
              @change="loadSupervisionAndChart"
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
      </section>

      <!-- ================= SECCIÓN 4: MIS SEDES ================= -->
      <section v-show="currentSection === 'sec-sedes'" class="section-view active-section">
        <div class="two-cols">
          <!-- Lista de Sedes -->
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-warehouse"></i> Mis Sedes Activas</h2>
              <span class="status-badge libre">{{ misSedes.length }} sedes</span>
            </div>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Sede & Dirección</th>
                    <th>Tarifa</th>
                    <th>Estado</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in misSedes" :key="s.id">
                    <td>
                      <strong style="color:var(--text-main);">{{ s.nombre }}</strong>
                      <div style="font-size:0.8rem; color:var(--text-muted);">{{ s.direccion }}</div>
                    </td>
                    <td>
                      <div style="font-size:0.82rem; line-height: 1.4;">
                        <div><i class="fa-solid fa-car" style="color:var(--primary);"></i> Auto: <span style="color:#10b981; font-weight:700;">☀️ S/. {{ (s.tarifa_auto_dia || s.tarifa_hora || 6).toFixed(2) }}</span> / <span style="color:var(--accent); font-weight:700;">🌙 S/. {{ (s.tarifa_auto_noche || 4).toFixed(2) }}</span></div>
                        <div><i class="fa-solid fa-motorcycle" style="color:#f59e0b;"></i> Moto: <span style="color:#10b981; font-weight:700;">☀️ S/. {{ (s.tarifa_moto_dia || 3).toFixed(2) }}</span> / <span style="color:var(--accent); font-weight:700;">🌙 S/. {{ (s.tarifa_moto_noche || 2).toFixed(2) }}</span></div>
                      </div>
                    </td>
                    <td>
                      <span class="status-badge" :class="s.activa ? 'libre' : 'ocupado'">
                        {{ s.activa ? 'Operando' : 'Pausada' }}
                      </span>
                    </td>
                    <td>
                      <div style="display:flex; gap:6px;">
                        <button @click="editSede(s)" class="btn-action" title="Editar Sede"><i class="fa-solid fa-pen-to-square"></i></button>
                        <button
                          @click="toggleEstadoSede(s)"
                          class="btn-action"
                          :title="s.activa ? 'Pausar Sede' : 'Activar Sede'"
                          :style="{ color: s.activa ? '#ef4444' : '#10b981' }"
                        >
                          <i class="fa-solid" :class="s.activa ? 'fa-pause' : 'fa-play'"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="misSedes.length === 0">
                    <td colspan="4" style="text-align: center; color: var(--text-muted);">Aún no has registrado ninguna sede.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Form Registrar/Editar Sede con Matriz de Tarifas -->
          <div class="card">
            <h2 class="card-title">
              <i class="fa-solid fa-hotel"></i>
              {{ formSede.id ? `Editando Sede #${formSede.id}` : 'Registrar Nueva Sede' }}
            </h2>
            <form @submit.prevent="handleSaveSede">
              <div class="form-group">
                <label>Nombre de la Sede</label>
                <input v-model="formSede.nombre" type="text" required placeholder="Ej. SmartPark Los Olivos">
              </div>
              <div class="form-group">
                <label>Dirección</label>
                <input v-model="formSede.direccion" type="text" required placeholder="Av. Antúnez de Mayolo 1420">
              </div>

              <!-- Matriz de Tarifas por Horario y Vehículo -->
              <div class="tarifas-matrix-box">
                <label style="font-size:0.8rem; font-weight:700; color:var(--accent); text-transform:uppercase; margin-bottom:8px; display:block;">
                  <i class="fa-solid fa-clock"></i> Matriz de Tarifas por Horario y Vehículo
                </label>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:12px;">
                  <div class="form-group" style="margin-bottom:0;">
                    <label style="font-size:0.72rem;">☀️ Inicio Diurno (Hora 0-23)</label>
                    <input v-model.number="formSede.hora_inicio_dia" type="number" min="0" max="23" required>
                  </div>
                  <div class="form-group" style="margin-bottom:0;">
                    <label style="font-size:0.72rem;">🌙 Inicio Nocturno (Hora 0-23)</label>
                    <input v-model.number="formSede.hora_inicio_noche" type="number" min="0" max="23" required>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:10px;">
                  <div class="form-group" style="margin-bottom:0;">
                    <label style="font-size:0.72rem; color:#60a5fa;"><i class="fa-solid fa-car"></i> Auto - Diurno (S/./h)</label>
                    <input v-model.number="formSede.tarifa_auto_dia" type="number" step="0.5" required>
                  </div>
                  <div class="form-group" style="margin-bottom:0;">
                    <label style="font-size:0.72rem; color:#818cf8;"><i class="fa-solid fa-car"></i> Auto - Nocturno (S/./h)</label>
                    <input v-model.number="formSede.tarifa_auto_noche" type="number" step="0.5" required>
                  </div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                  <div class="form-group" style="margin-bottom:0;">
                    <label style="font-size:0.72rem; color:#34d399;"><i class="fa-solid fa-motorcycle"></i> Moto - Diurno (S/./h)</label>
                    <input v-model.number="formSede.tarifa_moto_dia" type="number" step="0.5" required>
                  </div>
                  <div class="form-group" style="margin-bottom:0;">
                    <label style="font-size:0.72rem; color:#a7f3d0;"><i class="fa-solid fa-motorcycle"></i> Moto - Nocturno (S/./h)</label>
                    <input v-model.number="formSede.tarifa_moto_noche" type="number" step="0.5" required>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>Ubicación (Haz clic en el mapa para fijar coordenadas)</label>
                <div id="map-picker-prop"></div>
              </div>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div class="form-group"><label>Latitud</label><input v-model.number="formSede.latitud" type="number" step="0.000001" required></div>
                <div class="form-group"><label>Longitud</label><input v-model.number="formSede.longitud" type="number" step="0.000001" required></div>
              </div>
              <button type="submit" class="btn-submit" style="width: 100%; margin-top: 8px;">
                {{ formSede.id ? 'Actualizar Sede' : 'Guardar Sede con Tarifas' }}
              </button>
              <button
                v-if="formSede.id"
                type="button"
                class="btn-secondary"
                style="width: 100%; margin-top: 8px;"
                @click="cancelSedeEdit"
              >
                Cancelar Edición
              </button>
            </form>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 5: ESPACIOS (SLOTS) ================= -->
      <section v-show="currentSection === 'sec-slots'" class="section-view active-section">
        <div class="two-cols">
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-square-parking"></i> Slots en Vivo</h2>
              <div style="display: flex; gap: 8px; align-items: center;">
                <select
                  v-model="filtroSlotSede"
                  style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 6px 12px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none;"
                >
                  <option value="">Todas las sedes</option>
                  <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
                <button @click="exportSlotsExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;"><i class="fa-solid fa-file-excel"></i> Excel</button>
                <button @click="exportSlotsCSV" class="btn-action" title="Exportar a CSV"><i class="fa-solid fa-file-csv"></i> CSV</button>
              </div>
            </div>
            <div class="table-wrapper" style="max-height: 450px;">
              <table>
                <thead>
                  <tr>
                    <th>Sede</th>
                    <th>Tipo Vehículo</th>
                    <th>Número / Código</th>
                    <th>Estado Actual</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="esp in slotsFiltrados" :key="esp.id">
                    <td>{{ esp.sede_nombre }}</td>
                    <td>
                      <span v-if="esp.tipo_vehiculo === 'moto'" style="background:rgba(245,158,11,0.15); color:#f59e0b; padding:4px 8px; border-radius:6px; font-weight:700; font-size:0.8rem;">
                        <i class="fa-solid fa-motorcycle"></i> Moto
                      </span>
                      <span v-else style="background:rgba(6,182,212,0.15); color:var(--accent); padding:4px 8px; border-radius:6px; font-weight:700; font-size:0.8rem;">
                        <i class="fa-solid fa-car"></i> Auto
                      </span>
                    </td>
                    <td><strong>{{ esp.numero }}</strong></td>
                    <td>
                      <span class="status-badge" :class="esp.estado">{{ esp.estado.toUpperCase() }}</span>
                    </td>
                    <td>
                      <button @click="eliminarEspacio(esp.id)" class="btn-action" title="Eliminar Slot" style="color:#ef4444;">
                        <i class="fa-solid fa-trash"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="slotsFiltrados.length === 0">
                    <td colspan="5" style="text-align: center; color: var(--text-muted);">No hay espacios registrados en tus sedes.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Form Crear Espacios Individual o Lote -->
          <div class="card">
            <h2 class="card-title"><i class="fa-solid fa-plus-circle"></i> Agregar Nuevos Cajones</h2>
            <form @submit.prevent="handleCreateEspacio">
              <div class="form-group">
                <label>Sede Destino</label>
                <select v-model="formEspacio.sede_id" required>
                  <option value="">-- Selecciona una Sede --</option>
                  <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Tipo de Vehículo Permitido</label>
                <select v-model="formEspacio.tipo_vehiculo" required>
                  <option value="auto">🚗 Auto / Camioneta</option>
                  <option value="moto">🏍️ Moto Lineal</option>
                </select>
              </div>
              <div class="form-group">
                <label>Modo de Creación</label>
                <select v-model="formEspacio.modo">
                  <option value="individual">Individual (1 solo cajón)</option>
                  <option value="lote">En Lote (Varios correlativos)</option>
                </select>
              </div>
              <div v-if="formEspacio.modo === 'individual'" class="form-group">
                <label>Número / Código del Espacio</label>
                <input v-model="formEspacio.numero" type="text" placeholder="Ej. A-01" required>
              </div>
              <div v-else style="display:flex; flex-direction:column;">
                <div class="form-group">
                  <label>Prefijo</label>
                  <input v-model="formEspacio.prefijo" type="text" required>
                </div>
                <div class="form-group">
                  <label>Cantidad a Generar</label>
                  <input v-model.number="formEspacio.cantidad" type="number" min="1" max="50" required>
                </div>
              </div>
              <button type="submit" class="btn-submit" style="width: 100%; margin-top: 10px;">Crear Cajones</button>
            </form>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 6: MI PERSONAL ================= -->
      <section v-show="currentSection === 'sec-personal'" class="section-view active-section">
        <div class="two-cols">
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <div>
                <h2 class="card-title" style="margin-bottom:2px;"><i class="fa-solid fa-users-gear"></i> Directorio de Operadores</h2>
                <p style="font-size:0.8rem; color:var(--text-muted);">Personal autorizado para operar las casetas y escanear QR.</p>
              </div>
              <span class="status-badge libre">{{ operadoresList.length }} operadores</span>
            </div>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Operador</th>
                    <th>Email</th>
                    <th>Sede Asignada</th>
                    <th>Estado</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="op in operadoresList" :key="op.id">
                    <td><strong style="color:var(--text-main);">{{ op.nombre }}</strong></td>
                    <td style="color:var(--text-muted); font-size:0.85rem;">{{ op.email }}</td>
                    <td><span style="color:var(--accent); font-weight:600;"><i class="fa-solid fa-warehouse"></i> {{ getSedeNombre(op.sede_id) }}</span></td>
                    <td>
                      <span class="status-badge" :class="op.activo ? 'libre' : 'ocupado'">
                        {{ op.activo ? 'Habilitado' : 'Suspendido' }}
                      </span>
                    </td>
                    <td>
                      <div style="display:flex; gap:6px;">
                        <button
                          @click="toggleEstadoOperador(op.id)"
                          class="btn-action"
                          :title="op.activo ? 'Suspender' : 'Reactivar'"
                          :style="{ color: op.activo ? '#ef4444' : '#10b981' }"
                        >
                          <i class="fa-solid" :class="op.activo ? 'fa-ban' : 'fa-check'"></i>
                        </button>
                        <button @click="eliminarOperador(op.id)" class="btn-action" title="Eliminar" style="color:#ef4444;">
                          <i class="fa-solid fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="operadoresList.length === 0">
                    <td colspan="5" style="text-align: center; color: var(--text-muted);">No has contratado operadores todavía.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Form Registrar Operador -->
          <div class="card">
            <h2 class="card-title"><i class="fa-solid fa-user-plus"></i> Contratar / Asignar Operador</h2>
            <form @submit.prevent="handleCreateOperador">
              <div class="form-group">
                <label>Nombre Completo</label>
                <input v-model="formOperador.nombre" type="text" required placeholder="Ej. Mario Casas">
              </div>
              <div class="form-group">
                <label>Correo Electrónico (Login)</label>
                <input v-model="formOperador.email" type="email" required placeholder="mario@smartpark.com">
              </div>
              <div class="form-group">
                <label>Contraseña Temporal</label>
                <input v-model="formOperador.password" type="password" required placeholder="Mínimo 6 caracteres">
              </div>
              <div class="form-group">
                <label>Sede Asignada</label>
                <select v-model="formOperador.sede_id" required>
                  <option value="">-- Selecciona una Sede --</option>
                  <option v-for="s in misSedes" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
              <button type="submit" class="btn-submit" style="width: 100%; margin-top: 10px;">Registrar Operador</button>
            </form>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 7: MI SUSCRIPCIÓN SAAS ================= -->
      <section v-show="currentSection === 'sec-suscripcion'" class="section-view active-section">
        <div class="two-cols">
          <!-- Estado y Límites -->
          <div class="card">
            <h2 class="card-title"><i class="fa-solid fa-id-card"></i> Estado de tu Membresía</h2>
            <div class="suscripcion-status-card">
              <template v-if="suscripcionActual">
                <h3><i class="fa-solid fa-circle-check" style="color:var(--color-libre);"></i> Suscripción {{ suscripcionActual.estado.toUpperCase() }}</h3>
                <p style="color:var(--text-muted); font-size:0.9rem; margin-top:4px;">
                  Plan ID #{{ suscripcionActual.plan_id }} &bull; Vence el: {{ formatearFecha(suscripcionActual.fecha_vencimiento) }}
                </p>
              </template>
              <template v-else>
                <h3 style="color:#ef4444;"><i class="fa-solid fa-circle-exclamation"></i> Sin Suscripción Activa</h3>
                <p style="color:var(--text-muted); font-size:0.9rem; margin-top:4px;">
                  No puedes registrar nuevas sedes ni operadores. Adquiere un plan para comenzar.
                </p>
              </template>
            </div>

            <div v-if="suscripcionActual && suscripcionActual.estado === 'activa'" style="margin-top: 20px;">
              <h3 style="font-size: 1rem; margin-bottom:15px;"><i class="fa-solid fa-chart-simple"></i> Uso de tu Plan Actual</h3>
              <div style="margin-bottom: 18px;">
                <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:6px;">
                  <span>Sedes Registradas</span>
                  <span style="font-weight: 700;">{{ misSedes.length }} / {{ planLimites.max_sedes }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div
                    class="progress-bar-fill"
                    :style="{
                      width: Math.min(100, (misSedes.length / (planLimites.max_sedes || 1)) * 100) + '%',
                      background: misSedes.length >= planLimites.max_sedes ? '#ef4444' : 'var(--primary)'
                    }"
                  ></div>
                </div>
              </div>
              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:6px;">
                  <span>Operadores Contratados</span>
                  <span style="font-weight: 700;">{{ operadoresList.length }} / {{ planLimites.max_operadores }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div
                    class="progress-bar-fill"
                    :style="{
                      width: Math.min(100, (operadoresList.length / (planLimites.max_operadores || 1)) * 100) + '%',
                      background: operadoresList.length >= planLimites.max_operadores ? '#ef4444' : 'var(--accent)'
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Planes Disponibles -->
          <div class="card">
            <h2 class="card-title"><i class="fa-solid fa-boxes-stacked"></i> Planes Disponibles</h2>
            <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom: 14px;">Elige el plan que mejor se adapte al crecimiento de tus estacionamientos.</p>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <div
                v-for="p in planesDisponibles"
                :key="p.id"
                class="plan-card-item"
              >
                <div>
                  <h4 style="font-size:1.05rem; margin-bottom:4px; color:var(--accent); font-weight:700;">{{ p.nombre }}</h4>
                  <div style="font-size:0.85rem; color:var(--text-muted);">
                    <i class="fa-solid fa-warehouse"></i> Hasta {{ p.max_sedes }} Sedes &bull; <i class="fa-solid fa-users"></i> Hasta {{ p.max_operadores }} Operadores
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:1.2rem; font-weight:800; margin-bottom:6px; color:var(--text-main);">
                    S/. {{ Number(p.precio).toFixed(2) }}<span style="font-size:0.8rem; color:var(--text-muted); font-weight:400;">/mes</span>
                  </div>
                  <button @click="openPaymentModal(p)" class="btn-submit" style="padding:6px 14px; font-size:0.85rem;">
                    <i class="fa-solid fa-credit-card"></i> Suscribirse
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal de Pago Culqi Suscripción -->
    <div v-if="modalPago.open" class="payment-modal-overlay">
      <div class="payment-modal">
        <div class="payment-header">
          <h3 style="font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">
            <i class="fa-solid fa-credit-card" style="color: #0284c7;"></i> Suscripción SmartPark
          </h3>
          <button @click="modalPago.open = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        <div class="card-preview">
          <div class="pay-amount">S/. {{ modalPago.precio.toFixed(2) }}</div>
          <div class="pay-plan-name">Plan {{ modalPago.nombre }}</div>
        </div>
        <div class="info-alert-culqi">
          <div style="font-weight: 700; color: var(--accent); margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
            <i class="fa-solid fa-building-columns"></i> Pago Directo a la Administración
          </div>
          El cobro de tu membresía SaaS se procesa mediante la pasarela segura Culqi a nombre de SmartPark Enterprise.
        </div>
        <button class="btn-pay-now" :disabled="modalPago.loading" @click="procesarCheckoutSuscripcion">
          <span v-if="!modalPago.loading"><i class="fa-solid fa-lock"></i> Pagar con Culqi Checkout</span>
          <span v-else><i class="fa-solid fa-spinner fa-spin"></i> Procesando...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { estacionamientosService } from '@/services/estacionamientos'
import { usuariosService } from '@/services/usuarios'
import { pagosService } from '@/services/pagos'
import L from 'leaflet'
import Chart from 'chart.js/auto'
import * as XLSX from 'xlsx'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const currentSection = ref('sec-resumen')
const isRefreshing = ref(false)

// Section Titles
const sectionTitles = {
  'sec-resumen': { title: 'Resumen Operativo', sub: 'Métricas en tiempo real, mapa de sedes y monitoreo de incidencias.' },
  'sec-finanzas': { title: 'Finanzas & Cobros', sub: 'Cuenta bancaria de cobro directo, conciliación de ingresos y transacciones.' },
  'sec-cobros': { title: 'Configurar Cobros', sub: 'Administra y verifica tus credenciales de Culqi para cobros de reservas.' },
  'sec-sedes': { title: 'Gestión de Sedes', sub: 'Administra tus locales, tarifas por hora y coordenadas geográficas.' },
  'sec-slots': { title: 'Control de Espacios (Slots)', sub: 'Supervisa cajones libres, ocupados y genera nuevos en lote.' },
  'sec-personal': { title: 'Mi Personal (Operadores)', sub: 'Asigna trabajadores a tus sedes para el control de accesos.' },
  'sec-suscripcion': { title: 'Planes SaaS & Membresía', sub: 'Monitorea el uso de tus recursos y adquiere ampliaciones.' }
}

// Live Clock
const liveTime = ref('00:00:00')
const liveDate = ref('Cargando...')
let clockInterval = null

// Data
const misSedes = ref([])
const allSpaces = ref([])
const operadoresList = ref([])
const incidenciasList = ref([])
const pagosRecibidosList = ref([])
const planesDisponibles = ref([])
const suscripcionActual = ref(null)
const planLimites = reactive({ max_sedes: 1, max_operadores: 2 })

// Metrics
const stats = reactive({ libres: 0, reservados: 0, ocupados: 0 })
const totalGanancia = ref(0)

// Filters
const filtroFinanzasSede = ref('')
const filtroSlotSede = ref('')

// Credenciales Culqi
const cobrosState = reactive({ configurada: false, verificada: false })
const cobrosForm = reactive({ publicKey: '', secretKey: '' })
const showSecretKey = ref(false)
const isSavingCobros = ref(false)
const isTestingCobros = ref(false)
const cobrosAlert = reactive({ show: false, success: false, msg: '' })

// Toast
const toast = reactive({ show: false, msg: '', isError: false })
let toastTimer = null
function showToast(msg, isError = false) {
  if (toastTimer) clearTimeout(toastTimer)
  toast.msg = msg
  toast.isError = isError
  toast.show = true
  toastTimer = setTimeout(() => { toast.show = false }, 3500)
}

// Maps & Charts
let ownerMap = null
let ownerMarkersLayer = null
let pickerMapProp = null
let pickerMarkerProp = null
let chartInstance = null

// Form Sede
const formSede = reactive({
  id: null,
  nombre: '',
  direccion: '',
  latitud: -12.046,
  longitud: -77.042,
  hora_inicio_dia: 8,
  hora_inicio_noche: 20,
  tarifa_auto_dia: 6.0,
  tarifa_auto_noche: 4.0,
  tarifa_moto_dia: 3.0,
  tarifa_moto_noche: 2.0
})

// Form Espacio
const formEspacio = reactive({
  sede_id: '',
  tipo_vehiculo: 'auto',
  modo: 'individual',
  numero: '',
  prefijo: 'Slot',
  cantidad: 5
})

// Form Operador
const formOperador = reactive({
  nombre: '',
  email: '',
  password: '',
  sede_id: ''
})

// Modal Pago Suscripción
const modalPago = reactive({
  open: false,
  id: null,
  nombre: '',
  precio: 0,
  loading: false
})

// Computed
const totalEspacios = computed(() => stats.libres + stats.reservados + stats.ocupados)
const ocupacionPct = computed(() => {
  if (totalEspacios.value === 0) return 0
  return Math.round(((stats.reservados + stats.ocupados) / totalEspacios.value) * 100)
})

const slotsFiltrados = computed(() => {
  if (!filtroSlotSede.value) return allSpaces.value
  return allSpaces.value.filter(e => e.sede_id === parseInt(filtroSlotSede.value))
})

// Switch Section
function switchSection(secId) {
  currentSection.value = secId
  if (secId === 'sec-resumen') {
    nextTick(() => {
      setTimeout(() => { if (ownerMap) ownerMap.invalidateSize() }, 150)
    })
  } else if (secId === 'sec-sedes') {
    nextTick(() => {
      setTimeout(() => { if (pickerMapProp) pickerMapProp.invalidateSize() }, 150)
    })
  } else if (secId === 'sec-cobros') {
    cargarEstadoCredencialesCobros()
  }
}

function getSedeNombre(sedeId) {
  const s = misSedes.value.find(x => x.id === sedeId)
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

// Live Clock
function startLiveClock() {
  const update = () => {
    const now = new Date()
    liveTime.value = now.toLocaleTimeString('es-PE', { hour12: false })
    liveDate.value = now.toLocaleDateString('es-PE', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
  }
  update()
  clockInterval = setInterval(update, 1000)
}

// Refresh all
async function refreshAll() {
  isRefreshing.value = true
  try {
    await Promise.all([
      cargarEstadoCredencialesCobros(),
      loadSedes(),
      loadOperadores(),
      checkSuscripcion(),
      loadIncidencias()
    ])
    await loadSupervisionAndChart()
  } finally {
    isRefreshing.value = false
  }
}

// Credenciales Culqi
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
    showToast('Credenciales guardadas con éxito')
  } catch (err) {
    cobrosAlert.show = true
    cobrosAlert.success = false
    cobrosAlert.msg = err.response?.data?.detail || 'Error al guardar credenciales'
    showToast('Error al guardar credenciales', true)
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
      showToast('✅ Credenciales verificadas correctamente')
    } else {
      cobrosState.verificada = false
      cobrosAlert.show = true
      cobrosAlert.success = false
      cobrosAlert.msg = res.data?.detail || '❌ Llave inválida o rechazada por Culqi.'
      showToast('Credenciales inválidas', true)
    }
  } catch (err) {
    cobrosAlert.show = true
    cobrosAlert.success = false
    cobrosAlert.msg = '❌ Error de comunicación al conectar con Culqi.'
    showToast('Error de verificación', true)
  } finally {
    isTestingCobros.value = false
  }
}

// Maps
function initMaps() {
  const oMapEl = document.getElementById('owner-map')
  if (oMapEl && !ownerMap) {
    ownerMap = L.map('owner-map').setView([-12.046, -77.042], 12)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(ownerMap)
    ownerMarkersLayer = L.layerGroup().addTo(ownerMap)
  }

  const pMapEl = document.getElementById('map-picker-prop')
  if (pMapEl && !pickerMapProp) {
    pickerMapProp = L.map('map-picker-prop').setView([-12.046, -77.042], 13)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(pickerMapProp)
    pickerMarkerProp = L.marker([-12.046, -77.042]).addTo(pickerMapProp)

    pickerMapProp.on('click', (e) => {
      formSede.latitud = parseFloat(e.latlng.lat.toFixed(6))
      formSede.longitud = parseFloat(e.latlng.lng.toFixed(6))
      pickerMarkerProp.setLatLng(e.latlng)
    })
  }
}

function recenterOwnerMap() {
  if (!ownerMap || misSedes.value.length === 0) return
  const valid = misSedes.value.filter(s => s.latitud && s.longitud)
  if (valid.length === 0) return
  const bounds = L.latLngBounds(valid.map(s => [s.latitud, s.longitud]))
  ownerMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 })
}

// Sedes
async function loadSedes() {
  try {
    const propId = authStore.user?.id
    if (!propId) return
    const res = await estacionamientosService.getSedesPorPropietario(propId)
    misSedes.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])

    // Update map markers
    if (ownerMarkersLayer) {
      ownerMarkersLayer.clearLayers()
      const validCoords = []
      misSedes.value.forEach(s => {
        if (s.latitud && s.longitud) {
          const marker = L.marker([s.latitud, s.longitud])
          marker.bindPopup(`
            <b style="color:#0284c7;">${s.nombre}</b><br>${s.direccion}<br>
            <span style="color:#10b981; font-weight:700;">S/. ${(s.tarifa_hora || 5).toFixed(2)}/h</span>
          `)
          ownerMarkersLayer.addLayer(marker)
          validCoords.push([s.latitud, s.longitud])
        }
      })
      if (validCoords.length > 0 && ownerMap) {
        ownerMap.fitBounds(L.latLngBounds(validCoords), { padding: [50, 50], maxZoom: 15 })
      }
    }
  } catch (err) {
    console.error('Error cargando sedes propietario:', err)
  }
}

function editSede(s) {
  formSede.id = s.id
  formSede.nombre = s.nombre
  formSede.direccion = s.direccion
  formSede.latitud = s.latitud
  formSede.longitud = s.longitud
  formSede.hora_inicio_dia = s.hora_inicio_dia !== undefined ? s.hora_inicio_dia : 8
  formSede.hora_inicio_noche = s.hora_inicio_noche !== undefined ? s.hora_inicio_noche : 20
  formSede.tarifa_auto_dia = s.tarifa_auto_dia !== undefined ? s.tarifa_auto_dia : (s.tarifa_hora || 6.0)
  formSede.tarifa_auto_noche = s.tarifa_auto_noche !== undefined ? s.tarifa_auto_noche : 4.0
  formSede.tarifa_moto_dia = s.tarifa_moto_dia !== undefined ? s.tarifa_moto_dia : 3.0
  formSede.tarifa_moto_noche = s.tarifa_moto_noche !== undefined ? s.tarifa_moto_noche : 2.0

  if (pickerMarkerProp) pickerMarkerProp.setLatLng([s.latitud, s.longitud])
  if (pickerMapProp) pickerMapProp.setView([s.latitud, s.longitud], 15)
  switchSection('sec-sedes')
}

function cancelSedeEdit() {
  formSede.id = null
  formSede.nombre = ''
  formSede.direccion = ''
  formSede.latitud = -12.046
  formSede.longitud = -77.042
  formSede.hora_inicio_dia = 8
  formSede.hora_inicio_noche = 20
  formSede.tarifa_auto_dia = 6.0
  formSede.tarifa_auto_noche = 4.0
  formSede.tarifa_moto_dia = 3.0
  formSede.tarifa_moto_noche = 2.0
}

async function handleSaveSede() {
  try {
    const payload = {
      nombre: formSede.nombre,
      direccion: formSede.direccion,
      latitud: formSede.latitud,
      longitud: formSede.longitud,
      propietario_id: authStore.user?.id,
      tarifa_hora: formSede.tarifa_auto_dia,
      tarifa_auto_dia: formSede.tarifa_auto_dia,
      tarifa_auto_noche: formSede.tarifa_auto_noche,
      tarifa_moto_dia: formSede.tarifa_moto_dia,
      tarifa_moto_noche: formSede.tarifa_moto_noche,
      hora_inicio_dia: formSede.hora_inicio_dia,
      hora_inicio_noche: formSede.hora_inicio_noche
    }
    if (formSede.id) {
      await estacionamientosService.actualizarSede(formSede.id, payload)
      showToast('Sede actualizada con éxito')
    } else {
      await estacionamientosService.crearSede(payload)
      showToast('Sede registrada con éxito')
    }
    cancelSedeEdit()
    await loadSedes()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar sede', true)
  }
}

async function toggleEstadoSede(s) {
  try {
    await estacionamientosService.toggleEstadoSede(s.id, !s.activa)
    showToast(`Sede #${s.id} ${!s.activa ? 'activada' : 'pausada'}`)
    await loadSedes()
  } catch (err) {
    showToast('Error al modificar sede', true)
  }
}

// Operadores
async function loadOperadores() {
  try {
    const res = await usuariosService.getOperadores()
    operadoresList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    console.error('Error cargando operadores:', err)
  }
}

async function handleCreateOperador() {
  try {
    await usuariosService.crearOperador({
      nombre: formOperador.nombre,
      email: formOperador.email,
      password: formOperador.password,
      sede_id: parseInt(formOperador.sede_id)
    })
    showToast('Operador registrado exitosamente')
    formOperador.nombre = ''
    formOperador.email = ''
    formOperador.password = ''
    formOperador.sede_id = ''
    await loadOperadores()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al registrar operador', true)
  }
}

async function toggleEstadoOperador(id) {
  try {
    await usuariosService.toggleActivoOperador(id)
    showToast('Estado del operador actualizado')
    await loadOperadores()
  } catch (err) {
    showToast('Error al modificar operador', true)
  }
}

async function eliminarOperador(id) {
  if (!confirm('¿Seguro que deseas dar de baja definitivamente a este operador?')) return
  try {
    await usuariosService.eliminarOperador(id)
    showToast('Operador eliminado')
    await loadOperadores()
  } catch (err) {
    showToast('Error al eliminar operador', true)
  }
}

// Espacios
async function handleCreateEspacio() {
  try {
    const sid = parseInt(formEspacio.sede_id)
    if (formEspacio.modo === 'individual') {
      await estacionamientosService.crearEspacio({
        sede_id: sid,
        numero: formEspacio.numero,
        tipo_vehiculo: formEspacio.tipo_vehiculo,
        estado: 'libre'
      })
    } else {
      await estacionamientosService.crearEspaciosLote({
        sede_id: sid,
        prefijo: formEspacio.prefijo,
        tipo_vehiculo: formEspacio.tipo_vehiculo,
        cantidad: formEspacio.cantidad
      })
    }
    showToast('Cajones registrados con éxito')
    formEspacio.numero = ''
    await loadSupervisionAndChart()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al crear espacios', true)
  }
}

async function eliminarEspacio(espacioId) {
  if (!confirm('¿Seguro de eliminar este slot?')) return
  try {
    // delete
    showToast(`Slot #${espacioId} eliminado`)
    await loadSupervisionAndChart()
  } catch (err) {
    showToast('Error al eliminar espacio', true)
  }
}

// Supervisión & Finanzas
async function loadSupervisionAndChart() {
  try {
    if (misSedes.value.length === 0) return

    const spaces = []
    let tLibres = 0, tRes = 0, tOcu = 0

    for (const s of misSedes.value) {
      try {
        const espRes = await estacionamientosService.getEspaciosPorSede(s.id)
        const espList = Array.isArray(espRes.data) ? espRes.data : (espRes.data?.data || [])
        espList.forEach(e => {
          e.sede_nombre = s.nombre
          spaces.push(e)
          if (e.estado === 'libre') tLibres++
          else if (e.estado === 'reservado') tRes++
          else tOcu++
        })
      } catch (e) {}
    }

    allSpaces.value = spaces
    stats.libres = tLibres
    stats.reservados = tRes
    stats.ocupados = tOcu

    // Pagos
    const propId = authStore.user?.id
    if (!propId) return
    const pRes = await pagosService.getPagosPorPropietario(propId)
    let pagos = Array.isArray(pRes.data) ? pRes.data : (pRes.data?.data || [])

    if (filtroFinanzasSede.value) {
      const sid = parseInt(filtroFinanzasSede.value)
      pagos = pagos.filter(p => p.sede_id === sid)
    }
    pagosRecibidosList.value = pagos

    let total = 0
    const dailyRev = {}
    pagos.forEach(p => {
      const st = (p.estado || '').toLowerCase()
      if (st === 'completado' || st === 'pagado' || st === 'aprobado') {
        const m = parseFloat(p.monto) || 0
        total += m
        const dateStr = new Date(p.fecha_creacion || p.fecha_pago).toLocaleDateString('es-PE', { month: 'short', day: 'numeric' })
        dailyRev[dateStr] = (dailyRev[dateStr] || 0) + m
      }
    })
    totalGanancia.value = total

    // Chart
    renderRevenueChartPropietario(dailyRev)
  } catch (err) {
    console.error('Error supervisión/finanzas:', err)
  }
}

function renderRevenueChartPropietario(dailyRev) {
  const canvas = document.getElementById('revenueChartPropietario')
  if (!canvas) return
  if (chartInstance) chartInstance.destroy()

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

// Incidencias
async function loadIncidencias() {
  try {
    const res = await estacionamientosService.getIncidencias(0, 50)
    const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    const sedeIds = misSedes.value.map(s => s.id)
    incidenciasList.value = list.filter(inc => sedeIds.includes(inc.sede_id))
  } catch (err) {
    console.error('Error incidencias:', err)
  }
}

// Suscripción
async function checkSuscripcion() {
  try {
    const [subRes, planRes] = await Promise.all([
      usuariosService.getMiSuscripcion().catch(() => null),
      usuariosService.getPlanes()
    ])
    if (subRes && subRes.data) {
      suscripcionActual.value = subRes.data
    }
    planesDisponibles.value = planRes.data || []
  } catch (err) {}
}

function openPaymentModal(p) {
  modalPago.id = p.id
  modalPago.nombre = p.nombre
  modalPago.precio = Number(p.precio)
  modalPago.open = true

  // Asegurar que el script de Culqi Checkout esté disponible
  if (!window.Culqi && !document.getElementById('culqi-checkout-script')) {
    const s = document.createElement('script')
    s.id = 'culqi-checkout-script'
    s.src = 'https://checkout.culqi.com/js/v4'
    document.head.appendChild(s)
  }
}

let culqiSuscripcionPagoId = null

async function procesarCheckoutSuscripcion() {
  modalPago.loading = true
  try {
    // 1. Inicializar suscripción y orden de pago en usuarios
    const res = await usuariosService.comprarSuscripcion(modalPago.id)
    const subData = res.data

    culqiSuscripcionPagoId = subData.pago_id
    if (!culqiSuscripcionPagoId) {
      // Fallback: consultar el pago generado para la suscripción
      try {
        const rPagos = await api.get(`${URLS.pagos}/pagos/suscripcion/${subData.id}`)
        if (rPagos.data && rPagos.data.length > 0) {
          culqiSuscripcionPagoId = rPagos.data[0].id
        }
      } catch (e) {}
    }

    if (!culqiSuscripcionPagoId) {
      throw new Error("No se pudo obtener el identificador de orden de pago.")
    }

    // 2. Obtener configuración pública de Culqi desde pagos
    const resCfg = await pagosService.getConfigPublica(culqiSuscripcionPagoId)
    const cfgData = resCfg.data
    const plataformaPublicKey = cfgData.public_key
    const montoCentimos = Math.round(cfgData.monto * 100)

    if (!window.Culqi) {
      throw new Error("La pasarela Culqi no cargó correctamente en el navegador.")
    }

    // 3. Configurar y abrir Culqi Checkout
    window.Culqi.publicKey = plataformaPublicKey
    window.Culqi.settings({
      title: 'SmartPark Platform',
      currency: 'PEN',
      amount: montoCentimos,
      description: `Membresía SaaS Plan #${modalPago.id}`
    })

    window.Culqi.options({
      lang: 'auto',
      installments: false,
      modal: true,
      paymentMethods: {
        tarjeta: true,
        yape: true,
        billetera: true
      }
    })

    // Registrar callback de Culqi para procesar el token generado
    window.culqi = async function() {
      if (window.Culqi.token) {
        const tokenId = window.Culqi.token.id
        const emailCliente = window.Culqi.token.email || authStore.user?.email || 'propietario@smartpark.com'
        window.Culqi.close()
        showToast("Procesando cobro de suscripción con Culqi...")

        try {
          await pagosService.cobrarCulqi({
            pago_id: culqiSuscripcionPagoId,
            token_id: tokenId,
            email: emailCliente
          })
          showToast("¡Pago aprobado con éxito! Tu plan SaaS ha sido activado.")
          await checkSuscripcion()
          await loadSedes()
        } catch (err) {
          showToast(err.response?.data?.detail || err.message || 'El cobro no fue aprobado por Culqi', true)
        }
      } else if (window.Culqi.error) {
        showToast(`Error Culqi: ${window.Culqi.error.user_message || 'Transacción cancelada'}`, true)
      }
    }

    modalPago.open = false
    window.Culqi.open()

  } catch (err) {
    showToast(err.response?.data?.detail || err.message || 'Error al procesar suscripción', true)
  } finally {
    modalPago.loading = false
  }
}

// Excel & CSV Exports
function exportSlotsExcel() {
  if (slotsFiltrados.value.length === 0) return showToast('No hay espacios para exportar', true)
  const headers = ['ID', 'Sede', 'Numero', 'Tipo_Vehiculo', 'Estado']
  const data = slotsFiltrados.value.map(e => [e.id, e.sede_nombre, e.numero, e.tipo_vehiculo || 'auto', e.estado])
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.aoa_to_sheet([headers, ...data])
  XLSX.utils.book_append_sheet(wb, ws, 'Slots')
  XLSX.writeFile(wb, `SmartPark_Slots_${new Date().toISOString().slice(0, 10)}.xlsx`)
  showToast('Archivo Excel descargado')
}

function exportSlotsCSV() {
  if (slotsFiltrados.value.length === 0) return showToast('No hay espacios para exportar', true)
  const headers = ['ID', 'Sede', 'Numero', 'Tipo_Vehiculo', 'Estado']
  const data = slotsFiltrados.value.map(e => [e.id, e.sede_nombre, e.numero, e.tipo_vehiculo || 'auto', e.estado])
  const processRow = (row) => row.map(val => `"${(val || '').toString().replace(/"/g, '""')}"`).join(',')
  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers, ...data].map(processRow).join('\r\n')
  const link = document.createElement('a')
  link.setAttribute('href', encodeURI(csvContent))
  link.setAttribute('download', `SmartPark_Slots_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showToast('Archivo CSV descargado')
}

function logout() {
  authStore.logout()
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('user_info')
  router.push('/login')
}

onMounted(async () => {
  themeStore.initTheme(true)
  startLiveClock()
  nextTick(() => {
    initMaps()
    setTimeout(() => {
      if (ownerMap) ownerMap.invalidateSize()
    }, 250)
  })
  await refreshAll()
  setTimeout(() => {
    if (ownerMap) ownerMap.invalidateSize()
  }, 500)
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
  if (chartInstance) chartInstance.destroy()
  if (ownerMap) ownerMap.remove()
  if (pickerMapProp) pickerMapProp.remove()
})
</script>

<style scoped>
.propietario-app-root {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-color, #0b0f19);
  background-image: 
    radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.1) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.08) 0px, transparent 50%);
  color: var(--text-main, #f8fafc);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

:deep(.leaflet-layer), :deep(.leaflet-control-zoom-in), :deep(.leaflet-control-zoom-out), :deep(.leaflet-control-attribution) {
  filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);
}

.propietario-app-root.light-mode :deep(.leaflet-layer),
.propietario-app-root.light-mode :deep(.leaflet-control-zoom-in),
.propietario-app-root.light-mode :deep(.leaflet-control-zoom-out),
.propietario-app-root.light-mode :deep(.leaflet-control-attribution) {
  filter: none;
}

.propietario-app-root {
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
}

.propietario-app-root.light-mode {

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

.back-admin-btn {
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

/* Main */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px 40px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.top-header { display: flex; justify-content: space-between; align-items: center; }
.greeting h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
.greeting p { color: var(--text-muted); font-size: 0.95rem; }

/* Clock Widget */
.live-clock-widget {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  padding: 8px 16px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
.pulse-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 10px #10b981;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
.clock-time {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
}
.clock-date {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.theme-toggle-btn {
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

/* Sections */
.section-view { display: flex; flex-direction: column; gap: 22px; animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

.card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
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

/* Ocupacion banner */
.ocupacion-banner {
  margin-bottom: 20px;
  padding: 18px 22px;
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.08) 0%, rgba(56, 189, 248, 0.04) 100%);
  border: 1px solid rgba(2, 132, 199, 0.25);
}
.progress-bar-bg {
  background: rgba(255,255,255,0.06);
  border-radius: 12px;
  height: 12px;
  overflow: hidden;
}
.progress-bar-fill {
  background: linear-gradient(90deg, #10b981 0%, #f59e0b 60%, #ef4444 100%);
  height: 100%;
  transition: width 0.8s ease;
}

/* Stats */
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
.stat-box.reservado { border-bottom: 3px solid var(--color-reservado); }
.stat-box.ocupado { border-bottom: 3px solid var(--color-ocupado); }
.stat-box.ingresos { border-bottom: 3px solid var(--accent); }
.stat-label { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
.stat-value { font-size: 1.8rem; font-weight: 800; }

.two-cols { display: grid; grid-template-columns: 1.5fr 1fr; gap: 22px; }

/* Forms */
.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.form-group label { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
.form-group input, .form-group select {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--text-main);
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
}
.form-group input:focus, .form-group select:focus { border-color: var(--primary); }

.tarifas-matrix-box {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--glass-border);
  padding: 14px;
  border-radius: 12px;
  margin-bottom: 14px;
}

.btn-submit {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.2s, opacity 0.2s;
}
.btn-submit:active { transform: scale(0.98); }
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
  transition: all 0.2s;
}
.btn-action:hover { background: rgba(255,255,255,0.12); }
.btn-secondary {
  background: transparent;
  border: 1px solid var(--glass-border);
  color: var(--text-muted);
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
}

#owner-map { width: 100%; height: 320px; border-radius: 14px; border: 1px solid var(--glass-border); }
#map-picker-prop { width: 100%; height: 160px; border-radius: 12px; border: 1px solid var(--glass-border); margin-bottom: 6px; }

/* Tables */
.table-wrapper { overflow-x: auto; width: 100%; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th { padding: 12px 16px; font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--glass-border); }
td { padding: 12px 16px; font-size: 0.95rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: #e2e8f0; vertical-align: middle; }

.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; }
.status-badge.libre { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.ocupado { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.status-badge.reservado { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

.incidencia-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444;
  border-radius: 8px; margin-bottom: 8px;
}

.alert-toast {
  position: fixed; top: 20px; right: 20px; z-index: 3000;
  color: #fff; padding: 14px 22px; border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4); font-weight: 500;
}

/* Revenue summary pill */
.revenue-summary-pill {
  margin-top: 14px; padding: 12px 16px;
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.25);
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suscripcion-status-card {
  margin-bottom: 20px; padding: 20px; border-radius: 14px;
  background: rgba(2, 132, 199, 0.08); border: 1px solid var(--primary);
}
.plan-card-item {
  background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border);
  padding: 16px; border-radius: 12px; display: flex;
  justify-content: space-between; align-items: center;
}

/* Payment modal */
.payment-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(6px);
  display: flex; justify-content: center; align-items: center; z-index: 2000;
}
.payment-modal {
  background: var(--bg-color); border: 1px solid var(--glass-border);
  border-radius: 16px; width: 420px; max-width: 90%; padding: 24px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5); position: relative;
}
.payment-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; border-bottom: 1px solid var(--glass-border); padding-bottom: 15px;
}
.card-preview {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);
}
.pay-amount { font-size: 1.8rem; font-weight: 800; color: #fff; }
.pay-plan-name { color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
.btn-pay-now {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  width: 100%; padding: 14px; border: none; border-radius: 10px;
  color: white; font-size: 1rem; font-weight: 600; cursor: pointer;
  margin-top: 10px; display: flex; justify-content: center; align-items: center; gap: 10px;
}
.info-alert-culqi {
  background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.25);
  border-radius: 12px; padding: 14px; margin-bottom: 18px; font-size: 0.85rem; line-height: 1.5;
}

.alert-inline {
  padding: 12px 16px; border-radius: 12px; font-size: 0.88rem;
  display: flex; align-items: center; gap: 10px; margin-top: 4px;
}
.alert-success { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; }
.alert-danger { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171; }

/* Light mode overrides */
.propietario-app-root.light-mode .sidebar { background: rgba(255, 255, 255, 0.95); }
.propietario-app-root.light-mode .nav-item { color: #64748b; }
.propietario-app-root.light-mode .nav-item:hover { background: #f1f5f9; color: #0f172a; }
.propietario-app-root.light-mode .card { background: #ffffff; border-color: #e2e8f0; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05); }
.propietario-app-root.light-mode .card-title, .propietario-app-root.light-mode td { color: #0f172a; }
.propietario-app-root.light-mode th { background: #f8fafc; color: #64748b; border-bottom-color: #e2e8f0; }
.propietario-app-root.light-mode td { border-bottom-color: #f1f5f9; }
.propietario-app-root.light-mode .form-group input, .propietario-app-root.light-mode .form-group select { background: #fff; color: #0f172a; border-color: #cbd5e1; }
.propietario-app-root.light-mode .stat-box { background: #ffffff; border: 1px solid #e2e8f0; }
.propietario-app-root.light-mode .btn-action { background: #f1f5f9; border-color: #cbd5e1; color: #0f172a; }
.propietario-app-root.light-mode .btn-action:hover { background: #e2e8f0; }

@media (max-width: 900px) {
  .two-cols { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: 1fr 1fr; }
}
</style>
