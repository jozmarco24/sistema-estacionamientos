import api, { URLS } from './api'

export const usuariosService = {
  login(email, password) {
    return api.post(`${URLS.usuarios}/usuarios/login`, { email, password })
  },
  registro(data) {
    return api.post(`${URLS.usuarios}/usuarios/registro`, data)
  },
  getMe() {
    return api.get(`${URLS.usuarios}/usuarios/perfil`)
  },
  getUsuarios(skip = 0, limit = 100) {
    return api.get(`${URLS.usuarios}/usuarios/?skip=${skip}&limit=${limit}`)
  },
  getPropietarios() {
    return api.get(`${URLS.usuarios}/usuarios/propietarios`)
  },
  crearPropietario(data) {
    return api.post(`${URLS.usuarios}/usuarios/propietarios`, data)
  },
  actualizarPropietario(id, data) {
    return api.put(`${URLS.usuarios}/usuarios/propietarios/${id}`, data)
  },
  toggleActivoPropietario(id) {
    return api.put(`${URLS.usuarios}/usuarios/propietarios/${id}/toggle-activo`)
  },
  getOperadores() {
    return api.get(`${URLS.usuarios}/usuarios/operadores`)
  },
  crearOperador(data) {
    return api.post(`${URLS.usuarios}/usuarios/operadores`, data)
  },
  toggleActivoOperador(id) {
    return api.put(`${URLS.usuarios}/usuarios/operadores/${id}/toggle-activo`)
  },
  eliminarOperador(id) {
    return api.delete(`${URLS.usuarios}/usuarios/operadores/${id}`)
  },
  getMisVehiculos() {
    return api.get(`${URLS.usuarios}/usuarios/vehiculos`)
  },
  crearVehiculo(data) {
    return api.post(`${URLS.usuarios}/usuarios/vehiculos`, data)
  },
  getPlanes() {
    return api.get(`${URLS.usuarios}/usuarios/planes`)
  },
  crearPlan(data) {
    return api.post(`${URLS.usuarios}/usuarios/planes`, data)
  },
  actualizarPlan(id, data) {
    return api.put(`${URLS.usuarios}/usuarios/planes/${id}`, data)
  },
  getSuscripcionesTodas() {
    return api.get(`${URLS.usuarios}/usuarios/suscripciones/todas`)
  },
  actualizarSuscripcionEstado(id, data) {
    return api.put(`${URLS.usuarios}/usuarios/suscripciones/${id}/estado`, data)
  },
  cambiarPlanMembresia(data) {
    return api.post(`${URLS.usuarios}/membresias/cambiar-plan`, data)
  },
  getMiSuscripcion() {
    return api.get(`${URLS.usuarios}/usuarios/suscripcion/actual`)
  },
  comprarSuscripcion(planId) {
    return api.post(`${URLS.usuarios}/usuarios/suscripcion/comprar?plan_id=${planId}`)
  },
  health() {
    return api.get(`${URLS.usuarios}/health`)
  }
}
