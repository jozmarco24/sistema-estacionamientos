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
    monto_cobrado: Optional[float] = 0.0

    class Config:
        from_attributes = True

class CancelarReservaResponse(BaseModel):
    mensaje: str
    reserva: ReservaResponse

class WalkinCreate(BaseModel):
    espacio_id: int
    placa_vehiculo: str
    tipo_vehiculo: Optional[str] = "auto"  # "auto" | "moto"
    observacion: Optional[str] = None

class WalkinResponse(BaseModel):
    id: int
    espacio_id: int
    placa_vehiculo: str
    estado: EstadoReserva
    fecha_inicio: datetime
    mensaje: str = "Ingreso walk-in registrado correctamente"

    class Config:
        from_attributes = True

class CobrarCasetaResponse(BaseModel):
    reserva_id: int
    placa_vehiculo: str
    monto_cobrado: float
    duracion_horas: float
    fecha_inicio: datetime
    fecha_salida: datetime
    mensaje: str = "Cobro registrado y espacio liberado"
