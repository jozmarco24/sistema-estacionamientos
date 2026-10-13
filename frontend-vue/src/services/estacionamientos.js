import api, { URLS } from './api'

export const estacionamientosService = {
  getSedes(skip = 0, limit = 100) {
    return api.get(`${URLS.estacionamientos}/sedes/?skip=${skip}&limit=${limit}`)
  },
  getSede(id) {
    return api.get(`${URLS.estacionamientos}/sedes/${id}`)
  },
  getSedesCercanas(lat, lon) {
    return api.get(`${URLS.estacionamientos}/sedes/cercanas?lat=${lat}&lon=${lon}`)
  },
  getSedesPorPropietario(propietarioId) {
    return api.get(`${URLS.estacionamientos}/sedes/propietario/${propietarioId}`)
  },
  crearSede(data) {
    return api.post(`${URLS.estacionamientos}/sedes/`, data)
  },
  actualizarSede(id, data) {
    return api.put(`${URLS.estacionamientos}/sedes/${id}`, data)
  },
  toggleEstadoSede(id, activa) {
    return api.put(`${URLS.estacionamientos}/sedes/${id}/estado`, { activa })
  },
  getEspacios(skip = 0, limit = 100) {
    return api.get(`${URLS.estacionamientos}/espacios/?skip=${skip}&limit=${limit}`)
  },
  getEspaciosPorSede(sedeId, skip = 0, limit = 100) {
    return api.get(`${URLS.estacionamientos}/espacios/sede/${sedeId}?skip=${skip}&limit=${limit}`)
  },
  crearEspacio(data) {
    return api.post(`${URLS.estacionamientos}/espacios/`, data)
  },
  crearEspaciosLote(data) {
    return api.post(`${URLS.estacionamientos}/espacios/lote`, data)
  },
  actualizarEstadoEspacio(id, estado) {
    return api.put(`${URLS.estacionamientos}/espacios/${id}/estado`, { estado })
  },
  getIncidencias(skip = 0, limit = 50) {
    return api.get(`${URLS.estacionamientos}/incidencias/?skip=${skip}&limit=${limit}`)
  },
  crearIncidencia(data) {
    return api.post(`${URLS.estacionamientos}/incidencias/`, data)
  },
  health() {
    return api.get(`${URLS.estacionamientos}/health`)
  }
}
