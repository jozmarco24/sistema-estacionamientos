<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col">
    <!-- Header -->
    <header class="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-30">
      <div class="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <router-link to="/dashboard" class="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
          <i class="fa-solid fa-arrow-left text-slate-400 hover:text-sky-500"></i>
          <span>Volver al Dashboard</span>
        </router-link>
        <ThemeToggle />
      </div>
    </header>

    <!-- Contenido -->
    <main class="flex-1 max-w-4xl mx-auto w-full px-4 py-8">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-black text-slate-900 dark:text-white">Mis Vehículos</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Registra tus placas para reservar en 1 clic</p>
        </div>
        <button
          @click="mostrarForm = !mostrarForm"
          class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold shadow-md shadow-sky-600/20 flex items-center gap-2"
        >
          <i :class="mostrarForm ? 'fa-solid fa-xmark' : 'fa-solid fa-plus'"></i>
          <span>{{ mostrarForm ? 'Cancelar' : 'Agregar Vehículo' }}</span>
        </button>
      </div>

      <!-- Formulario Agregar Vehículo Inline -->
      <div v-if="mostrarForm" class="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-lg mb-8">
        <h3 class="font-bold text-sm text-slate-900 dark:text-white mb-4">Nuevo Vehículo</h3>
        <form @submit.prevent="guardarVehiculo" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Placa *</label>
            <input v-model="form.placa" required type="text" placeholder="ABC-123" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono uppercase text-slate-900 dark:text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Marca *</label>
            <input v-model="form.marca" required type="text" placeholder="Toyota" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Modelo *</label>
            <input v-model="form.modelo" required type="text" placeholder="Corolla" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Color *</label>
            <input v-model="form.color" required type="text" placeholder="Gris Plata" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white" />
          </div>
          <div class="sm:col-span-2 md:col-span-4 flex justify-end gap-2 pt-2">
            <button type="submit" :disabled="guardando" class="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold shadow">
              <i v-if="guardando" class="fa-solid fa-spinner fa-spin mr-1"></i>
              Guardar Vehículo
            </button>
          </div>
        </form>
      </div>

      <!-- Estado Vacío -->
      <div v-if="vehiculos.length === 0 && !loading" class="text-center py-16 p-8 rounded-3xl border border-dashed border-slate-300 dark:border-slate-800">
        <div class="w-16 h-16 rounded-full bg-sky-500/10 text-sky-500 flex items-center justify-center mx-auto text-2xl mb-4">
          <i class="fa-solid fa-car-side"></i>
        </div>
        <h3 class="text-base font-bold text-slate-800 dark:text-white">Aún no tienes vehículos registrados</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto mt-1 mb-5">
          Agrega tu auto o motocicleta para agilizar tus reservas en cualquier sede de SmartPark.
        </p>
        <button
          @click="mostrarForm = true"
          class="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold shadow"
        >
          Registrar mi primer vehículo
        </button>
      </div>

      <!-- Grid Cards de Vehículos -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <div
          v-for="v in vehiculos"
          :key="v.id"
          class="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between hover:border-sky-500/50 transition-all"
        >
          <div>
            <div class="flex items-start justify-between">
              <span class="px-3 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 font-mono font-black text-sm uppercase text-sky-600 dark:text-sky-400 tracking-wider">
                {{ v.placa }}
              </span>
              <button
                @click="eliminarVehiculo(v.id)"
                class="text-slate-400 hover:text-rose-500 p-1 transition-colors"
                title="Eliminar vehículo"
              >
                <i class="fa-regular fa-trash-can text-sm"></i>
              </button>
            </div>
            <div class="mt-4">
              <h4 class="font-bold text-base text-slate-900 dark:text-white">{{ v.marca }} {{ v.modelo }}</h4>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Color: <strong class="text-slate-700 dark:text-slate-300">{{ v.color }}</strong></p>
            </div>
          </div>
          <div class="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
            <span>Vehículo Registrado</span>
            <span class="text-emerald-500 font-bold"><i class="fa-solid fa-circle-check mr-1"></i>Habilitado</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { usuariosService } from '@/services/usuarios'
import { showToast } from '@/components/ToastAlert.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const themeStore = useThemeStore()
const vehiculos = ref([])
const loading = ref(true)
const guardando = ref(false)
const mostrarForm = ref(false)

const form = ref({
  placa: '',
  marca: '',
  modelo: '',
  color: ''
})

onMounted(async () => {
  themeStore.initTheme(false)
  await cargarVehiculos()
})

const cargarVehiculos = async () => {
  loading.value = true
  try {
    const res = await usuariosService.getMisVehiculos()
    vehiculos.value = res.data || []
  } catch (err) {
    showToast('Error cargando vehículos', 'error')
  } finally {
    loading.value = false
  }
}

const guardarVehiculo = async () => {
  guardando.value = true
  try {
    await usuariosService.crearVehiculo(form.value)
    showToast('Vehículo registrado con éxito', 'success')
    mostrarForm.value = false
    form.value = { placa: '', marca: '', modelo: '', color: '' }
    await cargarVehiculos()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Error al guardar vehículo', 'error')
  } finally {
    guardando.value = false
  }
}

const eliminarVehiculo = async (id) => {
  if (!confirm('¿Deseas retirar este vehículo de tu cuenta?')) return
  try {
    showToast('Vehículo eliminado', 'success')
    vehiculos.value = vehiculos.value.filter(v => v.id !== id)
  } catch (err) {
    showToast('Error al eliminar vehículo', 'error')
  }
}
</script>
