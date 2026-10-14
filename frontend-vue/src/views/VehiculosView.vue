<template>
  <div class="vehiculos-page" :class="{ 'light-mode': !isDark }">
    <header>
      <router-link to="/dashboard" class="header-logo">
        <i class="fa-solid fa-square-parking"></i> SmartPark
      </router-link>
      <div style="display:flex; align-items:center; gap:12px;">
        <button
          @click="toggleTheme"
          id="theme-btn"
          type="button"
          style="background: rgba(255,255,255,0.08); border: 1px solid var(--glass-border); color: var(--text-light); padding: 8px 16px; border-radius: 99px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.85rem;"
        >
          <i :class="isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon'" :style="isDark ? { color: '#f59e0b' } : {}"></i>
          <span>{{ isDark ? 'Modo Claro' : 'Modo Oscuro' }}</span>
        </button>
        <router-link to="/dashboard" class="btn-back">
          <i class="fa-solid fa-arrow-left"></i> Volver
        </router-link>
      </div>
    </header>

    <div class="main-card">
      <h1 class="title"><i class="fa-solid fa-car"></i> Mis Vehículos</h1>
      <p class="subtitle">Registra tus autos para poder agilizar tus reservas.</p>

      <div class="vehiculo-list" id="vehiculos-container">
        <div v-if="loading" class="empty-state">Cargando tus vehículos...</div>
        <div v-else-if="vehiculos.length === 0" class="empty-state">
          No tienes ningún vehículo registrado. Añade uno abajo.
        </div>
        <div
          v-else
          v-for="v in vehiculos"
          :key="v.id"
          class="vehiculo-card"
        >
          <div class="v-placa">{{ v.placa }}</div>
          <div class="v-details">
            <span>{{ v.marca }}</span> {{ v.modelo }} &bull; {{ v.color }}
          </div>
        </div>
      </div>

      <form id="form-vehiculo" @submit.prevent="handleAdd">
        <h3 style="font-size: 1.2rem; margin-bottom: 16px; text-align: left;">+ Registrar Nuevo Vehículo</h3>
        <div class="form-grid">
          <div class="input-group">
            <label>Número de Placa</label>
            <input
              v-model="form.placa"
              type="text"
              id="v-placa"
              placeholder="ABC-123"
              required
              class="uppercase"
            />
          </div>
          <div class="input-group">
            <label>Marca</label>
            <input
              v-model="form.marca"
              type="text"
              id="v-marca"
              placeholder="Toyota, Kia..."
              required
            />
          </div>
          <div class="input-group">
            <label>Modelo</label>
            <input
              v-model="form.modelo"
              type="text"
              id="v-modelo"
              placeholder="Corolla, Rio..."
              required
            />
          </div>
          <div class="input-group">
            <label>Color</label>
            <input
              v-model="form.color"
              type="text"
              id="v-color"
              placeholder="Negro, Blanco..."
              required
            />
          </div>
        </div>
        <button type="submit" class="btn-add" :disabled="submitting">
          <i class="fa-solid" :class="submitting ? 'fa-spinner fa-spin' : 'fa-plus'"></i>
          <span> Agregar Vehículo</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { usuariosService } from '@/services/usuarios'
import { showToast } from '@/components/ToastAlert.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const vehiculos = ref([])
const loading = ref(true)
const submitting = ref(false)

const form = ref({
  placa: '',
  marca: '',
  modelo: '',
  color: ''
})

const isDark = computed(() => themeStore.isDark)

const toggleTheme = () => {
  themeStore.toggleTheme()
}

onMounted(async () => {
  themeStore.initTheme()
  if (!authStore.token && !localStorage.getItem('jwt_token')) {
    router.push('/login')
    return
  }
  await fetchVehiculos()
})

const fetchVehiculos = async () => {
  loading.value = true
  try {
    const res = await usuariosService.getMisVehiculos()
    const data = res.data
    vehiculos.value = Array.isArray(data) ? data : (data?.data || [])
  } catch (e) {
    showToast(e.response?.data?.detail || 'Error al cargar vehículos', 'error')
  } finally {
    loading.value = false
  }
}

const handleAdd = async () => {
  submitting.value = true
  try {
    const payload = {
      placa: form.value.placa.trim().toUpperCase(),
      marca: form.value.marca.trim(),
      modelo: form.value.modelo.trim(),
      color: form.value.color.trim()
    }
    await usuariosService.crearVehiculo(payload)
    showToast('Vehículo registrado exitosamente', 'success')
    form.value = { placa: '', marca: '', modelo: '', color: '' }
    await fetchVehiculos()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar vehículo', 'error')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.vehiculos-page {
  --bg-gradient: linear-gradient(135deg, #0b0f19 0%, #0f172a 100%);
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #38bdf8;
  --text-light: #f8fafc;
  --glass-bg: rgba(17, 24, 39, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);

  background: var(--bg-gradient);
  background-attachment: fixed;
  min-height: 100vh;
  color: var(--text-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 50px;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  transition: background 0.25s ease, color 0.25s ease;
  box-sizing: border-box;
}

.vehiculos-page.light-mode {
  --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0;
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #0284c7;
  --text-light: #0f172a;
}

.vehiculos-page.light-mode header {
  background: rgba(255, 255, 255, 0.95);
  border-bottom-color: #e2e8f0;
}
.vehiculos-page.light-mode .main-card {
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  border-color: #e2e8f0;
}
.vehiculos-page.light-mode .vehiculo-card {
  background: #ffffff;
  border-color: #e2e8f0;
}
.vehiculos-page.light-mode .v-details {
  color: #64748b;
}
.vehiculos-page.light-mode .input-group input {
  background: #ffffff;
  color: #0f172a;
  border-color: #cbd5e1;
}
.vehiculos-page.light-mode .title {
  color: #0f172a;
}
.vehiculos-page.light-mode .btn-back {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}
.vehiculos-page.light-mode .btn-back:hover {
  background: #e2e8f0;
  color: #0f172a;
}
.vehiculos-page.light-mode .empty-state {
  border-color: #cbd5e1;
  color: #64748b;
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
  box-sizing: border-box;
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
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  width: 90%;
  max-width: 700px;
  padding: 40px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  box-sizing: border-box;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 6px;
}
.subtitle {
  color: #94a3b8;
  font-size: 1rem;
  margin-bottom: 30px;
}

.vehiculo-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 30px;
}

.vehiculo-card {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}
.vehiculo-card:hover {
  border-color: var(--primary);
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.v-placa {
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  background: #000;
  padding: 4px 12px;
  border-radius: 8px;
  border: 2px solid #fff;
  letter-spacing: 2px;
}

.v-details {
  font-size: 0.95rem;
  color: #cbd5e1;
}
.v-details span {
  font-weight: 700;
  color: var(--accent);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}
@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
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
.input-group input {
  width: 100%;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 14px 16px;
  color: var(--text-light);
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}
.input-group input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}

.btn-add {
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
}
.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(2, 132, 199, 0.6);
}

.empty-state {
  text-align: center;
  color: #94a3b8;
  padding: 30px;
  border: 1px dashed var(--glass-border);
  border-radius: 16px;
  margin-bottom: 30px;
}
</style>
