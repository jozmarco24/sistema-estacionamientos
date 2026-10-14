import api, { URLS } from './api'

export const reservasService = {
  getReservas(skip = 0, limit = 100) {
    return api.get(`${URLS.reservas}/reservas/?skip=${skip}&limit=${limit}`)
  },
  getReserva(id) {
    return api.get(`${URLS.reservas}/reservas/${id}`)
  },
  getReservasPorUsuario(usuarioId) {
    return api.get(`${URLS.reservas}/reservas/usuario/${usuarioId}`)
  },
  cotizar(espacioId, inicio, fin) {
    let url = `${URLS.reservas}/reservas/cotizar?espacio_id=${espacioId}`
    if (inicio) url += `&fecha_inicio=${encodeURIComponent(inicio)}`
    if (fin) url += `&fecha_fin=${encodeURIComponent(fin)}`
    return api.get(url)
  },
  crearReserva(data) {
    return api.post(`${URLS.reservas}/reservas/`, data)
  },
  cancelarReserva(id) {
    return api.put(`${URLS.reservas}/reservas/${id}/cancelar`)
  },
  confirmarReserva(id) {
    return api.patch(`${URLS.reservas}/reservas/${id}/confirmar`)
  },
  actualizarEstado(id, estado) {
    return api.patch(`${URLS.reservas}/reservas/${id}/estado`, { estado })
  },
  health() {
    return api.get(`${URLS.reservas}/health`)
  }
}
