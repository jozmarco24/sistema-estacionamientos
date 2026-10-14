<template>
  <div class="section-view active-section">
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
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import L from 'leaflet'

const props = defineProps({
  misSedes: { type: Array, default: () => [] },
  stats: { type: Object, required: true },
  incidenciasList: { type: Array, default: () => [] }
})

let ownerMap = null
let ownerMarkersLayer = null

const totalEspacios = computed(() => props.stats.libres + props.stats.reservados + props.stats.ocupados)
const ocupacionPct = computed(() => {
  if (totalEspacios.value === 0) return 0
  return Math.round(((props.stats.reservados + props.stats.ocupados) / totalEspacios.value) * 100)
})

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

function initOwnerMap() {
  const oMapEl = document.getElementById('owner-map')
  if (oMapEl && !ownerMap) {
    ownerMap = L.map('owner-map').setView([-12.046, -77.042], 12)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(ownerMap)
    ownerMarkersLayer = L.layerGroup().addTo(ownerMap)
    updateMarkers()
  }
  setTimeout(() => {
    if (ownerMap) ownerMap.invalidateSize()
  }, 150)
}

function updateMarkers() {
  if (!ownerMarkersLayer) return
  ownerMarkersLayer.clearLayers()
  const validCoords = []
  props.misSedes.forEach(s => {
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

function recenterOwnerMap() {
  if (!ownerMap || props.misSedes.length === 0) return
  const valid = props.misSedes.filter(s => s.latitud && s.longitud)
  if (valid.length === 0) return
  const bounds = L.latLngBounds(valid.map(s => [s.latitud, s.longitud]))
  ownerMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 })
}

onMounted(() => {
  nextTick(() => initOwnerMap())
})

watch(() => props.misSedes, () => {
  updateMarkers()
}, { deep: true })

onUnmounted(() => {
  if (ownerMap) ownerMap.remove()
})
</script>
