<template>
  <div class="google-button-container flex justify-center w-full min-h-[44px]">
    <div ref="googleBtnRef" class="w-full flex justify-center"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import api, { URLS } from '@/services/api'

const emit = defineEmits(['success', 'error'])

const googleBtnRef = ref(null)
let pollInterval = null

async function handleCredentialResponse(response) {
  if (!response || !response.credential) {
    emit('error', 'No se recibió la credencial de Google.')
    return
  }

  try {
    const res = await api.post(`${URLS.usuarios}/usuarios/auth/google`, {
      credential: response.credential
    })
    emit('success', res.data)
  } catch (err) {
    const detail = err.response?.data?.detail
    const msg = typeof detail === 'string' ? detail : (err.message || 'Error al autenticar con Google')
    emit('error', msg)
  }
}

function initGoogleButton() {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

  if (!clientId) {
    // Si no está configurado el client ID, se notifica pero no rompe la interfaz
    return
  }

  if (window.google?.accounts?.id && googleBtnRef.value) {
    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true
      })

      // Limpiar contenedor previo si existe
      googleBtnRef.value.innerHTML = ''

      const containerWidth = Math.min(googleBtnRef.value?.offsetWidth || 340, 400)
      window.google.accounts.id.renderButton(googleBtnRef.value, {
        type: 'standard',
        theme: 'outline',
        size: 'large',
        text: 'continue_with',
        shape: 'rectangular',
        logo_alignment: 'left',
        width: containerWidth > 0 ? containerWidth : 340,
        locale: 'es'
      })
    } catch (e) {
      console.error('Error al inicializar Google Sign-In:', e)
    }
  }
}

onMounted(() => {
  if (window.google?.accounts?.id) {
    initGoogleButton()
  } else {
    // Polling esperando la carga del script asíncrono
    let attempts = 0
    pollInterval = setInterval(() => {
      attempts++
      if (window.google?.accounts?.id) {
        clearInterval(pollInterval)
        pollInterval = null
        initGoogleButton()
      } else if (attempts >= 40) { // 8 segundos max
        clearInterval(pollInterval)
        pollInterval = null
      }
    }, 200)
  }
})

onBeforeUnmount(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
})
</script>

<style scoped>
.google-button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}
.google-button-container :deep(iframe) {
  margin: 0 auto !important;
}
</style>
