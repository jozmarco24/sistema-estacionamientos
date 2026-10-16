import os
import httpx
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Reserva, EstadoReserva
from schemas import (
    ReservaCreate, ReservaResponse, CancelarReservaResponse, CotizacionResponse,
    WalkinCreate, WalkinResponse, CobrarCasetaResponse
)
from auth import (
    get_current_user, require_admin, require_conductor, require_operador_or_above,
    verify_internal_key, CurrentUser
)
from time_utils import utc_now, to_utc, es_horario_diurno, get_hora_lima
from logger_config import setup_logger

from slowapi import Limiter
from slowapi.util import get_remote_address

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from circuit_breaker import http_breaker
import pybreaker

logger = setup_logger("reservas")
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/reservas", tags=["reservas"])

ESTACIONAMIENTOS_SERVICE_URL = os.getenv("ESTACIONAMIENTOS_SERVICE_URL", "http://estacionamientos:8002")
PAGOS_SERVICE_URL = os.getenv("PAGOS_SERVICE_URL", "http://pagos:8004")
INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "")

# ─────────────────────────────────────────────
# Circuit Breaker HTTP
# ─────────────────────────────────────────────
@http_breaker
def _llamada_http(url, headers, json_data=None, method="patch"):
    import httpx
    if method == "patch":
        r = httpx.patch(url, headers=headers, json=json_data, timeout=5.0)
    elif method == "get":
        r = httpx.get(url, headers=headers, timeout=5.0)
    elif method == "post":
        r = httpx.post(url, headers=headers, json=json_data, timeout=5.0)
    elif method == "put":
        r = httpx.put(url, headers=headers, json=json_data, timeout=5.0)
    else:
        r = httpx.request(method, url, headers=headers, json=json_data, timeout=5.0)
    r.raise_for_status()
    return r

# Circuit Breaker y Reintentos para llamadas externas
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type(httpx.RequestError),
    reraise=True
)
async def llamar_servicio_externo(method: str, url: str, headers: dict, json: dict = None) -> httpx.Response:
    try:
        r = _llamada_http(url, headers=headers, json_data=json, method=method.lower())
        return r
    except pybreaker.CircuitBreakerError as e:
        logger.warning("[CIRCUIT BREAKER] Servicio no disponible", extra={"url": url, "error": str(e)})
        raise httpx.RequestError(f"[CIRCUIT BREAKER] Servicio no disponible: {e}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            logger.warning("Error 5xx recibido de servicio externo", extra={"url": url, "status_code": e.response.status_code})
            raise httpx.RequestError(f"Error del servidor: {e.response.status_code}")
        return e.response
    except Exception as e:
        logger.warning(f"[HTTP] Error: {e}", extra={"url": url, "error": str(e)})
        raise httpx.RequestError(f"Error en llamada HTTP externa: {e}")

# Función de cálculo de monto en el servidor
async def calcular_monto_servidor(espacio_id: int, inicio: datetime, fin: datetime, validar_culqi: bool = True):
    inicio = to_utc(inicio)
    fin = to_utc(fin)
    if fin <= inicio:
        raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la de inicio.")
    
    try:
        resp = await llamar_servicio_externo(
            "GET",
            f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{espacio_id}",
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
        )
    except httpx.RequestError as exc:
        logger.warning("Fallo al conectar con servicio de estacionamientos tras reintentos", extra={"error": str(exc)})
        raise HTTPException(status_code=503, detail="Servicio de estacionamientos no disponible.")

    if resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Espacio no encontrado.")
    esp_data = resp.json()

    propietario_id = esp_data.get("propietario_id")
    sede_id = esp_data.get("sede_id")
    tipo_v = esp_data.get("tipo_vehiculo", "auto")

    # Verificar si el propietario tiene Culqi configurado (estricto al reservar)
    if validar_culqi and propietario_id:
        try:
            culqi_check = await llamar_servicio_externo(
                "GET",
                f"{PAGOS_SERVICE_URL}/pagos/internal/propietario/{propietario_id}/culqi-valida",
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
            )
            if culqi_check.status_code == 200 and not culqi_check.json().get("valida", False):
                raise HTTPException(
                    status_code=409,
                    detail="Este estacionamiento no tiene configuradas credenciales de Culqi activas. No puede recibir reservas en este momento."
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Error verificando Culqi de propietario", extra={"error": str(e), "propietario_id": propietario_id})

    inicio_dia = esp_data.get("hora_inicio_dia", 8)
    inicio_noche = esp_data.get("hora_inicio_noche", 20)
    es_diurno = es_horario_diurno(inicio, inicio_dia, inicio_noche)

    if tipo_v == "moto":
        tarifa_hr = esp_data.get("tarifa_moto_dia", 3.0) if es_diurno else esp_data.get("tarifa_moto_noche", 2.0)
    else:
        tarifa_hr = esp_data.get("tarifa_auto_dia", 6.0) if es_diurno else esp_data.get("tarifa_auto_noche", 4.0)

    duracion_horas = max(1.0, (fin - inicio).total_seconds() / 3600.0)
    monto_total = round(tarifa_hr * duracion_horas, 2)

    return {
        "monto": monto_total,
        "tarifa_aplicada": tarifa_hr,
        "duracion_horas": round(duracion_horas, 2),
        "es_diurno": es_diurno,
        "propietario_id": propietario_id,
        "sede_id": sede_id,
        "tipo_vehiculo": tipo_v
    }

# Endpoint de Cotización
@router.get("/cotizar", response_model=CotizacionResponse)
@limiter.limit("30/minute")
async def cotizar_reserva(
    request: Request,
    espacio_id: int,
    inicio: Optional[datetime] = None,
    fin: Optional[datetime] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
):
    dt_inicio = inicio or fecha_inicio
    dt_fin = fin or fecha_fin
    if not dt_inicio or not dt_fin:
        raise HTTPException(status_code=400, detail="Debe proporcionar fecha de inicio y fin.")
    calc = await calcular_monto_servidor(espacio_id, dt_inicio, dt_fin, validar_culqi=False)
    return CotizacionResponse(
        espacio_id=espacio_id,
        duracion_horas=calc["duracion_horas"],
        monto_estimado=calc["monto"],
        tarifa_aplicada=calc["tarifa_aplicada"],
        es_diurno=calc["es_diurno"]
    )

@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def crear_reserva(
    request: Request,
    reserva_in: ReservaCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_conductor)
):
    # Validaciones temporales
    ahora_utc = utc_now()
    f_inicio = to_utc(reserva_in.fecha_inicio)
    f_fin = to_utc(reserva_in.fecha_fin)

    # Permitir margen de 30 minutos hacia atrás para evitar problemas de desincronización de reloj
    if f_inicio < (ahora_utc - timedelta(minutes=30)):
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede estar en el pasado.")
    if f_fin <= f_inicio:
        raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la de inicio.")

    # 1. Calcular monto en el servidor y validar estado del propietario (o si tiene Culqi activo)
    calc = await calcular_monto_servidor(reserva_in.espacio_id, f_inicio, f_fin, validar_culqi=False)
    monto_calculado = calc["monto"]
    propietario_id = calc["propietario_id"]
    sede_id = calc["sede_id"]

    # 2. Bloqueo atómico en servicio de estacionamientos
    url_reserva_atomica = f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{reserva_in.espacio_id}/reservar_atomico"
    try:
        resp_est = await llamar_servicio_externo(
            "PUT",
            url_reserva_atomica,
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
        )
    except httpx.RequestError as exc:
        logger.warning("Fallo al conectar con servicio de estacionamientos tras 3 intentos", extra={"error": str(exc)})
        raise HTTPException(status_code=503, detail="Servicio de estacionamientos no disponible.")

    if resp_est.status_code == 409:
        raise HTTPException(status_code=409, detail="El espacio no está disponible en este momento.")
    elif resp_est.status_code != 200:
        raise HTTPException(status_code=resp_est.status_code, detail=f"Error bloqueando espacio: {resp_est.text}")

    # 3. Validar solapamiento de horario con reservas confirmadas
    reservas_solapadas = db.query(Reserva).filter(
        Reserva.espacio_id == reserva_in.espacio_id,
        Reserva.estado.in_([EstadoReserva.confirmada, EstadoReserva.en_curso]),
        Reserva.fecha_inicio < f_fin,
        Reserva.fecha_fin > f_inicio
    ).with_for_update().all()

    if reservas_solapadas:
        # Liberar el espacio retenido
        await liberar_espacio_remoto(reserva_in.espacio_id)
        raise HTTPException(status_code=409, detail="El espacio ya cuenta con una reserva activa en ese rango horario.")

    # 4. Guardar Reserva en estado pendiente con expiración en 10 minutos
    expira_en = ahora_utc + timedelta(minutes=10)
    nueva_reserva = Reserva(
        usuario_id=current_user.id,
        espacio_id=reserva_in.espacio_id,
        fecha_inicio=f_inicio,
        fecha_fin=f_fin,
        estado=EstadoReserva.pendiente,
        placa_vehiculo=reserva_in.placa_vehiculo.strip().upper(),
        creado_en=ahora_utc,
        expira_en=expira_en
    )

    try:
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
    except Exception as exc:
        db.rollback()
        await liberar_espacio_remoto(reserva_in.espacio_id)
        raise HTTPException(status_code=500, detail=f"Error al registrar reserva: {str(exc)}")

    # 5. Notificar al servicio de pagos para crear la orden de pago pendiente
    url_pago = f"{PAGOS_SERVICE_URL}/pagos/"
    pago_payload = {
        "tipo": "reserva",
        "reserva_id": nueva_reserva.id,
        "sede_id": sede_id,
        "pagador_id": current_user.id,
        "receptor_id": propietario_id,
        "monto": monto_calculado,
        "metodo_pago": reserva_in.metodo_pago or "tarjeta",
        "estado": "pendiente"
    }

    pago_creado = False
    try:
        resp_p = await llamar_servicio_externo(
            "POST",
            url_pago,
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY},
            json=pago_payload
        )
        if resp_p.status_code == 201:
            pago_creado = True
    except Exception as err:
        logger.warning("Fallo al crear pago tras reintentos", extra={"error": str(err)})

    # Compensación estricta si no se pudo crear el pago
    if not pago_creado:
        nueva_reserva.estado = EstadoReserva.cancelada
        db.commit()
        await liberar_espacio_remoto(reserva_in.espacio_id)
        raise HTTPException(status_code=500, detail="No se pudo inicializar la orden de pago. La reserva fue cancelada y el espacio liberado.")

    return nueva_reserva

# Función auxiliar de compensación para liberar espacio
async def liberar_espacio_remoto(espacio_id: int):
    try:
        await llamar_servicio_externo(
            "PUT",
            f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{espacio_id}/liberar",
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
        )
    except Exception as e:
        logger.warning("Error liberando espacio remoto tras reintentos", extra={"espacio_id": espacio_id, "error": str(e)})

# Cancelar Reserva
@router.put("/{reserva_id}/cancelar", response_model=CancelarReservaResponse)
async def cancelar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if current_user.rol != "admin" and reserva.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para cancelar esta reserva")

    if reserva.estado in [EstadoReserva.cancelada, EstadoReserva.finalizada]:
        raise HTTPException(status_code=409, detail="La reserva ya se encuentra cancelada o finalizada")

    if reserva.estado == EstadoReserva.confirmada:
        raise HTTPException(status_code=409, detail="No se puede cancelar una reserva confirmada")

    reserva.estado = EstadoReserva.cancelada
    db.commit()
    db.refresh(reserva)

    await liberar_espacio_remoto(reserva.espacio_id)

    return CancelarReservaResponse(
        mensaje="Reserva cancelada con éxito. Espacio liberado.",
        reserva=ReservaResponse.model_validate(reserva)
    )

# Listar Reservas (Con paginación y filtrado estricto por rol)
@router.get("/", response_model=dict)
def listar_reservas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    query = db.query(Reserva)
    if current_user.rol == "conductor":
        query = query.filter(Reserva.usuario_id == current_user.id)
    
    total = query.count()
    items = query.order_by(Reserva.id.desc()).offset(skip).limit(limit).all()
    data = [ReservaResponse.model_validate(r) for r in items]
    return {"total": total, "skip": skip, "limit": limit, "data": data}

# Obtener detalle de una reserva específica
@router.get("/{reserva_id}", response_model=ReservaResponse)
def obtener_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[CurrentUser] = Depends(get_current_user),
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key")
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if x_internal_key == INTERNAL_SERVICE_KEY:
        return reserva

    if not current_user:
        raise HTTPException(status_code=401, detail="No autenticado")

    if current_user.rol != "admin" and reserva.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado a esta reserva")

    return reserva

@router.get("/usuario/{usuario_id}", response_model=List[ReservaResponse])
def listar_reservas_por_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.rol != "admin" and current_user.id != usuario_id:
        raise HTTPException(status_code=403, detail="Acceso denegado a las reservas de otro usuario")
    return db.query(Reserva).filter(Reserva.usuario_id == usuario_id).order_by(Reserva.id.desc()).all()

# Máquina de estados validada
@router.put("/{reserva_id}/estado", response_model=ReservaResponse)
async def actualizar_estado_reserva(
    reserva_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: Optional[CurrentUser] = Depends(get_current_user),
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key")
):
    # Permitir llamada interna o de operador/admin
    is_internal = (x_internal_key == INTERNAL_SERVICE_KEY)
    if not is_internal:
        if not current_user or current_user.rol not in ["admin", "operador"]:
            raise HTTPException(status_code=403, detail="Solo llamadas internas, operadores o administradores pueden cambiar el estado")

    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    nuevo_estado = (payload.get("estado") or "").lower()
    estado_actual = reserva.estado.value

    # Máquina de Estados Validados:
    # pendiente -> confirmada | cancelada | fallida
    # confirmada -> en_curso | cancelada
    # en_curso -> finalizada
    transiciones_validas = {
        "pendiente": ["confirmada", "cancelada", "fallida"],
        "confirmada": ["en_curso", "cancelada"],
        "en_curso": ["finalizada"],
        "cancelada": [],
        "fallida": ["confirmada"],
        "finalizada": []
    }

    if nuevo_estado not in transiciones_validas.get(estado_actual, []):
        raise HTTPException(
            status_code=400,
            detail=f"Transición de estado inválida: no se puede pasar de '{estado_actual}' a '{nuevo_estado}'"
        )

    reserva.estado = EstadoReserva(nuevo_estado)
    db.commit()
    db.refresh(reserva)

    # Si pasa a cancelada, fallida o finalizada, liberar espacio
    if nuevo_estado in ["cancelada", "fallida", "finalizada"]:
        await liberar_espacio_remoto(reserva.espacio_id)

    return reserva

# Expiración interna (llamada desde tarea en segundo plano)
@router.put("/{reserva_id}/expirar-interno")
async def expirar_reserva_tiempo_interno(
    reserva_id: int,
    db: Session = Depends(get_db),
    _internal: bool = Depends(verify_internal_key)
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    if reserva.estado == EstadoReserva.pendiente:
        reserva.estado = EstadoReserva.cancelada
        db.commit()
        await liberar_espacio_remoto(reserva.espacio_id)
        return {"mensaje": "Reserva expirada por tiempo y espacio liberado"}
    return {"mensaje": "Reserva no requerida de expiración"}

# Expiración solicitada por el cliente autenticado (ej. timeout de pago en frontend)
@router.put("/{reserva_id}/expirar")
async def expirar_reserva_cliente(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    if current_user.rol != "admin" and reserva.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para modificar esta reserva")

    if reserva.estado == EstadoReserva.pendiente:
        reserva.estado = EstadoReserva.cancelada
        db.commit()
        await liberar_espacio_remoto(reserva.espacio_id)
        return {"mensaje": "Reserva expirada por límite de tiempo y espacio liberado con éxito"}
    return {"mensaje": f"La reserva ya no se encuentra pendiente (estado actual: {reserva.estado.value})"}

# ─────────────────────────────────────────────
# Extender plazo de expiración (llamada interna desde pagos antes de cobrar con Culqi)
# ─────────────────────────────────────────────
@router.patch("/{reserva_id}/extender-expiracion")
async def extender_expiracion(
    reserva_id: int,
    db: Session = Depends(get_db),
    _internal: bool = Depends(verify_internal_key)
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if reserva and reserva.estado == EstadoReserva.pendiente:
        reserva.expira_en = utc_now() + timedelta(minutes=10)
        db.commit()
    return {"ok": True}

# ─────────────────────────────────────────────
# Función auxiliar para verificar si el espacio sigue libre y no se solapa
# ─────────────────────────────────────────────
async def verificar_espacio_disponible(espacio_id: int, inicio: datetime, fin: datetime, db: Session, reserva_id_actual: int) -> bool:
    # 1. Verificar estado del espacio en el servicio de estacionamientos
    async with httpx.AsyncClient(timeout=6.0) as client:
        try:
            resp_disp = await client.get(f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{espacio_id}/disponibilidad")
            if resp_disp.status_code != 200:
                return False
            data = resp_disp.json()
            # Si está ocupado o reservado por otro proceso directo, no está libre
            if data.get("estado") not in ["libre", "bloqueado"]:
                return False
        except Exception as e:
            logger.warning("Error consultando disponibilidad remota", extra={"espacio_id": espacio_id, "error": str(e)})
            return False

    # 2. Verificar que no exista otra reserva activa confirmada en ese rango
    solapada = db.query(Reserva).filter(
        Reserva.id != reserva_id_actual,
        Reserva.espacio_id == espacio_id,
        Reserva.estado.in_([EstadoReserva.confirmada, EstadoReserva.en_curso]),
        Reserva.fecha_inicio < fin,
        Reserva.fecha_fin > inicio
    ).first()

    return solapada is None

# ─────────────────────────────────────────────
# Confirmar reserva tras pago exitoso (llamada interna desde pagos-service o webhook)
# ─────────────────────────────────────────────
@router.patch("/{reserva_id}/confirmar")
async def confirmar_reserva_tras_pago(
    reserva_id: int,
    db: Session = Depends(get_db),
    _internal: bool = Depends(verify_internal_key)
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.estado == EstadoReserva.confirmada:
        # Idempotente: ya estaba confirmada, no hacer nada
        return {"ok": True, "estado": "confirmada", "mensaje": "La reserva ya estaba confirmada."}

    # Si la reserva fue cancelada por expiración tardía, intentar recuperarla si el espacio sigue disponible
    if reserva.estado == EstadoReserva.cancelada:
        disponible = await verificar_espacio_disponible(reserva.espacio_id, reserva.fecha_inicio, reserva.fecha_fin, db, reserva.id)
        if not disponible:
            raise HTTPException(409, "El espacio ya fue tomado por otra reserva. Se requiere reembolso.")
        logger.info("Recuperando reserva cancelada tras cobro tardío exitoso", extra={"reserva_id": reserva.id})

    elif reserva.estado not in (EstadoReserva.pendiente, EstadoReserva.fallida):
        raise HTTPException(
            status_code=409,
            detail=f"No se puede confirmar una reserva en estado '{reserva.estado.value}'."
        )

    reserva.estado = EstadoReserva.confirmada
    reserva.expira_en = None  # ← Cancelar la expiración de 10 minutos
    db.commit()
    db.refresh(reserva)

    # Notificar a estacionamientos que el espacio pasa a "reservado"
    async with httpx.AsyncClient(timeout=6.0) as client:
        try:
            await client.put(
                f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{reserva.espacio_id}/reservar",
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
            )
        except httpx.RequestError as exc:
            logger.warning("Reserva confirmada pero error al marcar espacio como reservado", extra={"reserva_id": reserva_id, "error": str(exc)})

    return {"ok": True, "estado": "confirmada", "reserva_id": reserva_id}

# ─────────────────────────────────────────────
# Marcar reserva como fallida tras pago fallido o cancelado (llamada interna desde pagos-service o webhook)
# ─────────────────────────────────────────────
@router.patch("/{reserva_id}/fallar")
async def fallar_reserva_tras_pago(
    reserva_id: int,
    db: Session = Depends(get_db),
    _internal: bool = Depends(verify_internal_key)
):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.estado == EstadoReserva.fallida:
        return {"ok": True, "estado": "fallida", "mensaje": "La reserva ya estaba marcada como fallida."}

    reserva.estado = EstadoReserva.fallida
    reserva.expira_en = None
    db.commit()
    db.refresh(reserva)

    # Liberar el cajón de vuelta a "libre" (DISPONIBLE)
    await liberar_espacio_remoto(reserva.espacio_id)

    return {"ok": True, "estado": "fallida", "reserva_id": reserva_id}


# ─────────────────────────────────────────────
# ENDPOINTS PARA OPERADOR DE CASETA
# ─────────────────────────────────────────────

@router.post("/walkin", status_code=status.HTTP_201_CREATED, tags=["reservas"])
async def walkin_ingreso(
    walkin_in: WalkinCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_operador_or_above)
):
    """Registra ingreso presencial (walk-in) sin pago previo. Solo operadores."""
    ahora_utc = utc_now()

    # 1. Verificar que el espacio existe y está libre
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(
            f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{walkin_in.espacio_id}",
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Espacio no encontrado.")
        espacio = resp.json()

    if espacio.get("estado") not in ["libre"]:
        raise HTTPException(status_code=409, detail=f"El cajón no está libre. Estado actual: {espacio.get('estado')}")

    # 2. Bloquear/ocupar el espacio atómicamente
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp_bloqueo = await client.put(
            f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{walkin_in.espacio_id}/ocupar",
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
        )
        if resp_bloqueo.status_code == 409:
            raise HTTPException(status_code=409, detail="El cajón fue tomado por otro proceso. Intente de nuevo.")
        elif resp_bloqueo.status_code not in [200, 204]:
            raise HTTPException(status_code=502, detail="Error al ocupar el espacio.")

    # 3. Crear reserva en estado "en_curso" (ya está dentro)
    nueva_reserva = Reserva(
        usuario_id=current_user.id,
        espacio_id=walkin_in.espacio_id,
        fecha_inicio=ahora_utc,
        fecha_fin=ahora_utc + timedelta(hours=24),  # placeholder, se calcula al cobrar
        estado=EstadoReserva.en_curso,
        placa_vehiculo=walkin_in.placa_vehiculo.strip().upper(),
        creado_en=ahora_utc,
        expira_en=None,
        monto_cobrado=0.0
    )

    try:
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
    except Exception as exc:
        db.rollback()
        await liberar_espacio_remoto(walkin_in.espacio_id)
        raise HTTPException(status_code=500, detail=f"Error al registrar ingreso: {str(exc)}")

    return {
        "id": nueva_reserva.id,
        "espacio_id": nueva_reserva.espacio_id,
        "placa_vehiculo": nueva_reserva.placa_vehiculo,
        "estado": nueva_reserva.estado,
        "fecha_inicio": nueva_reserva.fecha_inicio,
        "mensaje": "Ingreso walk-in registrado correctamente"
    }


@router.post("/{reserva_id}/cobrar-caseta", tags=["reservas"])
async def cobrar_caseta(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_operador_or_above)
):
    """Calcula tiempo real, registra cobro y libera el espacio. Solo operadores."""
    ahora_utc = utc_now()

    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    if reserva.estado not in [EstadoReserva.en_curso, EstadoReserva.confirmada]:
        raise HTTPException(
            status_code=409,
            detail=f"No se puede cobrar una reserva en estado '{reserva.estado}'. Debe estar en_curso o confirmada."
        )

    # Calcular tiempo real de permanencia con to_utc
    inicio_real = to_utc(reserva.fecha_inicio)
    duracion_segundos = max(0.0, (ahora_utc - inicio_real).total_seconds())
    duracion_horas = max(0.5, duracion_segundos / 3600.0)  # mínimo 30 minutos

    # Obtener tarifa del espacio
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(
            f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{reserva.espacio_id}",
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Espacio no encontrado para calcular tarifa.")
        espacio = resp.json()

    inicio_dia = espacio.get("hora_inicio_dia", 8)
    inicio_noche = espacio.get("hora_inicio_noche", 20)
    es_diurno = es_horario_diurno(inicio_real, inicio_dia, inicio_noche)
    tipo_v = espacio.get("tipo_vehiculo", "auto")

    if tipo_v == "moto":
        tarifa_hr = espacio.get("tarifa_moto_dia", 3.0) if es_diurno else espacio.get("tarifa_moto_noche", 2.0)
    else:
        tarifa_hr = espacio.get("tarifa_auto_dia", 6.0) if es_diurno else espacio.get("tarifa_auto_noche", 4.0)

    monto_cobrado = round(tarifa_hr * duracion_horas, 2)

    # Actualizar reserva: estado completada, fecha_fin real, monto
    reserva.estado = EstadoReserva.completada
    reserva.fecha_fin = ahora_utc
    try:
        if hasattr(reserva, 'monto_cobrado'):
            reserva.monto_cobrado = monto_cobrado
    except Exception:
        pass

    try:
        db.commit()
        db.refresh(reserva)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar cobro: {str(exc)}")

    # Liberar espacio en microservicio de estacionamientos
    await liberar_espacio_remoto(reserva.espacio_id)

    # Notificar al servicio de pagos en background o directo
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            resp_pago = await client.post(
                f"{PAGOS_SERVICE_URL}/pagos/",
                json={
                    "tipo": "reserva",
                    "reserva_id": reserva.id,
                    "pagador_id": reserva.usuario_id,
                    "receptor_id": espacio.get("propietario_id"),
                    "sede_id": espacio.get("sede_id"),
                    "monto": monto_cobrado,
                    "metodo_pago": "efectivo",
                    "estado": "pagado"
                },
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
            )
            if resp_pago.status_code not in (200, 201):
                logger.warning(f"Error creando pago: {resp_pago.status_code} {resp_pago.text}")
        except Exception as e:
            logger.warning(f"Error registrando pago en caja: {e}")

    return {
        "reserva_id": reserva.id,
        "placa_vehiculo": reserva.placa_vehiculo,
        "monto_cobrado": monto_cobrado,
        "duracion_horas": round(duracion_horas, 2),
        "fecha_inicio": inicio_real,
        "fecha_salida": ahora_utc,
        "mensaje": f"Cobro de S/. {monto_cobrado:.2f} registrado. Cajón liberado."
    }


@router.post("/{reserva_id}/liberar-manual", tags=["reservas"])
async def liberar_manual(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_operador_or_above)
):
    """Libera un cajón manualmente sin cobro (salida sin pago / error operativo)."""
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    reserva.estado = EstadoReserva.cancelada
    reserva.fecha_fin = utc_now()

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al liberar: {str(exc)}")

    await liberar_espacio_remoto(reserva.espacio_id)

    return {"mensaje": f"Cajón del espacio {reserva.espacio_id} liberado manualmente.", "reserva_id": reserva_id}


@router.post("/limpiar-expiradas", tags=["reservas"])
async def limpiar_reservas_expiradas(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_operador_or_above)
):
    """Cancela reservas pendientes expiradas y libera sus espacios."""
    ahora_utc = utc_now()
    expiradas = db.query(Reserva).filter(
        Reserva.estado == EstadoReserva.pendiente,
        Reserva.expira_en < ahora_utc
    ).all()

    liberadas = []
    for r in expiradas:
        r.estado = EstadoReserva.cancelada
        liberadas.append(r.espacio_id)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al limpiar: {str(exc)}")

    for espacio_id in liberadas:
        try:
            await liberar_espacio_remoto(espacio_id)
        except Exception:
            pass

    return {"mensaje": f"{len(liberadas)} reservas expiradas canceladas.", "espacios_liberados": liberadas}

