import os
import httpx
from datetime import datetime, timezone
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
        fecha_pago=datetime.now(timezone.utc)
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

    # ✅ NUEVO: Validar que el pago siga pendiente antes de abrir checkout
    if pago.estado != EstadoPago.pendiente:
        raise HTTPException(
            status_code=409,
            detail=f"Este pago ya no está pendiente (estado: {pago.estado.value}). No se puede iniciar el checkout."
        )

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
        pk = PLATAFORMA_CULQI_PUBLIC

    return ConfigPublicaResponse(
        public_key=pk,
        monto=pago.monto,
        pago_id=pago.id,
        tipo=pago.tipo.value
    )

# 3. Procesar Cobro con Culqi
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

    if pago.estado == EstadoPago.pagado:
        return pago

    if pago.estado == EstadoPago.fallido:
        pago.estado = EstadoPago.pendiente

    if not payload.token_id or not payload.token_id.startswith("tkn_"):
        raise HTTPException(status_code=400, detail="Token de tarjeta inválido.")

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
        secret_key_usar = PLATAFORMA_CULQI_SECRET

    if not secret_key_usar or not secret_key_usar.startswith("sk_test_"):
        raise HTTPException(
            status_code=500,
            detail="Error de configuración: La llave secreta no es de prueba (sk_test_)."
        )

    amount_cents = int(round(pago.monto * 100))

    culqi_payload = {
        "amount": amount_cents,
        "currency_code": "PEN",
        "email": payload.email,
        "source_id": payload.token_id,
        "description": f"Pago SmartPark #{pago.id} ({pago.tipo.value})"
    }

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
        charge_id = culqi_data.get("id")
        pago.culqi_charge_id = charge_id
        pago.referencia_externa = charge_id
        pago.estado = EstadoPago.pagado
        pago.fecha_pago = datetime.now(timezone.utc)
        db.commit()
        db.refresh(pago)

        # ✅ NUEVO: Confirmar la reserva en el servicio de reservas tras pago exitoso
        if pago.tipo == TipoPago.reserva and pago.reserva_id:
            async with httpx.AsyncClient(timeout=8.0) as client:
                try:
                    resp_confirmar = await client.patch(
                        f"{RESERVAS_SERVICE_URL}/reservas/{pago.reserva_id}/confirmar",
                        headers={"X-Internal-Key": INTERNAL_SERVICE_KEY}
                    )
                    if resp_confirmar.status_code not in (200, 204):
                        print(f"[PAGOS] ⚠️ Pago #{pago.id} aprobado pero no se pudo confirmar reserva #{pago.reserva_id}. Status: {resp_confirmar.status_code}")
                except httpx.RequestError as exc:
                    print(f"[PAGOS] ⚠️ Error de red al confirmar reserva #{pago.reserva_id}: {str(exc)}")
    else:
        pago.estado = EstadoPago.fallido
        db.commit()
        db.refresh(pago)
        error_msg = culqi_data.get("user_message") or culqi_data.get("merchant_message") or "Error al procesar el pago."
        raise HTTPException(status_code=402, detail=error_msg)

    return pago
