import httpx
from datetime import datetime
import pytz
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import CredencialCulqi
from auth import get_current_user, require_propietario_o_admin, CurrentUser
from crypto import cifrar, descifrar

router = APIRouter(prefix="/credenciales", tags=["credenciales"])

class GuardarCredencialesRequest(BaseModel):
    public_key: str
    secret_key: str

class GuardarCredencialesResponse(BaseModel):
    public_key_mask: str
    esta_verificada: bool

class VerificarCredencialesResponse(BaseModel):
    estado: str  # "verificada" | "invalida"

class EstadoCredencialesResponse(BaseModel):
    configurada: bool
    verificada: bool
    public_key_mask: Optional[str] = None

def enmascarar_pk(pk: str) -> str:
    if not pk:
        return "pk_test_****"
    pk_clean = pk.strip()
    if len(pk_clean) <= 8:
        return "pk_test_****"
    return f"{pk_clean[:8]}****{pk_clean[-4:]}"

@router.post("/", response_model=GuardarCredencialesResponse)
def guardar_credenciales(
    payload: GuardarCredencialesRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario_o_admin)
):
    pk = payload.public_key.strip()
    sk = payload.secret_key.strip()

    if not pk or not sk:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requieren ambas llaves: public_key y secret_key."
        )

    pk_enc = cifrar(pk)
    sk_enc = cifrar(sk)

    cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == current_user.id).first()
    ahora = datetime.now(pytz.timezone("America/Lima"))

    if not cred:
        cred = CredencialCulqi(
            propietario_id=current_user.id,
            public_key_enc=pk_enc,
            secret_key_enc=sk_enc,
            esta_verificada=False,
            # Retrocompatibilidad
            public_key=pk,
            secret_key_cifrada=sk_enc,
            valida=False,
            actualizado_en=ahora,
            creado_en=ahora
        )
        db.add(cred)
    else:
        cred.public_key_enc = pk_enc
        cred.secret_key_enc = sk_enc
        cred.esta_verificada = False
        # Retrocompatibilidad
        cred.public_key = pk
        cred.secret_key_cifrada = sk_enc
        cred.valida = False
        cred.actualizado_en = ahora

    db.commit()
    db.refresh(cred)

    return GuardarCredencialesResponse(
        public_key_mask=enmascarar_pk(pk),
        esta_verificada=bool(cred.esta_verificada)
    )

@router.post("/verificar", response_model=VerificarCredencialesResponse)
async def verificar_credenciales(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario_o_admin)
):
    cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == current_user.id).first()
    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se han configurado credenciales Culqi."
        )

    # Obtener llave secreta cifrada (priorizar secret_key_enc, retrocompatible con secret_key_cifrada)
    sk_cifrada = cred.secret_key_enc or cred.secret_key_cifrada
    if not sk_cifrada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Llave secreta no encontrada en los registros."
        )

    try:
        sk_descifrada = descifrar(sk_cifrada).strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descifrar la llave secreta: {str(e)}"
        )

    # Petición real a https://api.culqi.com/v2/tokens con esa llave
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.culqi.com/v2/tokens",
                headers={
                    "Authorization": f"Bearer {sk_descifrada}"
                }
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error de conexión con la API de Culqi: {str(exc)}"
        )

    # Regla: Si responde 200 o 400 -> marca esta_verificada = TRUE
    # Si responde 401 -> retorna error "Llave inválida"
    if resp.status_code in [200, 400]:
        cred.esta_verificada = True
        cred.valida = True
        cred.verificada_en = datetime.now(pytz.timezone("America/Lima"))
        cred.actualizado_en = datetime.now(pytz.timezone("America/Lima"))
        db.commit()
        return VerificarCredencialesResponse(estado="verificada")
    elif resp.status_code == 401:
        cred.esta_verificada = False
        cred.valida = False
        cred.actualizado_en = datetime.now(pytz.timezone("America/Lima"))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Llave inválida"
        )
    else:
        # En caso de otro código inesperado
        err_msg = "Error al validar la llave con Culqi"
        try:
            err_json = resp.json()
            err_msg = err_json.get("merchant_message") or err_json.get("user_message") or err_msg
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{err_msg} (Status {resp.status_code})"
        )

@router.get("/estado", response_model=EstadoCredencialesResponse)
def estado_credenciales(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_propietario_o_admin)
):
    cred = db.query(CredencialCulqi).filter(CredencialCulqi.propietario_id == current_user.id).first()
    if not cred:
        return EstadoCredencialesResponse(
            configurada=False,
            verificada=False,
            public_key_mask=None
        )

    pk_real = None
    if cred.public_key_enc:
        try:
            pk_real = descifrar(cred.public_key_enc)
        except Exception:
            pk_real = None
    elif cred.public_key:
        pk_real = cred.public_key

    mask = enmascarar_pk(pk_real) if pk_real else None
    verificada = bool(cred.esta_verificada or cred.valida)

    return EstadoCredencialesResponse(
        configurada=True,
        verificada=verificada,
        public_key_mask=mask
    )
