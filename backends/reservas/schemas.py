from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import EstadoReserva

class ReservaCreate(BaseModel):
    espacio_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    placa_vehiculo: str
    metodo_pago: Optional[str] = "tarjeta"

class CotizacionResponse(BaseModel):
    espacio_id: int
    duracion_horas: float
    monto_estimado: float
    tarifa_aplicada: float
    es_diurno: bool
    moneda: str = "PEN"

class ReservaResponse(BaseModel):
    id: int
    usuario_id: int
    espacio_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: EstadoReserva
    placa_vehiculo: str
    expira_en: Optional[datetime] = None

    class Config:
        from_attributes = True

class CancelarReservaResponse(BaseModel):
    mensaje: str
    reserva: ReservaResponse
