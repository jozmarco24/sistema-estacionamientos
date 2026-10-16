<template>
  <div class="login-page-wrapper" :class="{ 'dark-mode': themeStore.isDark }">
    <!-- Botón Flotante para Alternar Modo Claro / Modo Oscuro -->
    <button class="theme-toggle-fixed" @click="themeStore.toggleTheme()" id="login-theme-btn" type="button">
      <i :class="themeStore.isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon'" :style="themeStore.isDark ? { color: '#f59e0b' } : {}"></i>
      <span>{{ themeStore.isDark ? 'Modo Claro' : 'Modo Oscuro' }}</span>
    </button>

    <!-- Selector de Tipo de Usuario (Conductor vs Empresa) -->
    <div class="portal-tabs">
      <button
        class="portal-tab-btn"
        :class="{ active: currentPortal === 'conductor' }"
        id="btn-portal-conductor"
        @click="selectPortal('conductor')"
        type="button"
      >
        <i class="fa-solid fa-car"></i> Para Conductores
      </button>
      <button
        class="portal-tab-btn"
        :class="{ active: currentPortal === 'empresa' }"
        id="btn-portal-empresa"
        @click="selectPortal('empresa')"
        type="button"
      >
        <i class="fa-solid fa-building"></i> Para Empresas / Dueños
      </button>
    </div>

    <!-- Tarjeta de Autenticación Blanca (Estilo Minimalista) -->
    <div class="auth-card">
      <!-- Logo -->
      <div class="logo-wrap">
        <div class="logo-icon"><i class="fa-solid fa-square-parking"></i></div>
        <div class="logo-text">Smart<span>Park</span></div>
      </div>
      <div class="brand-subline">Estacionamientos Inteligentes</div>

      <!-- Encabezado de Bienvenida -->
      <h1 class="welcome-title" id="txt-title">{{ isRegister ? 'Crear Cuenta' : 'Bienvenido' }}</h1>
      <p class="welcome-subtitle" id="txt-subtitle">
        {{ subtitleText }}
      </p>

      <!-- Caja de Alerta -->
      <div
        v-if="alertMessage"
        class="alert-box"
        :class="alertIsSuccess ? 'success' : 'error'"
        id="auth-alert"
      >
        {{ alertMessage }}
      </div>

      <!-- Formulario -->
      <form id="login-form" @submit.prevent="handleFormSubmit">
        <!-- Campo Nombre (solo visible cuando se elige Registrarse) -->
        <div v-if="isRegister" class="form-field" id="field-nombre">
          <label class="field-label" id="label-nombre">
            {{ currentPortal === 'empresa' ? 'Nombre de la Empresa o Razón Social' : 'Nombre completo' }}
          </label>
          <input
            v-model="nombre"
            type="text"
            class="input-clean"
            id="input-nombre"
            :placeholder="currentPortal === 'empresa' ? 'Ej. Estacionamientos San José S.A.C.' : 'Ej. Juan Pérez'"
            required
          />
        </div>

        <!-- Campo Correo Electrónico -->
        <div class="form-field">
          <label class="field-label">Correo electrónico*</label>
          <input
            v-model="email"
            type="email"
            class="input-clean"
            id="input-email"
            placeholder="correo@ejemplo.com"
            required
            autofocus
          />
        </div>

        <!-- Campo Contraseña -->
        <div class="form-field" id="field-password">
          <label class="field-label">Contraseña*</label>
          <input
            v-model="password"
            type="password"
            class="input-clean"
            id="input-password"
            placeholder="••••••••"
            required
          />
        </div>

        <!-- Botón Principal "Continuar / Registrarse" -->
        <button type="submit" class="btn-continue" id="btn-submit" :disabled="loading">
          <span v-if="!loading" id="btn-label">{{ isRegister ? 'Registrarse' : 'Continuar' }}</span>
          <div v-else class="spinner" id="btn-spinner" style="display:inline-block;"></div>
        </button>
      </form>

      <!-- Texto "¿No tiene una cuenta? Regístrese" -->
      <div class="toggle-account-wrap">
        <span id="toggle-prompt">{{ isRegister ? '¿Ya tiene una cuenta?' : '¿No tiene una cuenta?' }}</span>
        <a @click="toggleMode" id="toggle-link">{{ isRegister ? ' Iniciar sesión' : ' Regístrese' }}</a>
      </div>

      <!-- Bloque Google (Solo para Conductores en modo login) -->
      <div v-if="currentPortal === 'conductor' && !isRegister" id="google-block">
        <div class="divider-line">
          <span>o</span>
        </div>

        <GoogleButton @success="handleGoogleSuccess" @error="handleGoogleError" />
      </div>


      <div class="footer-note">
        SmartPark Enterprise Platform &copy; 2026
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api, { URLS } from '@/services/api'
import GoogleButton from '@/components/GoogleButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const currentPortal = ref('conductor') // 'conductor' | 'empresa'
const isRegister = ref(false)
const loading = ref(false)

const nombre = ref('')
const email = ref('')
const password = ref('')

const alertMessage = ref('')
const alertIsSuccess = ref(false)

const subtitleText = computed(() => {
  if (currentPortal.value === 'empresa') {
    return 'Acceso a la plataforma de gestión y cobro para dueños de sedes'
  }
  return 'Iniciar sesión en SmartPark para reservar y estacionar'
})

onMounted(() => {
  themeStore.initTheme()

  if (route.query.mode === 'register') {
    isRegister.value = true
  }
})

function showAlert(msg, isSuccess = false) {
  alertMessage.value = msg
  alertIsSuccess.value = isSuccess
}

function hideAlert() {
  alertMessage.value = ''
}

function selectPortal(portal) {
  currentPortal.value = portal
  hideAlert()
}

function toggleMode() {
  isRegister.value = !isRegister.value
  hideAlert()
  router.replace({ query: isRegister.value ? { mode: 'register' } : {} })
}


function redirectByRole(rol) {
  const r = (rol || '').toLowerCase()
  if (r === 'admin') router.push('/admin')
  else if (r === 'propietario') router.push('/propietario')
  else if (r === 'operador') router.push('/operador')
  else router.push('/dashboard')
}

async function handleFormSubmit() {
  hideAlert()
  loading.value = true

  try {
    if (!isRegister.value) {
      // Iniciar sesión con email + password
      const res = await api.post(`${URLS.usuarios}/usuarios/login`, {
        email: email.value.trim(),
        password: password.value
      })
      const data = res.data

      // Guardar sesión compatible tanto para Vue como para el frontend clásico
      authStore.setAuth(data.access_token, data.user)
      localStorage.setItem('jwt_token', data.access_token)
      localStorage.setItem('user_info', JSON.stringify(data.user))

      showAlert('¡Inicio de sesión exitoso! Redirigiendo...', true)

      setTimeout(() => {
        redirectByRole(data.user.rol)
      }, 700)

    } else {
      // Registro
      const rol = (currentPortal.value === 'empresa') ? 'propietario' : 'conductor'
      await api.post(`${URLS.usuarios}/usuarios/registro`, {
        nombre: nombre.value.trim(),
        email: email.value.trim(),
        password: password.value,
        rol
      })

      showAlert('¡Cuenta creada con éxito! Ingresando...', true)

      // Login automático inmediato
      const loginRes = await api.post(`${URLS.usuarios}/usuarios/login`, {
        email: email.value.trim(),
        password: password.value
      })
      const loginData = loginRes.data

      authStore.setAuth(loginData.access_token, loginData.user)
      localStorage.setItem('jwt_token', loginData.access_token)
      localStorage.setItem('user_info', JSON.stringify(loginData.user))

      setTimeout(() => {
        redirectByRole(loginData.user.rol)
      }, 700)
    }
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || 'Error en las credenciales'
    showAlert(typeof errorMsg === 'string' ? errorMsg : 'Error al procesar la solicitud', false)
  } finally {
    loading.value = false
  }
}

// Integración oficial con Google Identity Services
function handleGoogleSuccess(data) {
  authStore.setAuth(data.access_token, data.user)
  localStorage.setItem('jwt_token', data.access_token)
  localStorage.setItem('user_info', JSON.stringify(data.user))

  showAlert(`¡Bienvenido ${data.user.nombre}! Redirigiendo...`, true)
  setTimeout(() => {
    redirectByRole(data.user.rol)
  }, 700)
}

function handleGoogleError(errorMsg) {
  if (errorMsg && errorMsg.includes('solo para conductores')) {
    showAlert('Este acceso es solo para conductores. Ingresa con tu correo y contraseña.', false)
  } else {
    showAlert(errorMsg || 'Error de autenticación con Google', false)
  }
}
</script>

<style scoped>
.login-page-wrapper {
  --primary-blue: #0284c7;
  --primary-hover: #0369a1;
  --text-dark: #0f172a;
  --text-muted: #64748b;
  --border-color: #e2e8f0;
  --bg-page: #f8fafc;
  --card-bg: #ffffff;
  --input-bg: #ffffff;
  --portal-bg: #f1f5f9;
  --google-btn-bg: #ffffff;
  --google-btn-hover: #f8fafc;
  --google-btn-border: #cbd5e1;
  --google-btn-text: #334155;
  --shadow-card: 0 10px 30px -5px rgba(15, 23, 42, 0.06), 0 20px 25px -5px rgba(15, 23, 42, 0.03);

  background-color: var(--bg-page);
  background-image: 
      radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.08) 0px, transparent 50%),
      radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.06) 0px, transparent 50%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--text-dark);
  padding: 24px 16px;
  position: relative;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease;
}

.login-page-wrapper.dark-mode {
  --primary-blue: #38bdf8;
  --primary-hover: #0284c7;
  --text-dark: #f8fafc;
  --text-muted: #94a3b8;
  --border-color: rgba(255, 255, 255, 0.12);
  --bg-page: #0b0f19;
  --card-bg: rgba(30, 41, 59, 0.85);
  --input-bg: rgba(15, 23, 42, 0.7);
  --portal-bg: rgba(15, 23, 42, 0.8);
  --google-btn-bg: rgba(15, 23, 42, 0.6);
  --google-btn-hover: rgba(30, 41, 59, 0.9);
  --google-btn-border: rgba(255, 255, 255, 0.15);
  --google-btn-text: #f1f5f9;
  --shadow-card: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.08);
}

/* Botón de alternancia de Tema (Modo Claro / Oscuro) */
.theme-toggle-fixed {
  position: absolute;
  top: 24px;
  right: 24px;
  background: var(--card-bg);
  border: 1.5px solid var(--border-color);
  color: var(--text-dark);
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 0.86rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  z-index: 100;
  transition: all 0.2s ease;
}
.theme-toggle-fixed:hover {
  border-color: var(--primary-blue);
}

/* Selector de perfil superior (Conductor vs Empresa) */
.portal-tabs {
  display: inline-flex;
  background: var(--portal-bg);
  padding: 4px;
  border-radius: 9999px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.portal-tab-btn {
  border: none;
  background: transparent;
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.portal-tab-btn.active {
  background: var(--card-bg);
  color: var(--primary-blue);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Tarjeta Blanca Limpia Minimalista */
.auth-card {
  background: var(--card-bg);
  backdrop-filter: blur(16px);
  width: 100%;
  max-width: 420px;
  padding: 40px 36px;
  border-radius: 24px;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--border-color);
  text-align: center;
  position: relative;
}

/* Logo estilo marca moderna */
.logo-wrap {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 1.3rem;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
}

.logo-text {
  font-size: 1.65rem;
  font-weight: 800;
  color: var(--text-dark);
  letter-spacing: -0.5px;
}

.logo-text span {
  color: var(--primary-blue);
}

.brand-subline {
  font-size: 0.76rem;
  color: #94a3b8;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-top: -6px;
  margin-bottom: 24px;
  text-transform: uppercase;
}

.welcome-title {
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--text-dark);
  margin-bottom: 6px;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 0.92rem;
  color: var(--text-muted);
  margin-bottom: 28px;
  line-height: 1.45;
}

/* Formulario con campos limpios */
.form-field {
  text-align: left;
  margin-bottom: 18px;
}

.field-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-dark);
  margin-bottom: 6px;
}

.input-clean {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  font-size: 0.95rem;
  color: var(--text-dark);
  background: var(--input-bg);
  border: 1.5px solid var(--border-color);
  border-radius: 10px;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.input-clean::placeholder {
  color: var(--text-muted);
  font-size: 0.92rem;
}

.input-clean:focus {
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}

/* Botón Continuar Principal */
.btn-continue {
  width: 100%;
  height: 50px;
  background: var(--primary-blue);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
  margin-top: 8px;
}

.btn-continue:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(2, 132, 199, 0.35);
}

.btn-continue:active {
  transform: translateY(0);
}

/* Links de alternancia (¿No tiene una cuenta? Regístrese) */
.toggle-account-wrap {
  margin: 22px 0 20px 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.toggle-account-wrap a {
  color: var(--primary-blue);
  font-weight: 700;
  text-decoration: none;
  margin-left: 4px;
  cursor: pointer;
}

.toggle-account-wrap a:hover {
  text-decoration: underline;
}

/* Separador "O" */
.divider-line {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 20px 0;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
}

.divider-line::before,
.divider-line::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--border-color);
}

.divider-line span {
  padding: 0 14px;
}

/* Botón de Google Auténtico */
.btn-google {
  width: 100%;
  height: 48px;
  background: var(--google-btn-bg);
  color: var(--google-btn-text);
  border: 1.5px solid var(--google-btn-border);
  border-radius: 10px;
  font-size: 0.93rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.btn-google:hover {
  background: var(--google-btn-hover);
  border-color: var(--primary-blue);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.google-icon {
  width: 20px;
  height: 20px;
}

/* Alertas de error/éxito */
.alert-box {
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 0.88rem;
  margin-bottom: 20px;
  text-align: left;
}

.alert-box.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
}

.alert-box.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #15803d;
}

/* Loader */
.spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.footer-note {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 24px;
}

.role-badge {
  font-size: 0.75rem;
  color: var(--accent, #38bdf8);
  font-weight: 600;
  opacity: 0.8;
}
</style>
