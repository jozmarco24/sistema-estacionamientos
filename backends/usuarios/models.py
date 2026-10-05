import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Numeric
from database import Base, SCHEMA_NAME

class RolUsuario(str, enum.Enum):
    conductor = "conductor"
    propietario = "propietario"
    operador = "operador"
    admin = "admin"

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), default=RolUsuario.conductor, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    propietario_id = Column(Integer, nullable=True, index=True)
    sede_id = Column(Integer, nullable=True, index=True)

    # Datos bancarios únicos del Propietario para recepción directa de pagos
    banco = Column(String(50), nullable=True)
    numero_cuenta = Column(String(50), nullable=True)
    cci_alias = Column(String(50), nullable=True)
    titular_cuenta = Column(String(100), nullable=True)

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False, index=True)
    placa = Column(String(20), nullable=False)
    marca = Column(String(50), nullable=True)
    modelo = Column(String(50), nullable=True)
    color = Column(String(30), nullable=True)

class Plan(Base):
    __tablename__ = "planes"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    max_sedes = Column(Integer, nullable=False)
    max_operadores = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True)

class Suscripcion(Base):
    __tablename__ = "suscripciones"
    __table_args__ = {"schema": SCHEMA_NAME}

    id = Column(Integer, primary_key=True, index=True)
    propietario_id = Column(Integer, nullable=False, index=True)
    plan_id = Column(Integer, nullable=False)
    estado = Column(String(20), default="activa")
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_vencimiento = Column(DateTime, nullable=False)
