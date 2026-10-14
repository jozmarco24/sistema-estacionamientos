<template>
  <div class="admin-app-root" :class="{ 'light-mode': themeStore.isLight }">
    <!-- Mobile Top Bar -->
    <div class="mobile-bar">
      <div class="logo-area" style="margin-bottom:0; font-size:1.3rem;">
        <i class="fa-solid fa-square-parking"></i> SmartPark Admin
      </div>
      <button class="toggle-btn" @click="sidebarOpen = !sidebarOpen">
        <i class="fa-solid fa-bars"></i>
      </button>
    </div>

    <!-- Sidebar Navigation Organizada por Secciones -->
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="logo-area">
        <i class="fa-solid fa-square-parking"></i> SmartPark
      </div>
      <ul class="nav-menu">
        <div class="nav-divider">Centro de Control</div>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-dashboard' }"
          @click.prevent="switchSection('sec-dashboard')"
        >
          <i class="fa-solid fa-chart-pie"></i> Resumen General
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-sedes' }"
          @click.prevent="switchSection('sec-sedes')"
        >
          <i class="fa-solid fa-warehouse"></i> Sedes y Mapa
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-propietarios' }"
          @click.prevent="switchSection('sec-propietarios')"
        >
          <i class="fa-solid fa-users-gear"></i> Propietarios
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-saas' }"
          @click.prevent="switchSection('sec-saas')"
        >
          <i class="fa-solid fa-box-open"></i> Planes & Suscripciones
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-pagos' }"
          @click.prevent="switchSection('sec-pagos')"
        >
          <i class="fa-solid fa-credit-card"></i> Pagos & Transacciones
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-reservas' }"
          @click.prevent="switchSection('sec-reservas')"
        >
          <i class="fa-solid fa-clock-rotate-left"></i> Reservas en Vivo
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-conductores' }"
          @click.prevent="switchSection('sec-conductores')"
        >
          <i class="fa-solid fa-users"></i> Conductores
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-incidencias' }"
          @click.prevent="switchSection('sec-incidencias')"
        >
          <i class="fa-solid fa-bell"></i> Incidencias
        </a>

        <a href="#" class="nav-item logout-btn" @click.prevent="logout">
          <i class="fa-solid fa-right-from-bracket"></i> Cerrar Sesión
        </a>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Toast Alert Notification -->
      <div
        v-if="toast.show"
        class="alert-toast"
        :style="{ background: toast.isError ? 'rgba(239, 68, 68, 0.95)' : 'rgba(16, 185, 129, 0.95)' }"
      >
        {{ toast.msg }}
      </div>

      <!-- Top Header -->
      <div class="top-header">
        <div class="greeting">
          <h1>{{ sectionTitles[currentSection]?.title || 'Centro de Control Global' }}</h1>
          <p>{{ sectionTitles[currentSection]?.sub || 'Monitoreo y métricas clave de SmartPark en tiempo real.' }}</p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <button @click="refreshAll" class="btn-action" title="Recargar datos">
            <i class="fa-solid fa-rotate" :class="{ 'fa-spin': isRefreshing }"></i> Actualizar
          </button>
          <button @click="themeStore.toggleTheme" class="theme-toggle-btn">
            <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
            <span>{{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}</span>
          </button>
        </div>
      </div>

      <!-- ================= SECCIÓN 1: RESUMEN GENERAL (DASHBOARD) ================= -->
      <section v-show="currentSection === 'sec-dashboard'" class="section-view active-section">
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
            <button @click="checkHealth" class="btn-action" style="padding: 4px 10px; font-size: 0.8rem;">
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
      </section>

      <!-- ================= SECCIÓN 2: GESTIÓN DE SEDES Y MAPA ================= -->
      <section v-show="currentSection === 'sec-sedes'" class="section-view active-section">
        <div class="two-cols">
          <!-- Mapa Global de Sedes -->
          <div class="card" style="display: flex; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-earth-americas"></i> Sedes Activas en Mapa</h2>
              <button @click="recenterGlobalMap" class="btn-action" title="Centrar en todas las sedes">
                <i class="fa-solid fa-crosshairs"></i> Centrar Mapa
              </button>
            </div>
            <div id="global-map"></div>
          </div>

          <!-- Form Registrar/Editar Sede -->
          <div class="card">
            <h2 class="card-title">
              <i class="fa-solid fa-hotel"></i>
              {{ formSede.id ? `Editar Sede #${formSede.id}` : 'Registrar Nueva Sede' }}
            </h2>
            <form @submit.prevent="handleSaveSede">
              <div class="form-group">
                <label>Propietario Dueño</label>
                <select v-model="formSede.propietario_id" required>
                  <option value="">-- Selecciona el Propietario --</option>
                  <option v-for="p in propietariosList.filter(x => x.activo)" :key="p.id" :value="p.id">
                    {{ p.nombre }} ({{ p.email }})
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Nombre de la Sede</label>
                <input v-model="formSede.nombre" type="text" required placeholder="Ej. SmartPark Central">
              </div>
              <div class="form-group">
                <label>Dirección</label>
                <input v-model="formSede.direccion" type="text" required placeholder="Jr. Asamblea 120">
              </div>
              <div class="form-group">
                <label>Tarifa por Hora (S/.)</label>
                <input v-model.number="formSede.tarifa_hora" type="number" step="0.5" required>
              </div>
              <div class="form-group">
                <label>Ubicación (Haz clic en el mapa para fijar coordenadas)</label>
                <div id="map-picker"></div>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div class="form-group">
                  <label>Latitud</label>
                  <input v-model.number="formSede.latitud" type="number" step="0.000001" required>
                </div>
                <div class="form-group">
                  <label>Longitud</label>
                  <input v-model.number="formSede.longitud" type="number" step="0.000001" required>
                </div>
              </div>
              <button type="submit" class="btn-submit" style="margin-top: 10px;">
                {{ formSede.id ? 'Guardar Cambios' : 'Crear Sede' }}
              </button>
              <button
                v-if="formSede.id"
                type="button"
                class="btn-secondary"
                style="margin-top:8px;"
                @click="cancelSedeEdit"
              >
                Cancelar Edición
              </button>
            </form>
          </div>
        </div>

        <!-- Tabla de Sedes Registradas con Buscador y Exportador -->
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-warehouse"></i> Listado General de Sedes</h2>
              <span class="status-badge libre">{{ sedesFiltradas.length }} sedes</span>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
              <input
                v-model="searchSedes"
                type="text"
                placeholder="Buscar por nombre o dirección..."
                style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 220px;"
              >
              <button @click="exportSedesExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
                <i class="fa-solid fa-file-excel"></i> Exportar Excel
              </button>
              <button @click="exportSedesCSV" class="btn-action" title="Exportar a CSV">
                <i class="fa-solid fa-file-csv"></i> Exportar CSV
              </button>
            </div>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre & Dirección</th>
                  <th>Propietario</th>
                  <th>Tarifa</th>
                  <th>Estado</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in sedesFiltradas" :key="s.id">
                  <td>#{{ s.id }}</td>
                  <td>
                    <strong>{{ s.nombre }}</strong><br>
                    <span style="font-size:0.75rem; color:#94a3b8;"><i class="fa-solid fa-location-dot"></i> {{ s.direccion }}</span>
                  </td>
                  <td>{{ getOwnerName(s.propietario_id) }}</td>
                  <td>S/. {{ (s.tarifa_hora || 5.0).toFixed(2) }}</td>
                  <td>
                    <span class="status-badge" :class="s.activa ? 'libre' : 'ocupado'">
                      {{ s.activa ? 'Operando' : 'Cerrada' }}
                    </span>
                  </td>
                  <td>
                    <button @click="zoomToSede(s)" class="btn-action" title="Ver en mapa"><i class="fa-solid fa-map-pin"></i></button>
                    <button @click="editSede(s)" class="btn-action" title="Editar"><i class="fa-solid fa-pen"></i></button>
                    <button
                      @click="toggleSedeEstado(s)"
                      class="btn-action"
                      :title="s.activa ? 'Desactivar' : 'Activar'"
                    >
                      <i class="fa-solid" :class="s.activa ? 'fa-pause' : 'fa-play'"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="sedesFiltradas.length === 0">
                  <td colspan="6" style="text-align: center; color: var(--text-muted);">No se encontraron sedes.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 3: PROPIETARIOS ================= -->
      <section v-show="currentSection === 'sec-propietarios'" class="section-view active-section">
        <!-- Header con Acciones y Contador -->
        <div class="card" style="padding: 20px 24px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
              <h2 class="card-title" style="margin-bottom: 4px;">
                <i class="fa-solid fa-users-gear" style="color:var(--primary);"></i> Control y Acceso de Propietarios
              </h2>
              <p style="font-size: 0.85rem; color: var(--text-muted);">
                Los propietarios se auto-registran al comprar un plan. Desde aquí puedes <strong>Dar de Baja / Bloquear acceso</strong> al sistema o modificar credenciales.
              </p>
            </div>
            <button
              @click="openModalPropietario(null)"
              class="btn-action"
              style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%); color: #fff; padding: 10px 16px; font-weight: 600; border-radius: 10px;"
            >
              <i class="fa-solid fa-user-plus"></i> Crear Propietario Manual
            </button>
          </div>
        </div>

        <!-- Tabla Principal de Propietarios -->
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <h3 style="font-size: 1rem; color: #e2e8f0;"><i class="fa-solid fa-address-book"></i> Directorio de Dueños de Parqueaderos</h3>
              <span class="status-badge libre">{{ propietariosFiltrados.length }} propietarios</span>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
              <input
                v-model="searchPropietarios"
                type="text"
                placeholder="Buscar por nombre o email..."
                style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 220px;"
              >
              <button @click="exportPropietariosExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
                <i class="fa-solid fa-file-excel"></i> Exportar Excel
              </button>
              <button @click="exportPropietariosCSV" class="btn-action" title="Exportar a CSV">
                <i class="fa-solid fa-file-csv"></i> Exportar CSV
              </button>
            </div>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Propietario & Contacto</th>
                  <th>Plan SaaS Asignado</th>
                  <th>Sedes Activas</th>
                  <th>Estado de Acceso</th>
                  <th>Acción Inmediata</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in propietariosFiltrados" :key="p.id">
                  <td>#{{ p.id }}</td>
                  <td>
                    <strong>{{ p.nombre }}</strong><br>
                    <span style="font-size:0.8rem; color:#94a3b8;"><i class="fa-solid fa-envelope"></i> {{ p.email }}</span>
                  </td>
                  <td>
                    <span v-if="getPlanNameForProp(p.id)" style="color:var(--accent); font-weight:600;">
                      <i class="fa-solid fa-gem"></i> {{ getPlanNameForProp(p.id) }}
                    </span>
                    <span v-else style="color:#94a3b8; font-size:0.8rem;">Sin Plan Activo</span>
                  </td>
                  <td><span style="font-weight:600;">{{ countSedesForProp(p.id) }}</span> sedes</td>
                  <td>
                    <span class="status-badge" :class="p.activo ? 'libre' : 'ocupado'">
                      <i class="fa-solid" :class="p.activo ? 'fa-check' : 'fa-ban'"></i>
                      {{ p.activo ? 'Activo' : 'Bloqueado' }}
                    </span>
                  </td>
                  <td>
                    <button
                      @click="togglePropietarioAcceso(p)"
                      class="btn-action"
                      :style="{ color: p.activo ? '#ef4444' : '#10b981' }"
                      :title="p.activo ? 'Dar de baja / Bloquear acceso' : 'Reactivar acceso'"
                    >
                      <i class="fa-solid" :class="p.activo ? 'fa-user-slash' : 'fa-user-check'"></i>
                      {{ p.activo ? 'Bloquear' : 'Desbloquear' }}
                    </button>
                    <button @click="openModalPropietario(p)" class="btn-action" title="Editar datos o clave">
                      <i class="fa-solid fa-key"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="propietariosFiltrados.length === 0">
                  <td colspan="6" style="text-align: center; color: var(--text-muted);">No hay propietarios registrados.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 4: PLANES SAAS Y SUSCRIPCIONES ================= -->
      <section v-show="currentSection === 'sec-saas'" class="section-view active-section">
        <div class="two-cols">
          <!-- Planes SaaS SmartPark -->
          <div class="card">
            <h2 class="card-title"><i class="fa-solid fa-box-open"></i> Planes SaaS SmartPark</h2>
            <div class="table-wrapper" style="max-height: 220px; margin-bottom: 20px;">
              <table>
                <thead>
                  <tr>
                    <th>Plan</th>
                    <th>Precio</th>
                    <th>Límites</th>
                    <th>Editar</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pl in planesList" :key="pl.id">
                    <td>
                      <strong>{{ pl.nombre }}</strong><br>
                      <span class="status-badge" :class="pl.activo ? 'libre' : 'ocupado'">{{ pl.activo ? 'Activo' : 'Inactivo' }}</span>
                    </td>
                    <td>S/. {{ Number(pl.precio).toFixed(2) }}</td>
                    <td><span style="font-size:0.75rem;">{{ pl.max_sedes }} sedes<br>{{ pl.max_operadores }} op.</span></td>
                    <td>
                      <button @click="editPlan(pl)" class="btn-action"><i class="fa-solid fa-pen"></i></button>
                    </td>
                  </tr>
                  <tr v-if="planesList.length === 0">
                    <td colspan="4" style="text-align: center; color: var(--text-muted);">Cargando planes...</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Form Crear/Editar Plan -->
            <form @submit.prevent="handleSavePlan" style="border-top: 1px solid var(--glass-border); padding-top: 15px;">
              <div class="form-group">
                <label>{{ formPlan.id ? `Editando Plan #${formPlan.id} - ${formPlan.nombre}` : 'Crear / Modificar Plan' }}</label>
                <input v-model="formPlan.nombre" type="text" placeholder="Nombre (ej. Plan Pro)" required>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
                <div class="form-group">
                  <label>Precio S/.</label>
                  <input v-model.number="formPlan.precio" type="number" step="0.01" required>
                </div>
                <div class="form-group">
                  <label>Max Sedes</label>
                  <input v-model.number="formPlan.max_sedes" type="number" required>
                </div>
                <div class="form-group">
                  <label>Max Op.</label>
                  <input v-model.number="formPlan.max_operadores" type="number" required>
                </div>
              </div>
              <div v-if="formPlan.id" class="form-group">
                <label>Estado</label>
                <select v-model="formPlan.activo">
                  <option :value="true">Activo</option>
                  <option :value="false">Inactivo</option>
                </select>
              </div>
              <button type="submit" class="btn-submit" style="margin-top: 10px;">
                {{ formPlan.id ? 'Actualizar Plan' : 'Guardar Plan' }}
              </button>
              <button
                v-if="formPlan.id"
                type="button"
                class="btn-secondary"
                style="margin-top:8px;"
                @click="cancelPlanEdit"
              >
                Cancelar
              </button>
            </form>
          </div>

          <!-- Suscripciones Activas con Control -->
          <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-file-invoice"></i> Membresías Activas</h2>
              <span class="status-badge libre">{{ activeSubsCount }} activas</span>
            </div>
            <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:12px;">
              Administra el cobro y estado comercial de cada cliente (Cancelar, Reactivar o Extender +30 días).
            </p>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Propietario</th>
                    <th>Plan</th>
                    <th>Vencimiento</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in suscripcionesUnicas" :key="s.id">
                    <td>
                      <strong>{{ getOwnerName(s.propietario_id) }}</strong><br>
                      <span style="font-size:0.75rem; color:var(--text-muted);">ID Propietario: #{{ s.propietario_id }}</span>
                    </td>
                    <td><strong>{{ getPlanName(s.plan_id) }}</strong></td>
                    <td><span style="font-size:0.85rem;">{{ formatearFecha(s.fecha_vencimiento) }}</span></td>
                    <td>
                      <span class="status-badge" :class="s.estado === 'activa' ? 'libre' : 'ocupado'">
                        {{ s.estado ? s.estado.toUpperCase() : 'INACTIVA' }}
                      </span>
                    </td>
                    <td>
                      <button
                        @click="abrirModalCambiarPlan(s.propietario_id, s.plan_id, getOwnerName(s.propietario_id))"
                        class="btn-action"
                        style="color:var(--accent);"
                        title="Cambiar Plan"
                      >
                        <i class="fa-solid fa-arrows-rotate"></i> Cambiar Plan
                      </button>
                      <button
                        @click="toggleSubscriptionEstado(s.id, 'activa', 30)"
                        class="btn-action"
                        title="Extender +30 días"
                      >
                        <i class="fa-solid fa-calendar-plus"></i> +30 días
                      </button>
                      <button
                        v-if="s.estado === 'activa'"
                        @click="toggleSubscriptionEstado(s.id, 'cancelada')"
                        class="btn-action"
                        style="color:#ef4444;"
                        title="Cancelar membresía"
                      >
                        <i class="fa-solid fa-ban"></i> Cancelar
                      </button>
                      <button
                        v-else
                        @click="toggleSubscriptionEstado(s.id, 'activa')"
                        class="btn-action"
                        style="color:#10b981;"
                        title="Reactivar membresía"
                      >
                        <i class="fa-solid fa-rotate-left"></i> Reactivar
                      </button>
                    </td>
                  </tr>
                  <tr v-if="suscripcionesUnicas.length === 0">
                    <td colspan="5" style="text-align: center; color: var(--text-muted);">Sin membresías registradas.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 5: PAGOS Y TRANSACCIONES ================= -->
      <section v-show="currentSection === 'sec-pagos'" class="section-view active-section">
        <!-- KPIs de Pagos -->
        <div class="stats-row" style="grid-template-columns: repeat(4, 1fr);">
          <div class="stat-box ingresos">
            <span class="stat-label">Total Transacciones</span>
            <span class="stat-value" style="color: var(--primary);">{{ pagosList.length }}</span>
          </div>
          <div class="stat-box libre">
            <span class="stat-label">Pagos Aprobados</span>
            <span class="stat-value" style="color: var(--color-libre);">{{ statsPagos.aprobados }}</span>
          </div>
          <div class="stat-box reservado">
            <span class="stat-label">Pagos Pendientes</span>
            <span class="stat-value" style="color: var(--color-reservado);">{{ statsPagos.pendientes }}</span>
          </div>
          <div class="stat-box sedes">
            <span class="stat-label">Monto Total Facturado</span>
            <span class="stat-value" style="color: var(--accent);">S/. {{ statsPagos.totalMonto.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Tabla de Pagos & Transacciones -->
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-receipt"></i> Historial Global de Transacciones</h2>
              <span class="status-badge libre">{{ pagosFiltrados.length }} pagos</span>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
              <input
                v-model="searchPagos"
                type="text"
                placeholder="Buscar por método o ID..."
                style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 220px;"
              >
              <button @click="exportPagosExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
                <i class="fa-solid fa-file-excel"></i> Exportar Excel
              </button>
              <button @click="exportPagosCSV" class="btn-action" title="Exportar a CSV">
                <i class="fa-solid fa-file-csv"></i> Exportar CSV
              </button>
              <button @click="loadPagosGlobales" class="btn-action"><i class="fa-solid fa-rotate"></i> Actualizar</button>
            </div>
          </div>
          <div class="table-wrapper" style="max-height: 480px;">
            <table>
              <thead>
                <tr>
                  <th>ID Transacción</th>
                  <th>Reserva Asociada</th>
                  <th>Monto</th>
                  <th>Método de Pago</th>
                  <th>Fecha y Hora</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in pagosFiltrados" :key="p.id">
                  <td><strong>#TX-{{ p.id }}</strong></td>
                  <td>
                    <span style="color:var(--text-muted);">{{ p.suscripcion_id ? "Suscripción" : "Reserva" }}</span>
                    <strong> #{{ p.suscripcion_id || p.reserva_id || "-" }}</strong>
                  </td>
                  <td><span style="color:#10b981; font-weight:700;">S/. {{ Number(p.monto || 0).toFixed(2) }}</span></td>
                  <td>
                    <span style="display:inline-flex; align-items:center; gap:6px; font-size:0.85rem; text-transform:capitalize;">
                      <i
                        class="fa-solid"
                        :class="p.metodo_pago === 'yape' || p.metodo_pago === 'plin' ? 'fa-mobile-screen-button' : (p.metodo_pago === 'efectivo' ? 'fa-money-bill-1' : 'fa-credit-card')"
                        style="color:var(--accent);"
                      ></i>
                      {{ p.metodo_pago || 'Tarjeta' }}
                    </span>
                  </td>
                  <td style="font-size:0.85rem; color:var(--text-muted);">{{ formatearFecha(p.fecha_creacion || p.fecha_pago) }}</td>
                  <td>
                    <span
                      class="status-badge"
                      :class="(p.estado === 'completado' || p.estado === 'aprobado' || p.estado === 'exitoso') ? 'libre' : (p.estado === 'fallido' || p.estado === 'cancelado' ? 'ocupado' : 'reservado')"
                    >
                      {{ p.estado ? p.estado.toUpperCase() : 'PENDIENTE' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="pagosFiltrados.length === 0">
                  <td colspan="6" style="text-align: center; color: var(--text-muted);">No hay transacciones registradas.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 6: RESERVAS EN VIVO ================= -->
      <section v-show="currentSection === 'sec-reservas'" class="section-view active-section">
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <h2 class="card-title" style="margin-bottom:0;"><i class="fa-solid fa-clock-rotate-left"></i> Historial y Reservas Globales en Vivo</h2>
              <span class="status-badge libre">{{ reservasFiltradas.length }} reservas</span>
            </div>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
              <select
                v-model="filtroReservaSede"
                style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 12px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; min-width: 170px;"
              >
                <option value="">🏢 Todos los Estacionamientos</option>
                <option v-for="s in sedesList" :key="s.id" :value="s.id">🏢 {{ s.nombre }}</option>
              </select>
              <select
                v-model="filtroReservaEstado"
                style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 12px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none;"
              >
                <option value="">Todos los Estados</option>
                <option value="confirmada">Confirmada</option>
                <option value="pendiente">Pendiente</option>
                <option value="cancelada">Cancelada</option>
                <option value="finalizada">Finalizada</option>
              </select>
              <input
                v-model="searchReservas"
                type="text"
                placeholder="Buscar por placa o ID..."
                style="background: rgba(15,23,42,0.6); border: 1px solid var(--glass-border); padding: 8px 14px; border-radius: 8px; color: var(--text-main); font-size: 0.85rem; outline: none; width: 180px;"
              >
              <button @click="exportReservasExcel" class="btn-action" title="Exportar a Microsoft Excel (.xlsx)" style="color:#10b981;">
                <i class="fa-solid fa-file-excel"></i> Exportar Excel
              </button>
              <button @click="exportReservasCSV" class="btn-action" title="Exportar a CSV">
                <i class="fa-solid fa-file-csv"></i> Exportar CSV
              </button>
              <button @click="loadReservasGlobales" class="btn-action"><i class="fa-solid fa-rotate"></i> Actualizar</button>
            </div>
          </div>
          <div class="table-wrapper" style="max-height: 500px;">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Estacionamiento / Sede</th>
                  <th>Espacio</th>
                  <th>Placa Vehículo</th>
                  <th>Fecha Inicio</th>
                  <th>Fecha Fin</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in reservasFiltradas" :key="r.id">
                  <td><strong>#{{ r.id }}</strong></td>
                  <td>
                    <strong style="color:var(--primary);"><i class="fa-solid fa-square-parking"></i> {{ r.sede_nombre }}</strong>
                  </td>
                  <td>
                    <span style="background:rgba(2,132,199,0.1); color:var(--accent); padding:2px 8px; border-radius:6px; font-weight:700;">
                      {{ r.espacio_numero }}
                    </span>
                  </td>
                  <td><strong style="letter-spacing:0.5px;">{{ r.placa_vehiculo || 'N/A' }}</strong></td>
                  <td><span style="font-size:0.82rem; color:var(--text-muted);">{{ formatearFecha(r.fecha_inicio) }}</span></td>
                  <td><span style="font-size:0.82rem; color:var(--text-muted);">{{ formatearFecha(r.fecha_fin) }}</span></td>
                  <td>
                    <span
                      class="status-badge"
                      :class="r.estado === 'confirmada' ? 'activa' : (r.estado === 'cancelada' ? 'cancelada' : 'reservado')"
                    >
                      {{ r.estado ? r.estado.toUpperCase() : 'CONFIRMADA' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="reservasFiltradas.length === 0">
                  <td colspan="7" style="text-align: center; color: var(--text-muted);">No se encontraron reservas con los filtros aplicados.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 7: CONDUCTORES ================= -->
      <section v-show="currentSection === 'sec-conductores'" class="section-view active-section">
        <div class="card">
          <h2 class="card-title"><i class="fa-solid fa-users"></i> Conductores Registrados</h2>
          <div class="table-wrapper" style="max-height: 500px;">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre Completo</th>
                  <th>Correo Electrónico</th>
                  <th>Estado de Cuenta</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in conductoresList" :key="c.id">
                  <td>#{{ c.id }}</td>
                  <td>{{ c.nombre }}</td>
                  <td>{{ c.email }}</td>
                  <td>
                    <span class="status-badge" :class="c.activo ? 'libre' : 'ocupado'">
                      {{ c.activo ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="conductoresList.length === 0">
                  <td colspan="4" style="text-align: center; color: var(--text-muted);">No hay conductores registrados.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 8: INCIDENCIAS ================= -->
      <section v-show="currentSection === 'sec-incidencias'" class="section-view active-section">
        <div class="card">
          <h2 class="card-title" style="color: #f87171;">
            <i class="fa-solid fa-bell"></i> Incidencias Reportadas por Operadores de Caseta
          </h2>
          <div style="max-height: 500px; overflow-y: auto;">
            <div v-for="inc in incidenciasList" :key="inc.id" class="incidencia-row">
              <div>
                <div style="font-weight: 600;">Sede #{{ inc.sede_id }} (Operador #{{ inc.operador_id }})</div>
                <div class="desc">{{ inc.descripcion }}</div>
              </div>
              <div class="date">{{ formatearFecha(inc.fecha_reporte) }}</div>
            </div>
            <p v-if="incidenciasList.length === 0" style="color: var(--text-muted); text-align: center; padding: 20px;">
              No hay incidencias recientes.
            </p>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Propietario (Crear / Editar) -->
    <div v-if="modalProp.open" class="modal-overlay">
      <div class="card modal-content" style="width: 440px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h2 class="card-title" style="margin-bottom:0;">
            <i class="fa-solid fa-user-plus"></i> {{ modalProp.id ? `Editar Propietario #${modalProp.id}` : 'Registrar Propietario' }}
          </h2>
          <button @click="modalProp.open = false" style="background:none; border:none; color:var(--text-muted); font-size:1.2rem; cursor:pointer;">&times;</button>
        </div>
        <form @submit.prevent="handleSavePropietario">
          <div class="form-group">
            <label>Nombre Completo</label>
            <input v-model="modalProp.nombre" type="text" required placeholder="Ej. Carlos Mendoza">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="modalProp.email" type="email" required placeholder="carlos@gmail.com">
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input v-model="modalProp.password" type="password" :placeholder="modalProp.id ? '(En blanco para mantener actual)' : 'Contraseña segura'">
          </div>
          <div v-if="modalProp.id" class="form-group">
            <label>Estado de Acceso</label>
            <select v-model="modalProp.activo">
              <option :value="true">Activo (Permitir Ingreso)</option>
              <option :value="false">Bloqueado (Denegar Ingreso)</option>
            </select>
          </div>
          <button type="submit" class="btn-submit" style="margin-top: 10px;">Guardar Propietario</button>
          <button type="button" class="btn-secondary" style="margin-top:8px;" @click="modalProp.open = false">Cancelar</button>
        </form>
      </div>
    </div>

    <!-- Modal Cambiar Plan de Membresía -->
    <div v-if="modalPlanAdmin.open" class="modal-overlay">
      <div class="card modal-content" style="width: 500px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid var(--glass-border); padding-bottom:12px;">
          <h3 style="font-size: 1.15rem; margin:0; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-arrows-rotate" style="color: var(--primary);"></i> Cambiar Plan de Membresía
          </h3>
          <button @click="modalPlanAdmin.open = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:14px;">
          Cambiando plan para <strong>{{ modalPlanAdmin.propNombre }}</strong> (Propietario #{{ modalPlanAdmin.propId }}). Su membresía actual quedará cancelada y la nueva se activará inmediatamente por 30 días.
        </p>

        <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:20px;">
          <div
            v-for="p in planesList"
            :key="p.id"
            @click="p.id !== modalPlanAdmin.currentPlanId ? modalPlanAdmin.selectedPlanId = p.id : null"
            :style="{
              padding: '14px 16px',
              borderRadius: '12px',
              border: `2px solid ${modalPlanAdmin.selectedPlanId === p.id ? 'var(--primary)' : 'var(--glass-border)'}`,
              background: modalPlanAdmin.selectedPlanId === p.id ? 'rgba(2, 132, 199, 0.12)' : (modalPlanAdmin.currentPlanId === p.id ? 'rgba(255, 255, 255, 0.02)' : 'rgba(15, 23, 42, 0.5)'),
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              cursor: p.id === modalPlanAdmin.currentPlanId ? 'not-allowed' : 'pointer',
              opacity: p.id === modalPlanAdmin.currentPlanId ? '0.6' : '1',
              transition: 'all 0.2s'
            }"
          >
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <strong :style="{ color: modalPlanAdmin.selectedPlanId === p.id ? 'var(--accent)' : 'var(--text-main)', fontSize: '1rem' }">{{ p.nombre }}</strong>
                <span v-if="p.id === modalPlanAdmin.currentPlanId" class="status-badge libre" style="font-size:0.65rem;">Actual</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">
                {{ p.max_sedes }} Sedes &bull; {{ p.max_operadores }} Operadores
              </div>
            </div>
            <div style="text-align:right;">
              <span style="font-size:1.1rem; font-weight:800; color:var(--text-main);">S/. {{ Number(p.precio).toFixed(2) }}</span>
              <span style="font-size:0.75rem; color:var(--text-muted);">/mes</span>
            </div>
          </div>
        </div>

        <div style="display:flex; justify-content:flex-end; gap:10px;">
          <button type="button" @click="modalPlanAdmin.open = false" class="btn-secondary" style="padding:10px 16px;">Cancelar</button>
          <button
            type="button"
            :disabled="!modalPlanAdmin.selectedPlanId || modalPlanAdmin.selectedPlanId === modalPlanAdmin.currentPlanId || modalPlanAdmin.saving"
            @click="confirmarCambioPlanAdmin"
            class="btn-submit"
            style="padding:10px 18px;"
          >
            <i class="fa-solid" :class="modalPlanAdmin.saving ? 'fa-spinner fa-spin' : 'fa-check'"></i>
            Confirmar Cambio
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { usuariosService } from '@/services/usuarios'
import { estacionamientosService } from '@/services/estacionamientos'
import { reservasService } from '@/services/reservas'
import { pagosService } from '@/services/pagos'
import L from 'leaflet'
import Chart from 'chart.js/auto'
import * as XLSX from 'xlsx'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// Sections
const currentSection = ref('sec-dashboard')
const sidebarOpen = ref(false)
const isRefreshing = ref(false)
const isCheckingHealth = ref(false)
const lastHealthCheckTime = ref('')

const sectionTitles = {
  'sec-dashboard': { title: 'Centro de Control Global', sub: 'Monitoreo y métricas clave de SmartPark en tiempo real.' },
  'sec-sedes': { title: 'Gestión de Sedes y Mapa', sub: 'Control geográfico y administración de tarifas por sede.' },
  'sec-propietarios': { title: 'Gestión de Propietarios', sub: 'Cuentas de propietarios y dueños de parqueaderos.' },
  'sec-saas': { title: 'Planes SaaS y Suscripciones', sub: 'Configuración de paquetes mensuales y membresías activas.' },
  'sec-pagos': { title: 'Pagos & Transacciones Globales', sub: 'Auditoría financiera y flujo de caja de todas las transacciones procesadas.' },
  'sec-reservas': { title: 'Reservas Globales en Vivo', sub: 'Supervisión en tiempo real de espacios y vehículos reservados.' },
  'sec-conductores': { title: 'Directorio de Conductores', sub: 'Usuarios finales registrados en la plataforma móvil y web.' },
  'sec-incidencias': { title: 'Reporte de Incidencias', sub: 'Alertas y sucesos reportados por operadores en caseta.' }
}

// Data Lists
const sedesList = ref([])
const propietariosList = ref([])
const conductoresList = ref([])
const reservasList = ref([])
const pagosList = ref([])
const planesList = ref([])
const suscripcionesList = ref([])
const incidenciasList = ref([])
const espaciosMap = ref({}) // id -> { sede_id, sede_nombre, numero }

// Metrics
const stats = reactive({ libres: 0, reservados: 0, ocupados: 0 })
const mrrTotal = ref(0)

// Filters
const searchSedes = ref('')
const searchPropietarios = ref('')
const searchPagos = ref('')
const searchReservas = ref('')
const filtroReservaSede = ref('')
const filtroReservaEstado = ref('')

// Toast Notification
const toast = reactive({ show: false, msg: '', isError: false })
let toastTimer = null
function showToast(msg, isError = false) {
  if (toastTimer) clearTimeout(toastTimer)
  toast.msg = msg
  toast.isError = isError
  toast.show = true
  toastTimer = setTimeout(() => { toast.show = false }, 3500)
}

// Health status
const healthStatus = reactive({
  usuarios: { ok: true, ms: 0 },
  estacionamientos: { ok: true, ms: 0 },
  reservas: { ok: true, ms: 0 },
  pagos: { ok: true, ms: 0 }
})

// Leaflet maps & chart instances
let globalMap = null
let globalMapMarkers = null
let pickerMap = null
let pickerMarker = null
let revenueChart = null
let healthInterval = null

// Form Sede
const formSede = reactive({
  id: null,
  propietario_id: '',
  nombre: '',
  direccion: '',
  tarifa_hora: 5.0,
  latitud: -13.157661,
  longitud: -74.227060
})

// Form Plan
const formPlan = reactive({
  id: null,
  nombre: '',
  precio: 0,
  max_sedes: 1,
  max_operadores: 2,
  activo: true
})

// Modal Propietario
const modalProp = reactive({
  open: false,
  id: null,
  nombre: '',
  email: '',
  password: '',
  activo: true
})

// Modal Cambiar Plan
const modalPlanAdmin = reactive({
  open: false,
  propId: null,
  currentPlanId: null,
  selectedPlanId: null,
  propNombre: '',
  saving: false
})

// Computed
const sedesFiltradas = computed(() => {
  if (!searchSedes.value.trim()) return sedesList.value
  const q = searchSedes.value.toLowerCase()
  return sedesList.value.filter(s =>
    (s.nombre && s.nombre.toLowerCase().includes(q)) ||
    (s.direccion && s.direccion.toLowerCase().includes(q))
  )
})

const propietariosFiltrados = computed(() => {
  if (!searchPropietarios.value.trim()) return propietariosList.value
  const q = searchPropietarios.value.toLowerCase()
  return propietariosList.value.filter(p =>
    (p.nombre && p.nombre.toLowerCase().includes(q)) ||
    (p.email && p.email.toLowerCase().includes(q))
  )
})

const pagosFiltrados = computed(() => {
  if (!searchPagos.value.trim()) return pagosList.value
  const q = searchPagos.value.toLowerCase()
  return pagosList.value.filter(p =>
    (`${p.id}`.includes(q)) ||
    (p.metodo_pago && p.metodo_pago.toLowerCase().includes(q)) ||
    (p.estado && p.estado.toLowerCase().includes(q))
  )
})

const statsPagos = computed(() => {
  let aprobados = 0
  let pendientes = 0
  let totalMonto = 0
  pagosList.value.forEach(p => {
    const m = parseFloat(p.monto) || 0
    totalMonto += m
    const st = (p.estado || '').toLowerCase()
    if (st === 'completado' || st === 'aprobado' || st === 'exitoso') {
      aprobados++
    } else {
      pendientes++
    }
  })
  return { aprobados, pendientes, totalMonto }
})

const reservasFiltradas = computed(() => {
  return reservasList.value.filter(r => {
    if (filtroReservaSede.value && r.sede_id !== parseInt(filtroReservaSede.value)) return false
    if (filtroReservaEstado.value && (r.estado || '').toLowerCase() !== filtroReservaEstado.value.toLowerCase()) return false
    if (searchReservas.value.trim()) {
      const q = searchReservas.value.toLowerCase().trim()
      const matchId = `${r.id}`.includes(q)
      const matchPlaca = (r.placa_vehiculo || '').toLowerCase().includes(q)
      const matchSede = (r.sede_nombre || '').toLowerCase().includes(q)
      const matchEspacio = (r.espacio_numero || '').toLowerCase().includes(q)
      if (!matchId && !matchPlaca && !matchSede && !matchEspacio) return false
    }
    return true
  })
})

const suscripcionesUnicas = computed(() => {
  const map = {}
  suscripcionesList.value.forEach(s => {
    const pid = s.propietario_id
    if (!map[pid]) {
      map[pid] = s
    } else if (map[pid].estado !== 'activa' && s.estado === 'activa') {
      map[pid] = s
    }
  })
  return Object.values(map)
})

const activeSubsCount = computed(() => {
  return suscripcionesUnicas.value.filter(s => s.estado === 'activa').length
})

// Methods
function switchSection(secId) {
  currentSection.value = secId
  sidebarOpen.value = false
  if (secId === 'sec-sedes') {
    nextTick(() => {
      setTimeout(() => {
        if (!globalMap || !pickerMap) {
          initMaps()
        }
        if (globalMap) {
          globalMap.invalidateSize()
          recenterGlobalMap()
        }
        if (pickerMap) {
          pickerMap.invalidateSize()
        }
      }, 120)
    })
  }
}

function getOwnerName(propId) {
  const p = propietariosList.value.find(x => x.id === propId)
  return p ? p.nombre : `Prop #${propId}`
}

function countSedesForProp(propId) {
  return sedesList.value.filter(s => s.propietario_id === propId).length
}

function getPlanNameForProp(propId) {
  const sub = suscripcionesList.value.find(s => s.propietario_id === propId && s.estado === 'activa')
  if (!sub) return null
  const plan = planesList.value.find(pl => pl.id === sub.plan_id)
  return plan ? plan.nombre : `Plan #${sub.plan_id}`
}

function getPlanName(planId) {
  const plan = planesList.value.find(pl => pl.id === planId)
  return plan ? plan.nombre : `Plan #${planId}`
}

function formatearFecha(dateStr) {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('es-PE', {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch (e) {
    return dateStr
  }
}

// Health check with latency measurement
async function checkHealth() {
  if (isCheckingHealth.value) return
  isCheckingHealth.value = true

  const ping = async (fn) => {
    const start = performance.now()
    try {
      await fn()
      const end = performance.now()
      return { ok: true, ms: Math.max(1, Math.round(end - start)) }
    } catch (err) {
      return { ok: false, ms: 0 }
    }
  }

  try {
    const [u, e, r, p] = await Promise.all([
      ping(() => usuariosService.health()),
      ping(() => estacionamientosService.health()),
      ping(() => reservasService.health()),
      ping(() => pagosService.health())
    ])

    healthStatus.usuarios.ok = u.ok
    healthStatus.usuarios.ms = u.ms

    healthStatus.estacionamientos.ok = e.ok
    healthStatus.estacionamientos.ms = e.ms

    healthStatus.reservas.ok = r.ok
    healthStatus.reservas.ms = r.ms

    healthStatus.pagos.ok = p.ok
    healthStatus.pagos.ms = p.ms

    lastHealthCheckTime.value = new Date().toLocaleTimeString()
  } catch (err) {
    console.error('Error health check:', err)
  } finally {
    isCheckingHealth.value = false
  }
}

// Data loaders
async function refreshAll() {
  isRefreshing.value = true
  try {
    await checkHealth()
    await Promise.all([
      loadPropietarios(),
      loadConductores(),
      loadSedesAndStats(),
      loadSaaS(),
      loadPagosGlobales(),
      loadIncidencias()
    ])
    await loadReservasGlobales()
    await renderRevenueChart()
  } finally {
    isRefreshing.value = false
  }
}

async function loadPropietarios() {
  try {
    const res = await usuariosService.getPropietarios()
    propietariosList.value = res.data || []
  } catch (err) {
    console.error('Error cargando propietarios:', err)
  }
}

async function loadConductores() {
  try {
    const res = await usuariosService.getUsuarios(0, 300)
    const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    conductoresList.value = list.filter(u => u.rol === 'conductor')
  } catch (err) {
    console.error('Error cargando conductores:', err)
  }
}

async function loadSedesAndStats() {
  try {
    const res = await estacionamientosService.getSedes(0, 200)
    sedesList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])

    // Contabilizar espacios de todas las sedes
    let lib = 0, resv = 0, ocu = 0
    for (const s of sedesList.value) {
      try {
        const espRes = await estacionamientosService.getEspaciosPorSede(s.id)
        const espacios = espRes.data || []
        espacios.forEach(e => {
          if (e.estado === 'libre') lib++
          else if (e.estado === 'reservado') resv++
          else if (e.estado === 'ocupado') ocu++
        })
      } catch (e) {}
    }
    stats.libres = lib
    stats.reservados = resv
    stats.ocupados = ocu

    updateGlobalMapMarkers()
  } catch (err) {
    console.error('Error cargando sedes:', err)
  }
}

async function loadReservasGlobales() {
  try {
    // Espacios Map
    if (Object.keys(espaciosMap.value).length === 0) {
      try {
        const espRes = await estacionamientosService.getEspacios(0, 500)
        const espList = Array.isArray(espRes.data) ? espRes.data : (espRes.data?.data || [])
        espList.forEach(esp => {
          const sedeObj = sedesList.value.find(s => s.id === esp.sede_id)
          espaciosMap.value[esp.id] = {
            sede_id: esp.sede_id,
            sede_nombre: sedeObj ? sedeObj.nombre : `Sede #${esp.sede_id}`,
            numero: esp.numero
          }
        })
      } catch (e) {}
    }

    const res = await reservasService.getReservas(0, 500)
    const rawList = Array.isArray(res.data) ? res.data : (res.data?.data || [])
    reservasList.value = rawList.map(r => {
      const info = espaciosMap.value[r.espacio_id] || {}
      return {
        ...r,
        sede_id: info.sede_id || null,
        sede_nombre: info.sede_nombre || 'Sede General',
        espacio_numero: info.numero || `#${r.espacio_id}`
      }
    })
  } catch (err) {
    console.error('Error cargando reservas:', err)
  }
}

async function loadPagosGlobales() {
  try {
    const res = await pagosService.getPagos(0, 500)
    pagosList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    console.error('Error cargando pagos:', err)
  }
}

async function loadSaaS() {
  try {
    const [pRes, sRes] = await Promise.all([
      usuariosService.getPlanes(),
      usuariosService.getSuscripcionesTodas()
    ])
    planesList.value = pRes.data || []
    suscripcionesList.value = sRes.data || []

    // Calculate MRR
    const pMap = {}
    planesList.value.forEach(p => { pMap[p.id] = p.precio })
    let m = 0
    suscripcionesList.value.forEach(s => {
      if (s.estado === 'activa') {
        m += (pMap[s.plan_id] || 0)
      }
    })
    mrrTotal.value = m
  } catch (err) {
    console.error('Error cargando SaaS:', err)
  }
}

async function loadIncidencias() {
  try {
    const res = await estacionamientosService.getIncidencias(0, 50)
    incidenciasList.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    console.error('Error incidencias:', err)
  }
}

// Map functions
function initMaps() {
  // Picker map
  const pickerEl = document.getElementById('map-picker')
  if (pickerEl && !pickerMap) {
    pickerMap = L.map('map-picker').setView([-13.157661, -74.227060], 14)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(pickerMap)
    pickerMarker = L.marker([-13.157661, -74.227060]).addTo(pickerMap)

    pickerMap.on('click', (e) => {
      formSede.latitud = parseFloat(e.latlng.lat.toFixed(6))
      formSede.longitud = parseFloat(e.latlng.lng.toFixed(6))
      pickerMarker.setLatLng(e.latlng)
    })
  }

  // Global map
  const globalEl = document.getElementById('global-map')
  if (globalEl && !globalMap) {
    globalMap = L.map('global-map').setView([-13.157661, -74.227060], 14)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OSM' }).addTo(globalMap)
    globalMapMarkers = L.layerGroup().addTo(globalMap)
    updateGlobalMapMarkers()
  }

  setTimeout(() => {
    if (globalMap) globalMap.invalidateSize()
    if (pickerMap) pickerMap.invalidateSize()
  }, 100)
}

function updateGlobalMapMarkers() {
  if (!globalMapMarkers) return
  globalMapMarkers.clearLayers()

  sedesList.value.forEach(s => {
    if (s.latitud && s.longitud) {
      const markerColor = s.activa ? '#10b981' : '#ef4444'
      const icon = L.divIcon({
        className: 'custom-map-pin',
        html: `<div style="background:${markerColor}; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:13px; box-shadow:0 0 12px ${markerColor}; border:2px solid #fff;"><i class="fa-solid fa-parking"></i></div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      })

      const marker = L.marker([s.latitud, s.longitud], { icon })
      marker.bindPopup(`
        <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:180px;">
          <h3 style="margin:0 0 4px 0; color:#0f172a; font-size:1rem;">${s.nombre}</h3>
          <p style="margin:0 0 6px 0; color:#64748b; font-size:0.8rem;"><i class="fa-solid fa-location-dot"></i> ${s.direccion}</p>
          <div style="font-size:0.82rem; font-weight:600; color:#0f172a; margin-bottom:8px;">
            Tarifa: S/. ${(s.tarifa_hora || 5.0).toFixed(2)}/hr
          </div>
          <div style="font-size:0.75rem; color:#475569; margin-bottom:8px;">Dueño: <strong>${getOwnerName(s.propietario_id)}</strong></div>
        </div>
      `)
      globalMapMarkers.addLayer(marker)
    }
  })
}

function recenterGlobalMap() {
  if (!globalMap || sedesList.value.length === 0) return
  const valid = sedesList.value.filter(s => s.latitud && s.longitud)
  if (valid.length === 0) return
  const bounds = L.latLngBounds(valid.map(s => [s.latitud, s.longitud]))
  globalMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 })
}

function zoomToSede(s) {
  if (globalMap && s.latitud && s.longitud) {
    switchSection('sec-sedes')
    setTimeout(() => {
      globalMap.setView([s.latitud, s.longitud], 17)
    }, 200)
  }
}

// Sedes Form actions
function editSede(s) {
  formSede.id = s.id
  formSede.nombre = s.nombre
  formSede.direccion = s.direccion
  formSede.tarifa_hora = s.tarifa_hora || 5.0
  formSede.propietario_id = s.propietario_id
  formSede.latitud = s.latitud
  formSede.longitud = s.longitud

  if (pickerMarker) {
    pickerMarker.setLatLng([s.latitud, s.longitud])
    pickerMap.setView([s.latitud, s.longitud], 15)
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelSedeEdit() {
  formSede.id = null
  formSede.nombre = ''
  formSede.direccion = ''
  formSede.tarifa_hora = 5.0
  formSede.propietario_id = ''
  formSede.latitud = -13.157661
  formSede.longitud = -74.227060
  if (pickerMarker) pickerMarker.setLatLng([-13.157661, -74.227060])
}

async function handleSaveSede() {
  try {
    const payload = {
      nombre: formSede.nombre,
      direccion: formSede.direccion,
      tarifa_hora: formSede.tarifa_hora,
      propietario_id: formSede.propietario_id,
      latitud: formSede.latitud,
      longitud: formSede.longitud
    }
    if (formSede.id) {
      await estacionamientosService.actualizarSede(formSede.id, payload)
      showToast('Sede actualizada correctamente')
    } else {
      await estacionamientosService.crearSede(payload)
      showToast('Sede registrada exitosamente')
    }
    cancelSedeEdit()
    await loadSedesAndStats()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar la sede', true)
  }
}

async function toggleSedeEstado(s) {
  try {
    await estacionamientosService.toggleEstadoSede(s.id, !s.activa)
    showToast(`Sede #${s.id} ${!s.activa ? 'activada' : 'desactivada'}`)
    await loadSedesAndStats()
  } catch (err) {
    showToast('Error al cambiar estado de la sede', true)
  }
}

// Propietarios actions
function openModalPropietario(p) {
  if (p) {
    modalProp.id = p.id
    modalProp.nombre = p.nombre
    modalProp.email = p.email
    modalProp.password = ''
    modalProp.activo = p.activo
  } else {
    modalProp.id = null
    modalProp.nombre = ''
    modalProp.email = ''
    modalProp.password = ''
    modalProp.activo = true
  }
  modalProp.open = true
}

async function handleSavePropietario() {
  try {
    const payload = {
      nombre: modalProp.nombre,
      email: modalProp.email
    }
    if (modalProp.password) payload.password = modalProp.password
    if (modalProp.id) {
      payload.activo = modalProp.activo
      await usuariosService.actualizarPropietario(modalProp.id, payload)
      showToast('Propietario actualizado')
    } else {
      if (!modalProp.password) {
        showToast('La contraseña es obligatoria', true)
        return
      }
      payload.rol = 'propietario'
      await usuariosService.crearPropietario(payload)
      showToast('Propietario registrado exitosamente')
    }
    modalProp.open = false
    await loadPropietarios()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar propietario', true)
  }
}

async function togglePropietarioAcceso(p) {
  try {
    await usuariosService.toggleActivoPropietario(p.id)
    showToast(`Acceso del propietario #${p.id} ${!p.activo ? 'activado' : 'bloqueado'}`)
    await loadPropietarios()
  } catch (err) {
    showToast('Error al cambiar acceso del propietario', true)
  }
}

// Plans & Subscriptions
function editPlan(pl) {
  formPlan.id = pl.id
  formPlan.nombre = pl.nombre
  formPlan.precio = pl.precio
  formPlan.max_sedes = pl.max_sedes
  formPlan.max_operadores = pl.max_operadores
  formPlan.activo = pl.activo
}

function cancelPlanEdit() {
  formPlan.id = null
  formPlan.nombre = ''
  formPlan.precio = 0
  formPlan.max_sedes = 1
  formPlan.max_operadores = 2
  formPlan.activo = true
}

async function handleSavePlan() {
  try {
    const payload = {
      nombre: formPlan.nombre,
      precio: formPlan.precio,
      max_sedes: formPlan.max_sedes,
      max_operadores: formPlan.max_operadores,
      activo: formPlan.activo
    }
    if (formPlan.id) {
      await usuariosService.actualizarPlan(formPlan.id, payload)
      showToast('Plan actualizado')
    } else {
      await usuariosService.crearPlan(payload)
      showToast('Plan creado exitosamente')
    }
    cancelPlanEdit()
    await loadSaaS()
    await renderRevenueChart()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar plan', true)
  }
}

async function toggleSubscriptionEstado(subId, nuevoEstado, extenderDias = null) {
  try {
    const payload = { estado: nuevoEstado }
    if (extenderDias) payload.extender_dias = extenderDias
    await usuariosService.actualizarSuscripcionEstado(subId, payload)
    showToast(extenderDias ? `Membresía #${subId} renovada +30 días` : `Membresía #${subId} cambiada a ${nuevoEstado}`)
    await loadSaaS()
    await renderRevenueChart()
    await loadPropietarios()
  } catch (err) {
    showToast('Error al actualizar membresía', true)
  }
}

function abrirModalCambiarPlan(propId, currentPlanId, propNombre) {
  modalPlanAdmin.propId = propId
  modalPlanAdmin.currentPlanId = currentPlanId
  modalPlanAdmin.selectedPlanId = null
  modalPlanAdmin.propNombre = propNombre
  modalPlanAdmin.open = true
}

async function confirmarCambioPlanAdmin() {
  if (!modalPlanAdmin.selectedPlanId || !modalPlanAdmin.propId) return
  modalPlanAdmin.saving = true
  try {
    await usuariosService.cambiarPlanMembresia({
      propietario_id: modalPlanAdmin.propId,
      nuevo_plan_id: modalPlanAdmin.selectedPlanId
    })
    showToast(`¡Plan del propietario #${modalPlanAdmin.propId} cambiado con éxito!`)
    modalPlanAdmin.open = false
    await loadSaaS()
    await renderRevenueChart()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al cambiar plan', true)
  } finally {
    modalPlanAdmin.saving = false
  }
}

// Chart
function renderRevenueChart() {
  const canvas = document.getElementById('revenueChart')
  if (!canvas) return
  if (revenueChart) revenueChart.destroy()

  const pMap = {}
  planesList.value.forEach(p => { pMap[p.id] = p.precio })

  const dailyRevenue = {}
  suscripcionesList.value.forEach(s => {
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
        data: data.length > 0 ? data : [mrrTotal.value],
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

// Excel & CSV Exports
function downloadExcel(filename, sheetName, headers, rows) {
  try {
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows])
    XLSX.utils.book_append_sheet(wb, ws, sheetName || 'Datos')
    XLSX.writeFile(wb, filename)
    showToast('Archivo Excel (.xlsx) generado exitosamente')
  } catch (err) {
    downloadCSV(filename.replace(/\.xlsx$/i, '.csv'), [headers, ...rows])
  }
}

function downloadCSV(filename, rows) {
  const processRow = (row) => row.map(val => `"${(val || '').toString().replace(/"/g, '""')}"`).join(',')
  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + rows.map(processRow).join('\r\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showToast('Archivo CSV exportado exitosamente')
}

function exportSedesExcel() {
  if (sedesList.value.length === 0) return showToast('No hay sedes para exportar', true)
  const headers = ['ID', 'Nombre', 'Dirección', 'Tarifa_Hora', 'Latitud', 'Longitud', 'Propietario_ID', 'Estado']
  const data = sedesList.value.map(s => [
    s.id, s.nombre, s.direccion, s.tarifa_hora || 5.0, s.latitud, s.longitud, s.propietario_id, s.activa ? 'Activa' : 'Inactiva'
  ])
  downloadExcel(`SmartPark_Sedes_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Sedes', headers, data)
}

function exportSedesCSV() {
  if (sedesList.value.length === 0) return showToast('No hay sedes para exportar', true)
  const headers = ['ID', 'Nombre', 'Dirección', 'Tarifa_Hora', 'Latitud', 'Longitud', 'Propietario_ID', 'Estado']
  const data = sedesList.value.map(s => [
    s.id, s.nombre, s.direccion, s.tarifa_hora || 5.0, s.latitud, s.longitud, s.propietario_id, s.activa ? 'Activa' : 'Inactiva'
  ])
  downloadCSV(`SmartPark_Sedes_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}

function exportPropietariosExcel() {
  if (propietariosList.value.length === 0) return showToast('No hay propietarios para exportar', true)
  const headers = ['ID', 'Nombre', 'Email', 'Estado_Cuenta']
  const data = propietariosList.value.map(p => [
    p.id, p.nombre, p.email, p.activo ? 'Activo' : 'Bloqueado'
  ])
  downloadExcel(`SmartPark_Propietarios_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Propietarios', headers, data)
}

function exportPropietariosCSV() {
  if (propietariosList.value.length === 0) return showToast('No hay propietarios para exportar', true)
  const headers = ['ID', 'Nombre', 'Email', 'Estado_Cuenta']
  const data = propietariosList.value.map(p => [
    p.id, p.nombre, p.email, p.activo ? 'Activo' : 'Bloqueado'
  ])
  downloadCSV(`SmartPark_Propietarios_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}

function exportReservasExcel() {
  if (reservasFiltradas.value.length === 0) return showToast('Sin reservas para exportar', true)
  const headers = ['ID_Reserva', 'Estacionamiento', 'Espacio', 'Placa_Vehiculo', 'Fecha_Inicio', 'Fecha_Fin', 'Estado']
  const data = reservasFiltradas.value.map(r => [
    r.id, r.sede_nombre || 'Sede General', r.espacio_numero || `#${r.espacio_id}`, r.placa_vehiculo || 'N/A',
    r.fecha_inicio ? r.fecha_inicio.replace('T', ' ').slice(0, 19) : '',
    r.fecha_fin ? r.fecha_fin.replace('T', ' ').slice(0, 19) : '',
    (r.estado || '').toUpperCase()
  ])
  downloadExcel(`SmartPark_Reservas_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Reservas', headers, data)
}

function exportReservasCSV() {
  if (reservasFiltradas.value.length === 0) return showToast('Sin reservas para exportar', true)
  const headers = ['ID_Reserva', 'Estacionamiento', 'Espacio', 'Placa_Vehiculo', 'Fecha_Inicio', 'Fecha_Fin', 'Estado']
  const data = reservasFiltradas.value.map(r => [
    r.id, r.sede_nombre || 'Sede General', r.espacio_numero || `#${r.espacio_id}`, r.placa_vehiculo || 'N/A',
    r.fecha_inicio ? r.fecha_inicio.replace('T', ' ').slice(0, 19) : '',
    r.fecha_fin ? r.fecha_fin.replace('T', ' ').slice(0, 19) : '',
    (r.estado || '').toUpperCase()
  ])
  downloadCSV(`SmartPark_Reservas_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}

function exportPagosExcel() {
  if (pagosList.value.length === 0) return showToast('No hay transacciones para exportar', true)
  const headers = ['ID_Transaccion', 'Reserva_ID', 'Monto', 'Metodo_Pago', 'Fecha_Pago', 'Estado']
  const data = pagosList.value.map(p => [
    p.id, p.reserva_id || p.suscripcion_id, parseFloat(p.monto) || 0, p.metodo_pago || 'tarjeta',
    p.fecha_creacion || p.fecha_pago || '', p.estado || 'pendiente'
  ])
  downloadExcel(`SmartPark_Transacciones_${new Date().toISOString().slice(0, 10)}.xlsx`, 'Transacciones', headers, data)
}

function exportPagosCSV() {
  if (pagosList.value.length === 0) return showToast('No hay transacciones para exportar', true)
  const headers = ['ID_Transaccion', 'Reserva_ID', 'Monto', 'Metodo_Pago', 'Fecha_Pago', 'Estado']
  const data = pagosList.value.map(p => [
    p.id, p.reserva_id || p.suscripcion_id, p.monto, p.metodo_pago || 'tarjeta',
    p.fecha_creacion || p.fecha_pago || '', p.estado || 'pendiente'
  ])
  downloadCSV(`SmartPark_Transacciones_${new Date().toISOString().slice(0, 10)}.csv`, [headers, ...data])
}

function logout() {
  authStore.logout()
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('user_info')
  router.push('/login')
}

onMounted(async () => {
  themeStore.initTheme(true)
  nextTick(() => initMaps())
  await refreshAll()
  healthInterval = setInterval(checkHealth, 30000)
})

onUnmounted(() => {
  if (healthInterval) clearInterval(healthInterval)
  if (revenueChart) revenueChart.destroy()
  if (globalMap) globalMap.remove()
  if (pickerMap) pickerMap.remove()
})
</script>

<style scoped>
.admin-app-root {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-color, #0b0f19);
  background-image: radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.1) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.08) 0px, transparent 50%);
  color: var(--text-main, #f8fafc);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

:deep(.leaflet-layer), :deep(.leaflet-control-zoom-in), :deep(.leaflet-control-zoom-out), :deep(.leaflet-control-attribution) {
  filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);
}

.admin-app-root.light-mode :deep(.leaflet-layer),
.admin-app-root.light-mode :deep(.leaflet-control-zoom-in),
.admin-app-root.light-mode :deep(.leaflet-control-zoom-out),
.admin-app-root.light-mode :deep(.leaflet-control-attribution) {
  filter: none;
}

.admin-app-root {
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

.admin-app-root.light-mode {
  --bg-color: #f8fafc;
  --sidebar-bg: rgba(255, 255, 255, 0.95);
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0;
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #0284c7;
  --text-main: #0f172a;
  --text-muted: #64748b;
  background-image: radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.05) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(2, 132, 199, 0.03) 0px, transparent 50%);
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
  transition: transform 0.3s ease;
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
  padding: 30px 40px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.top-header { display: flex; justify-content: space-between; align-items: center; }
.greeting h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
.greeting p { color: var(--text-muted); font-size: 0.95rem; }

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
  transition: all 0.3s ease;
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

/* Stats 6 items */
.stats-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; }
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
.stat-box.ingresos { border-bottom: 3px solid var(--primary); }
.stat-box.sedes { border-bottom: 3px solid var(--accent); }
.stat-box.reservas-count { border-bottom: 3px solid #ec4899; }
.stat-label { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
.stat-value { font-size: 1.7rem; font-weight: 800; }

/* Health Service Status Badges */
.health-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.health-item {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--glass-border);
  padding: 14px 18px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}
.health-info { display: flex; flex-direction: column; gap: 3px; }
.health-name { font-weight: 600; display: flex; align-items: center; gap: 8px; }
.health-meta { font-size: 0.75rem; color: var(--text-muted); }

.health-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}
.health-status-badge.online {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.health-status-badge.offline {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.health-dot.online {
  background: var(--color-libre);
  box-shadow: 0 0 8px var(--color-libre);
}
.health-dot.offline {
  background: var(--color-ocupado);
  box-shadow: 0 0 8px var(--color-ocupado);
}

/* Forms & Buttons */
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
.form-group input:focus, .form-group select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}
.btn-submit {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}
.btn-submit:hover { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(2, 132, 199, 0.5); }
.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-main);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  padding: 12px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
}
.btn-secondary:hover { background: rgba(255, 255, 255, 0.15); }

#map-picker { 
  width: 100%; 
  height: 210px; 
  min-height: 210px; 
  border-radius: 12px; 
  border: 1px solid var(--glass-border); 
  margin-bottom: 6px; 
  position: relative;
  z-index: 1;
}

#global-map { 
  width: 100%; 
  height: 440px; 
  min-height: 440px; 
  border-radius: 14px; 
  border: 1px solid var(--glass-border); 
  position: relative;
  z-index: 1;
}

:deep(.leaflet-pane img),
:deep(.leaflet-tile),
:deep(.leaflet-marker-icon),
:deep(.leaflet-marker-shadow) {
  max-width: none !important;
  max-height: none !important;
}

:deep(.leaflet-container) {
  font-family: 'Plus Jakarta Sans', sans-serif;
  width: 100% !important;
  height: 100% !important;
}


/* Tables */
.table-wrapper { overflow-x: auto; overflow-y: auto; max-height: 400px; margin-top: 10px; border-radius: 10px; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th {
  padding: 12px 14px;
  font-size: 0.78rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 600;
  border-bottom: 1px solid var(--glass-border);
  position: sticky;
  top: 0;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(5px);
  z-index: 2;
}
td {
  padding: 12px 14px;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  color: #e2e8f0;
}
.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; display: inline-block; }
.status-badge.libre { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.ocupado { background: rgba(239, 68, 68, 0.15); color: #f87171; }
.status-badge.reservado { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.status-badge.activa { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.cancelada { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.btn-action {
  background: rgba(255,255,255,0.08);
  border: 1px solid var(--glass-border);
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.btn-action:hover { background: rgba(255,255,255,0.18); transform: translateY(-1px); }

/* Toast */
.alert-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  color: #fff;
  padding: 14px 20px;
  border-radius: 12px;
  font-weight: 500;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  animation: slideIn 0.3s ease forwards;
}
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

.incidencia-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(239, 68, 68, 0.08);
  border-left: 3px solid #ef4444;
  border-radius: 8px;
  margin-bottom: 8px;
}
.incidencia-row .date { font-size: 0.75rem; color: #94a3b8; }
.incidencia-row .desc { font-size: 0.9rem; margin-top: 2px; }

.two-cols { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; }

/* Modal overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(6px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  max-width: 92%;
  position: relative;
}

/* Mobile Bar */
.mobile-bar {
  display: none;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--sidebar-bg);
  border-bottom: 1px solid var(--glass-border);
  width: 100%;
}
.mobile-bar .toggle-btn {
  background: none;
  border: none;
  color: var(--text-main);
  font-size: 1.4rem;
  cursor: pointer;
}

/* Light mode overrides */
.admin-app-root.light-mode .nav-item { color: #64748b; }
.admin-app-root.light-mode .nav-item:hover { background: #f1f5f9; color: #0f172a; }
.admin-app-root.light-mode .card {
  background: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05);
}
.admin-app-root.light-mode .card-title, 
.admin-app-root.light-mode td,
.admin-app-root.light-mode h1,
.admin-app-root.light-mode h2,
.admin-app-root.light-mode h3 { color: #0f172a !important; }
.admin-app-root.light-mode th {
  background: #f8fafc;
  color: #64748b;
  border-bottom-color: #e2e8f0;
}
.admin-app-root.light-mode td { border-bottom-color: #f1f5f9; }
.admin-app-root.light-mode .form-group input, 
.admin-app-root.light-mode .form-group select,
.admin-app-root.light-mode input[type="text"],
.admin-app-root.light-mode input[type="email"],
.admin-app-root.light-mode input[type="password"],
.admin-app-root.light-mode input[type="number"],
.admin-app-root.light-mode select {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: #cbd5e1 !important;
}
.admin-app-root.light-mode input::placeholder {
  color: #94a3b8 !important;
}
.admin-app-root.light-mode .stat-box { background: #ffffff; border: 1px solid #e2e8f0; }
.admin-app-root.light-mode .health-item { background: #ffffff; border-color: #e2e8f0; }
.admin-app-root.light-mode .btn-action {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.admin-app-root.light-mode .btn-action:hover { background: #e2e8f0; }
.admin-app-root.light-mode .btn-secondary {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.admin-app-root.light-mode .btn-secondary:hover { background: #e2e8f0; }
.admin-app-root.light-mode .theme-toggle-btn {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.admin-app-root.light-mode .theme-toggle-btn:hover { background: #e2e8f0; }
.admin-app-root.light-mode .incidencia-row { background: rgba(239, 68, 68, 0.05); }


@media (max-width: 1200px) {
  .stats-row { grid-template-columns: repeat(3, 1fr); }
  .health-grid { grid-template-columns: repeat(2, 1fr); }
  .two-cols { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .admin-app-root { flex-direction: column; height: auto; overflow: auto; }
  .mobile-bar { display: flex; }
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 260px;
    transform: translateX(-100%);
    box-shadow: 5px 0 25px rgba(0,0,0,0.5);
  }
  .sidebar.open { transform: translateX(0); }
  .main-content { padding: 20px 15px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .top-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .health-grid { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  .stats-row { grid-template-columns: 1fr; }
  .stat-value { font-size: 1.5rem; }
}
</style>
