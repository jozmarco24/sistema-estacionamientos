from pydantic import BaseModel
from typing import Optional, List
from models import EstadoEspacio, TipoVehiculo

class SedeCreate(BaseModel):
    nombre: str
    direccion: str
    latitud: float
    longitud: float
    propietario_id: Optional[int] = None
    tarifa_hora: Optional[float] = 5.0
    tarifa_auto_dia: Optional[float] = 6.0
    tarifa_auto_noche: Optional[float] = 4.0
    tarifa_moto_dia: Optional[float] = 3.0
    tarifa_moto_noche: Optional[float] = 2.0
    hora_inicio_dia: Optional[int] = 8
    hora_inicio_noche: Optional[int] = 20

class SedeResponse(BaseModel):
    id: int
    nombre: str
    direccion: str
    latitud: float
    longitud: float
    propietario_id: int
    activa: bool
    tarifa_hora: float
    tarifa_auto_dia: float
    tarifa_auto_noche: float
    tarifa_moto_dia: float
    tarifa_moto_noche: float
    hora_inicio_dia: int
    hora_inicio_noche: int

    class Config:
        from_attributes = True

class SedeCercanaResponse(BaseModel):
    id: int
    nombre: str
    direccion: str
    latitud: float
    longitud: float
    propietario_id: int
    activa: bool
    tarifa_hora: float
    tarifa_auto_dia: Optional[float] = 6.0
    tarifa_auto_noche: Optional[float] = 4.0
    tarifa_moto_dia: Optional[float] = 3.0
    tarifa_moto_noche: Optional[float] = 2.0
    distancia_km: float
    culqi_activo: bool = False

    class Config:
        from_attributes = True

class SedeEstadoUpdate(BaseModel):
    activa: bool

class EspacioCreate(BaseModel):
    sede_id: int
    numero: str
    tipo_vehiculo: Optional[TipoVehiculo] = TipoVehiculo.auto
    estado: Optional[EstadoEspacio] = EstadoEspacio.libre

class EspacioResponse(BaseModel):
    id: int
    sede_id: int
    numero: str
    tipo_vehiculo: TipoVehiculo
    estado: EstadoEspacio

    class Config:
        from_attributes = True

class ActualizarEstadoEspacio(BaseModel):
    estado: EstadoEspacio

class EspacioLoteCreate(BaseModel):
    sede_id: int
    prefijo: Optional[str] = "Slot"
    tipo_vehiculo: Optional[TipoVehiculo] = TipoVehiculo.auto
    cantidad: int

class IncidenciaCreate(BaseModel):
    sede_id: int
    descripcion: str

class IncidenciaResponse(BaseModel):
    id: int
    sede_id: int
    operador_id: int
    descripcion: str
    fecha_reporte: str
    estado: str

    class Config:
        from_attributes = True

