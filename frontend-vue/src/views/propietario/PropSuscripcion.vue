<template>
  <div class="section-view active-section">
    <div class="two-cols">
      <!-- Estado y Límites -->
      <div class="card">
        <h2 class="card-title"><i class="fa-solid fa-id-card"></i> Estado de tu Membresía</h2>
        <div class="suscripcion-status-card">
          <template v-if="suscripcionActual">
            <h3><i class="fa-solid fa-circle-check" style="color:var(--color-libre);"></i> Suscripción {{ (suscripcionActual.estado || '').toUpperCase() }}</h3>
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
import { reactive, watch } from 'vue'
import { usuariosService } from '@/services/usuarios'
import { pagosService } from '@/services/pagos'
import api, { URLS } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  suscripcionActual: { type: Object, default: null },
  planesDisponibles: { type: Array, default: () => [] },
  misSedes: { type: Array, default: () => [] },
  operadoresList: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh', 'toast'])

const authStore = useAuthStore()

const planLimites = reactive({ max_sedes: 1, max_operadores: 2 })

const modalPago = reactive({
  open: false,
  id: null,
  nombre: '',
  precio: 0,
  loading: false
})

let culqiSuscripcionPagoId = null

watch(() => props.suscripcionActual, (sub) => {
  if (sub && sub.plan_id && props.planesDisponibles.length > 0) {
    const pl = props.planesDisponibles.find(p => p.id === sub.plan_id)
    if (pl) {
      planLimites.max_sedes = pl.max_sedes || 1
      planLimites.max_operadores = pl.max_operadores || 2
    }
  }
}, { immediate: true, deep: true })

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

function openPaymentModal(p) {
  modalPago.id = p.id
  modalPago.nombre = p.nombre
  modalPago.precio = Number(p.precio)
  modalPago.open = true

  if (!window.Culqi && !document.getElementById('culqi-checkout-script')) {
    const s = document.createElement('script')
    s.id = 'culqi-checkout-script'
    s.src = 'https://checkout.culqi.com/js/v4'
    document.head.appendChild(s)
  }
}

async function procesarCheckoutSuscripcion() {
  modalPago.loading = true
  try {
    const res = await usuariosService.comprarSuscripcion(modalPago.id)
    const subData = res.data

    culqiSuscripcionPagoId = subData.pago_id
    if (!culqiSuscripcionPagoId) {
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

    const resCfg = await pagosService.getConfigPublica(culqiSuscripcionPagoId)
    const cfgData = resCfg.data
    const plataformaPublicKey = cfgData.public_key
    const montoCentimos = Math.round(cfgData.monto * 100)

    if (!window.Culqi) {
      throw new Error("La pasarela Culqi no cargó correctamente en el navegador.")
    }

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

    window.culqi = async function() {
      if (window.Culqi.token) {
        const tokenId = window.Culqi.token.id
        const emailCliente = window.Culqi.token.email || authStore.user?.email || 'propietario@smartpark.com'
        window.Culqi.close()
        emit('toast', { msg: "Procesando cobro de suscripción con Culqi..." })

        try {
          await pagosService.cobrarCulqi({
            pago_id: culqiSuscripcionPagoId,
            token_id: tokenId,
            email: emailCliente
          })
          emit('toast', { msg: "¡Pago aprobado con éxito! Tu plan SaaS ha sido activado." })
          emit('refresh')
        } catch (err) {
          emit('toast', { msg: err.response?.data?.detail || err.message || 'El cobro no fue aprobado por Culqi', isError: true })
        }
      } else if (window.Culqi.error) {
        emit('toast', { msg: `Error Culqi: ${window.Culqi.error.user_message || 'Transacción cancelada'}`, isError: true })
      }
    }

    modalPago.open = false
    window.Culqi.open()

  } catch (err) {
    emit('toast', { msg: err.response?.data?.detail || err.message || 'Error al procesar suscripción', isError: true })
  } finally {
    modalPago.loading = false
  }
}
</script>
