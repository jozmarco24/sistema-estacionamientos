from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import TipoPago, EstadoPago

class PagoCreate(BaseModel):
    tipo: Optional[TipoPago] = TipoPago.reserva
    reserva_id: Optional[int] = None
    suscripcion_id: Optional[int] = None
    sede_id: Optional[int] = None
    pagador_id: int
    receptor_id: Optional[int] = None
    cuenta_destino: Optional[str] = None
    monto: float
    metodo_pago: Optional[str] = "tarjeta"
    estado: Optional[EstadoPago] = EstadoPago.pendiente

class PagoResponse(BaseModel):
    id: int
    tipo: TipoPago
    reserva_id: Optional[int] = None
    suscripcion_id: Optional[int] = None
    sede_id: Optional[int] = None
    pagador_id: int
    receptor_id: Optional[int] = None
    cuenta_destino: Optional[str] = None
    monto: float
    metodo_pago: str
    estado: EstadoPago
    fecha_pago: datetime
    culqi_charge_id: Optional[str] = None
    referencia_externa: Optional[str] = None

    class Config:
        from_attributes = True

class ActualizarEstadoPago(BaseModel):
    estado: EstadoPago

class CobroCulqiRequest(BaseModel):
    pago_id: int
    token_id: str
    email: str

class CredencialesCulqiInput(BaseModel):
    public_key: str
    secret_key: str

class CredencialesCulqiResponse(BaseModel):
    configurado: bool
    valida: bool
    public_key: Optional[str] = None
    secret_key_ultimos4: Optional[str] = None
    verificada_en: Optional[datetime] = None

class ConfigPublicaResponse(BaseModel):
    public_key: str
    monto: float
    pago_id: int
    tipo: str
