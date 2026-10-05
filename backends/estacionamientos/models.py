import enum
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base, SCHEMA_NAME

class EstadoEspacio(str, enum.Enum):
    libre = "libre"
    ocupado = "ocupado"
    reservado = "reservado"

class TipoVehiculo(str, enum.Enum):
    auto = "auto"
    moto = "moto"

class EstadoIncidencia(str, enum.Enum):
    abierta = "abierta"
    resuelta = "resuelta"

class Sede(Base):
    __tablename__ = "sedes"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(200), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    propietario_id = Column(Integer, nullable=False, index=True)
    activa = Column(Boolean, default=True, nullable=False)
    
    # Tarifas diferenciadas por vehículo y franja horaria
    tarifa_hora = Column(Float, default=5.0, nullable=False)        # Base general fallback
    tarifa_auto_dia = Column(Float, default=6.0, nullable=False)   # 8am a 8pm
    tarifa_auto_noche = Column(Float, default=4.0, nullable=False) # 8pm a 8am
    tarifa_moto_dia = Column(Float, default=3.0, nullable=False)   # 8am a 8pm
    tarifa_moto_noche = Column(Float, default=2.0, nullable=False) # 8pm a 8am
    hora_inicio_dia = Column(Integer, default=8, nullable=False)   # 8 (08:00 hrs)
    hora_inicio_noche = Column(Integer, default=20, nullable=False)# 20 (20:00 hrs)

    espacios = relationship("Espacio", back_populates="sede", cascade="all, delete-orphan")
    incidencias = relationship("Incidencia", back_populates="sede", cascade="all, delete-orphan")

class Espacio(Base):
    __tablename__ = "espacios"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    sede_id = Column(Integer, ForeignKey(f"{SCHEMA_NAME}.sedes.id"), nullable=False)
    numero = Column(String(20), nullable=False)
    tipo_vehiculo = Column(Enum(TipoVehiculo), default=TipoVehiculo.auto, nullable=False)
    estado = Column(Enum(EstadoEspacio), default=EstadoEspacio.libre, nullable=False)

    sede = relationship("Sede", back_populates="espacios")

class Incidencia(Base):
    __tablename__ = "incidencias"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    sede_id = Column(Integer, ForeignKey(f"{SCHEMA_NAME}.sedes.id"), nullable=False)
    operador_id = Column(Integer, nullable=False) # Guardamos el ID del operador que reporta
    descripcion = Column(String(500), nullable=False)
    fecha_reporte = Column(String, nullable=False) # Almacenamos ISO String temporalmente para simplificar sin tz
    estado = Column(Enum(EstadoIncidencia), default=EstadoIncidencia.abierta, nullable=False)

    sede = relationship("Sede", back_populates="incidencias")

