import os
import httpx
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Reserva, EstadoReserva
from schemas import ReservaCreate, ReservaResponse, CancelarReservaResponse, CotizacionResponse
from auth import (
    get_current_user, require_admin, require_conductor,
    verify_internal_key, CurrentUser
)
from time_utils import utc_now, to_utc, es_horario_diurno, get_hora_lima

router = APIRouter(prefix="/reservas", tags=["reservas"])

ESTACIONAMIENTOS_SERVICE_URL = os.getenv("ESTACIONAMIENTOS_SERVICE_URL", "http://estacionamientos:8002")
PAGOS_SERVICE_URL = os.getenv("PAGOS_SERVICE_URL", "http://pagos:8004")
INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "")

# Función de cálculo de monto en el servidor
async def calcular_monto_servidor(espacio_id: int, inicio: datetime, fin: datetime, validar_culqi: bool = True):
    if fin <= inicio:
        raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la de inicio.")
    
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(
            f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{espacio_id}",
            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Espacio no encontrado.")
        esp_data = resp.json()

    propietario_id = esp_data.get("propietario_id")
    sede_id = esp_data.get("sede_id")
    tipo_v = esp_data.get("tipo_vehiculo", "auto")

    # Verificar si el propietario tiene Culqi configurado (estricto al reservar)
    if validar_culqi and propietario_id:
        async with httpx.AsyncClient(timeout=6.0) as client:
            try:
                culqi_check = await client.get(
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
                print(f"Error verificando Culqi de propietario: {e}")

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
async def cotizar_reserva(
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

# Crear Reserva (Conductor logueado)
@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def crear_reserva(
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
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp_est = await client.put(
                url_reserva_atomica,
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error conectando con estacionamientos: {str(exc)}")

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
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            resp_p = await client.post(
                url_pago,
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY},
                json=pago_payload
            )
            if resp_p.status_code == 201:
                pago_creado = True
        except Exception as err:
            print(f"Error al crear pago en microservicio: {err}")

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
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.put(
                f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{espacio_id}/liberar",
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
            )
    except Exception as e:
        print(f"Error liberando espacio remoto {espacio_id}: {e}")

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
        raise HTTPException(status_code=400, detail="La reserva ya se encuentra cancelada o finalizada")

    reserva.estado = EstadoReserva.cancelada
    db.commit()
    db.refresh(reserva)

    await liberar_espacio_remoto(reserva.espacio_id)

    return CancelarReservaResponse(
        mensaje="Reserva cancelada con éxito. Espacio liberado.",
        reserva=ReservaResponse.model_validate(reserva)
    )

# Listar Reservas (Con filtrado estricto por rol)
@router.get("/", response_model=List[ReservaResponse])
def listar_reservas(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.rol == "admin":
        return db.query(Reserva).order_by(Reserva.id.desc()).all()
    elif current_user.rol == "conductor":
        return db.query(Reserva).filter(Reserva.usuario_id == current_user.id).order_by(Reserva.id.desc()).all()
    else:
        # Para operador o propietario se retornan las reservas registradas
        return db.query(Reserva).order_by(Reserva.id.desc()).all()

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
    # pendiente -> confirmada | cancelada
    # confirmada -> en_curso | cancelada
    # en_curso -> finalizada
    transiciones_validas = {
        "pendiente": ["confirmada", "cancelada"],
        "confirmada": ["en_curso", "cancelada"],
        "en_curso": ["finalizada"],
        "cancelada": [],
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

    # Si pasa a cancelada o finalizada, liberar espacio
    if nuevo_estado in ["cancelada", "finalizada"]:
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
# NUEVO: Confirmar reserva tras pago exitoso (llamada interna desde pagos-service)
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

    if reserva.estado not in (EstadoReserva.pendiente,):
        raise HTTPException(
            status_code=409,
            detail=f"No se puede confirmar una reserva en estado '{reserva.estado.value}'."
        )

    reserva.estado = EstadoReserva.confirmada
    reserva.expira_en = None  # ← Cancelar la expiración de 10 minutos
    db.commit()
    db.refresh(reserva)

    # Notificar a estacionamientos que el espacio pasa de "bloqueado" a "ocupado"
    async with httpx.AsyncClient(timeout=6.0) as client:
        try:
            await client.put(
                f"{ESTACIONAMIENTOS_SERVICE_URL}/espacios/{reserva.espacio_id}/ocupar",
                headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
            )
        except httpx.RequestError as exc:
            print(f"[RESERVAS] ⚠️ Reserva #{reserva_id} confirmada pero error al ocupar espacio: {str(exc)}")

    return {"ok": True, "estado": "confirmada", "reserva_id": reserva_id}
