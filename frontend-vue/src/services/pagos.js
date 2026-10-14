import api, { URLS } from './api'

export const pagosService = {
  getPagos(skip = 0, limit = 100) {
    return api.get(`${URLS.pagos}/pagos/?skip=${skip}&limit=${limit}`)
  },
  getPagosPorPropietario(propietarioId, skip = 0, limit = 100) {
    return api.get(`${URLS.pagos}/pagos/propietario/${propietarioId}?skip=${skip}&limit=${limit}`)
  },
  getPagosPorReserva(reservaId) {
    return api.get(`${URLS.pagos}/pagos/reserva/${reservaId}`)
  },
  getConfigPublica(pagoId = null) {
    const url = pagoId ? `${URLS.pagos}/pagos/config-publica?pago_id=${pagoId}` : `${URLS.pagos}/pagos/config-publica`
    return api.get(url)
  },
  crearPago(data) {
    return api.post(`${URLS.pagos}/pagos/`, data)
  },
  cobrarCulqi(data) {
    return api.post(`${URLS.pagos}/pagos/culqi/cobrar`, data)
  },
  getCredencialesEstado() {
    return api.get(`${URLS.pagos}/credenciales/estado`)
  },
  guardarCredenciales(data) {
    return api.post(`${URLS.pagos}/credenciales/`, data)
  },
  verificarCredenciales() {
    return api.post(`${URLS.pagos}/credenciales/verificar`)
  },
  health() {
    return api.get(`${URLS.pagos}/health`)
  }
}
