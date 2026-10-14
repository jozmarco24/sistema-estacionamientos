<template>
  <div class="pago-page-wrapper" :class="{ 'light-mode': !isDark }">
    <!-- Botón de Alternancia de Tema -->
    <button class="theme-btn-float" @click="toggleTheme" id="theme-btn" type="button">
      <i :class="isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon'" :style="isDark ? { color: '#f59e0b' } : {}"></i>
      <span>{{ isDark ? 'Modo Claro' : 'Modo Oscuro' }}</span>
    </button>

    <div class="payment-card">
      <!-- Banner Retención Tipo Cine -->
      <div v-if="reservaId && !pagoCompletado" class="seat-holding-timer" id="seat-timer-box">
        <div class="timer-info">
          <strong style="color:#fbbf24;"><i class="fa-solid fa-lock"></i> Espacio Bloqueado Exclusivo</strong>
          <p style="color:#94a3b8; font-size:0.75rem; margin-top:2px;">Tienes este tiempo para pagar antes de que se libere:</p>
        </div>
        <div class="timer-digits">
          <i class="fa-regular fa-clock" style="font-size:1.1rem;"></i>
          <span id="countdown-text" :style="timeLeftSeconds < 120 ? { color: '#ef4444' } : {}">{{ timerFormatted }}</span>
        </div>
      </div>

      <!-- Overlay Éxito -->
      <div id="success-screen" class="success-overlay" :class="{ active: pagoCompletado }">
        <div class="success-icon"><i class="fa-solid fa-circle-check"></i></div>
        <h2 class="title" style="color:var(--success-color);">¡Ticket Generado!</h2>
        <p style="color: #94a3b8; margin-bottom:20px;">Muestra este código al llegar a la caseta.</p>
        <div style="background: #fff; padding: 15px; border-radius: 16px; margin-bottom: 20px;">
          <img :src="qrCodeUrl" alt="QR Code" width="180" height="180" />
        </div>
        <p style="color: var(--accent); font-weight:700; font-size:1.2rem; margin-bottom: 20px;" id="success-placa">
          Placa: {{ placaFinal }}
        </p>
        <router-link to="/dashboard" class="btn-success">Finalizar</router-link>
      </div>

      <i class="fa-solid fa-file-invoice-dollar invoice-icon"></i>
      <h1 class="title">Procesar Pago</h1>
      <p class="subtitle">Completa tu transacción para asegurar la reserva definitiva</p>

      <div v-if="errorMessage" id="error-box" class="alert-error" style="display:block;">
        {{ errorMessage }}
      </div>

      <!-- TARJETA EMBEBIDA TIPO CULQI EXACTA -->
      <div class="culqi-card-widget">
        <!-- Header con Precio Total -->
        <div class="culqi-header-price">
          <div class="culqi-label-price">
            <i class="fa-solid fa-receipt"></i>
            <span>Precio total</span>
          </div>
          <div class="culqi-amount-price" id="culqi-display-total">S/ {{ pagoMonto.toFixed(2) }}</div>
        </div>

        <!-- Tabs de Métodos de Pago Culqi -->
        <div class="culqi-tabs-container">
          <div
            class="culqi-tab-btn"
            :class="{ active: activeCulqiTab === 'tarjeta' }"
            id="tab-tarjeta"
            @click="activeCulqiTab = 'tarjeta'"
          >
            <i class="fa-solid fa-credit-card tab-icon"></i>
            <div class="tab-label">Tarjeta débito / crédito</div>
          </div>
          <div
            class="culqi-tab-btn"
            :class="{ active: activeCulqiTab === 'yape' }"
            id="tab-yape"
            @click="activeCulqiTab = 'yape'"
          >
            <i class="fa-solid fa-qrcode tab-icon" style="color: #8b5cf6;"></i>
            <div class="tab-label">Yape</div>
          </div>
          <div
            class="culqi-tab-btn"
            :class="{ active: activeCulqiTab === 'billeteras' }"
            id="tab-billeteras"
            @click="activeCulqiTab = 'billeteras'"
          >
            <i class="fa-solid fa-wallet tab-icon" style="color: #06b6d4;"></i>
            <div class="tab-label">Billeteras móviles</div>
          </div>
          <div
            class="culqi-tab-btn"
            :class="{ active: activeCulqiTab === 'banca' }"
            id="tab-banca"
            @click="activeCulqiTab = 'banca'"
          >
            <i class="fa-solid fa-building-columns tab-icon" style="color: #10b981;"></i>
            <div class="tab-label">Banca internet</div>
          </div>
        </div>

        <!-- Panel 1: Formulario de Tarjeta -->
        <form v-show="activeCulqiTab === 'tarjeta'" id="culqi-card-form" @submit.prevent="procesarPagoDirecto">
          <div class="culqi-form-field">
            <label>Número de tarjeta</label>
            <div class="culqi-input-with-icon">
              <input
                v-model="card.number"
                type="text"
                id="culqi-card-number"
                placeholder="9999 9999 9999 9999"
                maxlength="19"
                required
                @input="formatCardNumber"
              />
              <div class="culqi-card-brands">
                <i class="fa-brands fa-cc-visa" style="color: #1a1f71; font-size: 1.4rem;"></i>
                <i class="fa-brands fa-cc-mastercard" style="color: #eb001b; font-size: 1.4rem;"></i>
              </div>
            </div>
          </div>

          <div class="culqi-row-two">
            <div class="culqi-form-field">
              <label>Vencimiento</label>
              <input
                v-model="card.exp"
                type="text"
                id="culqi-card-exp"
                placeholder="MM/AA"
                maxlength="5"
                required
                @input="formatExpiry"
              />
            </div>
            <div class="culqi-form-field">
              <label>Código de seguridad</label>
              <input
                v-model="card.cvv"
                type="password"
                id="culqi-card-cvv"
                placeholder="999"
                maxlength="4"
                required
              />
            </div>
          </div>

          <div class="culqi-form-field">
            <label>Número de cuotas</label>
            <select v-model="card.installments" id="culqi-card-installments">
              <option value="1">Sin cuotas (1 pago)</option>
              <option value="2">2 cuotas</option>
              <option value="3">3 cuotas</option>
              <option value="6">6 cuotas</option>
              <option value="12">12 cuotas</option>
            </select>
          </div>

          <div class="culqi-form-field">
            <label>Correo electrónico</label>
            <input
              v-model="card.email"
              type="email"
              id="culqi-card-email"
              placeholder="correo@electronico.com"
              required
            />
          </div>

          <button type="submit" class="culqi-btn-pay" id="btn-submit" :disabled="loading">
            <span v-if="!loading" id="btn-pay-text">Pagar S/ {{ pagoMonto.toFixed(2) }}</span>
            <span v-else id="btn-pay-spinner" class="loader"></span>
          </button>
        </form>

        <!-- Panel 2: Yape -->
        <div v-show="activeCulqiTab === 'yape'" id="culqi-yape-panel" style="text-align:center; padding: 20px 0;">
          <div style="background:#702f8a; color:#fff; padding:16px; border-radius:14px; margin-bottom:15px; font-weight:700;">
            <i class="fa-solid fa-qrcode" style="font-size:1.6rem; display:block; margin-bottom:8px;"></i>
            Paga al instante con tu App Yape
          </div>
          <div class="culqi-form-field" style="text-align:left;">
            <label>Número de Celular Yape</label>
            <input type="text" placeholder="999 999 999" maxlength="9" />
          </div>
          <div class="culqi-form-field" style="text-align:left;">
            <label>Código de Aprobación Yape (6 dígitos)</label>
            <input type="password" placeholder="123456" maxlength="6" />
          </div>
          <button type="button" class="culqi-btn-pay" style="background:#702f8a;" @click="abrirCheckoutCulqi">
            Abrir Checkout Oficial Culqi Yape
          </button>
        </div>

        <!-- Panel 3: Billeteras / Banca -->
        <div v-show="activeCulqiTab === 'billeteras' || activeCulqiTab === 'banca'" id="culqi-other-panel" style="text-align:center; padding: 20px 0;">
          <p style="color:#64748b; font-size:0.9rem; margin-bottom:15px;">
            Puedes completar tu pago mediante la ventana modal segura oficial de Culqi.
          </p>
          <button type="button" class="culqi-btn-pay" @click="abrirCheckoutCulqi">
            <i class="fa-solid fa-lock"></i> Continuar con Pasarela Culqi
          </button>
        </div>

        <!-- Footer con Sellos de Seguridad Culqi -->
        <div class="culqi-secure-footer">
          <div class="culqi-secure-badge">
            <i class="fa-solid fa-shield-halved"></i>
            <span>Compra segura con <strong>PCI</strong> y <strong>Verified by VISA</strong></span>
          </div>
          <div class="culqi-brand-seal">
            <span class="culqi-logo-text">Culqi <span class="culqi-dot">Q</span></span>
            <span class="culqi-credisello">Con el respaldo de <strong>BCP</strong></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api, { URLS } from '@/services/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const reservaId = computed(() => route.query.reserva_id ? parseInt(route.query.reserva_id) : null)
const suscripcionId = computed(() => route.query.suscripcion_id ? parseInt(route.query.suscripcion_id) : null)

const isDark = computed(() => themeStore.isDark)

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const activeCulqiTab = ref('tarjeta')
const pagoId = ref(null)
const pagoMonto = ref(0)
const reservaData = ref(null)
const culqiPublicKey = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const pagoCompletado = ref(false)
const qrCodeUrl = ref('')
const placaFinal = ref('')

const timeLeftSeconds = ref(600)
let timerInterval = null

const card = ref({
  number: '',
  exp: '',
  cvv: '',
  installments: '1',
  email: authStore.user?.email || 'cliente@smartpark.com'
})

const timerFormatted = computed(() => {
  const min = Math.floor(timeLeftSeconds.value / 60)
  const sec = timeLeftSeconds.value % 60
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
})

onMounted(async () => {
  themeStore.initTheme()
  if (!authStore.token && !localStorage.getItem('jwt_token')) {
    router.push('/login')
    return
  }


  // Cargar Culqi checkout script si no está presente
  if (!window.Culqi) {
    const script = document.createElement('script')
    script.src = 'https://checkout.culqi.com/js/v4'
    document.head.appendChild(script)
  }

  if (reservaId.value) {
    iniciarTemporizadorCine()
  }

  await fetchPagoDetails()
  await configurarCulqi()

  // Setup culqi callback
  window.culqi = handleCulqiModalCallback
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

function iniciarTemporizadorCine() {
  const storageKey = `timer_reserva_${reservaId.value}`
  const storedTime = sessionStorage.getItem(storageKey)
  if (storedTime) {
    const elapsed = Math.floor((Date.now() - parseInt(storedTime)) / 1000)
    timeLeftSeconds.value = Math.max(0, 600 - elapsed)
  } else {
    sessionStorage.setItem(storageKey, Date.now().toString())
  }

  timerInterval = setInterval(() => {
    timeLeftSeconds.value--
    if (timeLeftSeconds.value <= 0) {
      clearInterval(timerInterval)
      tiempoExpirado()
    }
  }, 1000)
}

async function tiempoExpirado() {
  errorMessage.value = '¡Tiempo expirado! Tu reserva temporal ha finalizado y el espacio ha sido liberado.'
  try {
    if (reservaId.value) {
      await api.put(`${URLS.reservas}/reservas/${reservaId.value}/expirar`)
    }
  } catch (e) {}

  setTimeout(() => {
    alert('Tu tiempo de reserva ha expirado. Serás redirigido al panel principal.')
    router.push('/dashboard')
  }, 2500)
}

function formatCardNumber(e) {
  let val = e.target.value.replace(/\D/g, '').substring(0, 16)
  card.value.number = val.match(/.{1,4}/g)?.join(' ') || val
}

function formatExpiry(e) {
  let val = e.target.value.replace(/\D/g, '')
  if (val.length >= 2) {
    card.value.exp = val.substring(0, 2) + '/' + val.substring(2, 4)
  } else {
    card.value.exp = val
  }
}

async function fetchPagoDetails() {
  try {
    let url = ''
    if (reservaId.value) {
      url = `${URLS.pagos}/pagos/reserva/${reservaId.value}`
    } else if (suscripcionId.value) {
      url = `${URLS.pagos}/pagos/suscripcion/${suscripcionId.value}`
    } else {
      router.push('/dashboard')
      return
    }

    const res = await api.get(url)
    const pagos = res.data
    if (!pagos || pagos.length === 0) throw new Error('No hay orden de pago pendiente')

    const pago = pagos[0]
    pagoId.value = pago.id
    pagoMonto.value = pago.monto

    if (reservaId.value) {
      const resResp = await api.get(`${URLS.reservas}/reservas/${reservaId.value}`)
      reservaData.value = resResp.data
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || err.message || 'Error al obtener orden de pago'
  }
}

async function configurarCulqi() {
  try {
    if (!pagoId.value) return
    const res = await api.get(`${URLS.pagos}/pagos/config-publica?pago_id=${pagoId.value}`)
    culqiPublicKey.value = res.data.public_key
    if (window.Culqi) {
      window.Culqi.publicKey = culqiPublicKey.value
    }
  } catch (err) {
    errorMessage.value = `Aviso de Pasarela: ${err.response?.data?.detail || err.message}`
  }
}

async function procesarPagoDirecto() {
  if (!pagoId.value) return alert('No hay orden de pago activa')
  if (reservaId.value && timeLeftSeconds.value <= 0) return alert('El tiempo de reserva ha expirado')
  if (!culqiPublicKey.value) return alert('Cargando pasarela Culqi... intenta nuevamente en un momento')

  const rawCardNumber = card.value.number.replace(/\s+/g, '')
  const expParts = card.value.exp.split('/')
  if (rawCardNumber.length < 13 || rawCardNumber.length > 19 || expParts.length !== 2) {
    return alert('Por favor ingresa datos de tarjeta válidos')
  }

  const expMonth = parseInt(expParts[0])
  let expYear = parseInt(expParts[1])
  if (expYear < 100) expYear += 2000

  loading.value = true
  errorMessage.value = ''

  try {
    // 1. Crear Token con Culqi API Token Directo
    const tokenResp = await fetch('https://secure.culqi.com/v2/tokens', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${culqiPublicKey.value}`
      },
      body: JSON.stringify({
        card_number: rawCardNumber,
        cvv: card.value.cvv,
        expiration_month: expMonth,
        expiration_year: expYear,
        email: card.value.email
      })
    })

    const tokenData = await tokenResp.json()
    if (!tokenResp.ok) {
      throw new Error(tokenData.user_message || tokenData.merchant_message || 'Tarjeta declinada o datos incorrectos')
    }

    // 2. Ejecutar cobro con nuestro backend
    const cobroResp = await api.post(`${URLS.pagos}/pagos/culqi/cobrar`, {
      pago_id: pagoId.value,
      token_id: tokenData.id,
      email: card.value.email
    })

    finalizarPagoExitoso(cobroResp.data.culqi_charge_id)
  } catch (err) {
    errorMessage.value = `Error Culqi: ${err.response?.data?.detail || err.message}`
  } finally {
    loading.value = false
  }
}

function abrirCheckoutCulqi() {
  if (!pagoId.value) return alert('No hay orden de pago activa')
  if (!window.Culqi || !culqiPublicKey.value) return alert('Cargando Culqi... espera un momento')

  const montoCentimos = Math.round(pagoMonto.value * 100)
  window.Culqi.publicKey = culqiPublicKey.value
  window.Culqi.settings({
    title: 'SmartPark Parking',
    currency: 'PEN',
    amount: montoCentimos,
    description: reservaId.value ? `Reserva #${reservaId.value}` : `Suscripción #${suscripcionId.value}`
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
  window.Culqi.open()
}

async function handleCulqiModalCallback() {
  if (window.Culqi.token) {
    const tokenId = window.Culqi.token.id
    const emailCliente = window.Culqi.token.email || card.value.email
    window.Culqi.close()
    loading.value = true

    try {
      const response = await api.post(`${URLS.pagos}/pagos/culqi/cobrar`, {
        pago_id: pagoId.value,
        token_id: tokenId,
        email: emailCliente
      })
      finalizarPagoExitoso(response.data.culqi_charge_id)
    } catch (err) {
      errorMessage.value = `Error Culqi: ${err.response?.data?.detail || err.message}`
    } finally {
      loading.value = false
    }
  } else if (window.Culqi.error) {
    alert(window.Culqi.error.user_message || 'Error en el checkout de Culqi')
  }
}

function finalizarPagoExitoso(chargeId) {
  if (timerInterval) clearInterval(timerInterval)
  if (reservaId.value) {
    sessionStorage.removeItem(`timer_reserva_${reservaId.value}`)
  }

  const placa = reservaData.value ? reservaData.value.placa_vehiculo : 'REGISTRADA'
  placaFinal.value = placa

  const qrData = JSON.stringify({
    reserva_id: reservaId.value,
    pago_id: pagoId.value,
    charge_id: chargeId,
    placa: placa
  })
  qrCodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrData)}`
  pagoCompletado.value = true
}
</script>

<style scoped>
.pago-page-wrapper {
  --bg-gradient: linear-gradient(135deg, #0b0f19 0%, #0f172a 100%);
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #38bdf8;
  --text-light: #f8fafc;
  --glass-bg: rgba(17, 24, 39, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);
  --success-color: #10b981;

  background: var(--bg-gradient);
  background-attachment: fixed;
  min-height: 100vh;
  color: var(--text-light);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  transition: background 0.25s ease, color 0.25s ease;
  box-sizing: border-box;
}

.pago-page-wrapper.light-mode {
  --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  --glass-bg: #ffffff;
  --glass-border: #e2e8f0;
  --primary: #0284c7;
  --primary-hover: #0369a1;
  --accent: #0284c7;
  --text-light: #0f172a;
}

.pago-page-wrapper.light-mode .payment-card {
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  border-color: #e2e8f0;
  color: #0f172a;
}
.pago-page-wrapper.light-mode .title {
  color: #0f172a;
}
.pago-page-wrapper.light-mode .success-overlay {
  background: #ffffff;
  color: #0f172a;
}

.theme-btn-float {
  position: absolute;
  top: 24px;
  right: 24px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-light);
  padding: 8px 16px;
  border-radius: 99px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  z-index: 100;
}

.payment-card {
  background: var(--glass-bg);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  width: 100%;
  max-width: 500px;
  padding: 40px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  text-align: center;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

.invoice-icon {
  font-size: 3rem;
  color: var(--accent);
  margin-bottom: 20px;
}

.title {
  font-size: 1.8rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.subtitle {
  color: #94a3b8;
  font-size: 0.95rem;
  margin-bottom: 30px;
}

.alert-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

/* Temporizador Cine */
.seat-holding-timer {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(239, 68, 68, 0.15) 100%);
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 14px;
  padding: 12px 16px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.timer-info {
  text-align: left;
  font-size: 0.8rem;
}
.timer-digits {
  font-size: 1.35rem;
  font-weight: 800;
  color: #fbbf24;
  font-variant-numeric: tabular-nums;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Culqi Card Widget */
.culqi-card-widget {
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12), 0 5px 15px rgba(0, 0, 0, 0.06);
  padding: 24px;
  color: #1e293b;
  text-align: left;
  margin-top: 15px;
  border: 1px solid #e2e8f0;
}

.culqi-header-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 14px;
  margin-bottom: 16px;
}

.culqi-label-price {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.88rem;
  font-weight: 500;
}

.culqi-amount-price {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
}

.culqi-tabs-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.culqi-tab-btn {
  flex: 1;
  min-width: 90px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 8px;
  text-align: left;
  cursor: pointer;
  background: #f8fafc;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.culqi-tab-btn:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}
.culqi-tab-btn.active {
  background: #fff9f5;
  border: 1.5px solid #ff6a00;
  box-shadow: 0 2px 8px rgba(255, 106, 0, 0.12);
}
.culqi-tab-btn .tab-icon {
  font-size: 1.25rem;
  color: #ff6a00;
}
.culqi-tab-btn .tab-label {
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1.2;
  color: #334155;
}

.culqi-form-field {
  margin-bottom: 15px;
}
.culqi-form-field label {
  display: block;
  font-size: 0.78rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}
.culqi-form-field input, .culqi-form-field select {
  width: 100%;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 0.95rem;
  color: #0f172a;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.culqi-form-field input:focus, .culqi-form-field select:focus {
  border-color: #ff6a00;
  box-shadow: 0 0 0 3px rgba(255, 106, 0, 0.15);
}

.culqi-input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}
.culqi-input-with-icon input {
  padding-right: 75px;
}

.culqi-card-brands {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  pointer-events: none;
}

.culqi-row-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.culqi-btn-pay {
  width: 100%;
  background: linear-gradient(135deg, #ff6a00 0%, #ee5100 100%);
  border: none;
  border-radius: 10px;
  padding: 14px;
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(238, 81, 0, 0.35);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 8px;
}
.culqi-btn-pay:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(238, 81, 0, 0.45);
}
.culqi-btn-pay:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.culqi-secure-footer {
  margin-top: 18px;
  text-align: center;
  border-top: 1px solid #f1f5f9;
  padding-top: 14px;
}
.culqi-secure-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 8px;
}
.culqi-brand-seal {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 0.8rem;
}
.culqi-logo-text {
  font-weight: 800;
  color: #0f172a;
  font-size: 0.95rem;
}
.culqi-dot {
  color: #ff6a00;
}
.culqi-credisello {
  color: #64748b;
  font-size: 0.75rem;
  border-left: 1px solid #cbd5e1;
  padding-left: 10px;
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

/* Success Overlay */
.success-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #0b0f19;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  opacity: 0;
  pointer-events: none;
  transition: all 0.5s ease;
}
.success-overlay.active {
  opacity: 1;
  pointer-events: all;
}
.success-icon {
  font-size: 5rem;
  color: var(--success-color);
  margin-bottom: 24px;
}

.btn-success {
  background: var(--success-color);
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 12px 28px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  text-decoration: none;
  margin-top: 20px;
  transition: all 0.3s ease;
}
.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
  background: #059669;
}
</style>
