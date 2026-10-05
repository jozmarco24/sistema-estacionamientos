import os
import httpx
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Pago, EstadoPago, TipoPago, CredencialCulqi
from schemas import (
    PagoCreate, PagoResponse, ActualizarEstadoPago,
    CobroCulqiRequest, CredencialesCulqiInput, CredencialesCulqiResponse,
    ConfigPublicaResponse
)
from auth import (
    get_current_user, require_admin, require_propietario,
    verify_internal_key, CurrentUser
)
from crypto import encrypt_secret_key, decrypt_secret_key

router = APIRouter(prefix="/pagos", tags=["pagos"])

RESERVAS_SERVICE_URL = os.getenv("RESERVAS_SERVICE_URL", "http://reservas:8003")
PLATAFORMA_CULQI_PUBLIC = os.getenv("CULQI_PUBLIC_KEY", "")
PLATAFORMA_CULQI_SECRET = os.getenv("CULQI_SECRET_KEY", "")
INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "")

# 1. Crear orden de pago (Solo llamada interna desde reservas o usuarios)
@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(
    pago_in: PagoCreate,
    db: Session = Depends(get_db),
    _internal: bool = Depends(verify_internal_key)
):
    nuevo_pago = Pago(
        tipo=pago_in.tipo or TipoPago.reserva,
        reserva_id=pago_in.reserva_id,
        suscripcion_id=pago_in.suscripcion_id,
        sede_id=pago_in.sede_id,
        pagador_id=pago_in.pagador_id,
        receptor_id=pago_in.receptor_id,
        cuenta_destino=pago_in.cuenta_destino,
        monto=pago_in.monto,
        metodo_pago=pago_in.metodo_pago or "tarjeta",
        estado=pago_in.estado or EstadoPago.pendiente,
        fecha_pago=datetime.utcnow()
    )
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

# 2. Configuración pública para el Checkout Culqi en frontend
@router.get("/config-publica", response_model=ConfigPublicaResponse)
def obtener_config_publica(
    pago_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
        
    if current_user.rol != "admin" and pago.pagador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este pago")

    # Si es reserva, obtener public_key del propietario receptor
    if pago.tipo == TipoPago.reserva:
        if not pago.receptor_id:
            raise HTTPException(status_code=409, detail="La reserva no tiene un propietario receptor asignado.")
        cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == pago.receptor_id).first()
        is_ok = bool(cred and (cred.esta_verificada or cred.valida))
        if not cred or not is_ok:
            raise HTTPException(
                status_code=409,
                detail="El propietario de este estacionamiento aún no ha configurado credenciales válidas de Culqi."
            )
        if cred.public_key_enc:
            try:
                pk = decrypt_secret_key(cred.public_key_enc)
            except Exception:
                pk = cred.public_key
        else:
            pk = cred.public_key
    else:
        # Suscripción SaaS: usa la public key de la plataforma
        pk = PLATAFORMA_CULQI_PUBLIC

    return ConfigPublicaResponse(
        public_key=pk,
        monto=pago.monto,
        pago_id=pago.id,
        tipo=pago.tipo.value
    )

# 3. Procesar Cobro con Culqi (Conductor o Propietario que paga su suscripción)
@router.post("/culqi/cobrar", response_model=PagoResponse)
async def cobrar_con_culqi(
    payload: CobroCulqiRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    pago = db.query(Pago).filter(Pago.id == payload.pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    if current_user.rol != "admin" and pago.pagador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para pagar esta orden.")

    # Idempotencia: Si ya está pagado, retornar resultado sin volver a cobrar
    if pago.estado == EstadoPago.pagado:
        return pago

    if pago.estado == EstadoPago.fallido:
        # Permitir reintento reiniciando a pendiente si la reserva sigue viva
        pago.estado = EstadoPago.pendiente

    # Validar token de Culqi
    if not payload.token_id or not payload.token_id.startswith("tkn_"):
        raise HTTPException(status_code=400, detail="Token de tarjeta inválido.")

    # Si es reserva, verificar con el microservicio de reservas que no haya expirado ni sido cancelada
    if pago.tipo == TipoPago.reserva and pago.reserva_id:
        async with httpx.AsyncClient(timeout=6.0) as client:
            try:
                res_verif = await client.get(
                    f"{RESERVAS_SERVICE_URL}/reservas/{pago.reserva_id}",
                    headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
                )
                if res_verif.status_code == 200:
                    r_data = res_verif.json()
                    estado_r = (r_data.get("estado") or "").lower()
                    if estado_r != "pendiente":
                        raise HTTPException(
                            status_code=409,
                            detail=f"La reserva ya no está pendiente de pago (estado: {estado_r}). No se procesó el cargo."
                        )
                elif res_verif.status_code == 404:
                    raise HTTPException(status_code=404, detail="La reserva asociada no existe.")
            except httpx.RequestError as exc:
                raise HTTPException(status_code=503, detail=f"No se pudo verificar el estado de la reserva: {str(exc)}")

    # Determinar llave secreta según tipo de pago
    secret_key_usar = None
    if pago.tipo == TipoPago.reserva:
        cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == pago.receptor_id).first()
        is_ok = bool(cred and (cred.esta_verificada or cred.valida))
        if not cred or not is_ok:
            raise HTTPException(
                status_code=409,
                detail="El propietario receptor no tiene credenciales de Culqi activas. Pago no procesado."
            )
        try:
            sk_target = cred.secret_key_enc or cred.secret_key_cifrada
            secret_key_usar = decrypt_secret_key(sk_target)
        except Exception:
            raise HTTPException(status_code=500, detail="Error interno al descifrar credenciales de cobro.")
    else:
        # Suscripción de plataforma
        secret_key_usar = PLATAFORMA_CULQI_SECRET

    if not secret_key_usar or not secret_key_usar.startswith("sk_test_"):
        raise HTTPException(
            status_code=500,
            detail="Error de configuración: La llave secreta no es de prueba (sk_test_)."
        )

    # El monto se toma de la base de datos (nunca del cliente) y se convierte a céntimos
    amount_cents = int(round(pago.monto * 100))

    culqi_payload = {
        "amount": amount_cents,
        "currency_code": "PEN",
        "email": payload.email,
        "source_id": payload.token_id,
        "description": f"Pago SmartPark #{pago.id} ({pago.tipo.value})"
    }

    # Llamada a la API de Culqi POST /v2/charges
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp_culqi = await client.post(
                "https://api.culqi.com/v2/charges",
                headers={
                    "Authorization": f"Bearer {secret_key_usar}",
                    "Content-Type": "application/json"
                },
                json=culqi_payload
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Error de comunicación con la pasarela de pagos Culqi: {str(exc)}"
            )

    culqi_data = resp_culqi.json() if resp_culqi.content else {}

    if resp_culqi.status_code == 201:
        # Pago aprobado
        charge_id = culqi_data.get("id")
        pago.culqi_charge_id = charge_id
        pago.referencia_externa = charge_id
        pago.estado = EstadoPago.pagado
        pago.fecha_pago = datetime.utcnow()
        db.commit()
        db.refresh(pago)

        # Si es reserva, confirmar reserva automáticamente con reintentos resilientes
        if pago.tipo == TipoPago.reserva and pago.reserva_id:
            confirmado = False
            for intento in range(3):
                try:
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        resp_res = await client.put(
                            f"{RESERVAS_SERVICE_URL}/reservas/{pago.reserva_id}/estado",
                            headers={"X-Internal-Key": INTERNAL_SERVICE_KEY},
                            json={"estado": "confirmada"}
                        )
                        if resp_res.status_code == 200:
                            confirmado = True
                            break
                except Exception as e:
                    print(f"Intento {intento+1}/3 falló al confirmar reserva #{pago.reserva_id}: {e}")
            if not confirmado:
                print(f"ADVERTENCIA CRÍTICA: No se pudo confirmar automáticamente la reserva #{pago.reserva_id} tras 3 intentos. Pago #{pago.id} registrado.")

        # Si es suscripción, activar suscripción en usuarios con reintentos
        if pago.tipo == TipoPago.suscripcion and pago.suscripcion_id:
            try:
                usuarios_url = os.getenv("USUARIOS_SERVICE_URL", "http://usuarios:8001")
                async with httpx.AsyncClient(timeout=8.0) as client:
                    await client.put(
                        f"{usuarios_url}/usuarios/suscripciones/{pago.suscripcion_id}/estado",
                        headers={"X-Internal-Key": INTERNAL_SERVICE_KEY},
                        json={"estado": "activa"}
                    )
            except Exception as e:
                print(f"Advertencia: No se pudo activar suscripción tras pago: {e}")

        return pago
    else:
        # Pago rechazado o error de Culqi
        pago.estado = EstadoPago.fallido
        db.commit()
        db.refresh(pago)

        msg_error = culqi_data.get("user_message") or culqi_data.get("merchant_message") or "El cargo fue declinado por el emisor."
        raise HTTPException(
            status_code=402,
            detail=f"Pago no procesado por Culqi: {msg_error}"
        )

# 4. Gestión de Credenciales Culqi para Propietarios (PASO 2B)
@router.get("/mis-credenciales-culqi", response_model=CredencialesCulqiResponse)
def obtener_mis_credenciales(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario)
):
    cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == current_user.id).first()
    if not cred:
        return CredencialesCulqiResponse(configurado=False, valida=False)
        
    try:
        decrypted_sk = decrypt_secret_key(cred.secret_key_cifrada)
        ultimos4 = decrypted_sk[-4:] if len(decrypted_sk) >= 4 else "****"
    except Exception:
        ultimos4 = "****"

    return CredencialesCulqiResponse(
        configurado=True,
        valida=cred.valida,
        public_key=cred.public_key,
        secret_key_ultimos4=ultimos4,
        verificada_en=cred.verificada_en
    )

@router.put("/mis-credenciales-culqi", response_model=CredencialesCulqiResponse)
async def configurar_mis_credenciales(
    payload: CredencialesCulqiInput,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario)
):
    # Validar modo de prueba estricto
    pk = payload.public_key.strip()
    sk = payload.secret_key.strip()

    if not pk.startswith("pk_test_"):
        raise HTTPException(
            status_code=400,
            detail="La llave pública debe iniciar obligatoriamente con 'pk_test_' (Solo modo prueba permitido)."
        )
    if not sk.startswith("sk_test_"):
        raise HTTPException(
            status_code=400,
            detail="La llave secreta debe iniciar obligatoriamente con 'sk_test_' (Solo modo prueba permitido)."
        )

    # Validar llave secreta con llamada de solo lectura a Culqi (GET /v2/charges?limit=1)
    valida = False
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            test_resp = await client.get(
                "https://api.culqi.com/v2/charges?limit=1",
                headers={"Authorization": f"Bearer {sk}"}
            )
            if test_resp.status_code == 200:
                valida = True
            else:
                err_data = test_resp.json() if test_resp.content else {}
                err_msg = err_data.get("merchant_message") or err_data.get("user_message") or "Llave secreta inválida o rechazada por Culqi."
                raise HTTPException(
                    status_code=400,
                    detail=f"Culqi rechazó la llave secreta: {err_msg}"
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"No se pudo conectar con los servidores de Culqi para validar tu llave: {str(exc)}"
            )

    cifrada = encrypt_secret_key(sk)
    cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == current_user.id).first()
    if not cred:
        cred = CredencialCulqi(
            propietario_id=current_user.id,
            public_key=pk,
            secret_key_cifrada=cifrada,
            valida=valida,
            verificada_en=datetime.utcnow()
        )
        db.add(cred)
    else:
        cred.public_key = pk
        cred.secret_key_cifrada = cifrada
        cred.valida = valida
        cred.verificada_en = datetime.utcnow()

    db.commit()
    db.refresh(cred)

    return CredencialesCulqiResponse(
        configurado=True,
        valida=cred.valida,
        public_key=cred.public_key,
        secret_key_ultimos4=sk[-4:],
        verificada_en=cred.verificada_en
    )

@router.delete("/mis-credenciales-culqi", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mis_credenciales(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario)
):
    cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == current_user.id).first()
    if cred:
        db.delete(cred)
        db.commit()
    return None

# Endpoint interno para que reservas y estacionamientos verifiquen si el dueño tiene Culqi configurado
@router.get("/internal/propietario/{propietario_id}/culqi-valida")
def verificar_culqi_propietario_interno(
    propietario_id: int,
    db: Session = Depends(get_db),
    _internal: bool = Depends(verify_internal_key)
):
    cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == propietario_id).first()
    is_valida = bool(cred and (cred.esta_verificada or cred.valida))
    return {"valida": is_valida}

# 5. Consultas protegidas existentes
@router.get("/", response_model=List[PagoResponse])
def listar_todos_los_pagos(
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_admin)
):
    return db.query(Pago).all()

@router.get("/propietario/{propietario_id}", response_model=List[PagoResponse])
def consultar_pagos_propietario(
    propietario_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.rol != "admin" and (current_user.rol != "propietario" or current_user.id != propietario_id):
        raise HTTPException(status_code=403, detail="No puedes ver pagos de otro propietario")
    return db.query(Pago).filter(
        Pago.receptor_id == propietario_id,
        Pago.tipo == TipoPago.reserva
    ).order_by(Pago.id.desc()).all()

@router.get("/admin/suscripciones", response_model=List[PagoResponse])
def consultar_pagos_suscripciones(
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_admin)
):
    return db.query(Pago).filter(
        Pago.tipo == TipoPago.suscripcion
    ).order_by(Pago.id.desc()).all()

@router.get("/{pago_id}", response_model=PagoResponse)
def consultar_pago(
    pago_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if current_user.rol != "admin" and pago.pagador_id != current_user.id and pago.receptor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado a este pago")
    return pago

@router.get("/reserva/{reserva_id}", response_model=List[PagoResponse])
def consultar_pagos_por_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    pagos = db.query(Pago).filter(Pago.reserva_id == reserva_id).all()
    if current_user.rol != "admin":
        for p in pagos:
            if p.pagador_id != current_user.id and p.receptor_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado para consultar estos pagos")
    return pagos

@router.get("/suscripcion/{suscripcion_id}", response_model=List[PagoResponse])
def consultar_pagos_por_suscripcion(
    suscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    pagos = db.query(Pago).filter(Pago.suscripcion_id == suscripcion_id).all()
    if current_user.rol != "admin":
        for p in pagos:
            if p.pagador_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado para consultar estos pagos de suscripción")
    return pagos

# Endpoint interno / admin para marcar pago en efectivo en caseta (operador o admin)
@router.put("/{pago_id}/procesar-interno", response_model=PagoResponse)
async def procesar_pago_interno(
    pago_id: int,
    payload: ActualizarEstadoPago,
    db: Session = Depends(get_db),
    _internal: bool = Depends(verify_internal_key)
):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    pago.estado = payload.estado
    pago.fecha_pago = datetime.utcnow()
    db.commit()
    db.refresh(pago)

    if payload.estado == EstadoPago.pagado and pago.reserva_id:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.put(
                    f"{RESERVAS_SERVICE_URL}/reservas/{pago.reserva_id}/estado",
                    headers={"X-Internal-Key": INTERNAL_SERVICE_KEY},
                    json={"estado": "confirmada"}
                )
        except Exception as e:
            print(f"Error confirmando reserva tras pago interno: {e}")

    return pago
