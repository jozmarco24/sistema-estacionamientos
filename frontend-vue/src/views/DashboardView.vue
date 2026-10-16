<template>
  <div class="dashboard-app-root" :class="{ 'light-mode': themeStore.isLight }">
    <!-- Sidebar Navegación Conductor -->
    <aside class="sidebar" id="sidebar">
      <div class="logo-area">
        <i class="fa-solid fa-square-parking"></i> SmartPark
      </div>
      <ul class="nav-menu">
        <router-link
          v-if="authStore.user?.rol === 'admin'"
          to="/admin"
          class="nav-item back-admin-btn"
        >
          <i class="fa-solid fa-arrow-left"></i> Volver a Admin
        </router-link>

        <div class="nav-divider">Servicios al Conductor</div>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-mapa' }"
          @click.prevent="switchSection('sec-mapa')"
        >
          <i class="fa-solid fa-map-location-dot"></i> Sedes en Mapa
        </a>
        <a
          href="#"
          class="nav-item"
          :class="{ active: currentSection === 'sec-mis-reservas' }"
          @click.prevent="switchSection('sec-mis-reservas')"
        >
          <i class="fa-solid fa-ticket-simple"></i> Mis Reservas & QR
        </a>
        <router-link to="/vehiculos" class="nav-item">
          <i class="fa-solid fa-car"></i> Mis Vehículos
        </router-link>

        <a href="#" class="nav-item logout-btn" @click.prevent="logout">
          <i class="fa-solid fa-right-from-bracket"></i> Salir
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

      <div class="top-header">
        <div class="greeting">
          <h1>{{ currentSection === 'sec-mapa' ? 'Sedes & Disponibilidad' : 'Mis Reservas & Pases Digitales' }}</h1>
          <p>{{ currentSection === 'sec-mapa' ? 'Calculando distancias en tiempo real desde tu ubicación.' : 'Consulta tus tickets QR para ingresar a la caseta.' }}</p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <button @click="obtenerUbicacionYRecalcular" class="btn-action" title="Actualizar ubicación y sedes">
            <i class="fa-solid fa-location-crosshairs" :class="{ 'fa-spin': isLocating }"></i> Recalcular GPS
          </button>
          <button @click="themeStore.toggleTheme" class="theme-toggle-btn">
            <i :class="themeStore.isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun'"></i>
            <span>{{ themeStore.isLight ? 'Modo Oscuro' : 'Modo Claro' }}</span>
          </button>
        </div>
      </div>

      <!-- ================= SECCIÓN 1: SEDES Y MAPA CON CÁLCULO DE DISTANCIA ================= -->
      <section v-show="currentSection === 'sec-mapa'" class="section-view active-section">
        <div class="map-layout">
          <!-- Lista de Sedes con Distancia Exacta -->
          <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
              <span style="font-weight:700; font-size:1.05rem;">
                <i class="fa-solid fa-compass" style="color:var(--accent);"></i> Sedes Cercanas
              </span>
              <span class="distancia-badge">{{ sedesList.length }} disponibles</span>
            </div>
            <div style="margin-bottom:12px;">
              <input
                v-model="searchSedesInput"
                type="text"
                placeholder="Buscar sede o dirección..."
                style="width:100%; background:rgba(15,23,42,0.6); border:1px solid var(--glass-border); padding:8px 12px; border-radius:10px; color:var(--text-main); font-size:0.85rem; outline:none;"
              >
            </div>
            <div class="sede-list">
              <div
                v-for="s in sedesFiltradas"
                :key="s.id"
                class="sede-card"
                @click="trazarRuta(s.latitud, s.longitud, s.nombre)"
              >
                <div class="sede-name">{{ s.nombre }}</div>
                <div class="sede-address"><i class="fa-solid fa-map-pin"></i> {{ s.direccion }}</div>
                <div class="sede-badges">
                  <span class="distancia-badge"><i class="fa-solid fa-route"></i> {{ s.distancia_km }} km</span>
                  <span style="font-size:0.75rem; color:#f59e0b; font-weight:700;">
                    <i class="fa-solid fa-clock"></i> ~{{ Math.max(2, Math.round(s.distancia_km * 2.8)) }} min
                  </span>
                  <span class="tarifa-badge">S/. {{ (s.tarifa_hora || 5.0).toFixed(2) }} / h</span>
                </div>
                <div style="margin-top:10px; display:flex; gap:8px; justify-content:flex-end;">
                  <button
                    class="btn-ruta"
                    @click.stop="trazarRuta(s.latitud, s.longitud, s.nombre)"
                  >
                    <i class="fa-solid fa-diamond-turn-right"></i> ¿Cómo llegar?
                  </button>
                  <router-link
                    :to="`/reserva?sede_id=${s.id}`"
                    class="btn-reserve-quick"
                    @click.stop
                  >
                    <i class="fa-solid fa-calendar-check"></i> Reservar
                  </router-link>
                </div>
              </div>
              <p v-if="sedesFiltradas.length === 0" style="color:var(--text-muted); font-size:0.85rem; text-align:center; padding:20px;">
                No se encontraron sedes cercanas.
              </p>
            </div>
          </div>

          <!-- Mapa Leaflet Interactivo -->
          <div class="card" style="padding:10px; position:relative;">
            <!-- Route info banner -->
            <div v-show="routeBanner.show" class="route-info-banner">
              <div class="route-info-title">
                <span><i class="fa-solid fa-diamond-turn-right" style="color:var(--accent);"></i> Hacia: {{ routeBanner.destName }}</span>
                <button @click="limpiarRuta" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.1rem;">&times;</button>
              </div>
              <div class="route-metrics">
                <div class="route-metric-pill">
                  <i class="fa-solid fa-clock" style="color:#f59e0b;"></i>
                  <span>{{ routeBanner.timeText }}</span>
                </div>
                <div class="route-metric-pill">
                  <i class="fa-solid fa-route" style="color:var(--accent);"></i>
                  <span>{{ routeBanner.distText }}</span>
                </div>
              </div>
              <div style="font-size:0.75rem; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center;">
                <span>Cálculo vial en tiempo real</span>
                <a :href="routeBanner.gmapsUrl" target="_blank" style="color:var(--primary); text-decoration:none; font-weight:600;">
                  Abrir en Google Maps <i class="fa-solid fa-external-link"></i>
                </a>
              </div>
            </div>

            <div id="map-dashboard"></div>
          </div>
        </div>
      </section>

      <!-- ================= SECCIÓN 2: MIS RESERVAS & TICKETS QR ================= -->
      <section v-show="currentSection === 'sec-mis-reservas'" class="section-view active-section">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <div>
              <h2 style="font-size:1.15rem; font-weight:700;"><i class="fa-solid fa-ticket-simple" style="color:var(--primary);"></i> Mis Reservas Activas e Historial</h2>
              <p style="font-size:0.85rem; color:var(--text-muted);">Muestra tu ticket QR en la caseta para que el operador te dé ingreso inmediato.</p>
            </div>
            <button @click="fetchMisReservas" class="btn-action"><i class="fa-solid fa-rotate"></i> Actualizar</button>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID Reserva</th>
                  <th>Placa</th>
                  <th>Fecha Inicio</th>
                  <th>Estado</th>
                  <th>Ticket / Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in reservasUsuario" :key="r.id">
                  <td><strong>#R-{{ r.id }}</strong></td>
                  <td>
                    <strong style="color:var(--accent);"><i class="fa-solid fa-car"></i> {{ r.placa_vehiculo || 'N/A' }}</strong>
                  </td>
                  <td style="font-size:0.85rem; color:var(--text-muted);">{{ formatearFecha(r.fecha_inicio) }}</td>
                  <td>
                    <span
                      class="status-badge"
                      :class="r.estado === 'confirmada' ? 'reservado' : (r.estado === 'cancelada' ? 'ocupado' : 'libre')"
                    >
                      {{ r.estado ? r.estado.toUpperCase() : 'ACTIVA' }}
                    </span>
                  </td>
                  <td>
                    <div style="display:flex; gap:6px;">
                      <button @click="mostrarTicketQR(r)" class="btn-action" style="color:var(--accent);" title="Ver Ticket QR">
                        <i class="fa-solid fa-qrcode"></i> Ver QR
                      </button>
                      <button
                        v-if="r.estado === 'confirmada' || r.estado === 'pendiente'"
                        @click="cancelarReservaCliente(r.id)"
                        class="btn-action"
                        style="color:#ef4444;"
                        title="Cancelar Reserva"
                      >
                        <i class="fa-solid fa-ban"></i> Cancelar
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="reservasUsuario.length === 0">
                  <td colspan="5" style="text-align: center; color: var(--text-muted);">
                    No tienes reservas registradas. ¡Reserva tu primer espacio en el mapa!
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Ver Ticket QR -->
    <div v-if="modalQR.open" class="modal-overlay">
      <div class="modal-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid var(--glass-border); padding-bottom:10px;">
          <h3 style="font-size:1.15rem; color:var(--text-main); display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-qrcode" style="color:var(--accent);"></i> Pase de Ingreso Digital
          </h3>
          <button @click="modalQR.open = false" style="background:none; border:none; color:var(--text-muted); font-size:1.3rem; cursor:pointer;">&times;</button>
        </div>
        <div style="background:#fff; padding:16px; border-radius:14px; display:inline-block; margin-bottom:14px;">
          <img :src="modalQR.imgUrl" alt="Ticket QR" style="width:180px; height:180px; display:block;">
        </div>
        <div style="margin-bottom:16px;">
          <h4 style="font-size:1.2rem; color:var(--primary); font-weight:800;">RESERVA #R-{{ modalQR.reservaId }}</h4>
          <p style="font-size:1rem; font-weight:700; color:var(--text-main);">PLACA: {{ modalQR.placa }}</p>
          <p style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">Muestra este código al llegar a la caseta del operador.</p>
        </div>
        <button @click="modalQR.open = false" class="btn-action" style="width:100%; justify-content:center;">Entendido</button>
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
import { reservasService } from '@/services/reservas'
import L from 'leaflet'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const currentSection = ref('sec-mapa')
const isLocating = ref(false)
const searchSedesInput = ref('')
const sedesList = ref([])
const reservasUsuario = ref([])

// User GPS Location (Default Lima Centro)
const userLocation = reactive({ lat: -12.046374, lon: -77.042793 })

// Leaflet
let map = null
let userMarker = null
let markersLayer = null
let activeRouteLayer = null

// Route Banner
const routeBanner = reactive({
  show: false,
  destName: '',
  timeText: '-- min',
  distText: '-- km',
  gmapsUrl: '#'
})

// QR Modal
const modalQR = reactive({
  open: false,
  reservaId: null,
  placa: '',
  imgUrl: ''
})

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

function calcularDistanciaKm(lat1, lon1, lat2, lon2) {
  const R = 6371.0
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return parseFloat((R * c).toFixed(2))
}

const sedesFiltradas = computed(() => {
  if (!searchSedesInput.value.trim()) return sedesList.value
  const q = searchSedesInput.value.toLowerCase().trim()
  return sedesList.value.filter(s =>
    (s.nombre && s.nombre.toLowerCase().includes(q)) ||
    (s.direccion && s.direccion.toLowerCase().includes(q))
  )
})

function switchSection(secId) {
  currentSection.value = secId
  if (secId === 'sec-mapa') {
    nextTick(() => {
      if (map) {
        setTimeout(() => map.invalidateSize(), 150)
      }
    })
  } else if (secId === 'sec-mis-reservas') {
    fetchMisReservas()
  }
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

function initMap() {
  const mapEl = document.getElementById('map-dashboard')
  if (!mapEl || map) return

  map = L.map('map-dashboard').setView([userLocation.lat, userLocation.lon], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(map)

  markersLayer = L.layerGroup().addTo(map)
  actualizarPosicionUsuario()
}

function actualizarPosicionUsuario() {
  if (!map) return
  if (userMarker) map.removeLayer(userMarker)

  const userIcon = L.divIcon({
    html: `<div style="background-color: #06b6d4; width: 14px; height: 14px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 12px #06b6d4;"></div>`,
    className: 'user-marker',
    iconSize: [20, 20]
  })
  userMarker = L.marker([userLocation.lat, userLocation.lon], { icon: userIcon }).addTo(map)
    .bindPopup('<b style="color:#06b6d4;"><i class="fa-solid fa-street-view"></i> Tu Ubicación Actual</b>')
}

function obtenerUbicacionYRecalcular() {
  isLocating.value = true
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLocation.lat = pos.coords.latitude
        userLocation.lon = pos.coords.longitude
        isLocating.value = false
        actualizarPosicionUsuario()
        fetchSedesCercanas()
      },
      (err) => {
        console.warn("GPS no disponible, usando coordenadas por defecto.")
        isLocating.value = false
        actualizarPosicionUsuario()
        fetchSedesCercanas()
      },
      { timeout: 7000 }
    )
  } else {
    isLocating.value = false
    actualizarPosicionUsuario()
    fetchSedesCercanas()
  }
}

async function fetchSedesCercanas() {
  try {
    const res = await estacionamientosService.getSedesCercanas(userLocation.lat, userLocation.lon)
    const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])

    list.forEach(s => {
      if (s.distancia_km === undefined || s.distancia_km === null) {
        s.distancia_km = calcularDistanciaKm(userLocation.lat, userLocation.lon, s.latitud, s.longitud)
      }
    })
    list.sort((a, b) => a.distancia_km - b.distancia_km)
    sedesList.value = list
    renderSedesEnMapa()
  } catch (err) {
    showToast('Error al consultar sedes', true)
  }
}

function renderSedesEnMapa() {
  if (!markersLayer || !map) return
  markersLayer.clearLayers()

  const coords = [[userLocation.lat, userLocation.lon]]

  sedesList.value.forEach(s => {
    if (s.latitud && s.longitud) {
      const tiempoAproxMin = Math.max(2, Math.round(s.distancia_km * 2.8))
      const marker = L.marker([s.latitud, s.longitud])
      marker.bindPopup(`
        <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:210px;">
          <b style="font-size:1rem; color:#0284c7;"><i class="fa-solid fa-square-parking"></i> ${s.nombre}</b>
          <p style="font-size:0.8rem; color:#64748b; margin:4px 0;">${s.direccion}</p>
          <div style="display:flex; justify-content:space-between; margin: 6px 0; font-size:0.8rem; font-weight:700;">
            <span style="color:#0284c7;"><i class="fa-solid fa-route"></i> ${s.distancia_km} km</span>
            <span style="color:#f59e0b;"><i class="fa-solid fa-clock"></i> ~${tiempoAproxMin} min</span>
          </div>
          <div style="display:flex; gap:6px; margin-top:8px;">
            <button onclick="window.trazarRutaDesdePopup(${s.latitud}, ${s.longitud}, '${s.nombre.replace(/'/g, "\\'")}')" style="flex:1; background:rgba(2,132,199,0.15); border:1px solid rgba(2,132,199,0.4); color:#0284c7; padding:7px 8px; border-radius:6px; font-weight:700; font-size:0.8rem; cursor:pointer;">
              <i class="fa-solid fa-diamond-turn-right"></i> Ruta
            </button>
            <a href="/reserva?sede_id=${s.id}" style="flex:1; text-align:center; background:#0284c7; color:#fff; text-decoration:none; padding:7px 8px; border-radius:6px; font-weight:700; font-size:0.8rem;">
              Reservar
            </a>
          </div>
        </div>
      `)
      markersLayer.addLayer(marker)
      coords.push([s.latitud, s.longitud])
    }
  })

  // Exponer función para popups HTML de Leaflet
  window.trazarRutaDesdePopup = (lat, lon, nombre) => {
    trazarRuta(lat, lon, nombre)
  }

  if (coords.length > 1) {
    const bounds = L.latLngBounds(coords)
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 })
  }
}

// ── Función: Dibujar ruta real por calles (OSRM - gratuito) ──
async function dibujarRutaReal(userLat, userLng, sedeLat, sedeLng, destNombre = '') {
  if (!map) return
  if (destNombre) {
    showToast(`Calculando mejor ruta hacia ${destNombre}...`)
    routeBanner.destName = destNombre
  }
  routeBanner.timeText = "Calculando..."
  routeBanner.distText = "Calculando..."
  routeBanner.gmapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${sedeLat},${sedeLng}&travelmode=driving`
  routeBanner.show = true

  try {
    // Limpiar ruta anterior si existe
    if (activeRouteLayer && map) {
      map.removeLayer(activeRouteLayer)
      activeRouteLayer = null
    }

    // Llamar a OSRM (gratuito, sin API key, usa OpenStreetMap)
    const url = `https://router.project-osrm.org/route/v1/driving/` +
      `${userLng},${userLat};${sedeLng},${sedeLat}` +
      `?overview=full&geometries=geojson`

    const response = await fetch(url)
    const data = await response.json()

    if (data.code !== 'Ok' || !data.routes?.length) {
      // Fallback: si OSRM falla, dibujar línea recta con aviso
      console.warn('OSRM no disponible, usando línea recta como fallback')
      const dKm = calcularDistanciaKm(userLat, userLng, sedeLat, sedeLng)
      const durMin = Math.max(3, Math.round(dKm * 2.8))
      routeBanner.distText = `${dKm} km`
      routeBanner.timeText = `${durMin} min aprox.`

      activeRouteLayer = L.polyline(
        [[userLat, userLng], [sedeLat, sedeLng]],
        {
          color: '#3b82f6',
          weight: 3,
          opacity: 0.7,
          dashArray: '8, 8'
        }
      ).addTo(map)

      map.fitBounds(activeRouteLayer.getBounds(), { padding: [40, 40] })
      showToast(`Ruta aproximada trazada: ~${durMin} min`)
      return
    }

    // Extraer coordenadas de la ruta real
    const coords = data.routes[0].geometry.coordinates.map(
      ([lng, lat]) => [lat, lng] // OSRM devuelve [lng,lat], Leaflet usa [lat,lng]
    )

    // Datos del viaje
    const distanciaKm = (data.routes[0].distance / 1000).toFixed(2)
    const duracionMin = Math.round(data.routes[0].duration / 60)

    // Actualizar banner reactivo
    routeBanner.distText = `${distanciaKm} km`
    routeBanner.timeText = `${duracionMin} min aprox.`

    // Crear grupo para la capa de ruta (línea principal + decorativa doble línea)
    const layerGroup = L.featureGroup()

    // Línea base principal
    L.polyline(coords, {
      color: '#3b82f6', // azul
      weight: 5,
      opacity: 0.85,
      lineJoin: 'round',
      lineCap: 'round'
    }).addTo(layerGroup)

    // Línea decorativa encima (efecto doble línea)
    L.polyline(coords, {
      color: '#93c5fd',
      weight: 2,
      opacity: 0.6,
      lineJoin: 'round'
    }).addTo(layerGroup)

    layerGroup.addTo(map)
    activeRouteLayer = layerGroup

    // Ajustar zoom para ver toda la ruta
    map.fitBounds(layerGroup.getBounds(), { padding: [40, 40] })
    showToast(`✅ Ruta real: ${distanciaKm} km (~${duracionMin} min)`)
    console.log(`✅ Ruta real: ${distanciaKm}km, ~${duracionMin}min`)
  } catch (error) {
    console.error('Error al obtener ruta:', error)
    const dKm = calcularDistanciaKm(userLat, userLng, sedeLat, sedeLng)
    const durMin = Math.max(3, Math.round(dKm * 2.8))
    routeBanner.distText = `${dKm} km`
    routeBanner.timeText = `${durMin} min aprox.`

    // Fallback silencioso: línea recta
    if (activeRouteLayer && map) map.removeLayer(activeRouteLayer)
    activeRouteLayer = L.polyline(
      [[userLat, userLng], [sedeLat, sedeLng]],
      { color: '#3b82f6', weight: 3, dashArray: '6, 6', opacity: 0.6 }
    ).addTo(map)

    map.fitBounds(activeRouteLayer.getBounds(), { padding: [40, 40] })
  }
}

async function trazarRuta(destLat, destLon, destNombre) {
  await dibujarRutaReal(userLocation.lat, userLocation.lon, destLat, destLon, destNombre)
}

function limpiarRuta() {
  if (activeRouteLayer && map) {
    map.removeLayer(activeRouteLayer)
    activeRouteLayer = null
  }
  routeBanner.show = false
}

// Mis Reservas
async function fetchMisReservas() {
  try {
    const uid = authStore.user?.id
    if (!uid) return
    const res = await reservasService.getReservasPorUsuario(uid)
    reservasUsuario.value = Array.isArray(res.data) ? res.data : (res.data?.data || [])
  } catch (err) {
    showToast('Error al cargar tus reservas', true)
  }
}

function mostrarTicketQR(r) {
  modalQR.reservaId = r.id
  modalQR.placa = r.placa_vehiculo || 'N/A'
  const payload = JSON.stringify({ reserva_id: r.id, placa: r.placa_vehiculo })
  modalQR.imgUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(payload)}`
  modalQR.open = true
}

async function cancelarReservaCliente(id) {
  if (!confirm('¿Seguro que deseas cancelar esta reserva? Tu espacio será liberado.')) return
  try {
    await reservasService.cancelarReserva(id)
    showToast('Reserva cancelada con éxito')
    await fetchMisReservas()
    await fetchSedesCercanas()
  } catch (err) {
    showToast('No se pudo cancelar la reserva', true)
  }
}

function logout() {
  authStore.logout()
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('user_info')
  router.push('/login')
}

onMounted(() => {
  themeStore.initTheme(true)
  nextTick(() => {
    initMap()
    obtenerUbicacionYRecalcular()
  })
})

onUnmounted(() => {
  if (map) map.remove()
})
</script>

<style scoped>
.dashboard-app-root {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-color, #0b0f19);
  background-image: 
    radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.08) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.06) 0px, transparent 50%);
  color: var(--text-main, #f8fafc);
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

:deep(.leaflet-layer), :deep(.leaflet-control-zoom-in), :deep(.leaflet-control-zoom-out), :deep(.leaflet-control-attribution) {
  filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);
}

.dashboard-app-root.light-mode :deep(.leaflet-layer),
.dashboard-app-root.light-mode :deep(.leaflet-control-zoom-in),
.dashboard-app-root.light-mode :deep(.leaflet-control-zoom-out),
.dashboard-app-root.light-mode :deep(.leaflet-control-attribution) {
  filter: none;
}

.dashboard-app-root {
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

.dashboard-app-root.light-mode {

  --bg-color: #f8fafc;
  --sidebar-bg: #ffffff;
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
  width: 320px;
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
  padding: 24px 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

.top-header { display: flex; justify-content: space-between; align-items: center; }
.greeting h1 { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
.greeting p { color: var(--text-muted); font-size: 0.95rem; }

.theme-toggle-btn {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.85rem;
}

/* Sections */
.section-view { display: flex; flex-direction: column; gap: 20px; flex: 1; }

.map-layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
  flex: 1;
  min-height: 480px;
}

.card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}

.sede-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  max-height: calc(100vh - 280px);
  padding-right: 6px;
}

.sede-card {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
}
.sede-card:hover {
  border-color: var(--primary);
  background: rgba(255, 255, 255, 0.04);
  transform: translateY(-2px);
}
.sede-name { font-size: 1rem; font-weight: 700; color: var(--text-main); margin-bottom: 4px; }
.sede-address { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.sede-badges { display: flex; justify-content: space-between; align-items: center; }

.distancia-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(6, 182, 212, 0.12);
  color: var(--accent);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}
.tarifa-badge { color: #10b981; font-size: 0.85rem; font-weight: 700; }

#map-dashboard {
  width: 100%;
  height: 100%;
  min-height: 480px;
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  z-index: 1;
}

/* Banner de Ruta */
.route-info-banner {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(2, 132, 199, 0.4);
  border-radius: 16px;
  padding: 14px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 320px;
  animation: fadeInDown 0.3s ease;
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.route-info-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.route-metrics { display: flex; gap: 12px; margin-top: 4px; }
.route-metric-pill {
  background: rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 600;
}
.btn-ruta {
  background: rgba(2, 132, 199, 0.15);
  border: 1px solid rgba(2, 132, 199, 0.4);
  color: var(--primary);
  padding: 5px 9px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.btn-ruta:hover { background: var(--primary); color: #fff; }

.btn-action {
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--glass-border);
  color: var(--text-main);
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.btn-action:hover { background: rgba(255,255,255,0.12); }

.btn-reserve-quick {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: #fff;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Tables */
.table-wrapper { overflow-x: auto; width: 100%; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th { padding: 12px 14px; font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--glass-border); }
td { padding: 12px 14px; font-size: 0.9rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: #e2e8f0; vertical-align: middle; }

.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; }
.status-badge.libre { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.reservado { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.status-badge.ocupado { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.alert-toast {
  position: fixed; top: 20px; right: 20px; z-index: 3000;
  color: #fff; padding: 14px 22px; border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.4); font-weight: 500;
}

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.65); backdrop-filter: blur(6px);
  display: flex; justify-content: center; align-items: center; z-index: 2000;
}
.modal-card {
  background: var(--bg-color); border: 1px solid var(--glass-border);
  border-radius: 18px; width: 420px; max-width: 90%; padding: 24px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5); text-align: center;
}

/* Light mode overrides */
.dashboard-app-root.light-mode .sidebar { background: #ffffff; border-right: 1px solid #e2e8f0; }
.dashboard-app-root.light-mode .nav-item { color: #64748b; }
.dashboard-app-root.light-mode .nav-item:hover { background: #f1f5f9; color: #0f172a; }
.dashboard-app-root.light-mode .nav-item.active { background: #eff6ff; color: #0284c7; border-left: 3px solid #0284c7; }
.dashboard-app-root.light-mode .card { background: #ffffff; border-color: #e2e8f0; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05); }
.dashboard-app-root.light-mode th { background: #f8fafc; color: #64748b; border-bottom-color: #e2e8f0; }
.dashboard-app-root.light-mode td { border-bottom-color: #f1f5f9; color: #0f172a; }
.dashboard-app-root.light-mode .sede-card { background: #ffffff; border-color: #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
.dashboard-app-root.light-mode .sede-card:hover { border-color: #0284c7; background: #f8fafc; }
.dashboard-app-root.light-mode .sede-name { color: #0f172a; }
.dashboard-app-root.light-mode .modal-card { background: #ffffff; border-color: #e2e8f0; box-shadow: 0 20px 40px rgba(0,0,0,0.12); }
.dashboard-app-root.light-mode .route-info-banner { background: rgba(255, 255, 255, 0.95); border-color: #0284c7; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
.dashboard-app-root.light-mode .route-info-title { color: #0f172a; }
.dashboard-app-root.light-mode .route-metric-pill { background: #f1f5f9; color: #0f172a; }
.dashboard-app-root.light-mode .btn-action { background: #f1f5f9; border-color: #e2e8f0; color: #0f172a; }
.dashboard-app-root.light-mode .btn-action:hover { background: #e2e8f0; }

@media (max-width: 900px) {
  .map-layout { grid-template-columns: 1fr; }
  #map-dashboard { min-height: 320px; }
}
</style>
